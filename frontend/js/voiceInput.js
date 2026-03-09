// Voice Input Service
class VoiceInputService {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.voiceBtn = null;
        this.messageInput = null;
        this.voiceIcon = null;
        
        this.initializeSpeechRecognition();
        this.bindEvents();
    }
    
    initializeSpeechRecognition() {
        // Check browser support
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.warn('Speech recognition not supported in this browser');
            this.showError('Speech recognition not supported. Please use Chrome or Edge.');
            if (this.voiceBtn) {
                this.voiceBtn.style.display = 'none';
            }
            return;
        }
        
        try {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            // Configure recognition
            this.recognition.continuous = true; // Keep listening continuously
            this.recognition.interimResults = true; // Show interim results
            this.recognition.lang = 'en-US';
            this.recognition.maxAlternatives = 1;
            
            // Add timeout handling
            this.silenceTimeout = null;
            this.maxSilenceTime = 15000; // 15 seconds of silence before stopping
            this.accumulatedText = ''; // Store accumulated text
            
            // Event handlers
            this.recognition.onstart = () => {
                console.log('🎤 Speech recognition started');
                this.isListening = true;
                this.accumulatedText = ''; // Reset accumulated text for new session
                this.updateUI(true);
                this.showStatus('Listening... Speak now!');
            };
            
            this.recognition.onresult = (event) => {
                console.log('🎤 Speech recognition result:', event);
                console.log('🎤 Results length:', event.results.length);
                
                // Clear any existing silence timeout
                if (this.silenceTimeout) {
                    clearTimeout(this.silenceTimeout);
                }
                
                let finalTranscript = '';
                let interimTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const result = event.results[i];
                    const transcript = result[0].transcript;
                    console.log(`🎤 Result ${i}:`, transcript, 'isFinal:', result.isFinal);
                    
                    if (result.isFinal) {
                        finalTranscript += transcript;
                        // Accumulate final text
                        this.accumulatedText += finalTranscript + ' ';
                        console.log('🎤 Accumulated text:', this.accumulatedText);
                    } else {
                        interimTranscript += transcript;
                    }
                }
                
                console.log('🎤 Final transcript:', finalTranscript);
                console.log('🎤 Interim transcript:', interimTranscript);
                console.log('🎤 Total accumulated text:', this.accumulatedText);
                console.log('🎤 Message input element:', this.messageInput);
                
                // Handle interim results (continuous listening)
                if (interimTranscript && this.messageInput) {
                    // Show accumulated + interim text for feedback
                    const displayText = this.accumulatedText + interimTranscript;
                    this.messageInput.value = displayText;
                    
                    // Trigger input event
                    const inputEvent = new Event('input', { bubbles: true });
                    this.messageInput.dispatchEvent(inputEvent);
                    
                    console.log('🎤 Interim text set:', displayText);
                    this.showStatus('Listening: ' + displayText);
                    
                    // Set timeout to stop after silence
                    this.silenceTimeout = setTimeout(() => {
                        console.log('🎤 Silence detected, stopping recognition');
                        if (this.recognition && this.isListening) {
                            this.recognition.stop();
                        }
                    }, this.maxSilenceTime);
                }
                
                // Handle final results
                if (finalTranscript && this.messageInput) {
                    // Clear silence timeout
                    if (this.silenceTimeout) {
                        clearTimeout(this.silenceTimeout);
                        this.silenceTimeout = null;
                    }
                    
                    // Set accumulated text (includes previous + new)
                    this.messageInput.value = this.accumulatedText;
                    
                    // Trigger events
                    const inputEvent = new Event('input', { bubbles: true });
                    this.messageInput.dispatchEvent(inputEvent);
                    
                    const changeEvent = new Event('change', { bubbles: true });
                    this.messageInput.dispatchEvent(changeEvent);
                    
                    console.log('🎤 Final accumulated text set:', this.accumulatedText);
                    console.log('🎤 Input value after setting:', this.messageInput.value);
                    this.showStatus('Voice input captured! Click to continue.');
                    
                    // Keep listening for more input
                    setTimeout(() => {
                        if (this.isListening) {
                            console.log('🎤 Restarting continuous listening...');
                            this.recognition.start();
                        }
                    }, 1000);
                } else if (!interimTranscript) {
                    console.warn('🎤 No transcript received');
                }
            };
            
            this.recognition.onerror = (event) => {
                console.error('🎤 Speech recognition error:', event.error, event.message);
                this.isListening = false;
                this.updateUI(false);
                
                let errorMessage = 'Voice recognition failed. ';
                switch (event.error) {
                    case 'no-speech':
                        errorMessage += 'No speech detected. Please try again.';
                        break;
                    case 'audio-capture':
                        errorMessage += 'Microphone not found or not allowed. Please check permissions.';
                        break;
                    case 'not-allowed':
                        errorMessage += 'Microphone permission denied. Please allow microphone access.';
                        break;
                    case 'network':
                        errorMessage += 'Network error. Please check your connection.';
                        break;
                    case 'service-not-allowed':
                        errorMessage += 'Speech recognition service not allowed.';
                        break;
                    default:
                        errorMessage += 'Please try again.';
                }
                
                this.showError(errorMessage);
            };
            
            this.recognition.onend = () => {
                console.log('🎤 Speech recognition ended');
                this.isListening = false;
                this.updateUI(false);
                this.showStatus('');
            };
            
            console.log('🎤 Speech recognition initialized successfully');
            
        } catch (error) {
            console.error('🎤 Failed to initialize speech recognition:', error);
            this.showError('Failed to initialize voice recognition');
        }
    }
    
    bindEvents() {
        console.log('🎤 Binding voice input events...');
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.bindElements());
        } else {
            this.bindElements();
        }
    }
    
    bindElements() {
        this.voiceBtn = document.getElementById('voiceBtn');
        this.messageInput = document.getElementById('messageInput');
        this.voiceIcon = document.getElementById('voiceIcon');
        
        console.log('🎤 DOM Elements found:', {
            voiceBtn: !!this.voiceBtn,
            messageInput: !!this.messageInput,
            voiceIcon: !!this.voiceIcon
        });
        
        if (this.voiceBtn) {
            this.voiceBtn.addEventListener('click', () => this.toggleVoiceInput());
            console.log('🎤 Voice button event listener attached');
        } else {
            console.error('🎤 Voice button not found - checking DOM...');
            // Debug: log all buttons
            const allButtons = document.querySelectorAll('button');
            console.log('🎤 All buttons found:', allButtons.length);
            allButtons.forEach((btn, index) => {
                console.log(`🎤 Button ${index}:`, btn.id, btn.className);
            });
        }
        
        if (!this.messageInput) {
            console.error('🎤 Message input not found - checking DOM...');
            // Debug: log all inputs
            const allInputs = document.querySelectorAll('input');
            console.log('🎤 All inputs found:', allInputs.length);
            allInputs.forEach((input, index) => {
                console.log(`🎤 Input ${index}:`, input.id, input.type, input.placeholder);
            });
        }
    }
    
    async toggleVoiceInput() {
        if (!this.recognition) {
            this.showError('Speech recognition not supported');
            return;
        }
        
        if (this.isListening) {
            console.log('🎤 Stopping speech recognition');
            this.isListening = false;
            if (this.silenceTimeout) {
                clearTimeout(this.silenceTimeout);
                this.silenceTimeout = null;
            }
            this.recognition.stop();
            this.updateUI(false);
            this.showStatus('Voice input stopped');
        } else {
            // Request microphone permission
            try {
                console.log('🎤 Requesting microphone permission...');
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                console.log('🎤 Microphone permission granted');
                stream.getTracks().forEach(track => track.stop()); // Stop stream immediately
                
                // Start speech recognition
                console.log('🎤 Starting continuous speech recognition');
                this.isListening = true;
                this.recognition.start();
                this.updateUI(true);
                this.showStatus('Continuous listening... Speak now!');
            } catch (error) {
                console.error('🎤 Microphone permission denied:', error);
                this.showError('Microphone permission denied. Please allow microphone access in your browser settings.');
            }
        }
    }
    
    updateUI(isListening) {
        if (!this.voiceBtn || !this.voiceIcon) return;
        
        if (isListening) {
            this.voiceBtn.classList.remove('text-gray-500');
            this.voiceBtn.classList.add('text-red-500', 'animate-pulse');
            this.voiceIcon.innerHTML = `
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            `;
        } else {
            this.voiceBtn.classList.remove('text-red-500', 'animate-pulse');
            this.voiceBtn.classList.add('text-gray-500');
            this.voiceIcon.innerHTML = `
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
            `;
        }
    }
    
    showError(message) {
        console.error('🎤 Voice Input Error:', message);
        
        // Remove existing error messages
        const existingErrors = document.querySelectorAll('.voice-error');
        existingErrors.forEach(error => error.remove());
        
        // Show new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'voice-error fixed top-4 right-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg z-50 max-w-sm';
        errorDiv.innerHTML = `
            <div class="flex items-center">
                <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
                </svg>
                <span>${message}</span>
            </div>
        `;
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
    
    showStatus(message) {
        // Remove existing status messages
        const existingStatus = document.querySelectorAll('.voice-status');
        existingStatus.forEach(status => status.remove());
        
        if (message) {
            const statusDiv = document.createElement('div');
            statusDiv.className = 'voice-status fixed top-4 left-4 bg-blue-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
            statusDiv.innerHTML = `
                <div class="flex items-center">
                    <svg class="w-5 h-5 mr-2 animate-pulse" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clip-rule="evenodd"></path>
                    </svg>
                    <span>${message}</span>
                </div>
            `;
            document.body.appendChild(statusDiv);
            
            setTimeout(() => {
                statusDiv.remove();
            }, 3000);
        }
    }
}

// Initialize voice input when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎤 Initializing voice input service...');
    window.voiceInputService = new VoiceInputService();
    
    // Add browser compatibility check
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        console.warn('🎤 Speech recognition not supported in this browser');
        console.log('🎤 Please use Chrome, Edge, or Safari for voice input');
    } else {
        console.log('🎤 Speech recognition supported in this browser');
    }
});
