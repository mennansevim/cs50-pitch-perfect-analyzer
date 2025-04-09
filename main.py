from audio_utils import list_and_select_microphone
from voice_analyzer import run_voice_test
from visualization import draw_voice_range

def main() -> None:
    """Ana program akışı."""

    list_and_select_microphone()
    choice = input("Ses aralığını test etmek istediğiniz cinsiyeti seçin (e/k): ").strip().lower()

    if choice == "e":
        print("Orta notadan (Do3 - 130.81 Hz) baslara ve tizlere doğru ses testi yapılacak.")
        start_note = ("C3", 130.81)
    elif choice == "k":
        print("Orta notadan (Do4 - 261.63 Hz) baslara ve tizlere doğru ses testi yapılacak.")
        start_note = ("C4", 261.63)
    else:
        print("Geçersiz seçim. Program sonlanıyor.")
        return

    print("\nÖnce bas seslere doğru test edilecek...")
    results_down = run_voice_test(start_note, direction=-1)

    print("\nŞimdi tizlere doğru test edilecek...")
    results_up = run_voice_test(start_note, direction=1)

    print("\nTüm test tamamlandı. Tespit edilen notalar:")
    all_results = results_down + results_up
    
    frequencies = [freq for _, freq, _ in all_results]
    
    if frequencies:
        min_freq = min(frequencies)
        max_freq = max(frequencies)
        draw_voice_range(min_freq, max_freq, choice)

if __name__ == "__main__":
    main() 