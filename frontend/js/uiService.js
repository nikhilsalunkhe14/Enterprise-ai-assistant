// UI Service for DOM manipulation and user interface management
class UIService {
    constructor() {
        this.elements = {};
        this.isInitialized = false;
        this.loadingStates = new Map();
        this.modals = new Map();
    }

    // Initialize DOM elements
    initializeElements() {
        this.elements = {
            // App containers
            app: document.getElementById('app'),
            sidebar: document.getElementById('sidebar'),
            mainContent: document.getElementById('mainContent'),
            
            // Authentication
            authModal: document.getElementById('authModal'),
            authForm: document.getElementById('authForm'),
            authTitle: document.getElementById('authTitle'),
            authSubtitle: document.getElementById('authSubtitle'),
            nameField: document.getElementById('nameField'),
            submitButton: document.getElementById('authSubmitBtn'),
            submitButtonText: document.getElementById('submitButtonText'),
            authToggleText: document.getElementById('authToggleText'),
            errorAlert: document.getElementById('errorAlert'),
            errorMessage: document.getElementById('errorMessage'),
            successAlert: document.getElementById('successAlert'),
            successMessage: document.getElementById('successMessage'),
            
            // Sidebar elements
            newChatBtn: document.getElementById('newChatBtn'),
            conversationList: document.getElementById('conversationList'),
            searchBox: document.getElementById('searchBox'),
            settingsBtn: document.getElementById('settingsBtn'),
            logoutBtn: document.getElementById('logoutBtn'),
            
            // Chat interface
            chatMessages: document.getElementById('chatMessages'),
            messageForm: document.getElementById('messageForm'),
            messageInput: document.getElementById('messageInput'),
            sendBtn: document.getElementById('sendBtn'),
            
            // Settings modal
            settingsModal: document.getElementById('settingsModal'),
            settingsCloseBtn: document.getElementById('settingsCloseBtn'),
            modelSelect: document.getElementById('modelSelect'),
            temperatureSlider: document.getElementById('temperatureSlider'),
            maxTokensInput: document.getElementById('maxTokensInput'),
            exportBtn: document.getElementById('exportBtn'),
            clearBtn: document.getElementById('clearBtn'),
            
            // User info
            userEmail: document.getElementById('userEmail'),
            userName: document.getElementById('userName'),
            
            // Loading states
            loadingSpinner: document.getElementById('loadingSpinner'),
            submitText: document.getElementById('submitText')
        };

        this.isInitialized = true;
        console.log('✅ UI Service initialized with', Object.keys(this.elements).length, 'elements');
    }

    // Get element by key
    getElement(key) {
        return this.elements[key];
    }

    // Show/hide element
    showElement(key, display = 'block') {
        const element = this.getElement(key);
        if (element) {
            element.style.display = display;
        }
    }

    hideElement(key) {
        const element = this.getElement(key);
        if (element) {
            element.style.display = 'none';
        }
    }

    // Toggle element visibility
    toggleElement(key) {
        const element = this.getElement(key);
        if (element) {
            const isHidden = element.style.display === 'none';
            element.style.display = isHidden ? 'block' : 'none';
        }
    }

    // Authentication modal methods
    showAuthModal(isLoginMode = true) {
        const modal = this.getElement('authModal');
        if (!modal) {
            console.error('Auth modal not found');
            return;
        }

        modal.style.display = 'flex';
        modal.style.zIndex = '9999';
        modal.style.position = 'fixed';
        
        this.toggleAuthMode(isLoginMode);
        console.log('✅ Auth modal shown');
    }

    hideAuthModal() {
        const modal = this.getElement('authModal');
        if (modal) {
            modal.style.display = 'none';
        }
        console.log('✅ Auth modal hidden');
    }

