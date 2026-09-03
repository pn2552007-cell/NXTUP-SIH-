import React, { useState, useEffect } from 'react';
import { providerAPI } from '../services/api';
import { MetricCard } from '../components/common/MetricCard';
import { Badge } from '../components/common/Badge';
import { CsvImportModal } from '../components/import/CsvImportModal';
import { Modal } from '../components/common/Modal';
import { useToast } from '../contexts/ToastContext';
import {
  Users,
  Award,
  Briefcase,
  TrendingUp,
  Cpu,
  Building2,
  UploadCloud,
  Filter,
  Search,
  CheckCircle2,
  RefreshCw,
  PlusCircle,
  BookOpen,
  AlertCircle
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

export const ProviderDashboard = () => {
  const [data, setData] = useState(null);
  const [trainees, setTrainees] = useState([]);
  const [selectedCohort, setSelectedCohort] = useState('ALL');
  const [selectedCourse, setSelectedCourse] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [isImportOpen, setIsImportOpen] = useState(false);
  const [isCreateCourseOpen, setIsCreateCourseOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  // New course form state
  const [courseName, setCourseName] = useState('');
  const [courseDomain, setCourseDomain] = useState('IT');
  const [courseDuration, setCourseDuration] = useState(12);
  const [courseSkills, setCourseSkills] = useState('');
  const [courseDescription, setCourseDescription] = useState('');
  const [creatingCourse, setCreatingCourse] = useState(false);

  const { showSuccess, showError } = useToast();

  const fetchData = async () => {
    try {
      setLoading(true);
      const [dashRes, trRes] = await Promise.all([
        providerAPI.getDashboard({ cohort: selectedCohort !== 'ALL' ? selectedCohort : undefined }),
        providerAPI.getTrainees({ cohort: selectedCohort !== 'ALL' ? selectedCohort : undefined }),
      ]);
      setData(dashRes.data);
      setTrainees(trRes.data);
    } catch (err) {
      console.error('Failed to load provider metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedCohort]);

  const handleCreateCourse = async (e) => {
    e.preventDefault();
    if (!courseName.trim()) {
      showError('Please enter a course name.');
      return;
    }
    setCreatingCourse(true);
    try {
      const skillsArray = courseSkills
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean);

      await providerAPI.createCourse({
        course_name: courseName.trim(),
        domain: courseDomain,
        duration_weeks: Number(courseDuration),
        required_skills: skillsArray,
        description: courseDescription.trim(),
      });

      showSuccess(`Course "${courseName}" created successfully!`);
      setIsCreateCourseOpen(false);
      setCourseName('');
      setCourseSkills('');
      setCourseDescription('');
      fetchData();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to create course.');
    } finally {
      setCreatingCourse(false);
    }
  };

  const filteredTrainees = trainees.filter((t) => {
    const matchesSearch =
      t.full_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.skillpulse_id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.course_name?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCourse = selectedCourse === 'ALL' || t.course_name === selectedCourse;
    return matchesSearch && matchesCourse;
  });

  const isEmpty = !data || (data.total_trainees === 0 && (data.courses_performance || []).length === 0);

  return (
    <div className="space-y-8">
      {/* Top Action Bar */}
      <div className="glass-panel-glow rounded-2xl p-6 border-purple-500/30 flex flex-wrap items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-white">{data?.provider_name || 'Training Provider Portal'}</h1>
            <Badge variant="purple">Accredited Provider</Badge>
          </div>
          <p className="text-xs text-slate-300">
            Outcome-Linked Vocational Training & Placement Management
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsCreateCourseOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-slate-900 border border-slate-700 text-slate-200 hover:text-white hover:border-purple-500/50 transition-all"
          >
            <PlusCircle className="w-4 h-4 text-purple-400" />
            <span>New Course</span>
          </button>

          <button
            onClick={() => setIsImportOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-500 hover:to-indigo-500 transition-all shadow-lg shadow-purple-950/40"
          >
            <UploadCloud className="w-4 h-4" />
            <span>Upload Trainee Roster (CSV)</span>
          </button>
        </div>
      </div>

      {/* Empty State Banner */}
      {isEmpty && !loading && (
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-purple-500/30 text-purple-200 flex items-start gap-4">
          <AlertCircle className="w-6 h-6 text-purple-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h3 className="text-sm font-bold text-white">No trainees registered yet.</h3>
            <p className="text-xs text-slate-300">
              Start by creating your first course or uploading a CSV roster of trainees. Longitudinal outcome tracking activates automatically upon trainee onboarding.
            </p>
          </div>
        </div>
      )}

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <MetricCard
          title="Total Trainees"
          value={data ? data.total_trainees : 0}
          subtitle="Enrolled in Programs"
          icon={Users}
          accentColor="purple"
        />

        <MetricCard
          title="Training Completion"
          value={data ? `${data.completion_rate}%` : '0%'}
          subtitle="Completed Curriculum"
          icon={Award}
          accentColor="cyan"
        />

        <MetricCard
          title="Certification Rate"
          value={data ? `${data.certification_rate}%` : '0%'}
          subtitle="Credential Issued"
          icon={CheckCircle2}
          accentColor="emerald"
        />

        <MetricCard
          title="Employment Rate"
          value={data ? `${data.employment_rate}%` : '0%'}
          subtitle="Verified Placed"
          icon={Briefcase}
          accentColor="emerald"
        />

        <MetricCard
          title="Placement Conversion"
          value={data ? `${data.placement_conversion}%` : '0%'}
          subtitle="Certified to Placed"
          icon={TrendingUp}
          accentColor="purple"
        />
      </div>

      {/* Course Performance Table */}
      <div className="glass-panel rounded-2xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-purple-400" />
              Course-Level Outcome Performance
            </h3>
            <p className="text-xs text-slate-400">
              Direct longitudinal placement and certification stats per curriculum.
            </p>
          </div>
        </div>

        <div className="overflow-x-auto rounded-xl border border-slate-800">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/90 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
              <tr>
                <th className="px-3 py-2.5">Course Name</th>
                <th className="px-3 py-2.5">Domain</th>
                <th className="px-3 py-2.5 text-center">Enrolled</th>
                <th className="px-3 py-2.5 text-center">Certified</th>
                <th className="px-3 py-2.5 text-center">Employed</th>
                <th className="px-3 py-2.5 text-center">Employment Rate</th>
                <th className="px-3 py-2.5 text-right">Avg Salary</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {(data?.courses_performance || []).length > 0 ? (
                data.courses_performance.map((c) => (
                  <tr key={c.course_id} className="hover:bg-slate-900/40">
                    <td className="px-3 py-2.5 font-semibold text-white">{c.course_name}</td>
                    <td className="px-3 py-2.5 text-slate-400">{c.domain}</td>
                    <td className="px-3 py-2.5 text-center font-mono">{c.total_enrolled}</td>
                    <td className="px-3 py-2.5 text-center font-mono text-cyan-300">{c.certified_count}</td>
                    <td className="px-3 py-2.5 text-center font-mono text-emerald-300">{c.employed_count}</td>
                    <td className="px-3 py-2.5 text-center font-bold text-emerald-400">{c.employment_rate}%</td>
                    <td className="px-3 py-2.5 text-right font-mono text-slate-300">
                      {c.avg_salary ? `₹${Number(c.avg_salary).toLocaleString()}` : 'N/A'}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-slate-400">
                    No courses created yet. Click "New Course" above to create your first course.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Trainees Roster Table */}
      <div className="glass-panel rounded-2xl p-6 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Users className="w-4 h-4 text-emerald-400" />
              Trainee Longitudinal Outcome Roster
            </h3>
            <p className="text-xs text-slate-400">
              Real trainee cohort tracking with persistent SkillPulse IDs.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search name, ID, course..."
                className="pl-9 pr-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 outline-none w-56"
              />
            </div>
          </div>
        </div>

        <div className="overflow-x-auto rounded-xl border border-slate-800">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/90 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
              <tr>
                <th className="px-3 py-2.5">SkillPulse ID</th>
                <th className="px-3 py-2.5">Trainee Name</th>
                <th className="px-3 py-2.5">Course</th>
                <th className="px-3 py-2.5 text-center">Training</th>
                <th className="px-3 py-2.5 text-center">Attendance</th>
                <th className="px-3 py-2.5 text-center">Employment</th>
                <th className="px-3 py-2.5">Employer</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {filteredTrainees.length > 0 ? (
                filteredTrainees.map((t) => (
                  <tr key={t.trainee_id} className="hover:bg-slate-900/40">
                    <td className="px-3 py-2.5 font-mono text-emerald-400">{t.skillpulse_id}</td>
                    <td className="px-3 py-2.5 font-semibold text-white">{t.full_name}</td>
                    <td className="px-3 py-2.5 text-slate-400">{t.course_name || '—'}</td>
                    <td className="px-3 py-2.5 text-center">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-500/15 text-cyan-300">
                        {t.completion_status}
                      </span>
                    </td>
                    <td className="px-3 py-2.5 text-center font-mono">{t.attendance_pct ? `${t.attendance_pct}%` : '—'}</td>
                    <td className="px-3 py-2.5 text-center font-semibold text-emerald-400">{t.employment_status}</td>
                    <td className="px-3 py-2.5 text-slate-300">{t.employer_name || '—'}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-slate-400">
                    No trainees registered yet. Start by uploading a CSV roster or adding your first trainee.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* CSV Import Modal */}
      <CsvImportModal
        isOpen={isImportOpen}
        onClose={() => setIsImportOpen(false)}
        onImportSuccess={() => {
          setIsImportOpen(false);
          fetchData();
        }}
      />

      {/* Create Course Modal */}
      <Modal
        isOpen={isCreateCourseOpen}
        onClose={() => setIsCreateCourseOpen(false)}
        title="Create Vocational Course"
      >
        <form onSubmit={handleCreateCourse} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Course Name</label>
            <input
              type="text"
              required
              value={courseName}
              onChange={(e) => setCourseName(e.target.value)}
              placeholder="e.g. Advanced Python & Cloud Engineering"
              className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-sm text-white focus:border-purple-500 outline-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Domain</label>
              <select
                value={courseDomain}
                onChange={(e) => setCourseDomain(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-sm text-white focus:border-purple-500 outline-none"
              >
                <option value="IT">IT & Software</option>
                <option value="Healthcare">Healthcare</option>
                <option value="Manufacturing">Manufacturing</option>
                <option value="Electronics">Electronics</option>
                <option value="Renewable Energy">Renewable Energy</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Duration (Weeks)</label>
              <input
                type="number"
                min="1"
                max="104"
                value={courseDuration}
                onChange={(e) => setCourseDuration(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-sm text-white focus:border-purple-500 outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Curriculum Skills (comma-separated)</label>
            <input
              type="text"
              value={courseSkills}
              onChange={(e) => setCourseSkills(e.target.value)}
              placeholder="Python, SQL, Docker, REST APIs"
              className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-sm text-white focus:border-purple-500 outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Description</label>
            <textarea
              rows={3}
              value={courseDescription}
              onChange={(e) => setCourseDescription(e.target.value)}
              placeholder="Course curriculum and career objectives..."
              className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-sm text-white focus:border-purple-500 outline-none"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setIsCreateCourseOpen(false)}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={creatingCourse}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-purple-600 hover:bg-purple-500 text-white disabled:opacity-50"
            >
              {creatingCourse ? 'Creating...' : 'Create Course'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
