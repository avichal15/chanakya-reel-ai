import React, { useState } from 'react';
import { ApiKeyModal } from './components/ApiKeyModal';
import { RedditInput } from './components/RedditInput';
import { ScriptGenerator } from './components/ScriptGenerator';
import { VideoStudio } from './components/VideoStudio';
import { MetadataGenerator } from './components/MetadataGenerator';
import { analyzePost, generateScript, generateSpeech, generateVeoBackground, generateMetadata, generateThumbnail, generateAvatar } from './services/gemini';
import { AppState, RedditPost, Step, ScriptData, CaptionStyle } from './types';
import { DEFAULT_CAPTION_STYLE } from './constants';

function App() {
  const [state, setState] = useState<AppState>({
    // Automatically use the API key from the backend environment if available
    apiKey: (process as any).env.GEMINI_API_KEY || null,
    post: null,
    script: null,
    audioBlob: null,
    audioUrl: null,
    backgroundVideoUrl: null,
    thumbnailUrl: null,
    metadata: null,
    captionStyle: DEFAULT_CAPTION_STYLE,
    avatarImageUrl: null,
    musicUrl: null,
    musicVolume: 0.15, // Default 15% volume
    isProcessing: false,
    statusMessage: '',
  });

  const [currentStep, setCurrentStep] = useState<Step>(Step.INPUT);

  const handleSetApiKey = (key: string) => {
    setState(prev => ({ ...prev, apiKey: key }));
  };

  const handleError = (error: any) => {
    console.error(error);
    alert(`Error: ${error.message || "Unknown error occurred"}`);
    setState(prev => ({ ...prev, isProcessing: false, statusMessage: '' }));
  };

  // Step 1: Analyze Input
  const handleAnalyze = async (input: string) => {
    if (!state.apiKey) return;
    setState(prev => ({ ...prev, isProcessing: true, statusMessage: 'Analyzing Reddit content...' }));
    try {
      const post = await analyzePost(state.apiKey, input);
      setState(prev => ({ ...prev, post, isProcessing: false }));
      setCurrentStep(Step.SCRIPT);
    } catch (e) {
      handleError(e);
    }
  };

  // Step 2: Generate Script
  const handleGenerateScript = async () => {
    if (!state.apiKey || !state.post) return;
    setState(prev => ({ ...prev, isProcessing: true, statusMessage: 'Writing viral script (Thinking)...' }));
    try {
      const script = await generateScript(state.apiKey, state.post);
      setState(prev => ({ ...prev, script, isProcessing: false }));
    } catch (e) {
      handleError(e);
    }
  };

  // Measure real duration of the generated voiceover
  const getAudioDuration = (blob: Blob): Promise<number | null> =>
    new Promise((resolve) => {
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audio.addEventListener('loadedmetadata', () => {
        URL.revokeObjectURL(url);
        resolve(isFinite(audio.duration) ? audio.duration : null);
      }, { once: true });
      audio.addEventListener('error', () => { URL.revokeObjectURL(url); resolve(null); }, { once: true });
    });

  // Step 3: Generate Audio
  const handleGenerateAudio = async (voiceId: string) => {
    if (!state.apiKey || !state.script) return;
    setState(prev => ({ ...prev, isProcessing: true, statusMessage: 'Synthesizing voiceover...' }));
    try {
      const blob = await generateSpeech(state.apiKey, state.script.fullScript, voiceId);
      // The LLM only estimates caption timings; stretch them to match the real audio
      const actualDuration = await getAudioDuration(blob);
      setState(prev => {
        let script = prev.script;
        if (script && actualDuration && script.captions.length > 0) {
          const estimatedEnd = script.captions[script.captions.length - 1].end;
          if (estimatedEnd > 0) {
            const scale = actualDuration / estimatedEnd;
            script = {
              ...script,
              captions: script.captions.map(c => ({ ...c, start: c.start * scale, end: c.end * scale })),
            };
          }
        }
        return { ...prev, script, audioBlob: blob, isProcessing: false };
      });
    } catch (e) {
      handleError(e);
    }
  };

  // Step 3.5: Generate Veo Video
  const handleGenerateVeo = async (imageBase64?: string) => {
    if (!state.apiKey || !state.post) return;
    setState(prev => ({ ...prev, isProcessing: true, statusMessage: 'Generating Veo video (this takes time)...' }));
    try {
      const prompt = imageBase64 
        ? `Animate this image. Abstract representation of: ${state.post.title}` 
        : `Abstract representation of: ${state.post.title}`;
        
      const url = await generateVeoBackground(state.apiKey, prompt, imageBase64);
      setState(prev => ({ ...prev, backgroundVideoUrl: url, isProcessing: false }));
    } catch (e) {
      handleError(e);
    }
  };

  // Step 3.6: Generate Avatar
  const handleGenerateAvatar = async (prompt: string) => {
    if (!state.apiKey) return;
    setState(prev => ({ ...prev, isProcessing: true, statusMessage: 'Generating Avatar character...' }));
    try {
        const base64 = await generateAvatar(state.apiKey, prompt);
        setState(prev => ({ ...prev, avatarImageUrl: base64, isProcessing: false }));
    } catch (e) {
        handleError(e);
    }
  };

  // Helper for manual background set
  const handleSetBackgroundVideo = (url: string) => {
    setState(prev => ({ ...prev, backgroundVideoUrl: url }));
  };
  
  // Helper for updating caption style
  const handleUpdateCaptionStyle = (style: Partial<CaptionStyle>) => {
    setState(prev => ({ ...prev, captionStyle: { ...prev.captionStyle, ...style } }));
  };

  // Music handlers
  const handleSetMusic = (url: string) => {
    setState(prev => ({ ...prev, musicUrl: url }));
  };
  
  const handleSetMusicVolume = (volume: number) => {
    setState(prev => ({ ...prev, musicVolume: volume }));
  };

  // Step 4: Metadata
  const handleGenerateMetadata = async () => {
    if (!state.apiKey || !state.post || !state.script) return;
    setState(prev => ({ ...prev, isProcessing: true, statusMessage: 'Creating social metadata...' }));
    try {
      const metadata = await generateMetadata(state.apiKey, state.post, state.script.fullScript);
      setState(prev => ({ ...prev, metadata, isProcessing: false }));
    } catch (e) {
      handleError(e);
    }
  };

  // Step 4.5: Generate Thumbnail
  const handleGenerateThumbnail = async () => {
    if (!state.apiKey || !state.script) return;
    setState(prev => ({ ...prev, isProcessing: true, statusMessage: 'Generating viral thumbnail...' }));
    try {
      const url = await generateThumbnail(state.apiKey, state.script.fullScript.substring(0, 300));
      setState(prev => ({ ...prev, thumbnailUrl: url, isProcessing: false }));
    } catch (e) {
      handleError(e);
    }
  };

  if (!state.apiKey) {
    return <ApiKeyModal onSave={handleSetApiKey} />;
  }

  return (
    <div className="min-h-screen bg-studio-dark text-white p-4 md:p-8 font-sans">
      <header className="max-w-5xl mx-auto mb-8 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-red-600 rounded-lg flex items-center justify-center shadow-lg">
             <span className="text-2xl font-bold">S</span>
          </div>
          <h1 className="text-2xl font-display font-bold tracking-tight">Reddit Shorts <span className="text-studio-accent">Studio</span></h1>
        </div>
        {state.isProcessing && (
          <div className="flex items-center gap-2 bg-studio-panel px-4 py-2 rounded-full border border-studio-accent/30 animate-pulse">
            <div className="w-2 h-2 bg-studio-accent rounded-full"></div>
            <span className="text-sm font-medium text-studio-accent">{state.statusMessage}</span>
          </div>
        )}
      </header>

      <main className="max-w-5xl mx-auto space-y-8 pb-20">
        
        {/* Step 1: Input */}
        <div className={currentStep === Step.INPUT ? 'block' : 'hidden'}>
           <RedditInput 
            onAnalyze={handleAnalyze} 
            isLoading={state.isProcessing} 
            apiKey={state.apiKey}
          />
        </div>

        {/* Step 2: Script */}
        {currentStep >= Step.SCRIPT && state.post && (
          <div className={currentStep === Step.SCRIPT ? 'block' : 'hidden'}>
            <ScriptGenerator 
              post={state.post} 
              script={state.script} 
              isLoading={state.isProcessing}
              onGenerate={handleGenerateScript}
              onUpdateScript={(text) => setState(prev => prev.script ? ({...prev, script: {...prev.script!, fullScript: text}}) : prev)}
              onNext={() => setCurrentStep(Step.VOICE_VIDEO)}
            />
          </div>
        )}

        {/* Step 3: Studio */}
        {currentStep >= Step.VOICE_VIDEO && state.script && (
          <div className={currentStep === Step.VOICE_VIDEO ? 'block' : 'hidden'}>
            <VideoStudio 
              script={state.script}
              audioBlob={state.audioBlob}
              backgroundVideoUrl={state.backgroundVideoUrl}
              captionStyle={state.captionStyle}
              avatarImageUrl={state.avatarImageUrl}
              musicUrl={state.musicUrl}
              musicVolume={state.musicVolume}
              isGeneratingAudio={state.isProcessing && state.statusMessage.includes('voice')}
              isGeneratingVideo={state.isProcessing && state.statusMessage.includes('Veo')}
              isGeneratingAvatar={state.isProcessing && state.statusMessage.includes('Avatar')}
              onGenerateAudio={handleGenerateAudio}
              onGenerateVeoBackground={handleGenerateVeo}
              onGenerateAvatar={handleGenerateAvatar}
              onSetBackgroundVideo={handleSetBackgroundVideo}
              onUpdateCaptionStyle={handleUpdateCaptionStyle}
              onSetMusic={handleSetMusic}
              onSetMusicVolume={handleSetMusicVolume}
              onNext={() => setCurrentStep(Step.METADATA)}
            />
          </div>
        )}

        {/* Step 4: Metadata */}
        {currentStep === Step.METADATA && (
          <MetadataGenerator 
            metadata={state.metadata}
            isLoading={state.isProcessing}
            scriptData={state.script}
            audioBlob={state.audioBlob}
            videoUrl={state.backgroundVideoUrl || ''} 
            captionStyle={state.captionStyle}
            thumbnailUrl={state.thumbnailUrl}
            musicUrl={state.musicUrl}
            musicVolume={state.musicVolume}
            onGenerate={handleGenerateMetadata}
            onGenerateThumbnail={handleGenerateThumbnail}
          />
        )}
      </main>
    </div>
  );
}

export default App;