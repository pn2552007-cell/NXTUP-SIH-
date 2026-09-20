import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  LayoutDashboard,
  ShieldCheck,
  Building2,
  Briefcase,
  Landmark,
} from 'lucide-react';

export const Sidebar = () => {
  const { role, nextupId } = useAuth();

  const navItems = {
    TRAINEE: [
      { to: '/trainee/dashboard', label: 'My Journey & Outcomes', icon: LayoutDashboard },
      { to: '/consent', label: 'Consent & NXTUP ID', icon: ShieldCheck },
    ],
    PROVIDER: [
      { to: '/provider/dashboard', label: 'Provider Overview', icon: Building2 },
    ],
    TRAINING_PROVIDER: [
      { to: '/provider/dashboard', label: 'Provider Overview', icon: Building2 },
    ],
    EMPLOYER: [
      { to: '/employer/dashboard', label: 'Verification & Talent', icon: Briefcase },
    ],
    ADMIN: [
      { to: '/admin/dashboard', label: 'National Outcome Analytics', icon: Landmark },
    ],
  }[role] || [];

  return (
    <aside className="w-64 shrink-0 bg-slate-950/60 border-r border-slate-800/80 p-4 hidden md:flex flex-col justify-between">
      <div className="space-y-6">
        {/* Role badge */}
        <div className="px-3 py-2.5 rounded-xl bg-slate-900/80 border border-slate-800">
          <div className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Current Role</div>
          <div className="text-sm font-bold text-white flex items-center gap-2 mt-0.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            {role?.replace('_', ' ')}
          </div>
          {nextupId && (
            <div className="text-[11px] font-mono text-emerald-400 mt-1 truncate">
              ID: {nextupId}
            </div>
          )}
        </div>

        {/* Navigation list */}
        <nav className="space-y-1.5">
          <div className="text-[10px] uppercase font-bold tracking-wider text-slate-400 px-3 pb-1">
            Dashboard Menu
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 shadow-sm'
                      : 'text-slate-400 hover:text-white hover:bg-slate-900/60'
                  }`
                }
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* Feature quick links */}
        <div className="space-y-1.5 pt-4 border-t border-slate-900">
          <div className="text-[10px] uppercase font-bold tracking-wider text-slate-400 px-3 pb-1">
            Platform Capabilities
          </div>
          <div className="px-3 py-2 text-xs text-slate-400 space-y-2">
            <div className="flex items-center gap-2 text-slate-300">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              <span>Unified NXTUP ID</span>
            </div>
            <div className="flex items-center gap-2 text-slate-300">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
              <span>AI Skill Gap Engine</span>
            </div>
            <div className="flex items-center gap-2 text-slate-300">
              <span className="w-1.5 h-1.5 rounded-full bg-purple-400" />
              <span>Longitudinal Tracking</span>
            </div>
            <div className="flex items-center gap-2 text-slate-300">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
              <span>Employer Verification</span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Info */}
      <div className="p-3 rounded-xl bg-slate-900/40 border border-slate-800/60 text-center">
        <div className="text-[11px] font-medium text-slate-300">NXTUP Platform</div>
        <div className="text-[10px] text-slate-400 mt-0.5">Longitudinal Skilling & Outcomes</div>
      </div>
    </aside>
  );
};
