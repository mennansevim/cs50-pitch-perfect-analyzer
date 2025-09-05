import numpy as np
import scipy.signal
import scipy.fftpack
from typing import List, Tuple
from models import VOICE_RANGES, nota_cevirici, NOTE_FREQUENCIES
from config import SAMPLE_RATE, ACCEPTABLE_MARGIN, NOTE_DURATION, MAX_ATTEMPTS, MIN_SUCCESS_RATE
from audio_utils import record_audio, play_note

def dominant_frequency(data: np.ndarray, rate: int) -> float:
    """Ses verisinden temel frekansı (fundamental frequency) hesaplar."""
    # Ses seviyesi kontrolü
    signal_power = np.mean(np.abs(data))
    if signal_power < 0.001:
        return 0
    
    # Normalizasyon
    data = data / np.max(np.abs(data)) if np.max(np.abs(data)) > 0 else data
    
    # Windowing - daha iyi harmonik ayrımı için
    windowed = data * np.hanning(len(data))
    spectrum = np.abs(scipy.fftpack.fft(windowed))
    freqs = scipy.fftpack.fftfreq(len(spectrum), d=1/rate)
    
    positive_mask = freqs > 0
    freqs = freqs[positive_mask]
    spectrum = spectrum[positive_mask]
    
    # Tam spectrum'u harmonik analiz için sakla
    full_freqs = freqs.copy()
    full_spectrum = spectrum.copy()
    
    # İnsan sesi için temel frekans aralığı (daha dar)
    fundamental_mask = (freqs >= 80) & (freqs <= 400)  # 80-400 Hz arası temel frekanslar
    fund_freqs = freqs[fundamental_mask]
    fund_spectrum = spectrum[fundamental_mask]
    
    if len(fund_freqs) == 0 or len(fund_spectrum) == 0:
        return 0
    
    # Normalize spectrum
    if np.max(fund_spectrum) > 0:
        fund_spectrum = fund_spectrum / np.max(fund_spectrum)
    if np.max(full_spectrum) > 0:
        full_spectrum = full_spectrum / np.max(full_spectrum)
    
    # Peak detection - sadece temel frekans aralığında
    peaks, properties = scipy.signal.find_peaks(
        fund_spectrum, 
        height=0.05,     # Daha düşük eşik - zayıf temel frekansları yakalamak için
        distance=5,      # Daha yakın peaks'e izin ver
        prominence=0.02  # Daha düşük prominence
    )
    
    if len(peaks) == 0:
        # Fallback: en yüksek frekans
        max_idx = np.argmax(fund_spectrum)
        return fund_freqs[max_idx]
    
    # Temel frekans bulma stratejisi
    peak_freqs = fund_freqs[peaks]
    peak_heights = fund_spectrum[peaks]
    
    # Harmonik kontrolü - gerçek temel frekansı bul
    best_fundamental = 0
    best_score = 0
    
    for i, (freq, height) in enumerate(zip(peak_freqs, peak_heights)):
        if height < 0.05:  # Çok zayıf peak'leri atla
            continue
            
        # Bu frekansın harmonikleri var mı kontrol et (tam spectrum'da)
        harmonic_strength = 0
        harmonic_count = 0
        
        # 2., 3., 4. harmonikleri kontrol et
        for harmonic in [2, 3, 4]:
            harmonic_freq = freq * harmonic
            if harmonic_freq > 800:
                break
                
            # Bu harmonik tam spectrum'da var mı?
            harmonic_indices = np.where(np.abs(full_freqs - harmonic_freq) < 15)[0]
            if len(harmonic_indices) > 0:
                # En yakın frekansı bul
                closest_idx = harmonic_indices[np.argmin(np.abs(full_freqs[harmonic_indices] - harmonic_freq))]
                harmonic_strength += full_spectrum[closest_idx]
                harmonic_count += 1
        
        # Skor hesaplama: temel frekans gücü + harmonik desteği + düşük frekans bonusu
        fundamental_score = height + (harmonic_strength * 0.4) + (300.0 / max(freq, 80)) * 0.3
        
        # Eğer bu frekansın güçlü harmonikleri varsa bonus ver
        if harmonic_count >= 2:
            fundamental_score *= 1.5
        
        if fundamental_score > best_score:
            best_score = fundamental_score
            best_fundamental = freq
    
    # Eğer harmonik analizde sonuç bulunamadıysa, en düşük frekanstaki en güçlü peak'i al
    if best_fundamental == 0:
        # En düşük frekanstaki yeterince güçlü peak'i bul
        for i in range(len(peaks)):
            if peak_heights[i] > 0.05:
                best_fundamental = peak_freqs[i]
                break
        
        # Hala bulunamadıysa, en güçlü peak'i al
        if best_fundamental == 0:
            highest_peak_idx = peaks[np.argmax(peak_heights)]
            best_fundamental = fund_freqs[highest_peak_idx]
    
    return best_fundamental

