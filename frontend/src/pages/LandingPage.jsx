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
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/80 border border-emerald-500/30 text-xs font-semibold text-emerald-400 shadow-lg shadow-emerald-950/50">
            <Sparkles className="w-3.5 h-3.5" />
            <span>National Skilling Longitudinal Outcome Engine</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-tight">
            SkillPulse
            <span className="block text-2xl sm:text-3xl lg:text-4xl mt-2 font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400">
              Track the journey from training to real-world impact.
            </span>
          </h1>

          <p className="text-base sm:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Solving the fragmented post-skilling data gap. Connect institutional training and certification
            directly to verified employment, 12-month retention, and wage progression.
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
              <span>Sign In to Portal</span>
            </Link>
          </div>

          {/* Trainee Journey Pipeline Flow */}
          <div className="pt-10">
            <div className="glass-panel-glow rounded-2xl p-6 border border-emerald-500/20">
              <div className="text-xs uppercase font-bold tracking-widest text-emerald-400 mb-4 text-left">
                Longitudinal Outcome Pipeline
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3 text-left">
                {[
                  { title: '1. Training', desc: 'Curriculum & Batches', icon: Building2 },
                  { title: '2. Certification', desc: 'Dynamic Assessment', icon: Award },
                  { title: '3. Employment', desc: 'Verified Job & Wage', icon: Briefcase },
                  { title: '4. Retention', desc: '6 & 12 Month Milestones', icon: CheckCircle2 },
                  { title: '5. Wage Growth', desc: 'Real Salary Progression', icon: TrendingUp },
                  { title: '6. Macro Impact', desc: 'National Skill Analytics', icon: ShieldCheck },
                ].map((item, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                    <div className="flex items-center justify-between mb-1.5">
                      <item.icon className="w-4 h-4 text-emerald-400" />
                      <span className="text-[10px] text-emerald-400 font-mono">0{idx + 1}</span>
                    </div>
                    <div className="text-xs font-bold text-white">{item.title}</div>
                    <div className="text-[10px] text-slate-400 mt-0.5">{item.desc}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* The Problem & The Solution */}
      <section className="px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="glass-panel rounded-2xl p-8 border-rose-500/20 space-y-4">
            <div className="flex items-center gap-2 text-rose-400 text-xs font-bold uppercase tracking-wider">
              <span>The Current Challenge</span>
            </div>
            <h3 className="text-2xl font-bold text-white">The "Black Hole" After Skilling</h3>
            <ul className="space-y-3 text-sm text-slate-300">
              <li className="flex items-start gap-2.5">
                <span className="text-rose-400 font-bold">•</span>
                <span>Government and institutions lose visibility the moment training certificates are issued.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="text-rose-400 font-bold">•</span>
                <span>Placement data is often self-reported or unverified without employer validation.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="text-rose-400 font-bold">•</span>
                <span>No long-term visibility into whether trainees remain employed at 6 or 12 months.</span>
              </li>
            </ul>
          </div>

          <div className="glass-panel rounded-2xl p-8 border-emerald-500/20 space-y-4">
            <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold uppercase tracking-wider">
              <span>The SkillPulse Solution</span>
            </div>
            <h3 className="text-2xl font-bold text-white">Unified Longitudinal Tracking</h3>
            <ul className="space-y-3 text-sm text-slate-300">
              <li className="flex items-start gap-2.5">
                <span className="text-emerald-400 font-bold">•</span>
                <span>Persistent SkillPulse ID connects training, certification, and verified employment.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="text-emerald-400 font-bold">•</span>
                <span>Dual verification workflow where employers confirm joining dates, job titles, and pay.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="text-emerald-400 font-bold">•</span>
                <span>AI-powered skill-gap detection highlights missing competencies against target roles.</span>
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
                Consent capture, unique SkillPulse ID, interactive milestone journey, AI skill gap analysis, employment reporting, and wage charts.
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
                Review and verify trainee employment, confirm joining dates and salaries, search candidate talent pools with AI skill match scoring.
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
                Batch management, placement conversion analytics, course outcome benchmarking, and bulk CSV trainee batch ingestion.
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
                Macro outcome metrics: 6-month retention rate, average wage growth (%), placement conversion, district trends, and provider impact rankings.
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
              SkillPulse mandates explicit trainee consent before longitudinal tracking begins. Trainee records are pseudonymized, timestamped with version control, and auditable across all transactions.
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
