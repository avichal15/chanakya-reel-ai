import React, { useState } from 'react';
import { Search, PenTool, BookOpen, Hash, Upload, FileText, Loader2, AlertCircle, ClipboardPaste, X } from 'lucide-react';
import { CHANAKYA_QUOTES } from '../data/chanakyaQuotes';
import { Quote } from '../types';
import { extractQuotesFromText } from '../services/geminiService';
import { getQuotes, createQuotesBulk, ingestPDF } from '../services/api';

interface LibraryProps {
  onSelectQuote: (quote: string) => void;
}

export const Library: React.FC<LibraryProps> = ({ onSelectQuote }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [quotes, setQuotes] = useState<Quote[]>(CHANAKYA_QUOTES);

  // Upload States
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Paste Mode States
  const [showPasteInput, setShowPasteInput] = useState(false);
  const [pastedText, setPastedText] = useState("");
  const [isProcessingText, setIsProcessingText] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState('');

  // Load backend quotes on mount
  React.useEffect(() => {
    const loadSavedQuotes = async () => {
      try {
        const savedQuotes = await getQuotes();
        // Backend returns elements with `.tags` as string. We need to convert to array.
        const formattedSaved = savedQuotes.map((q: any) => ({
          ...q,
          tags: q.tags ? q.tags.split(',') : [],
          source: 'Saved Import'
        }));
        setQuotes([...formattedSaved, ...CHANAKYA_QUOTES]);
      } catch (err) {
        console.error("Failed to load saved quotes:", err);
      }
    };
    loadSavedQuotes();
  }, []);

  // Extract unique tags
  const allTags = Array.from(new Set(quotes.flatMap(q => q.tags)));

  const filteredQuotes = quotes.filter(quote => {
    const matchesSearch = quote.text.toLowerCase().includes(searchTerm.toLowerCase()) ||
      quote.translation?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTag = selectedTag ? quote.tags.includes(selectedTag) : true;
    return matchesSearch && matchesTag;
  });

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      setUploadError("Please upload a valid PDF file.");
      return;
    }

    setIsUploading(true);
    setUploadError(null);
    setSuccessMsg(null);
    setShowPasteInput(false);
    setUploadProgress(0);
    setUploadStatus('Uploading PDF...');

    try {
      // Use streaming fetch to get real-time progress from backend
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('http://localhost:8000/api/ingest/pdf', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error(`Server error: ${response.status}`);
      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let finalQuotes: any[] = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const event = JSON.parse(line);
            setUploadProgress(event.progress || 0);
            setUploadStatus(event.status || 'Processing...');
            if (event.quotes) {
              finalQuotes = event.quotes;
            }
          } catch {
            // Skip malformed JSON lines
          }
        }
      }

      if (finalQuotes.length === 0) {
        setUploadError("No quotes could be extracted from this PDF.");
      } else {
        const mappedQuotes: Quote[] = finalQuotes.map((q: any) => ({
          id: q.id?.toString() || Math.random().toString(),
          text: q.text || "",
          translation: q.translation || "",
          meaning: q.meaning || "",
          tags: typeof q.tags === 'string' ? q.tags.split(',').map((t: string) => t.trim()).filter(Boolean) : (q.tags || []),
          source: "Imported PDF",
        }));
        setQuotes(prev => [...mappedQuotes, ...prev]);
        setSuccessMsg(`Success! Deep scan extracted ${finalQuotes.length} quotes from ${file.name}.`);
      }
    } catch (err: any) {
      setUploadError(err.message || "Failed to process PDF. The file may be too large or corrupted.");
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
      setUploadStatus('');
      event.target.value = '';
    }
  };

  const handlePasteImport = async () => {
    if (!pastedText.trim()) return;
    setIsProcessingText(true);
    setUploadError(null);
    setSuccessMsg(null);

    try {
      const extracted = await extractQuotesFromText(pastedText);
      if (extracted.length === 0) {
        setUploadError("No quotes found in text.");
      } else {
        try {
          // Attempt to save them to the backend
          const quotesToSave = extracted.map(q => ({
            text: q.text,
            translation: q.translation,
            meaning: q.meaning,
            tags: q.tags.join(','),
            language: 'mix'
          }));
          await createQuotesBulk(quotesToSave);
        } catch (saveErr) {
          console.error("Failed to persist to database:", saveErr);
        }
        setQuotes(prev => [...extracted, ...prev]);
        setSuccessMsg(`Imported ${extracted.length} quotes from text.`);
        setShowPasteInput(false);
        setPastedText("");
      }
    } catch (err: any) {
      setUploadError(err.message || "Failed to process text.");
    } finally {
      setIsProcessingText(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <header className="flex flex-col xl:flex-row justify-between items-start xl:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Quote Library</h1>
          <p className="text-slate-400">Browse ancient wisdom extracted from Chanakya Neeti.</p>
        </div>

        <div className="w-full xl:w-auto flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1 sm:flex-none">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
            <input
              type="text"
              placeholder="Search quotes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full sm:w-64 pl-10 pr-4 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-white focus:ring-2 focus:ring-orange-500 outline-none"
            />
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => {
                setShowPasteInput(!showPasteInput);
                setUploadError(null);
                setSuccessMsg(null);
              }}
              className={`flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl transition-colors font-medium border border-transparent ${showPasteInput ? 'bg-slate-700 text-white border-slate-600' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
            >
              <ClipboardPaste size={18} />
              <span className="hidden sm:inline">Paste</span>
            </button>

            <label className={`flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl cursor-pointer transition-colors whitespace-nowrap ${isUploading
                ? 'bg-slate-800 text-slate-400 cursor-not-allowed'
                : 'bg-orange-600 hover:bg-orange-500 text-white font-medium shadow-lg shadow-orange-900/20'
              }`}>
              {isUploading ? (
                <Loader2 size={18} className="animate-spin" />
              ) : (
                <Upload size={18} />
              )}
              <span className="hidden sm:inline">{isUploading ? 'Deep Scanning...' : 'Import PDF'}</span>
              <span className="sm:hidden">{isUploading ? '...' : 'PDF'}</span>
              <input
                type="file"
                accept=".pdf"
                className="hidden"
                onChange={handleFileUpload}
                disabled={isUploading}
              />
            </label>
          </div>
        </div>
      </header>

      {/* PDF Extraction Progress Bar */}
      {isUploading && (
        <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-4 animate-in fade-in slide-in-from-top-2">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-orange-400">{uploadStatus || 'Processing...'}</span>
            <span className="text-sm font-bold text-white">{uploadProgress}%</span>
          </div>
          <div className="w-full bg-slate-700 rounded-full h-3 overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500 ease-out"
              style={{
                width: `${uploadProgress}%`,
                background: 'linear-gradient(90deg, #f97316, #fb923c, #f97316)',
                backgroundSize: '200% 100%',
                animation: 'shimmer 1.5s infinite linear',
              }}
            />
          </div>
          <p className="text-xs text-slate-500 mt-2">Extracting quotes from your PDF in chunks. This may take a few minutes for large documents.</p>
          <style>{`@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }`}</style>
        </div>
      )}

      {showPasteInput && (
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4 animate-in fade-in slide-in-from-top-2">
          <div className="flex justify-between items-center mb-2">
            <label className="text-sm font-medium text-slate-300">Paste quote text or raw content</label>
            <button onClick={() => setShowPasteInput(false)} className="text-slate-500 hover:text-white"><X size={16} /></button>
          </div>
          <textarea
            value={pastedText}
            onChange={(e) => setPastedText(e.target.value)}
            placeholder="Paste Sanskrit text, translations, or raw book content here... e.g. 'A man is great by deeds...'"
            className="w-full h-32 bg-slate-950 border border-slate-700 rounded-lg p-3 text-slate-200 focus:ring-2 focus:ring-orange-500 focus:outline-none mb-3 resize-none"
          />
          <div className="flex justify-end">
            <button
              onClick={handlePasteImport}
              disabled={isProcessingText || !pastedText.trim()}
              className="bg-orange-600 hover:bg-orange-500 disabled:opacity-50 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors"
            >
              {isProcessingText ? <Loader2 size={16} className="animate-spin" /> : <ClipboardPaste size={16} />}
              {isProcessingText ? 'Analyzing...' : 'Import Quotes'}
            </button>
          </div>
        </div>
      )}

      {uploadError && (
        <div className="bg-red-500/10 border border-red-500/50 text-red-500 p-4 rounded-xl flex items-center gap-3 animate-in fade-in">
          <AlertCircle size={20} />
          <span>{uploadError}</span>
        </div>
      )}

      {successMsg && (
        <div className="bg-green-500/10 border border-green-500/50 text-green-500 p-4 rounded-xl flex items-center gap-3 animate-in fade-in">
          <FileText size={20} />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Tags Filter */}
      <div className="flex gap-2 overflow-x-auto pb-2 custom-scrollbar">
        <button
          onClick={() => setSelectedTag(null)}
          className={`px-4 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${selectedTag === null ? 'bg-orange-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
            }`}
        >
          All
        </button>
        {allTags.map(tag => (
          <button
            key={tag}
            onClick={() => setSelectedTag(tag === selectedTag ? null : tag)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${selectedTag === tag ? 'bg-orange-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
              }`}
          >
            {tag}
          </button>
        ))}
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredQuotes.map((quote) => (
          <div key={quote.id} className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 hover:border-orange-500/50 transition-all flex flex-col group h-full">
            <div className="mb-4 flex-1">
              <div className="flex flex-wrap items-center gap-2 mb-3">
                <span className="px-2 py-1 bg-slate-800 text-orange-400 text-xs font-bold rounded uppercase tracking-wider">
                  {quote.source.includes(',') ? quote.source.split(',')[1] : 'Verse'}
                </span>
                <div className="flex flex-wrap gap-1">
                  {quote.tags.slice(0, 2).map(t => (
                    <span key={t} className="text-xs text-slate-500 flex items-center gap-1">
                      <Hash size={10} />{t}
                    </span>
                  ))}
                </div>
              </div>
              <p className="text-lg font-serif text-slate-200 mb-3 italic leading-relaxed">
                "{quote.text.split('\n')[0]}..."
              </p>
              <div className="space-y-2">
                <p className="text-sm text-slate-400 line-clamp-3">
                  <span className="text-slate-500 font-semibold">Trans: </span>
                  {quote.translation}
                </p>
                {quote.meaning && (
                  <p className="text-sm text-slate-400 line-clamp-3 border-t border-slate-800 pt-2 mt-2">
                    <span className="text-orange-500/80 font-semibold">Meaning: </span>
                    {quote.meaning}
                  </p>
                )}
              </div>
            </div>

            <div className="mt-auto pt-4 border-t border-slate-800/50 flex justify-between items-center">
              <span className="text-xs text-slate-600 font-mono truncate max-w-[100px]">{quote.id}</span>
              <button
                onClick={() => onSelectQuote(`${quote.text}\n\nTranslation: ${quote.translation}\n\nMeaning: ${quote.meaning || ''}`)}
                className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-orange-600 text-white rounded-lg text-sm font-medium transition-colors group-hover:bg-orange-600 shadow-sm"
              >
                <PenTool size={14} />
                Create Reel
              </button>
            </div>
          </div>
        ))}
      </div>

      {filteredQuotes.length === 0 && (
        <div className="text-center py-20 text-slate-500">
          <BookOpen size={48} className="mx-auto mb-4 opacity-50" />
          <p className="text-xl font-medium">No wisdom found.</p>
          <p className="text-sm">Try searching for something else or import a PDF.</p>
        </div>
      )}
    </div>
  );
}