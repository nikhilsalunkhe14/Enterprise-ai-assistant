// Main Application Controller
class AppController {
    constructor() {
        console.log("🚀 Initializing Enterprise AI Assistant...");
        
        // State
        this.isInitialized = false;
        this.isLoginMode = true;
        this.currentConversation = null;
        this.currentUser = null;
        this.isAddingMessage = false; // Prevent duplicate rendering
        
        // Services (will be initialized in init())
        this.apiService = null;
        this.authService = null;
        this.uiService = null;
        this.stateManager = null;
        this.webSocketService = null;
        
        // Ensure singleton pattern
        if (window.appController) {
            console.warn("⚠️ AppController already exists, returning existing instance");
            return window.appController;
        }
        
        window.appController = this;
    }

    // Initialize application
    async init() {
        try {
            console.log("🔧 Setting up services...");
            
            // Initialize services
            this.setupServices();
            
            // Initialize UI elements
            this.uiService.initializeElements();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Setup state subscriptions
            this.setupStateSubscriptions();
            
            // Check authentication
            await this.checkAuthentication();
            
            this.isInitialized = true;
            this.stateManager.set('initialized', true);
            
            console.log('✅ Application initialized successfully');
        } catch (error) {
            console.error('❌ Failed to initialize application:', error);
            this.uiService.showError('Failed to initialize application');
        }
    }

    // Setup services
    setupServices() {
        // Get singleton services from window
        this.apiService = window.apiService;
        this.authService = window.authService;
        this.uiService = window.uiService;
        this.stateManager = window.stateManager;
        this.webSocketService = window.webSocketService;

        // Validate services
        const requiredServices = ['apiService', 'authService', 'uiService', 'stateManager'];
        const missingServices = requiredServices.filter(service => !this[service]);
        
        if (missingServices.length > 0) {
            throw new Error(`Missing required services: ${missingServices.join(', ')}`);
        }

        // Setup service dependencies
        this.authService.setApiService(this.apiService);
        
        console.log('✅ All services setup complete');
    }

