import numpy as np
import sounddevice as sd
import scipy.signal
import scipy.fftpack
import time
import simpleaudio as sa

# Erkek ve kadın ses aralıkları tanımlaması (soprano, alto, tenor, bas)
voice_ranges = {
    "Kadın - Soprano": (261.63, 1046.50),    # C4 - C6
    "Kadın - Alto": (220.00, 698.46),        # A3 - F5
    "Erkek - Tenor": (130.81, 523.25),          # C3 - C5
    "Erkek - Bas": (82.41, 329.63)              # E2 - E4
}

# Mikrofon ayarları
NOTE_DURATION = 2  # Her notanın kaydedilme süresi (saniye)
SAMPLE_RATE = 44100  # Örnekleme frekansı
ACCEPTABLE_MARGIN = 40  # Frekanstaki kabul edilebilir sapma (Hz)

# Nota isimleri ve frekansları (C2'den C6'ya kadar)
note_frequencies = [
    ("C2", 65.41), ("D2", 73.42), ("E2", 82.41), ("F2", 87.31), ("G2", 98.00), ("A2", 110.00), ("B2", 123.47),
    ("C3", 130.81), ("D3", 146.83), ("E3", 164.81), ("F3", 174.61), ("G3", 196.00), ("A3", 220.00), ("B3", 246.94),
    ("C4", 261.63), ("D4", 293.66), ("E4", 329.63), ("F4", 349.23), ("G4", 392.00), ("A4", 440.00), ("B4", 493.88),
    ("C5", 523.25), ("D5", 587.33), ("E5", 659.25), ("F5", 698.46), ("G5", 783.99), ("A5", 880.00), ("B5", 987.77),
    ("C6", 1046.50)
]

# Nota isimlerinin Türkçe karşılıkları
nota_isimleri = {
    "C": "Do",
    "D": "Re",
    "E": "Mi",
    "F": "Fa",
    "G": "Sol",
    "A": "La",
    "B": "Si"
}

def nota_cevirici(note_name):
    """C4 gibi nota isimlerini Do4 formatına çevirir"""
    harf = note_name[0]
    oktav = note_name[1]
    return f"{nota_isimleri[harf]}{oktav}"

# Fourier Transform ile dominant frekansı bulma fonksiyonu
def dominant_frequency(data, rate):
    """Temel frekansı harmonikleri de göz önünde bulundurarak bul"""
    # Hanning penceresi uygula
    windowed = data * np.hanning(len(data))

    # FFT uygula ve normalize et
    spectrum = np.abs(scipy.fftpack.fft(windowed))
    freqs = scipy.fftpack.fftfreq(len(spectrum), d=1/rate)

    # Sadece pozitif frekansları al
    positive_mask = freqs > 0
    freqs = freqs[positive_mask]
    spectrum = spectrum[positive_mask]

    # İnsan ses aralığına odaklan (60Hz - 1100Hz)
    valid_mask = (freqs >= 60) & (freqs <= 1100)
    freqs = freqs[valid_mask]
    spectrum = spectrum[valid_mask]

    if len(freqs) == 0 or len(spectrum) == 0:
        return 0

    # Spektrumu normalize et
    spectrum = spectrum / np.max(spectrum)
    
    # Eşik değerini düşür ve minimum mesafeyi artır
    threshold = 0.05
    min_peak_distance = 30
    
    # Spektrumda önemli tepeleri bul
    peaks, properties = scipy.signal.find_peaks(spectrum, height=threshold, distance=min_peak_distance)
    
    if len(peaks) == 0:
        return 0
        
    # Tüm önemli tepeleri frekanslarıyla birlikte al
    peak_freqs = freqs[peaks]
    peak_amps = spectrum[peaks]
    
    # En düşük frekanslı tepeyi seç (genellikle temel frekans)
    fundamental = peak_freqs[0]
    
    return fundamental

# Ses aralığını belirleme fonksiyonu
def identify_voice_range(frequency):
    for voice_type, (low, high) in voice_ranges.items():
        if low <= frequency <= high:
            return voice_type
    return "Bilinmeyen Aralık"

# Mikrofon kaydı alma fonksiyonu
def record_audio(duration, sample_rate):
    print("Dinliyorum...")
    time.sleep(1)
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float64')
    sd.wait()  # Kaydı bitir
    print("kayıt alındı.")
    return recording.flatten()