    toggleAuthMode(isLoginMode) {
        const title = this.getElement('authTitle');
        const subtitle = this.getElement('authSubtitle');
        const nameField = this.getElement('nameField');
        const submitText = this.getElement('submitButtonText');
        const toggleText = this.getElement('authToggleText');

        if (isLoginMode) {
            if (title) title.textContent = 'Sign In';
            if (subtitle) subtitle.textContent = 'Sign in to your account';
            if (nameField) nameField.classList.add('hidden');
            if (submitText) submitText.textContent = 'Sign In';
            if (toggleText) toggleText.textContent = "Don't have an account? Sign up";
        } else {
            if (title) title.textContent = 'Sign Up';
            if (subtitle) subtitle.textContent = 'Create your account';
            if (nameField) nameField.classList.remove('hidden');
            if (submitText) submitText.textContent = 'Sign Up';
            if (toggleText) toggleText.textContent = "Already have an account? Sign in";
        }
    }

    // Settings modal methods
    showSettings() {
        this.showElement('settingsModal', 'flex');
    }

    hideSettings() {
        this.hideElement('settingsModal');
    }

    // Sidebar methods
    toggleSidebar() {
        const sidebar = this.getElement('sidebar');
        if (sidebar) {
            sidebar.classList.toggle('collapsed');
        }
    }

    // Message methods
    addMessage(message) {
        const messagesContainer = this.getElement('chatMessages');
        if (!messagesContainer) return;

        const messageElement = this.createMessageElement(message);
        messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }

    createMessageElement(message) {
        const div = document.createElement('div');
        div.className = `message ${message.role}-message mb-4`;
        div.innerHTML = `
            <div class="flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}">
                <div class="max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.role === 'user' 
                        ? 'bg-blue-500 text-white' 
                        : 'bg-gray-200 text-gray-800'
                }">
                    <p class="text-sm">${message.content}</p>
                    <p class="text-xs ${message.role === 'user' ? 'text-blue-100' : 'text-gray-500'} mt-1">
                        ${new Date(message.timestamp).toLocaleTimeString()}
                    </p>
                </div>
            </div>
        `;
        return div;
    }

    clearMessages() {
        const messagesContainer = this.getElement('chatMessages');
        if (messagesContainer) {
            messagesContainer.innerHTML = '';
        }
    }

