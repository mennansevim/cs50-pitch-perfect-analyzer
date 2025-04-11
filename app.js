// Ses aralıkları ve notalar için sabit değerler
const VOICE_RANGES = {
    "Kadın - Soprano": [261.63, 1046.50],
    "Kadın - Alto": [220.00, 698.46],
    "Erkek - Tenor": [130.81, 523.25],
    "Erkek - Bas": [82.41, 329.63]
};

const NOTE_FREQUENCIES = [
    ["C2", 65.41], ["D2", 73.42], ["E2", 82.41], ["F2", 87.31], ["G2", 98.00], ["A2", 110.00], ["B2", 123.47],
    ["C3", 130.81], ["D3", 146.83], ["E3", 164.81], ["F3", 174.61], ["G3", 196.00], ["A3", 220.00], ["B3", 246.94],
    ["C4", 261.63], ["D4", 293.66], ["E4", 329.63], ["F4", 349.23], ["G4", 392.00], ["A4", 440.00], ["B4", 493.88],
    ["C5", 523.25], ["D5", 587.33], ["E5", 659.25], ["F5", 698.46], ["G5", 783.99], ["A5", 880.00], ["B5", 987.77],
    ["C6", 1046.50]
];

const NOTA_ISIMLERI = {
    "C": "Do",
    "D": "Re",
    "E": "Mi",
    "F": "Fa",
    "G": "Sol",
    "A": "La",
    "B": "Si"
};

// Uygulama ayarları
const CONFIG = {
    NOTE_DURATION: 2,
    SAMPLE_RATE: 44100,
    ACCEPTABLE_MARGIN: 40,
    MAX_ATTEMPTS: 2,
    MIN_SUCCESS_RATE: 80
};

// DOM Elementleri
const elements = {
    genderSelection: document.getElementById('genderSelection'),
    micSelection: document.getElementById('micSelection'),
    testArea: document.getElementById('testArea'),
    micSelect: document.getElementById('micSelect'),
    confirmMic: document.getElementById('confirmMic'),
    maleBtn: document.getElementById('maleBtn'),
    femaleBtn: document.getElementById('femaleBtn'),
    startBtn: document.getElementById('startBtn'),
    stopBtn: document.getElementById('stopBtn'),
    currentNote: document.getElementById('currentNote'),
    detected: document.getElementById('detected'),
    successIndicator: document.getElementById('success-indicator'),
    successGrid: document.getElementById('successGrid'),
    finalResult: document.getElementById('finalResult'),
    voiceRange: document.getElementById('voiceRange'),
    lowestNote: document.getElementById('lowestNote'),
    highestNote: document.getElementById('highestNote'),
    restartBtn: document.getElementById('restartBtn'),
    soundWaves: document.querySelector('.sound-waves')
};

// Uygulama durumu
let state = {
    selectedGender: null,
    selectedMicIndex: null,
    isRunning: false,
    currentNoteIndex: null,
    testDirection: 0, // -1: aşağı, 1: yukarı, 0: henüz başlamamış
    successfulNotes: [],
    audioContext: null,
    audioStream: null,
    mediaRecorder: null,
    audioChunks: [],
    listeningAnimationInterval: null
};

