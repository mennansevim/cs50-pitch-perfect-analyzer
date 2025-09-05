from typing import List, Tuple
from config import VISUALIZATION_WIDTH, TOTAL_MIN_FREQ, TOTAL_MAX_FREQ

def calculate_voice_type_percentages(min_freq: float, max_freq: float, gender: str) -> List[Tuple[str, float]]:
    """Kullanıcının ses tipine uygunluk yüzdelerini hesaplar."""
    voice_percentages = []
    
    if gender == "e":
        ranges = [
            ("Bas", 82.41, 329.63),
            ("Bariton", 98.00, 392.00),
            ("Tenor", 130.81, 523.25)
        ]
    else:
        ranges = [
            ("Kontralto", 164.81, 659.26),
            ("Mezzosoprano", 196.00, 783.99),
            ("Soprano", 261.63, 1046.50)
        ]
    
    for voice_type, low, high in ranges:
        # Kullanıcı aralığı ile ses tipi aralığının kesişimini bul
        overlap_start = max(min_freq, low)
        overlap_end = min(max_freq, high)
        
        if overlap_start <= overlap_end:
            # Kesişim var
            overlap_range = overlap_end - overlap_start
            voice_type_range = high - low
            user_range = max_freq - min_freq
            
            # Hem ses tipi kapsamına hem de kullanıcı aralığına göre yüzde hesapla
            coverage_of_voice_type = (overlap_range / voice_type_range) * 100
            coverage_of_user = (overlap_range / user_range) * 100
            
            # Ortalama al ve bonus ver
            average_coverage = (coverage_of_voice_type + coverage_of_user) / 2
            voice_percentages.append((voice_type, min(100, average_coverage)))
        else:
            voice_percentages.append((voice_type, 0))
    
    return voice_percentages

def draw_voice_range(min_freq: float, max_freq: float, gender: str) -> None:
    """Ses aralığını görsel olarak gösterir."""
    WIDTH = VISUALIZATION_WIDTH

    if gender == "e":
        RANGES = [
            ("Bas", 82.41, 329.63, "🎵"),
            ("Bariton", 98.00, 392.00, "🎶"),
            ("Tenor", 130.81, 523.25, "🎼")
        ]
        gender_text = "ERKEK"
    else:
        RANGES = [
            ("Kontralto", 164.81, 659.26, "🎵"),
            ("Mezzosoprano", 196.00, 783.99, "🎶"),
            ("Soprano", 261.63, 1046.50, "🎼")
        ]
        gender_text = "KADIN"

    print("\n" + "🎤"*30 + " SES ANALİZİ " + "🎤"*30)
    print(f"📊 {gender_text} SES ARALIĞI ANALİZİ 📊")
    print("="*80)
    
    # Ana grafik
    print(f"\n🎯 SES ARALIĞI GRAFİĞİ (Frekans: {TOTAL_MIN_FREQ}-{TOTAL_MAX_FREQ} Hz)")
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

    # Kullanıcının aralığı
    user_start_pos = int((min_freq - TOTAL_MIN_FREQ) / (TOTAL_MAX_FREQ - TOTAL_MIN_FREQ) * WIDTH)
    user_end_pos = int((max_freq - TOTAL_MIN_FREQ) / (TOTAL_MAX_FREQ - TOTAL_MIN_FREQ) * WIDTH)

    user_start_pos = max(0, min(user_start_pos, WIDTH - 1))
    user_end_pos = max(0, min(user_end_pos, WIDTH - 1))

    user_line = [" "] * WIDTH
    for i in range(user_start_pos, user_end_pos + 1):
        user_line[i] = "█"

    print("🎤 SİZİN SES ARALIĞINIZ:")
    print("┌" + "─"*WIDTH + "┐")
    print(f"│{''.join(user_line)}│ 🔊 Sizin sesiniz")
    print("└" + "─"*WIDTH + "┘")
    print(f" {' '*user_start_pos}{min_freq:.1f}Hz{' '*(user_end_pos-user_start_pos-len(f'{min_freq:.1f}')-len(f'{max_freq:.1f}')-2)}{max_freq:.1f}Hz")

    # Aralık bilgisi
    range_width = max_freq - min_freq
    print(f"\n📏 SES ARALIĞI GENİŞLİĞİ: {range_width:.1f} Hz")
    
    if range_width > 200:
        print("🏆 GENIŞ ARALIK! Çok iyi bir ses aralığınız var!")
    elif range_width > 150:
        print("👍 İYİ ARALIK! Güzel bir ses aralığınız var!")
    elif range_width > 100:
        print("✅ ORTA ARALIK! Kabul edilebilir bir ses aralığınız var!")
    else:
        print("📈 DAR ARALIK! Daha fazla çalışmayla geliştirebilirsiniz!")

    # Ses tipi analizi
    voice_percentages = calculate_voice_type_percentages(min_freq, max_freq, gender)
    
    print(f"\n🎭 SES TİPİ ANALİZİ:")
    print("─"*50)
    
    best_match = max(voice_percentages, key=lambda x: x[1])
    
    for voice_type, percentage in voice_percentages:
        # Progress bar
        bar_length = 25
        filled_length = int(bar_length * percentage / 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        # İkon ve stil
        if voice_type == best_match[0] and percentage > 50:
            icon = "🏆"
            status = "EN UYGUN"
        elif percentage > 70:
            icon = "⭐"
            status = "ÇOK UYGUN"
        elif percentage > 50:
            icon = "👍"
            status = "UYGUN"
        elif percentage > 30:
            icon = "📊"
            status = "KISMEN"
        else:
            icon = "❌"
            status = "UYGUN DEĞİL"
        
        print(f"{icon} {voice_type:<12} [{bar}] %{percentage:5.1f} - {status}")
    
    # Sonuç
    print(f"\n🎯 SONUÇ: ", end="")
    if best_match[1] > 70:
        print(f"🏆 '{best_match[0]}' (%{best_match[1]:.1f} uygunluk - Mükemmel eşleşme!)")
    elif best_match[1] > 50:
        print(f"⭐ '{best_match[0]}' (%{best_match[1]:.1f} uygunluk - İyi eşleşme!)")
    else:
        print(f"📊 '{best_match[0]}' (%{best_match[1]:.1f} uygunluk - Gelişebilir)")
    
    print("🎤" + "="*76 + "🎤") 