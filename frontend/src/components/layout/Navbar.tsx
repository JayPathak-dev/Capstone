import React from 'react';
import { Search, Bell, ShieldCheck, Activity, Cpu } from 'lucide-react';

interface NavbarProps {
  onSearchChange?: (val: string) => void;
  unreadAlertCount?: number;
  onAlertClick?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  onSearchChange,
  unreadAlertCount = 0,
  onAlertClick,
}) => {
  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-slate-800 bg-[#0B132B]/90 px-6 backdrop-blur-md">
      {/* Title & Organization */}
      <div className="flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-teal-600/20 text-teal-400 border border-teal-500/30">
          <Activity className="h-5 w-5" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-base font-bold tracking-tight text-white">
              PAIMANA <span className="text-teal-400 text-xs font-mono font-normal px-2 py-0.5 rounded bg-teal-950/60 border border-teal-800">INTELLIGENCE</span>
            </h1>
          </div>
          <p className="text-[11px] text-slate-400">
            Ministry Infrastructure Early Warning & Predictive Analytics System (SIH26103)
          </p>
        </div>
      </div>

      {/* Global Search & Actions */}
      <div className="flex items-center gap-4">
        <div className="relative w-64 md:w-80">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search projects, agencies, corridors..."
            onChange={(e) => onSearchChange && onSearchChange(e.target.value)}
            className="w-full rounded-lg border border-slate-700/80 bg-slate-900/90 py-1.5 pl-9 pr-4 text-xs text-slate-200 placeholder-slate-500 focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500/30"
          />
        </div>

        {/* Live Engine Status Badge */}
        <div className="hidden sm:flex items-center gap-2 rounded-full border border-emerald-900/60 bg-emerald-950/40 px-3 py-1 text-xs text-emerald-400">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="font-mono text-[11px]">API & ML Connected</span>
        </div>

        {/* Notification Bell */}
        <button
          onClick={onAlertClick}
          className="relative rounded-lg border border-slate-700/70 bg-slate-800/80 p-2 text-slate-300 hover:text-white hover:border-slate-600 transition-colors"
          title="Early Warnings"
        >
          <Bell className="h-4 w-4" />
          {unreadAlertCount > 0 && (
            <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-rose-500 text-[10px] font-bold text-white">
              {unreadAlertCount > 9 ? '9+' : unreadAlertCount}
            </span>
          )}
        </button>

        {/* User Persona Profile */}
        <div className="flex items-center gap-2.5 border-l border-slate-800 pl-4">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-800 text-teal-400 font-bold text-xs border border-slate-700">
            PMO
          </div>
          <div className="hidden lg:block text-left">
            <div className="text-xs font-semibold text-slate-200">Director General (PMO)</div>
            <div className="text-[10px] text-slate-400">Cabinet Secretariat Oversight</div>
          </div>
        </div>
      </div>
    </header>
  );
};
