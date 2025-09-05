from audio_utils import list_and_select_microphone
from voice_analyzer import run_voice_test
from visualization import draw_voice_range
from database import (
    init_database, 
    get_user_information, 
    save_or_update_user,
    save_test_results,
    show_scoreboard,
    show_personal_statistics,
    show_test_history,
    show_database_tables,
    show_merge_sort_info,
    restore_default_database
)

def print_welcome_screen() -> None:
    """Welcome screen."""
    print("🎤" + "="*60 + "🎤")
    print("🎵" + " "*18 + "CS50 PITCH PERFECT ANALYZER" + " "*18 + "🎵")
    print("🎼" + " "*15 + "Advanced Voice Range Detection v2.0" + " "*14 + "🎼")
    print("🎤" + "="*60 + "🎤")
    print()
    print("📋 WHAT DOES THIS PROGRAM DO?")
    print("   🎯 Measures your vocal range")
    print("   🎼 Tests which notes you can sing")
    print("   📊 Analyzes your voice type (Soprano, Alto, Tenor, Bass)")
    print("   📈 Provides detailed visual reports")
    print()
    print("⚡ HOW DOES IT WORK?")
    print("   🎹 Program will play notes for you")
    print("   🎤 You sing those notes back")
    print("   🔍 System analyzes your voice")
    print("   📊 Results are presented visually")
    print()
    print("💡 TIPS:")
    print("   🔊 Test in a quiet environment")
    print("   🎤 Speak close to the microphone")
    print("   🎵 Try to sing notes clearly and cleanly")
    print("   ⏱️  Don't rush, stay relaxed")
    print()
    print("🎤" + "="*60 + "🎤")

def print_test_transition(direction: str, total_successful: int) -> None:
    """Test transition screen."""
    if direction == "bass":
        print("\n" + "🔽"*25)
        print("🔽 BASS VOICE TEST COMPLETED! 🔽")
    else:
        print("\n" + "🔼"*25)
        print("🔼 HIGH VOICE TEST STARTING! 🔼")
    
    print(f"✅ {total_successful} notes successfully detected so far!")
    
    if direction == "treble":
        print("🎯 Now testing high notes...")
        print("💡 For high notes:")
        print("   🎵 Keep your voice lighter and thinner")
        print("   💨 Pay attention to breath control")
        print("   😌 Try not to be tense")
    
    print("🔽🔼" * 12 if direction == "bass" else "🔼🔽" * 12)

def print_final_summary(all_results: list, choice: str) -> None:
    """Final summary screen."""
    print("\n" + "🏁"*30)
    print("🏁 TEST COMPLETED! 🏁")
    print("="*80)
    
    if not all_results:
        print("😞 Unfortunately, no notes were detected.")
        print("💡 Suggestions:")
        print("   🔊 Increase your volume")
        print("   🎤 Check your microphone settings")
        print("   🎵 Try to speak more clearly")
        return
    
    # List of successful notes
    note_names = [nota for nota, _, _ in all_results]
    frequencies = [freq for _, freq, _ in all_results]
    
    print(f"🎊 CONGRATULATIONS! {len(all_results)} notes successfully detected!")
    print(f"🎼 Detected notes: {' → '.join(note_names)}")
    print(f"📏 Frequency range: {min(frequencies):.1f} Hz - {max(frequencies):.1f} Hz")
    print(f"📐 Total vocal range width: {max(frequencies) - min(frequencies):.1f} Hz")
    
    # Range evaluation
    range_width = max(frequencies) - min(frequencies)
    if range_width > 200:
        print("🏆 EXTRAORDINARY! You have a very wide vocal range!")
    elif range_width > 150:
        print("⭐ GREAT! You have a good vocal range!")
    elif range_width > 100:
        print("👍 GOOD! You have an average vocal range!")
    else:
        print("📈 You can improve your vocal range!")
    
    print("\n📊 Detailed analysis is presented below...")
    print("🏁" + "="*78 + "🏁")

def show_main_menu() -> str:
    """Shows main menu and returns user choice."""
    print("\n🎛️  MAIN MENU")
    print("─"*50)
    print("1. 🎤 Start Voice Test (t)")
    print("2. 🏆 View Top 10 Scoreboard (s)")
    print("3. 🗄️  View Database Tables (d)")
    print("4. 🎓 CS50 Merge Sort Info (a)")
    print("5. 🔄 Restore Database to Default (r)")
    print("6. 🚪 Exit (q)")
    
    while True:
        choice = input("\n🎯 Select an option (1-6 or letter): ").strip().lower()
        if choice in ['1', 't', '2', 's', '3', 'd', '4', 'a', '5', 'r', '6', 'q']:
            return choice
        print("❌ Invalid selection. Please choose 1-6 or corresponding letter.")

