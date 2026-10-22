import React from 'react';
import {
  LayoutDashboard,
  FolderGit2,
  AlertTriangle,
  Flame,
  Scale,
  Bot,
  FileSpreadsheet,
  Cpu,
  HelpCircle,
  ExternalLink,
} from 'lucide-react';

export type TabType =
  | 'overview'
  | 'projects'
  | 'risk'
  | 'alerts'
  | 'benchmarking'
  | 'assistant'
  | 'data'
  | 'models';

interface SidebarProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
  alertCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onTabChange,
  alertCount = 0,
}) => {
  const navItems = [
    { id: 'overview' as TabType, label: 'Overview', icon: LayoutDashboard },
    { id: 'projects' as TabType, label: 'Project Explorer', icon: FolderGit2 },
    { id: 'risk' as TabType, label: 'Risk Intelligence', icon: Flame },
    {
      id: 'alerts' as TabType,
      label: 'Early Warnings',
      icon: AlertTriangle,
      badge: alertCount > 0 ? alertCount : undefined,
    },
    { id: 'benchmarking' as TabType, label: 'Benchmarking', icon: Scale },
    { id: 'assistant' as TabType, label: 'AI Assistant', icon: Bot, isNew: true },
    { id: 'data' as TabType, label: 'Data Management', icon: FileSpreadsheet },
    { id: 'models' as TabType, label: 'Model Performance', icon: Cpu },
  ];

  return (
    <aside className="w-64 flex-shrink-0 border-r border-slate-800 bg-[#0B132B] flex flex-col justify-between p-4">
      {/* Navigation List */}
      <div className="space-y-1.5">
        <div className="px-3 py-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
          Intelligence Suite
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-xs font-medium transition-all ${
                isActive
                  ? 'bg-teal-600/15 text-teal-300 border border-teal-500/40 shadow-sm'
                  : 'text-slate-300 hover:bg-slate-800/60 hover:text-white'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon
                  className={`h-4 w-4 ${
                    isActive ? 'text-teal-400' : 'text-slate-400'
                  }`}
                />
                <span>{item.label}</span>
              </div>
              <div className="flex items-center gap-1.5">
                {item.isNew && (
                  <span className="rounded bg-teal-900/60 text-teal-300 text-[10px] px-1.5 py-0.2 border border-teal-700">
                    AI
                  </span>
                )}
                {item.badge !== undefined && (
                  <span className="rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30 text-[10px] font-bold px-2 py-0.5 font-mono">
                    {item.badge}
                  </span>
                )}
              </div>
            </button>
          );
        })}
      </div>

      {/* Footer Info Box */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-3.5 space-y-2">
        <div className="flex items-center justify-between text-xs text-slate-300 font-semibold">
          <span>PAIMANA Prototype</span>
          <span className="font-mono text-[10px] text-teal-400 bg-teal-950 px-1.5 py-0.5 rounded border border-teal-900">
            v1.0.0
          </span>
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed">
          Predictive early warnings and explainable risk scores for national infrastructure schemes.
        </p>
        <div className="pt-1 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
          <span>Smart India Hackathon</span>
          <span className="font-mono text-slate-400">SIH26103</span>
        </div>
      </div>
    </aside>
  );
};
