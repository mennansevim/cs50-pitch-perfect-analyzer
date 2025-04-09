from typing import Dict, Tuple, List

# Ses aralıkları
VOICE_RANGES: Dict[str, Tuple[float, float]] = {
    "Kadın - Soprano": (261.63, 1046.50),    # C4 - C6
    "Kadın - Alto": (220.00, 698.46),        # A3 - F5
    "Erkek - Tenor": (130.81, 523.25),       # C3 - C5
    "Erkek - Bas": (82.41, 329.63)           # E2 - E4
}

# Nota frekansları
NOTE_FREQUENCIES: List[Tuple[str, float]] = [
    ("C2", 65.41), ("D2", 73.42), ("E2", 82.41), ("F2", 87.31), ("G2", 98.00), ("A2", 110.00), ("B2", 123.47),
    ("C3", 130.81), ("D3", 146.83), ("E3", 164.81), ("F3", 174.61), ("G3", 196.00), ("A3", 220.00), ("B3", 246.94),
    ("C4", 261.63), ("D4", 293.66), ("E4", 329.63), ("F4", 349.23), ("G4", 392.00), ("A4", 440.00), ("B4", 493.88),
    ("C5", 523.25), ("D5", 587.33), ("E5", 659.25), ("F5", 698.46), ("G5", 783.99), ("A5", 880.00), ("B5", 987.77),
    ("C6", 1046.50)
]

# Nota isimleri
NOTA_ISIMLERI: Dict[str, str] = {
    "C": "Do",
    "D": "Re",
    "E": "Mi",
    "F": "Fa",
    "G": "Sol",
    "A": "La",
    "B": "Si"
}

def nota_cevirici(note_name: str) -> str:
    """C4 gibi nota isimlerini Do4 formatına çevirir"""
    harf = note_name[0]
    oktav = note_name[1]
    return f"{NOTA_ISIMLERI[harf]}{oktav}" 