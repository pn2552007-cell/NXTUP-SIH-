import React, { useState, useEffect } from 'react';
import { employerAPI } from '../services/api';
import { MetricCard } from '../components/common/MetricCard';
import { Badge } from '../components/common/Badge';
import { EmployerVerificationModal } from '../components/verification/EmployerVerificationModal';
import {
  Briefcase,
  CheckCircle2,
  AlertCircle,
  Search,
  Users,
  ShieldCheck,
  Building2,
  Calendar,
  DollarSign,
  RefreshCw,
} from 'lucide-react';

export const EmployerDashboard = () => {
  const [data, setData] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [searchCandidate, setSearchCandidate] = useState('');
  const [selectedVerificationItem, setSelectedVerificationItem] = useState(null);
  const [isVerifyModalOpen, setIsVerifyModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [dashRes, candRes] = await Promise.all([
        employerAPI.getDashboard(),
        employerAPI.searchCandidates(),
      ]);
      setData(dashRes.data);
      setCandidates(candRes.data);
    } catch (err) {
      console.error('Failed to load employer dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleOpenVerify = (item) => {
    setSelectedVerificationItem(item);
    setIsVerifyModalOpen(true);
  };

  const filteredCandidates = candidates.filter((c) => {
    return (
      c.nextup_id?.toLowerCase().includes(searchCandidate.toLowerCase()) ||
      c.skillpulse_id?.toLowerCase().includes(searchCandidate.toLowerCase()) ||
      c.skills?.some((s) => s.toLowerCase().includes(searchCandidate.toLowerCase())) ||
      c.course_completed?.toLowerCase().includes(searchCandidate.toLowerCase())
    );
  });

  const pendingList = data?.pending_verifications || [];
  const verifiedList = data?.verified_hires || [];

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="glass-panel-glow rounded-2xl p-6 border-blue-500/30 flex flex-wrap items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-white">{data?.company_name || 'Employer Portal'}</h1>
            <Badge variant="blue">Registered Employer</Badge>
          </div>
          <p className="text-xs text-slate-300">
            Industry: {data?.industry || 'Enterprise Partner'} • Employment Outcome Verification Gateway
          </p>
          <p className="text-[11px] text-slate-500">
            Verification confirms trainee-reported outcomes. It does not replace employer HR or payroll systems.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs">
            <span className="text-slate-400">Pending Actions: </span>
            <strong className="text-amber-400 font-mono text-sm">{data?.pending_verifications_count || 0}</strong>
          </div>
          <button
            onClick={fetchData}
            title="Refresh"
            className="p-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-300 hover:text-white"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <MetricCard
          title="Pending Verification Requests"
          value={data?.pending_verifications_count || 0}
          subtitle="Self-reported hires awaiting review"
          icon={AlertCircle}
          accentColor="amber"
        />

        <MetricCard
          title="Verified Employees"
          value={data?.verified_employees_count || 0}
          subtitle="Confirmed on Payroll"
          icon={CheckCircle2}
          accentColor="emerald"
        />

        <MetricCard
          title="Consenting Candidate Pool"
          value={data?.candidate_pool_count || 0}
          subtitle="Opted in for Placement"
          icon={Users}
          accentColor="cyan"
        />
      </div>

      {/* Pending Verification Requests Section */}
      <div className="glass-panel rounded-2xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-amber-400" />
              Pending Employment Verifications
            </h3>
            <p className="text-xs text-slate-400">
              Review and confirm reported hires, verified dates, and wage records.
            </p>
          </div>
          <Badge variant="amber">{pendingList.length} Awaiting Verification</Badge>
        </div>

        <div className="overflow-x-auto rounded-xl border border-slate-800">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/90 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
              <tr>
                <th className="px-3 py-2.5">NEXTUP ID</th>
                <th className="px-3 py-2.5">Candidate Name</th>
                <th className="px-3 py-2.5">Course Completed</th>
                <th className="px-3 py-2.5">Reported Job Title</th>
                <th className="px-3 py-2.5">Joining Date</th>
                <th className="px-3 py-2.5 text-right">Reported Salary</th>
                <th className="px-3 py-2.5 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {pendingList.length > 0 ? (
                pendingList.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-900/40">
                    <td className="px-3 py-2.5 font-mono text-emerald-400">{item.nextup_id || item.skillpulse_id}</td>
                    <td className="px-3 py-2.5 font-semibold text-white">{item.trainee_name}</td>
                    <td className="px-3 py-2.5 text-slate-400">{item.course_name || '—'}</td>
                    <td className="px-3 py-2.5 text-white">{item.reported_job || '—'}</td>
                    <td className="px-3 py-2.5 font-mono text-slate-400">{item.reported_joining_date || '—'}</td>
                    <td className="px-3 py-2.5 text-right font-mono text-emerald-400">
                      {item.reported_salary ? `₹${Number(item.reported_salary).toLocaleString()}` : '—'}
                    </td>
                    <td className="px-3 py-2.5 text-center">
                      <button
                        onClick={() => handleOpenVerify(item)}
                        className="px-3 py-1 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition-all shadow-md shadow-emerald-950/40"
                      >
                        Verify Record
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-slate-400">
                    No employment records currently pending verification for your organization.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Verified Employees Record */}
      <div className="glass-panel rounded-2xl p-6 space-y-4">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            Verified Hires History
          </h3>
          <p className="text-xs text-slate-400">
            Audit history of confirmed trainees on organizational payroll.
          </p>
        </div>

        <div className="overflow-x-auto rounded-xl border border-slate-800">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/90 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
              <tr>
                <th className="px-3 py-2.5">NEXTUP ID</th>
                <th className="px-3 py-2.5">Candidate Name</th>
                <th className="px-3 py-2.5">Job Title</th>
                <th className="px-3 py-2.5">Joining Date</th>
                <th className="px-3 py-2.5 text-right">Verified Salary</th>
                <th className="px-3 py-2.5 text-center">Confidence Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {verifiedList.length > 0 ? (
                verifiedList.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-900/40">
                    <td className="px-3 py-2.5 font-mono text-emerald-400">{item.nextup_id || item.skillpulse_id}</td>
                    <td className="px-3 py-2.5 font-semibold text-white">{item.trainee_name}</td>
                    <td className="px-3 py-2.5 text-slate-300">{item.reported_job}</td>
                    <td className="px-3 py-2.5 font-mono text-slate-400">{item.reported_joining_date}</td>
                    <td className="px-3 py-2.5 text-right font-mono text-emerald-400">
                      {item.reported_salary ? `₹${Number(item.reported_salary).toLocaleString()}` : '—'}
                    </td>
                    <td className="px-3 py-2.5 text-center">
                      <span className="px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-300 font-mono text-[10px] font-bold">
                        {item.confidence_score ? `${Math.round(item.confidence_score * 100)}%` : 'Verified'}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-slate-400">
                    No verified hires on record yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Consenting Candidates Talent Search */}
      <div className="glass-panel rounded-2xl p-6 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Users className="w-4 h-4 text-cyan-400" />
              Consenting Graduate Candidate Pool
            </h3>
            <p className="text-xs text-slate-400">
              Discover candidates who have opted into outcome tracking and talent discovery.
            </p>
          </div>

          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchCandidate}
              onChange={(e) => setSearchCandidate(e.target.value)}
              placeholder="Search skill, ID, or course..."
              className="pl-9 pr-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 outline-none w-64"
            />
          </div>
        </div>

        <div className="overflow-x-auto rounded-xl border border-slate-800">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/90 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
              <tr>
                <th className="px-3 py-2.5">NEXTUP ID</th>
                <th className="px-3 py-2.5">Course Completed</th>
                <th className="px-3 py-2.5">Location</th>
                <th className="px-3 py-2.5">Skills</th>
                <th className="px-3 py-2.5 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {filteredCandidates.length > 0 ? (
                filteredCandidates.map((c, idx) => (
                  <tr key={idx} className="hover:bg-slate-900/40">
                    <td className="px-3 py-2.5 font-mono text-emerald-400">{c.nextup_id || c.skillpulse_id}</td>
                    <td className="px-3 py-2.5 text-slate-300">{c.course_completed || 'Vocational Training'}</td>
                    <td className="px-3 py-2.5 text-slate-400">{c.location || '—'}</td>
                    <td className="px-3 py-2.5">
                      <div className="flex flex-wrap gap-1">
                        {(c.skills || []).map((s, sIdx) => (
                          <span key={sIdx} className="px-1.5 py-0.5 rounded bg-slate-800 text-[10px] text-slate-300">
                            {s}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-3 py-2.5 text-center">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-500/15 text-cyan-300">
                        {c.employment_status}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-slate-400">
                    No consenting candidates matching the criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Verification Modal */}
      {selectedVerificationItem && (
        <EmployerVerificationModal
          isOpen={isVerifyModalOpen}
          onClose={() => {
            setIsVerifyModalOpen(false);
            setSelectedVerificationItem(null);
          }}
          item={selectedVerificationItem}
          onSuccess={() => {
            setIsVerifyModalOpen(false);
            setSelectedVerificationItem(null);
            fetchData();
          }}
        />
      )}
    </div>
  );
};
