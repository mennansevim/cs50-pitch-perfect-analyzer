import numpy as np
import scipy.signal
import scipy.fftpack
from typing import List, Tuple
from models import VOICE_RANGES, nota_cevirici, NOTE_FREQUENCIES
from config import SAMPLE_RATE, ACCEPTABLE_MARGIN, NOTE_DURATION, MAX_ATTEMPTS, MIN_SUCCESS_RATE
from audio_utils import record_audio, play_note

def dominant_frequency(data: np.ndarray, rate: int) -> float:
    """Ses verisinden dominant frekansı hesaplar."""
    # Ses seviyesi kontrolü
    signal_power = np.mean(np.abs(data))
    if signal_power < 0.001:
        return 0
    
    # Normalizasyon
    data = data / np.max(np.abs(data)) if np.max(np.abs(data)) > 0 else data
    
    # Windowing
    windowed = data * np.hanning(len(data))
    spectrum = np.abs(scipy.fftpack.fft(windowed))
    freqs = scipy.fftpack.fftfreq(len(spectrum), d=1/rate)
    
    positive_mask = freqs > 0
    freqs = freqs[positive_mask]
    spectrum = spectrum[positive_mask]
    
    # İnsan sesi için daha geniş frekans aralığı
    valid_mask = (freqs >= 80) & (freqs <= 800)  # 80-800 Hz arası
    freqs = freqs[valid_mask]
    spectrum = spectrum[valid_mask]
    
    if len(freqs) == 0 or len(spectrum) == 0:
        return 0
    
    # Normalize spectrum
    if np.max(spectrum) > 0:
        spectrum = spectrum / np.max(spectrum)
    
    # Daha hassas peak detection
    peaks, properties = scipy.signal.find_peaks(
        spectrum, 
        height=0.1,      # Daha yüksek eşik
        distance=10,     # Daha yakın peaks
        prominence=0.05   # Peak prominence
    )
    
    if len(peaks) == 0:
        # Fallback: en yüksek frekans
        max_idx = np.argmax(spectrum)
        return freqs[max_idx]
    
    # En yüksek peak'i seç
    peak_heights = spectrum[peaks]
    highest_peak_idx = peaks[np.argmax(peak_heights)]
    
    return freqs[highest_peak_idx]

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

def run_voice_test(start_note: Tuple[str, float], direction: int) -> List[Tuple[str, float, str]]:
    """Ses testi yapar ve sonuçları döndürür."""
    detected_ranges = []
    index = NOTE_FREQUENCIES.index(start_note)
    
    print("Ses testi başlıyor...")

    while 0 <= index < len(NOTE_FREQUENCIES):
        note, frequency = NOTE_FREQUENCIES[index]
        turkce_nota = nota_cevirici(note)
        attempts = 0

        while attempts < MAX_ATTEMPTS:
            print(f"\nŞimdi söylemeniz gereken nota: {turkce_nota} ({frequency:.2f} Hz)")
            print(f"Deneme: {attempts + 1}/{MAX_ATTEMPTS}")
            play_note(frequency, NOTE_DURATION, waveform="piano")

            audio_data = record_audio(NOTE_DURATION, SAMPLE_RATE)
            dominant_freq = dominant_frequency(audio_data, SAMPLE_RATE)
            voice_range = identify_voice_range(dominant_freq)
            success_rate = calculate_success_percentage(frequency, dominant_freq, ACCEPTABLE_MARGIN)

            signal_power = np.mean(np.abs(audio_data))
            if signal_power < 0.01:
                print("Ses seviyesi çok düşük. Lütfen daha yüksek sesle tekrar deneyin.")
                attempts += 1
                if attempts >= MAX_ATTEMPTS:
                    print(f"\nBaşarısız! {MAX_ATTEMPTS} deneme sonunda yeterli ses seviyesine ulaşılamadı.")
                    return detected_ranges
                continue

            print(f"Söylenen frekans: {dominant_freq:.2f} Hz (Başarı: %{success_rate:.1f})")

            if success_rate >= MIN_SUCCESS_RATE:
                detected_ranges.append((turkce_nota, dominant_freq, voice_range))
                index += direction
                break
            else:
                attempts += 1
                if attempts < MAX_ATTEMPTS:
                    print(f"Başarı oranı çok düşük (%{success_rate:.1f}), en az %{MIN_SUCCESS_RATE} olmalı.")
                    print(f"Kalan deneme: {MAX_ATTEMPTS - attempts}")
                else:
                    print(f"\nBaşarısız! {MAX_ATTEMPTS} deneme sonunda %{MIN_SUCCESS_RATE} başarı oranına ulaşılamadı.")
                    print("Test sona eriyor.")
                    return detected_ranges

    return detected_ranges 