import React from 'react';

const STATUS_STYLES = {
  // Employment
  EMPLOYED:       'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
  SEEKING:        'bg-amber-500/15 text-amber-300 border-amber-500/30',
  SELF_EMPLOYED:  'bg-cyan-500/15 text-cyan-300 border-cyan-500/30',
  NOT_SEEKING:    'bg-slate-500/15 text-slate-300 border-slate-500/30',
  NOT_REPORTED:   'bg-slate-600/15 text-slate-400 border-slate-600/30',
  UNKNOWN:        'bg-slate-600/15 text-slate-400 border-slate-600/30',

  // Training
  COMPLETED:      'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
  IN_PROGRESS:    'bg-blue-500/15 text-blue-300 border-blue-500/30',
  DROPPED:        'bg-red-500/15 text-red-300 border-red-500/30',
  NOT_STARTED:    'bg-slate-600/15 text-slate-400 border-slate-600/30',
  ENROLLED:       'bg-indigo-500/15 text-indigo-300 border-indigo-500/30',

  // Verification
  VERIFIED:       'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
  PENDING:        'bg-amber-500/15 text-amber-300 border-amber-500/30',
  REJECTED:       'bg-red-500/15 text-red-300 border-red-500/30',

  // Certificates
  ISSUED:         'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
  REVOKED:        'bg-red-500/15 text-red-300 border-red-500/30',
  EXPIRED:        'bg-orange-500/15 text-orange-300 border-orange-500/30',
  NOT_ISSUED:     'bg-slate-600/15 text-slate-400 border-slate-600/30',

  // Users
  ADMIN:              'bg-purple-500/15 text-purple-300 border-purple-500/30',
  TRAINING_PROVIDER:  'bg-cyan-500/15 text-cyan-300 border-cyan-500/30',
  TRAINEE:            'bg-blue-500/15 text-blue-300 border-blue-500/30',
  EMPLOYER:           'bg-indigo-500/15 text-indigo-300 border-indigo-500/30',

  // Followups
  SCHEDULED:      'bg-blue-500/15 text-blue-300 border-blue-500/30',
  SENT:           'bg-indigo-500/15 text-indigo-300 border-indigo-500/30',
  RESPONDED:      'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
  OVERDUE:        'bg-red-500/15 text-red-300 border-red-500/30',

  // Boolean
  true:           'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
  false:          'bg-slate-600/15 text-slate-400 border-slate-600/30',
};

export const StatusBadge = ({ status, className = '' }) => {
  if (!status && status !== false) return <span className="text-slate-500 text-xs">—</span>;

  const key = String(status).toUpperCase() === 'TRUE' ? 'true' :
              String(status).toUpperCase() === 'FALSE' ? 'false' :
              String(status).toUpperCase();

  const style = STATUS_STYLES[key] || 'bg-slate-700/20 text-slate-400 border-slate-700/30';

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider border ${style} ${className}`}>
      {String(status).replace(/_/g, ' ')}
    </span>
  );
};
