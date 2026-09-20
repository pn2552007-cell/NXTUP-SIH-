import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  LayoutDashboard, Users, UserCheck, GraduationCap, Award,
  Briefcase, BadgeCheck, Calendar, TrendingUp, FileBarChart2,
  ScrollText, Settings, Shield, ChevronLeft, ChevronRight,
  LogOut, Zap
} from 'lucide-react';

const NAV_ITEMS = [
  { to: '/admin/dashboard',           label: 'Dashboard',            icon: LayoutDashboard },
  { to: '/admin/trainees',            label: 'Trainees',             icon: UserCheck },
  { to: '/admin/users',               label: 'Users',                icon: Users },
  { to: '/admin/training',            label: 'Training & Courses',   icon: GraduationCap },
  { to: '/admin/certificates',        label: 'Certificates',         icon: Award },
  { to: '/admin/employment',          label: 'Employment',           icon: Briefcase },
  { to: '/admin/employer-verification', label: 'Employer Verification', icon: BadgeCheck },
  { to: '/admin/followups',           label: 'Follow-ups',           icon: Calendar },
  { to: '/admin/skill-gaps',          label: 'Skill Gaps',           icon: TrendingUp },
  { to: '/admin/policy-insights',     label: 'Policy Insights',      icon: FileBarChart2 },
  { to: '/admin/reports',             label: 'Reports',              icon: ScrollText },
  { to: '/admin/audit-logs',          label: 'Audit Logs',           icon: Shield },
  { to: '/admin/settings',            label: 'Settings',             icon: Settings },
];

export const AdminSidebar = () => {
  const [collapsed, setCollapsed] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside
      className={`
        flex flex-col h-full bg-slate-950 border-r border-slate-800/80
        transition-all duration-300 ease-in-out shrink-0
        ${collapsed ? 'w-16' : 'w-64'}
      `}
    >
      {/* Logo / Branding */}
      <div className={`flex items-center gap-3 px-4 py-5 border-b border-slate-800/60 ${collapsed ? 'justify-center' : ''}`}>
        <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shrink-0">
          <Zap className="w-4 h-4 text-white" />
        </div>
        {!collapsed && (
          <div>
            <div className="text-sm font-bold text-white leading-tight">NXTUP</div>
            <div className="text-[10px] text-indigo-400 font-medium tracking-wide">ADMIN PANEL</div>
          </div>
        )}
      </div>

      {/* Collapse Toggle */}
      <button
        onClick={() => setCollapsed(c => !c)}
        className="absolute top-[68px] -right-3 w-6 h-6 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-700 transition-all z-10"
      >
        {collapsed ? <ChevronRight className="w-3 h-3" /> : <ChevronLeft className="w-3 h-3" />}
      </button>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-0.5">
        {!collapsed && (
          <div className="text-[10px] uppercase font-bold tracking-widest text-slate-500 px-3 pb-2">
            Navigation
          </div>
        )}
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              title={collapsed ? item.label : undefined}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl text-sm font-medium transition-all duration-150 group
                ${collapsed ? 'px-3 py-3 justify-center' : 'px-3 py-2.5'}
                ${isActive
                  ? 'bg-indigo-500/15 text-indigo-300 border border-indigo-500/30'
                  : 'text-slate-400 hover:text-white hover:bg-slate-900/60 border border-transparent'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <Icon className={`w-4 h-4 shrink-0 transition-colors ${isActive ? 'text-indigo-400' : 'text-slate-500 group-hover:text-slate-300'}`} />
                  {!collapsed && <span className="truncate">{item.label}</span>}
                </>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* User info + logout */}
      <div className={`border-t border-slate-800/60 p-3 space-y-2 ${collapsed ? 'items-center' : ''}`}>
        {!collapsed && user && (
          <div className="px-2 py-2 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="text-xs font-semibold text-white truncate">{user.full_name}</div>
            <div className="text-[10px] text-indigo-400 truncate">{user.email}</div>
            <div className="mt-1 inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-indigo-500/15 border border-indigo-500/30">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
              <span className="text-[10px] font-bold text-indigo-300">ADMIN</span>
            </div>
          </div>
        )}
        <button
          onClick={handleLogout}
          title={collapsed ? 'Logout' : undefined}
          className={`w-full flex items-center gap-2 px-3 py-2 rounded-xl text-sm text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-all border border-transparent hover:border-red-500/20 ${collapsed ? 'justify-center' : ''}`}
        >
          <LogOut className="w-4 h-4 shrink-0" />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </aside>
  );
};
