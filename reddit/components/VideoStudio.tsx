import React, { useRef, useState, useEffect, useMemo } from 'react';
import { ScriptData, VOICES, CaptionStyle } from '../types';
import { DEFAULT_BACKGROUND_VIDEO, PREDEFINED_BACKGROUNDS, BACKGROUND_MUSIC_TRACKS } from '../constants';

interface Props {
  script: ScriptData;
  audioBlob: Blob | null;
  backgroundVideoUrl: string | null;
  captionStyle: CaptionStyle;
  avatarImageUrl?: string | null;
  musicUrl: string | null;
  musicVolume: number;
  isGeneratingAudio: boolean;
  isGeneratingVideo: boolean;
  isGeneratingAvatar?: boolean;
  onGenerateAudio: (voiceId: string) => void;
  onGenerateVeoBackground: (image?: string) => void;
  onGenerateAvatar?: (prompt: string) => void;
  onSetBackgroundVideo: (url: string) => void;
  onUpdateCaptionStyle: (style: Partial<CaptionStyle>) => void;
  onSetMusic: (url: string) => void;
  onSetMusicVolume: (vol: number) => void;
  onNext: () => void;
}

const AVATAR_PRESETS = [
    { label: "3D Pixar Style", prompt: "3D rendered cute character, pixar style, expressive face" },
    { label: "Realistic Portrait", prompt: "Hyper-realistic portrait of a person looking at camera, studio lighting" },
    { label: "Cyberpunk", prompt: "Futuristic cyberpunk character, neon lights, glowing eyes" },
    { label: "Oil Painting", prompt: "Classic oil painting style portrait, textured brushstrokes" }
];

