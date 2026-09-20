import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Activity, LogOut, ShieldCheck, UserPlus } from 'lucide-react';

export const Navbar = () => {
  const { user, isAuthenticated, logout, role, nextupId } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-40 bg-slate-950/80 backdrop-blur-md border-b border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 p-0.5 shadow-lg shadow-emerald-950/40 group-hover:scale-105 transition-transform">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Activity className="w-5 h-5 text-emerald-400" />
            </div>
          </div>
          <div>
            <span className="text-xl font-bold tracking-tight text-white flex items-center gap-1.5">
              NXTUP
            </span>
            <div className="text-[9px] text-slate-500 -mt-0.5">AI-Powered Skilling Outcome Platform</div>
          </div>
        </Link>

        {/* Right Action Nav */}
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <div className="flex items-center gap-3">
              {nextupId && (
                <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-lg bg-emerald-950/50 border border-emerald-500/30 text-emerald-300 font-mono text-xs font-semibold">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                  <span>{nextupId}</span>
                </div>
              )}
              <div className="text-right hidden sm:block">
                <div className="text-xs font-semibold text-white">{user?.full_name}</div>
                <div className="text-[11px] text-slate-400 capitalize">{role?.replace('_', ' ').toLowerCase()}</div>
              </div>
              <button
                onClick={handleLogout}
                title="Sign out"
                className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-rose-400 hover:border-rose-500/30 hover:bg-rose-950/20 transition-all"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2.5">
              <Link
                to="/login"
                className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="px-4 py-2 rounded-xl text-sm font-semibold bg-emerald-600 text-white hover:bg-emerald-500 transition-all shadow-lg shadow-emerald-900/30 flex items-center gap-1.5"
              >
                <UserPlus className="w-4 h-4" />
                Register
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
