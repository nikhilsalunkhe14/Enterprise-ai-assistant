import React, { useState } from 'react';
import { useChat } from '../index';

export const Sidebar = () => {
  const { 
    conversations, 
    currentConversation, 
    isLoading, 
    createConversation, 
    fetchMessages, 
    deleteConversation,
    setCurrentConversation,
    setMessages
  } = useChat();

  const [showNewConversationModal, setShowNewConversationModal] = useState(false);
  const [newConversationTitle, setNewConversationTitle] = useState('');

  const handleCreateConversation = async () => {
    if (!newConversationTitle.trim()) return;

    const newConversation = await createConversation(newConversationTitle);
    if (newConversation) {
      setNewConversationTitle('');
      setShowNewConversationModal(false);
      fetchMessages(newConversation.id);
    }
  };

  const handleConversationClick = async (conversation) => {
    if (currentConversation?.id === conversation.id) return;
    fetchMessages(conversation.id);
  };

  const handleDeleteConversation = async (conversationId, e) => {
    e.stopPropagation();
    
    if (window.confirm('Are you sure you want to delete this conversation?')) {
      const success = await deleteConversation(conversationId);
      if (!success) {
        alert('Failed to delete conversation');
      }
    }
  };

  return (
    <>
      <div className="w-80 bg-gray-900 h-screen flex flex-col border-r border-gray-800">
        {/* Header */}
        <div className="p-4 border-b border-gray-800">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Conversations</h2>
            <button
              onClick={() => setShowNewConversationModal(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-lg transition-colors duration-200"
              title="New Conversation"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>
        </div>

        {/* Conversations List */}
        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="p-4 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
            </div>
          ) : conversations.length === 0 ? (
            <div className="p-4 text-center text-gray-400">
              <svg className="w-12 h-12 mx-auto mb-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8-9s-9-4.582-9-10c0-1.653.387-3.198 1.091-4.355 2.447-4.492 3.88-5.466 4.511-6.386.577-7.245.855-8.704 1.497-9.226 2.457-9.632 3.279-9.878 4.032-9.96 4.617-9.842 5.012-9.562 5.274-9.248 5.414-8.896 5.417-8.537 5.381-8.23 5.267-7.975 5.099-7.745 4.868-7.546 4.615-7.409 4.298-7.32 3.941-7.281 3.534-7.298 3.077-7.371 2.561-7.49 1.996-7.658 1.369-7.876.698-8.136.011-8.418-.727-8.722-1.498-9.045-2.331-9.379-3.242-9.698-4.19-9.98-5.219-10.238-6.28-10.475-7.362-10.682-8.478-10.856-9.6-10.976-10.736-10.99-10.736z" />
              </svg>
              <p className="text-sm">No conversations yet</p>
              <p className="text-xs text-gray-500 mt-2">Create your first conversation to get started</p>
            </div>
          ) : (
            <div className="p-2">
              {conversations.map((conversation) => (
                <div
                  key={conversation.id}
                  onClick={() => handleConversationClick(conversation)}
                  className={`p-3 rounded-lg cursor-pointer transition-all duration-200 mb-2 ${
                    currentConversation?.id === conversation.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-800 text-gray-300 hover:bg-gray-700 hover:text-white'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-medium truncate">
                        {conversation.title}
                      </h3>
                      <p className="text-xs opacity-75 mt-1">
                        {conversation.message_count || 0} messages
                      </p>
                    </div>
                    <button
                      onClick={(e) => handleDeleteConversation(conversation.id, e)}
                      className="ml-2 text-gray-400 hover:text-red-400 p-1 transition-colors"
                      title="Delete conversation"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* New Conversation Modal */}
      {showNewConversationModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-96 shadow-2xl">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Create New Conversation
            </h3>
            <input
              type="text"
              placeholder="Enter conversation title..."
              value={newConversationTitle}
              onChange={(e) => setNewConversationTitle(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              autoFocus
            />
            <div className="flex justify-end space-x-3 mt-4">
              <button
                onClick={() => setShowNewConversationModal(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateConversation}
                disabled={!newConversationTitle.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
