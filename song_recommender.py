#!/usr/bin/env python3
"""
Song Recommendation System Based on Vocal Range

This module provides intelligent song recommendations based on a user's detected
vocal range. It analyzes frequency overlaps between user capabilities and song
requirements to suggest appropriate songs with difficulty ratings.

Features:
- Smart matching algorithm with percentage compatibility
- Difficulty level calculation (Very Easy to Very Hard)
- Voice type specific recommendations (Bass, Tenor, Alto, Soprano)
- Genre-based filtering and categorization
- Visual terminal output with emojis and progress indicators
"""

import math
from typing import List, Dict, Tuple
from models import NOTE_FREQUENCIES

# Simple song database - expandable with API integration in the future
SONG_DATABASE = [
    # Male Songs - Bass/Baritone
    {"title": "Hallelujah", "artist": "Leonard Cohen", "min_freq": 98.0, "max_freq": 330.0, "difficulty": "Easy", "genre": "Folk"},
    {"title": "The Sound of Silence", "artist": "Simon & Garfunkel", "min_freq": 110.0, "max_freq": 350.0, "difficulty": "Easy", "genre": "Folk"},
    {"title": "Yesterday", "artist": "The Beatles", "min_freq": 123.47, "max_freq": 369.99, "difficulty": "Medium", "genre": "Pop"},
    {"title": "Mad World", "artist": "Gary Jules", "min_freq": 98.0, "max_freq": 293.66, "difficulty": "Easy", "genre": "Alternative"},
    
    # Male Songs - Tenor
    {"title": "Imagine", "artist": "John Lennon", "min_freq": 130.81, "max_freq": 493.88, "difficulty": "Medium", "genre": "Pop"},
    {"title": "Let It Be", "artist": "The Beatles", "min_freq": 146.83, "max_freq": 523.25, "difficulty": "Medium", "genre": "Pop"},
    {"title": "Wonderwall", "artist": "Oasis", "min_freq": 164.81, "max_freq": 587.33, "difficulty": "Hard", "genre": "Rock"},
    
    # Female Songs - Alto
    {"title": "Someone Like You", "artist": "Adele", "min_freq": 196.0, "max_freq": 523.25, "difficulty": "Medium", "genre": "Pop"},
    {"title": "Hello", "artist": "Adele", "min_freq": 174.61, "max_freq": 587.33, "difficulty": "Hard", "genre": "Pop"},
    {"title": "Tears in Heaven", "artist": "Eric Clapton", "min_freq": 220.0, "max_freq": 440.0, "difficulty": "Easy", "genre": "Ballad"},
    
    # Female Songs - Soprano
    {"title": "I Will Always Love You", "artist": "Whitney Houston", "min_freq": 261.63, "max_freq": 1046.50, "difficulty": "Expert", "genre": "R&B"},
    {"title": "My Heart Will Go On", "artist": "Celine Dion", "min_freq": 293.66, "max_freq": 880.0, "difficulty": "Hard", "genre": "Pop"},
    {"title": "Amazing Grace", "artist": "Traditional", "min_freq": 261.63, "max_freq": 698.46, "difficulty": "Medium", "genre": "Spiritual"},
    
    # Universal Songs
    {"title": "Happy Birthday", "artist": "Traditional", "min_freq": 130.81, "max_freq": 523.25, "difficulty": "Easy", "genre": "Traditional"},
    {"title": "Auld Lang Syne", "artist": "Traditional", "min_freq": 146.83, "max_freq": 440.0, "difficulty": "Easy", "genre": "Traditional"},
]

def frequency_to_note_name(frequency: float) -> str:
    """Converts frequency to the closest note name"""
    closest_note = None
    min_diff = float('inf')
    
    for note_name, note_freq in NOTE_FREQUENCIES:
        diff = abs(frequency - note_freq)
        if diff < min_diff:
            min_diff = diff
            closest_note = note_name
    
    return closest_note or "Unknown"

def calculate_vocal_range_coverage(song_min: float, song_max: float, user_min: float, user_max: float) -> float:
    """Calculates how much of the song's range overlaps with the user's vocal range"""
    # User's singable range
    user_range = user_max - user_min
    if user_range <= 0:
        return 0.0
    
    # Overlapping range
    overlap_start = max(song_min, user_min)
    overlap_end = min(song_max, user_max)
    overlap = max(0, overlap_end - overlap_start)
    
    # Percentage of song range within user's capabilities
    return (overlap / user_range) * 100

