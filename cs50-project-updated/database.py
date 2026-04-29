"""
SQLite veritabanı yönetimi ve scoreboard sistemi.
CS50 Pitch Perfect Analyzer Database Module
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager

DATABASE_PATH = "pitch_perfect.db"

@contextmanager
def get_db_connection():
    """Veritabanı bağlantısı context manager."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Dict-like access
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Initializes database and creates tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Voice types table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voice_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type_name TEXT NOT NULL UNIQUE,
                gender TEXT NOT NULL CHECK (gender IN ('male', 'female')),
                min_frequency REAL NOT NULL,
                max_frequency REAL NOT NULL,
                description TEXT
            )
        """)
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                gender TEXT NOT NULL CHECK (gender IN ('male', 'female')),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(first_name, last_name, gender)
            )
        """)
        
        # Test results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                voice_type_id INTEGER,
                min_frequency REAL NOT NULL,
                max_frequency REAL NOT NULL,
                frequency_range_width REAL NOT NULL,
                octave_range_width REAL NOT NULL,
                total_notes_count INTEGER NOT NULL,
                successful_notes_count INTEGER NOT NULL,
                success_rate REAL NOT NULL,
                voice_type_match_percentage REAL,
                possible_voice_groups TEXT,  -- Bass,Baritone or Soprano,Mezzo-soprano etc.
                lowest_achievable_note TEXT,
                highest_achievable_note TEXT,
                test_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (voice_type_id) REFERENCES voice_types (id)
            )
        """)
        
        # Voice analyzer history table - detailed test history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voice_analyzer_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_result_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                note_name TEXT NOT NULL,
                target_frequency REAL NOT NULL,
                detected_frequency REAL,
                octave_number INTEGER,
                accuracy_percentage REAL,
                attempt_number INTEGER DEFAULT 1,
                is_successful BOOLEAN DEFAULT 0,
                test_direction TEXT CHECK (test_direction IN ('down', 'up')),
                recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (test_result_id) REFERENCES test_results (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Initial voice types data
        voice_types_data = [
            ('Bass', 'male', 82.41, 329.63, 'Lowest male voice type'),
            ('Baritone', 'male', 98.00, 392.00, 'Middle male voice type'),
            ('Tenor', 'male', 130.81, 523.25, 'Highest male voice type'),
            ('Contralto', 'female', 164.81, 659.26, 'Lowest female voice type'),
            ('Mezzo-soprano', 'female', 196.00, 783.99, 'Middle female voice type'),
            ('Soprano', 'female', 261.63, 1046.50, 'Highest female voice type')
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO voice_types (type_name, gender, min_frequency, max_frequency, description)
            VALUES (?, ?, ?, ?, ?)
        """, voice_types_data)
        
        conn.commit()
        print("✅ Database initialized successfully!")

def get_user_information() -> Tuple[str, str]:
    """Gets user's first name and last name."""
    print("\n👤 USER INFORMATION")
    print("─"*40)
    
    while True:
        first_name = input("📝 Your first name: ").strip().title()
        if first_name and len(first_name) >= 2:
            break
        print("❌ Please enter a valid first name (at least 2 characters)")
    
    while True:
        last_name = input("📝 Your last name: ").strip().title()
        if last_name and len(last_name) >= 2:
            break
        print("❌ Please enter a valid last name (at least 2 characters)")
    
    return first_name, last_name

def save_or_update_user(first_name: str, last_name: str, gender: str) -> int:
    """Saves user or returns existing user's ID."""
    # Convert Turkish gender to English
    gender_map = {'erkek': 'male', 'kadın': 'female'}
    db_gender = gender_map.get(gender, gender)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check existing user
        cursor.execute("""
            SELECT id FROM users 
            WHERE first_name = ? AND last_name = ? AND gender = ?
        """, (first_name, last_name, db_gender))
        
        result = cursor.fetchone()
        if result:
            return result['id']
        
        # Add new user
        cursor.execute("""
            INSERT INTO users (first_name, last_name, gender)
            VALUES (?, ?, ?)
        """, (first_name, last_name, db_gender))
        
        conn.commit()
        return cursor.lastrowid

