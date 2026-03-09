import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import axios from 'axios';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
axios.defaults.baseURL = API_BASE_URL;

// Auth Context
const AuthContext = React.createContext();

// Chat Context
const ChatContext = React.createContext();

// Custom hooks
export const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const useChat = () => {
  const context = React.useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

// Auth Provider
export const AuthProvider = ({ children }) => {
  const [user, setUser] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [token, setToken] = React.useState(localStorage.getItem('token'));

  React.useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      axios.get('/api/auth/me')
      .then(response => {
        setUser(response.data);
        setLoading(false);
      })
      .catch(() => {
        localStorage.removeItem('token');
        delete axios.defaults.headers.common['Authorization'];
        setToken(null);
        setLoading(false);
      });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    try {
      const response = await axios.post('/api/auth/login', { email, password });
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      setToken(access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      const userResponse = await axios.get('/api/auth/me');
      setUser(userResponse.data);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Login failed' };
    }
  };

  const register = async (userData) => {
    try {
      await axios.post('/api/auth/register', userData);
      await login(userData.email, userData.password);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Registration failed' };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setToken(null);
    setUser(null);
  };

  return React.createElement(
    AuthContext.Provider,
    { value: { user, token, login, register, logout, loading } },
    children
  );
};

// Chat Provider
export const ChatProvider = ({ children }) => {
  const [conversations, setConversations] = React.useState([]);
  const [currentConversation, setCurrentConversation] = React.useState(null);
  const [messages, setMessages] = React.useState([]);
  const [availableModels, setAvailableModels] = React.useState([]);
  const [selectedModel, setSelectedModel] = React.useState('llama-3-8b');
  const [isLoading, setIsLoading] = React.useState(false);
  const [isTyping, setIsTyping] = React.useState(false);
  const messagesEndRef = React.useRef(null);

  React.useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await axios.get('/api/chat/models');
        setAvailableModels(response.data);
        // Set default model to first model's id
        if (response.data.length > 0) {
          setSelectedModel(response.data[0].id);
        }
      } catch (error) {
        console.error('Failed to fetch models:', error);
      }
    };
    fetchModels();
  }, []);

  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchConversations = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get('/api/conversations');
      setConversations(response.data);
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const createConversation = async (title) => {
    try {
      const response = await axios.post('/api/conversations', { title });
      const newConversation = response.data;
      setConversations(prev => [newConversation, ...prev]);
      return newConversation;
    } catch (error) {
      console.error('Failed to create conversation:', error);
      return null;
    }
  };

  const fetchMessages = async (conversationId) => {
    try {
      setIsLoading(true);
      const response = await axios.get(`/api/conversations/${conversationId}`);
      setCurrentConversation(response.data);
      setMessages(response.data.messages || []);
    } catch (error) {
      console.error('Failed to fetch messages:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async (content) => {
    if (!content.trim() || !currentConversation || isTyping) return;

    console.log('🚀 sendMessage called with:', content);
    setIsTyping(true);
    
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: content,
      created_at: new Date().toISOString()
    };
    console.log('📤 Adding user message:', userMessage);
    setMessages(prev => {
      console.log('📋 Current messages before adding:', prev);
      const newMessages = [...prev, userMessage];
      console.log('📋 Current messages after adding:', newMessages);
      return newMessages;
    });

    try {
      console.log('🌐 Sending to backend...');
      const response = await axios.post('/api/chat/chat', {
        message: content,
        conversation_id: currentConversation.id,
        model: selectedModel
      });
      console.log('✅ Backend response:', response.data);

      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.data.response,
        created_at: new Date().toISOString()
      };
      console.log('🤖 Adding AI message:', aiMessage);
      setMessages(prev => {
        console.log('📋 Messages before AI:', prev);
        const newMessages = [...prev, aiMessage];
        console.log('📋 Messages after AI:', newMessages);
        return newMessages;
      });

      setConversations(prev => prev.map(conv => 
        conv.id === currentConversation.id 
          ? { ...conv, message_count: (conv.message_count || 0) + 2 }
          : conv
      ));

    } catch (error) {
      console.error('❌ Failed to send message:', error);
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsTyping(false);
    }
  };

  const deleteConversation = async (conversationId) => {
    try {
      await axios.delete(`/api/conversations/${conversationId}`);
      setConversations(prev => prev.filter(conv => conv.id !== conversationId));
      
      if (currentConversation?.id === conversationId) {
        setCurrentConversation(null);
        setMessages([]);
      }
      return true;
    } catch (error) {
      console.error('Failed to delete conversation:', error);
      return false;
    }
  };

  return React.createElement(
    ChatContext.Provider,
    { 
      value: {
        conversations,
        currentConversation,
        messages,
        availableModels,
        selectedModel,
        isLoading,
        isTyping,
        fetchConversations,
        createConversation,
        fetchMessages,
        sendMessage,
        deleteConversation,
        setSelectedModel,
        setCurrentConversation,
        setMessages,
        messagesEndRef
      }
    },
    children
  );
};

