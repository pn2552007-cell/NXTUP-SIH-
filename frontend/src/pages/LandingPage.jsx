import React from 'react';
import { Link } from 'react-router-dom';
import {
  Activity,
  ArrowRight,
  ShieldCheck,
  Cpu,
  Clock,
  Briefcase,
  TrendingUp,
  BarChart3,
  CheckCircle2,
  Lock,
  Sparkles,
  Building2,
  Users,
  Award,
  Zap,
} from 'lucide-react';
import { Badge } from '../components/common/Badge';

export const LandingPage = () => {
  return (
    <div className="space-y-24 pb-20">
      {/* Hero Section */}
      <section className="relative pt-12 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto overflow-hidden">
        {/* Glow gradients */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-emerald-500/10 blur-[120px] rounded-full pointer-events-none" />
        <div className="absolute top-1/3 left-1/3 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[250px] bg-cyan-500/10 blur-[100px] rounded-full pointer-events-none" />

        <div className="relative text-center space-y-6 max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900/80 border border-emerald-500/30 text-xs font-semibold text-emerald-400 shadow-lg shadow-emerald-950/50">
            <Sparkles className="w-3.5 h-3.5" />
            <span>National Skilling Longitudinal Outcome Engine</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-tight">
            NEXTUP
            <span className="block text-2xl sm:text-3xl lg:text-4xl mt-2 font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400">
              AI-Powered Longitudinal Skilling Outcome Platform
            </span>
          </h1>

          <p className="text-base sm:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Bridging India's post-skilling data gap with persistent <strong>NEXTUP IDs</strong>, 
            machine learning placement risk prediction, dual employer verification, and longitudinal wage retention tracking.
          </p>

          {/* CTAs */}
          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <Link
              to="/register"
              className="px-6 py-3.5 rounded-xl font-bold text-sm bg-emerald-600 hover:bg-emerald-500 text-white transition-all shadow-xl shadow-emerald-950 flex items-center gap-2 group"
            >
              <span>Get Started</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              to="/login"
              className="px-6 py-3.5 rounded-xl font-bold text-sm bg-slate-900/90 hover:bg-slate-800 text-slate-200 border border-slate-700 transition-all flex items-center gap-2"
            >
              <Activity className="w-4 h-4 text-emerald-400" />
              <span>Sign In with Demo Accounts</span>
            </Link>
          </div>

          {/* Trainee Journey Pipeline Flow */}
          <div className="pt-10">
            <div className="glass-panel-glow rounded-2xl p-6 border border-emerald-500/20">
              <div className="text-xs uppercase font-bold tracking-widest text-emerald-400 mb-4 text-left">
                Unified Longitudinal Outcome Pipeline (NEXTUP)
              </div>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-left">
                <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
                  <div className="text-[10px] font-mono text-emerald-400 font-bold">01 • ENROLLMENT</div>
                  <div className="text-xs font-semibold text-white">Persistent ID</div>
                  <div className="text-[11px] text-slate-400">DPDP consent & NXT-2026-XXXXXX generation</div>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
                  <div className="text-[10px] font-mono text-teal-400 font-bold">02 • TRAINING</div>
                  <div className="text-xs font-semibold text-white">Course Milestones</div>
                  <div className="text-[11px] text-slate-400">Attendance, quiz scores & skill badges</div>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
                  <div className="text-[10px] font-mono text-cyan-400 font-bold">03 • AI RISK ENGINE</div>
                  <div className="text-xs font-semibold text-white">Risk Prediction</div>
                  <div className="text-[11px] text-slate-400">RandomForest model detects placement risk</div>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
                  <div className="text-[10px] font-mono text-blue-400 font-bold">04 • PLACEMENT</div>
                  <div className="text-xs font-semibold text-white">Dual Verification</div>
                  <div className="text-[11px] text-slate-400">Employer verifies joining, CTC & designation</div>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1 col-span-2 md:col-span-1">
                  <div className="text-[10px] font-mono text-purple-400 font-bold">05 • RETENTION</div>
                  <div className="text-xs font-semibold text-white">Longitudinal Tracking</div>
                  <div className="text-[11px] text-slate-400">3, 6, 12-month follow-up & wage trajectory</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Problem vs NEXTUP Solution */}
      <section className="px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="glass-panel rounded-2xl p-8 border-rose-500/20 space-y-4">
            <div className="flex items-center gap-2 text-rose-400 text-xs font-bold uppercase tracking-wider">
              <span>The National Skilling Blindspot</span>
            </div>
            <h3 className="text-2xl font-bold text-white">Fragmented Post-Training Data</h3>
            <ul className="space-y-3 text-sm text-slate-300">
              <li className="flex items-start gap-2.5">
                <span className="text-rose-400 font-bold">•</span>
                <span>Trainees vanish from records after certificate issuance; no unified national identifier.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="text-rose-400 font-bold">•</span>
                <span>Placement data is self-reported or unverified without tamper-proof employer validation.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="text-rose-400 font-bold">•</span>
                <span>Zero proactive early-warning system to identify struggling trainees before course completion.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="text-rose-400 font-bold">•</span>
                <span>No visibility into whether trainees remain employed at 6 or 12 months with wage progression.</span>
              </li>
            </ul>
          </div>

          <div className="glass-panel rounded-2xl p-8 border-emerald-500/20 space-y-4">
            <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold uppercase tracking-wider">
              <span>The NEXTUP Solution</span>
            </div>
            <h3 className="text-2xl font-bold text-white">AI-Powered Longitudinal Lifecycle</h3>
            <ul className="space-y-3 text-sm text-slate-300">
              <li className="flex items-start gap-2.5">
                <span className="text-emerald-400 font-bold">•</span>
                <span>Persistent NEXTUP ID connects training, certification, and verified employment across life.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="text-emerald-400 font-bold">•</span>
                <span>Production ML Risk Pipeline (RandomForest / GradientBoosting) predicts placement dropout risks early.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="text-emerald-400 font-bold">•</span>
                <span>Dual verification workflow where employers confirm joining dates, job titles, and compensation.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="text-emerald-400 font-bold">•</span>
                <span>Automated targeted skilling interventions (Mentorship, Mock Interviews, Bridge Courses).</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* Stakeholder Portals */}
      <section className="px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8">
        <div className="text-center space-y-2">
          <h2 className="text-3xl font-extrabold text-white">Built for Every Stakeholder</h2>
          <p className="text-xs sm:text-sm text-slate-400">
            Dedicated role-based portals for trainees, employers, training providers, and policymakers.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Trainee Card */}
          <div className="glass-panel rounded-2xl p-6 flex flex-col justify-between space-y-4 hover:border-emerald-500/40 transition-all">
            <div className="space-y-3">
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 w-fit">
                <Users className="w-6 h-6" />
              </div>
              <h4 className="text-lg font-bold text-white">Trainee Portal</h4>
              <p className="text-xs text-slate-300 leading-relaxed">
                Consent capture, unique NEXTUP ID, interactive milestone journey, AI placement risk score, targeted interventions, and wage charts.
              </p>
            </div>
            <Link
              to="/login"
              className="w-full py-2.5 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition-colors text-center block"
            >
              Access Trainee Portal →
            </Link>
          </div>

          {/* Employer Card */}
          <div className="glass-panel rounded-2xl p-6 flex flex-col justify-between space-y-4 hover:border-blue-500/40 transition-all">
            <div className="space-y-3">
              <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 w-fit">
                <Briefcase className="w-6 h-6" />
              </div>
              <h4 className="text-lg font-bold text-white">Employer Portal</h4>
              <p className="text-xs text-slate-300 leading-relaxed">
                Review and verify trainee employment, confirm joining dates and salaries, search candidate talent pools with skill match scoring.
              </p>
            </div>
            <Link
              to="/login"
              className="w-full py-2.5 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white transition-colors text-center block"
            >
              Access Employer Portal →
            </Link>
          </div>

          {/* Provider Card */}
          <div className="glass-panel rounded-2xl p-6 flex flex-col justify-between space-y-4 hover:border-purple-500/40 transition-all">
            <div className="space-y-3">
              <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400 w-fit">
                <Building2 className="w-6 h-6" />
              </div>
              <h4 className="text-lg font-bold text-white">Provider Portal</h4>
              <p className="text-xs text-slate-300 leading-relaxed">
                Batch management, cohort risk monitoring, placement conversion analytics, and bulk CSV trainee batch ingestion with instant NEXTUP ID creation.
              </p>
            </div>
            <Link
              to="/login"
              className="w-full py-2.5 rounded-xl text-xs font-bold bg-purple-600 hover:bg-purple-500 text-white transition-colors text-center block"
            >
              Access Provider Portal →
            </Link>
          </div>

          {/* Admin Card */}
          <div className="glass-panel rounded-2xl p-6 flex flex-col justify-between space-y-4 hover:border-cyan-500/40 transition-all">
            <div className="space-y-3">
              <div className="p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 w-fit">
                <BarChart3 className="w-6 h-6" />
              </div>
              <h4 className="text-lg font-bold text-white">Govt / Admin Portal</h4>
              <p className="text-xs text-slate-300 leading-relaxed">
                Macro outcome metrics: 6-month retention rate, average wage growth (%), placement conversion, district heatmaps, and ML model performance metrics.
              </p>
            </div>
            <Link
              to="/login"
              className="w-full py-2.5 rounded-xl text-xs font-bold bg-cyan-600 hover:bg-cyan-500 text-white transition-colors text-center block"
            >
              Access Admin Portal →
            </Link>
          </div>
        </div>
      </section>

      {/* Live vs Planned Status Table */}
      <section className="px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="glass-panel rounded-2xl p-6 border-slate-800 space-y-4">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-emerald-400" />
            <h3 className="text-lg font-bold text-white">Implementation Status & Roadmap</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left text-slate-300">
              <thead className="bg-slate-900/60 text-slate-400 font-semibold border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-4">Feature / Module</th>
                  <th className="py-2.5 px-4">Status</th>
                  <th className="py-2.5 px-4">Description</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                <tr>
                  <td className="py-2.5 px-4 font-semibold text-white">Persistent Trainee ID (NXT-YYYY-XXXXXX)</td>
                  <td className="py-2.5 px-4"><span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-mono text-[10px] font-bold">LIVE</span></td>
                  <td className="py-2.5 px-4 text-slate-400">Unique deterministic identifier linked to trainee consent & lifetime profile.</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-4 font-semibold text-white">ML Placement Risk Engine</td>
                  <td className="py-2.5 px-4"><span className="px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400 font-mono text-[10px] font-bold">PLANNED — prototype</span></td>
                  <td className="py-2.5 px-4 text-slate-400">Experimental scoring aid trained on synthetic demo data. No accuracy is claimed until trained and evaluated on real verified outcome data.</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-4 font-semibold text-white">Dual Employer Employment Verification</td>
                  <td className="py-2.5 px-4"><span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-mono text-[10px] font-bold">LIVE</span></td>
                  <td className="py-2.5 px-4 text-slate-400">Employer verification loop for verified salary, designation, joining date, and attrition.</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-4 font-semibold text-white">Longitudinal Retention & Wage Analytics</td>
                  <td className="py-2.5 px-4"><span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-mono text-[10px] font-bold">LIVE</span></td>
                  <td className="py-2.5 px-4 text-slate-400">3, 6, and 12-month follow-up milestones, salary growth tracking, and state/district reporting.</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-4 font-semibold text-white">DPDP Act Explicit Consent Framework</td>
                  <td className="py-2.5 px-4"><span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-mono text-[10px] font-bold">LIVE</span></td>
                  <td className="py-2.5 px-4 text-slate-400">Timestamped consent capture with version tracking and revoke options before tracking begins.</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-4 font-semibold text-white">National DigiLocker & Aadhaar Vault API</td>
                  <td className="py-2.5 px-4"><span className="px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 font-mono text-[10px] font-bold">PLANNED</span></td>
                  <td className="py-2.5 px-4 text-slate-400">Production integration via India Stack APIs pending sandbox access approval.</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-4 font-semibold text-white">EPFO / ESIC Real-time Contribution Sync</td>
                  <td className="py-2.5 px-4"><span className="px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 font-mono text-[10px] font-bold">PLANNED</span></td>
                  <td className="py-2.5 px-4 text-slate-400">Automated institutional employment cross-check with statutory PF/ESI databases.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Privacy & Consent Banner */}
      <section className="px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="glass-panel rounded-2xl p-8 border-slate-800 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold">
              <Lock className="w-4 h-4" />
              <span>Privacy-First Architecture • DPDP Act & GDPR Compliant</span>
            </div>
            <h3 className="text-xl font-bold text-white">Your Data, Your Consent</h3>
            <p className="text-xs text-slate-400 max-w-xl">
              NEXTUP mandates explicit trainee consent before longitudinal tracking begins. Trainee records are pseudonymized, timestamped with version control, and auditable across all transactions.
            </p>
          </div>
          <Link
            to="/consent"
            className="px-5 py-2.5 rounded-xl text-xs font-bold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors shrink-0"
          >
            Review Consent Framework
          </Link>
        </div>
      </section>
    </div>
  );
};