def calculate_octave_width(min_freq: float, max_freq: float) -> float:
    """Calculates octave width (log2 based)."""
    import math
    if min_freq <= 0 or max_freq <= 0:
        return 0.0
    return math.log2(max_freq / min_freq)

def find_best_voice_type(min_freq: float, max_freq: float, gender: str) -> Tuple[Optional[int], float, str]:
    """Finds the best matching voice type and calculates match percentage."""
    # Convert Turkish gender to English
    gender_map = {'erkek': 'male', 'kadın': 'female'}
    db_gender = gender_map.get(gender, gender)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, type_name, min_frequency, max_frequency 
            FROM voice_types 
            WHERE gender = ?
        """, (db_gender,))
        
        voice_types = cursor.fetchall()
        best_match_id = None
        highest_percentage = 0.0
        possible_groups = []
        
        for voice_type in voice_types:
            # Calculate overlap
            overlap_min = max(min_freq, voice_type['min_frequency'])
            overlap_max = min(max_freq, voice_type['max_frequency'])
            
            if overlap_max > overlap_min:
                overlap_range = overlap_max - overlap_min
                user_range = max_freq - min_freq
                match_percentage = (overlap_range / user_range) * 100
                
                if match_percentage > 20:  # Consider as possible group if >20% overlap
                    possible_groups.append(voice_type['type_name'])
                
                if match_percentage > highest_percentage:
                    highest_percentage = match_percentage
                    best_match_id = voice_type['id']
        
        possible_voice_groups = ','.join(possible_groups)
        return best_match_id, highest_percentage, possible_voice_groups

def save_test_results(user_id: int, test_results: List, gender: str, test_history: List) -> int:
    """Saves test results and detailed history to database."""
    if not test_results:
        print("❌ No test results found to save!")
        return None
    
    # Calculate frequency information
    frequencies = [freq for _, freq, _ in test_results]
    min_freq = min(frequencies)
    max_freq = max(frequencies)
    frequency_range_width = max_freq - min_freq
    octave_range_width = calculate_octave_width(min_freq, max_freq)
    
    # Calculate success rate
    successful_notes_count = len(test_results)
    total_notes_count = successful_notes_count  # Only successful notes are recorded
    success_rate = 100.0  # All recorded notes are successful
    
    # Find best voice type
    voice_type_id, voice_type_match_percentage, possible_voice_groups = find_best_voice_type(min_freq, max_freq, gender)
    
    # Determine note range
    note_names = [note for note, _, _ in test_results]
    lowest_achievable_note = note_names[-1] if note_names else None
    highest_achievable_note = note_names[0] if note_names else None
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check existing record (update if same user has previous result)
        cursor.execute("""
            SELECT id FROM test_results WHERE user_id = ?
            ORDER BY test_date DESC LIMIT 1
        """, (user_id,))
        
        existing_record = cursor.fetchone()
        
        if existing_record:
            # Update existing record
            cursor.execute("""
                UPDATE test_results SET
                    voice_type_id = ?,
                    min_frequency = ?,
                    max_frequency = ?,
                    frequency_range_width = ?,
                    octave_range_width = ?,
                    total_notes_count = ?,
                    successful_notes_count = ?,
                    success_rate = ?,
                    voice_type_match_percentage = ?,
                    possible_voice_groups = ?,
                    lowest_achievable_note = ?,
                    highest_achievable_note = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (voice_type_id, min_freq, max_freq, frequency_range_width, 
                  octave_range_width, total_notes_count, successful_notes_count,
                  success_rate, voice_type_match_percentage, possible_voice_groups,
                  lowest_achievable_note, highest_achievable_note, existing_record['id']))
            test_result_id = existing_record['id']
            print("🔄 Your test result has been updated!")
        else:
            # Insert new record
            cursor.execute("""
                INSERT INTO test_results (
                    user_id, voice_type_id, min_frequency, max_frequency,
                    frequency_range_width, octave_range_width, total_notes_count,
                    successful_notes_count, success_rate, voice_type_match_percentage,
                    possible_voice_groups, lowest_achievable_note, highest_achievable_note
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, voice_type_id, min_freq, max_freq,
                  frequency_range_width, octave_range_width, total_notes_count,
                  successful_notes_count, success_rate, voice_type_match_percentage,
                  possible_voice_groups, lowest_achievable_note, highest_achievable_note))
            test_result_id = cursor.lastrowid
            print("💾 Your test result has been saved!")
        
        # Clear previous history for this test result
        cursor.execute("DELETE FROM voice_analyzer_history WHERE test_result_id = ?", (test_result_id,))
        
        # Save detailed test history
        for history_item in test_history:
            cursor.execute("""
                INSERT INTO voice_analyzer_history (
                    test_result_id, user_id, note_name, target_frequency,
                    detected_frequency, octave_number, accuracy_percentage,
                    attempt_number, is_successful, test_direction
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                test_result_id, user_id, history_item['note_name'], 
                history_item['target_frequency'], history_item['detected_frequency'],
                history_item['octave_number'], history_item['accuracy_percentage'],
                history_item['attempt_number'], history_item['is_successful'],
                history_item['test_direction']
            ))
        
        conn.commit()
        return test_result_id

