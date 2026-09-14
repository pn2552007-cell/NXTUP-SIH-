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
  const token = localStorage.getItem('nextup_token');
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
      localStorage.removeItem('nextup_token');
      localStorage.removeItem('nextup_user');
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
  send: (followupId) => api.post(`/followups/send/${followupId}`),
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
  getFilters: (params) => api.get('/admin/filters', { params }),
  getTrainees: (params) => api.get('/admin/trainees', { params }),
  getTraineeDetail: (id) => api.get(`/admin/trainees/${id}`),
  getUsers: (params) => api.get('/admin/users', { params }),
  getTraining: (params) => api.get('/admin/training', { params }),
  getCertificates: (params) => api.get('/admin/certificates', { params }),
  getEmployment: (params) => api.get('/admin/employment', { params }),
  getEmployerVerification: (params) => api.get('/admin/employer-verification', { params }),
  getFollowups: (params) => api.get('/admin/followups', { params }),
  getSkillGaps: (params) => api.get('/admin/skill-gaps', { params }),
  getPolicyInsights: (params) => api.get('/admin/policy-insights', { params }),
  getReports: (params) => api.get('/admin/reports', { params }),
  getAuditLogs: (params) => api.get('/admin/audit-logs', { params }),
  getSettings: () => api.get('/admin/settings'),
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

export const mlAPI = {
  predictRisk: (data) => api.post('/ml/predict-risk', data),
  getModelInfo: () => api.get('/ml/model-info'),
  recommendIntervention: (data) => api.post('/ml/recommend-intervention', data),
  getRetrainStatus: () => api.get('/ml/retrain-status'),
};

export const interventionsAPI = {
  listForTrainee: (traineeId) => api.get(`/interventions/trainee/${traineeId}`),
  create: (data) => api.post('/interventions', data),
  updateStatus: (id, status) => api.patch(`/interventions/${id}/status`, { status }),
};

export const jobsAPI = {
  list: (params) => api.get('/jobs', { params }),
};

export default api;
