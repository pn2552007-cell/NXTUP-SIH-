import React from 'react';
import {
  CheckCircle2,
  Clock,
  HelpCircle,
  Briefcase,
  Award,
  GraduationCap,
  TrendingUp,
  ShieldCheck,
  Building2,
} from 'lucide-react';
import { Badge } from '../common/Badge';

const verificationBadge = (status) => {
  if (status === 'VERIFIED') return <Badge variant="emerald">Employer verified</Badge>;
  if (status === 'REJECTED') return <Badge variant="rose">Rejected by employer</Badge>;
  if (status === 'CORRECTION_REQUESTED') return <Badge variant="amber">Correction requested</Badge>;
  if (status) return <Badge variant="amber">Self-reported — unverified</Badge>;
  return <Badge variant="slate">Not reported</Badge>;
};

export const TraineeJourneyTracker = ({ profile, journey = [] }) => {
  const employmentVerified = profile?.verification_status === 'VERIFIED';
  const employmentCorrection = profile?.verification_status === 'CORRECTION_REQUESTED';
  const defaultSteps = [
    {
      id: 'CONSENT',
      label: 'Consent & ID',
      icon: ShieldCheck,
      status: profile?.consent_given ? 'COMPLETED' : 'IN_PROGRESS',
      detail: profile?.nextup_id || profile?.skillpulse_id || 'Pending Consent',
      date: profile?.consent_given ? 'DPDP consent active' : 'Step 1',
    },
    {
      id: 'TRAINING',
      label: 'Training',
      icon: GraduationCap,
      status: profile?.training_completion === 'COMPLETED' ? 'COMPLETED' : profile?.training_completion === 'NO_TRAINING_RECORD' ? 'PENDING' : 'IN_PROGRESS',
      detail: profile?.course_name || 'No training record yet',
      date: profile?.attendance_pct != null ? `${profile.attendance_pct}% Attendance` : 'Attendance pending',
    },
    {
      id: 'CERTIFICATION',
      label: 'Certification',
      icon: Award,
      status: profile?.certification_status === 'ISSUED' ? 'COMPLETED' : 'PENDING',
      detail: profile?.certificate_number || 'No certificate issued',
      date: profile?.assessment_score != null ? `Score: ${profile.assessment_score}/100` : 'Assessment pending',
    },
    {
      id: 'EMPLOYMENT',
      label: 'Employment',
      icon: Briefcase,
      status: employmentVerified ? 'COMPLETED' : profile?.employment_status === 'EMPLOYED' ? 'IN_PROGRESS' : 'PENDING',
      detail: profile?.current_employer ? `${profile.current_job || 'Role'} at ${profile.current_employer}` : 'No employment reported',
      date: profile?.verification_status === 'VERIFIED' ? 'Employer verified' : employmentCorrection ? 'Correction requested' : profile?.employment_status === 'EMPLOYED' ? 'Self-reported — unverified' : 'Awaiting report',
    },
    {
      id: 'RETENTION',
      label: '6-Mo Retention',
      icon: Building2,
      status: profile?.retention_6m ? 'COMPLETED' : profile?.employment_status === 'EMPLOYED' ? 'IN_PROGRESS' : 'PENDING',
      detail: profile?.retention_6m ? 'Active in Industry' : 'Tracking in progress',
      date: profile?.retention_6m ? 'Follow-up responded' : 'Checkpoint',
    },
    {
      id: 'WAGE_GROWTH',
      label: 'Wage Growth',
      icon: TrendingUp,
      status: (profile?.wage_growth_pct || 0) > 0 ? 'COMPLETED' : profile?.current_salary ? 'IN_PROGRESS' : 'PENDING',
      detail: profile?.current_salary ? `₹${Number(profile.current_salary).toLocaleString()}/mo` : 'No wage reported',
      date: profile?.wage_growth_pct != null ? `+${profile.wage_growth_pct}% Growth` : 'Growth pending',
    },
  ];

  return (
    <div className="glass-panel rounded-2xl p-6 relative overflow-hidden">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            Longitudinal Outcome Journey
            <Badge variant="emerald">Live Outcome Pipeline</Badge>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            End-to-end milestone progression from institutional skilling to post-training employment & wage growth.
          </p>
        </div>
        {(profile?.nextup_id || profile?.skillpulse_id) && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-emerald-500/30 font-mono text-xs text-emerald-400 font-bold">
            <span>NXTUP ID:</span>
            <span className="text-white">{profile.nextup_id || profile.skillpulse_id}</span>
          </div>
        )}
      </div>

      {/* Horizontal Step Timeline */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {defaultSteps.map((step, idx) => {
          const Icon = step.icon;
          const isCompleted = step.status === 'COMPLETED';
          const isInProgress = step.status === 'IN_PROGRESS';

          return (
            <div
              key={step.id}
              className={`p-4 rounded-xl border transition-all duration-300 relative ${
                isCompleted
                  ? 'bg-slate-900/90 border-emerald-500/40 shadow-sm'
                  : isInProgress
                  ? 'bg-slate-900/60 border-cyan-500/40'
                  : 'bg-slate-950/40 border-slate-800 opacity-60'
              }`}
            >
              {/* Step number */}
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-bold text-slate-400 font-mono">0{idx + 1}</span>
                {isCompleted ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                ) : isInProgress ? (
                  <Clock className="w-4 h-4 text-cyan-400 animate-pulse" />
                ) : (
                  <HelpCircle className="w-4 h-4 text-slate-400" />
                )}
              </div>

              {/* Icon & Label */}
              <div className="flex items-center gap-2 mb-2">
                <div
                  className={`p-2 rounded-lg ${
                    isCompleted
                      ? 'bg-emerald-500/20 text-emerald-400'
                      : isInProgress
                      ? 'bg-cyan-500/20 text-cyan-400'
                      : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                </div>
                <div className="text-xs font-bold text-slate-200 truncate">{step.label}</div>
              </div>

              {/* Detail & Date */}
              <div className="text-[11px] text-slate-300 font-medium truncate" title={step.detail}>
                {step.detail}
              </div>
              <div className="text-[10px] text-slate-400 mt-1 font-mono">{step.date}</div>
            </div>
          );
        })}
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2">
        {verificationBadge(profile?.verification_status)}
        {profile?.data_trust_note && (
          <span className="text-[11px] text-slate-500">{profile.data_trust_note}</span>
        )}
      </div>
    </div>
  );
};