def merge_sort_scores(arr, key_func):
    """CS50 Merge Sort algorithm for scoreboard ranking - O(n log n)."""
    if len(arr) <= 1:
        return arr
    
    # Divide
    mid = len(arr) // 2
    left = merge_sort_scores(arr[:mid], key_func)
    right = merge_sort_scores(arr[mid:], key_func)
    
    # Conquer (merge)
    merged = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        # Compare using key function (descending order for higher scores)
        if key_func(left[i]) >= key_func(right[j]):
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    
    # Add remaining elements
    merged.extend(left[i:])
    merged.extend(right[j:])
    
    return merged


def calculate_score(result):
    """Calculate composite score for ranking using CS50-style algorithm."""
    # Weight factors (can be adjusted)
    range_weight = 0.6      # 60% weight for frequency range
    octave_weight = 0.3     # 30% weight for octave range  
    notes_weight = 0.1      # 10% weight for successful notes
    
    # Normalize scores (0-100 scale)
    range_score = min(result['frequency_range_width'] / 5.0, 100)  # Max expected: 500Hz
    octave_score = min(result['octave_range_width'] * 25, 100)     # Max expected: 4 octaves
    notes_score = min(result['successful_notes_count'] * 5, 100)   # Max expected: 20 notes
    
    # Composite score
    composite_score = (range_score * range_weight + 
                      octave_score * octave_weight + 
                      notes_score * notes_weight)
    
    return composite_score

