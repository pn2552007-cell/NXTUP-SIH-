import React, { useState } from 'react';
import { followupsAPI } from '../../services/api';
import { useToast } from '../../contexts/ToastContext';
import { CheckCircle2, Clock, Send, MessageSquare, AlertCircle, Sparkles } from 'lucide-react';
import { Badge } from '../common/Badge';

export const FollowupTimeline = ({ followups = [], onUpdated }) => {
  const { showSuccess, showError } = useToast();
  const [selectedFollowup, setSelectedFollowup] = useState(null);
  const [employed, setEmployed] = useState(true);
  const [currentSalary, setCurrentSalary] = useState('');
  const [satisfaction, setSatisfaction] = useState(5);
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [triggering, setTriggering] = useState(false);

  const checkpointsMap = {
    '30_DAYS': { label: '30-Day Checkpoint', prompt: 'Have you found an employment opportunity or internship post-training?' },
    '90_DAYS': { label: '90-Day Checkpoint', prompt: 'Are you currently employed, on probation, or interviewing?' },
    '6_MONTHS': { label: '6-Month Retention', prompt: 'Are you still with the same employer? Report current salary progression.' },
    '12_MONTHS': { label: '12-Month Progression', prompt: 'Tell us about your 1-year longitudinal career growth, promotions, and new skills.' },
  };

  const handleOpenResponder = (fup) => {
    setSelectedFollowup(fup);
    setEmployed(fup.response_data?.employed ?? true);
    setCurrentSalary(fup.response_data?.salary || fup.response_data?.current_salary || '');
    setSatisfaction(fup.response_data?.satisfaction || 5);
    setNotes(fup.response_data?.notes || '');
  };

  const handleSubmitResponse = async (e) => {
    e.preventDefault();
    if (!selectedFollowup) return;

    setSubmitting(true);
    try {
      await followupsAPI.respond({
        followup_id: selectedFollowup.id,
        employed,
        current_salary: currentSalary ? Number(currentSalary) : null,
        same_employer: true,
        job_satisfaction: Number(satisfaction),
        notes,
      });

      showSuccess(`Response submitted for ${checkpointsMap[selectedFollowup.checkpoint]?.label || selectedFollowup.checkpoint}`);
      setSelectedFollowup(null);
      if (onUpdated) onUpdated();
    } catch (err) {
      showError('Failed to record follow-up response');
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleSimulateMockDispatch = async (cp) => {
    setTriggering(true);
    try {
      const res = await followupsAPI.triggerMock(cp);
      showSuccess(`[Mock Gateway] Dispatched simulated ${res.data.channel} follow-up message`);
      if (onUpdated) onUpdated();
    } catch (err) {
      showError('Mock notification dispatch failed');
      console.error(err);
    } finally {
      setTriggering(false);
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 relative overflow-hidden">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            Automated Longitudinal Follow-up Engine
            <Badge variant="purple">Multi-Checkpoint Tracking</Badge>
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Automated post-training check-ins at 30 days, 90 days, 6 months, and 12 months.
          </p>
        </div>
      </div>

      {/* Timeline Steps */}
      <div className="space-y-4">
        {followups.map((fup, idx) => {
          const cpInfo = checkpointsMap[fup.checkpoint] || { label: fup.checkpoint, prompt: 'Post-skilling check-in' };
          const isResponded = fup.status === 'RESPONDED';
          const isSent = fup.status === 'SENT';

          return (
            <div
              key={fup.id || idx}
              className={`p-4 rounded-xl border transition-all ${
                isResponded
                  ? 'bg-slate-900/80 border-emerald-500/30'
                  : isSent
                  ? 'bg-slate-900/60 border-cyan-500/30'
                  : 'bg-slate-950/40 border-slate-800'
              }`}
            >
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div className="flex items-start gap-3">
                  <div
                    className={`p-2 rounded-lg mt-0.5 ${
                      isResponded
                        ? 'bg-emerald-500/20 text-emerald-400'
                        : isSent
                        ? 'bg-cyan-500/20 text-cyan-400'
                        : 'bg-slate-800 text-slate-400'
                    }`}
                  >
                    {isResponded ? (
                      <CheckCircle2 className="w-4 h-4" />
                    ) : (
                      <Clock className="w-4 h-4" />
                    )}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold text-white">{cpInfo.label}</span>
                      <Badge variant={isResponded ? 'emerald' : isSent ? 'cyan' : 'slate'}>
                        {fup.status}
                      </Badge>
                      <span className="text-[10px] text-slate-400 font-mono">
                        Channel: {fup.channel}
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 mt-1">{cpInfo.prompt}</p>
                    {fup.mock_sent_message && (
                      <div className="mt-2 p-2 rounded-lg bg-slate-950 border border-slate-800 text-[11px] text-slate-400 italic">
                        💬 "{fup.mock_sent_message}"
                      </div>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleSimulateMockDispatch(fup.checkpoint)}
                    disabled={triggering}
                    title="Simulate WhatsApp/SMS Mock dispatch"
                    className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold flex items-center gap-1.5 transition-colors"
                  >
                    <Send className="w-3.5 h-3.5 text-cyan-400" />
                    <span className="hidden sm:inline">Mock Send</span>
                  </button>

                  <button
                    onClick={() => handleOpenResponder(fup)}
                    className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition-all shadow-sm"
                  >
                    {isResponded ? 'Update Response' : 'Answer Checkpoint'}
                  </button>
                </div>
              </div>

              {/* Response summary if already responded */}
              {isResponded && fup.response_data && (
                <div className="mt-3 pt-3 border-t border-slate-800/80 flex flex-wrap gap-4 text-xs text-slate-400">
                  <span>
                    Status: <strong className="text-emerald-400">{fup.response_data.employed ? 'Employed' : 'Searching'}</strong>
                  </span>
                  {fup.response_data.salary && (
                    <span>
                      Salary: <strong className="text-white">₹{Number(fup.response_data.salary).toLocaleString()}/mo</strong>
                    </span>
                  )}
                  {fup.response_data.satisfaction && (
                    <span>
                      Satisfaction: <strong className="text-amber-400">{'★'.repeat(fup.response_data.satisfaction)}</strong>
                    </span>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Embedded response modal */}
      {selectedFollowup && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="glass-panel-glow bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-md p-6 shadow-2xl space-y-4">
            <h4 className="text-base font-bold text-white">
              Respond to {checkpointsMap[selectedFollowup.checkpoint]?.label}
            </h4>
            <p className="text-xs text-slate-400">
              {checkpointsMap[selectedFollowup.checkpoint]?.prompt}
            </p>

            <form onSubmit={handleSubmitResponse} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Are you currently employed?
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setEmployed(true)}
                    className={`py-2 rounded-xl text-xs font-bold border transition-all ${
                      employed
                        ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300'
                        : 'bg-slate-950 border-slate-800 text-slate-400'
                    }`}
                  >
                    Yes, Employed
                  </button>
                  <button
                    type="button"
                    onClick={() => setEmployed(false)}
                    className={`py-2 rounded-xl text-xs font-bold border transition-all ${
                      !employed
                        ? 'bg-amber-500/20 border-amber-500 text-amber-300'
                        : 'bg-slate-950 border-slate-800 text-slate-400'
                    }`}
                  >
                    Actively Searching
                  </button>
                </div>
              </div>

              {employed && (
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Current Monthly Salary (₹)
                  </label>
                  <input
                    type="number"
                    value={currentSalary}
                    onChange={(e) => setCurrentSalary(e.target.value)}
                    placeholder="e.g. 28000"
                    className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              )}

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Job / Training Satisfaction Rating
                </label>
                <select
                  value={satisfaction}
                  onChange={(e) => setSatisfaction(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="5">★★★★★ Excellent - Highly aligned with training</option>
                  <option value="4">★★★★☆ Good - Relevant work</option>
                  <option value="3">★★★☆☆ Average - Moderate match</option>
                  <option value="2">★★☆☆☆ Needs Improvement</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Remarks / Promotions / New Skills Acquired
                </label>
                <textarea
                  rows="2"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="e.g. Promoted to Junior Cloud Specialist with 20% wage increment."
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setSelectedFollowup(null)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 rounded-xl text-xs font-bold bg-emerald-600 text-white hover:bg-emerald-500"
                >
                  {submitting ? 'Saving...' : 'Submit Update'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
