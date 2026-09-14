import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { consentAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { ShieldCheck, Lock, CheckCircle2, XCircle, FileText, AlertTriangle, ArrowRight, Sparkles, Undo2 } from 'lucide-react';
import { Badge } from '../components/common/Badge';

export const ConsentPage = () => {
  const { user, updateConsentStatus, nextupId, skillpulseId } = useAuth();
  const { showSuccess, showError } = useToast();
  const navigate = useNavigate();

  const [hasConsent, setHasConsent] = useState(false);
  const [agreed, setAgreed] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [activeId, setActiveId] = useState(nextupId || skillpulseId || null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await consentAPI.getStatus();
        if (res.data.consent_given) {
          setHasConsent(true);
          setAgreed(true);
          const assignedId = res.data.nextup_id || res.data.skillpulse_id;
          if (assignedId) setActiveId(assignedId);
        }
      } catch (err) {
        console.error('Failed to fetch consent status:', err);
      }
    };
    fetchStatus();
  }, []);

  const handleGiveConsent = async () => {
    if (!agreed) {
      showError('Please check the consent authorization box to continue.');
      return;
    }

    setSubmitting(true);
    try {
      const res = await consentAPI.submit({
        consent_status: true,
        consent_version: 'v1.0',
        purpose: 'Longitudinal tracking of training, employment, retention, and wage progression',
        consent_text: 'I voluntarily consent to NEXTUP tracking my longitudinal training and employment outcomes under DPDP Act framework.',
      });

      showSuccess(res.data.message);
      const assignedId = res.data.nextup_id || res.data.skillpulse_id;
      updateConsentStatus(true, assignedId);
      setActiveId(assignedId);
      setHasConsent(true);
    } catch (err) {
      showError('Failed to record consent');
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleRevokeConsent = async () => {
    setSubmitting(true);
    try {
      await consentAPI.revoke({ reason: 'Trainee explicitly revoked outcome tracking consent.' });
      updateConsentStatus(false, activeId);
      setHasConsent(false);
      setAgreed(false);
      showSuccess('Consent has been revoked. Longitudinal outcome tracking is now disabled.');
    } catch (err) {
      showError('Failed to revoke consent.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-8 space-y-6">
      {/* Header Banner */}
      <div className="text-center space-y-2">
        <div className="inline-flex p-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 mb-2">
          <ShieldCheck className="w-8 h-8" />
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Your Data, Your Consent.
        </h1>
        <p className="text-xs sm:text-sm text-slate-300 max-w-xl mx-auto">
          NEXTUP strictly adheres to India's Digital Personal Data Protection (DPDP) Act. Explicit consent is mandatory to create your unified NEXTUP ID and initiate longitudinal outcome tracking.
        </p>
      </div>

      {/* Active ID Banner if consented */}
      {hasConsent && activeId && (
        <div className="glass-panel-glow rounded-2xl p-6 border-emerald-500/40 text-center space-y-3">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-bold">
            <Sparkles className="w-3.5 h-3.5" />
            NEXTUP ID Activated
          </div>
          <div className="text-3xl font-black font-mono tracking-wider text-white">
            {activeId}
          </div>
          <p className="text-xs text-slate-300 max-w-md mx-auto">
            This persistent identifier connects your institutional training, assessment certifications, ML risk profile, employer verification records, and wage progression securely.
          </p>
          <div className="pt-2">
            <button
              onClick={() => navigate('/trainee/dashboard')}
              className="px-6 py-2.5 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition-all shadow-lg shadow-emerald-950 inline-flex items-center gap-2"
            >
              <span>Go to Trainee Journey Dashboard</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Consent Details Card */}
      <div className="glass-panel rounded-2xl p-6 space-y-6 border-slate-800">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-2 text-sm font-bold text-white">
            <FileText className="w-4 h-4 text-emerald-400" />
            <span>Digital Consent Agreement (DPDP Compliant • v1.0)</span>
          </div>
          <Badge variant={hasConsent ? 'emerald' : 'amber'}>
            {hasConsent ? 'Consent Active ✓' : 'Awaiting Consent'}
          </Badge>
        </div>

        {/* Informational Clauses */}
        <div className="space-y-3 text-xs text-slate-300 bg-slate-950/60 p-4 rounded-xl border border-slate-800/80 leading-relaxed">
          <div className="font-semibold text-white">How NEXTUP Uses Your Skilling Information:</div>
          <ul className="space-y-2 list-disc list-inside text-slate-400">
            <li>
              <strong>Training & Assessment Records:</strong> Connect your attendance, course completions, and assessment scores from accredited training providers.
            </li>
            <li>
              <strong>AI Placement Risk & Interventions:</strong> Calculate early dropout/placement risk to recommend tailored bridge courses and mentorship before training concludes.
            </li>
            <li>
              <strong>Post-Training Employment Verification:</strong> Facilitate employer verification of job titles, joining dates, and starting compensation to ensure data integrity.
            </li>
            <li>
              <strong>Longitudinal Follow-ups:</strong> Schedule automated check-in notifications (30-day, 90-day, 6-month, and 1-year) via portal and messaging gateways to track retention and salary progression.
            </li>
            <li>
              <strong>Policy Analytics:</strong> Aggregate outcomes for state and sector skilling dashboards to benchmark training effectiveness.
            </li>
          </ul>
        </div>

        {/* Consent Checkbox */}
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-700/80 space-y-2">
          <label className="flex items-start gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
              className="mt-1 w-4 h-4 text-emerald-600 bg-slate-950 border-slate-600 rounded focus:ring-emerald-500"
            />
            <span className="text-xs text-slate-200 font-medium">
              I voluntarily consent to NEXTUP tracking my training, employment, retention, and wage growth outcomes. I understand that I can review, update, or revoke my consent at any time.
            </span>
          </label>
        </div>

        {/* Actions */}
        <div className="flex flex-wrap items-center justify-end gap-3 pt-2">
          {hasConsent ? (
            <button
              type="button"
              disabled={submitting}
              onClick={handleRevokeConsent}
              className="px-4 py-2.5 rounded-xl text-xs font-semibold bg-rose-950/30 text-rose-400 border border-rose-500/30 hover:bg-rose-900/50 transition-all flex items-center gap-1.5"
            >
              <Undo2 className="w-4 h-4" />
              <span>Revoke Consent</span>
            </button>
          ) : (
            <button
              type="button"
              disabled={!agreed || submitting}
              onClick={handleGiveConsent}
              className="px-6 py-2.5 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition-all shadow-lg shadow-emerald-950 disabled:opacity-50 flex items-center gap-2"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>{submitting ? 'Recording Consent...' : 'Grant Consent & Activate NEXTUP ID'}</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
