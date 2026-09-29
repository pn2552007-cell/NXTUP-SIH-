import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { adminAPI } from '../../services/api';
import { StatusBadge } from '../../components/admin/StatusBadge';
import {
  Search, RefreshCw, Filter, ChevronLeft, ChevronRight,
  UserCheck, Users, GraduationCap, Award, Briefcase, BadgeCheck,
  Calendar, TrendingUp, FileBarChart2, ScrollText, Shield, Settings,
  AlertCircle, CheckCircle2, Building2, MapPin, BookOpen,
  BarChart2, Layers, Activity, Download, Info, Clock, User,
  Database, Server, ToggleRight, FileText, Globe, ChevronDown,
} from 'lucide-react';

// ─── Helpers ────────────────────────────────────────────────────────────────

const fmt = (v) => {
  if (v === null || v === undefined || v === '') return '—';
  if (typeof v === 'boolean') return v ? 'Yes' : 'No';
  return String(v);
};

const fmtDate = (v) => {
  if (!v) return '—';
  try {
    return new Date(v).toLocaleDateString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric',
    });
  } catch { return fmt(v); }
};

const fmtDateTime = (v) => {
  if (!v) return '—';
  try {
    return new Date(v).toLocaleString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  } catch { return fmt(v); }
};

const fmtPct = (v) =>
  v !== null && v !== undefined ? `${Number(v).toFixed(1)}%` : '—';

const fmtINR = (v) =>
  v ? `₹${Number(v).toLocaleString('en-IN')}` : '—';

// ─── Shared sub-components ──────────────────────────────────────────────────

const MetricCard = ({ label, value, sub, icon: Icon, color = 'cyan' }) => {
  const colors = {
    cyan:    { bg: 'bg-cyan-500/10',    border: 'border-cyan-500/20',    text: 'text-cyan-400',    val: 'text-cyan-300' },
    emerald: { bg: 'bg-emerald-500/10', border: 'border-emerald-500/20', text: 'text-emerald-400', val: 'text-emerald-300' },
    amber:   { bg: 'bg-amber-500/10',   border: 'border-amber-500/20',   text: 'text-amber-400',   val: 'text-amber-300' },
    blue:    { bg: 'bg-blue-500/10',    border: 'border-blue-500/20',    text: 'text-blue-400',    val: 'text-blue-300' },
    purple:  { bg: 'bg-purple-500/10',  border: 'border-purple-500/20',  text: 'text-purple-400',  val: 'text-purple-300' },
    rose:    { bg: 'bg-rose-500/10',    border: 'border-rose-500/20',    text: 'text-rose-400',    val: 'text-rose-300' },
  };
  const c = colors[color] || colors.cyan;
  return (
    <div className={`rounded-xl ${c.bg} border ${c.border} p-4 flex items-start gap-3`}>
      {Icon && (
        <div className={`p-2 rounded-lg ${c.bg} border ${c.border} shrink-0`}>
          <Icon className={`w-4 h-4 ${c.text}`} />
        </div>
      )}
      <div className="min-w-0">
        <div className="text-[11px] text-slate-400 uppercase font-mono tracking-wide leading-tight">{label}</div>
        <div className={`text-xl font-black mt-0.5 ${c.val}`}>{value}</div>
        {sub && <div className="text-[10px] text-slate-500 mt-0.5">{sub}</div>}
      </div>
    </div>
  );
};

const SectionCard = ({ title, icon: Icon, children, className = '' }) => (
  <div className={`rounded-xl bg-slate-900/60 border border-slate-800 overflow-hidden ${className}`}>
    {title && (
      <div className="px-4 py-3 border-b border-slate-800 flex items-center gap-2">
        {Icon && <Icon className="w-4 h-4 text-cyan-400" />}
        <span className="text-xs font-bold text-white uppercase tracking-wider">{title}</span>
      </div>
    )}
    {children}
  </div>
);

const EmptyState = ({ message = 'No records available.' }) => (
  <div className="py-16 flex flex-col items-center gap-3 text-slate-500">
    <Database className="w-8 h-8 opacity-40" />
    <p className="text-sm">{message}</p>
  </div>
);

// ─── SECTION CONFIG ──────────────────────────────────────────────────────────

