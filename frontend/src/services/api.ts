import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import type {
  LoginResponse,
  User,
  DashboardStats,
  Threat,
  Vulnerability,
  Scan,
  MalwareReport,
  AIResponse,
  Conversation,
  Message,
  Report,
  ReportDetail,
  Notification,
  PaginatedResponse,
  Device,
  NetworkStats,
  SiemLog,
  EdrProcess,
  Playbook,
  PlaybookExecution,
  FimEntry,
} from '../types';

const API_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_URL ? `${API_URL}/api` : '/api',
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken && error.config && !(error.config as any)._retry) {
        (error.config as any)._retry = true;
        try {
          const { data } = await axios.post('/api/auth/refresh', {
            refresh_token: refreshToken,
          });
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('refresh_token', data.refresh_token);
          error.config!.headers.Authorization = `Bearer ${data.access_token}`;
          return api(error.config!);
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// Auth
export const auth = {
  login: (email: string, password: string) =>
    api.post<LoginResponse>('/auth/login', { email, password }).then(r => r.data),
  register: (data: { email: string; username: string; password: string; full_name?: string }) =>
    api.post<LoginResponse>('/auth/register', data).then(r => r.data),
  me: () => api.get<User>('/auth/me').then(r => r.data),
  changePassword: (current_password: string, new_password: string) =>
    api.post('/auth/change-password', { current_password, new_password }),
};

// Dashboard
export const dashboard = {
  stats: () => api.get<DashboardStats>('/dashboard/stats').then(r => r.data),
};

// Threats
export const threats = {
  list: (params?: { page?: number; severity?: string; indicator_type?: string }) =>
    api.get<PaginatedResponse<Threat>>('/threats', { params }).then(r => r.data),
  summary: () => api.get('/threats/summary').then(r => r.data),
};

// CVEs
export const cves = {
  search: (params?: { query?: string; severity?: string; vendor?: string; product?: string; page?: number }) =>
    api.get('/cves', { params }).then(r => r.data),
  get: (cveId: string) => api.get<Vulnerability>(`/cves/${cveId}`).then(r => r.data),
  sync: () => api.post('/cves/sync').then(r => r.data),
};

// Scans
export const scans = {
  create: (data: { target: string; scan_type: string }) =>
    api.post<Scan>('/scans', data).then(r => r.data),
  list: (params?: { page?: number; page_size?: number }) =>
    api.get<PaginatedResponse<Scan>>('/scans', { params }).then(r => r.data),
  get: (id: number) => api.get<Scan>(`/scans/${id}`).then(r => r.data),
};

// AI
export const ai = {
  chat: (data: { message: string; conversation_id?: number }) =>
    api.post<AIResponse>('/ai/chat', data).then(r => r.data),
  conversations: () =>
    api.get<Conversation[]>('/ai/conversations').then(r => r.data),
  messages: (conversationId: number) =>
    api.get<Message[]>(`/ai/conversations/${conversationId}/messages`).then(r => r.data),
};

// Reports
export const reports = {
  create: (data: { title: string; report_type: string }) =>
    api.post<Report>('/reports', data).then(r => r.data),
  list: (params?: { page?: number }) =>
    api.get<PaginatedResponse<Report>>('/reports', { params }).then(r => r.data),
  get: (id: number) => api.get<ReportDetail>(`/reports/${id}`).then(r => r.data),
  delete: (id: number) => api.delete(`/reports/${id}`),
};

// Notifications
export const notifications = {
  list: (params?: { is_read?: boolean; page?: number; page_size?: number }) =>
    api.get('/notifications', { params }).then(r => r.data),
  markRead: (id: number) =>
    api.patch(`/notifications/${id}`, { is_read: true }),
  markAllRead: () => api.post('/notifications/mark-all-read'),
};

// Files
export const files = {
  upload: (file: File) => {
    const form = new FormData();
    form.append('file', file);
    return api.post('/files/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(r => r.data);
  },
};

// Users (admin)
export const users = {
  list: (params?: { page?: number }) =>
    api.get<PaginatedResponse<User>>('/users', { params }).then(r => r.data),
  get: (id: number) => api.get(`/users/${id}`).then(r => r.data),
  update: (id: number, data: any) => api.patch(`/users/${id}`, data),
  delete: (id: number) => api.delete(`/users/${id}`),
  roles: () => api.get('/users/roles/list').then(r => r.data),
};

// Settings (admin)
export const settings = {
  get: () => api.get('/settings').then(r => r.data),
  update: (key: string, value: string) => api.put(`/settings/${key}`, { value }),
};

// Network
export const network = {
  devices: (params?: { page?: number; status?: string }) =>
    api.get<PaginatedResponse<Device>>('/network/devices', { params }).then(r => r.data),
  stats: () =>
    api.get<NetworkStats>('/network/info').then(r => r.data),
};

// Audit Logs (admin)
export const auditLogs = {
  list: (params?: { page?: number; action?: string }) =>
    api.get('/audit-logs', { params }).then(r => r.data),
};

// MFA
export const mfa = {
  setup: () => api.post('/auth/mfa/setup').then(r => r.data),
  verifySetup: (code: string) => api.post('/auth/mfa/verify-setup', { code }).then(r => r.data),
  verify: (code: string) => api.post('/auth/mfa/verify', { code }).then(r => r.data),
  disable: () => api.post('/auth/mfa/disable').then(r => r.data),
  status: () => api.get('/auth/mfa/status').then(r => r.data),
};

// SIEM
export const siem = {
  logs: (params?: any) => api.get<PaginatedResponse<SiemLog>>('/siem/logs', { params }).then(r => r.data),
  get: (id: number) => api.get<SiemLog>(`/siem/logs/${id}`).then(r => r.data),
  stats: () => api.get('/siem/stats').then(r => r.data),
};

// EDR
export const edr = {
  processes: (params?: { suspicious_only?: boolean; search?: string }) =>
    api.get('/edr/processes', { params }).then(r => r.data),
  get: (pid: number) => api.get(`/edr/processes/${pid}`).then(r => r.data),
  stats: () => api.get('/edr/stats').then(r => r.data),
};

// SOAR
export const soar = {
  playbooks: () => api.get('/soar/playbooks').then(r => r.data),
  create: (data: any) => api.post('/soar/playbooks', data).then(r => r.data),
  toggle: (id: number) => api.post(`/soar/playbooks/${id}/toggle`).then(r => r.data),
  delete: (id: number) => api.delete(`/soar/playbooks/${id}`).then(r => r.data),
  executions: (params?: any) => api.get('/soar/executions', { params }).then(r => r.data),
};

// FIM
export const fim = {
  entries: (params?: any) => api.get('/fim/entries', { params }).then(r => r.data),
  scan: () => api.post('/fim/scan').then(r => r.data),
  add: (file_path: string) => api.post('/fim/add', { file_path }).then(r => r.data),
  stats: () => api.get('/fim/stats').then(r => r.data),
};

export default api;
