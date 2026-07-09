import React, { useState, useEffect, useRef } from 'react';
import { GeneratedScript, ScriptSection } from '../types';
import { Play, Pause, Download, Volume2, VolumeX, AlertCircle } from 'lucide-react';

interface VideoPreviewProps {
  script: GeneratedScript | null;
  isProcessing: boolean;
  error?: string | null;
}

export const VideoPreview: React.FC<VideoPreviewProps> = ({ script, isProcessing, error }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [currentSection, setCurrentSection] = useState<ScriptSection | null>(null);
  const [progress, setProgress] = useState(0);
  const duration = script ? script.estimatedDuration : 30; // default 30s
  
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    // Reset when script ID changes (new generation)
    // Edits to the same script (same ID) will not trigger this reset
    setCurrentTime(0);
    setIsPlaying(false);
    setProgress(0);
    if (script && script.sections.length > 0) {
        setCurrentSection(script.sections[0]);
    } else {
        setCurrentSection(null);
    }
  }, [script?.id]);

  useEffect(() => {
    if (isPlaying) {
      timerRef.current = window.setInterval(() => {
        setCurrentTime((prev) => {
          if (prev >= duration) {
            setIsPlaying(false);
            return 0;
          }
          return prev + 0.1;
        });
      }, 100);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [isPlaying, duration]);

  useEffect(() => {
    setProgress((currentTime / duration) * 100);
    
    if (!script || !script.sections.length) {
        return;
    }

    // Determine current section based on time distribution
    const totalChars = script.fullText.length;
    let charAccumulator = 0;
    let foundSection = false;

    for (const section of script.sections) {
        const sectionLen = section.content.length;
        const sectionRatio = sectionLen / totalChars;
        const sectionDuration = sectionRatio * duration;
        
        // Calculate start time for this section based on accum characters
        const startTime = (charAccumulator / totalChars) * duration;
        const endTime = startTime + sectionDuration;
        
        if (currentTime >= startTime && currentTime < endTime) {
            setCurrentSection(section);
            foundSection = true;
            break;
        }
        charAccumulator += sectionLen;
    }

    if (!foundSection && currentTime > 0) {
        // If we are at the very end, show the last one
         setCurrentSection(script.sections[script.sections.length-1]);
    } else if (currentTime === 0 && script.sections.length > 0) {
        setCurrentSection(script.sections[0]);
    }
    
  }, [currentTime, duration, script]);

  // Color logic based on section type
  const getCaptionColor = (type: string | undefined) => {
      switch (type) {
          case 'hook': return 'text-red-500 font-black'; // The Jhatka
          case 'authority': return 'text-yellow-400 font-bold'; // The Wisdom (Hindi)
          case 'cta': return 'text-green-400 font-bold'; // The CTA
          default: return 'text-white font-bold'; // Modern Breakdown
      }
  };

  const getCaptionSize = (type: string | undefined) => {
      if (type === 'hook') return 'text-3xl md:text-4xl';
      return 'text-xl md:text-2xl';
  };

  return (
    <div className="flex flex-col items-center w-full max-w-sm mx-auto">
      <div className="relative w-full aspect-[9/16] bg-black rounded-2xl overflow-hidden shadow-2xl border border-slate-800 group">
        
        {/* Background Layer / State Layer */}
        {isProcessing ? (
          <div className="absolute inset-0 flex items-center justify-center bg-slate-900 z-20">
             <div className="flex flex-col items-center gap-4">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-orange-500"></div>
                <p className="text-slate-400 text-sm animate-pulse">Forging Viral Script...</p>
             </div>
          </div>
        ) : error ? (
           <div className="absolute inset-0 flex items-center justify-center bg-slate-900 z-20 p-6 text-center">
             <div className="flex flex-col items-center gap-3">
                <AlertCircle size={32} className="text-red-500" />
                <p className="text-red-400 font-medium text-sm">{error}</p>
             </div>
          </div>
        ) : (
          <img 
            src="https://picsum.photos/1080/1920?grayscale"
            alt="Background" 
            className="absolute inset-0 w-full h-full object-cover opacity-60 transition-transform duration-[20s] ease-linear scale-110"
            style={{ transform: isPlaying ? 'scale(1.2)' : 'scale(1.0)' }}
          />
        )}

        {/* Overlay Gradient */}
        {!isProcessing && !error && (
            <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-transparent to-black/80 z-10 pointer-events-none"></div>
        )}

        {/* Captions Layer */}
        {!isProcessing && !error && (
            <div className="absolute inset-0 flex items-center justify-center p-8 z-20 pointer-events-none">
            <div className="text-center">
                {currentSection ? (
                    <p className={`${getCaptionColor(currentSection.type)} ${getCaptionSize(currentSection.type)} uppercase tracking-wider drop-shadow-[0_4px_4px_rgba(0,0,0,0.9)] leading-tight`}>
                    {currentSection.content}
                </p>
                ) : (
                    <p className="text-slate-400 text-sm">{script ? "Ready to play" : "Waiting for script..."}</p>
                )}
            </div>
            </div>
        )}

        {/* UI Controls Overlay (Hover) */}
        {!isProcessing && !error && (
            <div className="absolute inset-0 z-30 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-between p-4">
                <div className="flex justify-between items-center">
                    <div className="bg-black/50 px-2 py-1 rounded text-xs text-white">9:16 HD</div>
                    <button className="p-2 bg-black/50 rounded-full text-white hover:bg-orange-600">
                        <Volume2 size={16} />
                    </button>
                </div>
                
                <div className="flex justify-center">
                    <button 
                        onClick={() => setIsPlaying(!isPlaying)}
                        className="w-16 h-16 bg-orange-600/90 rounded-full flex items-center justify-center text-white hover:bg-orange-500 backdrop-blur-sm transition-transform hover:scale-105"
                    >
                        {isPlaying ? <Pause size={32} fill="currentColor" /> : <Play size={32} fill="currentColor" className="ml-1" />}
                    </button>
                </div>

                <div className="space-y-2">
                    <div className="flex justify-between text-xs text-slate-300 font-mono">
                        <span>{currentTime.toFixed(1)}s</span>
                        <span>{duration}s</span>
                    </div>
                    {/* Progress Bar */}
                    <div className="w-full h-1 bg-slate-700 rounded-full overflow-hidden">
                        <div 
                            className="h-full bg-orange-500 transition-all duration-100 ease-linear"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                </div>
            </div>
        )}
      </div>

      {/* Export Actions */}
      <div className="mt-6 flex gap-4 w-full">
        <button 
          disabled={!script || isProcessing || !!error}
          className="flex-1 flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-white py-3 rounded-xl transition-colors font-medium border border-slate-700"
        >
            <Download size={18} />
            Export MP4
        </button>
      </div>
    </div>
  );
};