def identify_voice_range(frequency: float) -> str:
    """Frekansa göre ses aralığını belirler."""
    for voice_type, (low, high) in VOICE_RANGES.items():
        if low <= frequency <= high:
            return voice_type
    return "Bilinmeyen Aralık"

def calculate_success_percentage(target_freq: float, actual_freq: float, margin: float) -> float:
    """Hedef ve gerçek frekans arasındaki başarı yüzdesini hesaplar."""
    if actual_freq == 0:
        return 0

    # Oktav kontrolü - eğer 2x veya 0.5x ise aynı nota
    ratios = [1.0, 2.0, 0.5, 4.0, 0.25]  # 1x, 2x, 0.5x, 4x, 0.25x oktavlar
    
    best_score = 0
    for ratio in ratios:
        adjusted_target = target_freq * ratio
        difference = abs(adjusted_target - actual_freq)
        
        if difference <= margin:
            score = ((margin - difference) / margin) * 100
            # Oktav bonusu: aynı oktav ise tam puan, farklı oktav ise %80
            if ratio == 1.0:
                score = score  # Tam puan
            else:
                score = score * 0.8  # %80 puan
            
            best_score = max(best_score, score)
    
    return min(100, max(0, best_score))

def get_octave_info(frequency: float) -> str:
    """Frekansdan oktav bilgisini hesaplar."""
    # A4 = 440 Hz referans alarak oktav hesaplama
    # Her oktav 2x frekans artışı demektir
    
    # A4'ten ne kadar uzakta olduğunu hesapla
    a4_freq = 440.0
    octave_difference = np.log2(frequency / a4_freq)
    octave_number = 4 + octave_difference
    
    if octave_number < 2:
        return "Very Low Octave"
    elif octave_number < 3:
        return "2nd Octave"
    elif octave_number < 4:
        return "3rd Octave"
    elif octave_number < 5:
        return "4th Octave"
    elif octave_number < 6:
        return "5th Octave"
    elif octave_number < 7:
        return "6th Octave"
    else:
        return "Very High Octave"

def print_success_visual(nota: str, success_rate: float, dominant_freq: float) -> None:
    """Visual display for successful notes."""
    # Message based on success rate
    if success_rate >= 95:
        status_msg = "🏆 PERFECT!"
    elif success_rate >= 90:
        status_msg = "⭐ GREAT!"
    elif success_rate >= 85:
        status_msg = "👍 VERY GOOD!"
    else:
        status_msg = "✅ GOOD!"
    
    # Octave information
    octave_info = get_octave_info(dominant_freq)
    
    # Success bar (shorter)
    bar_length = 20
    filled_length = int(bar_length * success_rate / 100)
    bar = "█" * filled_length + "░" * (bar_length - filled_length)
    
    print(f"\n🎵 SUCCESS! {nota} | {dominant_freq:.1f} Hz ({octave_info}) | [{bar}] %{success_rate:.1f} | {status_msg}")
    print("─" * 80)

def print_failure_visual(nota: str, success_rate: float, dominant_freq: float, target_freq: float, attempts: int, max_attempts: int) -> None:
    """Visual display for failed attempts."""
    # Octave information
    octave_info = get_octave_info(dominant_freq)
    
    # Motivational message
    if success_rate < 20:
        tip = "💡 Sing the note more clearly"
    elif success_rate < 50:
        tip = "💡 Sing slowly and carefully"
    else:
        tip = "💡 Very close! Try again"
    
    # Error bar
    bar_length = 15
    filled_length = int(bar_length * success_rate / 100)
    bar = "█" * filled_length + "░" * (bar_length - filled_length)
    
    if attempts < max_attempts:
        remaining = f"| {max_attempts - attempts} attempts left"
    else:
        remaining = "| Last attempt"
    
    print(f"\n❌ FAILED: {nota} | Target: {target_freq:.1f} Hz | Detected: {dominant_freq:.1f} Hz ({octave_info})")
    print(f"📊 [{bar}] %{success_rate:.1f} {remaining} {tip}")
    print("─" * 80)

