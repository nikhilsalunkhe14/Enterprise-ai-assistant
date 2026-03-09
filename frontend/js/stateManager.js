// State Manager Service
class StateManager {
    constructor() {
        this.state = {
            currentUser: null,
            conversations: [],
            currentConversationId: null,
            messages: [],
            sidebarOpen: true,
            settings: {
                model: 'gpt-3.5-turbo',
                temperature: 0.7,
                maxTokens: 2000
            },
            initialized: false
        };
        this.subscribers = new Map();
        this.history = [];
        this.maxHistorySize = 50;
    }

    // Get state value
    get(key) {
        return this.state[key];
    }

    // Set state value
    set(key, value) {
        const oldValue = this.state[key];
        this.state[key] = value;
        
        // Add to history
        this.history.push({
            key,
            oldValue,
            newValue: value,
            timestamp: Date.now()
        });
        
        // Trim history
        if (this.history.length > this.maxHistorySize) {
            this.history = this.history.slice(-this.maxHistorySize);
        }
        
        // Notify subscribers
        this.notifySubscribers(key, value, oldValue);
        
        console.log(`🔄 State updated: ${key} =`, value);
    }

    // Update multiple values
    updateState(updates) {
        Object.entries(updates).forEach(([key, value]) => {
            this.set(key, value);
        });
    }

    // Subscribe to state changes
    subscribe(key, callback) {
        if (!this.subscribers.has(key)) {
            this.subscribers.set(key, new Set());
        }
        this.subscribers.get(key).add(callback);
        
        // Return unsubscribe function
        return () => {
            const callbacks = this.subscribers.get(key);
            if (callbacks) {
                callbacks.delete(callback);
                if (callbacks.size === 0) {
                    this.subscribers.delete(key);
                }
            }
        };
    }

    // Notify all subscribers of a key
    notifySubscribers(key, newValue, oldValue) {
        const callbacks = this.subscribers.get(key);
        if (callbacks) {
            callbacks.forEach(callback => {
                try {
                    callback(newValue, oldValue, key);
                } catch (error) {
                    console.error('Error in state subscriber:', error);
                }
            });
        }
    }

    // Toggle sidebar
    toggleSidebar() {
        this.set('sidebarOpen', !this.state.sidebarOpen);
    }

    // Update settings
    updateSettings(settings) {
        this.set('settings', { ...this.state.settings, ...settings });
    }

    // Set current conversation
    setCurrentConversation(conversationId) {
        this.set('currentConversationId', conversationId);
    }

    // Add conversation
    addConversation(conversation) {
        const conversations = [conversation, ...this.state.conversations];
        this.set('conversations', conversations);
    }

    // Update conversation
    updateConversation(conversationId, updates) {
        const conversations = this.state.conversations.map(conv => 
            conv.id === conversationId ? { ...conv, ...updates } : conv
        );
        this.set('conversations', conversations);
    }

    // Delete conversation
    deleteConversation(conversationId) {
        const conversations = this.state.conversations.filter(conv => conv.id !== conversationId);
        this.set('conversations', conversations);
        
        // Clear current conversation if it was deleted
        if (this.state.currentConversationId === conversationId) {
            this.set('currentConversationId', null);
            this.set('messages', []);
        }
    }

    // Add message
    addMessage(message) {
        const messages = [...this.state.messages, message];
        this.set('messages', messages);
    }

    // Update message
    updateMessage(messageId, updates) {
        const messages = this.state.messages.map(msg => 
            msg.id === messageId ? { ...msg, ...updates } : msg
        );
        this.set('messages', messages);
    }

    // Clear messages
    clearMessages() {
        this.set('messages', []);
    }

    // Reset all state
    reset() {
        const oldState = { ...this.state };
        this.state = {
            currentUser: null,
            conversations: [],
            currentConversationId: null,
            messages: [],
            sidebarOpen: true,
            settings: {
                model: 'gpt-3.5-turbo',
                temperature: 0.7,
                maxTokens: 2000
            },
            initialized: false
        };
        
        // Notify all subscribers
        Object.keys(oldState).forEach(key => {
            this.notifySubscribers(key, this.state[key], oldState[key]);
        });
        
        console.log('🔄 State reset to initial values');
    }

    // Get state snapshot
    getSnapshot() {
        return { ...this.state };
    }

    // Get state history
    getHistory(key = null) {
        if (key) {
            return this.history.filter(entry => entry.key === key);
        }
        return [...this.history];
    }

    // Debug method to print current state
    debug() {
        console.group('🔍 State Manager Debug');
        console.log('Current State:', this.state);
        console.log('Subscribers:', Object.fromEntries(this.subscribers));
        console.log('History:', this.history.slice(-10));
        console.groupEnd();
    }
}

// Create singleton instance
const stateManager = new StateManager();

// Export to global scope
window.stateManager = stateManager;
