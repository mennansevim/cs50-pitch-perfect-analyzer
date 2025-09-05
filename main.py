from audio_utils import list_and_select_microphone
from voice_analyzer import run_voice_test
from visualization import draw_voice_range

def print_welcome_screen() -> None:
    """Hoşgeldin ekranı."""
    print("🎤" + "="*60 + "🎤")
    print("🎵" + " "*18 + "CS50 PITCH PERFECT ANALYZER" + " "*18 + "🎵")
    print("🎼" + " "*15 + "Advanced Voice Range Detection v2.0" + " "*14 + "🎼")
    print("🎤" + "="*60 + "🎤")
    print()
    print("📋 BU PROGRAM NE YAPAR?")
    print("   🎯 Ses aralığınızı (vocal range) ölçer")
    print("   🎼 Hangi notaları söyleyebildiğinizi test eder")
    print("   📊 Ses tipinizi analiz eder (Soprano, Alto, Tenor, Bas)")
    print("   📈 Detaylı görsel rapor sunar")
    print()
    print("⚡ NASIL ÇALIŞIR?")
    print("   🎹 Program size notalar çalacak")
    print("   🎤 Siz o notaları tekrar söyleyeceksiniz")
    print("   🔍 Sistem sesinizi analiz edecek")
    print("   📊 Sonuçları görsel olarak sunacak")
    print()
    print("💡 İPUÇLARI:")
    print("   🔊 Sakin bir ortamda test yapın")
    print("   🎤 Mikrofona yakın konuşun")
    print("   🎵 Notaları temiz ve net söylemeye çalışın")
    print("   ⏱️  Acele etmeyin, rahat olun")
    print()
    print("🎤" + "="*60 + "🎤")

def print_test_transition(direction: str, total_successful: int) -> None:
    """Test geçiş ekranı."""
    if direction == "bas":
        print("\n" + "🔽"*25)
        print("🔽 BAS SES TESTİ TAMAMLANDI! 🔽")
    else:
        print("\n" + "🔼"*25)
        print("🔼 TİZ SES TESTİ BAŞLIYOR! 🔼")
    
    print(f"✅ Şu ana kadar {total_successful} nota başarıyla tespit edildi!")
    
    if direction == "tiz":
        print("🎯 Şimdi tiz sesler test edilecek...")
        print("💡 Yüksek notalar için:")
        print("   🎵 Sesizi daha ince ve hafif tutun")
        print("   💨 Nefes kontrolünüze dikkat edin")
        print("   😌 Gergin olmamaya çalışın")
    
    print("🔽🔼" * 12 if direction == "bas" else "🔼🔽" * 12)

def print_final_summary(all_results: list, choice: str) -> None:
    """Final özet ekranı."""
    print("\n" + "🏁"*30)
    print("🏁 TEST TAMAMLANDI! 🏁")
    print("="*80)
    
    if not all_results:
        print("😞 Maalesef hiç nota tespit edilemedi.")
        print("💡 Öneriler:")
        print("   🔊 Ses seviyenizi artırın")
        print("   🎤 Mikrofon ayarlarınızı kontrol edin")
        print("   🎵 Daha net konuşmaya çalışın")
        return
    
    # Başarılı notalar listesi
    note_names = [nota for nota, _, _ in all_results]
    frequencies = [freq for _, freq, _ in all_results]
    
    print(f"🎊 TEBRİKLER! {len(all_results)} nota başarıyla tespit edildi!")
    print(f"🎼 Tespit edilen notalar: {' → '.join(note_names)}")
    print(f"📏 Frekans aralığı: {min(frequencies):.1f} Hz - {max(frequencies):.1f} Hz")
    print(f"📐 Toplam ses aralığı genişliği: {max(frequencies) - min(frequencies):.1f} Hz")
    
    # Aralık değerlendirmesi
    range_width = max(frequencies) - min(frequencies)
    if range_width > 200:
        print("🏆 OLAĞANÜSTÜ! Çok geniş bir ses aralığınız var!")
    elif range_width > 150:
        print("⭐ HARIKA! İyi bir ses aralığınız var!")
    elif range_width > 100:
        print("👍 İYİ! Ortalama bir ses aralığınız var!")
    else:
        print("📈 Ses aralığınızı geliştirebilirsiniz!")
    
    print("\n📊 Detaylı analiz aşağıda sunulmaktadır...")
    print("🏁" + "="*78 + "🏁")

def main() -> None:
    """Ana program akışı."""
    print_welcome_screen()
    
    # Mikrofon seçimi
    print("🎤 MİKROFON AYARLARI")
    print("─"*40)
    list_and_select_microphone()
    
    # Cinsiyet seçimi
    print("\n🚻 CİNSİYET SEÇİMİ")
    print("─"*40)
    print("👨 Erkek (e) - Do3 (130.81 Hz) referans notas ile başlar")
    print("👩 Kadın (k) - Do4 (261.63 Hz) referans notas ile başlar")
    choice = input("\n🎯 Lütfen seçiminizi yapın (e/k): ").strip().lower()

    if choice == "e":
        print("\n👨 ERKEK SES TESTİ SEÇİLDİ")
        print("🎼 Referans nota: Do3 (130.81 Hz)")
        start_note = ("C3", 130.81)
    elif choice == "k":
        print("\n👩 KADIN SES TESTİ SEÇİLDİ")
        print("🎼 Referans nota: Do4 (261.63 Hz)")
        start_note = ("C4", 261.63)
    else:
        print("❌ Geçersiz seçim. Program sonlanıyor.")
        return

    print("\n🚀 TEST BAŞLIYOR!")
    print("="*50)

    # Bas seslere doğru test
    results_down = run_voice_test(start_note, direction=-1)
    
    # Geçiş ekranı
    print_test_transition("tiz", len(results_down))
    
    # Tiz seslere doğru test
    results_up = run_voice_test(start_note, direction=1)

    # Final özeti
    all_results = results_down + results_up
    print_final_summary(all_results, choice)
    
    # Görsel analiz
    frequencies = [freq for _, freq, _ in all_results]
    if frequencies:
        min_freq = min(frequencies)
        max_freq = max(frequencies)
        draw_voice_range(min_freq, max_freq, choice)

if __name__ == "__main__":
    main() 