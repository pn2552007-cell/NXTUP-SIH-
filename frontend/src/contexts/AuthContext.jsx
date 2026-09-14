import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => localStorage.getItem('nextup_token'));
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('nextup_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          const res = await authAPI.getMe();
          setUser(res.data);
          localStorage.setItem('nextup_user', JSON.stringify(res.data));
        } catch (err) {
          console.error('Session restore failed:', err);
          logout();
        }
      }
      setLoading(false);
    };
    initAuth();
  }, [token]);

  const login = async (email, password) => {
    const res = await authAPI.login({ email, password });
    const data = res.data;
    setToken(data.access_token);
    setUser(data);
    localStorage.setItem('nextup_token', data.access_token);
    localStorage.setItem('nextup_user', JSON.stringify(data));
    return data;
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('nextup_token');
    localStorage.removeItem('nextup_user');
    // Clean up old skillpulse keys if present
    localStorage.removeItem('skillpulse_token');
    localStorage.removeItem('skillpulse_user');
  };

  const updateConsentStatus = (consentGiven, nextupId) => {
    setUser((prev) => {
      const updated = {
        ...prev,
        consent_given: consentGiven,
        nextup_id: nextupId || prev?.nextup_id,
        skillpulse_id: nextupId || prev?.skillpulse_id,
      };
      localStorage.setItem('nextup_user', JSON.stringify(updated));
      return updated;
    });
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        role: user?.role || null,
        isAuthenticated: !!token,
        consentGiven: user?.consent_given || false,
        nextupId: user?.nextup_id || user?.skillpulse_id || null,
        skillpulseId: user?.nextup_id || user?.skillpulse_id || null, // backward compat
        loading,
        login,
        logout,
        updateConsentStatus,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
