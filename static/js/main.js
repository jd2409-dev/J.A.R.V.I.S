const socket = io();
const screenImg = document.getElementById('screen');
const commandInput = document.getElementById('command-input');
const sendBtn = document.getElementById('send-btn');
const voiceBtn = document.getElementById('voice-btn');
const statusDiv = document.getElementById('status');

// Handle incoming screenshots
socket.on('screenshot', (data) => {
    screenImg.src = 'data:image/jpeg;base64,' + data.image;
});

// Handle AI responses
socket.on('ai_response', (data) => {
    statusDiv.innerText = 'J.A.R.V.I.S.: ' + data.message;
});

// Handle errors
socket.on('error', (data) => {
    statusDiv.innerText = 'Error: ' + data.message;
    statusDiv.style.color = '#ff4b2b';
});

// Send text commands
sendBtn.addEventListener('click', () => {
    const command = commandInput.value;
    if (command) {
        socket.emit('command', { command: command });
        commandInput.value = '';
        statusDiv.innerText = 'Processing command...';
    }
});

// Allow Enter key to send command
commandInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendBtn.click();
    }
});

// Handle mouse clicks on the screen
screenImg.addEventListener('click', (e) => {
    const rect = screenImg.getBoundingClientRect();
    const x = Math.round((e.clientX - rect.left) * (screenImg.naturalWidth / rect.width));
    const y = Math.round((e.clientY - rect.top) * (screenImg.naturalHeight / rect.height));

    socket.emit('mouse_click', { x: x, y: y, button: 'left' });
});

// Voice Control logic
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SpeechRecognition) {
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';

    voiceBtn.addEventListener('click', () => {
        recognition.start();
        statusDiv.innerText = 'Listening...';
        voiceBtn.innerText = 'LISTENING...';
    });

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        commandInput.value = transcript;
        voiceBtn.innerText = 'VOICE CONTROL';
        sendBtn.click();
    };

    recognition.onerror = (event) => {
        statusDiv.innerText = 'Speech recognition error: ' + event.error;
        voiceBtn.innerText = 'VOICE CONTROL';
    };
} else {
    voiceBtn.style.display = 'none';
    console.log('Speech Recognition not supported');
}