def show_scoreboard() -> None:
    """Shows Top 10 scoreboard using CS50 Merge Sort algorithm."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get ALL results (no SQL sorting)
        cursor.execute("""
            SELECT 
                u.first_name,
                u.last_name,
                u.gender,
                vt.type_name,
                tr.frequency_range_width,
                tr.octave_range_width,
                tr.min_frequency,
                tr.max_frequency,
                tr.voice_type_match_percentage,
                tr.test_date,
                tr.successful_notes_count,
                tr.possible_voice_groups,
                tr.lowest_achievable_note,
                tr.highest_achievable_note
            FROM test_results tr
            JOIN users u ON tr.user_id = u.id
            LEFT JOIN voice_types vt ON tr.voice_type_id = vt.id
        """)
        
        all_results = cursor.fetchall()
        
        # Convert to list of dictionaries for easier handling
        results_list = [dict(result) for result in all_results]
        
        # Apply CS50 Merge Sort algorithm
        print("🔄 Applying CS50 Merge Sort algorithm...")
        algorithm_name = "CS50 Merge Sort (O(n log n))"
        sorted_results = merge_sort_scores(results_list, calculate_score)
        
        # Take top 10
        results = sorted_results[:10]
        
        print("\n" + "="*85)
        print("🏆                        SCOREBOARD - TOP 10                        🏆")
        print("="*85)
        
        if not results:
            print("📊 No test results found yet!")
            print("🎤 Take the first test and claim your place on the scoreboard!")
            print("="*85)
            return
        
        print("┌──────┬──────────────────┬────────┬────────────┬────────┬────────┬───────┬───────┬────────────┐")
        print("│ RANK │      NAME        │ GENDER │ VOICE TYPE │ RANGE  │ OCTAVE │ NOTES │ SCORE │   GROUPS   │")
        print("├──────┼──────────────────┼────────┼────────────┼────────┼────────┼───────┼───────┼────────────┤")
        
        for i, result in enumerate(results, 1):
            voice_type = result['type_name'] or "Unknown"
            voice_groups = result['possible_voice_groups'] or "N/A"
            full_name = f"{result['first_name']} {result['last_name']}"
            score = calculate_score(result)
            
            print(f"│ {i:4d} │ {full_name:16s} │ {result['gender']:6s} │ {voice_type:10s} │ "
                  f"{result['frequency_range_width']:5.1f}Hz │ {result['octave_range_width']:6.2f} │ "
                  f"{result['successful_notes_count']:5d} │ {score:5.1f} │ {voice_groups[:10]:10s} │")
        
        print("└──────┴──────────────────┴────────┴────────────┴────────┴────────┴───────┴───────┴────────────┘")
        print(f"🎓 Algorithm: {algorithm_name}")
        print("📊 Scoring: 60% Range + 30% Octaves + 10% Notes (weighted composite)")
        print("🎯 Those with the highest composite scores are at the top!")
        print("="*85)

def show_personal_statistics(user_id: int) -> None:
    """Shows user's personal statistics."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                u.first_name,
                u.last_name,
                vt.type_name,
                tr.frequency_range_width,
                tr.octave_range_width,
                tr.min_frequency,
                tr.max_frequency,
                tr.voice_type_match_percentage,
                tr.successful_notes_count,
                tr.test_date,
                tr.possible_voice_groups,
                tr.lowest_achievable_note,
                tr.highest_achievable_note
            FROM test_results tr
            JOIN users u ON tr.user_id = u.id
            LEFT JOIN voice_types vt ON tr.voice_type_id = vt.id
            WHERE tr.user_id = ?
            ORDER BY tr.test_date DESC
            LIMIT 1
        """, (user_id,))
        
        result = cursor.fetchone()
        if not result:
            return
        
        print("\n" + "📊"*30)
        print("📊 YOUR PERSONAL STATISTICS 📊")
        print("="*60)
        print(f"👤 Name: {result['first_name']} {result['last_name']}")
        print(f"🎵 Voice Type: {result['type_name'] or 'Unknown'}")
        print(f"📏 Frequency Range: {result['min_frequency']:.1f} - {result['max_frequency']:.1f} Hz")
        print(f"📐 Range Width: {result['frequency_range_width']:.1f} Hz")
        print(f"🎼 Octave Width: {result['octave_range_width']:.2f} octaves")
        print(f"🎯 Match Percentage: {result['voice_type_match_percentage']:.1f}%")
        print(f"🎵 Successful Notes: {result['successful_notes_count']}")
        print(f"🎶 Possible Voice Groups: {result['possible_voice_groups'] or 'N/A'}")
        print(f"💻 Lowest Note: {result['lowest_achievable_note'] or 'N/A'}")
        print(f"📋 Highest Note: {result['highest_achievable_note'] or 'N/A'}")
        print(f"📅 Test Date: {result['test_date']}")
        print("="*60)

def show_test_history(user_id: int) -> None:
    """Shows detailed test history for a user."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get latest test result ID
        cursor.execute("""
            SELECT id FROM test_results 
            WHERE user_id = ? 
            ORDER BY test_date DESC 
            LIMIT 1
        """, (user_id,))
        
        test_result = cursor.fetchone()
        if not test_result:
            return
        
        # Get detailed history
        cursor.execute("""
            SELECT 
                note_name,
                target_frequency,
                detected_frequency,
                octave_number,
                accuracy_percentage,
                attempt_number,
                is_successful,
                test_direction,
                recorded_at
            FROM voice_analyzer_history
            WHERE test_result_id = ?
            ORDER BY recorded_at ASC
        """, (test_result['id'],))
        
        history = cursor.fetchall()
        if not history:
            return
        
        print("\n" + "="*75)
        print("📜                    DETAILED TEST HISTORY                    📜")
        print("="*75)
        print("┌──────┬─────────┬───────────┬─────┬──────────┬─────┬─────────┬──────┐")
        print("│ NOTE │ TARGET  │ DETECTED  │ OCT │ ACCURACY │ ATT │ SUCCESS │ DIR  │")
        print("├──────┼─────────┼───────────┼─────┼──────────┼─────┼─────────┼──────┤")
        
        for record in history:
            success_icon = "✓" if record['is_successful'] else "✗"
            direction_arrow = "↓" if record['test_direction'] == 'down' else "↑"
            
            detected_freq = record['detected_frequency'] or 0
            octave = record['octave_number'] or 0
            accuracy = record['accuracy_percentage'] or 0
            
            print(f"│ {record['note_name']:4s} │ {record['target_frequency']:7.1f} │ "
                  f"{detected_freq:9.1f} │ {octave:3d} │ {accuracy:7.1f}% │ "
                  f"{record['attempt_number']:3d} │   {success_icon:1s}     │  {direction_arrow:1s}   │")
        
        print("└──────┴─────────┴───────────┴─────┴──────────┴─────┴─────────┴──────┘")
        print("="*75)

