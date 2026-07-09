import React from 'react';
import { LayoutDashboard, Video, Library, Settings, ScrollText, PlayCircle } from 'lucide-react';

interface SidebarProps {
  activePage: string;
  setActivePage: (page: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activePage, setActivePage }) => {
  const navItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { id: 'studio', icon: Video, label: 'Reel Studio' },
    { id: 'library', icon: Library, label: 'Quote Library' },
    { id: 'history', icon: ScrollText, label: 'Export History' },
    { id: 'settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <div className="w-20 md:w-64 bg-slate-950 border-r border-slate-800 flex flex-col items-center md:items-stretch py-6 flex-shrink-0">
      <div className="flex items-center justify-center md:justify-start px-4 md:px-6 mb-10 text-orange-500 gap-3">
        <PlayCircle size={32} />
        <span className="hidden md:block text-xl font-bold tracking-tight text-white">Chanakya<span className="text-orange-500">AI</span></span>
      </div>

      <nav className="flex-1 w-full space-y-2 px-2">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActivePage(item.id)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
              activePage === item.id
                ? 'bg-orange-600 text-white shadow-lg shadow-orange-900/20'
                : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
            }`}
          >
            <item.icon size={20} />
            <span className="hidden md:block font-medium">{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="px-6 py-4 border-t border-slate-800 hidden md:block">
        <div className="bg-slate-900 rounded-lg p-3 text-xs text-slate-400 border border-slate-800">
          <p className="font-semibold text-slate-300 mb-1">Status</p>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-500"></span>
            Gemini API Ready
          </div>
        </div>
      </div>
    </div>
  );
};