const SECTION_CONFIG = {
  '/admin/trainees': {
    title: 'Trainee Cohort Directory',
    subtitle: 'Persistent NXTUP ID profiles and longitudinal livelihood tracking.',
    icon: UserCheck,
    fetcher: (params) => adminAPI.getTrainees(params),
    paginated: true,
  },
  '/admin/users': {
    title: 'User Access & Stakeholder Management',
    subtitle: 'Manage RBAC permissions for Trainees, Providers, Employers, and Admins.',
    icon: Users,
    fetcher: (params) => adminAPI.getUsers(params),
    paginated: true,
  },
  '/admin/training': {
    title: 'Training Batches & Courses',
    subtitle: 'Ecosystem course enrollments, completion milestones, and provider metrics.',
    icon: GraduationCap,
    fetcher: (params) => adminAPI.getTraining(params),
    paginated: false,
  },
  '/admin/certificates': {
    title: 'Certifications Ledger',
    subtitle: 'Digitally verified credentials and assessment records.',
    icon: Award,
    fetcher: (params) => adminAPI.getCertificates(params),
    paginated: true,
  },
  '/admin/employment': {
    title: 'Employment & Wage Records',
    subtitle: 'Post-training industry placement, salary benchmarks, and retention tenure.',
    icon: Briefcase,
    fetcher: (params) => adminAPI.getEmployment(params),
    paginated: true,
  },
  '/admin/employer-verification': {
    title: 'Employer Verification Queue',
    subtitle: 'Direct employer confirmations validating trainee employment status.',
    icon: BadgeCheck,
    fetcher: (params) => adminAPI.getEmployerVerification(params),
    paginated: true,
  },
  '/admin/followups': {
    title: 'Longitudinal Follow-up Surveys',
    subtitle: 'Scheduled automated survey responses tracking multi-year outcomes.',
    icon: Calendar,
    fetcher: (params) => adminAPI.getFollowups(params),
    paginated: true,
  },
  '/admin/skill-gaps': {
    title: 'Skill Gap & Demand Analytics',
    subtitle: 'Granular skill deficiency analysis against active industry requirements.',
    icon: TrendingUp,
    fetcher: (params) => adminAPI.getSkillGaps(params),
    paginated: true,
  },
  '/admin/policy-insights': {
    title: 'Policy & Impact Insights',
    subtitle: 'State and district outcome disparities, wage growth indices, and retention curves.',
    icon: FileBarChart2,
    fetcher: (params) => adminAPI.getPolicyInsights(params),
    paginated: false,
  },
  '/admin/reports': {
    title: 'Longitudinal Outcome Reports',
    subtitle: 'Audited outcome summaries and exportable compliance documentation.',
    icon: ScrollText,
    fetcher: (params) => adminAPI.getReports(params),
    paginated: false,
  },
  '/admin/audit-logs': {
    title: 'Security & Audit Trail',
    subtitle: 'Immutable system logs of logins, data updates, and administrative actions.',
    icon: Shield,
    fetcher: (params) => adminAPI.getAuditLogs(params),
    paginated: true,
  },
  '/admin/settings': {
    title: 'Platform System Settings',
    subtitle: 'Database configuration, ML pipeline thresholds, and integration status.',
    icon: Settings,
    fetcher: () => adminAPI.getSettings(),
    paginated: false,
  },
};

// ════════════════════════════════════════════════════════════════════════════
// PAGE-SPECIFIC RENDERERS
// ════════════════════════════════════════════════════════════════════════════

