import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subValue?: string;
  icon: LucideIcon;
  variant?: 'default' | 'danger' | 'warning' | 'success' | 'teal';
  change?: string;
  isPositive?: boolean;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subValue,
  icon: Icon,
  variant = 'default',
  change,
  isPositive,
}) => {
  const variantStyles = {
    default: {
      card: 'border-slate-800 bg-slate-900/80 hover:border-slate-700',
      iconBox: 'bg-slate-800/80 text-slate-300',
    },
    danger: {
      card: 'border-rose-900/50 bg-gradient-to-br from-slate-900 to-rose-950/20 hover:border-rose-700/60',
      iconBox: 'bg-rose-900/40 text-rose-400',
    },
    warning: {
      card: 'border-amber-900/50 bg-gradient-to-br from-slate-900 to-amber-950/20 hover:border-amber-700/60',
      iconBox: 'bg-amber-900/40 text-amber-400',
    },
    success: {
      card: 'border-emerald-900/50 bg-gradient-to-br from-slate-900 to-emerald-950/20 hover:border-emerald-700/60',
      iconBox: 'bg-emerald-900/40 text-emerald-400',
    },
    teal: {
      card: 'border-teal-900/50 bg-gradient-to-br from-slate-900 to-teal-950/20 hover:border-teal-700/60',
      iconBox: 'bg-teal-900/40 text-teal-400',
    },
  };

  const style = variantStyles[variant];

  return (
    <div
      className={`rounded-xl border p-5 backdrop-blur-sm transition-all duration-200 shadow-sm ${style.card}`}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
          {title}
        </span>
        <div className={`rounded-lg p-2.5 ${style.iconBox}`}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
      <div className="mt-4 flex items-baseline gap-2">
        <span className="text-2xl font-bold tracking-tight text-white font-mono">{value}</span>
        {subValue && <span className="text-xs text-slate-400">{subValue}</span>}
      </div>
      {change && (
        <div className="mt-2.5 flex items-center text-xs">
          <span
            className={`font-medium ${
              isPositive ? 'text-emerald-400' : 'text-rose-400'
            }`}
          >
            {change}
          </span>
          <span className="ml-1.5 text-slate-500">vs. baseline sanction</span>
        </div>
      )}
    </div>
  );
};
