import React, { useState, useRef, useEffect } from 'react';

export const ChatWindow = () => {
  const [newMessage, setNewMessage] = useState('');
  const [isComposing, setIsComposing] = useState(false);
  const textareaRef = useRef(null);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
  }, [newMessage]);

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;

    const message = newMessage.trim();
    setNewMessage('');
    setIsComposing(false);
    
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatMessage = (content) => {
    if (content.includes('```')) {
      return content.split('```').map((part, index) => {
        if (index % 2 === 1) {
          return '<pre class="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto"><code>' + part + '</code></pre>';
        }
        return part;
      }).join('');
    }
    
    return content.replace(/\n/g, '<br />');
  };

  return (
    <div className="flex-1 flex flex-col bg-white">
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Welcome to Enterprise AI Assistant</h2>
            <p className="text-sm text-gray-500">Select a conversation to start chatting</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto">
          <div className="px-6 py-4">
            <div className="text-center">
              <h3 className="text-xl font-bold text-gray-900 mb-4">ChatGPT-like Interface</h3>
              <p className="text-gray-600 mb-6">
                Professional chat interface with AI model selection and smooth animations.
              </p>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h4 className="font-semibold text-blue-900 mb-3">Features:</h4>
                <ul className="space-y-2 text-sm text-blue-800">
                  <li className="flex items-center">
                    <svg className="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l.322.322m1.636-.322L16 7m3 3h-1V4a1 1 0 00-1-1H4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    <span>Multiple AI Models</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h4a2 2 0 012 2v8a2 2 0 01-2 2zm6-4V6a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2h4a2 2 0 002 2v-4z" />
                    </svg>
                    <span>Smooth Animations</span>
                  </li>
                  <li className="flex items-center">
                    <svg className="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                    <span>Professional UI</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="border-t border-gray-200 bg-white px-6 py-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-end space-x-4">
            <div className="flex-1">
              <textarea
                ref={textareaRef}
                value={newMessage}
                onChange={(e) => {
                  setNewMessage(e.target.value);
                  setIsComposing(true);
                }}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                rows={1}
              />
            </div>
            <button
              onClick={handleSendMessage}
              disabled={!newMessage.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-all duration-200 flex items-center space-x-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
              <span>Send</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