export const VideoStudio: React.FC<Props> = ({
  script,
  audioBlob,
  backgroundVideoUrl,
  captionStyle,
  avatarImageUrl,
  musicUrl,
  musicVolume,
  isGeneratingAudio,
  isGeneratingVideo,
  isGeneratingAvatar,
  onGenerateAudio,
  onGenerateVeoBackground,
  onGenerateAvatar,
  onSetBackgroundVideo,
  onUpdateCaptionStyle,
  onSetMusic,
  onSetMusicVolume,
  onNext
}) => {
  const [selectedVoice, setSelectedVoice] = useState(VOICES[0].id);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [customUrlInput, setCustomUrlInput] = useState('');
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);
  
  // Tab State
  const [activeVisualTab, setActiveVisualTab] = useState<'background' | 'avatar'>('background');

  // Avatar State
  const [avatarPrompt, setAvatarPrompt] = useState(AVATAR_PRESETS[0].prompt);

  // Veo Image State
  const [veoReferenceImage, setVeoReferenceImage] = useState<string | null>(null);
  const veoImageInputRef = useRef<HTMLInputElement>(null);
  
  const audioRef = useRef<HTMLAudioElement>(null);
  const musicRef = useRef<HTMLAudioElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const animationFrameRef = useRef<number | null>(null);

  // Memoize audio URL
  const audioSrc = useMemo(() => {
    return audioBlob ? URL.createObjectURL(audioBlob) : null;
  }, [audioBlob]);

  // --- PLAYBACK ENGINE ---
  
  // 1. Sync Play/Pause State
  useEffect(() => {
    const applyPlayState = async () => {
      if (isPlaying) {
        try {
          const promises = [];
          if (audioRef.current) promises.push(audioRef.current.play());
          if (videoRef.current) promises.push(videoRef.current.play());
          if (musicRef.current && musicUrl) promises.push(musicRef.current.play());
          
          await Promise.allSettled(promises);
        } catch (e) {
          console.warn("Playback failed:", e);
          setIsPlaying(false);
        }
      } else {
        audioRef.current?.pause();
        videoRef.current?.pause();
        musicRef.current?.pause();
      }
    };
    applyPlayState();
  }, [isPlaying, musicUrl]); // Re-run if music changes while playing

  // 2. Sync Loop (RequestAnimationFrame) for smoother UI & Video Sync
  useEffect(() => {
    const tick = () => {
      if (!isPlaying || !audioRef.current) return;

      const t = audioRef.current.currentTime;
      setCurrentTime(t);

      // --- Video Drift Correction ---
      // We only correct if drift is significant (>0.5s) to prevent visual stuttering
      if (videoRef.current && !videoRef.current.paused && videoRef.current.duration) {
        const vDuration = videoRef.current.duration;
        const expectedVideoTime = t % vDuration; // Loop logic
        const diff = Math.abs(videoRef.current.currentTime - expectedVideoTime);
        
        // If drift is large (and we aren't at the loop boundary), force sync
        // Boundary check: diff < (vDuration - 0.5) ensures we don't snap when the video naturally loops from end to start
        if (diff > 0.5 && diff < (vDuration - 0.5)) {
           videoRef.current.currentTime = expectedVideoTime;
        }
      }

      // --- Music Drift Correction ---
      if (musicRef.current && !musicRef.current.paused && musicUrl && musicRef.current.duration) {
        const mDuration = musicRef.current.duration;
        const expectedMusicTime = t % mDuration;
        const diff = Math.abs(musicRef.current.currentTime - expectedMusicTime);
        if (diff > 0.5 && diff < (mDuration - 0.5)) {
            musicRef.current.currentTime = expectedMusicTime;
        }
      }

      animationFrameRef.current = requestAnimationFrame(tick);
    };

    if (isPlaying) {
      animationFrameRef.current = requestAnimationFrame(tick);
    } else {
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
    }

    return () => {
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
    };
  }, [isPlaying, musicUrl]);


  // 3. Handle Audio Ending
  const handleAudioEnded = () => {
    setIsPlaying(false);
    setCurrentTime(0);
    if (audioRef.current) audioRef.current.currentTime = 0;
    if (videoRef.current) {
        videoRef.current.pause();
        videoRef.current.currentTime = 0;
    }
    if (musicRef.current) {
        musicRef.current.pause();
        musicRef.current.currentTime = 0;
    }
    if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
  };

  // 4. Metadata Loaded
  const handleLoadedMetadata = () => {
    if (audioRef.current && isFinite(audioRef.current.duration)) {
        setDuration(audioRef.current.duration);
    }
  };

  // 5. Seeking
  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value);
    setCurrentTime(time);
    
    if (audioRef.current) audioRef.current.currentTime = time;
    
    if (videoRef.current && !isNaN(videoRef.current.duration)) {
         videoRef.current.currentTime = time % videoRef.current.duration;
    }
    if (musicRef.current && !isNaN(musicRef.current.duration)) {
         musicRef.current.currentTime = time % musicRef.current.duration;
    }
  };

  // 6. Volume Control
  useEffect(() => {
    if (musicRef.current) {
        musicRef.current.volume = musicVolume;
    }
  }, [musicVolume]);

  const togglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  const handleCustomUrlSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (customUrlInput.trim()) {
      onSetBackgroundVideo(customUrlInput.trim());
      setUploadedFileName(null);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      onSetBackgroundVideo(url);
      setUploadedFileName(file.name);
      setCustomUrlInput('');
    }
  };

  const handleVeoImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = (reader.result as string).split(',')[1];
        setVeoReferenceImage(base64);
      };
      reader.readAsDataURL(file);
    }
  };

  const formatTime = (seconds: number) => {
    if (!isFinite(seconds) || isNaN(seconds)) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Find current caption
  const currentCaption = script.captions.find(
    c => currentTime >= c.start && currentTime <= c.end
  );

  const finalVideoUrl = backgroundVideoUrl || DEFAULT_BACKGROUND_VIDEO;
  const isCustomUrl = !PREDEFINED_BACKGROUNDS.find(bg => bg.url === finalVideoUrl) && finalVideoUrl !== DEFAULT_BACKGROUND_VIDEO;

  return (
    <div className="bg-studio-panel rounded-xl p-6 border border-gray-800">
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-pink-600 p-2 rounded-full">
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
        </div>
        <h2 className="text-xl font-display font-bold">Step 3: Studio & Production</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Controls Column */}
        <div className="space-y-6">
          
          {/* Audio Generation */}
          <div className="bg-studio-dark p-4 rounded-lg border border-gray-700">
            <h3 className="text-sm font-bold uppercase text-gray-500 mb-3">1. AI Voiceover</h3>
            <div className="flex gap-2">
              <select
                value={selectedVoice}
                onChange={(e) => setSelectedVoice(e.target.value)}
                className="flex-1 bg-studio-panel text-white text-sm rounded-lg p-2 border border-gray-600 focus:outline-none"
              >
                {VOICES.map(v => <option key={v.id} value={v.id}>{v.name}</option>)}
              </select>
              <button
                onClick={() => onGenerateAudio(selectedVoice)}
                disabled={isGeneratingAudio}
                className="bg-pink-600 hover:bg-pink-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-bold"
              >
                {isGeneratingAudio ? 'Generating...' : 'Generate'}
              </button>
            </div>
            {audioBlob && <p className="text-green-400 text-xs mt-2">✓ Audio generated successfully ({formatTime(duration)})</p>}
          </div>

          {/* Audio Mixing */}
          <div className="bg-studio-dark p-4 rounded-lg border border-gray-700">
             <h3 className="text-sm font-bold uppercase text-gray-500 mb-3">2. Background Music</h3>
             <div className="space-y-3">
                 <select 
                    onChange={(e) => onSetMusic(e.target.value)}
                    value={musicUrl || ""}
                    className="w-full bg-studio-panel text-white text-sm rounded-lg p-2 border border-gray-600 focus:outline-none"
                 >
                     {BACKGROUND_MUSIC_TRACKS.map((track, i) => (
                         <option key={i} value={track.url}>{track.name} {track.url ? `(${track.category})` : ''}</option>
                     ))}
                 </select>
                 
                 {musicUrl && (
                     <div className="flex items-center gap-3">
                         <span className="text-xs text-gray-400">Volume</span>
                         <input 
                            type="range" 
                            min="0" max="1" step="0.05"
                            value={musicVolume}
                            onChange={(e) => onSetMusicVolume(parseFloat(e.target.value))}
                            className="flex-1 h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer accent-studio-accent"
                         />
                         <span className="text-xs text-gray-400 w-8">{Math.round(musicVolume * 100)}%</span>
                     </div>
                 )}
             </div>
          </div>

          {/* Video Background / Avatar */}
          <div className="bg-studio-dark p-4 rounded-lg border border-gray-700">
            <h3 className="text-sm font-bold uppercase text-gray-500 mb-3">3. Visuals</h3>
            
            {/* Visual Tabs */}
            <div className="flex gap-2 mb-4 border-b border-gray-600">
                <button
                    onClick={() => setActiveVisualTab('background')}
                    className={`pb-2 px-2 text-xs font-bold transition-colors ${activeVisualTab === 'background' ? 'text-white border-b-2 border-white' : 'text-gray-400'}`}
                >
                    Background Video
                </button>
                <button
                    onClick={() => setActiveVisualTab('avatar')}
                    className={`pb-2 px-2 text-xs font-bold transition-colors ${activeVisualTab === 'avatar' ? 'text-white border-b-2 border-white' : 'text-gray-400'}`}
                >
                    AI Avatar
                </button>
            </div>

            {activeVisualTab === 'background' ? (
                <div className="space-y-4 animate-fade-in">
                    {/* Option A: Veo Gen */}
                    <div>
                        <p className="text-xs text-gray-400 mb-2 font-semibold">Option A: Generate unique background</p>
                        {/* Optional Image Input for Veo */}
                        <div className="flex items-center gap-2 mb-2">
                            <button
                                onClick={() => veoImageInputRef.current?.click()}
                                className="text-[10px] bg-gray-800 hover:bg-gray-700 text-gray-300 px-2 py-1 rounded border border-gray-600"
                            >
                                {veoReferenceImage ? 'Change Reference Image' : '+ Add Reference Image (Optional)'}
                            </button>
                            {veoReferenceImage && (
                                <button 
                                    onClick={() => { setVeoReferenceImage(null); if(veoImageInputRef.current) veoImageInputRef.current.value = ''; }}
                                    className="text-[10px] text-red-400 hover:text-red-300"
                                >
                                    Clear
                                </button>
                            )}
                            <input type="file" ref={veoImageInputRef} accept="image/*" className="hidden" onChange={handleVeoImageUpload} />
                        </div>
                        {veoReferenceImage && <p className="text-[10px] text-green-500 mb-2">Image loaded. Veo will animate this.</p>}

                        <button
                            onClick={() => onGenerateVeoBackground(veoReferenceImage || undefined)}
                            disabled={isGeneratingVideo}
                            className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white py-2 rounded-lg text-sm font-bold flex items-center justify-center gap-2"
                        >
                            {isGeneratingVideo ? (
                                <>Generating...</>
                            ) : (
                                <>
                                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
                                    {veoReferenceImage ? 'Animate Image with Veo' : 'Generate with Veo AI'}
                                </>
                            )}
                        </button>
                    </div>

                    <div className="h-px bg-gray-600 w-full"></div>

                    {/* Option B: Manual */}
                    <div>
                        <p className="text-xs text-gray-400 mb-2 font-semibold">Option B: Select stock, upload, or custom</p>
                        <div className="flex flex-col gap-3">
                            <select 
                                onChange={(e) => {
                                    onSetBackgroundVideo(e.target.value);
                                    setUploadedFileName(null);
                                }} 
                                className="bg-studio-panel text-white text-sm rounded-lg p-2 border border-gray-600 focus:outline-none w-full"
                                value={isCustomUrl ? "custom" : finalVideoUrl}
                            >
                                <option value={DEFAULT_BACKGROUND_VIDEO}>Minecraft Parkour (Default)</option>
                                {PREDEFINED_BACKGROUNDS.map(bg => (
                                    <option key={bg.url} value={bg.url}>{bg.name}</option>
                                ))}
                                {isCustomUrl && (
                                    <option value="custom">Custom/Uploaded Video</option>
                                )}
                            </select>

                            <input
                                type="file"
                                ref={fileInputRef}
                                onChange={handleFileUpload}
                                accept="video/*"
                                className="hidden"
                            />
                            <button
                                onClick={() => fileInputRef.current?.click()}
                                className="bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded-lg text-xs font-bold flex items-center justify-center gap-2 border border-gray-600"
                            >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
                                {uploadedFileName ? `Change File (${uploadedFileName})` : 'Upload Video File'}
                            </button>

                            <form onSubmit={handleCustomUrlSubmit} className="flex gap-2">
                                <input 
                                    type="text" 
                                    placeholder="Or paste .mp4 URL..." 
                                    value={customUrlInput}
                                    onChange={(e) => setCustomUrlInput(e.target.value)}
                                    className="flex-1 bg-studio-panel border border-gray-600 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-studio-accent"
                                />
                                <button 
                                    type="submit"
                                    className="bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded-lg text-xs"
                                >
                                    Set
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="space-y-4 animate-fade-in">
                    {/* Avatar Studio */}
                    <p className="text-xs text-gray-400">Generate a custom AI character.</p>
                    
                    <div>
                        <label className="text-xs text-gray-500 uppercase block mb-1">Style Preset</label>
                        <div className="flex gap-2 overflow-x-auto pb-2">
                            {AVATAR_PRESETS.map((preset) => (
                                <button
                                    key={preset.label}
                                    onClick={() => setAvatarPrompt(preset.prompt)}
                                    className="text-[10px] bg-gray-800 hover:bg-gray-700 border border-gray-600 rounded px-2 py-1 whitespace-nowrap"
                                >
                                    {preset.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div>
                        <label className="text-xs text-gray-500 uppercase block mb-1">Character Description</label>
                        <textarea
                            value={avatarPrompt}
                            onChange={(e) => setAvatarPrompt(e.target.value)}
                            className="w-full bg-studio-panel text-white text-xs rounded-lg p-2 border border-gray-600 focus:outline-none h-20"
                            placeholder="Describe your character..."
                        />
                    </div>

                    <button
                        onClick={() => onGenerateAvatar && onGenerateAvatar(avatarPrompt)}
                        disabled={isGeneratingAvatar}
                        className="w-full bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white py-2 rounded-lg text-sm font-bold"
                    >
                        {isGeneratingAvatar ? 'Generating Image...' : '1. Generate Avatar Image'}
                    </button>

                    {avatarImageUrl && (
                        <div className="mt-2">
                             <div className="flex items-center gap-2 mb-2">
                                <span className="text-green-400 text-xs">✓ Image Ready</span>
                             </div>
                             <button
                                onClick={() => onGenerateVeoBackground(avatarImageUrl)}
                                disabled={isGeneratingVideo}
                                className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white py-2 rounded-lg text-sm font-bold flex items-center justify-center gap-2"
                             >
                                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
                                {isGeneratingVideo ? 'Animating...' : '2. Animate with Veo'}
                             </button>
                        </div>
                    )}
                </div>
            )}
          </div>

          {/* Caption Styles */}
          <div className="bg-studio-dark p-4 rounded-lg border border-gray-700">
            <h3 className="text-sm font-bold uppercase text-gray-500 mb-3">4. Caption Style</h3>
            <div className="space-y-3 text-sm">
                <div className="flex items-center justify-between">
                    <label className="text-gray-400 text-xs">Font</label>
                    <select
                        value={captionStyle.fontFamily}
                        onChange={(e) => onUpdateCaptionStyle({ fontFamily: e.target.value })}
                        className="bg-studio-panel text-white text-xs rounded p-1 border border-gray-600 w-32 focus:outline-none"
                    >
                        <option value="Montserrat">Montserrat</option>
                        <option value="Inter">Inter</option>
                        <option value="sans-serif">Sans Serif</option>
                        <option value="serif">Serif</option>
                        <option value="monospace">Monospace</option>
                    </select>
                </div>
                <div className="flex items-center justify-between">
                    <label className="text-gray-400 text-xs">Size ({captionStyle.fontSize}px)</label>
                    <input 
                        type="range" min="16" max="64" step="2"
                        value={captionStyle.fontSize}
                        onChange={(e) => onUpdateCaptionStyle({ fontSize: parseInt(e.target.value) })}
                        className="w-32 h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer accent-white"
                    />
                </div>
                <div className="flex items-center justify-between">
                    <label className="text-gray-400 text-xs">Text Color</label>
                    <input 
                        type="color"
                        value={captionStyle.textColor}
                        onChange={(e) => onUpdateCaptionStyle({ textColor: e.target.value })}
                        className="bg-transparent h-6 w-8 cursor-pointer rounded overflow-hidden p-0 border-0"
                    />
                </div>
                <div className="flex items-center justify-between">
                    <label className="text-gray-400 text-xs">Outline</label>
                    <div className="flex items-center gap-2">
                         <input 
                            type="number" min="0" max="10" 
                            value={captionStyle.outlineWidth}
                            onChange={(e) => onUpdateCaptionStyle({ outlineWidth: parseInt(e.target.value) })}
                             className="bg-studio-panel text-white text-xs rounded p-1 border border-gray-600 w-12 text-center"
                        />
                        <input 
                            type="color"
                            value={captionStyle.outlineColor}
                            onChange={(e) => onUpdateCaptionStyle({ outlineColor: e.target.value })}
                            className="bg-transparent h-6 w-8 cursor-pointer rounded overflow-hidden p-0 border-0"
                        />
                    </div>
                </div>
                 <div className="flex items-center justify-between">
                    <label className="text-gray-400 text-xs">Shadow</label>
                    <div className="flex items-center gap-2">
                         <input 
                            title="Blur Radius"
                            type="range" min="0" max="20" step="1"
                            value={captionStyle.shadowBlur}
                            onChange={(e) => onUpdateCaptionStyle({ shadowBlur: parseInt(e.target.value) })}
                             className="w-16 h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer accent-white"
                        />
                        <input 
                            type="color"
                            value={captionStyle.shadowColor}
                            onChange={(e) => onUpdateCaptionStyle({ shadowColor: e.target.value })}
                            className="bg-transparent h-6 w-8 cursor-pointer rounded overflow-hidden p-0 border-0"
                        />
                    </div>
                </div>
                 <div className="flex items-center justify-between">
                    <label className="text-gray-400 text-xs">Uppercase</label>
                    <input 
                        type="checkbox"
                        checked={captionStyle.isUppercase}
                        onChange={(e) => onUpdateCaptionStyle({ isUppercase: e.target.checked })}
                        className="rounded bg-studio-panel border-gray-600 text-studio-accent focus:ring-0"
                    />
                </div>
                <div className="flex items-center justify-between">
                    <label className="text-gray-400 text-xs">Y-Pos ({captionStyle.yOffset}%)</label>
                    <input 
                        type="range" min="10" max="90" step="5"
                        value={captionStyle.yOffset}
                        onChange={(e) => onUpdateCaptionStyle({ yOffset: parseInt(e.target.value) })}
                        className="w-32 h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer accent-white"
                    />
                </div>
            </div>
          </div>
          
           {audioBlob && (
            <div className="pt-4">
                 <button onClick={onNext} disabled={isGeneratingVideo} className="w-full bg-white text-black hover:bg-gray-200 font-bold py-3 rounded-lg transition-colors">
                   Finalize Metadata &rarr;
                 </button>
            </div>
           )}
        </div>

        {/* Preview Column */}
        <div className="flex justify-center">
          <div className="relative w-[280px] h-[500px] bg-black rounded-[2rem] border-4 border-gray-800 overflow-hidden shadow-2xl flex flex-col">
            <div className="relative flex-1 bg-black overflow-hidden">
                {/* Show static avatar preview if generating/present but video not ready */}
                {activeVisualTab === 'avatar' && avatarImageUrl && !videoRef.current?.src ? (
                    <img src={`data:image/png;base64,${avatarImageUrl}`} className="absolute inset-0 w-full h-full object-cover" alt="AI Avatar" />
                ) : (
                    <video
                        ref={videoRef}
                        src={finalVideoUrl}
                        className="absolute inset-0 w-full h-full object-cover"
                        loop
                        muted
                        playsInline
                        key={finalVideoUrl} 
                    />
                )}

                <div className="absolute inset-0 bg-gradient-to-b from-black/30 via-transparent to-black/60 pointer-events-none"></div>
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none w-full">
                    {currentCaption && (
                        <div className="text-center w-full px-4 absolute" style={{ bottom: `${captionStyle.yOffset}%` }}>
                            <span style={{ 
                                    fontFamily: captionStyle.fontFamily,
                                    fontSize: `${captionStyle.fontSize}px`,
                                    color: captionStyle.textColor,
                                    WebkitTextStroke: `${captionStyle.outlineWidth}px ${captionStyle.outlineColor}`,
                                    textShadow: `0px 2px ${captionStyle.shadowBlur}px ${captionStyle.shadowColor}`,
                                    textTransform: captionStyle.isUppercase ? 'uppercase' : 'none',
                                    fontWeight: 900,
                                    lineHeight: 1.2
                                }}>
                                {currentCaption.text}
                            </span>
                        </div>
                    )}
                </div>
                {!isPlaying && audioBlob && (
                    <button onClick={togglePlay} className="absolute inset-0 flex items-center justify-center bg-black/40 hover:bg-black/20 transition-colors z-10">
                        <div className="w-16 h-16 bg-white/90 rounded-full flex items-center justify-center shadow-lg">
                            <svg className="w-8 h-8 text-black ml-1" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                        </div>
                    </button>
                )}
                {!audioBlob && (
                     <div className="absolute inset-0 flex items-center justify-center bg-black/60 z-10">
                        <p className="text-gray-400 text-xs">Generate Audio to Preview</p>
                     </div>
                )}
            </div>

            {audioBlob && (
                <div className="h-14 bg-studio-panel border-t border-gray-800 flex items-center px-3 gap-3 z-20">
                    <button onClick={togglePlay} className="text-white hover:text-studio-accent transition-colors shrink-0">
                         {isPlaying ? (
                            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
                         ) : (
                            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                         )}
                    </button>
                    <div className="flex-1 flex flex-col justify-center">
                         <input
                            type="range"
                            min="0"
                            max={duration || 0}
                            step="0.1"
                            value={currentTime}
                            onChange={handleSeek}
                            className="w-full h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer accent-white hover:accent-studio-accent transition-all"
                        />
                         <div className="flex justify-between text-[10px] text-gray-400 mt-1 font-mono">
                            <span>{formatTime(currentTime)}</span>
                            <span>{formatTime(duration)}</span>
                         </div>
                    </div>
                </div>
            )}
          </div>
        </div>
      </div>

      {audioSrc && (
        <audio
            ref={audioRef}
            src={audioSrc}
            onEnded={handleAudioEnded}
            onLoadedMetadata={handleLoadedMetadata}
            className="hidden"
        />
      )}
      
      {musicUrl && (
          <audio
            ref={musicRef}
            src={musicUrl}
            loop
            className="hidden"
          />
      )}
    </div>
  );
};