# Nota çalma fonksiyonu
def play_note(frequency, duration=2, waveform="sine"):
    """Notayı çal"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    
    # Ses dalgasını oluştur
    if waveform == "vocal":
        note = 0.5 * (np.sin(2 * np.pi * frequency * t) + np.sin(2 * np.pi * (frequency / 2) * t))
    else:  # varsayılan olarak sine dalgası kullan
        note = 0.5 * np.sin(2 * np.pi * frequency * t)
    
    # Sesi çal
    audio = np.int16(note * 32767)
    play_obj = sa.play_buffer(audio, 1, 2, SAMPLE_RATE)
    play_obj.wait_done()

def calculate_success_percentage(target_freq, actual_freq, margin):
    """Hedef frekans ile söylenen frekans arasındaki başarı yüzdesini hesapla"""
    if actual_freq == 0:  # Geçersiz frekans tespiti
        return 0

    difference = abs(target_freq - actual_freq)
    if difference > margin:
        return 0
    # Fark margin'a yaklaştıkça başarı yüzdesi daha hızlı düşer (karesel azalma)
    success = ((margin - difference) / margin) ** 2 * 100
    return min(100, max(0, success))  # 0-100 arasında sınırla

# Ana test fonksiyonu (erkek veya kadın için)

def run_voice_test(start_note, direction):
    detected_ranges = []
    index = note_frequencies.index(start_note)
    MAX_ATTEMPTS = 2
    MIN_SUCCESS_RATE = 80
    print("Ses testi başlıyor...")

    while 0 <= index < len(note_frequencies):
        note, frequency = note_frequencies[index]
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

            # Ses sinyalinin gücünü kontrol et
            signal_power = np.mean(np.abs(audio_data))
            if signal_power < 0.01:
                print("Ses seviyesi çok düşük. Lütfen daha yüksek sesle tekrar deneyin.")
                attempts += 1
                if attempts >= MAX_ATTEMPTS:  # Maksimum deneme sayısına ulaşıldıysa testi sonlandır
                    print(f"\nBaşarısız! {MAX_ATTEMPTS} deneme sonunda yeterli ses seviyesine ulaşılamadı.")
                    return detected_ranges
                continue

            print(f"Söylenen frekans: {dominant_freq:.2f} Hz (Başarı: %{success_rate:.1f})")

            if success_rate >= MIN_SUCCESS_RATE:
                detected_ranges.append((turkce_nota, dominant_freq, voice_range))
                index += direction
                break  # Başarılı deneme, sonraki notaya geç
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


def draw_voice_range(min_freq, max_freq, gender):
    """Ses aralığını ve kullanıcının ses aralığını çizer"""
    WIDTH = 100  # Genişliği artırdım daha detaylı gösterim için

    if gender == "e":
        # Erkek ses aralıkları (Hz)
        RANGES = [
            ("Bas", 82.41, 329.63),  # E2-E4
            ("Bariton", 98.00, 392.00),  # G2-G4
            ("Tenor", 130.81, 523.25)  # C3-C5
        ]
    else:
        # Kadın ses aralıkları (Hz)
        RANGES = [
            ("Kontralto", 164.81, 659.26),  # E3-E5
            ("Mezzosoprano", 196.00, 783.99),  # G3-G5
            ("Soprano", 261.63, 1046.50)  # C4-C6
        ]

    TOTAL_MIN = 80  # En düşük frekans
    TOTAL_MAX = 550  # En yüksek frekans (tenor üst sınırını da göstermek için)

    print("\nSes Aralığı Analizi:")

    # Her ses tipi için ayrı çizgi çiz
    for voice_type, low, high in RANGES:
        # Ses tipinin başlangıç ve bitiş pozisyonlarını hesapla
        start_pos = int((low - TOTAL_MIN) / (TOTAL_MAX - TOTAL_MIN) * WIDTH)
        end_pos = int((high - TOTAL_MIN) / (TOTAL_MAX - TOTAL_MIN) * WIDTH)

        # Sınırları kontrol et
        start_pos = max(0, min(start_pos, WIDTH - 1))
        end_pos = max(0, min(end_pos, WIDTH - 1))

        # Ses tipi çizgisini oluştur
        voice_line = [" "] * WIDTH
        for i in range(start_pos, end_pos + 1):
            voice_line[i] = "─"

        # Ses tipinin ismini ve çizgisini yazdır
        print(f"{voice_type:<10} │{''.join(voice_line)}│")
        print(f"          {low:>6.1f}Hz{' ' * (end_pos - start_pos - 8)}{high:<6.1f}Hz")
        print()

    # Kullanıcının ses aralığını göster
    user_line = [" "] * WIDTH
    start_pos = int((min_freq - TOTAL_MIN) / (TOTAL_MAX - TOTAL_MIN) * WIDTH)
    end_pos = int((max_freq - TOTAL_MIN) / (TOTAL_MAX - TOTAL_MIN) * WIDTH)

    # Sınırları kontrol et
    start_pos = max(0, min(start_pos, WIDTH - 1))
    end_pos = max(0, min(end_pos, WIDTH - 1))

    # Kullanıcının aralığını çiz
    for i in range(start_pos, end_pos + 1):
        user_line[i] = "█"

    print("Sizin ses aralığınız:")
    print(f"          │{''.join(user_line)}│")
    print(f"          {min_freq:>6.1f}Hz{' ' * (end_pos - start_pos - 8)}{max_freq:<6.1f}Hz")

    # Ses tipi analizi
    print("\nSes tipi analizi:")
    if min_freq <= 98.0:  # Bas aralığında
        bas_oran = min(100, max(0, (329.63 - min_freq) / (329.63 - 82.41) * 100))
        print(f"Bas özelliği: %{bas_oran:.1f}")

    if 98.0 <= max_freq <= 392.0:  # Bariton aralığında
        bariton_oran = min(100, max(0, (max_freq - 98.0) / (392.0 - 98.0) * 100))
        print(f"Bariton özelliği: %{bariton_oran:.1f}")

    if max_freq >= 130.81:  # Tenor aralığında
        tenor_oran = min(100, max(0, (max_freq - 130.81) / (523.25 - 130.81) * 100))
        print(f"Tenor özelliği: %{tenor_oran:.1f}")

# Mikrofon listesini görüntüleme ve seçme fonksiyonu
def list_and_select_microphone():
    """Kullanılabilir mikrofonları listeler ve kullanıcıya seçim yaptırır"""
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
        
    selection = input("\nKullanmak istediğiniz mikrofonun numarasını girin: ")
    try:
        device_index = input_devices[int(selection)]
        sd.default.device = device_index
        print(f"Seçilen mikrofon: {devices[device_index]['name']}")
        return device_index
    except:
        print("Geçersiz seçim, varsayılan mikrofon kullanılacak.")
        return None

# Kullanıcı seçimi ve başlatma
def main():
    list_and_select_microphone()
    choice = input("Ses aralığını test etmek istediğiniz cinsiyeti seçin (E/K): ").strip().lower()
    if choice == "e":
        print("Orta notadan (Do3 - 130.81 Hz) aşağıya ve yukarıya doğru ses testi yapılacak.")
        start_note = ("C3", 130.81)
    elif choice == "k":
        print("Orta notadan (Do4 - 261.63 Hz) aşağıya ve yukarıya doğru ses testi yapılacak.")
        start_note = ("C4", 261.63)
    else:
        print("Geçersiz seçim. Program sonlanıyor.")
        return

    print("\nÖnce aşağıya doğru test edilecek...")
    results_down = run_voice_test(start_note, direction=-1)

    print("\nŞimdi yukarıya doğru test edilecek...")
    results_up = run_voice_test(start_note, direction=1)

    print("\nTüm test tamamlandı. Tespit edilen notalar:")
    all_results = results_down + results_up
    
    # Frekansları topla
    frequencies = [freq for _, freq, _ in all_results]
    
    for nota, freq, _ in all_results:
        hedef_freq = next(f for n, f in note_frequencies if nota_cevirici(n) == nota)
        basari = calculate_success_percentage(hedef_freq, freq, ACCEPTABLE_MARGIN)
        print(f"Nota: {nota} - Hedef: {hedef_freq:.2f} Hz, Söylenen: {freq:.2f} Hz (Başarı: %{basari:.1f})")
    
    # Ses aralığı görsel gösterimi
    if frequencies:
        draw_voice_range(min(frequencies), max(frequencies), choice)

if __name__ == "__main__":
    main()
