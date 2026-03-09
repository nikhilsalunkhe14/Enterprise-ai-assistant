// WebSocket Service for Streaming Chat
class WebSocketService {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.messageCallbacks = [];
        this.connectionCallbacks = [];
    }

    // Create WebSocket connection
    connect() {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                console.error('No authentication token available');
                return;
            }
            
            const wsURL = `ws://localhost:8000/ws/chat?token=${token}`;
            console.log('Connecting to WebSocket:', wsURL);
            
            this.ws = new WebSocket(wsURL);
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.notifyConnectionCallbacks(true);
            };

            this.ws.onmessage = async (event) => {
                try {
                    // Handle different message formats
                    let data;
                    if (typeof event.data === 'string') {
                        try {
                            data = JSON.parse(event.data);
                        } catch (e) {
                            console.error('Failed to parse WebSocket message:', event.data);
                            return;
                        }
                    } else if (event.data instanceof Blob) {
                        // Handle Blob data
                        const text = await event.data.text();
                        data = JSON.parse(text);
                    } else {
                        data = event.data;
                    }
                    
                    console.log('🔍 WebSocket message received:', data);
                    
                    // Handle different message types
                    if (data.type === 'stream_start') {
                        console.log('📝 AI response starting...');
                    } else if (data.type === 'stream_chunk') {
                        // Stream chunk - update UI with partial response
                        if (data.content && window.appController && window.appController.handleStreamChunk) {
                            window.appController.handleStreamChunk(data);
                        }
                    } else if (data.type === 'stream_end') {
                        // Stream complete - add final message
                        if (data.message && window.appController && window.appController.addAssistantMessage) {
                            window.appController.addAssistantMessage(data.message);
                        }
                    } else if (data.type === 'assistant') {
                        // Direct assistant message
                        if (window.appController && window.appController.addAssistantMessage) {
                            window.appController.addAssistantMessage(data);
                        }
                    } else if (data.type === 'error') {
                        console.error('🚨 WebSocket error:', data.message);
                        if (window.appController && window.appController.showError) {
                            window.appController.showError(data.message);
                        }
                    }
                    
                    this.notifyMessageCallbacks(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                    console.log('Raw message:', event.data);
                }
            };

            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.isConnected = false;
                this.notifyConnectionCallbacks(false);
                this.attemptReconnect();
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.isConnected = false;
            };

        } catch (error) {
            console.error('Failed to connect to WebSocket:', error);
        }
    }

    // Attempt to reconnect
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            console.error('Max reconnection attempts reached');
        }
    }

    // Disconnect WebSocket
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.isConnected = false;
    }

    // Send message through WebSocket
    sendMessage(data) {
        if (this.isConnected && this.ws) {
            this.ws.send(JSON.stringify(data));
            return true;
        } else {
            console.warn('WebSocket not connected, message not sent');
            return false;
        }
    }

    // Send chat message
    sendChatMessage(conversationId, message, model = 'grok-1') {
        return this.sendMessage({
            type: 'chat',
            conversation_id: conversationId,
            message: message,
            model: model
        });
    }

    // Set current conversation
    setConversation(conversationId) {
        return this.sendMessage({
            type: 'set_conversation',
            conversation_id: conversationId
        });
    }

    // Edit message
    editMessage(messageId, content) {
        return this.sendMessage({
            type: 'edit_message',
            message_id: messageId,
            content: content
        });
    }

    // Regenerate response
    regenerateResponse(messageId, conversationId, model = 'grok-1') {
        return this.sendMessage({
            type: 'regenerate_response',
            message_id: messageId,
            conversation_id: conversationId,
            model: model
        });
    }

    // Send ping
    ping() {
        return this.sendMessage({ type: 'ping' });
    }

    // Add message callback
    onMessage(callback) {
        this.messageCallbacks.push(callback);
    }

    // Remove message callback
    offMessage(callback) {
        const index = this.messageCallbacks.indexOf(callback);
        if (index > -1) {
            this.messageCallbacks.splice(index, 1);
        }
    }

    // Add connection callback
    onConnection(callback) {
        this.connectionCallbacks.push(callback);
    }

    // Remove connection callback
    offConnection(callback) {
        const index = this.connectionCallbacks.indexOf(callback);
        if (index > -1) {
            this.connectionCallbacks.splice(index, 1);
        }
    }

    // Notify message callbacks
    notifyMessageCallbacks(data) {
        this.messageCallbacks.forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error('Error in message callback:', error);
            }
        });
    }

    // Notify connection callbacks
    notifyConnectionCallbacks(connected) {
        this.connectionCallbacks.forEach(callback => {
            try {
                callback(connected);
            } catch (error) {
                console.error('Error in connection callback:', error);
            }
        });
    }

    // Get connection status
    isWebSocketConnected() {
        return this.isConnected;
    }

    // Reset connection
    reset() {
        this.disconnect();
        this.reconnectAttempts = 0;
        this.connect();
    }
}

// Export singleton instance
const webSocketService = new WebSocketService();

// Export to global scope
window.webSocketService = webSocketService;
