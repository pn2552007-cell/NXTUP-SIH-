import React, { useState, useEffect } from 'react';
import { aiAPI } from '../../services/api';
import { Cpu, CheckCircle2, AlertTriangle, BookOpen, RefreshCw, AlertCircle, Sparkles } from 'lucide-react';
import { Badge } from '../common/Badge';

export const SkillGapCard = ({ traineeId, traineeSkills = [], courseSkills = [] }) => {
  const [roles, setRoles] = useState([]);
  const [selectedRole, setSelectedRole] = useState('Full Stack Developer');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchRoles = async () => {
      try {
        const res = await aiAPI.getJobRoles();
        setRoles(res.data);
      } catch (err) {
        console.error('Failed to fetch job roles:', err);
      }
    };
    fetchRoles();
  }, []);

  const runAnalysis = async (roleName) => {
    setLoading(true);
    try {
      const res = await aiAPI.analyzeSkillGap({
        trainee_id: traineeId,
        trainee_skills: traineeSkills,
        course_skills: courseSkills,
        target_role: roleName,
      });
      setAnalysis(res.data);
    } catch (err) {
      console.error('Skill gap analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runAnalysis(selectedRole);
  }, [selectedRole, traineeId, traineeSkills.length]);

  return (
    <div className="glass-panel rounded-2xl p-6 relative overflow-hidden space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              AI-Powered Skill Gap Analysis
              <Badge variant="cyan">Workforce Intelligence</Badge>
            </h3>
            <p className="text-xs text-slate-400">
              Evaluates acquired competencies against industry target role requirements.
            </p>
          </div>
        </div>

        {/* Target role selector */}
        <div className="flex items-center gap-2">
          <label htmlFor="target-role-select" className="text-xs text-slate-400 font-medium">Target Role:</label>
          <select
            id="target-role-select"
            value={selectedRole}
            onChange={(e) => setSelectedRole(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-xl px-3 py-1.5 focus:outline-none focus:border-cyan-500"
          >
            {(roles || []).map((r) => (
              <option key={r.title} value={r.title}>
                {r.title}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="py-12 flex flex-col items-center justify-center text-slate-400 gap-3">
          <RefreshCw className="w-6 h-6 animate-spin text-cyan-400" />
          <span className="text-xs">Computing AI competency match & skill gaps...</span>
        </div>
      ) : analysis ? (
        <div className="space-y-6">
          {/* Unconfigured or Notice Message */}
          {!analysis.available && (
            <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
              <div>
                <strong className="block font-semibold text-amber-300 mb-0.5">AI Engine Status</strong>
                <p>{analysis.error || 'AI_API_KEY is not configured in backend environment. Configure it in .env to enable automated longitudinal analysis.'}</p>
              </div>
            </div>
          )}

          {/* AI Summary Banner */}
          {analysis.summary && (
            <div className="p-4 rounded-xl bg-slate-900/80 border border-cyan-500/20 text-xs text-slate-300 space-y-1">
              <div className="flex items-center gap-1.5 font-bold text-cyan-400">
                <Sparkles className="w-4 h-4" />
                <span>AI Readiness Evaluation Summary</span>
              </div>
              <p className="leading-relaxed">{analysis.summary}</p>
            </div>
          )}

          {/* Top Score Banner */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
              <div className="text-xs text-slate-400 font-medium">Job Readiness Score</div>
              <div className="text-2xl font-bold text-emerald-400 mt-1">
                {analysis.job_readiness || Math.round(100 - (analysis.skill_gap_score || 0))}%
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">
                Target: {analysis.target_role}
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
              <div className="text-xs text-slate-400 font-medium">Skill Gap Index</div>
              <div className="text-2xl font-bold text-cyan-400 mt-1">
                {analysis.skill_gap_score}%
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">
                Competencies to bridge
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
              <div className="text-xs text-slate-400 font-medium">Evaluation Model</div>
              <div className="text-sm font-bold text-purple-400 mt-2 font-mono">
                Groq Workforce AI
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">
                Pydantic validated output
              </div>
            </div>
          </div>

          {/* Matched vs Missing Skills */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Matched Skills / Strengths */}
            <div className="p-4 rounded-xl bg-slate-900/40 border border-emerald-500/20">
              <div className="flex items-center gap-2 text-xs font-bold text-emerald-400 mb-3">
                <CheckCircle2 className="w-4 h-4" />
                <span>Verified Strengths & Competencies ({(analysis.strengths || analysis.matched_skills || []).length})</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {(analysis.strengths && analysis.strengths.length > 0) ? (
                  analysis.strengths.map((str, idx) => (
                    <span
                      key={idx}
                      className="px-2.5 py-1 rounded-lg bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-medium"
                    >
                      ✓ {str}
                    </span>
                  ))
                ) : (analysis.matched_skills || []).length > 0 ? (
                  analysis.matched_skills.map((item, idx) => (
                    <span
                      key={idx}
                      className="px-2.5 py-1 rounded-lg bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-medium"
                    >
                      ✓ {item.skill}
                    </span>
                  ))
                ) : (
                  <p className="text-xs text-slate-400">No verified skills recorded yet for this trainee.</p>
                )}
              </div>
            </div>

            {/* Missing Skills / Gaps */}
            <div className="p-4 rounded-xl bg-slate-900/40 border border-amber-500/20">
              <div className="flex items-center gap-2 text-xs font-bold text-amber-400 mb-3">
                <AlertTriangle className="w-4 h-4" />
                <span>Identified Skill Gaps ({(analysis.skill_gaps || analysis.missing_skills || []).length})</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {((analysis.skill_gaps && analysis.skill_gaps.length > 0) ? analysis.skill_gaps : (analysis.missing_skills || [])).map((skill, idx) => (
                  <span
                    key={idx}
                    className="px-2.5 py-1 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-medium"
                  >
                    + {skill}
                  </span>
                ))}
              </div>
              {(!analysis.skill_gaps?.length && !analysis.missing_skills?.length) && (
                <p className="text-xs text-slate-400">All required skills fulfilled for this target role!</p>
              )}

              {/* Recommended Skills */}
              {(analysis.recommended_skills || []).length > 0 && (
                <div className="mt-4 pt-3 border-t border-slate-800 space-y-2">
                  <div className="text-[11px] font-bold text-slate-300 flex items-center gap-1.5">
                    <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Recommended Learning Areas:</span>
                  </div>
                  <ul className="space-y-1">
                    {analysis.recommended_skills.map((rec, rIdx) => (
                      <li key={rIdx} className="text-xs text-slate-400 flex items-start gap-1.5">
                        <span className="text-cyan-400 font-bold">•</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