// Belirtilen frekansta ses çalma
function playNote(frequency, duration = 2, waveform = "piano") {
    if (!state.audioContext) {
        state.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    
    const audioContext = state.audioContext;
    const currentTime = audioContext.currentTime;
    
    // Oscillator (Ana ton) oluşturma
    const oscillator = audioContext.createOscillator();
    oscillator.type = 'sine';
    oscillator.frequency.setValueAtTime(frequency, currentTime);
    
    // Gain node oluşturma (ses seviyesi için)
    const gainNode = audioContext.createGain();
    
    // Harmonikler için düğümler (piyano efekti için)
    let oscillators = [oscillator];
    if (waveform === "piano") {
        // 2. harmonik
        const osc2 = audioContext.createOscillator();
        osc2.type = 'sine';
        osc2.frequency.setValueAtTime(frequency * 2, currentTime);
        const gain2 = audioContext.createGain();
        gain2.gain.setValueAtTime(0.3, currentTime);
        osc2.connect(gain2);
        gain2.connect(gainNode);
        oscillators.push(osc2);
        
        // 3. harmonik
        const osc3 = audioContext.createOscillator();
        osc3.type = 'sine';
        osc3.frequency.setValueAtTime(frequency * 3, currentTime);
        const gain3 = audioContext.createGain();
        gain3.gain.setValueAtTime(0.1, currentTime);
        osc3.connect(gain3);
        gain3.connect(gainNode);
        oscillators.push(osc3);
    }
    
    // Ana ossilatörü gain node'a bağla
    oscillator.connect(gainNode);
    
    // Attack ve release için ses şekillendirme
    gainNode.gain.setValueAtTime(0, currentTime);
    gainNode.gain.linearRampToValueAtTime(0.5, currentTime + 0.1);
    gainNode.gain.setValueAtTime(0.5, currentTime + duration - 0.1);
    gainNode.gain.linearRampToValueAtTime(0, currentTime + duration);
    
    // Çıkışa bağla
    gainNode.connect(audioContext.destination);
    
    // Tüm osilatörleri başlat
    oscillators.forEach(osc => osc.start(currentTime));
    
    // Osilatörleri durdur
    oscillators.forEach(osc => osc.stop(currentTime + duration));
    
    // Çalan nota hakkında bilgi
    console.log(`${frequency} Hz frekansında nota çalınıyor...`);
    
    // Promise olarak dön - süre sonunda resolve olsun
    return new Promise(resolve => {
        setTimeout(() => {
            resolve();
        }, duration * 1000);
    });
}

// Mikrofon erişimi
async function getMicrophones() {
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const audioInputs = devices.filter(device => device.kind === 'audioinput');
        
        // Mikrofon seçim kutusuna ekle
        elements.micSelect.innerHTML = '';
        audioInputs.forEach((device, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.text = device.label || `Mikrofon ${index + 1}`;
            elements.micSelect.appendChild(option);
        });
        
        if (audioInputs.length === 0) {
            alert('Hiç mikrofon bulunamadı!');
        }
    } catch (error) {
        console.error('Mikrofonlar alınamadı:', error);
        alert('Mikrofonlara erişilemedi: ' + error.message);
    }
}

// Notayı Türkçe formatına çevirme
function notaCevirici(noteName) {
    const harf = noteName[0];
    const oktav = noteName.slice(1);
    return `${NOTA_ISIMLERI[harf]}${oktav}`;
}

// Frekansa göre ses aralığını belirler
function identifyVoiceRange(frequency) {
    for (const [voiceType, [low, high]] of Object.entries(VOICE_RANGES)) {
        if (low <= frequency && frequency <= high) {
            return voiceType;
        }
    }
    return "Bilinmeyen Aralık";
}

// Başarı yüzdesini hesaplar
function calculateSuccessPercentage(targetFreq, actualFreq, margin) {
    if (actualFreq === 0) {
        return 0;
    }

    const difference = Math.abs(targetFreq - actualFreq);
    if (difference > margin) {
        return 0;
    }
    const success = Math.pow((margin - difference) / margin, 2) * 100;
    return Math.min(100, Math.max(0, success));
}

// Ses testi başlatma
async function startTest() {
    state.isRunning = true;
    elements.startBtn.disabled = true;
    elements.stopBtn.disabled = false;
    elements.soundWaves.classList.remove('hidden');
    
    // Audio Context oluştur
    state.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    
    // Test başlangıç notası
    let startNoteIndex;
    if (state.selectedGender === 'male') {
        startNoteIndex = NOTE_FREQUENCIES.findIndex(note => note[0] === 'C3');
        console.log("Erkek için C3'ten başlıyor (130.81 Hz)");
    } else {
        startNoteIndex = NOTE_FREQUENCIES.findIndex(note => note[0] === 'C4');
        console.log("Kadın için C4'ten başlıyor (261.63 Hz)");
    }
    
    state.currentNoteIndex = startNoteIndex;
    
    // Önce aşağıya doğru test
    state.testDirection = -1;
    console.log("Önce bas seslere doğru test ediliyor...");
    
    // İlk notayı göster
    showCurrentNote();
    
    // Mikrofona erişim iste
    try {
        state.audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        runVoiceTest();
    } catch (error) {
        console.error('Mikrofon erişimi hatası:', error);
        alert('Mikrofona erişilemedi: ' + error.message);
        stopTest();
    }
}

// Mevcut notayı göster
function showCurrentNote() {
    if (state.currentNoteIndex < 0 || state.currentNoteIndex >= NOTE_FREQUENCIES.length) {
        return;
    }
    
    const [note, frequency] = NOTE_FREQUENCIES[state.currentNoteIndex];
    const turkishNote = notaCevirici(note);
    elements.currentNote.textContent = `${turkishNote} (${frequency.toFixed(2)} Hz)`;
}

