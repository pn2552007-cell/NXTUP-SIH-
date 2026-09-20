import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { adminAPI } from '../../services/api';
import { StatusBadge } from '../../components/admin/StatusBadge';
import {
  Search, RefreshCw, Filter, ChevronLeft, ChevronRight,
  UserCheck, Users, GraduationCap, Award, Briefcase, BadgeCheck,
  Calendar, TrendingUp, FileBarChart2, ScrollText, Shield, Settings,
  AlertCircle, CheckCircle2, Building2, MapPin
} from 'lucide-react';

const SECTION_CONFIG = {
  '/admin/trainees': {
    title: 'Trainee Cohort Directory',
    subtitle: 'Persistent NXTUP ID profiles and longitudinal livelihood tracking.',
    icon: UserCheck,
    fetcher: (params) => adminAPI.getTrainees(params),
  },
  '/admin/users': {
    title: 'User Access & Stakeholder Management',
    subtitle: 'Manage RBAC permissions for Trainees, Providers, Employers, and Admins.',
    icon: Users,
    fetcher: (params) => adminAPI.getUsers(params),
  },
  '/admin/training': {
    title: 'Training Batches & Courses',
    subtitle: 'Ecosystem course enrollments, completion milestones, and provider metrics.',
    icon: GraduationCap,
    fetcher: (params) => adminAPI.getTraining(params),
  },
  '/admin/certificates': {
    title: 'Certifications Ledger',
    subtitle: 'Digitally verified credentials and assessment records.',
    icon: Award,
    fetcher: (params) => adminAPI.getCertificates(params),
  },
  '/admin/employment': {
    title: 'Employment & Wage Records',
    subtitle: 'Post-training industry placement, salary benchmarks, and retention tenure.',
    icon: Briefcase,
    fetcher: (params) => adminAPI.getEmployment(params),
  },
  '/admin/employer-verification': {
    title: 'Employer Verification Queue',
    subtitle: 'Direct employer confirmations validating trainee employment status.',
    icon: BadgeCheck,
    fetcher: (params) => adminAPI.getEmployerVerification(params),
  },
  '/admin/followups': {
    title: 'Longitudinal Follow-up Surveys',
    subtitle: 'Scheduled automated survey responses tracking multi-year outcomes.',
    icon: Calendar,
    fetcher: (params) => adminAPI.getFollowups(params),
  },
  '/admin/skill-gaps': {
    title: 'Skill Gap & Demand Analytics',
    subtitle: 'Granular skill deficiency analysis against active industry requirements.',
    icon: TrendingUp,
    fetcher: (params) => adminAPI.getSkillGaps(params),
  },
  '/admin/policy-insights': {
    title: 'Policy & Impact Insights',
    subtitle: 'State and district outcome disparities, wage growth indices, and retention curves.',
    icon: FileBarChart2,
    fetcher: (params) => adminAPI.getPolicyInsights(params),
  },
  '/admin/reports': {
    title: 'Longitudinal Outcome Reports',
    subtitle: 'Audited outcome summaries and exportable compliance documentation.',
    icon: ScrollText,
    fetcher: (params) => adminAPI.getReports(params),
  },
  '/admin/audit-logs': {
    title: 'Security & Audit Trail',
    subtitle: 'Immutable system logs of logins, data updates, and administrative actions.',
    icon: Shield,
    fetcher: (params) => adminAPI.getAuditLogs(params),
  },
  '/admin/settings': {
    title: 'Platform System Settings',
    subtitle: 'Database configuration, ML pipeline thresholds, and integration status.',
    icon: Settings,
    fetcher: () => adminAPI.getSettings(),
  },
};

