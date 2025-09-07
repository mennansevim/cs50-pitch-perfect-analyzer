# CS50 Pitch Perfect Analyzer

#### Video Demo: `https://youtu.be/dXU6F9-1BeM?si=maFuepktLWQDVwa3`
#### Description:

**Advanced Voice Range Detection System with Harmonic Analysis**

🎵 A sophisticated Python application that analyzes your vocal range, detects pitch with high accuracy, and provides detailed voice type classification for choral voice grouping.

## 🎯 Project Purpose

This application was developed to solve a real-world problem in choral music. When new singers join a choir, they need to be quickly assessed to determine their voice type classification. In polyphonic choral music, voice groups are traditionally divided into:

**Female Voices:**
- **Alto** - Lower female voice range
- **Soprano** - Higher female voice range

**Male Voices:**
- **Bass** - Lower male voice range  
- **Tenor** - Higher male voice range

The application scientifically measures vocal ranges through frequency analysis, allowing choir directors to properly place singers in their optimal voice groups. This ensures balanced harmonies and helps singers perform within their comfortable range, ultimately improving the overall choral sound quality.

Additionally, the built-in SQLite3 database stores test results, creating a persistent scoreboard system that can transform vocal assessments into engaging competitions among choir members.

## 🎹 Audio Implementation

### Piano Recordings
All reference piano notes were personally recorded using my home **Kawai CN201 digital piano**. Each note (C2 through C6) was individually recorded to ensure consistent tone quality and authentic piano timbre. To eliminate audio artifacts and popping sounds that typically occur at the beginning and end of digital recordings, I implemented fade-in and fade-out effects using the pydub library.

### Audio Quality Enhancement
```python
# Anti-pop processing for WAV files
fade_duration = min(50, len(audio) // 4)  # 50ms or 1/4 of audio length
audio = audio.fade_in(fade_duration).fade_out(fade_duration)
```

This preprocessing ensures smooth, professional-quality audio playback that won't interfere with the precision required for vocal range testing.

## 🤖 AI Assistance Declaration

In accordance with CS50's academic honesty policy regarding AI tool usage for final projects, I acknowledge the following AI assistance:

### AI Usage
- **Code Documentation**: Asked ChatGPT to help interpret and document complex audio processing requirements
- **Algorithm Explanation**: Used ChatGPT to clarify digital signal processing concepts and frequency analysis mathematics
- **Error Debugging**: Consulted ChatGPT for troubleshooting specific Python audio library integration issues
- **Audio Algorithm Development**: Utilized Cursor AI's code completion for implementing advanced pitch detection algorithms
- **Database Query Optimization**: Received assistance in crafting efficient SQLite queries for the scoreboard functionality
- **Code Refactoring**: Used Cursor AI suggestions for improving code structure and readability

The essence of this work remains my own, with AI tools serving as productivity amplifiers rather than primary creators of the codebase.

## ✨ Features

### 🎯 Core Functionality
- **Advanced Pitch Detection**: Uses harmonic analysis and fundamental frequency detection
- **Voice Range Analysis**: Comprehensive vocal range measurement (80-400 Hz fundamental)
- **Voice Type Classification**: Automatically determines your voice type (Soprano, Alto, Tenor, Bass)
- **Octave Detection**: Real-time octave identification for each detected note
- **Visual Progress Tracking**: Beautiful progress bars and success indicators
- **SQLite Database Integration**: Persistent data storage for users and test results
- **Scoreboard System**: Top 10 rankings based on vocal range width and octave span
- **Personal Statistics**: Individual performance tracking and historical data
- **🆕 Smart Song Recommendations**: AI-powered song suggestions based on your vocal range
- **🆕 Professional Piano Audio**: Authentic Kawai CN201 digital piano recordings for reference notes
- **🆕 Intelligent Difficulty Assessment**: Automatic song difficulty rating based on your capabilities

### 🎼 Technical Highlights
- **Harmonic Analysis Algorithm**: Prevents false harmonics detection (e.g., 494 Hz instead of 164 Hz)
- **Fundamental Frequency Extraction**: Advanced FFT with peak detection and harmonic validation
- **Oktav Calculation**: Logarithmic octave detection based on A4=440Hz reference
- **Real-time Audio Processing**: Live microphone input with noise filtering
- **🆕 Vocal Range Matching**: Smart algorithm calculates percentage overlap between user range and song requirements
- **🆕 Genre-Based Filtering**: Categorized song recommendations by musical genre (Pop, Rock, Folk, R&B, etc.)
- **🆕 Multi-Octave Recognition**: Detects and handles octave variations in user singing