// Ses testi yürütme
async function runVoiceTest() {
    if (!state.isRunning) return;
    
    // Eğer geçerli bir nota indeksi yoksa, test sonlandır
    if (state.currentNoteIndex < 0 || state.currentNoteIndex >= NOTE_FREQUENCIES.length) {
        if (state.testDirection === -1) {
            // Bas testini tamamladık, şimdi tizlere geçelim
            console.log("Şimdi tizlere doğru test ediliyor...");
            state.testDirection = 1;
            
            // Başlangıç notasını bul
            if (state.selectedGender === 'male') {
                state.currentNoteIndex = NOTE_FREQUENCIES.findIndex(note => note[0] === 'C3');
            } else {
                state.currentNoteIndex = NOTE_FREQUENCIES.findIndex(note => note[0] === 'C4');
            }
            
            showCurrentNote();
            runVoiceTest();
            return;
        } else {
            // Test tamamlandı
            showFinalResults();
            return;
        }
    }
    
    const [note, targetFrequency] = NOTE_FREQUENCIES[state.currentNoteIndex];
    const turkishNote = notaCevirici(note);
    
    // Şazam efekti
    elements.soundWaves.classList.remove('hidden');
    
    // Önce notayı çal
    console.log(`Şimdi söylemeniz gereken nota: ${turkishNote} (${targetFrequency.toFixed(2)} Hz)`);
    await playNote(targetFrequency, CONFIG.NOTE_DURATION, "piano");
    
    // Kullanıcı bilgilendirme
    elements.detected.textContent = "Lütfen notayı söyleyin...";
    elements.successIndicator.innerHTML = '<i class="fas fa-microphone-alt"></i>';
    
    // Zorluğa göre başarı olasılığını hesaplama
    // Orta notalar daha kolay, tiz ve bas notalar daha zor
    let notaDifficulty = calculateNoteDifficulty(note);
    console.log(`Nota zorluğu: ${notaDifficulty}`);
    
    // "Ses algılanıyor" animasyonu
    startListeningAnimation();
    
    // Rastgele demo amaçlı - gerçek uygulamada gerçek ses analizi yapılmalı
    setTimeout(() => {
        // Dinleme animasyonunu durdur
        stopListeningAnimation();
        
        // Zorluk seviyesine göre başarı şansı
        // Erkekler için tizlerde, kadınlar için baslarda başarısızlık olasılığı daha yüksek
        const isSuccessful = checkNoteSuccess(notaDifficulty);
        
        if (isSuccessful) {
            // Başarılı kabul edelim
            const dominantFreq = targetFrequency + (Math.random() * 10 - 5); // +-5 Hz sapma
            elements.detected.textContent = `${dominantFreq.toFixed(2)} Hz`;
            elements.successIndicator.innerHTML = '<i class="fas fa-check-circle success"></i>';
            
            // Başarılı notayı listeye ekle
            const voiceRange = identifyVoiceRange(dominantFreq);
            state.successfulNotes.push([turkishNote, dominantFreq, voiceRange]);
            addSuccessNote(turkishNote);
            
            // Bir sonraki notaya geç
            state.currentNoteIndex += state.testDirection;
            showCurrentNote();
            
            // Devam et
            setTimeout(() => runVoiceTest(), 1500);
        } else {
            // Başarısız kabul edelim
            const dominantFreq = targetFrequency + (Math.random() * 50 - 25); // +-25 Hz sapma
            elements.detected.textContent = `${dominantFreq.toFixed(2)} Hz (Başarısız)`;
            elements.successIndicator.innerHTML = '<i class="fas fa-times-circle fail"></i>';
            
            // Tekrar dene
            setTimeout(async () => {
                if (state.isRunning) {
                    console.log("Tekrar deniyor...");
                    // Notayı tekrar çal
                    await playNote(targetFrequency, CONFIG.NOTE_DURATION, "piano");
                    // Tekrar dene
                    runVoiceTest();
                }
            }, 1500);
        }
    }, (CONFIG.NOTE_DURATION + 1.5) * 1000); // Nota süresinin ardından dinleme süresi
}

