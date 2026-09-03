import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

export const MetricCard = ({
  title,
  value,
  subtitle,
  trend,
  trendPositive = true,
  icon: Icon,
  badgeText,
  accentColor = 'emerald',
  className = '',
}) => {
  const accentClasses = {
    emerald: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    cyan: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
    purple: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
    amber: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
    rose: 'text-rose-400 bg-rose-500/10 border-rose-500/20',
  }[accentColor] || 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';

  return (
    <div className={`glass-panel rounded-2xl p-5 relative overflow-hidden transition-all duration-300 hover:border-slate-700/80 hover:translate-y-[-2px] ${className}`}>
      {/* Background glow decoration */}
      <div className="absolute -right-6 -bottom-6 w-24 h-24 rounded-full bg-slate-800/40 blur-2xl pointer-events-none" />

      <div className="flex items-start justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          {title}
        </span>
        {Icon && (
          <div className={`p-2.5 rounded-xl border ${accentClasses}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-2xl lg:text-3xl font-bold tracking-tight text-white">
          {value}
        </span>
        {badgeText && (
          <span className="text-xs font-medium px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 border border-slate-700/50">
            {badgeText}
          </span>
        )}
      </div>

      {(subtitle || trend) && (
        <div className="mt-2.5 flex items-center gap-2 text-xs text-slate-400">
          {trend && (
            <span
              className={`flex items-center font-semibold ${
                trendPositive ? 'text-emerald-400' : 'text-rose-400'
              }`}
            >
              {trendPositive ? (
                <TrendingUp className="w-3.5 h-3.5 mr-0.5" />
              ) : (
                <TrendingDown className="w-3.5 h-3.5 mr-0.5" />
              )}
              {trend}
            </span>
          )}
          {subtitle && <span>{subtitle}</span>}
        </div>
      )}
    </div>
  );
};
