const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '');

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    });
  } catch (error) {
    throw new Error(`Backend unavailable${API_BASE_URL ? ` at ${API_BASE_URL}` : ''}. Start Flask and try again.`);
  }
  let payload;
  try { payload = await response.json(); } catch { throw new Error(`Backend returned a non-JSON response (${response.status}).`); }
  if (!response.ok || !payload.success) throw new Error(payload.error?.message || `Request failed (${response.status}).`);
  return payload.data;
}

export const api = {
  createCase: (body) => request('/api/cases', { method: 'POST', body: JSON.stringify(body) }),
  analyze: (body) => request('/api/investigations/analyze', { method: 'POST', body: JSON.stringify(body) }),
  getCase: (id) => request(`/api/cases/${encodeURIComponent(id)}`),
  getPriority: (id) => request(`/api/cases/${encodeURIComponent(id)}/priority`),
  getRisk: (id) => request(`/api/cases/${encodeURIComponent(id)}/risk`),
  getTransactions: (id) => request(`/api/cases/${encodeURIComponent(id)}/transactions?page=1&limit=100`),
  getGraph: (id) => request(`/api/cases/${encodeURIComponent(id)}/graph`),
  getRelated: (id) => request(`/api/cases/${encodeURIComponent(id)}/related`),
  getAttribution: (id) => request(`/api/cases/${encodeURIComponent(id)}/attribution`),
  getReport: (id) => request(`/api/cases/${encodeURIComponent(id)}/report`),
};

export { API_BASE_URL };