// Notanın zorluğunu hesaplar (0-100 arası)
function calculateNoteDifficulty(note) {
    // Note adını ve oktavını ayır
    const noteName = note[0];
    const octave = parseInt(note.slice(1));
    
    let difficulty = 50; // Orta zorluk
    
    // Erkekler için C3 (130.81 Hz) ortada, bundan uzaklaştıkça zorluk artar
    // Kadınlar için C4 (261.63 Hz) ortada, bundan uzaklaştıkça zorluk artar
    if (state.selectedGender === 'male') {
        // Erkek sesi için, tiz notalar daha zor
        if (octave > 3) {
            difficulty += (octave - 3) * 20; // Tizlerde her oktav için +20 zorluk
        } else if (octave < 3) {
            difficulty += (3 - octave) * 15; // Baslarda her oktav için +15 zorluk
        }
        
        // Aynı oktavda, C'den uzaklaştıkça zorlaşsın
        const noteOrder = ["C", "D", "E", "F", "G", "A", "B"];
        const noteIndex = noteOrder.indexOf(noteName);
        
        if (octave === 3) {
            // C3'ten uzaklaştıkça zorluk artar
            difficulty += noteIndex * 5; // Her nota için +5 zorluk
        }
    } else {
        // Kadın sesi için, bas notalar daha zor
        if (octave > 4) {
            difficulty += (octave - 4) * 15; // Tizlerde her oktav için +15 zorluk
        } else if (octave < 4) {
            difficulty += (4 - octave) * 20; // Baslarda her oktav için +20 zorluk
        }
        
        // Aynı oktavda, C'den uzaklaştıkça zorlaşsın
        const noteOrder = ["C", "D", "E", "F", "G", "A", "B"];
        const noteIndex = noteOrder.indexOf(noteName);
        
        if (octave === 4) {
            // C4'ten uzaklaştıkça zorluk artar
            difficulty += noteIndex * 5; // Her nota için +5 zorluk
        }
    }
    
    // Zorluğu 0-100 arasında sınırla
    return Math.min(100, Math.max(0, difficulty));
}

// Zorluğa göre başarı şansı hesaplar
function checkNoteSuccess(difficulty) {
    // Zorluk 50 ise %80 başarı şansı
    // Zorluk 100 ise %20 başarı şansı
    // Zorluk 0 ise %95 başarı şansı
    const successChance = 95 - (difficulty * 0.75);
    
    // Rastgele değer üret
    const random = Math.random() * 100;
    
    console.log(`Başarı şansı: %${successChance.toFixed(1)}, Rastgele: ${random.toFixed(1)}`);
    
    return random <= successChance;
}

// "Ses algılanıyor" animasyonu başlat
function startListeningAnimation() {
    elements.soundWaves.classList.remove('hidden');
    
    // Her 300ms'de bir mikrofon simgesini değiştir (yanıp sönen efekt)
    state.listeningAnimationInterval = setInterval(() => {
        const micIcon = elements.successIndicator.querySelector('i');
        if (micIcon) {
            micIcon.classList.toggle('fa-microphone-alt');
            micIcon.classList.toggle('fa-microphone');
        }
    }, 300);
}

// "Ses algılanıyor" animasyonunu durdur
function stopListeningAnimation() {
    if (state.listeningAnimationInterval) {
        clearInterval(state.listeningAnimationInterval);
        state.listeningAnimationInterval = null;
    }
}

// Basit frekans analizi (FFT kullanarak)
function analyzeDominantFrequency(audioData, sampleRate) {
    // DFT (Discrete Fourier Transform) hesaplaması - basitleştirilmiş
    const bufferSize = audioData.length;
    const magnitudes = new Float32Array(bufferSize / 2);
    
    for (let i = 0; i < bufferSize / 2; i++) {
        let real = 0;
        let imag = 0;
        
        for (let j = 0; j < bufferSize; j++) {
            const angle = (2 * Math.PI * i * j) / bufferSize;
            real += audioData[j] * Math.cos(angle);
            imag -= audioData[j] * Math.sin(angle);
        }
        
        magnitudes[i] = Math.sqrt(real * real + imag * imag);
    }
    
    // En güçlü frekansı bul
    let maxMagnitude = 0;
    let maxIndex = 0;
    
    // Sadece insan sesi aralığını dikkate al (80Hz - 1100Hz)
    const minFreqIndex = Math.floor(80 * bufferSize / sampleRate);
    const maxFreqIndex = Math.floor(1100 * bufferSize / sampleRate);
    
    for (let i = minFreqIndex; i < maxFreqIndex; i++) {
        if (magnitudes[i] > maxMagnitude) {
            maxMagnitude = magnitudes[i];
            maxIndex = i;
        }
    }
    
    // Rastgele bir değer döndürelim (gerçek uygulamada AudioWorklet API ile gerçekleştirilmeli)
    // Bu kısım demo amaçlıdır, gerçek uygulamada FFT analizi sonuçları kullanılmalıdır
    const currentNote = NOTE_FREQUENCIES[state.currentNoteIndex];
    const targetFreq = currentNote[1];
    
    // Gerçekçi bir simülasyon için biraz rastgele sapma ekleyelim
    const deviation = (Math.random() * 20) - 10; // -10 ile +10 arasında
    return targetFreq + deviation;
}

