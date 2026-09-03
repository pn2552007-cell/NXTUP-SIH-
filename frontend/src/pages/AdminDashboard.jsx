import React, { useState, useEffect } from 'react';
import { adminAPI } from '../services/api';
import { MetricCard } from '../components/common/MetricCard';
import { Badge } from '../components/common/Badge';
import {
  Landmark,
  TrendingUp,
  Briefcase,
  Users,
  Building2,
  Award,
  Cpu,
  MapPin,
  Info,
  RefreshCw,
  BarChart3,
  AlertCircle
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

export const AdminDashboard = () => {
  const [data, setData] = useState(null);
  const [filterOptions, setFilterOptions] = useState(null);
  const [selectedState, setSelectedState] = useState('ALL');
  const [selectedDistrict, setSelectedDistrict] = useState('ALL');
  const [loading, setLoading] = useState(true);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const [dashRes, filtersRes] = await Promise.all([
        adminAPI.getDashboard({
          state: selectedState !== 'ALL' ? selectedState : undefined,
          district: selectedDistrict !== 'ALL' ? selectedDistrict : undefined,
        }),
        adminAPI.getFilters(),
      ]);
      setData(dashRes.data);
      setFilterOptions(filtersRes.data);
    } catch (err) {
      console.error('Failed to load admin analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, [selectedState, selectedDistrict]);

  const isEmptyDatabase = !data || (data.total_trainees === 0 && data.total_courses === 0);

  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="glass-panel-glow rounded-2xl p-6 border-cyan-500/30 flex flex-wrap items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-white">National Skilling Outcome Command Center</h1>
            <Badge variant="cyan">Policy & Livelihood Analytics</Badge>
          </div>
          <p className="text-xs text-slate-300 flex items-center gap-1.5">
            <Info className="w-3.5 h-3.5 text-cyan-400" />
            <span>Tracking longitudinal outcomes across states, districts, and training providers from live records.</span>
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-2.5">
          <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-700 px-3 py-1.5 rounded-xl text-xs">
            <MapPin className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={selectedState}
              onChange={(e) => {
                setSelectedState(e.target.value);
                setSelectedDistrict('ALL');
              }}
              className="bg-transparent text-slate-200 focus:outline-none cursor-pointer"
            >
              {(filterOptions?.states || ['ALL']).map((st) => (
                <option key={st} value={st} className="bg-slate-900 text-slate-100">
                  {st === 'ALL' ? 'All States' : st}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-700 px-3 py-1.5 rounded-xl text-xs">
            <select
              value={selectedDistrict}
              onChange={(e) => setSelectedDistrict(e.target.value)}
              className="bg-transparent text-slate-200 focus:outline-none cursor-pointer"
            >
              {(filterOptions?.districts || ['ALL']).map((dist) => (
                <option key={dist} value={dist} className="bg-slate-900 text-slate-100">
                  {dist === 'ALL' ? 'All Districts' : dist}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={fetchDashboard}
            title="Refresh database metrics"
            className="p-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-300 hover:text-white transition-all"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Empty Database State Notice */}
      {isEmptyDatabase && !loading && (
        <div className="p-6 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-200 flex items-start gap-4">
          <AlertCircle className="w-6 h-6 text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h3 className="text-sm font-bold text-white">No analytics available yet.</h3>
            <p className="text-xs text-slate-300">
              The platform database is currently at zero data. Metrics and geographic outcome breakdowns will populate dynamically as training providers create courses and enroll trainees.
            </p>
          </div>
        </div>
      )}

      {/* Macro Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
        <MetricCard
          title="Macro Employment Rate"
          value={data ? `${data.macro_employment_rate}%` : '0%'}
          subtitle="Trained to Employed"
          icon={Briefcase}
          accentColor="emerald"
        />

        <MetricCard
          title="6-Month Retention"
          value={data?.macro_retention_6m !== null && data?.macro_retention_6m !== undefined ? `${data.macro_retention_6m}%` : 'Insufficient data'}
          subtitle="Sustained in Industry"
          icon={Building2}
          accentColor="cyan"
        />

        <MetricCard
          title="Average Wage Growth"
          value={data?.avg_wage_growth_pct !== null && data?.avg_wage_growth_pct !== undefined ? `+${data.avg_wage_growth_pct}%` : 'No wage history'}
          subtitle="Starting to Current Pay"
          icon={TrendingUp}
          accentColor="emerald"
        />

        <MetricCard
          title="Placement Conversion"
          value={data ? `${data.placement_conversion_rate}%` : '0%'}
          subtitle="Certified to Employed"
          icon={Award}
          accentColor="purple"
        />

        <MetricCard
          title="Macro Skill Gap Index"
          value={data?.macro_skill_gap_index !== null && data?.macro_skill_gap_index !== undefined ? `${data.macro_skill_gap_index}%` : 'N/A'}
          subtitle="Curriculum Alignment"
          icon={Cpu}
          accentColor="amber"
        />

        <MetricCard
          title="Total Ecosystem Trainees"
          value={data ? data.total_trainees : 0}
          subtitle={`Across ${data?.total_providers || 0} Providers`}
          icon={Users}
          accentColor="cyan"
        />
      </div>

      {/* Sectoral Breakdown and Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sectoral Skilling Performance */}
        <div className="lg:col-span-3 glass-panel rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-cyan-400" />
                Sectoral Skilling Performance by Domain
              </h3>
              <p className="text-xs text-slate-400">
                Course enrollments and placement distribution across vocational sectors.
              </p>
            </div>
          </div>

          {(data?.domains_breakdown || []).length > 0 ? (
            <div className="h-64 w-full pt-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.domains_breakdown}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="domain" stroke="#64748b" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }}
                  />
                  <Bar dataKey="trainees" name="Trainees Enrolled" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="employment_rate" name="Employment Rate (%)" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-48 flex flex-col items-center justify-center text-slate-400 text-xs">
              <BarChart3 className="w-8 h-8 mb-2 opacity-30 text-slate-500" />
              <span>No domain or course records available yet.</span>
            </div>
          )}
        </div>
      </div>

      {/* District Trends & Provider Impact Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* District-level outcome trends */}
        <div className="glass-panel rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <MapPin className="w-4 h-4 text-emerald-400" />
                District Livelihood Disparity Index
              </h3>
              <p className="text-xs text-slate-400">
                Employment and outcome metrics across registered districts.
              </p>
            </div>
          </div>

          <div className="overflow-x-auto rounded-xl border border-slate-800">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/90 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
                <tr>
                  <th className="px-3 py-2.5">District</th>
                  <th className="px-3 py-2.5">State</th>
                  <th className="px-3 py-2.5 text-center">Trainees</th>
                  <th className="px-3 py-2.5 text-center">Employment</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-200">
                {(data?.districts_data || []).length > 0 ? (
                  data.districts_data.map((dist, idx) => (
                    <tr key={idx} className="hover:bg-slate-900/40">
                      <td className="px-3 py-2.5 font-semibold text-white">{dist.district}</td>
                      <td className="px-3 py-2.5 text-slate-400">{dist.state}</td>
                      <td className="px-3 py-2.5 text-center font-mono">{dist.total_trainees}</td>
                      <td className="px-3 py-2.5 text-center font-bold text-emerald-400">{dist.employment_rate}%</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={4} className="px-4 py-8 text-center text-slate-400">
                      No district records available yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Training Provider Impact Index */}
        <div className="glass-panel rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Award className="w-4 h-4 text-purple-400" />
                Training Provider Impact Rankings
              </h3>
              <p className="text-xs text-slate-400">
                Outcomes based on actual certifications and employment verifications.
              </p>
            </div>
          </div>

          <div className="overflow-x-auto rounded-xl border border-slate-800">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/90 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
                <tr>
                  <th className="px-3 py-2.5">Provider</th>
                  <th className="px-3 py-2.5 text-center">Trained</th>
                  <th className="px-3 py-2.5 text-center">Placement</th>
                  <th className="px-3 py-2.5 text-right">Impact Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-200">
                {(data?.provider_rankings || []).length > 0 ? (
                  data.provider_rankings.map((prv) => (
                    <tr key={prv.provider_id} className="hover:bg-slate-900/40">
                      <td className="px-3 py-2.5">
                        <div className="font-semibold text-white">{prv.provider_name}</div>
                        <div className="text-[10px] text-slate-400">{prv.state}</div>
                      </td>
                      <td className="px-3 py-2.5 text-center font-mono">{prv.total_trained}</td>
                      <td className="px-3 py-2.5 text-center font-bold text-emerald-400">{prv.employed_pct}%</td>
                      <td className="px-3 py-2.5 text-right">
                        <span className="px-2 py-0.5 rounded bg-purple-500/15 text-purple-300 font-mono font-bold border border-purple-500/30">
                          {prv.impact_score}/100
                        </span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={4} className="px-4 py-8 text-center text-slate-400">
                      No training providers registered yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
