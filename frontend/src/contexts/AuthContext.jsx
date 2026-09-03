import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => localStorage.getItem('skillpulse_token'));
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('skillpulse_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          const res = await authAPI.getMe();
          setUser(res.data);
          localStorage.setItem('skillpulse_user', JSON.stringify(res.data));
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
    localStorage.setItem('skillpulse_token', data.access_token);
    localStorage.setItem('skillpulse_user', JSON.stringify(data));
    return data;
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('skillpulse_token');
    localStorage.removeItem('skillpulse_user');
  };

  const updateConsentStatus = (consentGiven, skillpulseId) => {
    setUser((prev) => {
      const updated = { ...prev, consent_given: consentGiven, skillpulse_id: skillpulseId || prev?.skillpulse_id };
      localStorage.setItem('skillpulse_user', JSON.stringify(updated));
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
        skillpulseId: user?.skillpulse_id || null,
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