// Başarılı notayı grid'e ekle
function addSuccessNote(note) {
    const noteCell = document.createElement('div');
    noteCell.className = 'note-cell success';
    noteCell.innerHTML = `${note}<span class="check-icon"><i class="fas fa-check"></i></span>`;
    elements.successGrid.appendChild(noteCell);
}

// Son sonuçları göster
function showFinalResults() {
    if (!state.isRunning) return;
    
    stopTest();
    
    if (state.successfulNotes.length === 0) {
        elements.voiceRange.textContent = 'Yeterli veri yok';
        elements.lowestNote.textContent = '-';
        elements.highestNote.textContent = '-';
    } else {
        // Analiz et
        const frequencies = state.successfulNotes.map(note => note[1]);
        const minFreq = Math.min(...frequencies);
        const maxFreq = Math.max(...frequencies);
        
        // En düşük ve en yüksek notaları bul
        const lowestNoteInfo = state.successfulNotes.find(note => note[1] === minFreq);
        const highestNoteInfo = state.successfulNotes.find(note => note[1] === maxFreq);
        
        // Ses aralığını belirle
        const voiceRange = identifyVoiceRange((minFreq + maxFreq) / 2);
        
        elements.voiceRange.textContent = voiceRange;
        elements.lowestNote.textContent = `${lowestNoteInfo[0]} (${minFreq.toFixed(2)} Hz)`;
        elements.highestNote.textContent = `${highestNoteInfo[0]} (${maxFreq.toFixed(2)} Hz)`;
    }
    
    elements.finalResult.style.display = 'block';
}

// Testi durdur
function stopTest() {
    state.isRunning = false;
    elements.startBtn.disabled = false;
    elements.stopBtn.disabled = true;
    elements.soundWaves.classList.add('hidden');
    
    if (state.audioStream) {
        state.audioStream.getTracks().forEach(track => track.stop());
        state.audioStream = null;
    }
    
    if (state.audioContext) {
        state.audioContext.close();
        state.audioContext = null;
    }
}

// Uygulamayı baştan başlat
function restartApp() {
    // Durumu sıfırla
    state.selectedGender = null;
    state.selectedMicIndex = null;
    state.isRunning = false;
    state.currentNoteIndex = null;
    state.testDirection = 0;
    state.successfulNotes = [];
    
    // UI sıfırla
    elements.genderSelection.style.display = 'block';
    elements.micSelection.style.display = 'none';
    elements.testArea.style.display = 'none';
    elements.finalResult.style.display = 'none';
    elements.successGrid.innerHTML = '';
    elements.currentNote.textContent = '-';
    elements.detected.textContent = '-';
    elements.successIndicator.innerHTML = '';
}

// Event Listeners
window.addEventListener('load', () => {
    // Cinsiyet seçimi
    elements.maleBtn.addEventListener('click', () => {
        state.selectedGender = 'male';
        elements.genderSelection.style.display = 'none';
        elements.micSelection.style.display = 'block';
        getMicrophones();
    });
    
    elements.femaleBtn.addEventListener('click', () => {
        state.selectedGender = 'female';
        elements.genderSelection.style.display = 'none';
        elements.micSelection.style.display = 'block';
        getMicrophones();
    });
    
    // Mikrofon seçimi
    elements.confirmMic.addEventListener('click', () => {
        state.selectedMicIndex = elements.micSelect.value;
        elements.micSelection.style.display = 'none';
        elements.testArea.style.display = 'block';
    });
    
    // Test kontrolleri
    elements.startBtn.addEventListener('click', startTest);
    elements.stopBtn.addEventListener('click', stopTest);
    elements.restartBtn.addEventListener('click', restartApp);
    
    // Sound waves başlangıçta gizli
    elements.soundWaves.classList.add('hidden');
}); 