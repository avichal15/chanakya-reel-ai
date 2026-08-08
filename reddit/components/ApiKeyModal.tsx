import React, { useState } from 'react';

interface Props {
  onSave: (key: string) => void;
}

export const ApiKeyModal: React.FC<Props> = ({ onSave }) => {
  const [key, setKey] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (key.trim()) {
      onSave(key.trim());
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="bg-studio-panel p-8 rounded-xl max-w-md w-full border border-gray-700 shadow-2xl">
        <h2 className="text-2xl font-display font-bold mb-4 text-white">Welcome to Reddit Shorts Studio</h2>
        <p className="text-gray-400 mb-6 text-sm">
          To generate scripts, voiceovers, and videos, this app requires a Google Gemini API Key. 
          Your key is stored locally in memory and never sent to our servers.
        </p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase text-gray-500 mb-1">Gemini API Key</label>
            <input
              type="password"
              value={key}
              onChange={(e) => setKey(e.target.value)}
              placeholder="AIza..."
              className="w-full bg-studio-dark border border-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-studio-accent outline-none"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full bg-studio-accent hover:bg-blue-600 text-white font-bold py-3 rounded-lg transition-all"
          >
            Start Creating
          </button>
        </form>
        <div className="mt-4 text-center">
          <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noreferrer" className="text-xs text-blue-400 hover:underline">
            Get an API Key here
          </a>
        </div>
      </div>
    </div>
  );
};