    scrollToBottom() {
        const messagesContainer = this.getElement('chatMessages');
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    // Conversation methods
    renderConversations(conversations) {
        const listContainer = this.getElement('conversationList');
        if (!listContainer) return;

        listContainer.innerHTML = '';
        
        conversations.forEach(conv => {
            const convElement = this.createConversationElement(conv);
            listContainer.appendChild(convElement);
        });
    }

    createConversationElement(conversation) {
        const div = document.createElement('div');
        div.className = 'conversation-item p-3 hover:bg-gray-700 cursor-pointer rounded';
        div.innerHTML = `
            <h3 class="text-sm font-medium text-white truncate">${conversation.title}</h3>
            <p class="text-xs text-gray-400">${new Date(conversation.updated_at).toLocaleDateString()}</p>
        `;
        
        div.addEventListener('click', () => {
            if (window.appController) {
                window.appController.selectConversation(conversation.id);
            }
        });
        
        return div;
    }

    // Loading states
    setLoading(elementKey, loading = true) {
        const element = this.getElement(elementKey);
        if (!element) return;

        if (loading) {
            this.loadingStates.set(elementKey, element.disabled);
            element.disabled = true;
            
            if (elementKey === 'submitButton') {
                const originalText = element.textContent;
                element.innerHTML = `
                    <svg class="animate-spin h-5 w-5 mr-2 inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Processing...
                `;
            }
        } else {
            element.disabled = this.loadingStates.get(elementKey) || false;
            this.loadingStates.delete(elementKey);
            
            if (elementKey === 'submitButton') {
                element.textContent = 'Sign In';
            }
        }
    }

    // Error and success messages
    showError(message) {
        const errorAlert = this.getElement('errorAlert');
        const errorMessage = this.getElement('errorMessage');
        
        if (errorAlert && errorMessage) {
            errorMessage.textContent = message;
            errorAlert.classList.remove('hidden');
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                errorAlert.classList.add('hidden');
            }, 5000);
        }
    }

    showSuccess(message) {
        const successAlert = this.getElement('successAlert');
        const successMessage = this.getElement('successMessage');
        
        if (successAlert && successMessage) {
            successMessage.textContent = message;
            successAlert.classList.remove('hidden');
            
            // Auto-hide after 3 seconds
            setTimeout(() => {
                successAlert.classList.add('hidden');
            }, 3000);
        }
    }

    clearMessages() {
        const errorAlert = this.getElement('errorAlert');
        const successAlert = this.getElement('successAlert');
        
        if (errorAlert) errorAlert.classList.add('hidden');
        if (successAlert) successAlert.classList.add('hidden');
    }

    // Form methods
    getFormData(formKey) {
        const form = this.getElement(formKey);
        if (!form) return {};

        const formData = new FormData(form);
        const data = {};
        
        formData.forEach((value, key) => {
            data[key] = value;
        });
        
        return data;
    }

    clearForm(formKey) {
        const form = this.getElement(formKey);
        if (form) {
            form.reset();
        }
    }

    // User display methods
    updateUserDisplay(user) {
        const userEmail = this.getElement('userEmail');
        const userName = this.getElement('userName');
        
        if (userEmail && user.email) {
            userEmail.textContent = user.email;
        }
        
        if (userName && user.name) {
            userName.textContent = user.name;
        }
    }

    // Welcome screen
    showWelcomeScreen() {
        const messagesContainer = this.getElement('chatMessages');
        if (messagesContainer) {
            messagesContainer.innerHTML = `
                <div class="flex-1 flex items-center justify-center text-gray-500">
                    <div class="text-center">
                        <div class="text-6xl mb-4">💬</div>
                        <h3 class="text-xl font-semibold mb-2">Welcome to Enterprise AI Assistant</h3>
                        <p class="text-gray-400">Click "New Chat" to start a conversation</p>
                    </div>
                </div>
            `;
        }
    }

    // Get selected model
    getSelectedModel() {
        const modelSelect = this.getElement('modelSelect');
        return modelSelect ? modelSelect.value : 'gpt-3.5-turbo';
    }

    // Add message to UI
    addMessageToUI(message) {
        const messagesContainer = this.getElement('chatMessages');
        if (!messagesContainer) return;

        // Check if message already exists to prevent duplicates
        const existingMessage = messagesContainer.querySelector(`[data-message-id="${message.id}"]`);
        if (existingMessage) {
            console.log('⚠️ Message already exists, skipping:', message.id);
            return;
        }

        // Remove welcome screen if it exists
        const welcomeScreen = messagesContainer.querySelector('.text-center');
        if (welcomeScreen) {
            welcomeScreen.remove();
        }

        const messageElement = this.createMessageElement(message);
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Create message element
    createMessageElement(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} mb-4`;
        messageDiv.setAttribute('data-message-id', message.id);
        
        const contentDiv = document.createElement('div');
        contentDiv.className = `max-w-xs lg:max-w-2xl px-4 py-2 rounded-lg ${
            message.role === 'user' 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-200 text-gray-800'
        }`;
        
        contentDiv.innerHTML = `
            <p class="text-sm whitespace-pre-wrap">${this.escapeHtml(message.content)}</p>
            ${message.model ? `<span class="text-xs opacity-70">${message.model}</span>` : ''}
            ${message.tokens ? `<span class="text-xs opacity-70 ml-2">${message.tokens} tokens</span>` : ''}
            ${message.confidence !== undefined ? `<span class="text-xs opacity-70 ml-2">🎯 ${message.confidence}% confidence</span>` : ''}
            ${message.context_chunks !== undefined ? `<span class="text-xs opacity-70 ml-2">📚 ${message.context_chunks} sources</span>` : ''}
        `;
        
        messageDiv.appendChild(contentDiv);
        return messageDiv;
    }

    // Update streaming message
    updateStreamingMessage(chunk) {
        let streamingMessage = document.getElementById('streaming-message');
        
        if (!streamingMessage) {
            streamingMessage = document.createElement('div');
            streamingMessage.id = 'streaming-message';
            streamingMessage.className = 'flex justify-start mb-4';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'max-w-xs lg:max-w-2xl px-4 py-2 rounded-lg bg-gray-200 text-gray-800';
            contentDiv.innerHTML = '<p class="text-sm whitespace-pre-wrap" id="streaming-content"></p>';
            
            streamingMessage.appendChild(contentDiv);
            
            const messagesContainer = this.getElement('chatMessages');
            if (messagesContainer) {
                messagesContainer.appendChild(streamingMessage);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        }
        
        const contentElement = document.getElementById('streaming-content');
        if (contentElement) {
            contentElement.textContent += chunk;
        }
    }

    // Remove streaming message
    removeStreamingMessage() {
        const streamingMessage = document.getElementById('streaming-message');
        if (streamingMessage) {
            streamingMessage.remove();
        }
    }

    // Render conversations in sidebar
    renderConversations(conversations, currentConversationId) {
        const conversationList = this.getElement('conversationList');
        if (!conversationList) return;

        if (conversations.length === 0) {
            conversationList.innerHTML = `
                <div class="text-center text-gray-400 py-8">
                    <div class="text-4xl mb-2">💬</div>
                    <p class="text-sm">No conversations yet</p>
                    <p class="text-xs">Start a new chat to begin</p>
                </div>
            `;
            return;
        }

        conversationList.innerHTML = conversations.map(conv => `
            <div class="conversation-item group relative p-3 rounded-lg hover:bg-gray-800 cursor-pointer transition-colors ${
                conv.id === currentConversationId ? 'bg-gray-800' : ''
            }" data-conversation-id="${conv.id}">
                <div class="flex items-center justify-between">
                    <div class="flex-1 min-w-0">
                        <h3 class="text-sm font-medium text-gray-200 truncate">${conv.title || 'New Chat'}</h3>
                        <p class="text-xs text-gray-400 truncate">${this.formatDate(conv.updated_at || conv.created_at)}</p>
                        ${conv.message_count ? `<span class="text-xs text-gray-500">${conv.message_count} messages</span>` : ''}
                    </div>
                    <div class="conversation-dropdown opacity-0 group-hover:opacity-100 transition-opacity">
                        <button class="text-gray-400 hover:text-gray-200 p-1" onclick="window.appController.showConversationMenu('${conv.id}', event)">
                            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"></path>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // Show conversation dropdown menu
    showConversationDropdown(conversationId, event) {
        event.stopPropagation();
        
        // Remove existing dropdown
        const existingDropdown = document.getElementById('conversation-dropdown');
        if (existingDropdown) {
            existingDropdown.remove();
        }

        const dropdown = document.createElement('div');
        dropdown.id = 'conversation-dropdown';
        dropdown.className = 'absolute right-0 mt-1 w-48 bg-gray-800 rounded-lg shadow-lg border border-gray-700 z-50';
        dropdown.innerHTML = `
            <div class="py-1">
                <button class="w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 flex items-center" onclick="window.appController.renameConversation('${conversationId}')">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                    </svg>
                    Rename
                </button>
                <button class="w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 flex items-center" onclick="window.appController.exportConversation('${conversationId}')">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4 4m4-4v12"></path>
                    </svg>
                    Export
                </button>
                <button class="w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-gray-700 flex items-center" onclick="window.appController.deleteConversation('${conversationId}')">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                    Delete
                </button>
            </div>
        `;

        // Position dropdown
        const button = event.target.closest('button');
        const rect = button.getBoundingClientRect();
        dropdown.style.position = 'fixed';
        dropdown.style.right = (rect.right - 200) + 'px';
        dropdown.style.top = rect.bottom + 'px';

        document.body.appendChild(dropdown);

        // Close dropdown when clicking outside
        setTimeout(() => {
            document.addEventListener('click', () => {
                if (document.getElementById('conversation-dropdown')) {
                    document.getElementById('conversation-dropdown').remove();
                }
            }, { once: true });
        }, 100);
    }

    // Format date
    formatDate(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        return date.toLocaleDateString();
    }

    // Clear all messages
    clearMessages() {
        const messagesContainer = this.getElement('chatMessages');
        if (messagesContainer) {
            messagesContainer.innerHTML = '';
        }
    }

    // Escape HTML
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Debug method
    debug() {
        console.group('🔍 UI Service Debug');
        console.log('Initialized:', this.isInitialized);
        console.log('Elements:', Object.keys(this.elements));
        console.log('Loading states:', Array.from(this.loadingStates.keys()));
        console.groupEnd();
    }
}

// Create singleton instance
const uiService = new UIService();

// Export to global scope
window.uiService = uiService;