def get_difficulty_score(song: Dict, user_range_hz: float) -> str:
    """Determines the difficulty level of a song based on user's vocal range"""
    song_range = song["max_freq"] - song["min_freq"]
    
    if song_range <= user_range_hz * 0.5:
        return "Very Easy"
    elif song_range <= user_range_hz * 0.7:
        return "Easy"
    elif song_range <= user_range_hz * 0.9:
        return "Medium"
    elif song_range <= user_range_hz * 1.1:
        return "Hard"
    else:
        return "Very Hard"

def recommend_songs(user_min_freq: float, user_max_freq: float, voice_type: str, limit: int = 10) -> List[Dict]:
    """Generates song recommendations based on user's vocal range"""
    user_range_hz = user_max_freq - user_min_freq
    recommendations = []
    
    for song in SONG_DATABASE:
        # Calculate how well the song fits the user's range
        coverage = calculate_vocal_range_coverage(
            song["min_freq"], song["max_freq"], 
            user_min_freq, user_max_freq
        )
        
        # Minimum 70% overlap required
        if coverage >= 70:
            difficulty = get_difficulty_score(song, user_range_hz)
            
            recommendation = {
                **song,
                "coverage_percentage": round(coverage, 1),
                "recommended_difficulty": difficulty,
                "min_note": frequency_to_note_name(song["min_freq"]),
                "max_note": frequency_to_note_name(song["max_freq"]),
                "suitable_for_voice_type": voice_type.lower() in song.get("voice_types", ["all"])
            }
            recommendations.append(recommendation)
    
    # Sort by coverage percentage
    recommendations.sort(key=lambda x: x["coverage_percentage"], reverse=True)
    
    return recommendations[:limit]

def display_song_recommendations(user_min_freq: float, user_max_freq: float, voice_type: str):
    """Displays song recommendations in a beautifully formatted output"""
    recommendations = recommend_songs(user_min_freq, user_max_freq, voice_type)
    
    print("\n🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵")
    print("🎤                    RECOMMENDED SONGS FOR YOUR VOICE                    🎤")
    print("🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵")
    
    min_note = frequency_to_note_name(user_min_freq)
    max_note = frequency_to_note_name(user_max_freq)
    
    print(f"🎼 Your vocal range: {min_note} ({user_min_freq:.1f} Hz) - {max_note} ({user_max_freq:.1f} Hz)")
    print(f"🎭 Voice type: {voice_type}")
    print(f"📏 Range width: {user_max_freq - user_min_freq:.1f} Hz")
    print()
    
    if not recommendations:
        print("😕 No suitable songs found for your vocal range.")
        print("💡 Try expanding your range with vocal exercises!")
        return
    
    for i, song in enumerate(recommendations, 1):
        difficulty_emoji = {
            "Very Easy": "🟢", "Easy": "🟡", "Medium": "🟠", 
            "Hard": "🔴", "Very Hard": "⚫"
        }
        
        print(f"🎵 {i}. {song['title']} - {song['artist']}")
        print(f"    🎼 Range: {song['min_note']} - {song['max_note']} ({song['min_freq']:.1f}Hz - {song['max_freq']:.1f}Hz)")
        print(f"    📊 Voice match: {song['coverage_percentage']}%")
        print(f"    {difficulty_emoji.get(song['recommended_difficulty'], '⚪')} Difficulty: {song['recommended_difficulty']}")
        print(f"    🎭 Genre: {song['genre']}")
        print()
    
    print("💡 TIP: Start with 'Very Easy' and 'Easy' songs to build confidence!")
    print("🎯 Songs with 90%+ match are perfect for your current range!")

def export_playlist(recommendations: List[Dict], filename: str = "my_vocal_range_playlist.txt"):
    """Exports recommended songs to a text file"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("🎵 MY VOCAL RANGE PLAYLIST 🎵\n")
        f.write("=" * 50 + "\n\n")
        
        for i, song in enumerate(recommendations, 1):
            f.write(f"{i}. {song['title']} - {song['artist']}\n")
            f.write(f"   Range: {song['min_note']} - {song['max_note']}\n")
            f.write(f"   Match: {song['coverage_percentage']}%\n")
            f.write(f"   Difficulty: {song['recommended_difficulty']}\n\n")
    
    print(f"📁 Playlist saved to: {filename}")

# Test function
if __name__ == "__main__":
    # Sample values for testing
    test_min_freq = 130.81  # C3
    test_max_freq = 523.25  # C5
    test_voice_type = "Tenor"
    
    print("🧪 Testing Song Recommendation System...")
    display_song_recommendations(test_min_freq, test_max_freq, test_voice_type)
