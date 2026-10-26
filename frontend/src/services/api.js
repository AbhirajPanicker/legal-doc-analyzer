/**
 * Axios API client — all backend calls go through this file.
 * The Vite dev proxy forwards /api/* to http://localhost:8000.
 * An Axios request interceptor automatically attaches the Bearer token
 * from localStorage to every outgoing request.
 */
import axios from 'axios';

const TOKEN_KEY = 'lex_token';

const api = axios.create({
  baseURL: `${import.meta.env.VITE_API_URL}/api/v1`,
});

// ── Auth token injection ───────────────────────────────────────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Auth endpoints (no token required) ────────────────────────────────────────

export const loginUser = (email, password) =>
  api.post('/auth/login', { email, password });

export const registerUser = (email, password, full_name = '') =>
  api.post('/auth/register', { email, password, full_name });

export const getMe = () => api.get('/auth/me');

// ── Documents ──────────────────────────────────────────────────────────────────

export const uploadDocument = (formData, onProgress) =>
  api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: onProgress,
  });

export const listDocuments = () => api.get('/documents');

export const getDocument = (id) => api.get(`/documents/${id}`);

export const deleteDocument = (id) => api.delete(`/documents/${id}`);

// ── Chat ───────────────────────────────────────────────────────────────────────

export const askQuestion = (docId, question, eli5 = false) =>
  api.post(`/chat/${docId}`, { question, eli5 });

// ── Summarise ──────────────────────────────────────────────────────────────────

export const summariseDocument = (docId) =>
  api.post(`/summarise/${docId}`, {}, { timeout: 180000 }); // 3 min for large docs

// ── Clause Analysis ────────────────────────────────────────────────────────────

export const analyseDocumentClauses = (docId) =>
  api.post(`/clauses/${docId}`, {}, { timeout: 180000 }); // 3 min for large docs

export const detectBlindSpots = (docId) =>
  api.post(`/blind-spots/${docId}`, {}, { timeout: 180000 }); // 3 min for deep audit

// ── ELI5 Jargon Decoder ────────────────────────────────────────────────────────

export const decodeJargon = (text) =>
  api.post('/eli5/decode', { text });

export const getJargonPresets = () =>
  api.get('/eli5/presets');

// ── Status ─────────────────────────────────────────────────────────────────────

export const getStatus = () => api.get('/status');

export default api;
