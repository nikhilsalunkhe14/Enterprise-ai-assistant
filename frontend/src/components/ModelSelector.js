import React, { useState } from 'react';
import { useChat } from '../index';

export const ModelSelector = () => {
  const { availableModels, selectedModel, setSelectedModel } = useChat();
  const [isOpen, setIsOpen] = useState(false);

  const selectedModelConfig = availableModels.find(model => model.id === selectedModel);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors duration-200"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0 1.756 2.924 3.35 0 1.756-2.924-3.35-1.756zm3.35 6.817l-3.35-6.817c-.433 1.756-2.924 1.756-3.35 0-1.756 2.924-3.35 0 1.756 2.924 3.35 1.756zm5.01 3.35l-5.01-3.35c-.433 1.756-2.924 1.756-3.35 0-1.756 2.924-3.35 0 1.756 2.924 3.35 1.756z" />
        </svg>
        <span className="text-sm font-medium">
          {selectedModelConfig?.name || 'Select Model'}
        </span>
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-80 bg-white rounded-lg shadow-xl border border-gray-200 z-50">
          <div className="p-4">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Select AI Model</h3>
            <div className="space-y-2">
              {availableModels.map((model) => (
                <button
                  key={model.id}
                  onClick={() => {
                    setSelectedModel(model.id);
                    setIsOpen(false);
                  }}
                  className={`w-full text-left p-3 rounded-lg transition-colors duration-200 ${
                    selectedModel === model.id
                      ? 'bg-blue-50 border-2 border-blue-500 text-blue-700'
                      : 'bg-gray-50 border border-gray-200 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-sm">{model.name}</div>
                      <div className="text-xs text-gray-500 mt-1">{model.description}</div>
                    </div>
                    <div className="text-xs text-gray-400">
                      {model.max_tokens.toLocaleString()} tokens
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
