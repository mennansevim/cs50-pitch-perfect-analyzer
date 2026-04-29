# Building a Voice Range Analyzer with Python: My CS50 Final Project Journey

In this article, I will try to tell you about my CS50 final project, the Pitch Perfect Analyzer, a sophisticated Python application that analyzes vocal ranges, provides intelligent voice type classification, and recommends songs based on your voice color.

The CS50 Pitch Perfect Analyzer is an advanced voice range detection system that uses harmonic analysis and fundamental frequency detection to scientifically measure vocal capabilities. The application helps solve a real-world problem in choral music by quickly assessing singers' voice types for proper group placement. Additionally, it features an intelligent song recommendation engine that analyzes your detected vocal range and suggests appropriate songs with difficulty ratings, making it easier to find music that matches your voice color and capabilities.

This project represents the culmination of Harvard's CS50 Introduction to Computer Science course, demonstrating complex algorithm implementation, real-time audio processing, and practical problem-solving skills.

## THE PROBLEM

When new singers join a choir, they need to be quickly assessed to determine their voice type classification. In polyphonic choral music, voice groups are traditionally divided into:

**Female Voices:**
- **Alto** - Lower female voice range
- **Soprano** - Higher female voice range

**Male Voices:**
- **Bass** - Lower male voice range
- **Tenor** - Higher male voice range

The traditional method of voice classification relies heavily on subjective assessment by choir directors, which can be time-consuming and inconsistent. My application scientifically measures vocal ranges through frequency analysis, ensuring balanced harmonies and helping singers perform within their comfortable range.

Want to read this story later? Save it in Journal.

Additionally, the built-in SQLite3 database stores test results, creating a persistent scoreboard system that transforms vocal assessments into engaging competitions among choir members.

## TECHNICAL ARCHITECTURE

Let's talk about the core technical implementation of this system.

### Audio Processing Engine

The heart of the application is the `voice_analyzer.py` module, which implements advanced FFT-based frequency analysis algorithms. The system uses Fast Fourier Transform to convert time-domain audio signals into frequency-domain data, allowing precise pitch detection.

Press enter or click to view image in full size

Sample Voice Analysis Output - Success Indicators

### Fundamental Frequency Detection

One of the most challenging aspects was implementing accurate pitch detection. Simple peak detection often fails with human voice due to harmonic content. For example, when someone sings 164 Hz (E3), the system might incorrectly detect 494 Hz (the third harmonic) instead of the fundamental frequency.

I solved this by implementing a sophisticated harmonic analysis algorithm:

```python
# Harmonic validation - prevents false harmonics detection
for harmonic in [2, 3, 4]:
    harmonic_freq = freq * harmonic
    if harmonic_freq > 800:
        break
    # Check if this harmonic exists in full spectrum
    harmonic_indices = np.where(np.abs(full_freqs - harmonic_freq) < 15)[0]
```

The algorithm analyzes the 2nd, 3rd, and 4th harmonics to validate fundamental frequency candidates, achieving >95% pitch detection accuracy for clear vocals.

### Octave Calculation

The system calculates octaves using logarithmic mathematics with A4=440Hz as reference:

```python
a4_freq = 440.0
octave_difference = np.log2(frequency / a4_freq)
octave_number = 4 + octave_difference
```

This mathematical approach ensures precise octave identification across the entire vocal range (80-1050 Hz).

## PIANO AUDIO IMPLEMENTATION

All reference piano notes were personally recorded using my home **Kawai CN201 digital piano**. Each note from C2 through C6 was individually recorded to ensure consistent tone quality and authentic piano timbre.

### Audio Quality Enhancement

To eliminate audio artifacts and popping sounds that typically occur at the beginning and end of digital recordings, I implemented fade-in and fade-out effects using the pydub library:

```python
# Anti-pop processing for WAV files
fade_duration = min(50, len(audio) // 4)  # 50ms or 1/4 of audio length
audio = audio.fade_in(fade_duration).fade_out(fade_duration)
```

This preprocessing ensures smooth, professional-quality audio playback that won't interfere with the precision required for vocal range testing.

## FEATURES

### Core Functionality

**Advanced Pitch Detection**: Uses harmonic analysis and fundamental frequency detection to accurately identify sung notes.

**Voice Range Analysis**: Comprehensive vocal range measurement covering 80-400 Hz fundamental frequencies.

**Voice Type Classification**: Automatically determines your voice type (Soprano, Alto, Tenor, Bass, Baritone, Mezzo-soprano, Contralto) based on frequency analysis.

