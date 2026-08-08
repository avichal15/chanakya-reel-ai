import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Video, Scroll } from 'lucide-react';

export const Hub: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-slate-900 text-slate-50 flex flex-col items-center justify-center p-6 font-sans">
      <div className="max-w-4xl w-full text-center mb-12">
        <h1 className="text-5xl font-extrabold bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent mb-4">
          Creator Hub
        </h1>
        <p className="text-lg text-slate-400">Select an AI Studio to begin crafting viral content</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl w-full">
        {/* Chanakya Card */}
        <div 
          onClick={() => navigate('/chanakya')}
          className="bg-slate-800 border border-slate-700 rounded-2xl p-8 hover:border-amber-500 hover:shadow-[0_0_30px_rgba(245,158,11,0.2)] transition-all cursor-pointer group flex flex-col items-center text-center"
        >
          <div className="w-20 h-20 rounded-full bg-amber-500/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
            <Scroll className="w-10 h-10 text-amber-500" />
          </div>
          <h2 className="text-3xl font-bold mb-3">Chanakya Reel AI</h2>
          <p className="text-slate-400">Generate viral philosophical reels automatically with deep historical wisdom.</p>
        </div>

        {/* Reddit Card */}
        <div 
          onClick={() => navigate('/reddit')}
          className="bg-slate-800 border border-slate-700 rounded-2xl p-8 hover:border-orange-500 hover:shadow-[0_0_30px_rgba(249,115,22,0.2)] transition-all cursor-pointer group flex flex-col items-center text-center"
        >
          <div className="w-20 h-20 rounded-full bg-orange-500/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
            <Video className="w-10 h-10 text-orange-500" />
          </div>
          <h2 className="text-3xl font-bold mb-3">Reddit Reel Maker</h2>
          <p className="text-slate-400">Convert trending Reddit stories into highly engaging short-form videos.</p>
        </div>
      </div>
    </div>
  );
};
