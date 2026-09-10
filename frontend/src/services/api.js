import axios from 'axios';

const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || '';
const apiBaseUrl = rawBaseUrl.replace(/\/+$/, '');

const api = axios.create({
  baseURL: apiBaseUrl ? `${apiBaseUrl}/api` : '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to auto-inject Bearer token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('skillpulse_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor to handle expired tokens
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('skillpulse_token');
      localStorage.removeItem('skillpulse_user');
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  getMe: () => api.get('/auth/me'),
};

export const consentAPI = {
  getStatus: () => api.get('/consent/status'),
  submit: (consentData) => api.post('/consent', consentData),
  revoke: (reasonData) => api.post('/consent/revoke', reasonData),
  getAuditTrail: () => api.get('/consent/audit-trail'),
};

export const traineeAPI = {
  getProfile: () => api.get('/trainee/profile'),
  getJourney: () => api.get('/trainee/journey'),
  getSkills: () => api.get('/trainee/skills'),
  addSkill: (skillData) => api.post('/trainee/skills', skillData),
  getWageGrowth: () => api.get('/trainee/wage-growth'),
};

export const employmentAPI = {
  report: (data) => api.post('/employment', data),
  getRecord: (id) => api.get(`/employment/${id}`),
};

export const followupsAPI = {
  getAll: () => api.get('/followups'),
  respond: (data) => api.post('/followups/respond', data),
  schedule: (params) => api.post('/followups/schedule', null, { params }),
};

export const employerAPI = {
  getDashboard: () => api.get('/employer/dashboard'),
  verify: (data) => api.post('/employer/verify', data),
  searchCandidates: (params) => api.get('/employer/candidates', { params }),
};

export const providerAPI = {
  getDashboard: (params) => api.get('/providers/dashboard', { params }),
  getTrainees: (params) => api.get('/providers/trainees', { params }),
  createCourse: (data) => api.post('/providers/courses', data),
  getCourses: () => api.get('/providers/courses'),
  createBatch: (data) => api.post('/providers/batches', data),
  enrollTrainee: (data) => api.post('/providers/enroll', data),
  importCsv: (formData) =>
    api.post('/providers/import-trainees', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  downloadSampleCsvUrl: apiBaseUrl ? `${apiBaseUrl}/api/providers/sample-csv` : '/api/providers/sample-csv',
};

export const adminAPI = {
  getDashboard: (params) => api.get('/admin/dashboard', { params }),
  getFilters: () => api.get('/admin/filters'),
};

export const analyticsAPI = {
  getOverview: (params) => api.get('/analytics/overview', { params }),
  getEmployment: () => api.get('/analytics/employment'),
  getRetention: () => api.get('/analytics/retention'),
  getWageGrowth: () => api.get('/analytics/wage-growth'),
  getSkillGaps: () => api.get('/analytics/skill-gaps'),
  getProviders: () => api.get('/analytics/providers'),
  getCourses: () => api.get('/analytics/courses'),
  getDistricts: () => api.get('/analytics/districts'),
};

export const aiAPI = {
  getJobRoles: () => api.get('/ai/job-roles'),
  analyzeSkillGap: (data) => api.post('/ai/skill-gap', data),
};

export default api;