export const AdminSectionView = () => {
  const location = useLocation();
  const path = location.pathname;
  const config = SECTION_CONFIG[path] || {
    title: 'Admin Module',
    subtitle: 'NXTUP administrative management console.',
    icon: Shield,
    fetcher: () => adminAPI.getDashboard(),
  };

  const Icon = config.icon;
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await config.fetcher({ page, per_page: 15, search: search || undefined });
      setData(res.data);
    } catch (err) {
      console.error(`Error loading ${path}:`, err);
      setError(err.response?.data?.detail || 'Failed to load records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setPage(1);
  }, [path]);

  useEffect(() => {
    fetchData();
  }, [path, page]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchData();
  };

  // Render Table based on path
  const renderContent = () => {
    if (loading) {
      return (
        <div className="flex flex-col items-center justify-center py-20 text-slate-400 space-y-3">
          <RefreshCw className="w-6 h-6 animate-spin text-emerald-400" />
          <span className="text-xs">Loading {config.title}...</span>
        </div>
      );
    }

    if (error) {
      return (
        <div className="p-6 rounded-2xl bg-red-500/10 border border-red-500/30 text-red-300 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
          <span className="text-xs font-medium">{error}</span>
        </div>
      );
    }

    // Trainees Table
    if (path === '/admin/trainees') {
      const items = data?.items || [];
      return (
        <div className="overflow-x-auto rounded-xl border border-slate-800">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/90 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
              <tr>
                <th className="px-3.5 py-3">NXTUP ID</th>
                <th className="px-3.5 py-3">Trainee Name</th>
                <th className="px-3.5 py-3">State / District</th>
                <th className="px-3.5 py-3">Course / Provider</th>
                <th className="px-3.5 py-3">Training Status</th>
                <th className="px-3.5 py-3">Certificate</th>
                <th className="px-3.5 py-3">Employment</th>
                <th className="px-3.5 py-3">Verification</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {items.length > 0 ? (
                items.map((t) => (
                  <tr key={t.id} className="hover:bg-slate-900/40 transition-colors">
                    <td className="px-3.5 py-3 font-mono font-bold text-emerald-400">
                      {t.nextup_id || t.skillpulse_id || `NXT-2026-${String(t.id).padStart(6, '0')}`}
                    </td>
                    <td className="px-3.5 py-3">
                      <div className="font-semibold text-white">{t.full_name}</div>
                      <div className="text-[10px] text-slate-400">{t.email}</div>
                    </td>
                    <td className="px-3.5 py-3 text-slate-300">
                      {t.district ? `${t.district}, ${t.state}` : (t.state || '—')}
                    </td>
                    <td className="px-3.5 py-3">
                      <div className="text-slate-200">{t.course_name || '—'}</div>
                      <div className="text-[10px] text-slate-400">{t.provider_name || '—'}</div>
                    </td>
                    <td className="px-3.5 py-3">
                      <StatusBadge status={t.training_status} />
                    </td>
                    <td className="px-3.5 py-3">
                      <StatusBadge status={t.certificate_status} />
                    </td>
                    <td className="px-3.5 py-3">
                      <StatusBadge status={t.employment_status} />
                    </td>
                    <td className="px-3.5 py-3">
                      <StatusBadge status={t.verification_status} />
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="px-4 py-12 text-center text-slate-400">
                    No trainees match your search or filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      );
    }

    // Users Table
    if (path === '/admin/users') {
      const items = data?.items || [];
      return (
        <div className="overflow-x-auto rounded-xl border border-slate-800">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/90 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
              <tr>
                <th className="px-3.5 py-3">User</th>
                <th className="px-3.5 py-3">Role</th>
                <th className="px-3.5 py-3">Linked ID</th>
                <th className="px-3.5 py-3">Contact</th>
                <th className="px-3.5 py-3">Active</th>
                <th className="px-3.5 py-3">Created</th>
                <th className="px-3.5 py-3">Last Login</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {items.length > 0 ? (
                items.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-900/40 transition-colors">
                    <td className="px-3.5 py-3">
                      <div className="font-semibold text-white">{u.full_name}</div>
                      <div className="text-[10px] text-slate-400">{u.email}</div>
                    </td>
                    <td className="px-3.5 py-3">
                      <StatusBadge status={u.role} />
                    </td>
                    <td className="px-3.5 py-3 font-mono text-emerald-400 text-xs">
                      {u.nextup_id || u.skillpulse_id || '—'}
                    </td>
                    <td className="px-3.5 py-3 text-slate-300">
                      {u.phone || '—'}
                    </td>
                    <td className="px-3.5 py-3">
                      <StatusBadge status={u.is_active ? 'ACTIVE' : 'INACTIVE'} />
                    </td>
                    <td className="px-3.5 py-3 text-slate-400 text-[11px]">
                      {u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}
                    </td>
                    <td className="px-3.5 py-3 text-slate-400 text-[11px]">
                      {u.last_login ? new Date(u.last_login).toLocaleString() : 'Never'}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="px-4 py-12 text-center text-slate-400">
                    No users found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      );
    }

    // Generic display for Training, Employment, Certificates, etc.
    const items = data?.items || (Array.isArray(data) ? data : []);
    if (items.length > 0) {
      const keys = Object.keys(items[0]).filter(k => k !== 'id' && !k.endsWith('_id'));
      return (
        <div className="overflow-x-auto rounded-xl border border-slate-800">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/90 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
              <tr>
                {keys.slice(0, 7).map((k) => (
                  <th key={k} className="px-3.5 py-3">
                    {k.replace(/_/g, ' ')}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {items.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-900/40 transition-colors">
                  {keys.slice(0, 7).map((k) => {
                    const val = row[k];
                    const isStatus = typeof val === 'string' && ['COMPLETED', 'EMPLOYED', 'VERIFIED', 'PENDING', 'ACTIVE', 'ISSUED'].includes(val.toUpperCase());
                    return (
                      <td key={k} className="px-3.5 py-3">
                        {isStatus ? (
                          <StatusBadge status={val} />
                        ) : typeof val === 'boolean' ? (
                          <StatusBadge status={val} />
                        ) : typeof val === 'object' && val !== null ? (
                          JSON.stringify(val)
                        ) : (
                          String(val || '—')
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    // If data is an object with summary stats (like settings or policy insights)
    if (data && typeof data === 'object' && !Array.isArray(data)) {
      return (
        <div className="glass-panel rounded-2xl p-6 border-slate-800 space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(data).map(([key, val]) => {
              if (typeof val === 'object' && val !== null) return null;
              return (
                <div key={key} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div className="text-[11px] text-slate-400 uppercase font-mono">{key.replace(/_/g, ' ')}</div>
                  <div className="text-base font-bold text-white mt-1">{String(val)}</div>
                </div>
              );
            })}
          </div>
          <div className="pt-4 border-t border-slate-800/60">
            <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-[11px] font-mono text-slate-300 overflow-auto max-h-72">
              {JSON.stringify(data, null, 2)}
            </pre>
          </div>
        </div>
      );
    }

    return (
      <div className="py-16 text-center text-slate-400 text-xs">
        No records available in this section.
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="glass-panel-glow rounded-2xl p-6 border-cyan-500/30 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-cyan-600 to-emerald-400 p-0.5">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Icon className="w-5 h-5 text-cyan-400" />
            </div>
          </div>
          <div>
            <h1 className="text-xl font-black text-white">{config.title}</h1>
            <p className="text-xs text-slate-300">{config.subtitle}</p>
          </div>
        </div>

        {/* Search & Actions */}
        <div className="flex items-center gap-2.5">
          <form onSubmit={handleSearchSubmit} className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search records..."
              className="bg-slate-900 border border-slate-700 rounded-xl pl-8 pr-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500 w-48 sm:w-64"
            />
          </form>

          <button
            onClick={fetchData}
            title="Refresh"
            className="p-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-300 hover:text-white transition-all"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Main Table / View */}
      <div className="glass-panel rounded-2xl p-6 border-slate-800 space-y-4">
        {renderContent()}

        {/* Pagination */}
        {data?.pages > 1 && (
          <div className="flex items-center justify-between pt-4 border-t border-slate-800/60 text-xs">
            <span className="text-slate-400">
              Showing page <strong className="text-white">{data.page}</strong> of <strong className="text-white">{data.pages}</strong> ({data.total} total items)
            </span>
            <div className="flex items-center gap-2">
              <button
                disabled={page <= 1 || loading}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white disabled:opacity-40 flex items-center gap-1"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
                <span>Prev</span>
              </button>
              <button
                disabled={page >= data.pages || loading}
                onClick={() => setPage((p) => p + 1)}
                className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white disabled:opacity-40 flex items-center gap-1"
              >
                <span>Next</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminSectionView;