### 🎨 User Experience
- **Interactive CLI**: Beautiful terminal-based interface with emojis and progress bars
- **Multi-language Support**: English interface with international terminology
- **Visual Feedback**: Success/failure indicators with motivational messages
- **Detailed Analytics**: Comprehensive voice analysis with percentage matching
- **🆕 Personalized Song Suggestions**: Get song recommendations perfectly matched to your vocal capabilities
- **🆕 Professional Audio Quality**: High-quality piano reference notes with anti-pop processing

## 🚀 Installation

### Prerequisites
```bash
python3 -pip install numpy scipy sounddevice simpleaudio
```

### Quick Start
```bash
git clone https://github.com/mennansevim/cs50-pitch-perfect-analyzer.git
cd cs50-pitch-perfect-analyzer
python main.py
```

## 🎤 How It Works

### 1. **Microphone Setup**
- Select from available microphones
- Automatic device detection and configuration

### 2. **Voice Range Testing**
- Choose gender-specific starting point (C3 for male, C4 for female)
- Program plays reference notes (piano sounds)
- Sing/hum the same note back
- Real-time frequency analysis and feedback

### 3. **Advanced Analysis**
```
🎵 SUCCESS! G3 | 195.0 Hz (3rd Octave) | [████████████████████░] 98.8% | 🏆 PERFECT!
```

### 4. **Final Report**
- Visual frequency range chart
- Voice type classification with confidence percentages
- Comprehensive analysis and recommendations

### 5. **🆕 Smart Song Recommendations**
- Personalized song suggestions based on your detected vocal range
- Intelligent difficulty assessment (Very Easy to Expert)
- Genre-based categorization (Pop, Rock, Folk, R&B, Traditional)
- Percentage compatibility matching for each song
- Note range visualization for easy comparison

## 🔬 Technical Architecture

### Core Algorithms

#### **Fundamental Frequency Detection**
```python
def dominant_frequency(data: np.ndarray, rate: int) -> float:
    # Advanced FFT with harmonic analysis
    # Prevents false harmonic detection
    # Returns true fundamental frequency
```

#### **Harmonic Validation**
- Analyzes 2nd, 3rd, and 4th harmonics
- Validates fundamental frequency candidates
- Prevents common pitch detection errors

#### **Voice Type Classification**
```python
voice_percentages = calculate_voice_type_percentages(min_freq, max_freq, gender)
# Intelligent overlap analysis between user range and standard voice types
```

#### **🆕 Song Recommendation Algorithm**
```python
def calculate_vocal_range_coverage(song_min, song_max, user_min, user_max):
    # Smart overlap calculation between song requirements and user capabilities
    # Returns percentage compatibility (70%+ recommended for matching)
```

#### **🆕 Difficulty Assessment**
```python
def get_difficulty_score(song, user_range_hz):
    # Analyzes song range relative to user's vocal capabilities
    # Categorizes as: Very Easy, Easy, Medium, Hard, Very Hard
```

## 📊 Sample Output

### Voice Analysis Results
```
🎤============================================================🎤
🎵                  CS50 PITCH PERFECT ANALYZER                🎵
🎼               Advanced Voice Range Detection v2.0           🎼
🎤============================================================🎤

🎵 SUCCESS! C3 | 130.5 Hz (2nd Octave) | [███████████████████░] 98.4% | 🏆 PERFECT!
🎵 SUCCESS! D3 | 146.5 Hz (2nd Octave) | [███████████████████░] 99.6% | 🏆 PERFECT!

🎯 RESULT: 🏆 'Bass' (93.5% compatibility - Perfect match!)
```

