import React, { useState, useEffect } from 'react';
import { mlAPI, interventionsAPI } from '../../services/api';
import { useToast } from '../../contexts/ToastContext';
import {
  AlertTriangle,
  ShieldCheck,
  CheckCircle2,
  TrendingUp,
  Cpu,
  RefreshCw,
  Sparkles,
  ArrowRight,
  ListOrdered,
  Clock,
} from 'lucide-react';
import { Badge } from '../common/Badge';

export const PlacementRiskCard = ({ traineeId, onInterventionUpdated }) => {
  const { showSuccess, showError } = useToast();
  const [loading, setLoading] = useState(true);
  const [riskData, setRiskData] = useState(null);
  const [interventions, setInterventions] = useState([]);
  const [requestingIntervention, setRequestingIntervention] = useState(false);

  const fetchRiskAndInterventions = async () => {
    if (!traineeId) return;
    try {
      setLoading(true);
      const [riskRes, intRes] = await Promise.all([
        mlAPI.predictRisk({ trainee_id: traineeId }),
        interventionsAPI.listForTrainee(traineeId).catch(() => ({ data: [] })),
      ]);
      setRiskData(riskRes.data);
      setInterventions(intRes.data || []);
    } catch (err) {
      console.error('Error fetching ML risk:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRiskAndInterventions();
  }, [traineeId]);

  const handleRequestIntervention = async () => {
    if (!riskData) return;
    try {
      setRequestingIntervention(true);
      await mlAPI.recommendIntervention({
        trainee_id: traineeId,
        risk_level: riskData.risk_level || 'MEDIUM',
        risk_score: riskData.risk_score || 50.0,
        missing_skills: [],
      });
      showSuccess('New personalized intervention plan generated!');
      await fetchRiskAndInterventions();
      if (onInterventionUpdated) onInterventionUpdated();
    } catch (err) {
      showError('Failed to generate intervention recommendation');
      console.error(err);
    } finally {
      setRequestingIntervention(false);
    }
  };

  const handleStatusChange = async (interventionId, newStatus) => {
    try {
      await interventionsAPI.updateStatus(interventionId, newStatus);
      showSuccess(`Intervention status updated to ${newStatus}`);
      await fetchRiskAndInterventions();
      if (onInterventionUpdated) onInterventionUpdated();
    } catch (err) {
      showError('Failed to update status');
    }
  };

  const getRiskBadge = (level) => {
    switch (level?.toUpperCase()) {
      case 'LOW':
        return <Badge variant="emerald">LOW PLACEMENT RISK</Badge>;
      case 'MEDIUM':
        return <Badge variant="amber">MODERATE RISK</Badge>;
      case 'HIGH':
        return <Badge variant="rose">HIGH ATTRITION RISK</Badge>;
      default:
        return <Badge variant="blue">EVALUATING</Badge>;
    }
  };

  const getRiskColor = (level) => {
    switch (level?.toUpperCase()) {
      case 'LOW':
        return 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
      case 'MEDIUM':
        return 'text-amber-400 border-amber-500/30 bg-amber-500/10';
      case 'HIGH':
        return 'text-rose-400 border-rose-500/30 bg-rose-500/10';
      default:
        return 'text-slate-400 border-slate-700 bg-slate-900';
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border-slate-800 space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-white">Placement Risk Signals</h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30">
                PLANNED — prototype
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Experimental early-warning signals only. Not validated on real verified outcome data.
            </p>
          </div>
        </div>

        <button
          onClick={fetchRiskAndInterventions}
          disabled={loading}
          className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white flex items-center gap-1.5 transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Re-evaluate</span>
        </button>
      </div>

      {loading && !riskData ? (
        <div className="py-8 text-center text-slate-400 text-xs flex items-center justify-center gap-2">
          <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />
          <span>Evaluating longitudinal training signals with ML model...</span>
        </div>
      ) : riskData ? (
        <div className="space-y-6">
          <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-[11px] text-amber-200 leading-relaxed">
            <strong>PLANNED — prototype only:</strong> placement-risk scoring is experimental and trained on synthetic demo data.
            Do not use it for admission, placement, funding, or policy decisions until it is trained and evaluated on real verified outcome data.
            {riskData.disclaimer ? ` Model note: ${riskData.disclaimer}` : ''}
          </div>
          {/* Main Risk Overview */}
          {riskData.available && <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Risk Level Box */}
            <div className={`p-4 rounded-xl border flex flex-col justify-between ${getRiskColor(riskData.risk_level)}`}>
              <div>
                <div className="text-[10px] uppercase font-bold tracking-widest text-slate-400 mb-1">
                  Predicted Placement Risk
                </div>
                <div className="text-2xl font-black">{riskData.risk_level || 'UNKNOWN'}</div>
              </div>
              <div className="mt-3">
                {getRiskBadge(riskData.risk_level)}
              </div>
            </div>

            {/* Risk Score Gauge */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
              <div>
                <div className="text-[10px] uppercase font-bold tracking-widest text-slate-400 mb-1">
                  Risk Probability Score
                </div>
                <div className="text-2xl font-black font-mono text-white">
                  {riskData.risk_score ? `${riskData.risk_score.toFixed(1)}%` : 'N/A'}
                </div>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 mt-3 overflow-hidden">
                <div
                  className={`h-2 rounded-full transition-all duration-500 ${
                    (riskData.risk_score || 0) > 65
                      ? 'bg-rose-500'
                      : (riskData.risk_score || 0) > 35
                      ? 'bg-amber-500'
                      : 'bg-emerald-500'
                  }`}
                  style={{ width: `${Math.min(100, Math.max(5, riskData.risk_score || 0))}%` }}
                />
              </div>
            </div>

            {/* Placement Probability */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
              <div>
                <div className="text-[10px] uppercase font-bold tracking-widest text-slate-400 mb-1">
                  Model Placement Likelihood
                </div>
                <div className="text-2xl font-black font-mono text-emerald-400">
                  {riskData.prob_placed !== null && riskData.prob_placed !== undefined
                    ? `${riskData.prob_placed.toFixed(1)}%`
                    : 'Not available'}
                </div>
              </div>
              <div className="text-[11px] text-slate-400 mt-2">
                Derived from training attendance, assessment scores & verified skills
              </div>
            </div>
          </div>

          }
          {/* Contributing Factors */}
          {riskData.contributing_factors && riskData.contributing_factors.length > 0 && (
            <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800/80 space-y-2">
              <div className="flex items-center gap-2 text-xs font-bold text-amber-400">
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>Identified Risk Drivers & Early Indicators:</span>
              </div>
              <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-300">
                {riskData.contributing_factors.map((factor, idx) => (
                  <li key={idx} className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-400 shrink-0" />
                    <span>{factor}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Interventions Section */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm font-bold text-white">
                <Sparkles className="w-4 h-4 text-emerald-400" />
                <span>Targeted Skilling Interventions ({interventions.length})</span>
              </div>
              <button
                type="button"
                onClick={handleRequestIntervention}
                disabled={requestingIntervention || !riskData.available}
                className="px-3 py-1.5 rounded-lg text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition-all shadow-md shadow-emerald-950 flex items-center gap-1.5 disabled:opacity-50"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>{requestingIntervention ? 'Generating...' : 'Generate New Intervention'}</span>
              </button>
            </div>

            {interventions.length === 0 ? (
              <div className="p-4 rounded-xl bg-slate-950/60 border border-dashed border-slate-800 text-center text-xs text-slate-400">
                No active intervention programs assigned yet. Click "Generate New Intervention" to let NEXTUP prescribe custom remedial sprints.
              </div>
            ) : (
              <div className="space-y-3">
                {interventions.map((item) => (
                  <div
                    key={item.id}
                    className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3 hover:border-slate-700 transition-all"
                  >
                    <div className="flex flex-wrap items-start justify-between gap-2">
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="text-xs font-bold text-white">{item.title}</h4>
                          <span
                            className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                              item.status === 'COMPLETED'
                                ? 'bg-emerald-500/20 text-emerald-400'
                                : item.status === 'IN_PROGRESS'
                                ? 'bg-cyan-500/20 text-cyan-400'
                                : 'bg-amber-500/20 text-amber-400'
                            }`}
                          >
                            {item.status}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400 mt-0.5">{item.description}</p>
                      </div>

                      {/* Status Action Buttons */}
                      <div className="flex items-center gap-1.5">
                        {item.status === 'RECOMMENDED' && (
                          <button
                            onClick={() => handleStatusChange(item.id, 'IN_PROGRESS')}
                            className="px-2.5 py-1 rounded text-[11px] font-semibold bg-cyan-600/80 hover:bg-cyan-500 text-white transition-all"
                          >
                            Start Action
                          </button>
                        )}
                        {item.status === 'IN_PROGRESS' && (
                          <button
                            onClick={() => handleStatusChange(item.id, 'COMPLETED')}
                            className="px-2.5 py-1 rounded text-[11px] font-semibold bg-emerald-600/80 hover:bg-emerald-500 text-white transition-all"
                          >
                            Mark Completed
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Recommended Actions list */}
                    {item.recommended_actions && item.recommended_actions.length > 0 && (
                      <div className="pt-2 border-t border-slate-800/60">
                        <div className="text-[10px] uppercase font-bold tracking-wider text-slate-400 mb-1.5">
                          Action Items:
                        </div>
                        <ul className="space-y-1">
                          {item.recommended_actions.map((act, actIdx) => (
                            <li key={actIdx} className="text-xs text-slate-300 flex items-start gap-2">
                              <span className="text-cyan-400 font-bold">•</span>
                              <span>{act}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Prototype disclosure */}
          <div className="text-[10px] text-slate-500 border-t border-slate-800/60 pt-3 flex items-center justify-between">
            <span>
              Placement-risk model: PLANNED prototype trained on synthetic demo data. No accuracy is claimed.
            </span>
            <span className="font-mono text-cyan-400">NEXTUP v1.0</span>
          </div>
        </div>
      ) : null}
    </div>
  );
};
