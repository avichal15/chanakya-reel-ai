import React, { useState, useEffect, useCallback } from 'react';
import { Wand2, FileText, Music, LayoutTemplate, AlertCircle, CheckCircle2, RefreshCw, Video, Download, Copy, Hash, Upload, X, Trash2 } from 'lucide-react';
import { GeneratedScript, Tone, MOCK_VOICES } from '../types';
import { generateScript, generateVoice, generateVideo, generateCaption, uploadBackground, uploadAudio, getUploadedVideos, getUploadedAudio, deleteUploadedVideo, deleteUploadedAudio } from '../services/api';
import { VideoPreview } from '../components/VideoPreview';

interface StudioProps {
  initialQuote?: string;
}

export const Studio: React.FC<StudioProps> = ({ initialQuote }) => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // State for the project
  const [quoteText, setQuoteText] = useState("");
  const [rageLevel, setRageLevel] = useState(7);
  const [tone, setTone] = useState<Tone>(Tone.CONTROVERSIAL);
  const [script, setScript] = useState<GeneratedScript | null>(null);
  const [selectedVoice, setSelectedVoice] = useState(MOCK_VOICES[0].id);

  // Output States
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [audioPath, setAudioPath] = useState<string | null>(null); // Backend path
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [captionData, setCaptionData] = useState<any>(null); // New Caption State

  // Upload States
  const [bgVideos, setBgVideos] = useState<any[]>([]); // Array of selected background videos
  const [loopVideo, setLoopVideo] = useState(true); // Loop toggle
  const [bgMusic, setBgMusic] = useState<any | null>(null); // Background music (mixed under voiceover)
  const [bgMusicVolume, setBgMusicVolume] = useState(0.15); // 0 to 1 (default 15%)

  // Saved uploads (media library)
  const [savedVideos, setSavedVideos] = useState<any[]>([]);
  const [savedAudio, setSavedAudio] = useState<any[]>([]);

  // Render Settings
  const [captionSize, setCaptionSize] = useState<string>("Medium");
  const [useSmartSfx, setUseSmartSfx] = useState(true);
  const [useAutoBRoll, setUseAutoBRoll] = useState(false);

  // Fetch voices from backend
  const [voices, setVoices] = useState<any[]>(MOCK_VOICES);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/voices')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data) && data.length > 0) {
          // Enhance backend data with UI props if needed, or map
          const mapped = data.map(v => ({
            id: v.id,
            name: v.name,
            gender: 'Male', // Backend doesn't send gender yet, default to M
            category: 'Narration'
          }));
          setVoices(mapped);
          if (mapped.length > 0) setSelectedVoice(mapped[0].id);
        }
      })
      .catch(err => console.error("Failed to fetch voices:", err));
  }, []);

  // Define generation logic
  const executeGeneration = useCallback(async (text: string, rLevel: number, tStrategy: Tone) => {
    if (!text) return;
    setLoading(true);
    setError(null);
    try {
      const generated = await generateScript(text, "Chanakya", rLevel);
      if (generated.error) throw new Error(generated.error);

      setScript(generated);
      setStep(2);
    } catch (err: any) {
      setError(err.message || "Failed to generate script");
    } finally {
      setLoading(false);
    }
  }, []);

  const handleVoiceGeneration = async () => {
    if (!script) return;
    setLoading(true);
    setError(null);
    try {
      const res = await generateVoice(script.fullText, selectedVoice);
      setAudioUrl(res.url); // /assets/file.mp3
      setAudioPath(res.audio_path);
    } catch (err: any) {
      setError(err.message || "Voice generation failed");
    } finally {
      setLoading(false);
    }
  };

  const handleRenderVideo = async () => {
    if (!script || !audioPath) return;
    setLoading(true);
    setError(null);
    setVideoUrl(null); // Clear previous

    try {
      const res = await generateVideo(
        script,
        audioPath,
        undefined, // Removed visual theme background
        bgVideos.map(v => v.background_path), // bgVideoPaths
        bgMusic?.audio_path,
        bgMusic ? bgMusicVolume : undefined,
        captionSize, // Pass selected caption size
        useSmartSfx, // Pass SFX toggle
        useAutoBRoll // Pass Auto B-Roll toggle
      );
      setVideoUrl(res.url); // /output/file.mp4
    } catch (err: any) {
      setError(err.message || "Video rendering failed");
    } finally {
      setLoading(false);
    }
  };

  // Fetch saved uploads when entering Step 3
  useEffect(() => {
    if (step === 3) {
      getUploadedVideos().then(setSavedVideos).catch(() => { });
      getUploadedAudio().then(setSavedAudio).catch(() => { });
    }
  }, [step]);

  const handleCaptionGeneration = async () => {
    if (!script) return;
    setLoading(true);
    setError(null);
    try {
      const res = await generateCaption({
        philosopher_name: "Chanakya",
        quote_text: quoteText,
        script_text: script.fullText,
        theme: "Harsh Truths",
        rage_level: rageLevel,
        audience_type: "General"
      });
      setCaptionData(res);
    } catch (err: any) {
      setError(err.message || "Caption generation failed");
    } finally {
      setLoading(false);
    }
  };


  // Pre-fill quote and auto-generate if coming from Library
  useEffect(() => {
    if (initialQuote) {
      setQuoteText(initialQuote);
      setStep(1);
      setScript(null);
      // Auto-trigger generation with current (default) settings
      executeGeneration(initialQuote, 7, Tone.CONTROVERSIAL);
    }
  }, [initialQuote, executeGeneration]);

  const handleManualGenerate = () => {
    executeGeneration(quoteText, rageLevel, tone);
  };

  const handleScriptChange = (index: number, newContent: string) => {
    if (!script) return;
    const newSections = [...script.sections];
    // Simple duration estimate update
    const newDuration = Math.ceil(newContent.split(' ').length / 2.5); // approx 2.5 words/sec

    newSections[index] = {
      ...newSections[index],
      content: newContent,
      durationEstimate: newDuration
    };

    const newFullText = newSections.map(s => s.content).join(" ");
    const totalDuration = Math.max(newSections.reduce((acc, curr) => acc + curr.durationEstimate, 0), 15);

    setScript({
      ...script,
      sections: newSections,
      fullText: newFullText,
      estimatedDuration: totalDuration
    });
  };

  const steps = [
    { num: 1, label: 'Input Quote' },
    { num: 2, label: 'Review Script' },
    { num: 3, label: 'Visualize & Render' },
  ];

  return (
    <div className="h-full flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-500">

      {/* Stepper */}
      <div className="mb-8 flex items-center justify-center">
        {steps.map((s, idx) => (
          <div key={s.num} className="flex items-center">
            <div className={`flex items-center justify-center w-10 h-10 rounded-full font-bold border-2 transition-colors ${step >= s.num
              ? 'bg-orange-600 border-orange-600 text-white'
              : 'bg-slate-900 border-slate-700 text-slate-500'
              }`}>
              {step > s.num ? <CheckCircle2 size={20} /> : s.num}
            </div>
            <span className={`ml-3 mr-6 font-medium ${step >= s.num ? 'text-white' : 'text-slate-600'}`}>
              {s.label}
            </span>
            {idx < steps.length - 1 && (
              <div className={`w-12 h-1 rounded mr-6 ${step > s.num ? 'bg-orange-600' : 'bg-slate-800'}`} />
            )}
          </div>
        ))}
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-8 min-h-0">

        {/* LEFT COLUMN: Controls */}
        <div className="flex flex-col gap-6 overflow-y-auto pr-2 custom-scrollbar">

          {step === 1 && (
            <div className="space-y-6 bg-slate-900/50 p-6 rounded-2xl border border-slate-800">
              <div>
                <label className="block text-slate-300 font-medium mb-2">Enter Chanakya Neeti Quote</label>
                <textarea
                  value={quoteText}
                  onChange={(e) => setQuoteText(e.target.value)}
                  placeholder="e.g., A man is great by deeds, not by birth."
                  className="w-full h-32 bg-slate-950 border border-slate-700 rounded-xl p-4 text-white placeholder:text-slate-600 focus:ring-2 focus:ring-orange-500 focus:outline-none resize-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-slate-300 font-medium mb-2">Rage / Controversy Level</label>
                  <div className="flex items-center gap-4">
                    <input
                      type="range"
                      min="1" max="10"
                      value={rageLevel}
                      onChange={(e) => setRageLevel(Number(e.target.value))}
                      className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-orange-500"
                    />
                    <span className="text-xl font-bold text-orange-500 w-8">{rageLevel}</span>
                  </div>
                  <p className="text-xs text-slate-500 mt-2">Higher levels use more aggressive and provoking language.</p>
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-2">Tone Strategy</label>
                  <select
                    value={tone}
                    onChange={(e) => setTone(e.target.value as Tone)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-white focus:ring-2 focus:ring-orange-500 outline-none"
                  >
                    {Object.values(Tone).map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>
              </div>

              {error && (
                <div className="bg-red-500/10 border border-red-500/50 text-red-500 p-4 rounded-xl flex items-center gap-3">
                  <AlertCircle size={20} />
                  <span>{error}</span>
                </div>
              )}

              <button
                onClick={handleManualGenerate}
                disabled={loading || !quoteText}
                className="w-full bg-orange-600 hover:bg-orange-500 disabled:opacity-50 text-white font-bold py-4 rounded-xl flex items-center justify-center gap-3 transition-all"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                    Generating Magic...
                  </>
                ) : (
                  <>
                    <Wand2 size={20} />
                    Generate Viral Script
                  </>
                )}
              </button>
            </div>
          )}

          {step >= 2 && script && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
              <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <FileText size={18} className="text-orange-500" />
                    Generated Script
                  </h3>
                  <div className="flex gap-2">
                    <button
                      onClick={() => executeGeneration(quoteText, rageLevel, tone)}
                      disabled={loading}
                      className="text-xs bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-lg text-slate-300 transition-colors flex items-center gap-1"
                    >
                      <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
                      Regenerate
                    </button>
                  </div>
                </div>

                <div className="space-y-4">
                  {script.sections?.map((sec, idx) => (
                    <div key={idx} className="group relative pl-4 border-l-2 border-slate-700 hover:border-orange-500 transition-colors py-1">
                      <span className="text-xs uppercase tracking-wider text-slate-500 font-bold mb-1 block flex justify-between">
                        {sec.type}
                        <span className="opacity-0 group-hover:opacity-100 transition-opacity text-[10px] text-orange-500 font-normal">Editing</span>
                      </span>
                      <textarea
                        value={sec.content}
                        onChange={(e) => handleScriptChange(idx, e.target.value)}
                        className="w-full bg-transparent text-slate-200 leading-relaxed focus:outline-none focus:ring-1 focus:ring-orange-500/50 rounded p-2 -ml-2 resize-none transition-all hover:bg-slate-800/30 focus:bg-slate-950"
                        rows={Math.max(2, Math.ceil(sec.content.length / 50))}
                      />
                    </div>
                  ))}
                </div>
                <p className="text-xs text-slate-500 mt-4 italic text-center">Tip: Edit text above to update the preview instantly.</p>
              </div>

              {step === 2 && (
                <button
                  onClick={() => setStep(3)}
                  className="w-full bg-slate-800 hover:bg-slate-700 text-white font-bold py-4 rounded-xl flex items-center justify-center gap-3 border border-slate-700"
                >
                  <LayoutTemplate size={20} />
                  Proceed to Visuals
                </button>
              )}
            </div>
          )}

          {step === 3 && (
            <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 space-y-6">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Music size={18} className="text-orange-500" />
                Production Settings
              </h3>

              <div>
                {useAutoBRoll ? (
                  <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-xl p-6 text-center mb-6">
                    <Video className="w-8 h-8 text-indigo-400 mx-auto mb-2" />
                    <h4 className="text-sm font-bold text-indigo-300">Auto B-Roll is Active</h4>
                    <p className="text-xs text-slate-400 mt-1">Manual background video uploads are disabled while AI fetches stock footage.</p>
                  </div>
                ) : (
                  <>
                    <label className="block text-slate-300 font-medium mb-3 flex justify-between items-center">
                      Background Video
                      {bgVideos.length > 0 && <span className="text-xs text-orange-500 font-bold uppercase">Custom Video(s) Active</span>}
                    </label>

                    {/* Selected Videos List (Sequence) */}
                    {bgVideos.length > 0 && (
                      <div className="space-y-2 mb-4 bg-slate-950 p-3 rounded-xl border border-orange-500/30">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-xs text-orange-500 font-bold uppercase tracking-wider">Sequence ({bgVideos.length})</span>
                          <label className="flex items-center gap-2 cursor-pointer select-none">
                            <input
                              type="checkbox"
                              checked={loopVideo}
                              onChange={e => setLoopVideo(e.target.checked)}
                              className="w-3 h-3 text-orange-600 rounded focus:ring-orange-500 bg-slate-800 border-slate-700"
                            />
                            <span className="text-xs text-slate-400">Loop Sequence</span>
                          </label>
                        </div>
                        <div className="space-y-1 max-h-40 overflow-y-auto custom-scrollbar">
                          {bgVideos.map((v, idx) => (
                            <div key={`${v.filename}-${idx}`} className="flex items-center justify-between bg-slate-900 p-2 rounded border border-slate-800">
                              <div className="flex items-center gap-2 truncate">
                                <span className="text-xs text-slate-500 font-mono w-4">{idx + 1}.</span>
                                <Video size={14} className="text-orange-500 flex-shrink-0" />
                                <span className="text-xs text-slate-300 truncate" title={v.filename}>{v.filename.replace(/^[a-f0-9-]+_/, '')}</span>
                              </div>
                              <button onClick={() => setBgVideos(bgVideos.filter((_, i) => i !== idx))} className="text-slate-600 hover:text-red-500 p-1 transition-colors">
                                <X size={14} />
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
                      {/* Upload Area - Always visible to allow adding more */}
                      <label className="flex flex-col items-center justify-center h-20 border-2 border-dashed border-slate-700 rounded-lg cursor-pointer hover:border-orange-500 hover:bg-slate-900 transition-all group mb-3">
                        <div className="flex flex-col items-center justify-center pt-2 pb-2">
                          <Upload className="w-5 h-5 text-slate-500 group-hover:text-orange-500 mb-1" />
                          <p className="text-xs text-slate-500 group-hover:text-slate-300 font-medium">Add Video (MP4)</p>
                        </div>
                        <input
                          type="file"
                          className="hidden"
                          accept="video/*"
                          onChange={async (e) => {
                            const file = e.target.files?.[0];
                            if (file) {
                              setLoading(true);
                              try {
                                const res = await uploadBackground(file);
                                setBgVideos([...bgVideos, res]); // Append
                                // Refresh saved list
                                getUploadedVideos().then(setSavedVideos).catch(() => { });
                              } catch (err) {
                                console.error(err);
                                setError("Failed to upload video");
                              } finally {
                                setLoading(false);
                              }
                            }
                          }}
                        />
                      </label>

                      {/* Previous Uploads (Library) */}
                      {savedVideos.length > 0 && (
                        <div className="space-y-1">
                          <p className="text-xs text-slate-500 uppercase tracking-wider mb-2">From Library</p>
                          <div className="max-h-40 overflow-y-auto space-y-1 pr-1 custom-scrollbar">
                            {savedVideos.map(v => (
                              <div
                                key={v.filename}
                                onClick={() => { setBgVideos([...bgVideos, v]); }}
                                className="w-full flex items-center justify-between p-2 rounded-lg border border-slate-800 bg-slate-900/50 text-slate-400 hover:border-slate-600 hover:text-slate-200 transition-all text-xs cursor-pointer group"
                              >
                                <div className="truncate flex items-center gap-2">
                                  <Video size={14} className="group-hover:text-orange-500 transition-colors" />
                                  <span className="truncate" title={v.filename.replace(/^[a-f0-9-]+_/, '')}>{v.filename.replace(/^[a-f0-9-]+_/, '')}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <span className="text-[10px] text-orange-500 opacity-0 group-hover:opacity-100 uppercase font-bold shrink-0">+ Add</span>
                                  <button
                                    onClick={async (e) => {
                                      e.stopPropagation();
                                      if (window.confirm("Delete this video permanently?")) {
                                        setLoading(true);
                                        try {
                                          await deleteUploadedVideo(v.filename);
                                          getUploadedVideos().then(setSavedVideos).catch(() => {});
                                        } catch (err) {
                                          console.error(err);
                                          setError("Failed to delete video");
                                        } finally {
                                          setLoading(false);
                                        }
                                      }
                                    }}
                                    className="text-slate-500 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity p-1 flex-shrink-0"
                                    title="Delete video"
                                  >
                                    <Trash2 size={14} />
                                  </button>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </>
                )}
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-3">Narrator Voice</label>
                <div className="space-y-2 mb-4">
                  {voices.map(v => (
                    <button
                      key={v.id}
                      onClick={() => setSelectedVoice(v.id)}
                      className={`w-full flex items-center justify-between p-3 rounded-lg border transition-all ${selectedVoice === v.id ? 'bg-orange-600/20 border-orange-500 text-orange-200' : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-600'}`}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${selectedVoice === v.id ? 'bg-orange-600 text-white' : 'bg-slate-800'}`}>
                          {v.gender ? v.gender[0] : 'A'}
                        </div>
                        <span className="font-medium">{v.name}</span>
                      </div>
                      {selectedVoice === v.id && <CheckCircle2 size={16} />}
                    </button>
                  ))}
                </div>
              </div>

              {/* Caption Size Section */}
              <div>
                <label className="block text-slate-300 font-medium mb-3">Caption Size</label>
                <div className="flex bg-slate-950 border border-slate-800 rounded-lg overflow-hidden mb-4">
                  {['Small', 'Medium', 'Large'].map((size) => (
                    <button
                      key={size}
                      onClick={() => setCaptionSize(size)}
                      className={`flex-1 py-2 text-sm font-medium transition-all ${captionSize === size
                        ? 'bg-orange-600 text-white'
                        : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
                        }`}
                    >
                      {size}
                    </button>
                  ))}
                </div>
              </div>

              {/* Smart SFX Section */}
              <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 mb-4">
                <label className="flex items-center justify-between cursor-pointer">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${useSmartSfx ? 'bg-orange-500/20 text-orange-400' : 'bg-slate-800 text-slate-500'}`}>
                      <Music size={18} />
                    </div>
                    <div>
                      <span className="block text-sm font-bold text-slate-200">Smart SFX Engine</span>
                      <span className="text-xs text-slate-500 font-medium">Auto-add whoosh, impact, and coin sounds based on script events</span>
                    </div>
                  </div>
                  <div className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${useSmartSfx ? 'bg-orange-600' : 'bg-slate-700'}`}>
                    <input
                      type="checkbox"
                      className="sr-only"
                      checked={useSmartSfx}
                      onChange={(e) => setUseSmartSfx(e.target.checked)}
                    />
                    <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${useSmartSfx ? 'translate-x-6' : 'translate-x-1'}`} />
                  </div>
                </label>
              </div>

              {/* Auto B-Roll Section */}
              <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 mb-4">
                <label className="flex items-center justify-between cursor-pointer">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${useAutoBRoll ? 'bg-indigo-500/20 text-indigo-400' : 'bg-slate-800 text-slate-500'}`}>
                      <Video size={18} />
                    </div>
                    <div>
                      <span className="block text-sm font-bold text-slate-200">Auto B-Roll Engine</span>
                      <span className="text-xs text-slate-500 font-medium">AI fetches cinematic stock clips from Pexels based on the script</span>
                    </div>
                  </div>
                  <div className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${useAutoBRoll ? 'bg-indigo-600' : 'bg-slate-700'}`}>
                    <input
                      type="checkbox"
                      className="sr-only"
                      checked={useAutoBRoll}
                      onChange={(e) => {
                        setUseAutoBRoll(e.target.checked);
                        if (e.target.checked) setBgVideos([]); // Clear manual videos if turning on auto
                      }}
                    />
                    <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${useAutoBRoll ? 'translate-x-6' : 'translate-x-1'}`} />
                  </div>
                </label>
              </div>

              {/* Background Music Section */}
              <div>
                <label className="block text-slate-300 font-medium mb-3 flex justify-between items-center">
                  Background Music (Optional)
                  {bgMusic && <span className="text-xs text-blue-400 font-bold uppercase">Music Active</span>}
                </label>

                {/* Previously uploaded audio */}
                {savedAudio.length > 0 && !bgMusic && (
                  <div className="space-y-1 mb-3">
                    <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Previously Uploaded</p>
                    {savedAudio.map(a => (
                      <div
                        key={a.filename}
                        onClick={() => setBgMusic(a)}
                        className="w-full flex items-center justify-between gap-2 p-2 rounded-lg border border-slate-800 bg-slate-950 text-slate-400 hover:border-blue-500 hover:text-blue-300 transition-all text-xs cursor-pointer group"
                      >
                        <div className="flex items-center gap-2 truncate">
                          <Music size={14} className="flex-shrink-0" />
                          <span className="truncate">{a.filename.replace(/^audio_[a-f0-9-]+_/, '')}</span>
                        </div>
                        <button
                          onClick={async (e) => {
                            e.stopPropagation();
                            if (window.confirm("Delete this audio permanently?")) {
                              setLoading(true);
                              try {
                                await deleteUploadedAudio(a.filename);
                                getUploadedAudio().then(setSavedAudio).catch(() => {});
                              } catch (err) {
                                console.error(err);
                                setError("Failed to delete audio");
                              } finally {
                                setLoading(false);
                              }
                            }
                          }}
                          className="text-slate-500 hover:text-red-500 p-1 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"
                          title="Delete audio"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
                  {!bgMusic ? (
                    <label className="flex flex-col items-center justify-center h-24 border-2 border-dashed border-slate-700 rounded-lg cursor-pointer hover:border-blue-500 hover:bg-slate-900 transition-all group">
                      <div className="flex flex-col items-center justify-center pt-2 pb-3">
                        <Upload className="w-6 h-6 text-slate-500 group-hover:text-blue-500 mb-2" />
                        <p className="text-xs text-slate-500 group-hover:text-slate-300 font-medium">Upload Background Music (MP3/WAV)</p>
                      </div>
                      <input
                        type="file"
                        className="hidden"
                        accept="audio/*"
                        onChange={async (e) => {
                          const file = e.target.files?.[0];
                          if (file) {
                            setLoading(true);
                            try {
                              const res = await uploadAudio(file);
                              setBgMusic(res);
                              // Refresh saved list
                              getUploadedAudio().then(setSavedAudio).catch(() => { });
                            } catch (err) {
                              console.error(err);
                              setError("Failed to upload background music");
                            } finally {
                              setLoading(false);
                            }
                          }
                        }}
                      />
                    </label>
                  ) : (
                    <div className="flex items-center justify-between bg-slate-900 p-3 rounded-lg border border-blue-500/50">
                      <div className="flex items-center gap-3 overflow-hidden">
                        <Music size={20} className="text-blue-400 flex-shrink-0" />
                        <span className="text-sm text-slate-200 truncate max-w-[200px]">{bgMusic.filename.replace(/^audio_[a-f0-9-]+_/, '')}</span>
                      </div>
                      <button
                        onClick={() => setBgMusic(null)}
                        className="text-slate-500 hover:text-red-500 transition-colors p-1"
                      >
                        <X size={16} />
                      </button>
                    </div>
                  )}
                </div>

                {/* Volume slider — only visible when bg music is active */}
                {bgMusic && (
                  <div className="mt-3 px-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-slate-400">Music Volume</span>
                      <span className="text-xs text-blue-400 font-mono font-bold">{Math.round(bgMusicVolume * 100)}%</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="50"
                      value={Math.round(bgMusicVolume * 100)}
                      onChange={(e) => setBgMusicVolume(parseInt(e.target.value) / 100)}
                      className="w-full h-1.5 bg-slate-700 rounded-full appearance-none cursor-pointer accent-blue-500"
                    />
                    <div className="flex justify-between text-[10px] text-slate-600 mt-0.5">
                      <span>Mute</span>
                      <span>50%</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Generation Actions */}
              <div className="pt-4 space-y-3">

                {/* Caption Generator */}
                {!captionData ? (
                  <button
                    onClick={handleCaptionGeneration}
                    disabled={loading}
                    className="w-full bg-slate-800 hover:bg-slate-700 text-white font-bold py-3 rounded-xl flex items-center justify-center gap-3 border border-slate-700 transition-all"
                  >
                    {loading ? <div className="animate-spin rounded-full h-4 w-4 border-2 border-white" /> : <Hash size={18} />}
                    Generate Viral Caption & Tags
                  </button>
                ) : (
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-xs uppercase tracking-wider text-slate-500 font-bold">Viral Caption</span>
                      <button
                        onClick={() => navigator.clipboard.writeText(captionData.caption_text + "\n\n" + captionData.combined_hashtags)}
                        className="text-orange-500 hover:text-orange-400 text-xs flex items-center gap-1"
                      >
                        <Copy size={12} /> Copy
                      </button>
                    </div>
                    <p className="text-sm text-slate-300 whitespace-pre-wrap mb-3">{captionData.caption_text}</p>
                    <p className="text-xs text-blue-400">{captionData.combined_hashtags}</p>
                  </div>
                )}

                {!audioUrl && (
                  <button
                    onClick={handleVoiceGeneration}
                    disabled={loading}
                    className="w-full bg-slate-800 hover:bg-slate-700 text-white font-bold py-3 rounded-xl flex items-center justify-center gap-3 border border-slate-700 transition-all"
                  >
                    {loading ? <div className="animate-spin rounded-full h-4 w-4 border-2 border-white" /> : <Music size={18} />}
                    Generate Voiceover (AI)
                  </button>
                )}

                {audioUrl && (
                  <div className="flex items-center gap-3 p-3 bg-green-900/20 border border-green-500/30 rounded-lg text-green-400">
                    <CheckCircle2 size={18} />
                    <span className="text-sm font-medium flex-1">Voice Generated</span>
                    <audio controls src={audioUrl} className="h-8 w-32" />
                  </div>
                )}

                <button
                  onClick={handleRenderVideo}
                  disabled={loading || !audioUrl}
                  className="w-full bg-orange-600 hover:bg-orange-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-4 rounded-xl flex items-center justify-center gap-3 shadow-lg shadow-orange-900/20 transition-all"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                      Rendering Video...
                    </>
                  ) : (
                    <>
                      <Video size={20} />
                      Render Final Reel
                    </>
                  )}
                </button>
              </div>

              {error && (
                <div className="bg-red-500/10 border border-red-500/50 text-red-500 p-4 rounded-xl flex items-center gap-3 text-sm">
                  <AlertCircle size={16} />
                  <span>{error}</span>
                </div>
              )}
            </div>
          )}

        </div>

        {/* RIGHT COLUMN: Preview */}
        <div className="flex flex-col justify-start items-center bg-slate-950/50 rounded-2xl border border-slate-800 p-8">
          <h2 className="text-slate-400 font-medium mb-6 uppercase tracking-widest text-sm">Live Preview</h2>

          {videoUrl ? (
            <div className="space-y-4 w-full flex flex-col items-center">
              <video
                src={videoUrl}
                controls
                className="w-[300px] h-[533px] object-cover rounded-xl shadow-2xl border border-slate-800"
                autoPlay
              />
              <a
                href={videoUrl}
                download="chanakya_reel.mp4"
                className="flex items-center gap-2 px-6 py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-lg font-medium transition-colors"
              >
                <Download size={18} />
                Download Reel
              </a>
            </div>
          ) : (
            <VideoPreview script={script} isProcessing={loading} error={error} />
          )}

          {script && !videoUrl && (
            <div className="mt-8 grid grid-cols-3 gap-4 w-full max-w-sm text-center">
              <div className="bg-slate-900 p-3 rounded-lg border border-slate-800">
                <div className="text-xs text-slate-500 uppercase">Duration</div>
                <div className="font-bold text-slate-200">{script.estimatedDuration}s</div>
              </div>
              <div className="bg-slate-900 p-3 rounded-lg border border-slate-800">
                <div className="text-xs text-slate-500 uppercase">Words</div>
                <div className="font-bold text-slate-200">{script.fullText.split(' ').length}</div>
              </div>
              <div className="bg-slate-900 p-3 rounded-lg border border-slate-800">
                <div className="text-xs text-slate-500 uppercase">Ratio</div>
                <div className="font-bold text-slate-200">9:16</div>
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};
