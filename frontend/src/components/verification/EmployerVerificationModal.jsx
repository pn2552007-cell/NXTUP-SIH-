import React, { useState } from 'react';
import { employerAPI } from '../../services/api';
import { useToast } from '../../contexts/ToastContext';
import { Modal } from '../common/Modal';
import { CheckCircle2, XCircle, AlertCircle, Building2, Calendar, DollarSign, Briefcase } from 'lucide-react';

export const EmployerVerificationModal = ({ isOpen, onClose, requestItem, onSuccess }) => {
  const { showSuccess, showError } = useToast();
  const [action, setAction] = useState('VERIFIED'); // VERIFIED, REJECTED, CORRECTION_REQUESTED
  const [verifiedSalary, setVerifiedSalary] = useState(requestItem?.reported_salary || 25000);
  const [verifiedJobTitle, setVerifiedJobTitle] = useState(requestItem?.reported_job || '');
  const [verifiedJoiningDate, setVerifiedJoiningDate] = useState(requestItem?.reported_joining_date || '');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  if (!requestItem) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await employerAPI.verify({
        employment_record_id: requestItem.employment_record_id,
        status: action,
        notes,
        verified_salary: action === 'VERIFIED' ? Number(verifiedSalary) : null,
        verified_job_title: action === 'VERIFIED' ? verifiedJobTitle : null,
        verified_joining_date: action === 'VERIFIED' ? verifiedJoiningDate : null,
      });

      showSuccess(`Employment record ${action.toLowerCase()} successfully!`);
      if (onSuccess) onSuccess();
      onClose();
    } catch (err) {
      showError('Failed to record employer verification');
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Employer Verification Portal">
      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Candidate & Reported Details */}
        <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <div>
              <div className="text-sm font-bold text-white">{requestItem.trainee_name}</div>
              <div className="text-xs font-mono text-emerald-400">ID: {requestItem.skillpulse_id}</div>
            </div>
            <span className="text-xs px-2 py-1 rounded bg-slate-800 text-slate-300 font-medium">
              {requestItem.course_name}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="flex items-center gap-2 text-slate-300">
              <Briefcase className="w-3.5 h-3.5 text-slate-400" />
              <span>Reported Role: <strong>{requestItem.reported_job}</strong></span>
            </div>
            <div className="flex items-center gap-2 text-slate-300">
              <Calendar className="w-3.5 h-3.5 text-slate-400" />
              <span>Joining Date: <strong>{requestItem.reported_joining_date}</strong></span>
            </div>
            <div className="flex items-center gap-2 text-slate-300">
              <DollarSign className="w-3.5 h-3.5 text-slate-400" />
              <span>Reported Salary: <strong>₹{requestItem.reported_salary?.toLocaleString()}/mo</strong></span>
            </div>
            <div className="flex items-center gap-2 text-slate-300">
              <Building2 className="w-3.5 h-3.5 text-slate-400" />
              <span>Location: <strong>{requestItem.reported_location}</strong></span>
            </div>
          </div>
        </div>

        {/* Verification Action Selection */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-2">
            Verification Decision
          </label>
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => setAction('VERIFIED')}
              className={`p-3 rounded-xl border flex flex-col items-center gap-1.5 text-xs font-semibold transition-all ${
                action === 'VERIFIED'
                  ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300 shadow-md shadow-emerald-950'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>✓ Verify</span>
            </button>

            <button
              type="button"
              onClick={() => setAction('REJECTED')}
              className={`p-3 rounded-xl border flex flex-col items-center gap-1.5 text-xs font-semibold transition-all ${
                action === 'REJECTED'
                  ? 'bg-rose-500/20 border-rose-500 text-rose-300 shadow-md shadow-rose-950'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              <XCircle className="w-4 h-4 text-rose-400" />
              <span>✗ Reject</span>
            </button>

            <button
              type="button"
              onClick={() => setAction('CORRECTION_REQUESTED')}
              className={`p-3 rounded-xl border flex flex-col items-center gap-1.5 text-xs font-semibold transition-all ${
                action === 'CORRECTION_REQUESTED'
                  ? 'bg-amber-500/20 border-amber-500 text-amber-300 shadow-md shadow-amber-950'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              <AlertCircle className="w-4 h-4 text-amber-400" />
              <span>↻ Correction</span>
            </button>
          </div>
        </div>

        {/* Form fields for verified specifics if approving */}
        {action === 'VERIFIED' && (
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <label className="block text-slate-400 mb-1">Confirmed Job Title</label>
              <input
                type="text"
                value={verifiedJobTitle}
                onChange={(e) => setVerifiedJobTitle(e.target.value)}
                placeholder="Job Title"
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
              />
            </div>
            <div>
              <label className="block text-slate-400 mb-1">Confirmed Monthly Salary (₹)</label>
              <input
                type="number"
                value={verifiedSalary}
                onChange={(e) => setVerifiedSalary(e.target.value)}
                placeholder="25000"
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
              />
            </div>
          </div>
        )}

        {/* Notes */}
        <div>
          <label className="block text-xs text-slate-400 mb-1">HR Verification Notes / Remarks</label>
          <textarea
            rows="2"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="e.g., Verified active on payroll under Q1 campus recruitment drive."
            className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
          />
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="px-5 py-2 rounded-xl text-xs font-bold bg-emerald-600 text-white hover:bg-emerald-500 transition-all shadow-lg shadow-emerald-950 disabled:opacity-50"
          >
            {submitting ? 'Submitting...' : 'Submit Verification'}
          </button>
        </div>
      </form>
    </Modal>
  );
};