def main() -> None:
    """Main program flow."""
    # Initialize database
    init_database()
    
    print_welcome_screen()
    
    # Show main menu
    while True:
        choice = show_main_menu()
        
        if choice in ['6', 'q']:
            print("\n👋 Thank you for using CS50 Pitch Perfect Analyzer!")
            print("🎵 Keep practicing your voice! 🎵")
            return
        elif choice in ['2', 's']:
            show_scoreboard()
            input("\n⏸️  Press Enter to continue...")
            continue
        elif choice in ['3', 'd']:
            show_database_tables()
            input("\n⏸️  Press Enter to continue...")
            continue
        elif choice in ['4', 'a']:
            show_merge_sort_info()
            input("\n⏸️  Press Enter to continue...")
            continue
        elif choice in ['5', 'r']:
            restore_default_database()
            input("\n⏸️  Press Enter to continue...")
            continue
        elif choice in ['1', 't']:
            break  # Continue to voice test
        
    # Get user information
    first_name, last_name = get_user_information()
    
    # Microphone selection
    print("\n🎤 MICROPHONE SETTINGS")
    print("─"*40)
    list_and_select_microphone()
    
    # Gender selection
    print("\n🚻 GENDER SELECTION")
    print("─"*40)
    print("👨 Male (m) - Starts with C3 (130.81 Hz) reference note")
    print("👩 Female (f) - Starts with C4 (261.63 Hz) reference note")
    choice = input("\n🎯 Please make your selection (m/f): ").strip().lower()

    if choice == "m":
        gender = "erkek"
        print("\n👨 MALE VOICE TEST SELECTED")
        print("🎼 Reference note: C3 (130.81 Hz)")
        start_note = ("C3", 130.81)
    elif choice == "f":
        gender = "kadın"
        print("\n👩 FEMALE VOICE TEST SELECTED")
        print("🎼 Reference note: C4 (261.63 Hz)")
        start_note = ("C4", 261.63)
    else:
        print("❌ Invalid selection. Program terminating.")
        return

    # Save user to database
    user_id = save_or_update_user(first_name, last_name, gender)
    print(f"👤 Hello {first_name} {last_name}! You have been registered in the system.")

    print("\n🚀 TEST STARTING!")
    print("="*50)

    # Test towards bass notes
    results_down, history_down = run_voice_test(start_note, direction=-1)
    
    # Transition screen
    print_test_transition("treble", len(results_down))
    
    # Test towards treble notes
    results_up, history_up = run_voice_test(start_note, direction=1)

    # Final summary
    all_results = results_down + results_up
    all_history = history_down + history_up
    print_final_summary(all_results, choice)
    
    # Save test results to database
    if all_results:
        test_result_id = save_test_results(user_id, all_results, gender, all_history)
        
        # Show personal statistics
        show_personal_statistics(user_id)
    
    # Visual analysis
    frequencies = [freq for _, freq, _ in all_results]
    if frequencies:
        min_freq = min(frequencies)
        max_freq = max(frequencies)
        draw_voice_range(min_freq, max_freq, choice)
    
    # Show scoreboard and detailed history
    print("\n🎯 ADDITIONAL REPORTS AND CS50 MERGE SORT")
    print("─"*50)
    print("1. Scoreboard (with CS50 Merge Sort) (s)")
    print("2. Detailed test history (h)")
    print("3. Database tables (d)")
    print("4. CS50 Merge Sort algorithm info (a)")
    print("5. Show all (t)")
    print("6. Restore database to default (r)")
    print("7. Show none (n)")
    
    report_choice = input("\nMake your selection: ").strip().lower()
    
    if report_choice in ['s', 't']:
        show_scoreboard()
    
    if report_choice in ['h', 't'] and all_results:
        show_test_history(user_id)
    
    if report_choice in ['d', 't']:
        show_database_tables()
    
    if report_choice in ['a', 't']:
        show_merge_sort_info()
    
    if report_choice == 'r':
        restore_default_database()

if __name__ == "__main__":
    main() 