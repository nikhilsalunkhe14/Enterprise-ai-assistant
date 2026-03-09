import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const ChatInterface = ({ token, logout }) => {
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [model, setModel] = useState('gpt-3.5-turbo');
  const [availableModels, setAvailableModels] = useState([]);
  const [streamingMessage, setStreamingMessage] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [websocket, setWebsocket] = useState(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingMessage]);

  // Initialize WebSocket connection
  useEffect(() => {
    if (token) {
      const ws = new WebSocket(`ws://localhost:8000/ws/chat?token=${token}`);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      };
      
      ws.onclose = () => {
        console.log('WebSocket disconnected');
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      setWebsocket(ws);
      
      return () => {
        ws.close();
      };
    }
  }, [token]);

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'message_saved':
        // User message saved
        break;
      case 'stream_start':
        setIsStreaming(true);
        setStreamingMessage('');
        break;
      case 'stream_chunk':
        setStreamingMessage(prev => prev + data.content);
        break;
      case 'stream_end':
        setIsStreaming(false);
        setStreamingMessage('');
        // Add the complete message to messages
        setMessages(prev => [...prev, data.message]);
        // Refresh conversations to get updated message counts
        fetchConversations();
        break;
      case 'error':
        setIsStreaming(false);
        setStreamingMessage('');
        const errorMessage = { 
          role: 'assistant', 
          content: `Error: ${data.message}` 
        };
        setMessages(prev => [...prev, errorMessage]);
        break;
      case 'conversation_updated':
        // Update conversation title in sidebar
        setConversations(prev => prev.map(conv => 
          conv.id === data.conversation_id 
            ? { ...conv, title: data.title }
            : conv
        ));
        break;
      default:
        break;
    }
  };

  // Fetch conversations on mount
  useEffect(() => {
    fetchConversations();
    fetchModels();
  }, []);

  // Fetch messages when conversation changes
  useEffect(() => {
    if (currentConversation) {
      fetchMessages(currentConversation.id);
    }
  }, [currentConversation]);

  const fetchConversations = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/conversations`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setConversations(response.data);
    } catch (error) {
      console.error('Error fetching conversations:', error);
    }
  };

  const fetchMessages = async (conversationId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/conversations/${conversationId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessages(response.data.messages || []);
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const fetchModels = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/chat/models`);
      setAvailableModels(response.data);
    } catch (error) {
      console.error('Error fetching models:', error);
    }
  };

  const createNewConversation = async () => {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/conversations`,
        { title: 'New Chat' },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const newConversation = response.data;
      setConversations([newConversation, ...conversations]);
      setCurrentConversation(newConversation);
      setMessages([]);
    } catch (error) {
      console.error('Error creating conversation:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !currentConversation || isLoading || isStreaming) return;

    const userMessage = { role: 'user', content: inputMessage };
    setMessages([...messages, userMessage]);
    const messageToSend = inputMessage;
    setInputMessage('');

    try {
      // Send message via WebSocket for streaming
      if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify({
          type: 'chat',
          conversation_id: currentConversation.id,
          message: messageToSend,
          model: model
        }));
      } else {
        // Fallback to HTTP if WebSocket is not available
        setIsLoading(true);
        const response = await axios.post(
          `${API_BASE_URL}/api/chat/chat`,
          {
            message: messageToSend,
            conversation_id: currentConversation.id,
            model: model
          },
          { headers: { Authorization: `Bearer ${token}` } }
        );

        const assistantMessage = { role: 'assistant', content: response.data.response };
        setMessages(prev => [...prev, assistantMessage]);

        // Update conversation title if it's the first message
        if (messages.length === 0) {
          const title = messageToSend.slice(0, 30) + (messageToSend.length > 30 ? '...' : '');
          await updateConversationTitle(currentConversation.id, title);
        }

        // Refresh conversations to get updated message counts
        fetchConversations();
        setIsLoading(false);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setIsLoading(false);
      const errorMessage = { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please try again.' 
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const deleteConversation = async (conversationId) => {
    if (!confirm('Are you sure you want to delete this conversation?')) return;

    try {
      await axios.delete(`${API_BASE_URL}/api/conversations/${conversationId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setConversations(conversations.filter(conv => conv.id !== conversationId));
      
      if (currentConversation?.id === conversationId) {
        setCurrentConversation(null);
        setMessages([]);
      }
    } catch (error) {
      console.error('Error deleting conversation:', error);
    }
  };

  const updateConversationTitle = async (conversationId, title) => {
    try {
      await axios.put(
        `${API_BASE_URL}/api/conversations/${conversationId}`,
        { title },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setConversations(conversations.map(conv => 
        conv.id === conversationId ? { ...conv, title } : conv
      ));
      
      if (currentConversation?.id === conversationId) {
        setCurrentConversation({ ...currentConversation, title });
      }
    } catch (error) {
      console.error('Error updating conversation title:', error);
    }
  };

  const formatMessage = (content) => {
    // Simple markdown-like formatting
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1 rounded">$1</code>')
      .replace(/\n/g, '<br />');
  };

  return (
    <div className="flex h-screen bg-white">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-0'} transition-all duration-300 bg-gray-50 border-r border-gray-200 flex flex-col`}>
        {/* Sidebar Header */}
        <div className="p-4 border-b border-gray-200">
          <button
            onClick={createNewConversation}
            className="w-full flex items-center justify-center px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Chat
          </button>
        </div>

        {/* Conversations List */}
        <div className="flex-1 overflow-y-auto p-4">
          {conversations.map((conversation) => (
            <div
              key={conversation.id}
              className={`mb-2 p-3 rounded-lg cursor-pointer transition-colors ${
                currentConversation?.id === conversation.id
                  ? 'bg-gray-200'
                  : 'hover:bg-gray-100'
              }`}
              onClick={() => setCurrentConversation(conversation)}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1 truncate">
                  <div className="font-medium text-sm text-gray-900 truncate">
                    {conversation.title}
                  </div>
                  <div className="text-xs text-gray-500">
                    {conversation.message_count || 0} messages
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteConversation(conversation.id);
                  }}
                  className="ml-2 p-1 text-gray-400 hover:text-red-500 transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">User</div>
            <button
              onClick={logout}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="mr-4 p-2 text-gray-500 hover:text-gray-700"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <h1 className="text-xl font-semibold text-gray-900">
                {currentConversation ? currentConversation.title : 'Enterprise AI Assistant'}
              </h1>
            </div>
            
            {/* Model Selector */}
            <div className="flex items-center">
              <label className="mr-2 text-sm text-gray-600">Model:</label>
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {availableModels.map((modelOption) => (
                  <option key={modelOption.id} value={modelOption.id}>
                    {modelOption.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {messages.length === 0 && !currentConversation ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">
                  Welcome to Enterprise AI Assistant
                </h2>
                <p className="text-gray-600 mb-8">
                  Start a new conversation or select an existing one from the sidebar
                </p>
                <button
                  onClick={createNewConversation}
                  className="px-6 py-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors"
                >
                  Start New Chat
                </button>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`mb-6 flex ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`max-w-3xl px-4 py-3 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-gray-900 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <div
                      className="prose prose-sm max-w-none"
                      dangerouslySetInnerHTML={{ __html: formatMessage(message.content) }}
                    />
                  </div>
                </div>
              ))}
              
              {/* Streaming message */}
              {isStreaming && streamingMessage && (
                <div className="flex justify-start mb-6">
                  <div className="bg-gray-100 text-gray-900 px-4 py-3 rounded-lg">
                    <div
                      className="prose prose-sm max-w-none"
                      dangerouslySetInnerHTML={{ __html: formatMessage(streamingMessage) }}
                    />
                    <div className="flex items-center space-x-1 mt-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                    </div>
                  </div>
                </div>
              )}
              
              {isLoading && !isStreaming && (
                <div className="flex justify-start mb-6">
                  <div className="bg-gray-100 text-gray-900 px-4 py-3 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <div className="animate-pulse flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                      </div>
                      <span className="text-sm text-gray-600">Thinking...</span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        {currentConversation && (
          <div className="border-t border-gray-200 px-6 py-4">
            <div className="flex items-end space-x-4">
              <div className="flex-1">
                <textarea
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      sendMessage();
                    }
                  }}
                  placeholder="Type your message..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={3}
                  disabled={isLoading || isStreaming}
                />
              </div>
              <button
                onClick={sendMessage}
                disabled={!inputMessage.trim() || isLoading || isStreaming}
                className="px-6 py-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading || isStreaming ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;