**Real-time Audio Processing**: Live microphone input with noise filtering and signal validation.

**Visual Progress Tracking**: Beautiful terminal-based progress bars and success indicators with motivational feedback.

Press enter or click to view image in full size

Visual Progress Indicators

### Database Integration

The application uses SQLite for persistent data storage, demonstrating database concepts learned in CS50. The database stores:

- User profiles with personal information
- Test results with detailed frequency data
- Historical performance tracking
- Scoreboard rankings with merge sort implementation

The scoreboard feature uses the merge sort algorithm (a CS50 requirement) to rank users based on vocal range width and octave span:

```python
def merge_sort(arr, key_func):
    """CS50 merge sort implementation for scoreboard ranking"""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key_func)
    right = merge_sort(arr[mid:], key_func)
    return merge(left, right, key_func)
```

### Smart Song Recommendations

One of the newest features is the intelligent song recommendation engine. The system analyzes your detected vocal range and suggests appropriate songs with difficulty ratings.

Press enter or click to view image in full size

Song Recommendation Output

The recommendation algorithm calculates percentage overlap between user capabilities and song requirements:

```python
def calculate_vocal_range_coverage(song_min, song_max, user_min, user_max):
    # Overlapping range calculation
    overlap_start = max(song_min, user_min)
    overlap_end = min(song_max, user_max)
    overlap = max(0, overlap_end - overlap_start)
    return (overlap / user_range) * 100
```

Songs with 70%+ overlap are recommended, with difficulty levels automatically calculated based on range requirements.

## HOW IT WORKS

Let me walk you through the user experience.

### 1. Microphone Setup

When you first launch the application, it automatically detects available microphones on your system. You select your preferred input device, and the system configures audio parameters:

- **Sample Rate**: 44100 Hz (CD quality)
- **Recording Duration**: 2 seconds per note
- **Frequency Tolerance**: ±80 Hz margin

### 2. User Registration

The system prompts for your name and gender. Gender selection determines the starting reference note:
- **Male**: Starts at C3 (130.81 Hz)
- **Female**: Starts at C4 (261.63 Hz)

This optimization ensures the test begins within a comfortable range for most voices.

### 3. Voice Range Testing

The application plays reference notes (authentic piano recordings) and you sing them back. The test proceeds in two directions:

**Bass Direction (🔽)**: Tests progressively lower notes from the starting point until you can no longer match the pitch.

**Treble Direction (🔼)**: Tests progressively higher notes from the starting point until you reach your upper limit.

For each note:
- Piano reference plays for 2 seconds
- You sing back into the microphone
- System analyzes your voice using FFT
- Real-time feedback shows accuracy percentage
- Visual progress bar indicates performance
- Up to 2 attempts per note allowed

### 4. Real-time Feedback

The system provides immediate visual feedback for each attempt:

```
🎵 SUCCESS! G3 | 195.0 Hz (3rd Octave) | [████████████████████░] 98.8% | 🏆 PERFECT!
```

Or for unsuccessful attempts:

```
❌ FAILED: A3 | Target: 220.0 Hz | Detected: 198.5 Hz (3rd Octave)
📊 [███████░░░░░░░░] 65.2% | 1 attempt left | 💡 Very close! Try again
```

### 5. Comprehensive Analysis

After testing completes, the application generates:

- Visual frequency range chart
- Voice type classification with confidence percentages
- Detailed statistics (range width, octave span)
- Personal scoreboard ranking
- Song recommendations matched to your capabilities

## PROJECT STRUCTURE

The application follows a modular design with clear separation of concerns:

**main.py** - Main application entry point and user interface flow

**voice_analyzer.py** - Core pitch detection algorithms with FFT implementation

**audio_utils.py** - Audio I/O, microphone handling, and piano playback

**visualization.py** - Terminal-based charts, progress bars, and result presentation

**database.py** - SQLite operations, scoreboard calculations, and merge sort implementation

**models.py** - Voice science definitions, frequency ranges, and note mappings

**config.py** - Centralized configuration for audio parameters and system settings

**song_recommender.py** - Intelligent song matching algorithm with difficulty assessment

