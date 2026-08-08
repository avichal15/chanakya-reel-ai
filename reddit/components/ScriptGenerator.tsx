import React from 'react';
import { RedditPost, ScriptData } from '../types';

interface Props {
  post: RedditPost;
  script: ScriptData | null;
  isLoading: boolean;
  onGenerate: () => void;
  onUpdateScript: (text: string) => void;
  onNext: () => void;
}

export const ScriptGenerator: React.FC<Props> = ({ post, script, isLoading, onGenerate, onUpdateScript, onNext }) => {
  return (
    <div className="bg-studio-panel rounded-xl p-6 border border-gray-800">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="bg-purple-600 p-2 rounded-full">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
          </div>
          <h2 className="text-xl font-display font-bold">Step 2: Scripting</h2>
        </div>
        {!script && (
          <button
            onClick={onGenerate}
            disabled={isLoading}
            className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors"
          >
            {isLoading ? 'Generating Script...' : 'Generate with AI'}
          </button>
        )}
      </div>

      {script ? (
        <div className="space-y-4 animate-fade-in">
           <div className="bg-studio-dark p-4 rounded-lg border border-gray-700">
             <div className="flex justify-between items-center mb-2">
               <label className="text-xs font-bold uppercase text-gray-500">Viral Script (Editable)</label>
               <span className="text-xs text-purple-400">~45 sec est.</span>
             </div>
             <textarea
               value={script.fullScript}
               onChange={(e) => onUpdateScript(e.target.value)}
               className="w-full h-48 bg-transparent text-white text-sm resize-none focus:outline-none"
             />
           </div>
           
           <div className="flex justify-end">
             <button
               onClick={onNext}
               className="bg-white text-black hover:bg-gray-200 font-bold px-6 py-2 rounded-lg transition-colors"
             >
               Next: Voice & Video &rarr;
             </button>
           </div>
        </div>
      ) : (
        <div className="bg-studio-dark/50 p-6 rounded-lg border border-dashed border-gray-700 text-center">
          <p className="text-gray-500 text-sm">Post loaded: "{(post.title || "Untitled").substring(0, 40)}..."</p>
          <p className="text-gray-400 text-sm mt-1">Ready to generate script.</p>
        </div>
      )}
    </div>
  );
};