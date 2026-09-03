import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ToastProvider } from './contexts/ToastContext';

import { PublicLayout } from './layouts/PublicLayout';
import { DashboardLayout } from './layouts/DashboardLayout';

import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ConsentPage } from './pages/ConsentPage';
import { TraineeDashboard } from './pages/TraineeDashboard';
import { ProviderDashboard } from './pages/ProviderDashboard';
import { EmployerDashboard } from './pages/EmployerDashboard';
import { AdminDashboard } from './pages/AdminDashboard';
import { NotFoundPage } from './pages/NotFoundPage';

// Protected Route Component
const ProtectedRoute = ({ children, allowedRoles }) => {
  const { isAuthenticated, role, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-400 text-xs">
        Authenticating SkillPulse Session...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(role) && role !== 'ADMIN') {
    // If not authorized for this role, redirect to their role dashboard
    if (role === 'TRAINEE') return <Navigate to="/trainee/dashboard" replace />;
    if (role === 'PROVIDER') return <Navigate to="/provider/dashboard" replace />;
    if (role === 'EMPLOYER') return <Navigate to="/employer/dashboard" replace />;
    if (role === 'ADMIN') return <Navigate to="/admin/dashboard" replace />;
    return <Navigate to="/" replace />;
  }

  return children;
};

export function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <AuthProvider>
          <Routes>
            {/* Public Layout Routes */}
            <Route element={<PublicLayout />}>
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/consent" element={<ConsentPage />} />
            </Route>

            {/* Dashboard Layout Routes */}
            <Route element={<DashboardLayout />}>
              <Route
                path="/trainee/dashboard"
                element={
                  <ProtectedRoute allowedRoles={['TRAINEE', 'ADMIN']}>
                    <TraineeDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/provider/dashboard"
                element={
                  <ProtectedRoute allowedRoles={['PROVIDER', 'ADMIN']}>
                    <ProviderDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/employer/dashboard"
                element={
                  <ProtectedRoute allowedRoles={['EMPLOYER', 'ADMIN']}>
                    <EmployerDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin/dashboard"
                element={
                  <ProtectedRoute allowedRoles={['ADMIN']}>
                    <AdminDashboard />
                  </ProtectedRoute>
                }
              />
            </Route>

            {/* 404 Route */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </AuthProvider>
      </ToastProvider>
    </BrowserRouter>
  );
}

export default App;
