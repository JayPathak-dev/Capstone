import React from 'react';

interface RiskBadgeProps {
  level: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL' | string;
  score?: number;
  size?: 'sm' | 'md' | 'lg';
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, score, size = 'md' }) => {
  const normLevel = level.toUpperCase();

  let bgClass = 'bg-emerald-950/70 text-emerald-400 border-emerald-800/80';
  let dotClass = 'bg-emerald-400 animate-pulse';

  if (normLevel === 'MODERATE') {
    bgClass = 'bg-amber-950/70 text-amber-400 border-amber-800/80';
    dotClass = 'bg-amber-400';
  } else if (normLevel === 'HIGH') {
    bgClass = 'bg-orange-950/70 text-orange-400 border-orange-800/80';
    dotClass = 'bg-orange-400';
  } else if (normLevel === 'CRITICAL') {
    bgClass = 'bg-rose-950/70 text-rose-400 border-rose-800/80';
    dotClass = 'bg-rose-400 animate-ping';
  }

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
    lg: 'text-sm px-3.5 py-1.5 font-semibold',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border font-medium ${sizeClasses[size]} ${bgClass}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${dotClass}`} />
      <span>{normLevel}</span>
      {score !== undefined && (
        <span className="opacity-80 font-mono text-[10px] ml-0.5">({score.toFixed(1)})</span>
      )}
    </span>
  );
};
