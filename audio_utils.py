import numpy as np
import sounddevice as sd
import simpleaudio as sa
import time
import os
from typing import Optional
from config import SAMPLE_RATE, NOTE_DURATION
from pydub import AudioSegment
from pydub.playback import play
from models import NOTE_FREQUENCIES

def record_audio(duration: float, sample_rate: int) -> np.ndarray:
    """Records audio from microphone."""
    print("Listening...")
    time.sleep(1)
    recording = sd.rec(int(duration * sample_rate), 
                      samplerate=sample_rate, 
                      channels=1, 
                      dtype='float64')
    sd.wait()
    print("Recording captured.")
    return recording.flatten()

def find_closest_note(frequency: float) -> Optional[str]:
    """Verilen frekansa en yakın notayı bulur."""
    min_diff = float('inf')
    closest_note = None
    
    for note_name, note_freq in NOTE_FREQUENCIES:
        diff = abs(frequency - note_freq)
        if diff < min_diff:
            min_diff = diff
            closest_note = note_name
    
    return closest_note

def play_note(frequency: float, duration: float = 2, waveform: str = "piano") -> None:
    """Belirtilen frekansta ses çalar - önce WAV dosyası arar, bulamazsa sentetik ses üretir."""
    
    # En yakın notayı bul
    note_name = find_closest_note(frequency)
    
    if note_name and waveform == "piano":
        # WAV dosyası yolunu oluştur
        wav_file_path = os.path.join("sounds", "piano", f"{note_name}.wav")
        
        # WAV dosyası varsa çal
        if os.path.exists(wav_file_path):
            try:
                audio = AudioSegment.from_wav(wav_file_path)
                # Süreyi ayarla
                if len(audio) > duration * 1000:  # milisaniye cinsinden
                    audio = audio[:int(duration * 1000)]
                elif len(audio) < duration * 1000:
                    # Kısa ses dosyalarını tekrarla
                    repeat_count = int((duration * 1000) / len(audio)) + 1
                    audio = audio * repeat_count
                    audio = audio[:int(duration * 1000)]
                
                # Pat sesini önlemek için yumuşak giriş/çıkış ekle
                fade_duration = min(50, len(audio) // 4)  # 50ms veya ses uzunluğunun 1/4'ü
                audio = audio.fade_in(fade_duration).fade_out(fade_duration)
                
                print(f"🎹 {note_name} playing...")
                play(audio)
                return  # ÖNEMLİ: WAV dosyası başarıyla çalındıysa fonksiyondan çık
            except Exception as e:
                print(f"⚠️ Error while playing WAV file: {e}")
                # WAV hatası durumunda sentetik sese geç
        else:
            print(f"⚠️ {note_name} için WAV dosyası bulunamadı")
    
    # WAV dosyası bulunamazsa veya hata olursa sentetik ses üret
    print(f"🎵 {frequency:.1f} Hz frekansta sentetik piano sesi çalınıyor...")
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    
    if waveform == "piano":
        # Harmonics for piano sound - daha yumuşak geçiş için envelope ekle
        envelope = np.exp(-t * 0.5)  # Decay envelope
        note = 0.5 * envelope * (
            0.6 * np.sin(2 * np.pi * frequency * t) +  # Fundamental frequency
            0.3 * np.sin(2 * np.pi * 2 * frequency * t) +  # 2nd harmonic
            0.1 * np.sin(2 * np.pi * 3 * frequency * t) +  # 3rd harmonic
            0.05 * np.sin(2 * np.pi * 4 * frequency * t)  # 4th harmonic
        )
    else:
        note = 0.5 * np.sin(2 * np.pi * frequency * t)
    
    # Pat sesini önlemek için yumuşak giriş/çıkış ekle
    fade_samples = int(0.02 * SAMPLE_RATE)  # 20ms fade
    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)
    
    if len(note) > 2 * fade_samples:
        note[:fade_samples] *= fade_in
        note[-fade_samples:] *= fade_out
    
    audio = np.int16(note * 32767)
    play_obj = sa.play_buffer(audio, 1, 2, SAMPLE_RATE)
    play_obj.wait_done()

def list_and_select_microphone() -> Optional[int]:
    """Lists available microphones and makes selection."""
    devices = sd.query_devices()
    input_devices = []
    
    print("\nAvailable Microphones:")
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"{len(input_devices)}: {device['name']}")
            input_devices.append(i)
    
    if not input_devices:
        print("No microphones found!")
        return None
        
    try:
        selection = int(input("\nEnter the number of the microphone you want to use: "))
        device_index = input_devices[selection]
        sd.default.device = device_index
        print(f"Selected microphone: {devices[device_index]['name']}")
        return device_index
    except:
        print("Invalid selection, default microphone will be used.")
        return None 