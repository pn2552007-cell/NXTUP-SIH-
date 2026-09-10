import React from 'react';
import { useLocation } from 'react-router-dom';
import { Bell, RefreshCw } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const ROUTE_LABELS = {
  '/admin/dashboard':             'Dashboard',
  '/admin/trainees':              'Trainees',
  '/admin/users':                 'Users',
  '/admin/training':              'Training & Courses',
  '/admin/certificates':          'Certificates',
  '/admin/employment':            'Employment',
  '/admin/employer-verification': 'Employer Verification',
  '/admin/followups':             'Follow-ups',
  '/admin/skill-gaps':            'Skill Gap Analytics',
  '/admin/policy-insights':       'Policy Insights',
  '/admin/reports':               'Reports',
  '/admin/audit-logs':            'Audit Logs',
  '/admin/settings':              'Settings',
};

export const AdminTopBar = ({ onRefresh, loading }) => {
  const location = useLocation();
  const { user } = useAuth();

  const pageLabel = ROUTE_LABELS[location.pathname] || 'Admin Panel';

  return (
    <header className="h-14 bg-slate-950/80 backdrop-blur border-b border-slate-800/60 flex items-center justify-between px-6 shrink-0">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm">
        <span className="text-slate-500">SkillPulse Admin</span>
        <span className="text-slate-700">/</span>
        <span className="text-white font-semibold">{pageLabel}</span>
      </div>

      {/* Right actions */}
      <div className="flex items-center gap-3">
        {onRefresh && (
          <button
            onClick={onRefresh}
            title="Refresh data"
            className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition-all"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        )}

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800">
          <div className="w-6 h-6 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-[10px] font-bold text-white">
            {user?.full_name?.charAt(0)?.toUpperCase() || 'A'}
          </div>
          <div className="hidden sm:block">
            <div className="text-xs font-medium text-white leading-tight">{user?.full_name || 'Admin'}</div>
            <div className="text-[10px] text-indigo-400">Administrator</div>
          </div>
        </div>
      </div>
    </header>
  );
};