def show_database_tables() -> None:
    """Shows database tables with formatted output."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        print("\n" + "="*80)
        print("🗄️                     DATABASE TABLES OVERVIEW                     🗄️")
        print("="*80)
        
        # Users table
        print("\n👥 USERS TABLE:")
        print("┌────┬──────────────┬──────────────┬────────┬──────────────────┐")
        print("│ ID │ FIRST NAME   │ LAST NAME    │ GENDER │     CREATED      │")
        print("├────┼──────────────┼──────────────┼────────┼──────────────────┤")
        cursor.execute("SELECT id, first_name, last_name, gender, created_at FROM users ORDER BY id")
        users = cursor.fetchall()
        for user in users:
            print(f"│ {user['id']:2d} │ {user['first_name']:12s} │ {user['last_name']:12s} │ "
                  f"{user['gender']:6s} │ {user['created_at'][:16]:16s} │")
        print("└────┴──────────────┴──────────────┴────────┴──────────────────┘")
        
        # Voice types table
        print(f"\n🎵 VOICE TYPES TABLE:")
        print("┌────┬───────────────┬────────┬──────────┬──────────┐")
        print("│ ID │   TYPE NAME   │ GENDER │ MIN FREQ │ MAX FREQ │")
        print("├────┼───────────────┼────────┼──────────┼──────────┤")
        cursor.execute("SELECT id, type_name, gender, min_frequency, max_frequency FROM voice_types ORDER BY id")
        voice_types = cursor.fetchall()
        for vt in voice_types:
            print(f"│ {vt['id']:2d} │ {vt['type_name']:13s} │ {vt['gender']:6s} │ "
                  f"{vt['min_frequency']:8.1f} │ {vt['max_frequency']:8.1f} │")
        print("└────┴───────────────┴────────┴──────────┴──────────┘")
        
        # Test results table
        print(f"\n📊 TEST RESULTS TABLE:")
        print("┌────┬──────┬─────────────┬──────────┬──────────┬────────┬────────┬─────────┐")
        print("│ ID │ USER │ VOICE TYPE  │ MIN FREQ │ MAX FREQ │ RANGE  │ OCTAVE │ SUCCESS │")
        print("├────┼──────┼─────────────┼──────────┼──────────┼────────┼────────┼─────────┤")
        cursor.execute("""
            SELECT tr.id, u.first_name, vt.type_name, tr.min_frequency, 
                   tr.max_frequency, tr.frequency_range_width, tr.octave_range_width,
                   tr.successful_notes_count
            FROM test_results tr
            JOIN users u ON tr.user_id = u.id
            LEFT JOIN voice_types vt ON tr.voice_type_id = vt.id
            ORDER BY tr.id
        """)
        test_results = cursor.fetchall()
        for tr in test_results:
            print(f"│ {tr['id']:2d} │ {tr['first_name']:4s} │ {(tr['type_name'] or 'N/A'):11s} │ "
                  f"{tr['min_frequency']:8.1f} │ {tr['max_frequency']:8.1f} │ "
                  f"{tr['frequency_range_width']:6.1f} │ {tr['octave_range_width']:6.2f} │ {tr['successful_notes_count']:7d} │")
        print("└────┴──────┴─────────────┴──────────┴──────────┴────────┴────────┴─────────┘")
        
        # History table count
        cursor.execute("SELECT COUNT(*) as count FROM voice_analyzer_history")
        history_count = cursor.fetchone()['count']
        print(f"\n📜 VOICE ANALYZER HISTORY: {history_count} records")
        
        print("="*80)

def restore_default_database():
    """Restore database to default state by clearing all user data."""
    print("\n" + "="*70)
    print("🔄 DATABASE RESTORE TO DEFAULT")
    print("="*70)
    
    # Confirmation prompt
    print("⚠️  WARNING: This will delete ALL user data!")
    print("   • All users will be removed")
    print("   • All test results will be deleted") 
    print("   • All test history will be cleared")
    print("   • Voice types will be reset to defaults")
    
    confirm = input("\n❓ Are you sure you want to continue? (yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        print("❌ Restore operation cancelled.")
        return
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            print("\n🗑️  Clearing all tables...")
            
            # Clear all user data tables (order matters due to foreign keys)
            cursor.execute("DELETE FROM voice_analyzer_history")
            print("   ✅ voice_analyzer_history cleared")
            
            cursor.execute("DELETE FROM test_results") 
            print("   ✅ test_results cleared")
            
            cursor.execute("DELETE FROM users")
            print("   ✅ users cleared")
            
            cursor.execute("DELETE FROM voice_types")
            print("   ✅ voice_types cleared")
            
            # Reset auto-increment counters
            cursor.execute("DELETE FROM sqlite_sequence")
            print("   ✅ Auto-increment counters reset")
            
            conn.commit()
            
            print("\n🔄 Reinitializing default voice types...")
            # Reinitialize voice types with default data
            voice_types_data = [
                ('Bass', 'male', 82.41, 329.63, 'Lowest male voice type'),
                ('Baritone', 'male', 98.00, 392.00, 'Middle male voice type'),
                ('Tenor', 'male', 130.81, 523.25, 'Highest male voice type'),
                ('Contralto', 'female', 164.81, 659.26, 'Lowest female voice type'),
                ('Mezzo-soprano', 'female', 196.00, 783.99, 'Middle female voice type'),
                ('Soprano', 'female', 261.63, 1046.50, 'Highest female voice type')
            ]
            
            cursor.executemany("""
                INSERT OR IGNORE INTO voice_types (type_name, gender, min_frequency, max_frequency, description)
                VALUES (?, ?, ?, ?, ?)
            """, voice_types_data)
            
            conn.commit()
            
            print("\n✅ DATABASE SUCCESSFULLY RESTORED TO DEFAULT!")
            print("🎯 All user data cleared, ready for fresh start.")
            
    except sqlite3.Error as e:
        print(f"❌ Database error during restore: {e}")
    except Exception as e:
        print(f"❌ Unexpected error during restore: {e}")
    
    print("="*70)
