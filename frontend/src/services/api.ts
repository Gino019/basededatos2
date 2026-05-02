import type {
  Connection, ConnectionCreate,
  MaskingRule, RuleCreate,
  MaskingJob, JobCreate,
  Summary, User, AuthResponse
} from '../types';

const BASE = import.meta.env.VITE_API_URL || '/api/v1';
const TOKEN_KEY = 'enmask_access_token';

export function getStoredToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearStoredToken() {
  localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getStoredToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE}${path}`, {
    headers,
    ...init,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail ?? 'Request failed');
  }
  if (res.status === 204) return undefined as unknown as T;
  return res.json();
}

// ---- Auth ----
export const signInWithGoogle = (idToken: string) =>
  request<AuthResponse>('/auth/google', { method: 'POST', body: JSON.stringify({ id_token: idToken }) });
export const getCurrentUser = () => request<User>('/auth/me');

// ---- Connections ----
export const getConnections = () => request<Connection[]>('/connections/');
export const createConnection = (data: ConnectionCreate) =>
  request<Connection>('/connections/', { method: 'POST', body: JSON.stringify(data) });
export const deleteConnection = (id: string) =>
  request<void>(`/connections/${id}`, { method: 'DELETE' });

// ---- Rules ----
export const getRules = () => request<MaskingRule[]>('/rules/');
export const createRule = (data: RuleCreate) =>
  request<MaskingRule>('/rules/', { method: 'POST', body: JSON.stringify(data) });
export const deleteRule = (id: string) =>
  request<void>(`/rules/${id}`, { method: 'DELETE' });

// ---- Jobs ----
export const getJobs = () => request<MaskingJob[]>('/jobs/');
export const createJob = (data: JobCreate) =>
  request<MaskingJob>('/jobs/', { method: 'POST', body: JSON.stringify(data) });
export const runJob = (id: string) =>
  request<{ message: string }>(`/jobs/${id}/run`, { method: 'POST' });
export const getJob = (id: string) => request<MaskingJob>(`/jobs/${id}`);

// ---- Reports ----
export const getSummary = () => request<Summary>('/reports/summary');
