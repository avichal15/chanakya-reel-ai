import React, { useState, useRef } from 'react';
import { SAMPLE_POST } from '../constants';
import { getTopPosts, transcribeAudio } from '../services/gemini';
import { RedditPost } from '../types';

interface Props {
  onAnalyze: (input: string) => void;
  isLoading: boolean;
  apiKey?: string | null;
}

type Tab = 'text' | 'discover' | 'dictate';

export const RedditInput: React.FC<Props> = ({ onAnalyze, isLoading, apiKey }) => {
  const [activeTab, setActiveTab] = useState<Tab>('text');
  
  // Text State
  const [input, setInput] = useState('');

  // Discover State
  const [subredditSearch, setSubredditSearch] = useState('');
  const [topPosts, setTopPosts] = useState<RedditPost[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Dictate State
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  // -- Text Handlers --
  const handleAnalyze = () => {
    if (input.trim()) onAnalyze(input.trim());
  };

  const handleUseSample = () => {
    const sampleText = `${SAMPLE_POST.title}\n\n${SAMPLE_POST.content}`;
    setInput(sampleText);
    onAnalyze(sampleText);
  };

  // -- Discover Handlers --
  const handleSearchPosts = async () => {
    if (!apiKey || !subredditSearch.trim()) return;
    setIsSearching(true);
    try {
      const posts = await getTopPosts(apiKey, subredditSearch.trim());
      setTopPosts(posts);
    } catch (e) {
      console.error(e);
      alert("Failed to fetch top posts.");
    } finally {
      setIsSearching(false);
    }
  };

  const selectPost = (post: RedditPost) => {
    // We pass the content directly to analyze, or formatted text
    const textToAnalyze = `${post.title}\n\n${post.content}`;
    onAnalyze(textToAnalyze);
  };

  // -- Dictate Handlers --
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks: BlobPart[] = [];

      recorder.ondataavailable = (e) => chunks.push(e.data);
      recorder.onstop = async () => {
        const audioBlob = new Blob(chunks, { type: 'audio/webm' }); // Chrome default
        if (apiKey) {
            setIsSearching(true); // Reuse searching spinner
            try {
                const text = await transcribeAudio(apiKey, audioBlob);
                setInput(text);
                setActiveTab('text'); // Switch back to text to verify
            } catch (e) {
                alert("Transcription failed.");
            } finally {
                setIsSearching(false);
            }
        }
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current = recorder;
      recorder.start();
      setIsRecording(true);
    } catch (e) {
      alert("Microphone access denied or not available.");
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setIsRecording(false);
  };

  return (
    <div className="bg-studio-panel rounded-xl p-6 border border-gray-800">
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-reddit p-2 rounded-full">
          <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701z"/></svg>
        </div>
        <h2 className="text-xl font-display font-bold">Step 1: Source Content</h2>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 mb-6 border-b border-gray-700">
        <button
            onClick={() => setActiveTab('text')}
            className={`pb-2 px-4 text-sm font-medium transition-colors ${activeTab === 'text' ? 'text-studio-accent border-b-2 border-studio-accent' : 'text-gray-400 hover:text-white'}`}
        >
            Link / Text
        </button>
        <button
            onClick={() => setActiveTab('discover')}
            className={`pb-2 px-4 text-sm font-medium transition-colors ${activeTab === 'discover' ? 'text-studio-accent border-b-2 border-studio-accent' : 'text-gray-400 hover:text-white'}`}
        >
            Discover Top Posts
        </button>
        <button
            onClick={() => setActiveTab('dictate')}
            className={`pb-2 px-4 text-sm font-medium transition-colors ${activeTab === 'dictate' ? 'text-studio-accent border-b-2 border-studio-accent' : 'text-gray-400 hover:text-white'}`}
        >
            Dictate Story
        </button>
      </div>

      {/* TEXT TAB */}
      {activeTab === 'text' && (
        <div className="animate-fade-in">
          <p className="text-gray-400 mb-4 text-sm">Paste a Reddit post URL or raw text content to begin.</p>
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="https://reddit.com/r/... or 'My neighbor stole my cat...'"
              className="flex-1 bg-studio-dark border border-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-studio-accent outline-none"
            />
            <button
              onClick={handleAnalyze}
              disabled={isLoading || !input.trim()}
              className="bg-studio-accent disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-600 text-white font-bold px-6 py-3 rounded-lg transition-all"
            >
              {isLoading ? 'Analyzing...' : 'Fetch'}
            </button>
          </div>
          <div className="mt-4">
            <button onClick={handleUseSample} className="text-xs text-gray-500 hover:text-white underline">
              Use sample post for demo
            </button>
          </div>
        </div>
      )}

      {/* DISCOVER TAB */}
      {activeTab === 'discover' && (
        <div className="animate-fade-in space-y-4">
            <p className="text-gray-400 text-sm">Find top trending posts from any subreddit using Gemini Search.</p>
            <div className="flex gap-2">
                <input
                    type="text"
                    value={subredditSearch}
                    onChange={(e) => setSubredditSearch(e.target.value)}
                    placeholder="e.g. r/AskReddit, r/tifu, r/nosleep"
                    className="flex-1 bg-studio-dark border border-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-studio-accent outline-none"
                />
                <button
                    onClick={handleSearchPosts}
                    disabled={isSearching || !subredditSearch.trim()}
                    className="bg-orange-600 hover:bg-orange-700 disabled:opacity-50 text-white font-bold px-6 py-3 rounded-lg transition-all"
                >
                    {isSearching ? 'Searching...' : 'Find Posts'}
                </button>
            </div>
            
            {topPosts.length > 0 && (
                <div className="grid gap-3 mt-4 max-h-60 overflow-y-auto pr-2">
                    {topPosts.map((post, idx) => (
                        <div 
                            key={idx} 
                            onClick={() => selectPost(post)}
                            className="bg-studio-dark p-3 rounded-lg border border-gray-700 hover:border-studio-accent cursor-pointer transition-colors group"
                        >
                            <h3 className="font-bold text-sm group-hover:text-studio-accent truncate">{post.title}</h3>
                            <p className="text-xs text-gray-500 line-clamp-2 mt-1">{post.content || "(No text content)"}</p>
                            <div className="text-[10px] text-gray-600 mt-2 flex justify-between">
                                <span>{post.author}</span>
                                <span>Click to Select &rarr;</span>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
      )}

      {/* DICTATE TAB */}
      {activeTab === 'dictate' && (
        <div className="animate-fade-in text-center py-6">
            <div className={`w-20 h-20 mx-auto rounded-full flex items-center justify-center cursor-pointer transition-all ${isRecording ? 'bg-red-600 animate-pulse shadow-[0_0_20px_rgba(220,38,38,0.5)]' : 'bg-gray-700 hover:bg-gray-600'}`}
                 onClick={isRecording ? stopRecording : startRecording}
            >
                {isRecording ? (
                     <div className="w-8 h-8 bg-white rounded-sm"></div>
                ) : (
                     <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
                )}
            </div>
            <p className="mt-4 text-white font-medium">{isRecording ? 'Recording... Tap to stop' : 'Tap mic to start dictating'}</p>
            <p className="text-xs text-gray-500 mt-2">
                {isSearching ? 'Transcribing...' : 'Your speech will be converted to text for the script.'}
            </p>
        </div>
      )}
    </div>
  );
};