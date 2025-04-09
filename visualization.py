from typing import List
from config import VISUALIZATION_WIDTH, TOTAL_MIN_FREQ, TOTAL_MAX_FREQ

def draw_voice_range(min_freq: float, max_freq: float, gender: str) -> None:
    """Ses aralığını görsel olarak gösterir."""
    WIDTH = VISUALIZATION_WIDTH

    if gender == "e":
        RANGES = [
            ("Bas", 82.41, 329.63),
            ("Bariton", 98.00, 392.00),
            ("Tenor", 130.81, 523.25)
        ]
    else:
        RANGES = [
            ("Kontralto", 164.81, 659.26),
            ("Mezzosoprano", 196.00, 783.99),
            ("Soprano", 261.63, 1046.50)
        ]

    print("\nSes Aralığı Analizi:")

    for voice_type, low, high in RANGES:
        start_pos = int((low - TOTAL_MIN_FREQ) / (TOTAL_MAX_FREQ - TOTAL_MIN_FREQ) * WIDTH)
        end_pos = int((high - TOTAL_MIN_FREQ) / (TOTAL_MAX_FREQ - TOTAL_MIN_FREQ) * WIDTH)

        start_pos = max(0, min(start_pos, WIDTH - 1))
        end_pos = max(0, min(end_pos, WIDTH - 1))

        voice_line = [" "] * WIDTH
        for i in range(start_pos, end_pos + 1):
            voice_line[i] = "─"

        print(f"{voice_type:<10} │{''.join(voice_line)}│")
        print(f"          {low:>6.1f}Hz{' ' * (end_pos - start_pos - 8)}{high:<6.1f}Hz")
        print()

    user_line = [" "] * WIDTH
    start_pos = int((min_freq - TOTAL_MIN_FREQ) / (TOTAL_MAX_FREQ - TOTAL_MIN_FREQ) * WIDTH)
    end_pos = int((max_freq - TOTAL_MIN_FREQ) / (TOTAL_MAX_FREQ - TOTAL_MIN_FREQ) * WIDTH)

    start_pos = max(0, min(start_pos, WIDTH - 1))
    end_pos = max(0, min(end_pos, WIDTH - 1))

    for i in range(start_pos, end_pos + 1):
        user_line[i] = "█"

    print("Sizin ses aralığınız:")
    print(f"          │{''.join(user_line)}│")
    print(f"          {min_freq:>6.1f}Hz{' ' * (end_pos - start_pos - 8)}{max_freq:<6.1f}Hz")

    print("\nSes tipi analizi:")
    if min_freq <= 98.0:
        bas_oran = min(100, max(0, (329.63 - min_freq) / (329.63 - 82.41) * 100))
        print(f"Bas özelliği: %{bas_oran:.1f}")

    if 98.0 <= max_freq <= 392.0:
        bariton_oran = min(100, max(0, (max_freq - 98.0) / (392.0 - 98.0) * 100))
        print(f"Bariton özelliği: %{bariton_oran:.1f}")

    if max_freq >= 130.81:
        tenor_oran = min(100, max(0, (max_freq - 130.81) / (523.25 - 130.81) * 100))
        print(f"Tenor özelliği: %{tenor_oran:.1f}") 