// ─── /admin/training ────────────────────────────────────────────────────────
const TrainingView = ({ data }) => {
  const s = data?.summary || {};
  const courses = data?.courses || [];
  const providers = data?.providers || [];

  return (
    <div className="space-y-6">
      {/* Summary metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <MetricCard label="Courses"        value={fmt(s.total_courses)}   icon={BookOpen}   color="cyan" />
        <MetricCard label="Providers"      value={fmt(s.total_providers)} icon={Building2}  color="blue" />
        <MetricCard label="Batches"        value={fmt(s.total_batches)}   icon={Layers}     color="purple" />
        <MetricCard label="Enrolled"       value={fmt(s.total_enrolled)}  icon={Users}      color="amber" />
        <MetricCard label="Completed"      value={fmt(s.total_completed)} icon={Award}      color="emerald" />
        <MetricCard label="Completion Rate" value={fmtPct(s.completion_rate_pct)} icon={Activity} color="emerald" />
      </div>

      {/* Courses table */}
      <SectionCard title="Courses" icon={BookOpen}>
        {courses.length === 0 ? (
          <EmptyState message="No courses found." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/90 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
                <tr>
                  <th className="px-3.5 py-3">Course</th>
                  <th className="px-3.5 py-3">Domain</th>
                  <th className="px-3.5 py-3">Provider</th>
                  <th className="px-3.5 py-3 text-right">Duration</th>
                  <th className="px-3.5 py-3 text-right">Enrolled</th>
                  <th className="px-3.5 py-3 text-right">Completed</th>
                  <th className="px-3.5 py-3 text-right">Completion %</th>
                  <th className="px-3.5 py-3 text-right">Employed</th>
                  <th className="px-3.5 py-3 text-right">Employment %</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-200">
                {courses.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-900/40 transition-colors">
                    <td className="px-3.5 py-3 font-semibold text-white">{c.course_name}</td>
                    <td className="px-3.5 py-3 text-slate-400">{fmt(c.domain)}</td>
                    <td className="px-3.5 py-3 text-slate-300">{fmt(c.provider_name)}</td>
                    <td className="px-3.5 py-3 text-right text-slate-400">{c.duration_weeks ? `${c.duration_weeks}w` : '—'}</td>
                    <td className="px-3.5 py-3 text-right font-mono text-blue-300">{fmt(c.enrolled)}</td>
                    <td className="px-3.5 py-3 text-right font-mono text-emerald-300">{fmt(c.completed)}</td>
                    <td className="px-3.5 py-3 text-right">
                      <span className="font-bold text-cyan-300">{fmtPct(c.completion_rate)}</span>
                    </td>
                    <td className="px-3.5 py-3 text-right font-mono text-amber-300">{fmt(c.employed)}</td>
                    <td className="px-3.5 py-3 text-right">
                      <span className="font-bold text-purple-300">{fmtPct(c.employment_rate)}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </SectionCard>

      {/* Providers table */}
      <SectionCard title="Training Providers" icon={Building2}>
        {providers.length === 0 ? (
          <EmptyState message="No providers found." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/90 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
                <tr>
                  <th className="px-3.5 py-3">Organization</th>
                  <th className="px-3.5 py-3">Location</th>
                  <th className="px-3.5 py-3 text-right">Courses</th>
                  <th className="px-3.5 py-3 text-right">Batches</th>
                  <th className="px-3.5 py-3 text-right">Trained</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-200">
                {providers.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-900/40 transition-colors">
                    <td className="px-3.5 py-3 font-semibold text-white">{p.organization_name}</td>
                    <td className="px-3.5 py-3 text-slate-400">
                      {p.district && p.state ? `${p.district}, ${p.state}` : (p.state || '—')}
                    </td>
                    <td className="px-3.5 py-3 text-right font-mono text-cyan-300">{fmt(p.total_courses)}</td>
                    <td className="px-3.5 py-3 text-right font-mono text-purple-300">{fmt(p.total_batches)}</td>
                    <td className="px-3.5 py-3 text-right font-mono text-emerald-300">{fmt(p.total_trained)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </SectionCard>
    </div>
  );
};

// ─── /admin/policy-insights ─────────────────────────────────────────────────
const PolicyInsightsView = ({ data }) => {
  const sm = data?.summary_metrics || {};
  const insights = data?.insights || [];
  const courses = data?.course_performance || [];
  const districts = data?.district_performance || [];
  const filters = data?.active_filters || {};

  const dataQualityColor = (q) => {
    if (q === 'VERIFIED') return 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
    if (q === 'PARTIAL')  return 'text-amber-400 border-amber-500/30 bg-amber-500/10';
    return 'text-slate-400 border-slate-600/30 bg-slate-800/40';
  };

  const insightTypeIcon = (type) => {
    if (type === 'EMPLOYMENT_OUTCOME')    return Briefcase;
    if (type === 'TRAINING_EFFECTIVENESS') return GraduationCap;
    if (type === 'RETENTION')             return Activity;
    return Info;
  };

  // Active filters display
  const activeFilterEntries = Object.entries(filters).filter(
    ([, v]) => v !== null && v !== undefined && v !== 'ALL' && v !== ''
  );

  return (
    <div className="space-y-6">
      {/* Disclaimer */}
      {data?.data_disclaimer && (
        <div className="flex gap-3 p-4 rounded-xl bg-amber-500/10 border border-amber-500/30">
          <Info className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <p className="text-xs text-amber-200 leading-relaxed">{data.data_disclaimer}</p>
        </div>
      )}

      {/* Meta row */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-slate-400">
        <div className="flex items-center gap-1.5">
          <Clock className="w-3.5 h-3.5" />
          <span>Generated: {fmtDateTime(data?.generated_at)}</span>
        </div>
        {activeFilterEntries.length > 0 && (
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-slate-500">Filters:</span>
            {activeFilterEntries.map(([k, v]) => (
              <span key={k} className="px-2 py-0.5 rounded-md bg-slate-800 border border-slate-700 text-slate-300 font-mono text-[10px]">
                {k.replace(/_/g, ' ')}: {String(v)}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Summary metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
        <MetricCard label="Total Trainees"        value={fmt(sm.total_trainees)}                 icon={Users}      color="cyan" />
        <MetricCard label="Employment Rate"        value={fmtPct(sm.employment_rate_pct)}         icon={Briefcase}  color="emerald" />
        <MetricCard label="Verified Employment"    value={fmtPct(sm.verified_employment_rate_pct)} icon={BadgeCheck} color="blue" />
        <MetricCard label="Avg Wage Growth"        value={fmtPct(sm.avg_wage_growth_pct)}         icon={TrendingUp} color="purple" />
        <MetricCard label="6-Month Retention"      value={fmtPct(sm.retention_6m_pct)}            icon={Activity}   color="amber" />
        <MetricCard label="Verified Placements"    value={fmt(sm.verified_employment_count)}      icon={CheckCircle2} color="emerald" />
        <MetricCard label="Self-Reported Placed"   value={fmt(sm.self_reported_employment_count)} icon={UserCheck}  color="blue" />
      </div>

      {/* Policy Insights */}
      {insights.length > 0 && (
        <SectionCard title="Evidence-Based Insights" icon={FileBarChart2}>
          <div className="divide-y divide-slate-800/60">
            {insights.map((ins, idx) => {
              const InsIcon = insightTypeIcon(ins.type);
              return (
                <div key={idx} className="p-4 space-y-3">
                  <div className="flex items-start gap-3">
                    <div className="p-1.5 rounded-lg bg-slate-800 border border-slate-700 shrink-0">
                      <InsIcon className="w-3.5 h-3.5 text-cyan-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex flex-wrap items-center gap-2 mb-1">
                        <span className="text-sm font-bold text-white">{ins.title}</span>
                        {ins.data_quality && (
                          <span className={`text-[10px] font-mono border px-2 py-0.5 rounded-full ${dataQualityColor(ins.data_quality)}`}>
                            {ins.data_quality}
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-slate-300 leading-relaxed">{ins.observation}</p>
                    </div>
                  </div>
                  {ins.evidence?.length > 0 && (
                    <div className="ml-8 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
                      {ins.evidence.map((ev, ei) => (
                        <div key={ei} className="bg-slate-900/60 rounded-lg border border-slate-800 p-2.5">
                          <div className="text-[10px] text-slate-500 leading-tight">{ev.label}</div>
                          <div className="text-sm font-bold text-white mt-0.5">{fmt(ev.value)}</div>
                        </div>
                      ))}
                    </div>
                  )}
                  {ins.caveat && (
                    <p className="ml-8 text-[10px] text-slate-500 italic leading-relaxed">
                      ⚠ {ins.caveat}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </SectionCard>
      )}

      {/* Course Performance */}
      {courses.length > 0 && (
        <SectionCard title="Course Performance" icon={BookOpen}>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/90 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
                <tr>
                  <th className="px-3.5 py-3">Course</th>
                  <th className="px-3.5 py-3 text-right">Trainees</th>
                  <th className="px-3.5 py-3 text-right">Employed</th>
                  <th className="px-3.5 py-3 text-right">Employment %</th>
                  <th className="px-3.5 py-3 text-right">Verified</th>
                  <th className="px-3.5 py-3 text-right">Avg Wage Growth</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-200">
                {courses.map((c, i) => (
                  <tr key={i} className="hover:bg-slate-900/40 transition-colors">
                    <td className="px-3.5 py-3 font-semibold text-white">{c.course_name || '—'}</td>
                    <td className="px-3.5 py-3 text-right font-mono text-blue-300">{fmt(c.total_trainees)}</td>
                    <td className="px-3.5 py-3 text-right font-mono text-emerald-300">{fmt(c.employed)}</td>
                    <td className="px-3.5 py-3 text-right font-bold text-cyan-300">{fmtPct(c.employment_rate_pct)}</td>
                    <td className="px-3.5 py-3 text-right font-mono text-amber-300">{fmt(c.verified_employed)}</td>
                    <td className="px-3.5 py-3 text-right font-bold text-purple-300">{fmtPct(c.avg_wage_growth_pct)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </SectionCard>
      )}

      {/* District Performance */}
      {districts.length > 0 && (
        <SectionCard title="District Outcomes" icon={MapPin}>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/90 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
                <tr>
                  <th className="px-3.5 py-3">District</th>
                  <th className="px-3.5 py-3">State</th>
                  <th className="px-3.5 py-3 text-right">Trainees</th>
                  <th className="px-3.5 py-3 text-right">Employed</th>
                  <th className="px-3.5 py-3 text-right">Rate</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-200">
                {districts.map((d, i) => (
                  <tr key={i} className="hover:bg-slate-900/40 transition-colors">
                    <td className="px-3.5 py-3 font-semibold text-white">{d.district || '—'}</td>
                    <td className="px-3.5 py-3 text-slate-400">{d.state || '—'}</td>
                    <td className="px-3.5 py-3 text-right font-mono text-blue-300">{fmt(d.total_trainees)}</td>
                    <td className="px-3.5 py-3 text-right font-mono text-emerald-300">{fmt(d.employed)}</td>
                    <td className="px-3.5 py-3 text-right font-bold text-cyan-300">{fmtPct(d.employment_rate_pct)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </SectionCard>
      )}
    </div>
  );
};

// ─── /admin/reports ─────────────────────────────────────────────────────────
const ReportsView = ({ data, onExportCsv }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const s = data?.summary || {};
  const records = data?.records || [];
  const filters = data?.filters_applied || {};

  const filtered = searchTerm
    ? records.filter((r) =>
        Object.values(r).some((v) =>
          String(v || '').toLowerCase().includes(searchTerm.toLowerCase())
        )
      )
    : records;

  return (
    <div className="space-y-6">
      {/* Report header cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        <MetricCard label="Total Records"      value={fmt(data?.total_records)}      icon={FileText}   color="cyan" />
        <MetricCard label="Trainees"           value={fmt(s.total_trainees)}          icon={Users}      color="blue" />
        <MetricCard label="Employed"           value={fmt(s.employed)}                icon={Briefcase}  color="emerald" />
        <MetricCard label="Employment Rate"    value={fmtPct(s.employment_rate_pct)}  icon={TrendingUp} color="purple" />
        <MetricCard label="Completion Rate"    value={fmtPct(s.completion_rate_pct)}  icon={Award}      color="amber" />
      </div>

      {/* Meta / filter info */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-3 text-xs">
          {data?.generated_at && (
            <div className="flex items-center gap-1.5 text-slate-400">
              <Clock className="w-3.5 h-3.5" />
              <span>Generated: {fmtDateTime(data.generated_at)}</span>
            </div>
          )}
          {data?.generated_by && (
            <div className="flex items-center gap-1.5 text-slate-400">
              <User className="w-3.5 h-3.5" />
              <span>By: {data.generated_by}</span>
            </div>
          )}
        </div>
        <button
          onClick={onExportCsv}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600/20 border border-emerald-600/40 text-emerald-300 text-xs font-medium hover:bg-emerald-600/30 transition-colors"
        >
          <Download className="w-3.5 h-3.5" />
          Export CSV
        </button>
      </div>

      {/* Applied filters */}
      {Object.keys(filters).length > 0 && (
        <div className="flex flex-wrap gap-2 items-center text-xs">
          <span className="text-slate-500">Applied filters:</span>
          {Object.entries(filters).map(([k, v]) => (
            <span key={k} className="px-2 py-0.5 rounded-md bg-slate-800 border border-slate-700 text-slate-300 font-mono text-[10px]">
              {k.replace(/_/g, ' ')}: {fmt(v)}
            </span>
          ))}
        </div>
      )}

      {/* Records table */}
      <SectionCard title={`Records (${filtered.length})`} icon={ScrollText}>
        {/* In-table search */}
        <div className="px-4 py-3 border-b border-slate-800">
          <div className="relative max-w-sm">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Filter records..."
              className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-8 pr-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        {filtered.length === 0 ? (
          <EmptyState message="No records match your filters." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/90 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
                <tr>
                  <th className="px-3.5 py-3">ID</th>
                  <th className="px-3.5 py-3">State / District</th>
                  <th className="px-3.5 py-3">Gender</th>
                  <th className="px-3.5 py-3">Education</th>
                  <th className="px-3.5 py-3">Course</th>
                  <th className="px-3.5 py-3">Provider</th>
                  <th className="px-3.5 py-3">Training</th>
                  <th className="px-3.5 py-3">Certificate</th>
                  <th className="px-3.5 py-3">Employment</th>
                  <th className="px-3.5 py-3">Employer</th>
                  <th className="px-3.5 py-3">Job Title</th>
                  <th className="px-3.5 py-3">Joined</th>
                  <th className="px-3.5 py-3">Verification</th>
                  <th className="px-3.5 py-3">Registered</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-200">
                {filtered.map((r, i) => (
                  <tr key={i} className="hover:bg-slate-900/40 transition-colors">
                    <td className="px-3.5 py-2.5 font-mono text-emerald-400 text-[10px] whitespace-nowrap">{fmt(r.skillpulse_id)}</td>
                    <td className="px-3.5 py-2.5 text-slate-300 whitespace-nowrap">
                      {r.district && r.state ? `${r.district}, ${r.state}` : fmt(r.state)}
                    </td>
                    <td className="px-3.5 py-2.5 text-slate-400">{fmt(r.gender)}</td>
                    <td className="px-3.5 py-2.5 text-slate-400 max-w-[120px] truncate">{fmt(r.education)}</td>
                    <td className="px-3.5 py-2.5 text-slate-200 max-w-[160px] truncate">{fmt(r.course_name)}</td>
                    <td className="px-3.5 py-2.5 text-slate-400 max-w-[140px] truncate">{fmt(r.provider_name)}</td>
                    <td className="px-3.5 py-2.5"><StatusBadge status={r.training_status} /></td>
                    <td className="px-3.5 py-2.5"><StatusBadge status={r.certificate_status} /></td>
                    <td className="px-3.5 py-2.5"><StatusBadge status={r.employment_status} /></td>
                    <td className="px-3.5 py-2.5 text-slate-300 max-w-[140px] truncate">{fmt(r.employer_name)}</td>
                    <td className="px-3.5 py-2.5 text-slate-300 max-w-[130px] truncate">{fmt(r.job_title)}</td>
                    <td className="px-3.5 py-2.5 text-slate-400 whitespace-nowrap">{fmtDate(r.joining_date)}</td>
                    <td className="px-3.5 py-2.5"><StatusBadge status={r.verification_status} /></td>
                    <td className="px-3.5 py-2.5 text-slate-400 whitespace-nowrap">{fmtDate(r.registered_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </SectionCard>
    </div>
  );
};

// ─── /admin/settings ────────────────────────────────────────────────────────
const SettingsView = ({ data }) => {
  const profile = data?.admin_profile || {};
  const platform = data?.platform_info || {};

  return (
    <div className="space-y-6">
      {/* Admin Profile Card */}
      <SectionCard title="Admin Profile" icon={User}>
        <div className="p-5 space-y-4">
          {/* Avatar + Name */}
          <div className="flex items-center gap-4 pb-4 border-b border-slate-800">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-600 to-cyan-500 flex items-center justify-center text-white text-xl font-black shrink-0">
              {profile.full_name ? profile.full_name.charAt(0).toUpperCase() : 'A'}
            </div>
            <div>
              <div className="text-lg font-black text-white">{fmt(profile.full_name)}</div>
              <div className="text-xs text-slate-400">{fmt(profile.email)}</div>
              <div className="mt-1 flex gap-2">
                <StatusBadge status={profile.role} />
                <StatusBadge status={profile.is_active ? 'ACTIVE' : 'INACTIVE'} />
              </div>
            </div>
          </div>

          {/* Fields */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            {[
              { label: 'User ID',      value: fmt(profile.id) },
              { label: 'Role',         value: fmt(profile.role) },
              { label: 'Account Status', value: profile.is_active ? 'Active' : 'Inactive' },
              { label: 'Member Since', value: fmtDate(profile.created_at) },
            ].map(({ label, value }) => (
              <div key={label} className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="text-[10px] text-slate-500 uppercase font-mono tracking-wide mb-1">{label}</div>
                <div className="text-sm font-semibold text-white">{value}</div>
              </div>
            ))}
          </div>
        </div>
      </SectionCard>

      {/* Platform Info */}
      <SectionCard title="Platform Information" icon={Server}>
        <div className="p-5">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <MetricCard label="Admin Accounts"   value={fmt(platform.total_admin_accounts)}    icon={Shield}    color="purple" />
            <MetricCard label="Total Users"      value={fmt(platform.total_registered_users)}  icon={Users}     color="cyan" />
          </div>
        </div>
      </SectionCard>

      {/* Platform notes */}
      <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 flex gap-3">
        <Info className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
        <div className="text-xs text-slate-400 leading-relaxed space-y-1">
          <p>Platform settings such as ML thresholds, integration status, and database configuration are managed server-side.</p>
          <p>Contact the system administrator for changes to infrastructure or pipeline configuration.</p>
        </div>
      </div>
    </div>
  );
};

// ─── Trainees Table ──────────────────────────────────────────────────────────
const TraineesView = ({ data }) => {
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
                <td className="px-3.5 py-3"><StatusBadge status={t.training_status} /></td>
                <td className="px-3.5 py-3"><StatusBadge status={t.certificate_status} /></td>
                <td className="px-3.5 py-3"><StatusBadge status={t.employment_status} /></td>
                <td className="px-3.5 py-3"><StatusBadge status={t.verification_status} /></td>
              </tr>
            ))
          ) : (
            <tr><td colSpan={8} className="px-4 py-12 text-center text-slate-400">No trainees match your search or filter.</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

// ─── Users Table ─────────────────────────────────────────────────────────────
const UsersView = ({ data }) => {
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
                <td className="px-3.5 py-3"><StatusBadge status={u.role} /></td>
                <td className="px-3.5 py-3 font-mono text-emerald-400 text-xs">{u.nextup_id || u.skillpulse_id || '—'}</td>
                <td className="px-3.5 py-3 text-slate-300">{u.phone || '—'}</td>
                <td className="px-3.5 py-3"><StatusBadge status={u.is_active ? 'ACTIVE' : 'INACTIVE'} /></td>
                <td className="px-3.5 py-3 text-slate-400 text-[11px]">{fmtDate(u.created_at)}</td>
                <td className="px-3.5 py-3 text-slate-400 text-[11px]">{u.last_login ? fmtDateTime(u.last_login) : 'Never'}</td>
              </tr>
            ))
          ) : (
            <tr><td colSpan={7} className="px-4 py-12 text-center text-slate-400">No users found.</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

// ─── Generic paginated table fallback (Certificates, Employment, Followups, Skill Gaps, Employer Verification, Audit Logs) ───
const GenericTableView = ({ data }) => {
  const items = data?.items || (Array.isArray(data) ? data : []);
  if (items.length === 0) return <EmptyState />;
  const keys = Object.keys(items[0]).filter((k) => k !== 'id' && !k.endsWith('_id'));
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-800">
      <table className="w-full text-left text-xs">
        <thead className="bg-slate-900/90 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
          <tr>
            {keys.slice(0, 8).map((k) => (
              <th key={k} className="px-3.5 py-3">{k.replace(/_/g, ' ')}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/60 text-slate-200">
          {items.map((row, idx) => (
            <tr key={idx} className="hover:bg-slate-900/40 transition-colors">
              {keys.slice(0, 8).map((k) => {
                const val = row[k];
                const strVal = String(val ?? '');
                const isStatus =
                  typeof val === 'string' &&
                  ['COMPLETED','EMPLOYED','VERIFIED','PENDING','ACTIVE','ISSUED','IN_PROGRESS',
                   'SEARCHING','REJECTED','RESPONDED','SENT','SCHEDULED','OVERDUE','NOT_LOOKING',
                   'NOT_APPLICABLE','NOT_REPORTED','NOT_ISSUED','NOT_STARTED'].includes(strVal.toUpperCase());
                const isDate = typeof val === 'string' && /^\d{4}-\d{2}-\d{2}/.test(val);
                return (
                  <td key={k} className="px-3.5 py-3">
                    {isStatus ? (
                      <StatusBadge status={val} />
                    ) : typeof val === 'boolean' ? (
                      <StatusBadge status={val} />
                    ) : isDate ? (
                      <span className="text-slate-400">{fmtDate(val)}</span>
                    ) : typeof val === 'object' && val !== null ? (
                      <span className="text-slate-500 text-[10px] font-mono">[object]</span>
                    ) : (
                      <span className={val === null || val === undefined || val === '' ? 'text-slate-600' : ''}>
                        {fmt(val)}
                      </span>
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
};

// ════════════════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ════════════════════════════════════════════════════════════════════════════

export const AdminSectionView = () => {
  const location = useLocation();
  const path = location.pathname;
  const config = SECTION_CONFIG[path] || {
    title: 'Admin Module',
    subtitle: 'NXTUP administrative management console.',
    icon: Shield,
    fetcher: () => adminAPI.getDashboard(),
    paginated: false,
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

  const handleExportCsv = async () => {
    try {
      const res = await adminAPI.getReports({ format: 'csv' });
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'text/csv' }));
      const a = document.createElement('a');
      a.href = url;
      a.download = `nxtup_report_${new Date().toISOString().slice(0,10)}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch {
      alert('CSV export failed. Please try again.');
    }
  };

  useEffect(() => { setPage(1); }, [path]);
  useEffect(() => { fetchData(); }, [path, page]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchData();
  };

  // ── Loading ──
  if (loading) {
    return (
      <div className="space-y-6">
        <div className="glass-panel-glow rounded-2xl p-6 border-cyan-500/30 flex items-center gap-3.5">
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
        <div className="glass-panel rounded-2xl p-12 border-slate-800 flex flex-col items-center gap-3 text-slate-400">
          <RefreshCw className="w-6 h-6 animate-spin text-emerald-400" />
          <span className="text-xs">Loading {config.title}...</span>
        </div>
      </div>
    );
  }

  // ── Error ──
  if (error) {
    return (
      <div className="space-y-6">
        <div className="glass-panel-glow rounded-2xl p-6 border-cyan-500/30 flex items-center gap-3.5">
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
        <div className="p-6 rounded-2xl bg-red-500/10 border border-red-500/30 text-red-300 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
          <span className="text-xs font-medium">{error}</span>
        </div>
      </div>
    );
  }

  // ── Render page-specific content ──
  const renderContent = () => {
    if (!data) return <EmptyState />;

    if (path === '/admin/trainees') return <TraineesView data={data} />;
    if (path === '/admin/users')    return <UsersView data={data} />;
    if (path === '/admin/training') return <TrainingView data={data} />;
    if (path === '/admin/policy-insights') return <PolicyInsightsView data={data} />;
    if (path === '/admin/reports')  return <ReportsView data={data} onExportCsv={handleExportCsv} />;
    if (path === '/admin/settings') return <SettingsView data={data} />;

    // All remaining paginated sections (certificates, employment, followups, skill-gaps, employer-verification, audit-logs)
    return <GenericTableView data={data} />;
  };

  // Decide whether to show the search bar (not for settings/training/policy-insights)
  const showSearch = ![ '/admin/settings', '/admin/training', '/admin/policy-insights' ].includes(path);

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
          {showSearch && (
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
          )}
          <button
            onClick={fetchData}
            title="Refresh"
            className="p-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-300 hover:text-white transition-all"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="glass-panel rounded-2xl p-6 border-slate-800 space-y-4">
        {renderContent()}

        {/* Pagination — only for paginated endpoints */}
        {config.paginated && data?.pages > 1 && (
          <div className="flex items-center justify-between pt-4 border-t border-slate-800/60 text-xs">
            <span className="text-slate-400">
              Page <strong className="text-white">{data.page}</strong> of{' '}
              <strong className="text-white">{data.pages}</strong> ({data.total} total items)
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