// Protected Route
export const ProtectedRoute = ({ children }) => {
  const { token, loading } = useAuth();

  if (loading) {
    return React.createElement('div', {
      style: { minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f9fafb' }
    }, [
      React.createElement('div', { style: { display: 'flex', flexDirection: 'column', alignItems: 'center', spaceY: 4 } }, [
        React.createElement('div', { 
          style: { width: 12, height: 12, border: '2px solid #3b82f6', borderTop: '2px solid transparent', borderRight: '2px solid transparent', animation: 'spin 1s linear infinite' }
        }),
        React.createElement('p', { style: { color: '#6b7280' } }, 'Loading Enterprise AI Assistant...')
      ])
    ]);
  }

  if (!token) {
    return React.createElement('div', {
      style: { minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f9fafb' }
    }, [
      React.createElement('h1', { style: { fontSize: 24, color: '#1f2937', marginBottom: 16 } }, 'Authentication Required'),
      React.createElement('p', { style: { fontSize: 16, color: '#6b7280' } }, 'Please login to access the Enterprise AI Assistant.')
    ]);
  }

  return children;
};

// Login Component
export const Login = () => {
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState('');
  const [isRegister, setIsRegister] = React.useState(false);
  const [name, setName] = React.useState('');

  const { login, register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isRegister) {
        const result = await register({ email, password, name });
        if (!result.success) {
          setError(result.error);
        }
      } else {
        const result = await login(email, password);
        if (!result.success) {
          setError(result.error);
        }
      }
    } catch (err) {
      setError('An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  return React.createElement('div', {
    style: { minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }
  }, [
    React.createElement('div', { style: { maxWidth: 400, width: '100%', spaceY: 32, padding: 32 } }, [
      React.createElement('div', { style: { textAlign: 'center' } }, [
        React.createElement('h1', { style: { fontSize: 32, fontWeight: 'bold', color: '#1f2937', marginBottom: 8 } }, 'Enterprise AI Assistant'),
        React.createElement('p', { style: { fontSize: 16, color: '#6b7280' } }, 'Powered by Advanced AI Models')
      ]),
      
      React.createElement('div', { style: { backgroundColor: 'white', padding: 32, borderRadius: 12, boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)' } }, [
        React.createElement('h2', { style: { fontSize: 24, fontWeight: 'bold', textAlign: 'center', color: '#1f2937', marginBottom: 24 } }, 
          isRegister ? 'Create Account' : 'Sign In'
        ),
        
        React.createElement('form', { onSubmit: handleSubmit, style: { spaceY: 20 } }, [
          error && React.createElement('div', {
            style: { backgroundColor: '#fef2f2', border: '1px solid #fecaca', color: '#dc2626', padding: 12, borderRadius: 8, marginBottom: 16 }
          }, error),

          isRegister && React.createElement('div', { style: { marginBottom: 16 } }, [
            React.createElement('label', { style: { display: 'block', fontSize: 14, fontWeight: 500, color: '#374151', marginBottom: 8 } }, 'Full Name'),
            React.createElement('input', {
              type: 'text',
              required: true,
              style: { width: '100%', padding: 12, border: '1px solid #d1d5db', borderRadius: 8, fontSize: 14 },
              value: name,
              onChange: (e) => setName(e.target.value),
              placeholder: 'Enter your full name'
            })
          ]),

          React.createElement('div', { style: { marginBottom: 16 } }, [
            React.createElement('label', { style: { display: 'block', fontSize: 14, fontWeight: 500, color: '#374151', marginBottom: 8 } }, 'Email Address'),
            React.createElement('input', {
              type: 'email',
              required: true,
              style: { width: '100%', padding: 12, border: '1px solid #d1d5db', borderRadius: 8, fontSize: 14 },
              value: email,
              onChange: (e) => setEmail(e.target.value),
              placeholder: 'Enter your email'
            })
          ]),

          React.createElement('div', { style: { marginBottom: 16 } }, [
            React.createElement('label', { style: { display: 'block', fontSize: 14, fontWeight: 500, color: '#374151', marginBottom: 8 } }, 'Password'),
            React.createElement('input', {
              type: 'password',
              required: true,
              style: { width: '100%', padding: 12, border: '1px solid #d1d5db', borderRadius: 8, fontSize: 14 },
              value: password,
              onChange: (e) => setPassword(e.target.value),
              placeholder: 'Enter your password'
            })
          ]),

          React.createElement('button', {
            type: 'submit',
            disabled: loading,
            style: {
              width: '100%',
              padding: 12,
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: 8,
              fontSize: 14,
              fontWeight: 500,
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.5 : 1
            }
          }, loading ? 
            React.createElement('div', { style: { display: 'flex', alignItems: 'center', justifyContent: 'center' } }, [
              React.createElement('div', { 
                style: { width: 16, height: 16, border: '2px solid #ffffff', borderTop: '2px solid transparent', borderRight: '2px solid transparent', animation: 'spin 1s linear infinite' }
              }),
              React.createElement('span', { style: { marginLeft: 8 } }, 'Processing...')
            ])
          : React.createElement('span', null, isRegister ? 'Create Account' : 'Sign In')
          ),

          React.createElement('div', { style: { textAlign: 'center' } }, [
            React.createElement('button', {
              type: 'button',
              onClick: () => setIsRegister(!isRegister),
              style: {
                backgroundColor: 'transparent',
                color: '#3b82f6',
                border: 'none',
                fontSize: 14,
                fontWeight: 500,
                cursor: 'pointer'
              }
            }, isRegister ? 'Already have an account? Sign In' : "Don't have an account? Sign Up")
          ])
        ])
      ])
    ])
  ]);
};
