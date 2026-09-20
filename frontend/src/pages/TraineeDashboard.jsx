import React, { useState, useEffect } from 'react';
import { traineeAPI, employmentAPI, followupsAPI } from '../services/api';
import { useToast } from '../contexts/ToastContext';
import { MetricCard } from '../components/common/MetricCard';
import { TraineeJourneyTracker } from '../components/journey/TraineeJourneyTracker';
import { SkillGapCard } from '../components/ai/SkillGapCard';
import { PlacementRiskCard } from '../components/ai/PlacementRiskCard';
import { FollowupTimeline } from '../components/followups/FollowupTimeline';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import {
  Briefcase,
  TrendingUp,
  Cpu,
  Building2,
  Calendar,
  CheckCircle2,
  AlertCircle,
  PlusCircle,
  Sparkles,
  Award,
  RefreshCw,
  Plus,
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

export const TraineeDashboard = () => {
  const { showSuccess, showError } = useToast();
  const [profile, setProfile] = useState(null);
  const [journey, setJourney] = useState([]);
  const [skills, setSkills] = useState([]);
  const [wageGrowth, setWageGrowth] = useState(null);
  const [followups, setFollowups] = useState([]);
  const [loading, setLoading] = useState(true);

  // Employment Report Modal State
  const [isReportOpen, setIsReportOpen] = useState(false);
  const [reportStatus, setReportStatus] = useState('EMPLOYED');
  const [employerName, setEmployerName] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [joiningDate, setJoiningDate] = useState('');
  const [startingSalary, setStartingSalary] = useState('');
  const [locationCity, setLocationCity] = useState('');
  const [nonPlacementReason, setNonPlacementReason] = useState('');
  const [submittingReport, setSubmittingReport] = useState(false);

  // Add Skill State
  const [isAddSkillOpen, setIsAddSkillOpen] = useState(false);
  const [newSkillName, setNewSkillName] = useState('');
  const [newSkillProficiency, setNewSkillProficiency] = useState('INTERMEDIATE');
  const [submittingSkill, setSubmittingSkill] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [pRes, jRes, sRes, wRes, fRes] = await Promise.all([
        traineeAPI.getProfile(),
        traineeAPI.getJourney(),
        traineeAPI.getSkills(),
        traineeAPI.getWageGrowth(),
        followupsAPI.getAll(),
      ]);

      setProfile(pRes.data);
      setJourney(jRes.data);
      setSkills(sRes.data);
      setWageGrowth(wRes.data);
      setFollowups(fRes.data);
    } catch (err) {
      console.error('Failed to load trainee data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleEmploymentSubmit = async (e) => {
    e.preventDefault();
    if (reportStatus === 'EMPLOYED' && (!employerName.trim() || !jobTitle.trim() || !joiningDate || !startingSalary)) {
      showError('Employer name, job title, joining date, and starting salary are required.');
      return;
    }
    setSubmittingReport(true);
    try {
      await employmentAPI.report({
        status: reportStatus,
        employer_name: reportStatus === 'EMPLOYED' ? employerName : undefined,
        job_title: reportStatus === 'EMPLOYED' ? jobTitle : undefined,
        joining_date: reportStatus === 'EMPLOYED' ? joiningDate : undefined,
        starting_salary: reportStatus === 'EMPLOYED' && startingSalary ? Number(startingSalary) : undefined,
        location_city: reportStatus === 'EMPLOYED' ? locationCity : undefined,
        non_placement_reason: reportStatus !== 'EMPLOYED' ? nonPlacementReason || undefined : undefined,
      });

      showSuccess(reportStatus === 'EMPLOYED'
        ? 'Employment outcome reported as self-reported and queued for employer verification.'
        : 'Status updated. This remains self-reported until verified.');
      setIsReportOpen(false);
      setNonPlacementReason('');
      fetchData();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to record employment status');
      console.error(err);
    } finally {
      setSubmittingReport(false);
    }
  };

  const handleAddSkill = async (e) => {
    e.preventDefault();
    if (!newSkillName.trim()) {
      showError('Please enter a skill name.');
      return;
    }
    setSubmittingSkill(true);
    try {
      await traineeAPI.addSkill({
        skill_name: newSkillName.trim(),
        proficiency_level: newSkillProficiency,
      });
      showSuccess(`Skill "${newSkillName}" added successfully.`);
      setIsAddSkillOpen(false);
      setNewSkillName('');
      fetchData();
    } catch (err) {
      showError('Failed to add skill.');
    } finally {
      setSubmittingSkill(false);
    }
  };

  if (loading && !profile) {
    return (
      <div className="py-24 flex flex-col items-center justify-center text-slate-400 gap-3">
        <RefreshCw className="w-8 h-8 animate-spin text-emerald-400" />
        <span className="text-sm">Loading your NXTUP trajectory...</span>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Top Banner with NXTUP ID */}
      <div className="glass-panel-glow rounded-2xl p-6 border-emerald-500/30 flex flex-wrap items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-white">{profile?.full_name}</h1>
            <Badge variant="emerald">Authenticated Trainee</Badge>
          </div>
          <p className="text-xs text-slate-300">
            {profile?.course_name ? `${profile.course_name} • ${profile?.provider_name || 'Vocational Academy'}` : 'Enrolled Trainee Profile'}
          </p>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-[10px] uppercase font-bold tracking-widest text-slate-400">
              Unique NXTUP ID
            </div>
            <div className="text-xl font-mono font-black text-emerald-400">
              {profile?.nextup_id || profile?.skillpulse_id}
            </div>
          </div>
          <button
            onClick={() => setIsReportOpen(true)}
            className="px-4 py-2 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition-all shadow-md shadow-emerald-950 flex items-center gap-1.5"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Update Employment</span>
          </button>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Employment Status"
          value={profile?.employment_status || 'NOT_REPORTED'}
          subtitle={profile?.current_employer || 'No employer reported'}
          icon={Briefcase}
          badgeText={profile?.verification_label || profile?.verification_status || 'Not reported'}
          accentColor={profile?.verification_status === 'VERIFIED' ? 'emerald' : 'amber'}
        />

        <MetricCard
          title="AI Skill Gap Score"
          value={profile?.skill_gap_score !== null && profile?.skill_gap_score !== undefined ? `${profile.skill_gap_score}%` : 'Analysis Ready'}
          subtitle="Evaluated against Target Role"
          icon={Cpu}
          accentColor="cyan"
        />

        <MetricCard
          title="6-Month Retention"
          value={profile?.retention_6m === true ? 'Confirmed ✓' : profile?.retention_6m === false ? 'Not Retained' : 'Awaiting Checkpoint'}
          subtitle="Longitudinal Milestone"
          icon={Building2}
          accentColor="purple"
        />

        <MetricCard
          title="Wage Progression"
          value={profile?.wage_growth_pct !== null && profile?.wage_growth_pct !== undefined ? `+${profile.wage_growth_pct}%` : 'No Wage History'}
          subtitle={profile?.current_salary ? `Current: ₹${Number(profile.current_salary).toLocaleString()}/mo` : 'No salary reported yet'}
          icon={TrendingUp}
          accentColor="amber"
        />
      </div>

      {/* Trainee Longitudinal Journey Flow */}
      <TraineeJourneyTracker profile={profile} journey={journey} />

      {/* AI Skill Gap Detection */}
      <SkillGapCard
        traineeId={profile?.id}
        traineeSkills={skills.map((s) => s.skill_name)}
        courseSkills={profile?.course_name ? [profile.course_name] : []}
      />

      {/* NXTUP ML Placement Risk & Targeted Interventions */}
      <PlacementRiskCard traineeId={profile?.id} onInterventionUpdated={fetchData} />

      {/* Salary & Wage Growth Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-panel rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                Longitudinal Wage Growth Trajectory
                {profile?.wage_growth_pct !== null && profile?.wage_growth_pct !== undefined && (
                  <Badge variant="emerald">+{profile.wage_growth_pct}% Growth</Badge>
                )}
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Formula: <code>((Current Salary - Starting Salary) / Starting Salary) × 100</code>
              </p>
            </div>
            {profile?.current_salary && (
              <div className="text-right">
                <div className="text-xs text-slate-400">Current Monthly Compensation</div>
                <div className="text-lg font-bold text-emerald-400 font-mono">
                  ₹{Number(profile.current_salary).toLocaleString()}
                </div>
              </div>
            )}
          </div>

          {wageGrowth?.has_history && wageGrowth?.history?.length > 0 ? (
            <div className="h-64 w-full pt-4">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={wageGrowth.history}>
                  <defs>
                    <linearGradient id="salaryGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="effective_date" stroke="#64748b" textAnchor="end" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 11 }} tickFormatter={(v) => `₹${v / 1000}k`} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }}
                    formatter={(val) => [`₹${Number(val).toLocaleString()}/month`, 'Salary']}
                  />
                  <Area type="monotone" dataKey="salary_amount" stroke="#10b981" strokeWidth={3} fill="url(#salaryGradient)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-48 flex flex-col items-center justify-center text-slate-400 text-xs space-y-2">
              <TrendingUp className="w-8 h-8 opacity-30 text-emerald-400" />
              <span>No wage history available yet.</span>
              <button
                onClick={() => setIsReportOpen(true)}
                className="text-emerald-400 hover:underline font-semibold"
              >
                Report starting employment & wage
              </button>
            </div>
          )}
        </div>

        {/* Acquired Skills Summary */}
        <div className="glass-panel rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Award className="w-4 h-4 text-emerald-400" />
              My Acquired Skills
            </h3>
            <button
              onClick={() => setIsAddSkillOpen(true)}
              className="flex items-center gap-1 text-xs text-emerald-400 hover:text-emerald-300 font-semibold"
            >
              <Plus className="w-3.5 h-3.5" />
              Add Skill
            </button>
          </div>

          <div className="space-y-2.5 max-h-64 overflow-y-auto">
            {skills.length > 0 ? (
              skills.map((sk) => (
                <div
                  key={sk.id}
                  className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between text-xs"
                >
                  <div className="font-semibold text-slate-200">{sk.skill_name}</div>
                  <Badge variant={sk.proficiency_level === 'ADVANCED' ? 'emerald' : 'cyan'} size="sm">
                    {sk.proficiency_level}
                  </Badge>
                </div>
              ))
            ) : (
              <div className="py-8 text-center text-slate-400 text-xs">
                No skills recorded yet. Click "Add Skill" to register acquired technical competencies.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Automated Longitudinal Follow-up timeline */}
      <FollowupTimeline followups={followups} onUpdated={fetchData} />

      {/* Employment Report Modal */}
      <Modal isOpen={isReportOpen} onClose={() => setIsReportOpen(false)} title="Update Post-Training Employment Status">
        <form onSubmit={handleEmploymentSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2">
              Have you found employment post-training?
            </label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { key: 'EMPLOYED', label: 'Yes, Employed' },
                { key: 'SEEKING', label: 'Still Searching' },
                { key: 'SELF_EMPLOYED', label: 'Self Employed' },
              ].map((item) => (
                <button
                  key={item.key}
                  type="button"
                  onClick={() => setReportStatus(item.key)}
                  className={`py-2 rounded-xl text-xs font-bold border transition-all ${
                    reportStatus === item.key
                      ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300'
                      : 'bg-slate-950 border-slate-800 text-slate-400'
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>

          {reportStatus === 'EMPLOYED' || reportStatus === 'SELF_EMPLOYED' ? (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Employer / Enterprise Name</label>
                  <input
                    type="text"
                    required
                    value={employerName}
                    onChange={(e) => setEmployerName(e.target.value)}
                    placeholder="e.g. Infotech Solutions"
                    className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Job Title / Role</label>
                  <input
                    type="text"
                    required
                    value={jobTitle}
                    onChange={(e) => setJobTitle(e.target.value)}
                    placeholder="e.g. Junior Software Engineer"
                    className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Joining Date</label>
                  <input
                    type="date"
                    required
                    value={joiningDate}
                    onChange={(e) => setJoiningDate(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Monthly Starting Salary (₹)</label>
                  <input
                    type="number"
                    required
                    min="1"
                    value={startingSalary}
                    onChange={(e) => setStartingSalary(e.target.value)}
                    placeholder="e.g. 25000"
                    className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs text-slate-400 mb-1">Work Location City</label>
                <input
                  type="text"
                  value={locationCity}
                  onChange={(e) => setLocationCity(e.target.value)}
                  placeholder="e.g. Pune, Bengaluru, Chennai"
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                />
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300">
                Your status will be marked as actively seeking. This stays self-reported. Providers and approved employers can view your profile for potential placement opportunities.
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Reason not placed (optional, helps providers improve)</label>
                <select
                  value={nonPlacementReason}
                  onChange={(e) => setNonPlacementReason(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="">Select a reason</option>
                  <option value="Interviewing — no offer yet">Interviewing — no offer yet</option>
                  <option value="Skill gap identified">Skill gap identified</option>
                  <option value="Location constraint">Location constraint</option>
                  <option value="Salary expectation mismatch">Salary expectation mismatch</option>
                  <option value="Pursuing higher education">Pursuing higher education</option>
                  <option value="Health or family reason">Health or family reason</option>
                </select>
              </div>
            </div>
          )}

          <p className="text-[11px] text-slate-500">
            Reports are labelled self-reported until an employer verifies them. Verification confirms the outcome only and does not replace employer HR or payroll records.
          </p>

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setIsReportOpen(false)}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submittingReport}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white disabled:opacity-50"
            >
              {submittingReport ? 'Saving...' : 'Submit Report'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Add Skill Modal */}
      <Modal isOpen={isAddSkillOpen} onClose={() => setIsAddSkillOpen(false)} title="Add Acquired Skill">
        <form onSubmit={handleAddSkill} className="space-y-4">
          <div>
            <label className="block text-xs text-slate-300 mb-1 font-semibold">Skill Name</label>
            <input
              type="text"
              required
              value={newSkillName}
              onChange={(e) => setNewSkillName(e.target.value)}
              placeholder="e.g. Python, SQL, Docker, React"
              className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div>
            <label className="block text-xs text-slate-300 mb-1 font-semibold">Proficiency Level</label>
            <select
              value={newSkillProficiency}
              onChange={(e) => setNewSkillProficiency(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
            >
              <option value="BEGINNER">Beginner</option>
              <option value="INTERMEDIATE">Intermediate</option>
              <option value="ADVANCED">Advanced</option>
              <option value="EXPERT">Expert</option>
            </select>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setIsAddSkillOpen(false)}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submittingSkill}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white disabled:opacity-50"
            >
              {submittingSkill ? 'Adding...' : 'Save Skill'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