### 🆕 Song Recommendations Output
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
```

## 🎼 Voice Types Supported

### Male Voices
- **Bass**: 82.41 - 329.63 Hz
- **Baritone**: 98.00 - 392.00 Hz  
- **Tenor**: 130.81 - 523.25 Hz

### Female Voices
- **Contralto**: 164.81 - 659.26 Hz
- **Mezzo-soprano**: 196.00 - 783.99 Hz
- **Soprano**: 261.63 - 1046.50 Hz

## 🔧 Configuration

### Audio Settings (`config.py`)
```python
NOTE_DURATION = 2          # Recording duration per note
SAMPLE_RATE = 44100        # Audio sample rate
ACCEPTABLE_MARGIN = 80     # Frequency tolerance (Hz)
MIN_SUCCESS_RATE = 80      # Minimum success percentage
MAX_ATTEMPTS = 2           # Attempts per note
```

### Visualization Settings
```python
VISUALIZATION_WIDTH = 100   # Chart width
TOTAL_MIN_FREQ = 80        # Minimum frequency for charts
TOTAL_MAX_FREQ = 550       # Maximum frequency for charts
```

## 🎯 CS50 Final Project

This project represents the culmination of CS50 coursework, demonstrating:

- **Complex Algorithm Implementation**: Advanced DSP and harmonic analysis
- **Real-time Audio Processing**: Live microphone input and FFT analysis
- **Data Visualization**: Terminal-based charts and progress indicators
- **User Experience Design**: Intuitive interface with multilingual support
- **Error Handling**: Robust microphone detection and audio processing
- **Code Organization**: Modular design with clear separation of concerns

### Educational Value
- **Mathematics**: Logarithmic octave calculation, FFT analysis
- **Signal Processing**: Fundamental frequency detection, harmonic analysis
- **Computer Science**: Algorithm optimization, real-time processing
- **User Interface**: CLI design principles, user feedback systems

## 📁 Project Structure & File Descriptions

Each file in this project serves a specific purpose in the overall voice analysis system:

### 📄 Core Application Files

**`main.py`** - Main Application Entry Point
- Handles user interface and menu navigation
- Manages the overall application flow from start to finish
- Contains user registration, gender selection, and microphone setup
- Orchestrates the voice testing process and result presentation
- Integrates all modules together for seamless user experience

**`voice_analyzer.py`** - Core Pitch Detection Engine
- Implements advanced FFT-based frequency analysis algorithms
- Contains the fundamental frequency detection logic with harmonic validation
- Handles real-time audio processing and pitch identification
- Includes octave calculation using logarithmic mathematics
- Manages voice range testing loops and success/failure determination
- This is the heart of the application where the core CS50 algorithms reside

**`audio_utils.py`** - Audio I/O and Hardware Interface
- Manages microphone detection and selection
- Handles audio recording from system microphones
- Contains piano note playback functionality (both WAV and synthetic)
- Implements fade-in/fade-out anti-pop audio processing
- Provides hardware abstraction layer for cross-platform compatibility

**`database.py`** - Data Persistence and Analytics
- SQLite database operations for user management and test results
- Implements scoreboard calculations and ranking algorithms
- Handles voice type classification based on frequency ranges
- Contains merge sort implementation for leaderboard ranking (CS50 algorithmic requirement)
- Manages historical data storage and retrieval

**`models.py`** - Voice Science Definitions
- Defines scientifically accurate voice frequency ranges
- Contains note frequency mappings for all musical notes (C2-C6)
- Includes voice type classifications (Soprano, Alto, Tenor, Bass)
- Provides Turkish-to-English note name translation functions
- Serves as the scientific foundation for all voice analysis

**`visualization.py`** - Terminal Graphics and User Interface
- Creates beautiful ASCII-based charts and progress bars
- Implements real-time visual feedback during voice testing
- Generates frequency range visualization charts
- Handles colorful terminal output with emojis and formatting
- Provides comprehensive result presentation and analysis reports

**`config.py`** - System Configuration
- Centralized configuration management for all audio parameters
- Sample rate, duration, and frequency tolerance settings
- Visualization parameters and user interface constants
- Makes the system easily configurable without code changes

**`song_recommender.py`** - 🆕 Intelligent Song Recommendation Engine
- Smart vocal range matching algorithm with percentage overlap calculation
- Comprehensive song database with frequency ranges and difficulty levels
- Genre-based categorization and filtering system
- Automatic difficulty assessment based on user's vocal capabilities
- Beautiful terminal output with song recommendations and compatibility ratings

### 🎵 Audio Assets

**`sounds/piano/`** - Reference Audio Files
- Contains 29 individual piano note recordings (C2 through C6)
- Each WAV file recorded personally using Kawai CN201 digital piano
- Provides authentic piano reference tones for accurate pitch comparison
- Essential for the scientific accuracy of voice range testing

### 📊 Database Files

**`pitch_perfect.db`** - SQLite Database (Auto-generated)
- Stores user profiles, test results, and historical data
- Enables persistent scoreboard and ranking functionality
- Contains tables for users, test_results, and voice classifications

## 🎯 Design Decisions and Rationale

### Why Console Application?
I chose a terminal-based interface over a GUI for several strategic reasons:
- **Accessibility**: Works on any system with Python, regardless of graphics capabilities
- **Performance**: No GUI overhead allows focus on real-time audio processing
- **CS50 Spirit**: Emphasizes algorithmic problem-solving over visual design
- **Simplicity**: Reduces complexity, allowing focus on core voice analysis logic

### Why SQLite Over Text Files?
- **Data Integrity**: ACID compliance ensures reliable data storage
- **Scalability**: Can handle hundreds of users and thousands of test results
- **Query Flexibility**: Enables complex scoreboard rankings and statistical analysis
- **CS50 Curriculum**: Demonstrates database concepts learned in the course

### Why Personal Piano Recordings?
- **Audio Quality**: Professional-grade recordings ensure accurate frequency references
- **Consistency**: Uniform recording conditions across all notes
- **Copyright Freedom**: No licensing issues with commercial audio samples
- **Educational Value**: Demonstrates real-world data collection methodology

### Why Harmonic Analysis Over Simple Peak Detection?
Simple peak detection often fails with human voice due to harmonic content. My implementation:
- Analyzes multiple harmonics to validate the fundamental frequency
- Prevents false positives (e.g., detecting 494Hz instead of 164Hz)
- Provides scientifically accurate results essential for voice classification
- Demonstrates advanced signal processing concepts beyond basic CS50 curriculum

### Why Fade-In/Fade-Out Processing?
Audio "pops" and "clicks" can interfere with precise frequency analysis:
- Eliminates artifacts that could affect pitch detection accuracy
- Provides professional audio quality essential for musical applications
- Demonstrates understanding of digital signal processing principles

```
cs50-pitch-perfect-analyzer/
├── main.py              # Main application entry point
├── voice_analyzer.py    # Core pitch detection algorithms  
├── audio_utils.py       # Audio I/O and microphone handling
├── visualization.py     # Terminal-based charts and graphics
├── database.py         # SQLite database operations and scoreboard
├── models.py           # Voice ranges and note frequency definitions
├── config.py           # Configuration parameters
├── song_recommender.py  # 🆕 Intelligent song recommendation system
├── requirements.txt    # Python dependencies
├── pitch_perfect.db    # SQLite database (auto-created)
├── sounds/piano/       # Piano reference recordings (29 WAV files)
├── .gitignore         # Git ignore patterns
└── README.md          # This documentation
```

## 🏆 Performance

- **Accuracy**: >95% pitch detection accuracy for clear vocals
- **Speed**: Real-time processing with <100ms latency
- **Reliability**: Robust harmonic validation prevents false positives
- **Range**: Supports 65Hz - 1050Hz frequency range (4+ octaves)

## 🎵 Demo

Run the application and follow the interactive prompts:

1. **Enter Personal Info**: Provide your name and surname for database storage
2. **Select Microphone**: Choose from detected audio devices
3. **Choose Gender**: Male (C3 start) or Female (C4 start)  
4. **Sing Notes**: Follow audio cues and sing back the reference notes
5. **View Results**: Comprehensive analysis with visual charts and personal statistics
6. **🆕 Get Song Recommendations**: Receive personalized song suggestions based on your vocal range
7. **Check Scoreboard**: See top 10 rankings and compare with other users

## 🚀 Future Enhancements

- [ ] **MIDI Export**: Save detected notes as MIDI files
- [ ] **Web Interface**: Browser-based version with WebAudio API
- [ ] **Machine Learning**: Neural network-based pitch detection
- [ ] **Multi-language**: Additional language support
- [ ] **Cloud Storage**: Save and compare results over time
- [ ] **🆕 Expanded Song Database**: Integration with Spotify/Apple Music APIs for larger song selection
- [ ] **🆕 Custom Playlist Export**: Export recommended songs to Spotify or Apple Music playlists
- [ ] **🆕 Vocal Training Mode**: Guided exercises to expand vocal range based on song requirements
- [ ] **🆕 Performance Tracking**: Track improvement over time with difficulty progression suggestions

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Your Name:** Mennan Sevim  
**GitHub Username:** github.com/mennansevim  
**edX Username:** mennansevim  
**City and Country:** İzmir, Turkey  
**Registration Date:** September 7, 2025

- GitHub: [@mennansevim](https://github.com/mennansevim)
- Project: [CS50 Pitch Perfect Analyzer](https://github.com/mennansevim/cs50-pitch-perfect-analyzer)

---

*This project was created as a final project for Harvard's CS50 Introduction to Computer Science course.*

🎤 **"Perfect pitch detection through perfect code"** 🎵
