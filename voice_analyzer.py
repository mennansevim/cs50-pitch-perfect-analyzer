import numpy as np
import scipy.signal
import scipy.fftpack
from typing import List, Tuple
from models import VOICE_RANGES, nota_cevirici, NOTE_FREQUENCIES
from config import SAMPLE_RATE, ACCEPTABLE_MARGIN, NOTE_DURATION, MAX_ATTEMPTS, MIN_SUCCESS_RATE
from audio_utils import record_audio, play_note

def dominant_frequency(data: np.ndarray, rate: int) -> float:
    """Ses verisinden dominant frekansı hesaplar."""
    windowed = data * np.hanning(len(data))
    spectrum = np.abs(scipy.fftpack.fft(windowed))
    freqs = scipy.fftpack.fftfreq(len(spectrum), d=1/rate)
    
    positive_mask = freqs > 0
    freqs = freqs[positive_mask]
    spectrum = spectrum[positive_mask]
    
    valid_mask = (freqs >= 60) & (freqs <= 1100)
    freqs = freqs[valid_mask]
    spectrum = spectrum[valid_mask]
    
    if len(freqs) == 0 or len(spectrum) == 0:
        return 0
        
    spectrum = spectrum / np.max(spectrum)
    peaks, _ = scipy.signal.find_peaks(spectrum, height=0.05, distance=30)
    
    return freqs[peaks[0]] if len(peaks) > 0 else 0

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

    difference = abs(target_freq - actual_freq)
    if difference > margin:
        return 0
    success = ((margin - difference) / margin) ** 2 * 100
    return min(100, max(0, success))

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
            play_note(frequency, NOTE_DURATION, waveform="sine")

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