    // Setup event listeners
    setupEventListeners() {
        // Authentication form
        const authForm = this.uiService.getElement('authForm');
        if (authForm) {
            authForm.addEventListener('submit', (e) => this.handleAuth(e));
        }

        // Message form
        const messageForm = this.uiService.getElement('messageForm');
        if (messageForm) {
            messageForm.addEventListener('submit', (e) => this.sendMessage(e));
        }

        // New chat button
        const newChatBtn = this.uiService.getElement('newChatBtn');
        if (newChatBtn) {
            newChatBtn.addEventListener('click', () => this.createNewConversation());
        }

        // Settings button
        const settingsBtn = this.uiService.getElement('settingsBtn');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => this.showSettings());
        }

        // Logout button
        const logoutBtn = this.uiService.getElement('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.logout());
        }

        // Settings close button
        const settingsCloseBtn = this.uiService.getElement('settingsCloseBtn');
        if (settingsCloseBtn) {
            settingsCloseBtn.addEventListener('click', () => this.hideSettings());
        }

        // Auth toggle button
        const authToggleBtn = this.uiService.getElement('authToggleBtn');
        if (authToggleBtn) {
            authToggleBtn.addEventListener('click', () => this.toggleAuthMode());
        }

        // Conversation list clicks
        const conversationList = this.uiService.getElement('conversationList');
        if (conversationList) {
            conversationList.addEventListener('click', (e) => {
                const conversationItem = e.target.closest('.conversation-item');
                if (conversationItem && !e.target.closest('.conversation-dropdown')) {
                    const conversationId = conversationItem.dataset.conversationId;
                    if (conversationId) {
                        this.loadConversation(conversationId);
                    }
                }
            });
        }

        // Model selector
        const modelSelect = this.uiService.getElement('modelSelect');
        if (modelSelect) {
            modelSelect.addEventListener('change', () => this.changeModel());
        }

        // Clear button
        const clearBtn = this.uiService.getElement('clearBtn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearAllConversations());
        }

        console.log('✅ Event listeners setup complete');
    }

    // Setup state subscriptions
    setupStateSubscriptions() {
        // Subscribe to conversations changes
        this.stateManager.subscribe('conversations', (conversations) => {
            console.log('📝 Conversations updated:', conversations.length);
            this.uiService.renderConversations(
                conversations,
                this.stateManager.get('currentConversationId')
            );
        });

        // Subscribe to current conversation changes
        this.stateManager.subscribe('currentConversationId', (conversationId) => {
            console.log('🔄 Current conversation changed:', conversationId);
            
            // Update WebSocket conversation
            if (this.webSocketService && this.webSocketService.isConnected) {
                this.webSocketService.setConversation(conversationId);
            }
            
            // Update conversation list UI
            const conversations = this.stateManager.get('conversations');
            this.uiService.renderConversations(conversations, conversationId);
        });

        // Subscribe to messages
        this.stateManager.subscribe('messages', (messages) => {
            console.log('💬 Messages updated:', messages.length);
            // Only re-render if we're not in the middle of adding a message
            if (!this.isAddingMessage) {
                this.uiService.clearMessages();
                messages.forEach(message => {
                    this.uiService.addMessageToUI(message);
                });
            }
        });

        // Subscribe to current user
        this.stateManager.subscribe('currentUser', (user) => {
            console.log('👤 Current user updated:', user?.email);
            this.currentUser = user;
            if (user) {
                this.updateUserInfo(user);
            }
        });

        console.log('✅ State subscriptions setup complete');
    }

    // Update user info in UI
    updateUserInfo(user) {
        const userEmail = this.uiService.getElement('userEmail');
        const userName = this.uiService.getElement('userName');
        const userInitial = this.uiService.getElement('userInitial');
        
        if (userEmail) userEmail.textContent = user.email;
        if (userName) userName.textContent = user.name || 'User';
        if (userInitial) userInitial.textContent = (user.name || 'U').charAt(0).toUpperCase();
    }

    // Check authentication
    async checkAuthentication() {
        const token = localStorage.getItem('token');
        
        if (token) {
            console.log('🔑 Token found, verifying...');
            try {
                // Verify token with backend
                const user = await this.apiService.getCurrentUser();
                if (user) {
                    console.log('✅ User authenticated:', user.email);
                    this.stateManager.set('currentUser', user);
                    
                    // Load conversations
                    await this.loadConversations();
                    
                    // Connect WebSocket
                    if (this.webSocketService) {
                        this.webSocketService.connect();
                    }
                    
                    // Show welcome screen if no conversations
                    const conversations = this.stateManager.get('conversations');
                    if (conversations.length === 0) {
                        // Auto-create first conversation for better UX
                        console.log('📝 No conversations found, creating first one...');
                        await this.createNewConversation();
                    } else {
                        this.uiService.showWelcomeScreen();
                    }
                } else {
                    console.log('❌ Invalid token');
                    this.showAuthModal();
                }
            } catch (error) {
                console.error('❌ Authentication failed:', error);
                this.showAuthModal();
            }
        } else {
            console.log('❌ No token found');
            this.showAuthModal();
        }
    }

    // Authentication methods
    showAuthModal(isLoginMode = true) {
        this.isLoginMode = isLoginMode;
        this.uiService.showAuthModal(isLoginMode);
    }

    hideAuthModal() {
        this.uiService.hideAuthModal();
    }

    toggleAuthMode() {
        this.isLoginMode = !this.isLoginMode;
        this.uiService.toggleAuthMode(this.isLoginMode);
    }

    async handleAuth(event) {
        event.preventDefault();
        
        const formData = this.uiService.getFormData('authForm');
        const { email, password, name } = formData;

        // Basic validation
        if (!email || !password) {
            this.uiService.showError('Please fill in all required fields');
            return;
        }

        if (!this.isLoginMode && !name) {
            this.uiService.showError('Please enter your full name');
            return;
        }

        if (password.length < 6) {
            this.uiService.showError('Password must be at least 6 characters long');
            return;
        }

        // Set loading state
        this.uiService.setLoading('submitButton', true);

        try {
            let response;
            if (this.isLoginMode) {
                console.log('🔑 Attempting login...');
                response = await this.authService.login({ email, password });
            } else {
                console.log('📝 Attempting registration...');
                response = await this.authService.register({ email, password, name });
            }

            if (response) {
                this.uiService.showSuccess(this.isLoginMode ? 'Login successful!' : 'Registration successful!');
                this.hideAuthModal();
                
                // Reload user data
                await this.checkAuthentication();
            }
        } catch (error) {
            console.error('❌ Authentication error:', error);
            this.uiService.showError(error.message || 'Authentication failed');
        } finally {
            this.uiService.setLoading('submitButton', false);
        }
    }

    // Logout
    logout() {
        if (!confirm('Are you sure you want to logout?')) {
            return;
        }

        console.log('🚪 Starting logout process...');
        
        // Disconnect WebSocket
        if (this.webSocketService) {
            this.webSocketService.disconnect();
        }

        // Clear auth token
        this.apiService.clearToken();
        
        // Reset state
        this.stateManager.reset();
        
        // Show login modal
        this.showAuthModal(true);
        
        console.log('🚪 Logged out successfully');
    }

    // Conversation methods
    async createNewConversation() {
        try {
            console.log('📝 Creating new conversation...');
            const conversation = await this.apiService.createConversation();
            
            if (conversation) {
                this.stateManager.addConversation(conversation);
                this.stateManager.setCurrentConversation(conversation.id);
                console.log('✅ New conversation created:', conversation.id);
                
                // Set conversation in WebSocket
                if (this.webSocketService && this.webSocketService.isConnected) {
                    this.webSocketService.setConversation(conversation.id);
                }
            }
        } catch (error) {
            console.error('❌ Failed to create conversation:', error);
            this.uiService.showError('Failed to create conversation');
        }
    }

    async loadConversations() {
        try {
            console.log('📂 Loading conversations...');
            const conversations = await this.apiService.getConversations();
            
            if (conversations) {
                this.stateManager.set('conversations', conversations);
                console.log(`✅ Loaded ${conversations.length} conversations`);
                
                // Render conversations in UI
                this.uiService.renderConversations(
                    conversations,
                    this.stateManager.get('currentConversationId')
                );
            }
        } catch (error) {
            console.error('❌ Failed to load conversations:', error);
            this.uiService.showError('Failed to load conversations');
        }
    }

    selectConversation(conversationId) {
        this.stateManager.setCurrentConversation(conversationId);
    }

    // Message methods
    async sendMessage(event) {
        if (event) {
            event.preventDefault();
        }

        const messageInput = this.uiService.getElement('messageInput');
        const message = messageInput?.value?.trim();
        
        if (!message) {
            return;
        }

        // Clear input
        if (messageInput) {
            messageInput.value = '';
        }

        // Add user message to state
        this.isAddingMessage = true; // Prevent re-rendering during user message addition
        
        const userMessage = {
            id: Date.now().toString(),
            role: 'user',
            content: message,
            timestamp: new Date().toISOString()
        };
        
        this.stateManager.addMessage(userMessage);
        this.uiService.addMessageToUI(userMessage); // Directly add to UI

        try {
            console.log('📤 Sending message...');
            
            // Check if we have a conversation, if not create one
            let currentConversationId = this.stateManager.get('currentConversationId');
            if (!currentConversationId) {
                console.log('📝 No conversation found, creating one before sending message...');
                const newConversation = await this.createNewConversation();
                currentConversationId = newConversation.id;
                this.stateManager.set('currentConversationId', currentConversationId);
                console.log('✅ Created conversation:', currentConversationId);
            }
            
            // Send via WebSocket if available, otherwise via HTTP
            if (this.webSocketService && this.webSocketService.isConnected) {
                this.webSocketService.sendChatMessage(
                    this.stateManager.get('currentConversationId'),
                    message
                );
            } else {
                // Fallback to HTTP API
                const response = await this.apiService.sendMessage({
                    conversation_id: this.stateManager.get('currentConversationId'),
                    message: message
                });
                
                if (response) {
                    // Add AI response to state
                    const aiMessage = {
                        id: response.id || Date.now().toString(),
                        role: 'assistant',
                        content: response.content,
                        timestamp: response.timestamp || new Date().toISOString()
                    };
                    
                    this.stateManager.addMessage(aiMessage);
                }
            }
        } catch (error) {
            console.error('❌ Failed to send message:', error);
            this.uiService.showError('Failed to send message');
        } finally {
            // Clear the flag after processing
            setTimeout(() => {
                this.isAddingMessage = false;
            }, 100);
        }
    }

    // Settings methods
    showSettings() {
        this.uiService.showSettings();
    }

    hideSettings() {
        this.uiService.hideSettings();
    }

    changeModel() {
        const model = this.uiService.getSelectedModel();
        this.stateManager.updateSettings({ model });
        console.log('Model changed to:', model);
    }

    async exportAllConversations() {
        if (!confirm('This will export all your conversations. Continue?')) {
            return;
        }

        try {
            // Get conversations data
            const data = await this.apiService.exportAllConversations('json');
            
            // Create download options
            const format = prompt('Choose export format:\n1. JSON\n2. Markdown\n3. TXT\n4. PDF (via browser print)\n\nEnter number (1-4):', '4');
            
            if (format === '4') {
                // PDF export via browser print
                this.printConversations(data);
            } else {
                // File download
                const exportFormat = format === '2' ? 'markdown' : format === '3' ? 'txt' : 'json';
                const exportData = await this.apiService.exportAllConversations(exportFormat);
                
                let filename, mimeType;
                if (exportFormat === 'json') {
                    filename = 'conversations.json';
                    mimeType = 'application/json';
                } else if (exportFormat === 'markdown') {
                    filename = 'conversations.md';
                    mimeType = 'text/markdown';
                } else {
                    filename = 'conversations.txt';
                    mimeType = 'text/plain';
                }
                
                const blob = new Blob([exportData], { type: mimeType });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                
                this.uiService.showSuccess(`Conversations exported as ${filename}`);
            }
        } catch (error) {
            console.error('❌ Failed to export conversations:', error);
            this.uiService.showError('Failed to export conversations: ' + error.message);
        }
    }

    printConversations(data) {
        // Create a new window for printing
        const printWindow = window.open('', '_blank');
        
        let html = `
            <!DOCTYPE html>
            <html>
            <head>
                <title>All Conversations Export</title>
                <style>
                    @page {
                        margin: 1in;
                        size: A4;
                    }
                    body { 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                        margin: 0; 
                        padding: 20px; 
                        line-height: 1.6;
                        color: #333;
                        background: white;
                    }
                    .header {
                        text-align: center;
                        border-bottom: 3px solid #2563eb;
                        padding-bottom: 20px;
                        margin-bottom: 30px;
                    }
                    h1 { 
                        color: #1e40af; 
                        margin: 0 0 10px 0;
                        font-size: 32px;
                        font-weight: 700;
                    }
                    .meta { 
                        color: #6b7280; 
                        font-size: 14px; 
                        margin-bottom: 10px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }
                    .meta-item {
                        display: flex;
                        align-items: center;
                        gap: 5px;
                    }
                    .summary-info {
                        background: #f8fafc;
                        padding: 20px;
                        border-radius: 8px;
                        margin-bottom: 30px;
                        border-left: 4px solid #2563eb;
                    }
                    .summary-info h3 {
                        margin: 0 0 15px 0;
                        color: #1e40af;
                        font-size: 18px;
                    }
                    .summary-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 15px;
                    }
                    .summary-item {
                        background: white;
                        padding: 15px;
                        border-radius: 6px;
                        border: 1px solid #e5e7eb;
                    }
                    .summary-item strong {
                        color: #1e40af;
                        display: block;
                        margin-bottom: 5px;
                    }
                    .conversation { 
                        margin: 30px 0; 
                        page-break-inside: avoid;
                    }
                    .conversation-header {
                        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                        padding: 20px;
                        border-radius: 12px;
                        border-left: 4px solid #2563eb;
                        margin-bottom: 20px;
                    }
                    .conversation-title {
                        color: #1e40af;
                        font-size: 20px;
                        font-weight: 600;
                        margin: 0 0 10px 0;
                    }
                    .conversation-meta {
                        color: #6b7280;
                        font-size: 13px;
                        display: flex;
                        gap: 20px;
                        flex-wrap: wrap;
                    }
                    .message { 
                        margin: 15px 0; 
                        padding: 15px; 
                        border-radius: 10px;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                        transition: all 0.2s ease;
                    }
                    .message:hover {
                        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
                    }
                    .user { 
                        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
                        border-left: 3px solid #0ea5e9;
                        margin-left: 25px;
                    }
                    .assistant { 
                        background: linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 100%);
                        border-left: 3px solid #9333ea;
                        margin-right: 25px;
                    }
                    .message-label { 
                        font-weight: 600; 
                        margin-bottom: 6px;
                        font-size: 13px;
                        display: flex;
                        align-items: center;
                        gap: 6px;
                    }
                    .message-content { 
                        line-height: 1.6;
                        font-size: 13px;
                        white-space: pre-wrap;
                        word-wrap: break-word;
                    }
                    .timestamp {
                        font-size: 11px;
                        color: #6b7280;
                        margin-top: 6px;
                        font-style: italic;
                    }
                    .footer {
                        margin-top: 50px;
                        padding-top: 20px;
                        border-top: 2px solid #e5e7eb;
                        text-align: center;
                        color: #6b7280;
                        font-size: 12px;
                    }
                    .toc {
                        background: #f8fafc;
                        padding: 20px;
                        border-radius: 8px;
                        margin-bottom: 30px;
                        border: 1px solid #e5e7eb;
                    }
                    .toc h3 {
                        margin: 0 0 15px 0;
                        color: #1e40af;
                        font-size: 16px;
                    }
                    .toc-list {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                        gap: 10px;
                        list-style: none;
                        padding: 0;
                        margin: 0;
                    }
                    .toc-list li {
                        padding: 8px 12px;
                        background: white;
                        border-radius: 6px;
                        border: 1px solid #e5e7eb;
                    }
                    .toc-list a {
                        color: #1e40af;
                        text-decoration: none;
                        font-size: 13px;
                    }
                    .toc-list a:hover {
                        text-decoration: underline;
                    }
                    .icon {
                        width: 14px;
                        height: 14px;
                        display: inline-block;
                    }
                    @media print { 
                        body { margin: 0.5in; }
                        .conversation { page-break-inside: avoid; }
                        .message { margin: 10px 0; }
                        .user { margin-left: 15px; }
                        .assistant { margin-right: 15px; }
                        .header { page-break-after: always; }
                        .toc { page-break-after: always; }
                    }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>📚 All Conversations</h1>
                    <div class="meta">
                        <div class="meta-item">
                            📅 Export Date: ${new Date().toLocaleDateString()}
                        </div>
                        <div class="meta-item">
                            🕐 Export Time: ${new Date().toLocaleTimeString()}
                        </div>
                    </div>
                </div>
                
                <div class="summary-info">
                    <h3>📊 Export Summary</h3>
                    <div class="summary-grid">
                        <div class="summary-item">
                            <strong>Total Conversations</strong>
                            ${data.conversations ? data.conversations.length : 0}
                        </div>
                        <div class="summary-item">
                            <strong>Total Messages</strong>
                            ${data.conversations ? data.conversations.reduce((sum, conv) => sum + (conv.messages ? conv.messages.length : 0), 0) : 0}
                        </div>
                        <div class="summary-item">
                            <strong>Date Range</strong>
                            ${data.conversations && data.conversations.length > 0 ? 
                                `${new Date(Math.min(...data.conversations.map(c => new Date(c.created_at)))).toLocaleDateString()} - ${new Date(Math.max(...data.conversations.map(c => new Date(c.created_at)))).toLocaleDateString()}` : 
                                'No conversations'
                            }
                        </div>
                        <div class="summary-item">
                            <strong>Generated By</strong>
                            Enterprise AI Assistant
                        </div>
                    </div>
                </div>
                
                <div class="toc">
                    <h3>📋 Table of Contents</h3>
                    <ul class="toc-list">
        `;
        
        if (data.conversations) {
            data.conversations.forEach((conv, index) => {
                html += `
                    <li>
                        <a href="#conversation-${index}">
                            ${conv.title || 'Untitled Conversation'} (${conv.messages ? conv.messages.length : 0} messages)
                        </a>
                    </li>
                `;
            });
        }
        
        html += `
                    </ul>
                </div>
        `;
        
        if (data.conversations) {
            data.conversations.forEach((conv, convIndex) => {
                const messages = conv.messages || [];
                html += `
                    <div class="conversation" id="conversation-${convIndex}">
                        <div class="conversation-header">
                            <h2 class="conversation-title">${conv.title || 'Untitled Conversation'}</h2>
                            <div class="conversation-meta">
                                <span>📅 Created: ${new Date(conv.created_at).toLocaleDateString()}</span>
                                <span>🔄 Updated: ${new Date(conv.updated_at).toLocaleDateString()}</span>
                                <span>💬 ${messages.length} messages</span>
                                <span>🆔 ID: ${conv.id}</span>
                            </div>
                        </div>
                `;
                
                messages.forEach((msg, msgIndex) => {
                    const className = msg.role === 'user' ? 'user' : 'assistant';
                    const label = msg.role === 'user' ? '👤 User' : '🤖 Assistant';
                    const timestamp = msg.created_at ? new Date(msg.created_at).toLocaleString() : 'No timestamp';
                    
                    html += `
                        <div class="message ${className}">
                            <div class="message-label">
                                <span class="icon">${msg.role === 'user' ? '👤' : '🤖'}</span>
                                <strong>${label}</strong>
                                <span style="margin-left: auto; font-size: 11px; color: #6b7280;">
                                    ${convIndex + 1}.${msgIndex + 1}
                                </span>
                            </div>
                            <div class="message-content">${this.escapeHtml(msg.content)}</div>
                            <div class="timestamp">🕐 ${timestamp}</div>
                        </div>
                    `;
                });
                
                html += `
                    </div>
                `;
            });
        }
        
        html += `
                <div class="footer">
                    <p><strong>Generated by Enterprise AI Assistant</strong></p>
                    <p>Export Date: ${new Date().toLocaleString()}</p>
                    <p>This document contains ${data.conversations ? data.conversations.length : 0} conversations with a total of ${data.conversations ? data.conversations.reduce((sum, conv) => sum + (conv.messages ? conv.messages.length : 0), 0) : 0} messages</p>
                </div>
            </body>
            </html>
        `;
        
        printWindow.document.write(html);
        printWindow.document.close();
        printWindow.focus();
        printWindow.print();
        printWindow.close();
        
        this.uiService.showSuccess('Print dialog opened - choose "Save as PDF" to export');
    }

    async clearAllConversations() {
        if (!confirm('Are you sure you want to delete all conversations? This action cannot be undone!')) {
            return;
        }

        try {
            // Delete all conversations from backend
            const conversations = this.stateManager.get('conversations');
            for (const conversation of conversations) {
                await this.apiService.deleteConversation(conversation.id);
            }
            
            // Reset state
            this.stateManager.reset();
            
            // Create new conversation
            await this.createNewConversation();
            
            this.uiService.showSuccess('All conversations cleared!');
        } catch (error) {
            console.error('❌ Failed to clear conversations:', error);
            this.uiService.showError('Failed to clear conversations');
        }
    }

    // Message handling methods
    handleStreamChunk(data) {
        // Handle streaming AI response chunks
        if (data.content) {
            // Update or create streaming message
            this.uiService.updateStreamingMessage(data.content);
        }
    }

    addAssistantMessage(message) {
        // Remove streaming message if exists
        this.uiService.removeStreamingMessage();
        
        // Set flag to prevent duplicate rendering
        this.isAddingMessage = true;
        
        // Handle enhanced response format
        let assistantMessage;
        if (message.confidence !== undefined || message.context_chunks !== undefined) {
            // Enhanced AI response with metadata
            assistantMessage = {
                id: message.id || Date.now().toString(),
                role: 'assistant',
                content: message.content,
                timestamp: message.created_at || new Date().toISOString(),
                tokens: message.tokens,
                confidence: message.confidence,
                context_chunks: message.context_chunks
            };
            
            // Display enhanced metadata in UI
            console.log(`🎯 Enhanced AI Response - Confidence: ${message.confidence}%, Context: ${message.context_chunks} chunks`);
        } else {
            // Standard response
            assistantMessage = {
                id: message.id || Date.now().toString(),
                role: 'assistant',
                content: message.content,
                timestamp: message.created_at || new Date().toISOString(),
                tokens: message.tokens
            };
        }
        
        this.stateManager.addMessage(assistantMessage);
        this.uiService.addMessageToUI(assistantMessage);
        console.log('✅ Assistant message added:', assistantMessage);
        
        // Clear flag after a short delay
        setTimeout(() => {
            this.isAddingMessage = false;
        }, 100);
    }

    // Conversation management methods
    showConversationMenu(conversationId, event) {
        this.uiService.showConversationDropdown(conversationId, event);
    }

    async renameConversation(conversationId) {
        const conversation = this.stateManager.get('conversations').find(c => c.id === conversationId);
        const currentTitle = conversation?.title || 'New Chat';
        
        const newTitle = prompt('Enter new title:', currentTitle);
        if (newTitle && newTitle !== currentTitle) {
            try {
                await this.apiService.updateConversation(conversationId, { title: newTitle });
                
                // Update local state
                const conversations = this.stateManager.get('conversations');
                const convIndex = conversations.findIndex(c => c.id === conversationId);
                if (convIndex !== -1) {
                    conversations[convIndex].title = newTitle;
                    this.stateManager.set('conversations', conversations);
                }
                
                this.uiService.showSuccess('Conversation renamed successfully!');
            } catch (error) {
                console.error('❌ Failed to rename conversation:', error);
                this.uiService.showError('Failed to rename conversation');
            }
        }
    }

    async exportConversation(conversationId) {
        try {
            // Ask user for format
            const format = prompt('Choose export format:\n1. JSON\n2. Markdown\n3. TXT\n4. PDF (via browser print)\n\nEnter number (1-4):', '1');
            
            if (format === '4') {
                // PDF export via browser print
                const exportData = await this.apiService.exportConversation(conversationId, 'json');
                this.printSingleConversation(exportData);
            } else {
                // File download
                const exportFormat = format === '2' ? 'markdown' : format === '3' ? 'txt' : 'json';
                const exportData = await this.apiService.exportConversation(conversationId, exportFormat);
                
                let filename, mimeType;
                if (exportFormat === 'json') {
                    filename = `conversation_${new Date().toISOString().split('T')[0]}.json`;
                    mimeType = 'application/json';
                } else if (exportFormat === 'markdown') {
                    filename = `conversation_${new Date().toISOString().split('T')[0]}.md`;
                    mimeType = 'text/markdown';
                } else {
                    filename = `conversation_${new Date().toISOString().split('T')[0]}.txt`;
                    mimeType = 'text/plain';
                }
                
                const blob = new Blob([exportData], { type: mimeType });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                a.click();
                URL.revokeObjectURL(url);
                
                this.uiService.showSuccess(`Conversation exported as ${filename}`);
            }
        } catch (error) {
            console.error('❌ Failed to export conversation:', error);
            this.uiService.showError('Failed to export conversation');
        }
    }

    printSingleConversation(data) {
        // Create a new window for printing
        const printWindow = window.open('', '_blank');
        
        const conv = data.conversation;
        const messages = data.messages || [];
        
        let html = `
            <!DOCTYPE html>
            <html>
            <head>
                <title>${conv.title} - Conversation Export</title>
                <style>
                    @page {
                        margin: 1in;
                        size: A4;
                    }
                    body { 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                        margin: 0; 
                        padding: 20px; 
                        line-height: 1.6;
                        color: #333;
                        background: white;
                    }
                    .header {
                        text-align: center;
                        border-bottom: 3px solid #2563eb;
                        padding-bottom: 20px;
                        margin-bottom: 30px;
                    }
                    h1 { 
                        color: #1e40af; 
                        margin: 0 0 10px 0;
                        font-size: 28px;
                        font-weight: 700;
                    }
                    .meta { 
                        color: #6b7280; 
                        font-size: 14px; 
                        margin-bottom: 10px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }
                    .meta-item {
                        display: flex;
                        align-items: center;
                        gap: 5px;
                    }
                    .conversation-info {
                        background: #f8fafc;
                        padding: 15px;
                        border-radius: 8px;
                        margin-bottom: 25px;
                        border-left: 4px solid #2563eb;
                    }
                    .conversation-info h3 {
                        margin: 0 0 10px 0;
                        color: #1e40af;
                        font-size: 16px;
                    }
                    .message { 
                        margin: 20px 0; 
                        padding: 15px; 
                        border-radius: 12px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        transition: all 0.3s ease;
                    }
                    .message:hover {
                        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                    }
                    .user { 
                        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
                        border-left: 4px solid #0ea5e9;
                        margin-left: 30px;
                    }
                    .assistant { 
                        background: linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 100%);
                        border-left: 4px solid #9333ea;
                        margin-right: 30px;
                    }
                    .message-label { 
                        font-weight: 600; 
                        margin-bottom: 8px;
                        font-size: 14px;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    }
                    .message-content { 
                        line-height: 1.7;
                        font-size: 14px;
                        white-space: pre-wrap;
                        word-wrap: break-word;
                    }
                    .timestamp {
                        font-size: 12px;
                        color: #6b7280;
                        margin-top: 8px;
                        font-style: italic;
                    }
                    .footer {
                        margin-top: 40px;
                        padding-top: 20px;
                        border-top: 1px solid #e5e7eb;
                        text-align: center;
                        color: #6b7280;
                        font-size: 12px;
                    }
                    .icon {
                        width: 16px;
                        height: 16px;
                        display: inline-block;
                    }
                    @media print { 
                        body { margin: 0.5in; }
                        .message { 
                            page-break-inside: avoid;
                            margin: 15px 0;
                        }
                        .user { margin-left: 20px; }
                        .assistant { margin-right: 20px; }
                        .header { page-break-after: always; }
                    }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>${conv.title}</h1>
                    <div class="meta">
                        <div class="meta-item">
                            📅 Created: ${new Date(conv.created_at).toLocaleDateString()}
                        </div>
                        <div class="meta-item">
                            🔄 Updated: ${new Date(conv.updated_at).toLocaleDateString()}
                        </div>
                    </div>
                </div>
                
                <div class="conversation-info">
                    <h3>📋 Conversation Details</h3>
                    <div><strong>Total Messages:</strong> ${messages.length}</div>
                    <div><strong>Conversation ID:</strong> ${conv.id}</div>
                    <div><strong>Export Date:</strong> ${new Date().toLocaleString()}</div>
                </div>
        `;
        
        messages.forEach((msg, index) => {
            const className = msg.role === 'user' ? 'user' : 'assistant';
            const label = msg.role === 'user' ? '👤 User' : '🤖 Assistant';
            const timestamp = msg.created_at ? new Date(msg.created_at).toLocaleString() : 'No timestamp';
            
            html += `
                <div class="message ${className}">
                    <div class="message-label">
                        <span class="icon">${msg.role === 'user' ? '👤' : '🤖'}</span>
                        <strong>${label}</strong>
                        <span style="margin-left: auto; font-size: 12px; color: #6b7280;">
                            Message ${index + 1}
                        </span>
                    </div>
                    <div class="message-content">${this.escapeHtml(msg.content)}</div>
                    <div class="timestamp">🕐 ${timestamp}</div>
                </div>
            `;
        });
        
        html += `
                <div class="footer">
                    <p>Generated by Enterprise AI Assistant | Export Date: ${new Date().toLocaleString()}</p>
                    <p>This document contains ${messages.length} messages from the conversation "${conv.title}"</p>
                </div>
            </body>
            </html>
        `;
        
        printWindow.document.write(html);
        printWindow.document.close();
        printWindow.focus();
        printWindow.print();
        printWindow.close();
        
        this.uiService.showSuccess('Print dialog opened - choose "Save as PDF" to export');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async deleteConversation(conversationId) {
        if (!confirm('Are you sure you want to delete this conversation? This action cannot be undone!')) {
            return;
        }

        try {
            await this.apiService.deleteConversation(conversationId);
            
            // Remove from local state
            const conversations = this.stateManager.get('conversations');
            const updatedConversations = conversations.filter(c => c.id !== conversationId);
            this.stateManager.set('conversations', updatedConversations);
            
            // If this was the current conversation, create a new one
            if (this.stateManager.get('currentConversationId') === conversationId) {
                await this.createNewConversation();
            }
            
            this.uiService.showSuccess('Conversation deleted successfully!');
        } catch (error) {
            console.error('❌ Failed to delete conversation:', error);
            this.uiService.showError('Failed to delete conversation');
        }
    }

    async loadConversation(conversationId) {
        try {
            // Set flag to prevent duplicate rendering
            this.isAddingMessage = true;
            
            // Set current conversation
            this.stateManager.setCurrentConversation(conversationId);
            
            // Load messages for this conversation
            const messages = await this.apiService.getConversationMessages(conversationId);
            this.stateManager.set('messages', messages);
            
            // Clear and render messages in UI (bypassing subscription)
            this.uiService.clearMessages();
            messages.forEach(message => {
                this.uiService.addMessageToUI(message);
            });
            
            // Set conversation in WebSocket
            if (this.webSocketService && this.webSocketService.isConnected) {
                this.webSocketService.setConversation(conversationId);
            }
            
            // Update conversation list UI
            this.uiService.renderConversations(
                this.stateManager.get('conversations'),
                conversationId
            );
            
            console.log('✅ Conversation loaded:', conversationId);
            
            // Clear flag after loading
            setTimeout(() => {
                this.isAddingMessage = false;
            }, 100);
        } catch (error) {
            console.error('❌ Failed to load conversation:', error);
            this.uiService.showError('Failed to load conversation');
        }
    }

    // Utility methods
    debug() {
        console.group('🔍 AppController Debug');
        console.log('Initialized:', this.isInitialized);
        console.log('Current User:', this.currentUser);
        console.log('Current Conversation:', this.currentConversation);
        console.log('Services:', {
            apiService: !!this.apiService,
            authService: !!this.authService,
            uiService: !!this.uiService,
            stateManager: !!this.stateManager,
            webSocketService: !!this.webSocketService
        });
        console.groupEnd();
    }
}

// Create singleton instance
// Export singleton instance (only if not already created)
let appController = null;
if (!window.appController) {
    appController = new AppController();
    window.appController = appController;
}

// Export global functions for HTML onclick handlers
window.showAuthModal = (isLoginMode = true) => appController.showAuthModal(isLoginMode);
window.hideAuthModal = () => appController.hideAuthModal();
window.toggleAuthMode = () => appController.toggleAuthMode();
window.handleAuth = (event) => appController.handleAuth(event);
window.logout = () => appController.logout();
window.createNewConversation = () => appController.createNewConversation();
window.sendMessage = (event) => appController.sendMessage(event);
window.showSettings = () => appController.showSettings();
window.hideSettings = () => appController.hideSettings();
window.changeModel = () => appController.changeModel();
window.clearAllConversations = () => appController.clearAllConversations();
window.renameConversation = (id) => appController.renameConversation(id);
window.exportConversation = (id) => appController.exportConversation(id);
window.deleteConversation = (id) => appController.deleteConversation(id);
window.showConversationMenu = (id, event) => appController.showConversationMenu(id, event);
