import numpy as np
import sounddevice as sd
import simpleaudio as sa
import time
from typing import Optional
from config import SAMPLE_RATE, NOTE_DURATION

def record_audio(duration: float, sample_rate: int) -> np.ndarray:
    """Mikrofondan ses kaydı alır."""
    print("Dinliyorum...")
    time.sleep(1)
    recording = sd.rec(int(duration * sample_rate), 
                      samplerate=sample_rate, 
                      channels=1, 
                      dtype='float64')
    sd.wait()
    print("Kayıt alındı.")
    return recording.flatten()

def play_note(frequency: float, duration: float = 2, waveform: str = "piano") -> None:
    """Belirtilen frekansta ses çalar."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    
    if waveform == "piano":
        # Piyano sesi için harmonikler
        note = 0.5 * (
            0.6 * np.sin(2 * np.pi * frequency * t) +  # Temel frekans
            0.3 * np.sin(2 * np.pi * 2 * frequency * t) +  # 2. harmonik
            0.1 * np.sin(2 * np.pi * 3 * frequency * t) +  # 3. harmonik
            0.05 * np.sin(2 * np.pi * 4 * frequency * t)  # 4. harmonik
        )
    else:
        note = 0.5 * np.sin(2 * np.pi * frequency * t)
    
    audio = np.int16(note * 32767)
    play_obj = sa.play_buffer(audio, 1, 2, SAMPLE_RATE)
    play_obj.wait_done()

def list_and_select_microphone() -> Optional[int]:
    """Kullanılabilir mikrofonları listeler ve seçim yapar."""
    devices = sd.query_devices()
    input_devices = []
    
    print("\nKullanılabilir Mikrofonlar:")
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"{len(input_devices)}: {device['name']}")
            input_devices.append(i)
    
    if not input_devices:
        print("Hiç mikrofon bulunamadı!")
        return None
        
    try:
        selection = int(input("\nKullanmak istediğiniz mikrofonun numarasını girin: "))
        device_index = input_devices[selection]
        sd.default.device = device_index
        print(f"Seçilen mikrofon: {devices[device_index]['name']}")
        return device_index
    except:
        print("Geçersiz seçim, varsayılan mikrofon kullanılacak.")
        return None 