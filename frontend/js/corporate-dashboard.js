// Corporate Dashboard JavaScript
class CorporateDashboard {
    constructor() {
        this.sessionId = localStorage.getItem('session_id');
        this.userName = localStorage.getItem('user_name');
        this.chatHistory = [];
        this.stats = {
            totalQueries: 0,
            avgConfidence: 0,
            toolsUsed: 0,
            avgResponseTime: 0
        };
        this.voiceEnabled = false;
        this.settings = {
            temperature: 0.3,
            maxTokens: 1000,
            theme: 'dark'
        };
        
        this.init();
    }

    init() {
        this.checkAuth();
        this.setupEventListeners();
        this.initializeUI();
        this.loadStats();
        this.startRealTimeUpdates();
    }

    checkAuth() {
        if (!this.sessionId || !this.userName) {
            window.location.href = 'login.html';
            return false;
        }
        return true;
    }

    setupEventListeners() {
        // Chat functionality
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        
        sendBtn.addEventListener('click', () => this.sendMessage());
        
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize textarea
        messageInput.addEventListener('input', () => {
            this.updateCharCount();
            this.autoResizeTextarea(messageInput);
        });

        // Quick action buttons
        document.querySelectorAll('.quick-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const query = btn.getAttribute('data-query');
                messageInput.value = query;
                this.updateCharCount();
                this.sendMessage();
            });
        });

        // Voice toggle
        document.getElementById('voiceToggle').addEventListener('click', () => {
            this.toggleVoice();
        });

        document.getElementById('voiceBtn').addEventListener('click', () => {
            this.startVoiceInput();
        });

        // Tool results
        document.getElementById('closeToolResults').addEventListener('click', () => {
            document.getElementById('toolResults').style.display = 'none';
        });

        // Settings modal
        document.getElementById('settingsBtn').addEventListener('click', () => {
            this.showSettings();
        });

        document.getElementById('closeSettings').addEventListener('click', () => {
            this.hideSettings();
            this.closeSettings();
        });

        document.getElementById('saveSettings').addEventListener('click', () => {
            this.saveSettings();
        });

        document.getElementById('cancelSettings').addEventListener('click', () => {
            this.closeSettings();
        });

        // Chat actions
        document.getElementById('clearChat').addEventListener('click', () => {
            this.clearChat();
        });

        document.getElementById('exportChat').addEventListener('click', () => {
            this.toggleExportMenu();
        });

        // Export menu items
        document.getElementById('exportJSON').addEventListener('click', () => {
            this.exportChat('json');
        });

        document.getElementById('exportPDF').addEventListener('click', () => {
            this.exportChat('pdf');
        });

        // Logout
        document.getElementById('logoutBtn').addEventListener('click', () => {
            this.logout();
        });

        // Temperature slider
        document.getElementById('temperatureSlider').addEventListener('input', (e) => {
            document.getElementById('temperatureValue').textContent = (e.target.value / 100).toFixed(2);
        });

        // Close export menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#exportChat') && !e.target.closest('#exportMenu')) {
                this.hideExportMenu();
            }
        });
    }

    initializeUI() {
        // Set user name
        document.getElementById('userName').textContent = this.userName;
        
        // Initialize stats
        this.updateStatsDisplay();
        
        // Focus on message input
        document.getElementById('messageInput').focus();
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message) return;

        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Clear input
        messageInput.value = '';
        this.updateCharCount();
        this.autoResizeTextarea(messageInput);

        // Show loading
        this.showLoading();

        try {
            const startTime = Date.now();
            
            const response = await fetch(`${window.location.origin}/generate-prompt`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    user_query: message
                })
            });

            const responseTime = Date.now() - startTime;
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Process response
            await this.processAIResponse(data, responseTime);
            
            // Update stats
            this.updateStats(data, responseTime);
            
        } catch (error) {
            console.error('Error:', error);
            this.addMessage('Sorry, I encountered an error processing your request. Please try again.', 'ai', true);
        } finally {
            this.hideLoading();
        }
    }

    async processAIResponse(data, responseTime) {
        let responseText = '';
        
        if (data.llm_response) {
            // New RAG + LLM format
            responseText = data.llm_response;
            
            // Add metadata info
            const metadata = `📊 **Analysis Results:**\n` +
                           `• **Model:** ${data.model_used || 'Groq LLaMA3 + FAISS RAG'}\n` +
                           `• **Confidence:** ${data.confidence_score || 0}%\n` +
                           `• **Context Chunks:** ${data.retrieved_context?.length || 0}\n` +
                           `• **Response Time:** ${(responseTime / 1000).toFixed(2)}s\n\n`;
            
            this.addMessage(metadata + responseText, 'ai');
            
            // Handle tool output
            if (data.tool_output) {
                this.displayToolResults(data.tool_output);
            }
            
        } else if (data.generated_response || data.generated_prompt) {
            // Legacy format
            responseText = data.generated_response || data.generated_prompt;
            this.addMessage(responseText, 'ai');
        } else {
            this.addMessage('I received your query but couldn\'t generate a proper response. Please try rephrasing your question.', 'ai', true);
        }
    }

    addMessage(content, sender, isError = false) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const timestamp = new Date().toLocaleTimeString();
        
        if (sender === 'user') {
            messageDiv.innerHTML = `
                <div class="message-content">
                    <div class="message-text">${content}</div>
                    <div class="message-time">${timestamp}</div>
                </div>
            `;
        } else {
            // AI response with proper formatting
            const formattedContent = content
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\n/g, '<br>')
                .replace(/• (.*?)(\n|$)/g, '<li>$1</li>')
                .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
            
            messageDiv.innerHTML = `
                <div class="message-content">
                    <div class="message-text response-text">${formattedContent}</div>
                    <div class="message-time">${timestamp}</div>
                </div>
            `;
        }
        
        if (isError) {
            messageDiv.classList.add('error');
        }
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Store in history
        this.chatHistory.push({
            content,
            sender,
            timestamp: new Date().toISOString(),
            isError
        });
    }

    formatMessage(content) {
        // Simple markdown-like formatting
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>')
            .replace(/• (.*?)(\n|$)/g, '<li>$1</li>')
            .replace(/<li>(.*?)<\/li>/g, '<ul><li>$1</li></ul>')
            .replace(/<\/ul><ul>/g, '');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    displayToolResults(toolOutput) {
        const toolResultsSection = document.getElementById('toolResults');
        const toolResultsContent = document.getElementById('toolResultsContent');
        
        let html = '';
        
        if (toolOutput.document_type) {
            // Document generator result
            html = `
                <div class="tool-result-card">
                    <h4><i class="fas fa-file-alt"></i> ${toolOutput.document_type}</h4>
                    <p><strong>Project:</strong> ${toolOutput.project_name}</p>
                    <p><strong>Status:</strong> <span class="badge success">${toolOutput.status}</span></p>
                    <p><strong>Sections:</strong></p>
                    <ul>
                        ${toolOutput.sections.map(section => `<li>${section}</li>`).join('')}
                    </ul>
                </div>
            `;
        } else if (toolOutput.risk_score !== undefined) {
            // Risk scoring result
            const riskLevel = toolOutput.risk_level.toLowerCase();
            const riskClass = riskLevel === 'high' ? 'danger' : riskLevel === 'medium' ? 'warning' : 'success';
            
            html = `
                <div class="tool-result-card">
                    <h4><i class="fas fa-exclamation-triangle"></i> Risk Assessment</h4>
                    <p><strong>Risk Score:</strong> <span class="badge ${riskClass}">${toolOutput.risk_score}</span></p>
                    <p><strong>Risk Level:</strong> <span class="badge ${riskClass}">${toolOutput.risk_level}</span></p>
                    <div class="risk-indicator">
                        <div class="risk-bar" style="width: ${Math.min(toolOutput.risk_score * 4, 100)}%; background: ${riskLevel === 'high' ? '#ef4444' : riskLevel === 'medium' ? '#f59e0b' : '#10b981'}"></div>
                    </div>
                </div>
            `;
        } else if (toolOutput.estimated_duration_weeks) {
            // Timeline estimation result
            html = `
                <div class="tool-result-card">
                    <h4><i class="fas fa-calendar-alt"></i> Timeline Estimation</h4>
                    <p><strong>Estimated Duration:</strong> <span class="badge info">${toolOutput.estimated_duration_weeks} weeks</span></p>
                    <p><strong>Complexity:</strong> ${toolOutput.complexity}</p>
                    <p><strong>Team Size:</strong> ${toolOutput.team_size} members</p>
                </div>
            `;
        }
        
        toolResultsContent.innerHTML = html;
        toolResultsSection.style.display = 'block';
        
        // Scroll to tool results
        toolResultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    updateStats(data, responseTime) {
        this.stats.totalQueries++;
        this.stats.avgResponseTime = ((this.stats.avgResponseTime * (this.stats.totalQueries - 1)) + responseTime) / this.stats.totalQueries;
        
        if (data.confidence_score) {
            this.stats.avgConfidence = ((this.stats.avgConfidence * (this.stats.totalQueries - 1)) + data.confidence_score) / this.stats.totalQueries;
        }
        
        if (data.tool_output) {
            this.stats.toolsUsed++;
        }
        
        this.updateStatsDisplay();
        this.saveStats();
    }

    updateStatsDisplay() {
        document.getElementById('totalQueries').textContent = this.stats.totalQueries;
        document.getElementById('avgConfidence').textContent = Math.round(this.stats.avgConfidence) + '%';
        document.getElementById('toolsUsed').textContent = this.stats.toolsUsed;
        document.getElementById('avgResponseTime').textContent = (this.stats.avgResponseTime / 1000).toFixed(1) + 's';
    }

    updateCharCount() {
        const messageInput = document.getElementById('messageInput');
        const charCount = document.getElementById('charCount');
        charCount.textContent = messageInput.value.length;
    }

    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    toggleVoice() {
        this.voiceEnabled = !this.voiceEnabled;
        const voiceToggle = document.getElementById('voiceToggle');
        const voiceBtn = document.getElementById('voiceBtn');
        
        if (this.voiceEnabled) {
            voiceToggle.classList.add('active');
            voiceToggle.innerHTML = '<i class="fas fa-microphone-slash"></i>';
            this.showToast('Voice input enabled', 'success');
        } else {
            voiceToggle.classList.remove('active');
            voiceToggle.innerHTML = '<i class="fas fa-microphone"></i>';
            this.showToast('Voice input disabled', 'info');
        }
    }

    async startVoiceInput() {
        // Auto-enable voice if not already enabled
        if (!this.voiceEnabled) {
            this.toggleVoice();
        }

        // Check for speech recognition support
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            this.showToast('Speech recognition not supported in your browser. Please try Chrome or Edge.', 'error');
            return;
        }

        // Check for microphone permission
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            stream.getTracks().forEach(track => track.stop());
        } catch (error) {
            this.showToast('Microphone permission denied. Please allow microphone access.', 'error');
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';
        recognition.maxAlternatives = 1;

        const voiceBtn = document.getElementById('voiceBtn');
        const messageInput = document.getElementById('messageInput');
        
        voiceBtn.innerHTML = '<i class="fas fa-stop"></i>';
        voiceBtn.style.color = '#ef4444';
        voiceBtn.style.animation = 'pulse 1.5s infinite';

        recognition.onstart = () => {
            this.showToast('Listening... Speak now!', 'info');
        };

        recognition.onresult = (event) => {
            let finalTranscript = '';
            let interimTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript + ' ';
                } else {
                    interimTranscript += transcript;
                }
            }
            
            // Update input with final + interim results
            messageInput.value = (messageInput.value + finalTranscript).trim();
            this.updateCharCount();
            this.autoResizeTextarea(messageInput);
            
            // Show interim results in toast for better UX
            if (interimTranscript) {
                this.showToast(`Hearing: ${interimTranscript}`, 'info');
            }
            
            if (finalTranscript) {
                this.showToast('Voice input captured!', 'success');
            }
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            let errorMessage = 'Voice input failed';
            
            switch(event.error) {
                case 'no-speech':
                    errorMessage = 'No speech detected. Please try again.';
                    break;
                case 'audio-capture':
                    errorMessage = 'Microphone not accessible. Please check permissions.';
                    break;
                case 'not-allowed':
                    errorMessage = 'Microphone permission denied. Please allow microphone access.';
                    break;
                case 'network':
                    errorMessage = 'Network error. Please check your connection.';
                    break;
                case 'service-not-allowed':
                    errorMessage = 'Speech recognition service not allowed.';
                    break;
                default:
                    errorMessage = `Voice error: ${event.error}`;
            }
            
            this.showToast(errorMessage, 'error');
            this.resetVoiceButton();
        };

        recognition.onend = () => {
            this.resetVoiceButton();
            // Focus on input for potential editing
            messageInput.focus();
        };

        try {
            recognition.start();
        } catch (error) {
            console.error('Failed to start recognition:', error);
            this.showToast('Failed to start voice recognition. Please try again.', 'error');
            this.resetVoiceButton();
        }
    }

    resetVoiceButton() {
        const voiceBtn = document.getElementById('voiceBtn');
        voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        voiceBtn.style.color = '';
        voiceBtn.style.animation = '';
    }

    clearChat() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = `
                <div class="welcome-message">
                    <div class="ai-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="message-content">
                        <h3>Chat Cleared</h3>
                        <p>Start a new conversation with the AI Assistant!</p>
                    </div>
                </div>
            `;
            this.chatHistory = [];
            this.showToast('Chat history cleared', 'success');
        }
    }

    toggleExportMenu() {
        const menu = document.getElementById('exportMenu');
        menu.classList.toggle('show');
    }

    hideExportMenu() {
        const menu = document.getElementById('exportMenu');
        menu.classList.remove('show');
    }

    exportChat(format = 'json') {
        if (this.chatHistory.length === 0) {
            this.showToast('No chat history to export', 'warning');
            return;
        }

        try {
            if (format === 'pdf') {
                this.exportToPDF();
            } else {
                this.exportToJSON();
            }
        } catch (error) {
            console.error('Export error:', error);
            this.showToast('Export failed. Please try again.', 'error');
        }
        
        this.hideExportMenu();
    }

    exportToJSON() {
        const chatData = {
            exportDate: new Date().toISOString(),
            totalMessages: this.chatHistory.length,
            chatHistory: this.chatHistory
        };

        const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ai-assistant-chat-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showToast('Chat exported as JSON', 'success');
    }

    async exportToPDF() {
        this.showToast('Generating PDF...', 'info');

        try {
            // Load jsPDF library
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
            script.onload = () => {
                this.generatePDFContent();
            };
            script.onerror = () => {
                this.showToast('Failed to load PDF library', 'error');
            };
            document.head.appendChild(script);
        } catch (error) {
            console.error('PDF generation error:', error);
            this.showToast('PDF generation failed', 'error');
        }
    }

    generatePDFContent() {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();

        // Add title
        doc.setFontSize(20);
        doc.setTextColor(102, 126, 234);
        doc.text('AI IT Project Delivery Assistant', 105, 20);

        // Add metadata
        doc.setFontSize(12);
        doc.setTextColor(0, 0, 0);
        doc.text(`Export Date: ${new Date().toLocaleString()}`, 20, 35);
        doc.text(`Total Messages: ${this.chatHistory.length}`, 20, 45);

        // Add chat content
        let yPosition = 65;
        doc.setFontSize(10);
        
        this.chatHistory.forEach((message, index) => {
            if (yPosition > 270) {
                doc.addPage();
                yPosition = 20;
            }

            const sender = message.sender === 'user' ? 'You' : 'AI Assistant';
            const timestamp = new Date(message.timestamp).toLocaleString();
            
            doc.setFontSize(12);
            doc.setTextColor(102, 126, 234);
            doc.text(`${sender} - ${timestamp}`, 20, yPosition);
            
            doc.setFontSize(10);
            doc.setTextColor(0, 0, 0);
            
            const content = message.content.replace(/\*\*(.*?)\*\*/g, '$1'); // Remove markdown
            const lines = doc.splitTextToSize(content, 170, { fontSize: 10 });
            
            lines.forEach(line => {
                if (yPosition > 270) {
                    doc.addPage();
                    yPosition = 20;
                }
                doc.text(line, 20, yPosition);
                yPosition += 6;
            });
            
            yPosition += 10;
        });

        // Save PDF
        doc.save(`ai-assistant-chat-${new Date().toISOString().split('T')[0]}.pdf`);
        this.showToast('Chat exported as PDF', 'success');
    }

    openSettings() {
        document.getElementById('settingsModal').classList.add('active');
        // Load current settings
        document.getElementById('temperatureSlider').value = this.settings.temperature * 100;
        document.getElementById('temperatureValue').textContent = this.settings.temperature.toFixed(2);
        document.getElementById('maxTokens').value = this.settings.maxTokens;
        document.getElementById('themeSelect').value = this.settings.theme;
    }

    closeSettings() {
        document.getElementById('settingsModal').classList.remove('active');
    }

    saveSettings() {
        this.settings.temperature = document.getElementById('temperatureSlider').value / 100;
        this.settings.maxTokens = parseInt(document.getElementById('maxTokens').value);
        this.settings.theme = document.getElementById('themeSelect').value;
        
        localStorage.setItem('dashboard_settings', JSON.stringify(this.settings));
        this.closeSettings();
        this.showToast('Settings saved successfully', 'success');
    }

    showLoading() {
        document.getElementById('loadingOverlay').classList.add('active');
    }

    hideLoading() {
        document.getElementById('loadingOverlay').classList.remove('active');
    }

    showToast(message, type = 'info') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        
        // Add toast styles if not already present
        if (!document.querySelector('#toast-styles')) {
            const style = document.createElement('style');
            style.id = 'toast-styles';
            style.textContent = `
                .toast {
                    position: fixed;
                    bottom: 2rem;
                    right: 2rem;
                    background: white;
                    padding: 1rem 1.5rem;
                    border-radius: 0.5rem;
                    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                    z-index: 4000;
                    animation: slideInRight 0.3s ease;
                    max-width: 400px;
                }
                .toast-success { border-left: 4px solid #10b981; color: #10b981; }
                .toast-error { border-left: 4px solid #ef4444; color: #ef4444; }
                .toast-warning { border-left: 4px solid #f59e0b; color: #f59e0b; }
                .toast-info { border-left: 4px solid #3b82f6; color: #3b82f6; }
                @keyframes slideInRight {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(toast);
        
        // Remove toast after 3 seconds
        setTimeout(() => {
            toast.style.animation = 'slideInRight 0.3s ease reverse';
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }

    loadStats() {
        const savedStats = localStorage.getItem('dashboard_stats');
        if (savedStats) {
            this.stats = { ...this.stats, ...JSON.parse(savedStats) };
            this.updateStatsDisplay();
        }
        
        const savedSettings = localStorage.getItem('dashboard_settings');
        if (savedSettings) {
            this.settings = { ...this.settings, ...JSON.parse(savedSettings) };
        }
    }

    saveStats() {
        localStorage.setItem('dashboard_stats', JSON.stringify(this.stats));
    }

    startRealTimeUpdates() {
        // Simulate real-time updates (can be connected to actual backend)
        setInterval(() => {
            // Update system status
            const statusDot = document.querySelector('.status-dot');
            if (statusDot) {
                statusDot.className = 'status-dot online';
            }
        }, 30000); // Check every 30 seconds
    }

    logout() {
        if (confirm('Are you sure you want to logout?')) {
            localStorage.clear();
            window.location.href = 'login.html';
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CorporateDashboard();
});
