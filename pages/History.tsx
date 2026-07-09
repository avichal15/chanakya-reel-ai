import React, { useEffect, useState } from 'react';
import { Download, Calendar, Activity, RefreshCw } from 'lucide-react';
import { getExportHistory } from '../services/api';
import { ExportHistoryRecord } from '../types';

export const History: React.FC = () => {
    const [history, setHistory] = useState<ExportHistoryRecord[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [expandedScriptIds, setExpandedScriptIds] = useState<Set<number>>(new Set());

    const toggleScript = (id: number) => {
        setExpandedScriptIds(prev => {
            const next = new Set(prev);
            if (next.has(id)) next.delete(id);
            else next.add(id);
            return next;
        });
    };

    const fetchHistory = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await getExportHistory();
            setHistory(data);
        } catch (err: any) {
            console.error(err);
            setError('Failed to load export history.');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchHistory();
    }, []);

    const formatDate = (isoString: string) => {
        try {
            const d = new Date(isoString);
            return d.toLocaleDateString(undefined, {
                month: 'short', day: 'numeric', year: 'numeric',
                hour: 'numeric', minute: '2-digit'
            });
        } catch {
            return isoString;
        }
    };

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <header className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2">Export History</h1>
                    <p className="text-slate-400">Review and download your successfully generated viral reels.</p>
                </div>
                <button
                    onClick={fetchHistory}
                    disabled={isLoading}
                    className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl transition-colors disabled:opacity-50"
                >
                    <RefreshCw size={18} className={isLoading ? "animate-spin" : ""} />
                    Refresh
                </button>
            </header>

            {error ? (
                <div className="bg-red-500/10 border border-red-500/20 text-red-500 p-4 rounded-xl">
                    {error}
                </div>
            ) : isLoading ? (
                <div className="flex flex-col items-center justify-center h-64 text-slate-500 gap-4">
                    <Activity className="animate-pulse text-orange-500" size={48} />
                    <p className="font-medium animate-pulse">Loading history pipeline...</p>
                </div>
            ) : history.length === 0 ? (
                <div className="flex flex-col items-center justify-center p-12 bg-slate-900/50 border border-slate-800 rounded-2xl text-slate-500 text-center">
                    <Activity size={48} className="mb-4 opacity-50" />
                    <h3 className="text-xl font-bold text-slate-300 mb-2">No exports yet</h3>
                    <p className="max-w-md">Head over to the Reel Studio to generate your first viral Chanakya video. It will appear here once it's finished rendering.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                    {history.map((record) => (
                        <div key={record.id} className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden hover:border-slate-700 transition-colors shadow-lg">
                            <div className="aspect-[9/16] bg-black relative">
                                <video
                                    src={`http://localhost:8000${record.video_url}`}
                                    controls
                                    playsInline
                                    className="w-full h-full object-cover"
                                />
                            </div>
                            <div className="p-5 space-y-4">
                                <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
                                    <div className="flex items-center gap-1.5">
                                        <Calendar size={14} />
                                        {formatDate(record.created_at)}
                                    </div>
                                    <span className="px-2 py-1 bg-green-500/10 text-green-500 rounded-lg">
                                        {record.status}
                                    </span>
                                </div>

                                <div className="space-y-2">
                                    <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider">Script</h4>
                                    <div
                                        className={`text-sm text-slate-400 leading-relaxed cursor-pointer transition-all duration-200 ${expandedScriptIds.has(record.id) ? '' : 'line-clamp-3'}`}
                                        onClick={() => toggleScript(record.id)}
                                    >
                                        {record.caption_text || "No script available."}
                                    </div>
                                    {record.caption_text && record.caption_text.length > 100 && (
                                        <button
                                            onClick={() => toggleScript(record.id)}
                                            className="text-xs text-orange-500 hover:text-orange-400 font-medium"
                                        >
                                            {expandedScriptIds.has(record.id) ? "Show Less" : "Read Full Script"}
                                        </button>
                                    )}
                                </div>

                                <div className="pt-2 border-t border-slate-800/50">
                                    <a
                                        href={`http://localhost:8000${record.video_url}`}
                                        download
                                        target="_blank"
                                        rel="noreferrer"
                                        className="flex w-full items-center justify-center gap-2 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium rounded-xl transition-colors"
                                    >
                                        <Download size={16} />
                                        Download MP4
                                    </a>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};
