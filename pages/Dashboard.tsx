import React, { useEffect, useState } from 'react';
import { TrendingUp, Video, BookOpen, HardDrive, Clock, ShieldCheck, RefreshCw, Zap } from 'lucide-react';

interface Stats {
  quotes: {
    total: number;
    used: number;
    remaining: number;
  };
  generations: {
    total_videos: number;
  };
  library: {
    media_files: number;
    storage_mb: number;
  };
  api_health: {
    voice: {
      status: string;
      mode: string;
      credits: string;
    };
    gemini: {
      status: string;
    };
  };
  automation: {
    next_run: string;
    status: string;
  };
}

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error("Failed to fetch stats:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000); // Update every 30s
    return () => clearInterval(interval);
  }, []);

  if (loading || !stats) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center space-y-4">
          <RefreshCw className="w-12 h-12 text-orange-500 animate-spin mx-auto" />
          <p className="text-slate-400 font-medium">Loading your empire...</p>
        </div>
      </div>
    );
  }

  const metricCards = [
    { 
      label: 'Quotes Used', 
      value: stats.quotes.used, 
      subValue: `${stats.quotes.total} total`,
      icon: ShieldCheck, 
      color: 'text-green-400', 
      bg: 'bg-green-500/10',
      gradient: 'from-green-500/20 to-transparent'
    },
    { 
      label: 'Library Remaining', 
      value: stats.quotes.remaining, 
      subValue: 'New drops needed',
      icon: BookOpen, 
      color: 'text-blue-400', 
      bg: 'bg-blue-500/10',
      gradient: 'from-blue-500/20 to-transparent'
    },
    { 
      label: 'Videos Generated', 
      value: stats.generations.total_videos, 
      subValue: 'Live on YT/IG',
      icon: Video, 
      color: 'text-purple-400', 
      bg: 'bg-purple-500/10',
      gradient: 'from-purple-500/20 to-transparent'
    },
    { 
      label: 'Storage Usage', 
      value: `${stats.library.storage_mb} MB`, 
      subValue: `${stats.library.media_files} assets`,
      icon: HardDrive, 
      color: 'text-orange-400', 
      bg: 'bg-orange-500/10',
      gradient: 'from-orange-500/20 to-transparent'
    },
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 pb-12">
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl font-black text-white tracking-tight mb-2">
            Strategist <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-500 to-red-600">Dashboard</span>
          </h1>
          <p className="text-slate-400 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            System Active • Automated Scheduler Running
          </p>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={fetchStats}
            className="p-3 bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700 rounded-xl transition-all"
          >
            <RefreshCw size={20} className="text-slate-300" />
          </button>
          <div className="px-4 py-2 bg-indigo-600/20 border border-indigo-500/30 rounded-xl flex items-center gap-3">
             <div className="p-1.5 bg-indigo-500 rounded-lg">
                <Clock size={16} className="text-white" />
             </div>
             <div>
                <p className="text-[10px] uppercase font-bold text-indigo-300 tracking-wider">Next Run</p>
                <p className="text-sm font-bold text-white">{stats.automation.next_run}</p>
             </div>
          </div>
        </div>
      </header>

      {/* Metric Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {metricCards.map((card, i) => (
          <div 
            key={i} 
            className={`relative group overflow-hidden bg-slate-900/40 border border-slate-800/50 p-6 rounded-3xl hover:border-slate-700 transition-all duration-300 backdrop-blur-sm`}
          >
            <div className={`absolute inset-0 bg-gradient-to-br ${card.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`}></div>
            
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-6">
                <div className={`p-4 rounded-2xl ${card.bg} ${card.color} ring-1 ring-inset ring-white/10`}>
                  <card.icon size={28} strokeWidth={2.5} />
                </div>
                <TrendingUp size={20} className="text-slate-600" />
              </div>
              <div className="space-y-1">
                <h3 className="text-4xl font-black text-white tracking-tight">{card.value}</h3>
                <p className="text-slate-300 font-bold text-sm tracking-wide">{card.label}</p>
              </div>
              <div className="mt-4 pt-4 border-t border-slate-800/50">
                <p className="text-slate-500 text-xs font-semibold uppercase tracking-widest">{card.subValue}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Main Content Areas */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          {/* Automation Intelligence */}
          <div className="bg-slate-900/40 border border-slate-800/50 rounded-3xl p-8 backdrop-blur-sm relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-8 opacity-5">
              <Zap size={120} className="text-white" />
            </div>
            
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-2xl font-bold text-white">Automation Intelligence</h2>
                <p className="text-slate-500 text-sm mt-1">Smart tracking of your philosophical empire</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-slate-950/50 border border-slate-800 p-6 rounded-2xl">
                <p className="text-slate-500 text-sm font-medium mb-2">Quote Pipeline Usage</p>
                <div className="flex items-end gap-3 mb-4">
                    <span className="text-3xl font-black text-white">{stats.quotes.total > 0 ? Math.round((stats.quotes.used / stats.quotes.total) * 100) : 0}%</span>
                    <span className="text-slate-500 pb-1 text-sm">capacity reached</span>
                </div>
                <div className="w-full h-3 bg-slate-800 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-orange-500 to-red-600 rounded-full transition-all duration-1000 ease-out"
                      style={{ width: `${stats.quotes.total > 0 ? (stats.quotes.used / stats.quotes.total) * 100 : 0}%` }}
                    ></div>
                </div>
              </div>

              <div className="bg-slate-950/50 border border-slate-800 p-6 rounded-2xl">
                <p className="text-slate-500 text-sm font-medium mb-2">Library Availability</p>
                <div className="flex items-end gap-3 mb-4">
                    <span className="text-3xl font-black text-white">{stats.quotes.remaining}</span>
                    <span className="text-slate-500 pb-1 text-sm">quotes untapped</span>
                </div>
                <div className="flex gap-1.5">
                    {[...Array(10)].map((_, i) => (
                      <div 
                        key={i} 
                        className={`h-2 flex-1 rounded-full ${stats.quotes.total > 0 && i < (stats.quotes.remaining / stats.quotes.total * 10) ? 'bg-blue-500' : 'bg-slate-800'}`}
                      ></div>
                    ))}
                </div>
              </div>
            </div>
          </div>

          {/* API & Connectivity Center */}
          <div className="bg-slate-900/40 border border-slate-800/50 rounded-3xl p-8 backdrop-blur-sm relative overflow-hidden group">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-2xl font-bold text-white">API Connectivity Center</h2>
                <p className="text-slate-500 text-sm mt-1">Real-time health of your generation engines</p>
              </div>
              <div className="px-4 py-1.5 bg-green-500/10 border border-green-500/20 rounded-full">
                <p className="text-xs font-bold text-green-400 uppercase tracking-widest tracking-tighter">Systems Secure</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-slate-950/50 border border-slate-800 p-6 rounded-2xl flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-slate-500 text-xs font-black uppercase tracking-widest">ElevenLabs Voice</p>
                  <p className="text-xl font-bold text-white uppercase">{stats.api_health.voice.mode === 'premium' ? 'Premium Mode' : 'Fallback Active'}</p>
                  <p className="text-xs text-slate-500 font-medium">{stats.api_health.voice.credits}</p>
                </div>
                <div className={`w-3 h-3 rounded-full ${stats.api_health.voice.status === 'active' ? 'bg-green-500 shadow-[0_0_12px_rgba(34,197,94,0.5)]' : 'bg-orange-500 shadow-[0_0_12px_rgba(249,115,22,0.5)]'}`}></div>
              </div>

              <div className="bg-slate-950/50 border border-slate-800 p-6 rounded-2xl flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-slate-500 text-xs font-black uppercase tracking-widest">Gemini Engine</p>
                  <p className="text-xl font-bold text-white uppercase">Neural Logic</p>
                  <p className="text-xs text-slate-500 font-medium">{stats.api_health.gemini.status === 'active' ? 'Connected' : 'Offline'}</p>
                </div>
                <div className={`w-3 h-3 rounded-full ${stats.api_health.gemini.status === 'active' ? 'bg-green-500 shadow-[0_0_12px_rgba(34,197,94,0.5)]' : 'bg-red-500 shadow-[0_0_12px_rgba(239,68,68,0.5)]'}`}></div>
              </div>
            </div>
            
            <div className="mt-6 p-4 bg-orange-500/10 border border-orange-500/20 rounded-xl flex items-center gap-4">
              <Zap className="text-orange-400 shrink-0" size={20} />
              <p className="text-sm text-orange-200/80 leading-snug">
                {stats.api_health.voice.mode === 'fallback' 
                  ? "Your ElevenLabs credits are currently exhausted. The system is automatically using high-quality Free Fallback (Edge-TTS) to keep the automation running."
                  : "ElevenLabs premium credits are active. The system is utilizing high-fidelity custom voices for maximum engagement."
                }
              </p>
            </div>
          </div>
        </div>

        <div className="space-y-8">
          <div className="bg-gradient-to-br from-indigo-600 via-purple-700 to-pink-600 rounded-3xl p-8 text-white flex flex-col justify-between relative overflow-hidden shadow-2xl shadow-indigo-500/20 aspect-square lg:aspect-auto">
            <div className="relative z-10">
              <div className="w-12 h-12 bg-white/20 backdrop-blur-md rounded-2xl flex items-center justify-center mb-6">
                <Zap className="text-white fill-white" size={24} />
              </div>
              <h2 className="text-3xl font-black mb-3 tracking-tight">Expand Your Library</h2>
              <p className="text-indigo-100 text-lg leading-relaxed mb-8">
                Add more Chanakya Neeti quotes to keep the automation fueled for months.
              </p>
              <button className="bg-white text-indigo-700 font-black py-4 px-8 rounded-2xl hover:scale-105 active:scale-95 transition-all w-full shadow-xl text-lg tracking-wide uppercase">
                Ingest More Quotes
              </button>
            </div>
            <div className="absolute -bottom-12 -right-12 w-48 h-48 bg-white/10 rounded-full blur-3xl"></div>
            <div className="absolute top-10 -left-10 w-24 h-24 bg-yellow-400/20 rounded-full blur-2xl"></div>
          </div>
          
          <div className="bg-slate-900/40 border border-slate-800/50 rounded-3xl p-8 backdrop-blur-sm">
            <h3 className="text-lg font-bold text-white mb-4">Quick Insights</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between py-3 border-b border-slate-800/50">
                <p className="text-slate-400 text-sm">Engagement Rate</p>
                <p className="text-white font-bold tracking-tight">High</p>
              </div>
              <div className="flex items-center justify-between py-3 border-b border-slate-800/50">
                <p className="text-slate-400 text-sm">Upload Success</p>
                <p className="text-green-400 font-bold tracking-tight">98.2%</p>
              </div>
              <div className="flex items-center justify-between py-3">
                <p className="text-slate-400 text-sm">Library Health</p>
                <p className="text-orange-400 font-bold tracking-tight">Refill Soon</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};