import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { Activity, Mail, Lock, ArrowRight, Loader2, ShieldCheck, Sparkles, UserCheck } from 'lucide-react';

export const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const { login } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();

  const handleQuickFill = (demoEmail, demoPass) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setErrorMsg('');
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setErrorMsg('Please enter both email and password.');
      return;
    }

    setSubmitting(true);
    setErrorMsg('');

    try {
      const user = await login(email, password);
      addToast(`Welcome back, ${user.full_name}!`, 'success');

      // Route by role
      if (user.role === 'TRAINEE') {
        if (!user.consent_given) {
          navigate('/consent');
        } else {
          navigate('/trainee/dashboard');
        }
      } else if (user.role === 'PROVIDER' || user.role === 'TRAINING_PROVIDER') {
        navigate('/provider/dashboard');
      } else if (user.role === 'EMPLOYER') {
        navigate('/employer/dashboard');
      } else if (user.role === 'ADMIN') {
        navigate('/admin/dashboard');
      } else {
        navigate('/');
      }
    } catch (err) {
      const msg = err.response?.data?.detail || 'Authentication failed. Please check your credentials.';
      setErrorMsg(msg);
      addToast(msg, 'error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 sm:px-6 lg:px-8 py-12">
      <div className="w-full max-w-md space-y-6">
        {/* Title */}
        <div className="text-center space-y-2">
          <div className="inline-flex p-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 mb-2">
            <Activity className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Sign In to NEXTUP</h2>
          <p className="text-xs text-slate-400">
            AI-Powered Skilling Outcome Platform
          </p>
        </div>

        {/* Quick Demo Logins */}
        <div className="glass-panel rounded-2xl p-4 border-slate-800 space-y-2.5">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-400">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Quick Demo Presets (1-Click Fill)</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <button
              type="button"
              onClick={() => handleQuickFill('trainee@nextup.demo', 'NextUp@Demo2026!')}
              className="px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-emerald-500/40 text-slate-300 hover:text-white text-left transition-all flex items-center justify-between"
            >
              <span>🎓 Trainee</span>
              <span className="text-[10px] text-emerald-400 font-mono">Fill</span>
            </button>
            <button
              type="button"
              onClick={() => handleQuickFill('provider@nextup.demo', 'NextUp@Demo2026!')}
              className="px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-purple-500/40 text-slate-300 hover:text-white text-left transition-all flex items-center justify-between"
            >
              <span>🏫 Provider</span>
              <span className="text-[10px] text-purple-400 font-mono">Fill</span>
            </button>
            <button
              type="button"
              onClick={() => handleQuickFill('employer@nextup.demo', 'NextUp@Demo2026!')}
              className="px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-blue-500/40 text-slate-300 hover:text-white text-left transition-all flex items-center justify-between"
            >
              <span>💼 Employer</span>
              <span className="text-[10px] text-blue-400 font-mono">Fill</span>
            </button>
            <button
              type="button"
              onClick={() => handleQuickFill('admin@nextup.demo', 'NextUp@Demo2026!')}
              className="px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-cyan-500/40 text-slate-300 hover:text-white text-left transition-all flex items-center justify-between"
            >
              <span>🏛️ Admin / Govt</span>
              <span className="text-[10px] text-cyan-400 font-mono">Fill</span>
            </button>
          </div>
        </div>

        {errorMsg && (
          <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs">
            {errorMsg}
          </div>
        )}

        {/* Standard Credentials Form */}
        <form onSubmit={handleLogin} className="glass-panel rounded-2xl p-6 border-slate-800 space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@nextup.demo"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/90 border border-slate-800 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 text-sm text-white placeholder-slate-500 outline-none transition-all"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold text-slate-300">Password</label>
            </div>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/90 border border-slate-800 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 text-sm text-white placeholder-slate-500 outline-none transition-all"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-2.5 px-4 rounded-xl text-sm font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition-all shadow-lg shadow-emerald-950/40 flex items-center justify-center gap-2 mt-2 disabled:opacity-50"
          >
            {submitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Verifying Credentials...</span>
              </>
            ) : (
              <>
                <span>Sign In to NEXTUP</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        {/* Footer info */}
        <div className="text-center text-xs text-slate-400 space-y-2">
          <p>
            Don't have an account yet?{' '}
            <Link to="/register" className="text-emerald-400 hover:underline font-semibold">
              Create a NEXTUP account
            </Link>
          </p>
          <div className="flex items-center justify-center gap-2 pt-2 text-[11px] text-slate-400">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>Role-Based Access Control • End-to-End Encryption</span>
          </div>
        </div>
      </div>
    </div>
  );
};
