import React, { useState } from 'react';
import { Metadata, CaptionStyle, ScriptData } from '../types';
import { DEFAULT_BACKGROUND_VIDEO } from '../constants';

interface Props {
  metadata: Metadata | null;
  isLoading: boolean;
  scriptData: ScriptData | null;
  audioBlob: Blob | null;
  videoUrl: string | null;
  captionStyle: CaptionStyle;
  thumbnailUrl: string | null;
  musicUrl: string | null;
  musicVolume: number;
  onGenerate: () => void;
  onGenerateThumbnail: () => void;
}

export const MetadataGenerator: React.FC<Props> = ({ 
  metadata, isLoading, scriptData, audioBlob, videoUrl, captionStyle, thumbnailUrl, musicUrl, musicVolume, onGenerate, onGenerateThumbnail
}) => {
  const [activeTab, setActiveTab] = useState<'youtube' | 'instagram'>('youtube');
  const [exportProgress, setExportProgress] = useState(0);
  const [isExporting, setIsExporting] = useState(false);

  const renderVideo = async () => {
    if (!scriptData || !audioBlob) return;
    setIsExporting(true);
    setExportProgress(0);

    try {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const width = 1080;
        const height = 1920;
        canvas.width = width;
        canvas.height = height;

        // Determine MIME type
        let mimeType = 'video/mp4';
        if (!MediaRecorder.isTypeSupported(mimeType)) {
             mimeType = 'video/webm';
        }

        // --- AUDIO MIXING SETUP ---
        const AudioContext = window.AudioContext || (window as any).webkitAudioContext;
        const audioCtx = new AudioContext();
        const dest = audioCtx.createMediaStreamDestination();

        // 1. Load Voiceover
        const voiceAudio = new Audio(URL.createObjectURL(audioBlob));
        await new Promise((resolve, reject) => {
             voiceAudio.addEventListener('loadedmetadata', resolve, { once: true });
             voiceAudio.addEventListener('error', () => reject(new Error("Failed to load voice audio")), { once: true });
        });
        const voiceSource = audioCtx.createMediaElementSource(voiceAudio);
        voiceSource.connect(dest);
        voiceSource.connect(audioCtx.destination); // Let user hear it while rendering? Optional.

        // 2. Load Music (if selected)
        let musicAudio: HTMLAudioElement | null = null;
        if (musicUrl) {
            musicAudio = new Audio(musicUrl);
            musicAudio.crossOrigin = 'anonymous';
            musicAudio.loop = true;
            await new Promise((resolve) => {
                 // Warn but don't fail if music fails (CORS etc)
                 musicAudio!.addEventListener('loadedmetadata', resolve, { once: true });
                 musicAudio!.addEventListener('error', () => { console.warn("Music load failed"); resolve(null); }, { once: true });
            });
            
            if (musicAudio) {
                const musicSource = audioCtx.createMediaElementSource(musicAudio);
                const musicGain = audioCtx.createGain();
                musicGain.gain.value = musicVolume;
                musicSource.connect(musicGain);
                musicGain.connect(dest);
                musicGain.connect(audioCtx.destination);
            }
        }

        // 3. Load Background Video
        const video = document.createElement('video');
        video.crossOrigin = 'anonymous';
        video.src = videoUrl || DEFAULT_BACKGROUND_VIDEO;
        video.muted = true;
        video.playsInline = true;
        video.loop = true;

        await new Promise((resolve, reject) => {
            video.addEventListener('loadeddata', resolve, { once: true });
            video.addEventListener('error', () => reject(new Error('Failed to load video source. If using a custom URL, ensure CORS is enabled.')), { once: true });
        });

        // 4. Recorder Setup
        const stream = canvas.captureStream(30);
        // Add the mixed audio track
        if (dest.stream.getAudioTracks().length > 0) {
            stream.addTrack(dest.stream.getAudioTracks()[0]);
        }

        const recorder = new MediaRecorder(stream, { mimeType });
        const chunks: BlobPart[] = [];
        
        recorder.ondataavailable = (e) => {
            if (e.data.size > 0) chunks.push(e.data);
        };

        recorder.onstop = () => {
            const blob = new Blob(chunks, { type: mimeType });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `reddit_shorts_final.${mimeType.includes('mp4') ? 'mp4' : 'webm'}`;
            a.click();
            
            // Cleanup
            setIsExporting(false);
            setExportProgress(0);
            audioCtx.close();
            setTimeout(() => URL.revokeObjectURL(url), 100);
        };

        recorder.start();
        
        // Start Playback
        await voiceAudio.play();
        if (musicAudio) musicAudio.play();
        await video.play();

        const draw = () => {
            if (voiceAudio.paused || voiceAudio.ended) {
                if (recorder.state === 'recording') recorder.stop();
                // Stop music if playing
                if (musicAudio) musicAudio.pause();
                return;
            }

            if (ctx) {
                // Background
                ctx.drawImage(video, 0, 0, width, height);
                
                // Dim Overlay
                ctx.fillStyle = 'rgba(0,0,0,0.3)';
                ctx.fillRect(0, 0, width, height);

                // Captions
                const currentTime = voiceAudio.currentTime;
                const currentCaption = scriptData.captions.find(
                    c => currentTime >= c.start && currentTime <= c.end
                );

                if (currentCaption) {
                    const fontSize = captionStyle.fontSize * 3; // Scale up for 1080p
                    const fontName = captionStyle.fontFamily.includes(' ') ? `"${captionStyle.fontFamily}"` : captionStyle.fontFamily;
                    const fontWeight = captionStyle.isUppercase ? '900' : '700';
                    ctx.font = `${fontWeight} ${fontSize}px ${fontName}, sans-serif`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    
                    const x = width / 2;
                    const y = height * (1 - (captionStyle.yOffset / 100));

                    // Shadow
                    ctx.shadowColor = captionStyle.shadowColor;
                    ctx.shadowBlur = captionStyle.shadowBlur * 3;
                    ctx.shadowOffsetX = 0;
                    ctx.shadowOffsetY = 4;

                    // Stroke
                    if (captionStyle.outlineWidth > 0) {
                        ctx.lineWidth = captionStyle.outlineWidth * 3;
                        ctx.strokeStyle = captionStyle.outlineColor;
                        ctx.lineJoin = 'round';
                        ctx.strokeText(captionStyle.isUppercase ? currentCaption.text.toUpperCase() : currentCaption.text, x, y);
                        // Clear shadow for fill to avoid double shadow
                        ctx.shadowColor = 'transparent';
                    }

                    // Fill
                    ctx.fillStyle = captionStyle.textColor;
                    ctx.fillText(captionStyle.isUppercase ? currentCaption.text.toUpperCase() : currentCaption.text, x, y);
                }
            }
            
            if (voiceAudio.duration > 0) {
                setExportProgress((voiceAudio.currentTime / voiceAudio.duration) * 100);
            }
            requestAnimationFrame(draw);
        };

        draw();

    } catch (e: any) {
        console.error("Export failed:", e);
        alert("Export failed: " + e.message);
        setIsExporting(false);
        setExportProgress(0);
    }
  };

  // If no metadata yet, show generation button
  if (!metadata) {
    return (
      <div className="bg-studio-panel rounded-xl p-6 border border-gray-800 text-center py-12">
        <h2 className="text-xl font-display font-bold mb-4">Final Polish</h2>
        <p className="text-gray-400 mb-6">Generate viral titles, descriptions, and hashtags tailored for your script.</p>
        <button
          onClick={onGenerate}
          disabled={isLoading}
          className="bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-bold px-8 py-3 rounded-lg transition-all"
        >
          {isLoading ? 'Thinking...' : 'Generate Metadata'}
        </button>
      </div>
    );
  }

  const CopyButton = ({ text }: { text: string }) => (
    <button 
        onClick={() => navigator.clipboard.writeText(text)}
        className="absolute top-2 right-2 text-xs bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded text-white"
    >
        Copy
    </button>
  );

  return (
    <div className="bg-studio-panel rounded-xl p-6 border border-gray-800">
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-green-600 p-2 rounded-full">
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" /></svg>
        </div>
        <h2 className="text-xl font-display font-bold">Metadata & Export</h2>
      </div>

      <div className="flex gap-4 mb-6 border-b border-gray-700">
        <button
          onClick={() => setActiveTab('youtube')}
          className={`pb-2 px-4 font-medium text-sm transition-colors ${activeTab === 'youtube' ? 'text-red-500 border-b-2 border-red-500' : 'text-gray-400'}`}
        >
          YouTube Shorts
        </button>
        <button
          onClick={() => setActiveTab('instagram')}
          className={`pb-2 px-4 font-medium text-sm transition-colors ${activeTab === 'instagram' ? 'text-pink-500 border-b-2 border-pink-500' : 'text-gray-400'}`}
        >
          Instagram Reels
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Metadata Text Column */}
        <div className="space-y-6">
          {activeTab === 'youtube' && (
            <div className="space-y-4 animate-fade-in">
              <div className="relative group">
                  <label className="block text-xs text-gray-500 uppercase mb-1">Video Title</label>
                  <div className="bg-studio-dark p-3 rounded-lg border border-gray-700 text-white">{metadata.youtubeTitle}</div>
                  <CopyButton text={metadata.youtubeTitle} />
              </div>
              <div className="relative group">
                  <label className="block text-xs text-gray-500 uppercase mb-1">Description</label>
                  <div className="bg-studio-dark p-3 rounded-lg border border-gray-700 text-white whitespace-pre-wrap">{metadata.youtubeDescription}</div>
                  <CopyButton text={metadata.youtubeDescription} />
              </div>
              <div className="relative group">
                  <label className="block text-xs text-gray-500 uppercase mb-1">Tags</label>
                  <div className="bg-studio-dark p-3 rounded-lg border border-gray-700 text-blue-400 text-sm">{metadata.youtubeTags.join(', ')}</div>
                  <CopyButton text={metadata.youtubeTags.join(', ')} />
              </div>
            </div>
          )}

          {activeTab === 'instagram' && (
            <div className="space-y-4 animate-fade-in">
              <div className="relative group">
                  <label className="block text-xs text-gray-500 uppercase mb-1">Caption</label>
                  <div className="bg-studio-dark p-3 rounded-lg border border-gray-700 text-white whitespace-pre-wrap">{metadata.instagramCaption}</div>
                  <CopyButton text={metadata.instagramCaption} />
              </div>
              <div className="relative group">
                  <label className="block text-xs text-gray-500 uppercase mb-1">Hashtags</label>
                  <div className="bg-studio-dark p-3 rounded-lg border border-gray-700 text-blue-400 text-sm">{metadata.instagramHashtags.join(' ')}</div>
                  <CopyButton text={metadata.instagramHashtags.join(' ')} />
              </div>
            </div>
          )}
        </div>
        
        {/* Thumbnail & Export Column */}
        <div className="space-y-6">
            <div className="bg-studio-dark p-4 rounded-lg border border-gray-700">
                <h3 className="text-sm font-bold uppercase text-gray-500 mb-3">Thumbnail / Cover Art</h3>
                
                {thumbnailUrl ? (
                    <div className="space-y-3">
                        <img src={thumbnailUrl} alt="Generated Thumbnail" className="w-full h-auto rounded-lg shadow-lg border border-gray-600" />
                        <div className="flex gap-2">
                             <a 
                                href={thumbnailUrl} 
                                download="thumbnail.png"
                                className="flex-1 bg-gray-700 hover:bg-gray-600 text-white text-xs font-bold py-2 rounded text-center transition-colors"
                             >
                                Download Image
                             </a>
                             <button
                                onClick={onGenerateThumbnail}
                                disabled={isLoading}
                                className="bg-gray-800 hover:bg-gray-700 text-gray-300 text-xs py-2 px-3 rounded"
                             >
                                Regenerate
                             </button>
                        </div>
                    </div>
                ) : (
                    <div className="text-center py-8 border-2 border-dashed border-gray-700 rounded-lg">
                        <p className="text-gray-400 text-sm mb-4">Generate a clickbait-style viral thumbnail.</p>
                        <button
                            onClick={onGenerateThumbnail}
                            disabled={isLoading}
                            className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-bold px-4 py-2 rounded text-sm transition-colors"
                        >
                            {isLoading ? 'Generating Image...' : 'Generate AI Thumbnail'}
                        </button>
                    </div>
                )}
            </div>

            <div className="bg-studio-dark p-4 rounded-lg border border-gray-700">
                 <h3 className="text-sm font-bold uppercase text-gray-500 mb-3">Final Video</h3>
                 <p className="text-xs text-gray-500 mb-4">Render audio, video, and captions into a single MP4.</p>
                 
                 {isExporting && (
                     <div className="w-full bg-gray-700 rounded-full h-2 mb-3 overflow-hidden">
                        <div className="bg-green-500 h-2 rounded-full transition-all duration-300" style={{ width: `${exportProgress}%` }}></div>
                     </div>
                 )}

                 <button 
                    onClick={renderVideo}
                    disabled={isExporting}
                    className="w-full bg-white text-black font-bold px-6 py-3 rounded-lg hover:bg-gray-200 disabled:opacity-50"
                >
                    {isExporting ? `Rendering ${Math.round(exportProgress)}%` : 'Export Final Video'}
                </button>
            </div>
        </div>
      </div>
    </div>
  );
};