import React, { useState } from 'react';
import { followupsAPI } from '../../services/api';
import { useToast } from '../../contexts/ToastContext';
import { CheckCircle2, Clock, Send, MessageSquare, AlertCircle, Sparkles } from 'lucide-react';
import { Badge } from '../common/Badge';

export const FollowupTimeline = ({ followups = [], onUpdated }) => {
  const { showSuccess, showError } = useToast();
  const [selectedFollowup, setSelectedFollowup] = useState(null);
  const [employed, setEmployed] = useState(true);
  const [employerName, setEmployerName] = useState('');
  const [jobTitle, setJobTitle] = useState('');
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
    setEmployerName(fup.response_data?.employer_name || '');
    setJobTitle(fup.response_data?.job_title || '');
    setCurrentSalary(fup.response_data?.salary || fup.response_data?.current_salary || '');
    setSatisfaction(fup.response_data?.satisfaction_score || fup.response_data?.satisfaction || 5);
    setNotes(Array.isArray(fup.response_data?.skills_used) ? fup.response_data.skills_used.join(', ') : (fup.response_data?.notes || ''));
  };

  const handleSubmitResponse = async (e) => {
    e.preventDefault();
    if (!selectedFollowup) return;

    setSubmitting(true);
    try {
      await followupsAPI.respond({
        followup_id: selectedFollowup.id,
        employed,
        employer_name: employed ? employerName : null,
        job_title: employed ? jobTitle : null,
        current_salary: employed && currentSalary ? Number(currentSalary) : null,
        satisfaction_score: Number(satisfaction),
        skills_used: notes ? notes.split(',').map((s) => s.trim()).filter(Boolean) : [],
      });

      showSuccess(`Response submitted for ${checkpointsMap[selectedFollowup.checkpoint]?.label || selectedFollowup.checkpoint}`);
      setSelectedFollowup(null);
      setEmployerName('');
      setJobTitle('');
      if (onUpdated) onUpdated();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to record follow-up response');
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleSendFollowup = async (fup) => {
    setTriggering(true);
    try {
      await followupsAPI.send(fup.id);
      showSuccess(`${checkpointsMap[fup.checkpoint]?.label || fup.checkpoint} marked as sent.`);
      if (onUpdated) onUpdated();
    } catch (err) {
      showError(err.response?.data?.detail || 'Could not mark follow-up as sent');
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
                    {fup.scheduled_date && (
                      <span className="text-[10px] text-slate-500 font-mono">
                        Scheduled: {fup.scheduled_date}
                      </span>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2">
                  {(fup.status === 'SCHEDULED' || fup.status === 'PENDING') && (
                    <button
                      onClick={() => handleSendFollowup(fup)}
                      disabled={triggering}
                      title="Mark this checkpoint as sent to the trainee"
                      className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold flex items-center gap-1.5 transition-colors"
                    >
                      <Send className="w-3.5 h-3.5 text-cyan-400" />
                      <span className="hidden sm:inline">Send</span>
                    </button>
                  )}

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
                    Status: <strong className="text-emerald-400">{fup.response_data.employed ? 'Employed (self-reported)' : 'Searching'}</strong>
                  </span>
                  {fup.response_data.employer_name && (
                    <span>
                      Employer: <strong className="text-white">{fup.response_data.employer_name}</strong>
                    </span>
                  )}
                  {(fup.response_data.current_salary || fup.response_data.salary) && (
                    <span>
                      Salary: <strong className="text-white">₹{Number(fup.response_data.current_salary || fup.response_data.salary).toLocaleString()}/mo</strong>
                    </span>
                  )}
                  {fup.response_data.satisfaction_score && (
                    <span>
                      Satisfaction: <strong className="text-amber-400">{'★'.repeat(Number(fup.response_data.satisfaction_score) || 0)}</strong>
                    </span>
                  )}
                  <span className="text-slate-500">Follow-up responses are self-reported until employer-verified.</span>
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
                <>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-slate-300 mb-1">
                        Employer Name
                      </label>
                      <input
                        type="text"
                        value={employerName}
                        onChange={(e) => setEmployerName(e.target.value)}
                        placeholder="e.g. TechCore Solutions"
                        className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-300 mb-1">
                        Job Title
                      </label>
                      <input
                        type="text"
                        value={jobTitle}
                        onChange={(e) => setJobTitle(e.target.value)}
                        placeholder="e.g. Junior Web Developer"
                        className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                      />
                    </div>
                  </div>
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
                </>
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
                  Skills Used in Current Role (comma-separated)
                </label>
                <textarea
                  rows="2"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="e.g. React, REST APIs, SQL"
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
