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

export const TraineeJourneyTracker = ({ profile, journey = [] }) => {
  const defaultSteps = [
    {
      id: 'CONSENT',
      label: 'Consent & ID',
      icon: ShieldCheck,
      status: profile?.consent_given ? 'COMPLETED' : 'IN_PROGRESS',
      detail: profile?.skillpulse_id || 'Pending Consent',
      date: 'Step 1',
    },
    {
      id: 'TRAINING',
      label: 'Training',
      icon: GraduationCap,
      status: profile?.training_completion === 'COMPLETED' ? 'COMPLETED' : 'IN_PROGRESS',
      detail: profile?.course_name || 'Full Stack Engineering',
      date: `${profile?.attendance_pct || 95}% Attendance`,
    },
    {
      id: 'CERTIFICATION',
      label: 'Certification',
      icon: Award,
      status: profile?.certification_status === 'ISSUED' ? 'COMPLETED' : 'IN_PROGRESS',
      detail: profile?.certificate_number || 'Assessment: 88%',
      date: `Score: ${profile?.assessment_score || 88}/100`,
    },
    {
      id: 'EMPLOYMENT',
      label: 'Employment',
      icon: Briefcase,
      status: profile?.employment_status === 'EMPLOYED' ? 'COMPLETED' : (profile?.employment_status === 'SEARCHING' ? 'IN_PROGRESS' : 'PENDING'),
      detail: profile?.current_employer ? `${profile.current_job} at ${profile.current_employer}` : 'Searching Opportunities',
      date: profile?.verification_status === 'VERIFIED' ? 'Verified ✓' : 'Pending Verification',
    },
    {
      id: 'RETENTION',
      label: '6-Mo Retention',
      icon: Building2,
      status: profile?.retention_6m ? 'COMPLETED' : (profile?.employment_status === 'EMPLOYED' ? 'IN_PROGRESS' : 'PENDING'),
      detail: profile?.retention_6m ? 'Active in Industry' : 'Tracking in progress',
      date: profile?.retention_6m ? 'Verified ✓' : 'Checkpoint',
    },
    {
      id: 'WAGE_GROWTH',
      label: 'Wage Growth',
      icon: TrendingUp,
      status: profile?.wage_growth_pct > 0 ? 'COMPLETED' : 'IN_PROGRESS',
      detail: profile?.current_salary ? `₹${profile.current_salary.toLocaleString()}/mo` : 'Baseline: ₹20k',
      date: `+${profile?.wage_growth_pct || 33.3}% Growth`,
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
        {profile?.skillpulse_id && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-emerald-500/30 font-mono text-xs text-emerald-400 font-bold">
            <span>SkillPulse ID:</span>
            <span className="text-white">{profile.skillpulse_id}</span>
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
    </div>
  );
};
