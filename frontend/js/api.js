// API Service for ChatGPT Clone
class ApiService {
    constructor() {
        this.baseURL = 'http://localhost:8000';
        this.token = localStorage.getItem('token');
    }

    // Set authentication token
    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
        console.log('🔑 Token set in localStorage:', token ? token.substring(0, 20) + '...' : 'undefined');
    }

    // Clear authentication token
    clearToken() {
        this.token = null;
        localStorage.removeItem('token');
    }

    // Get headers with authentication
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        return headers;
    }

    // Generic request method
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: this.getHeaders(),
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (response.status === 401) {
                this.clearToken();
                window.location.href = 'login.html';
                return null;
            }

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Request failed');
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Authentication methods
    async register(userData) {
        return this.request('/api/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    async login(credentials) {
        const response = await this.request('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
        
        if (response && response.access_token) {
            this.setToken(response.access_token);
            console.log(' Token stored:', response.access_token ? response.access_token.substring(0, 20) + '...' : 'undefined');
        }
        
        return response;
    }

    async getCurrentUser() {
        return this.request('/api/auth/me');
    }

    // Conversation methods
    async getConversations() {
        return this.request('/api/conversations');
    }

    async createConversation(title = null) {
        return this.request('/api/conversations', {
            method: 'POST',
            body: JSON.stringify({ title })
        });
    }

    async updateConversation(conversationId, title) {
        return this.request(`/api/conversations/${conversationId}`, {
            method: 'PUT',
            body: JSON.stringify({ title })
        });
    }

    async deleteConversation(conversationId) {
        return this.request(`/api/conversations/${conversationId}`, {
            method: 'DELETE'
        });
    }

    async getConversation(conversationId) {
        return this.request(`/api/conversations/${conversationId}`);
    }

    async searchConversations(query) {
        return this.request(`/api/conversations/search?q=${encodeURIComponent(query)}`);
    }

    async pinConversation(conversationId) {
        return this.request(`/api/conversations/${conversationId}/pin`, {
            method: 'POST'
        });
    }

    async archiveConversation(conversationId) {
        return this.request(`/api/conversations/${conversationId}/archive`, {
            method: 'POST'
        });
    }

    async generateTitle(conversationId) {
        return this.request(`/api/conversations/${conversationId}/generate-title`, {
            method: 'POST'
        });
    }

    async getConversationMessages(conversationId) {
        return this.request(`/api/conversations/${conversationId}/messages`);
    }

    // Message methods
    async sendMessage(message, conversationId, model = 'grok-1') {
        return this.request('/api/chat/chat', {
            method: 'POST',
            body: JSON.stringify({
                message,
                conversation_id: conversationId,
                model
            })
        });
    }

    async updateMessage(messageId, updateData) {
        return this.request(`/api/messages/${messageId}`, {
            method: 'PUT',
            body: JSON.stringify(updateData)
        });
    }

    async regenerateMessage(messageId, model = 'grok-1') {
        return this.request(`/api/messages/${messageId}/regenerate`, {
            method: 'POST',
            body: JSON.stringify({ model })
        });
    }

    async deleteMessage(messageId) {
        return this.request(`/api/messages/${messageId}`, {
            method: 'DELETE'
        });
    }

    async getMessage(messageId) {
        return this.request(`/api/messages/${messageId}`);
    }

    // Conversation management
    async getConversation(conversationId) {
        return this.request(`/api/conversations/${conversationId}`);
    }

    async updateConversation(conversationId, updateData) {
        return this.request(`/api/conversations/${conversationId}`, {
            method: 'PUT',
            body: JSON.stringify(updateData)
        });
    }

    async deleteConversation(conversationId) {
        return this.request(`/api/conversations/${conversationId}`, {
            method: 'DELETE'
        });
    }

    async getConversationMessages(conversationId) {
        return this.request(`/api/conversations/${conversationId}/messages`);
    }

    // Export methods
    async exportAllConversations(format = 'json') {
        return this.request(`/api/conversations/export?format=${format}`);
    }

    async exportConversation(conversationId, format = 'json') {
        return this.request(`/api/conversations/${conversationId}/export?format=${format}`);
    }

    // Usage tracking methods
    async getUsageStats() {
        return this.request('/api/usage');
    }

    // Model methods
    async getModels() {
        return this.request('/api/chat/models');
    }

    // Health check
    async healthCheck() {
        return this.request('/health');
    }

    // WebSocket connection
    createWebSocket() {
        const token = this.token;
        if (!token) {
            console.error('No token available for WebSocket connection');
            return null;
        }
        
        const wsURL = `ws://localhost:8000/ws/chat?token=${token}`;
        console.log('Creating WebSocket connection to:', wsURL);
        return new WebSocket(wsURL);
    }
}

// Create singleton instance
const apiService = new ApiService();

// Export to global scope
window.apiService = apiService;