def print_low_volume_warning() -> None:
    """Low volume warning."""
    print("\n🔇 VOLUME TOO LOW! | Move closer to microphone and speak louder | 💡 Speak more clearly")
    print("─" * 80)

def run_voice_test(start_note: Tuple[str, float], direction: int) -> Tuple[List[Tuple[str, float, str]], List[dict]]:
    """Performs voice test and returns results + detailed history."""
    detected_ranges = []
    test_history = []
    index = NOTE_FREQUENCIES.index(start_note)
    successful_notes = []
    
    direction_text = "🔽 BASS" if direction == -1 else "🔼 TREBLE"
    test_direction = "down" if direction == -1 else "up"
    print(f"\n🎵 {direction_text} VOICE TEST STARTING 🎵")
    print("="*50)

    while 0 <= index < len(NOTE_FREQUENCIES):
        note, frequency = NOTE_FREQUENCIES[index]
        turkce_nota = nota_cevirici(note)
        attempts = 0

        print(f"\n🎼 UP NEXT: {turkce_nota} ({frequency:.2f} Hz)")
        print("🎹 Playing reference note...")
        
        while attempts < MAX_ATTEMPTS:
            attempts += 1
            play_note(frequency, NOTE_DURATION, waveform="piano")

            audio_data = record_audio(NOTE_DURATION, SAMPLE_RATE)
            dominant_freq = dominant_frequency(audio_data, SAMPLE_RATE)
            voice_range = identify_voice_range(dominant_freq)
            success_rate = calculate_success_percentage(frequency, dominant_freq, ACCEPTABLE_MARGIN)
            
            # Calculate octave
            import math
            if dominant_freq > 0:
                octave_number = int(math.log2(dominant_freq / 440) * 12 / 12) + 4
            else:
                octave_number = None

            signal_power = np.mean(np.abs(audio_data))
            if signal_power < 0.01:
                print_low_volume_warning()
                # Don't record low volume attempts in test history
                if attempts >= MAX_ATTEMPTS:
                    print(f"\n❌ Sufficient volume level could not be reached after {MAX_ATTEMPTS} attempts.")
                    print("🎯 Test ending...")
                    # Only record final failed attempt when all attempts fail due to low volume
                    test_history.append({
                        'note_name': note,
                        'target_frequency': frequency,
                        'detected_frequency': 0,
                        'octave_number': 0,
                        'accuracy_percentage': 0.0,
                        'attempt_number': attempts,
                        'is_successful': False,
                        'test_direction': test_direction
                    })
                    return detected_ranges, test_history
                continue

            # Save to test history
            test_history.append({
                'note_name': note,
                'target_frequency': frequency,
                'detected_frequency': dominant_freq,
                'octave_number': octave_number,
                'accuracy_percentage': success_rate,
                'attempt_number': attempts,
                'is_successful': success_rate >= MIN_SUCCESS_RATE,
                'test_direction': test_direction
            })

            if success_rate >= MIN_SUCCESS_RATE:
                print_success_visual(turkce_nota, success_rate, dominant_freq)
                detected_ranges.append((turkce_nota, dominant_freq, voice_range))
                successful_notes.append(turkce_nota)
                
                # List of successful notes
                if len(successful_notes) > 1:
                    print(f"\n🏆 SUCCESSFUL NOTES: {' → '.join(successful_notes)}")
                
                index += direction
                break
            else:
                print_failure_visual(turkce_nota, success_rate, dominant_freq, frequency, attempts, MAX_ATTEMPTS)
                
                if attempts >= MAX_ATTEMPTS:
                    print(f"\n🏁 Test completed for {turkce_nota} note.")
                    print("🎯 Moving to next test...")
                    return detected_ranges, test_history

    return detected_ranges, test_history 