**sounds/piano/** - 29 WAV files of personally recorded piano notes (C2-C6)

## ADVANTAGES

Let me tell you about the key advantages of this system.

**Scientific Accuracy**: Uses proven DSP techniques with >95% accuracy, eliminating subjective bias in voice classification.

**Real-time Processing**: Provides immediate feedback with <100ms latency, making the testing experience smooth and responsive.

**Educational Value**: Demonstrates advanced CS50 concepts including FFT analysis, harmonic validation, database design, and algorithmic sorting.

**Practical Application**: Solves real-world problems for choir directors, vocal coaches, and singing enthusiasts.

**Scalable Database**: SQLite integration supports hundreds of users with thousands of test results, enabling long-term performance tracking.

**Professional Audio Quality**: Personally recorded piano references ensure authentic frequency standards for accurate testing.

**Engaging Gamification**: Scoreboard system transforms voice testing into a competitive, motivational experience.

**Personalized Recommendations**: Smart song suggestion algorithm helps users find appropriate music for their vocal capabilities.

**Cross-platform Compatibility**: Works on Windows, macOS, and Linux with minimal dependencies.

**Open Source**: MIT license allows free use and modification for educational purposes.

## DESIGN DECISIONS

I want to talk about some important design decisions I made during development.

### Why Console Application?

I chose a terminal-based interface over a GUI for several strategic reasons:

**Accessibility**: Works on any system with Python, regardless of graphics capabilities. This is especially important for educational environments where GUI frameworks might not be available.

**Performance**: No GUI overhead allows the system to focus entirely on real-time audio processing, which is computationally intensive.

**CS50 Spirit**: The course emphasizes algorithmic problem-solving over visual design, and a console application better demonstrates core programming concepts.

**Simplicity**: Reduces complexity, allowing focus on the core voice analysis logic rather than interface design.

### Why Harmonic Analysis?

Simple peak detection fails with human voice because of harmonic content. A sung note contains not just the fundamental frequency but also integer multiples (harmonics). My implementation:

- Analyzes multiple harmonics to validate the fundamental frequency
- Prevents false positives (e.g., detecting 494 Hz instead of 164 Hz)
- Provides scientifically accurate results essential for voice classification
- Demonstrates advanced signal processing beyond basic CS50 curriculum

### Why Personal Piano Recordings?

**Audio Quality**: Professional-grade recordings ensure accurate frequency references, which is critical for pitch comparison.

**Consistency**: Uniform recording conditions across all notes eliminate variables that could affect accuracy.

**Copyright Freedom**: No licensing issues with commercial audio samples, making the project freely shareable.

**Educational Value**: Demonstrates real-world data collection methodology and attention to detail.

### Why SQLite Over Text Files?

**Data Integrity**: ACID compliance ensures reliable data storage even with concurrent access or system crashes.

**Scalability**: Can handle hundreds of users and thousands of test results without performance degradation.

**Query Flexibility**: Enables complex scoreboard rankings and statistical analysis using SQL.

**CS50 Curriculum**: Demonstrates database concepts learned in the course, including schema design and SQL queries.

## CHALLENGES AND SOLUTIONS

### Challenge 1: False Harmonic Detection

**Problem**: When users sang low notes like E3 (164 Hz), the system frequently detected the third harmonic at 494 Hz instead of the fundamental frequency.

**Solution**: Implemented a sophisticated harmonic validation algorithm that analyzes 2nd, 3rd, and 4th harmonics to identify the true fundamental frequency. The algorithm assigns scores based on harmonic presence and strength, with bonus points for multiple confirmed harmonics.

### Challenge 2: Low Volume Handling

**Problem**: Users with quiet voices or poor microphone positioning produced insufficient signal strength for accurate analysis.

**Solution**: Added signal power detection with user-friendly warnings:

```python
signal_power = np.mean(np.abs(audio_data))
if signal_power < 0.01:
    print_low_volume_warning()
```

The system provides actionable feedback like "Move closer to microphone" and "Speak louder" instead of generic error messages.

### Challenge 3: Octave Confusion

**Problem**: Users sometimes sang the same note in different octaves (e.g., C3 vs C4), which should both be considered correct.

**Solution**: Implemented octave-aware matching that accepts frequencies at 2x, 0.5x, 4x, and 0.25x the target frequency:

```python
ratios = [1.0, 2.0, 0.5, 4.0, 0.25]  # 1x, 2x, 0.5x, 4x, 0.25x octaves
for ratio in ratios:
    adjusted_target = target_freq * ratio
    # Calculate score with slight penalty for octave differences
```

### Challenge 4: Audio Pops and Clicks

**Problem**: Digital recordings often contain artifacts at the beginning and end, which interfered with frequency analysis.

**Solution**: Implemented fade-in/fade-out processing using pydub, ensuring smooth audio transitions that don't affect pitch detection accuracy.

## CS50 FINAL PROJECT REQUIREMENTS

This project fulfills all CS50 final project requirements:

**Algorithmic Complexity**: Advanced FFT implementation, harmonic analysis, and merge sort for scoreboard ranking.

**Real-world Application**: Solves practical problems in choral music and vocal training.

**Code Organization**: Modular design with clear separation of concerns across 8 main files.

**Educational Value**: Demonstrates mathematics (logarithmic octave calculation), signal processing (FFT analysis), computer science (algorithm optimization), and database design.

**Academic Honesty**: Full disclosure of AI assistance in the README, with transparency about ChatGPT and Cursor AI usage for documentation, debugging, and code refactoring.

## PERFORMANCE METRICS

The application delivers impressive performance:

- **Accuracy**: >95% pitch detection accuracy for clear vocals
- **Speed**: Real-time processing with <100ms latency
- **Reliability**: Robust harmonic validation prevents false positives
- **Range**: Supports 65-1050 Hz frequency range (4+ octaves)
- **Scalability**: Handles hundreds of users without performance degradation

## SAMPLE OUTPUT

Here's what a typical test session looks like:

```
🎤============================================================🎤
🎵                  CS50 PITCH PERFECT ANALYZER                🎵
🎼               Advanced Voice Range Detection v2.0           🎼
🎤============================================================🎤

🔽 BASS VOICE TEST STARTING 🔽
==================================================

🎼 UP NEXT: C3 (130.81 Hz)

🎵 SUCCESS! C3 | 130.5 Hz (2nd Octave) | [███████████████████░] 98.4% | 🏆 PERFECT!

🎼 UP NEXT: B2 (123.47 Hz)

🎵 SUCCESS! B2 | 123.8 Hz (2nd Octave) | [███████████████████░] 99.1% | 🏆 PERFECT!

🏆 SUCCESSFUL NOTES: C3 → B2

🔼 HIGH VOICE TEST STARTING! 🔼
✅ 2 notes successfully detected so far!

🎯 RESULT: 🏆 'Tenor' (87.3% compatibility - Great match!)
```

Press enter or click to view image in full size

Final Voice Analysis Report

## SONG RECOMMENDATION SYSTEM

The intelligent recommendation engine analyzes your vocal capabilities and suggests appropriate songs:

```
🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵
🎤                    RECOMMENDED SONGS FOR YOUR VOICE                    🎤
🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵

🎼 Your vocal range: C3 (130.8 Hz) - C5 (523.3 Hz)
🎭 Voice type: Tenor
📏 Range width: 392.5 Hz

🎵 1. Let It Be - The Beatles
    🎼 Range: D3 - C5 (146.8Hz - 523.3Hz)
    📊 Voice match: 95.2%
    🟡 Difficulty: Easy
    🎭 Genre: Pop

🎵 2. Imagine - John Lennon
    🎼 Range: C3 - A4 (130.8Hz - 440.0Hz)
    📊 Voice match: 88.7%
    🟢 Difficulty: Very Easy
    🎭 Genre: Pop

💡 TIP: Start with 'Very Easy' and 'Easy' songs to build confidence!
🎯 Songs with 90%+ match are perfect for your current range!
```

The system categorizes songs by:
- **Genre**: Pop, Rock, Folk, R&B, Traditional, Ballad
- **Difficulty**: Very Easy, Easy, Medium, Hard, Very Hard, Expert
- **Compatibility**: Percentage match with your vocal range

## FUTURE ENHANCEMENTS

I have several ideas for future versions:

**MIDI Export**: Save detected notes as MIDI files for use in music production software.

**Web Interface**: Browser-based version using WebAudio API for easier accessibility.

**Machine Learning**: Neural network-based pitch detection for even higher accuracy.

**Expanded Song Database**: Integration with Spotify/Apple Music APIs for thousands of song recommendations.

**Custom Playlist Export**: Direct export to Spotify or Apple Music playlists.

**Vocal Training Mode**: Guided exercises to systematically expand vocal range.

**Performance Tracking**: Long-term progress visualization showing improvement over weeks and months.

**Cloud Storage**: Synchronize results across devices with cloud backup.

## DISADVANTAGES

I want to be transparent about some limitations of the system.

**Console Interface**: While functional, a graphical interface would be more intuitive for non-technical users.

**Limited Song Database**: Currently contains only 15 songs; integration with music APIs would provide thousands of options.

**Python Dependency**: Requires Python installation, which might be challenging for non-programmers.

**No MIDI Input**: Cannot analyze pre-recorded audio files, only live microphone input.

**English Interface Only**: Multi-language support would make the application more accessible globally.

**Quiet Environment Required**: Background noise can interfere with frequency detection accuracy.

Still, these limitations don't significantly impact the core functionality, and most could be addressed in future versions.

## INSTALLATION AND USAGE

### Prerequisites

```bash
python3 -m pip install numpy scipy sounddevice simpleaudio pydub
```

### Quick Start

```bash
git clone https://github.com/mennansevim/cs50-pitch-perfect-analyzer.git
cd cs50-pitch-perfect-analyzer
python main.py
```

### Configuration

You can customize audio parameters in `config.py`:

```python
NOTE_DURATION = 2          # Recording duration per note
SAMPLE_RATE = 44100        # Audio sample rate
ACCEPTABLE_MARGIN = 80     # Frequency tolerance (Hz)
MIN_SUCCESS_RATE = 80      # Minimum success percentage
MAX_ATTEMPTS = 2           # Attempts per note
```

## VOICE TYPES SUPPORTED

The system recognizes all standard voice classifications:

### Male Voices
- **Bass**: 82.41 - 329.63 Hz (E2 - E4)
- **Baritone**: 98.00 - 392.00 Hz (G2 - G4)
- **Tenor**: 130.81 - 523.25 Hz (C3 - C5)

### Female Voices
- **Contralto**: 164.81 - 659.26 Hz (E3 - E5)
- **Mezzo-soprano**: 196.00 - 783.99 Hz (G3 - G5)
- **Soprano**: 261.63 - 1046.50 Hz (C4 - C6)

These ranges are based on scientific vocal research and represent typical professional singing ranges.

## AI ASSISTANCE DISCLOSURE

In accordance with CS50's academic honesty policy, I want to be transparent about AI tool usage:

**ChatGPT**: Helped interpret complex audio processing requirements, clarify DSP concepts, and troubleshoot Python audio library issues.

**Cursor AI**: Provided code completion suggestions for implementing pitch detection algorithms, database query optimization, and code refactoring.

The essence of this work remains my own, with AI tools serving as productivity amplifiers rather than primary creators of the codebase. All core algorithms, design decisions, and problem-solving approaches are original work.

## EDUCATIONAL VALUE

This project demonstrates several key CS50 concepts:

**Algorithm Analysis**: Understanding time complexity of FFT (O(n log n)) versus naive frequency detection.

**Data Structures**: Efficient use of arrays, lists, and dictionaries for audio processing and database operations.

**Sorting Algorithms**: Implementation of merge sort for scoreboard ranking.

**Database Design**: Proper schema design with foreign keys and normalized tables.

**Signal Processing**: Real-world application of Fourier transforms and harmonic analysis.

**User Experience**: Thoughtful interface design with clear feedback and error handling.

## DEMO VIDEO

You can watch a full demonstration of the application in action:

**Video Demo**: https://youtu.be/JzcOPJ1XdKM

The video shows:
- Complete installation process
- User registration and microphone setup
- Full voice range testing session
- Real-time feedback and progress indicators
- Final analysis and results presentation
- Song recommendation feature
- Scoreboard and database visualization

Thanks for reading.

## ABOUT THE AUTHOR

**Name**: Mennan Sevim  
**Location**: İzmir, Turkey  
**GitHub**: [@mennansevim](https://github.com/mennansevim)  
**edX Username**: mennansevim  
**Project Repository**: [CS50 Pitch Perfect Analyzer](https://github.com/mennansevim/cs50-pitch-perfect-analyzer)

This project was created as a final project for Harvard's CS50 Introduction to Computer Science course.

🎤 **"Perfect pitch detection through perfect code"** 🎵

## References and Sources

CS50 Course: https://cs50.harvard.edu/x/

NumPy Documentation: https://numpy.org/doc/

SciPy Signal Processing: https://docs.scipy.org/doc/scipy/reference/signal.html

FFT Theory: https://en.wikipedia.org/wiki/Fast_Fourier_transform

Voice Classification Research: https://www.ncvs.org/

SQLite Documentation: https://www.sqlite.org/docs.html

Harmonic Analysis: https://en.wikipedia.org/wiki/Harmonic_analysis

---

*This article documents my journey building an advanced voice analysis system as part of CS50. The project combines signal processing, database design, and algorithm implementation to solve real-world problems in music education.*

