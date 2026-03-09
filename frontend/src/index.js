import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider, ChatProvider, ProtectedRoute, Login, useChat } from './components-complete.js';

// Simple Sidebar Component
const Sidebar = () => {
  const { conversations, createConversation, setCurrentConversation, fetchConversations } = useChat();
  const [loading, setLoading] = React.useState(false);

  React.useEffect(() => {
    fetchConversations();
  }, []);

  const handleNewConversation = async () => {
    console.log('Creating new conversation...');
    setLoading(true);
    try {
      const newConv = await createConversation('New Conversation');
      console.log('New conversation created:', newConv);
      if (newConv) {
        setCurrentConversation(newConv);
        console.log('Conversation set as current');
      }
    } catch (error) {
      console.error('Failed to create conversation:', error);
    } finally {
      setLoading(false);
    }
  };

  return React.createElement('div', {
    style: { 
      width: 280, 
      backgroundColor: '#1f2937', 
      color: 'white', 
      padding: 20,
      height: '100vh',
      borderRight: '1px solid #374151'
    }
  }, [
    React.createElement('h2', { style: { fontSize: 18, fontWeight: 'bold', marginBottom: 20 } }, '💬 Conversations'),
    React.createElement('button', {
      onClick: handleNewConversation,
      disabled: loading,
      style: {
        width: '100%',
        padding: 12,
        backgroundColor: loading ? '#6b7280' : '#3b82f6',
        color: 'white',
        border: 'none',
        borderRadius: 8,
        cursor: loading ? 'not-allowed' : 'pointer',
        fontSize: 14,
        marginBottom: 20
      }
    }, loading ? 'Creating...' : '+ New Conversation'),
    React.createElement('div', { style: { marginTop: 20 } }, 
      conversations.length > 0 ? conversations.map(conv => 
        React.createElement('div', { 
          key: conv.id,
          style: { 
            padding: 12, 
            backgroundColor: '#374151', 
            borderRadius: 8, 
            marginBottom: 8,
            cursor: 'pointer'
          },
          onClick: () => setCurrentConversation(conv)
        }, conv.title || `Conversation ${conv.id}`)
      ) : React.createElement('div', { 
        style: { 
          padding: 12, 
          backgroundColor: '#374151', 
          borderRadius: 8, 
          textAlign: 'center',
          color: '#9ca3af'
        } }, 'No conversations yet')
    )
  ]);
};

