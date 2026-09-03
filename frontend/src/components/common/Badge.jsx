import React from 'react';

const BADGE_VARIANTS = {
  emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  cyan: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
  amber: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  rose: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
  purple: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
  slate: 'bg-slate-800/60 text-slate-300 border-slate-700',
  blue: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
};

export const Badge = ({ children, variant = 'slate', className = '', size = 'md' }) => {
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs font-medium';
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border ${BADGE_VARIANTS[variant] || BADGE_VARIANTS.slate} ${sizeClasses} ${className}`}
    >
      {children}
    </span>
  );
};
