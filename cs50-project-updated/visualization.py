from typing import List, Tuple
from config import VISUALIZATION_WIDTH, TOTAL_MIN_FREQ, TOTAL_MAX_FREQ

def calculate_voice_type_percentages(min_freq: float, max_freq: float, gender: str) -> List[Tuple[str, float]]:
    """Calculates user's voice type compatibility percentages."""
    voice_percentages = []
    
    if gender == "m":
        ranges = [
            ("Bass", 82.41, 329.63),
            ("Baritone", 98.00, 392.00),
            ("Tenor", 130.81, 523.25)
        ]
    else:
        ranges = [
            ("Contralto", 164.81, 659.26),
            ("Mezzo-soprano", 196.00, 783.99),
            ("Soprano", 261.63, 1046.50)
        ]
    
    for voice_type, low, high in ranges:
        # Find intersection between user range and voice type range
        overlap_start = max(min_freq, low)
        overlap_end = min(max_freq, high)
        
        if overlap_start <= overlap_end:
            # Intersection exists
            overlap_range = overlap_end - overlap_start
            voice_type_range = high - low
            user_range = max_freq - min_freq
            
            # Calculate percentage based on both voice type coverage and user range
            coverage_of_voice_type = (overlap_range / voice_type_range) * 100
            coverage_of_user = (overlap_range / user_range) * 100
            
            # Take average and apply bonus
            average_coverage = (coverage_of_voice_type + coverage_of_user) / 2
            voice_percentages.append((voice_type, min(100, average_coverage)))
        else:
            voice_percentages.append((voice_type, 0))
    
    return voice_percentages

def draw_voice_range(min_freq: float, max_freq: float, gender: str) -> None:
    """Displays voice range visually."""
    WIDTH = VISUALIZATION_WIDTH

    if gender == "m":
        RANGES = [
            ("Bass", 82.41, 329.63, "🎵"),
            ("Baritone", 98.00, 392.00, "🎶"),
            ("Tenor", 130.81, 523.25, "🎼")
        ]
        gender_text = "MALE"
    else:
        RANGES = [
            ("Contralto", 164.81, 659.26, "🎵"),
            ("Mezzo-soprano", 196.00, 783.99, "🎶"),
            ("Soprano", 261.63, 1046.50, "🎼")
        ]
        gender_text = "FEMALE"

    print("\n" + "🎤"*30 + " VOICE ANALYSIS " + "🎤"*30)
    print(f"📊 {gender_text} VOICE RANGE ANALYSIS 📊")
    print("="*80)
    
    # Main chart
    print(f"\n🎯 VOICE RANGE CHART (Frequency: {TOTAL_MIN_FREQ}-{TOTAL_MAX_FREQ} Hz)")
    print("┌" + "─"*WIDTH + "┐")

    for voice_type, low, high, icon in RANGES:
        start_pos = int((low - TOTAL_MIN_FREQ) / (TOTAL_MAX_FREQ - TOTAL_MIN_FREQ) * WIDTH)
        end_pos = int((high - TOTAL_MIN_FREQ) / (TOTAL_MAX_FREQ - TOTAL_MIN_FREQ) * WIDTH)

        start_pos = max(0, min(start_pos, WIDTH - 1))
        end_pos = max(0, min(end_pos, WIDTH - 1))

        voice_line = [" "] * WIDTH
        for i in range(start_pos, end_pos + 1):
            voice_line[i] = "▓"

        print(f"│{''.join(voice_line)}│ {icon} {voice_type}")
        print(f"└{'─'*start_pos}┬{'─'*(end_pos-start_pos)}┬{'─'*(WIDTH-end_pos-1)}┘")
        print(f" {' '*start_pos}{low:.0f}Hz{' '*(end_pos-start_pos-len(str(int(low)))-len(str(int(high)))-2)}{high:.0f}Hz")
        print()

    # User's range
    user_start_pos = int((min_freq - TOTAL_MIN_FREQ) / (TOTAL_MAX_FREQ - TOTAL_MIN_FREQ) * WIDTH)
    user_end_pos = int((max_freq - TOTAL_MIN_FREQ) / (TOTAL_MAX_FREQ - TOTAL_MIN_FREQ) * WIDTH)

    user_start_pos = max(0, min(user_start_pos, WIDTH - 1))
    user_end_pos = max(0, min(user_end_pos, WIDTH - 1))

    user_line = [" "] * WIDTH
    for i in range(user_start_pos, user_end_pos + 1):
        user_line[i] = "█"

    print("🎤 YOUR VOICE RANGE:")
    print("┌" + "─"*WIDTH + "┐")
    print(f"│{''.join(user_line)}│ 🔊 Your voice")
    print("└" + "─"*WIDTH + "┘")
    print(f" {' '*user_start_pos}{min_freq:.1f}Hz{' '*(user_end_pos-user_start_pos-len(f'{min_freq:.1f}')-len(f'{max_freq:.1f}')-2)}{max_freq:.1f}Hz")

    # Range information
    range_width = max_freq - min_freq
    print(f"\n📏 VOICE RANGE WIDTH: {range_width:.1f} Hz")
    
    if range_width > 200:
        print("🏆 WIDE RANGE! You have an excellent voice range!")
    elif range_width > 150:
        print("👍 GOOD RANGE! You have a nice voice range!")
    elif range_width > 100:
        print("✅ AVERAGE RANGE! You have an acceptable voice range!")
    else:
        print("📈 NARROW RANGE! You can improve with more practice!")

    # Voice type analysis
    voice_percentages = calculate_voice_type_percentages(min_freq, max_freq, gender)
    
    print(f"\n🎭 VOICE TYPE ANALYSIS:")
    print("─"*50)
    
    best_match = max(voice_percentages, key=lambda x: x[1])
    
    for voice_type, percentage in voice_percentages:
        # Progress bar
        bar_length = 25
        filled_length = int(bar_length * percentage / 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        # Icon and style
        if voice_type == best_match[0] and percentage > 50:
            icon = "🏆"
            status = "BEST MATCH"
        elif percentage > 70:
            icon = "⭐"
            status = "VERY SUITABLE"
        elif percentage > 50:
            icon = "👍"
            status = "SUITABLE"
        elif percentage > 30:
            icon = "📊"
            status = "PARTIAL"
        else:
            icon = "❌"
            status = "NOT SUITABLE"
        
        print(f"{icon} {voice_type:<12} [{bar}] %{percentage:5.1f} - {status}")
    
    # Result
    print(f"\n🎯 RESULT: ", end="")
    if best_match[1] > 70:
        print(f"🏆 '{best_match[0]}' ({best_match[1]:.1f}% compatibility - Perfect match!)")
    elif best_match[1] > 50:
        print(f"⭐ '{best_match[0]}' ({best_match[1]:.1f}% compatibility - Good match!)")
    else:
        print(f"📊 '{best_match[0]}' ({best_match[1]:.1f}% compatibility - Can improve)")
    
    print("🎤" + "="*76 + "🎤") 