// Simple Chat Window Component
const ChatWindow = () => {
  const { 
    currentConversation, 
    messages, 
    sendMessage, 
    isTyping,
    setMessages
  } = useChat();
  const [inputMessage, setInputMessage] = React.useState('');
  const messagesEndRef = React.useRef(null);

  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    console.log('=== SEND MESSAGE DEBUG ===');
    console.log('Input message:', inputMessage);
    console.log('Current conversation:', currentConversation);
    console.log('Is typing:', isTyping);
    
    if (!inputMessage.trim()) {
      console.log('❌ Message is empty');
      return;
    }
    
    if (!currentConversation) {
      console.log('❌ No current conversation');
      return;
    }
    
    if (isTyping) {
      console.log('❌ Already typing');
      return;
    }
    
    // Clear input immediately (like ChatGPT does)
    const messageToSend = inputMessage;
    setInputMessage('');
    
    try {
      console.log('📤 Sending message to backend...');
      await sendMessage(messageToSend);
      console.log('✅ Message sent successfully');
    } catch (error) {
      console.error('❌ Failed to send message:', error);
      console.error('Error details:', error.response?.data);
      // Restore the input message if sending failed
      setInputMessage(messageToSend);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!currentConversation) {
    return React.createElement('div', {
      style: { 
        flex: 1, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        backgroundColor: '#f9fafb'
      }
    }, [
      React.createElement('div', {
        style: {
          textAlign: 'center',
          maxWidth: 600,
          padding: 40
        }
      }, [
        React.createElement('h2', { style: { fontSize: 24, color: '#1f2937', marginBottom: 16 } }, '🤖 Enterprise AI Assistant'),
        React.createElement('p', { style: { fontSize: 16, color: '#6b7280', marginBottom: 20 } }, 'Select or create a conversation to start chatting'),
        React.createElement('div', {
          style: {
            backgroundColor: '#e0f2fe',
            padding: 20,
            borderRadius: 8,
            fontSize: 14
          }
        }, '💡 Click "+ New Conversation" in the sidebar to begin')
      ])
    ]);
  }

  return React.createElement('div', {
    style: { flex: 1, display: 'flex', flexDirection: 'column', backgroundColor: '#f9fafb' }
  }, [
    React.createElement('div', {
      style: { 
        backgroundColor: 'white', 
        borderBottom: '1px solid #e5e7eb', 
        padding: 16,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }
    }, [
      React.createElement('h3', { style: { fontSize: 18, fontWeight: 'bold', color: '#1f2937' } }, 
        currentConversation.title || `Conversation ${currentConversation.id}`
      )
    ]),
    
    React.createElement('div', {
      style: { 
        flex: 1, 
        padding: 20, 
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column'
      }
    }, [
      messages.length === 0 ? React.createElement('div', {
        style: {
          textAlign: 'center',
          padding: 40,
          color: '#6b7280'
        }
      }, 'Start a conversation by typing a message below...') :
      
      messages.map(message => 
        React.createElement('div', {
          key: message.id,
          style: {
            marginBottom: 16,
            display: 'flex',
            justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start'
          }
        }, [
          React.createElement('div', {
            style: {
              maxWidth: '70%',
              padding: 12,
              borderRadius: 12,
              backgroundColor: message.role === 'user' ? '#3b82f6' : '#f3f4f6',
              color: message.role === 'user' ? 'white' : '#1f2937'
            }
          }, [
            React.createElement('div', { style: { fontWeight: 'bold', marginBottom: 4 } }, 
              message.role === 'user' ? '👤 You' : '🤖 AI Assistant'
            ),
            React.createElement('div', null, message.content)
          ])
        ])
      ),
      
      isTyping && React.createElement('div', {
        style: {
          display: 'flex',
          justifyContent: 'flex-start',
          marginBottom: 16
        }
      }, [
        React.createElement('div', {
          style: {
            backgroundColor: '#f3f4f6',
            padding: 12,
            borderRadius: 12,
            color: '#1f2937'
          }
        }, '🤖 AI is typing...')
      ]),
      
      React.createElement('div', { ref: messagesEndRef })
    ]),
    
    React.createElement('div', {
      style: {
        backgroundColor: 'white',
        borderTop: '1px solid #e5e7eb',
        padding: 16
      }
    }, [
      React.createElement('div', {
        style: {
          display: 'flex',
          gap: 8
        }
      }, [
        React.createElement('input', {
          type: 'text',
          value: inputMessage,
          onChange: (e) => setInputMessage(e.target.value),
          onKeyPress: handleKeyPress,
          placeholder: 'Type your message...',
          disabled: isTyping,
          style: {
            flex: 1,
            padding: 12,
            border: '1px solid #d1d5db',
            borderRadius: 8,
            fontSize: 14,
            outline: 'none'
          }
        }),
        React.createElement('button', {
          onClick: handleSendMessage,
          disabled: !inputMessage.trim() || isTyping,
          style: {
            padding: '12px 24px',
            backgroundColor: (!inputMessage.trim() || isTyping) ? '#d1d5db' : '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: 8,
            cursor: (!inputMessage.trim() || isTyping) ? 'not-allowed' : 'pointer',
            fontSize: 14
          }
        }, isTyping ? 'Sending...' : 'Send')
      ])
    ])
  ]);
};

const Dashboard = () => {
  return React.createElement('div', {
    style: { display: 'flex', minHeight: '100vh', backgroundColor: '#f9fafb' }
  }, [
    React.createElement(Sidebar),
    React.createElement('div', {
      style: { flex: 1, display: 'flex', flexDirection: 'column' }
    }, [
      React.createElement('div', {
        style: {
          backgroundColor: 'white',
          borderBottom: '1px solid #e5e7eb',
          padding: 16,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }
      }, [
        React.createElement('h1', {
          style: { fontSize: 20, fontWeight: 'bold', color: '#1f2937' }
        }, 'Enterprise AI Assistant')
      ]),
      React.createElement(ChatWindow)
    ])
  ]);
};

const App = () => {
  return React.createElement(
    AuthProvider,
    null,
    React.createElement(
      ChatProvider,
      null,
      React.createElement(
        Router,
        null,
        React.createElement(Routes, null, [
          React.createElement(Route, { 
            path: '/login', 
            element: React.createElement(Login) 
          }),
          React.createElement(Route, { 
            path: '/', 
            element: React.createElement(
              ProtectedRoute,
              null,
              React.createElement(Dashboard)
            ) 
          })
        ])
      )
    )
  );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(React.createElement(App));
