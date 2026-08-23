import { api, API_BASE_URL } from './api.js';

const $ = (id) => document.getElementById(id);
const state = { user: JSON.parse(localStorage.getItem('chaintrace_user') || 'null'), caseId: null, report: null };
const setText = (id, value) => { const el = $(id); if (el) el.textContent = value == null ? '—' : String(value); };
const inr = (value) => `₹${Number(value || 0).toLocaleString('en-IN')}`;
const short = (value) => value ? `${value.slice(0, 10)}…${value.slice(-8)}` : '—';

function setSession() {
  const locked = $('sessionLocked'), out = $('sessionOut'), form = $('caseForm'), lock = $('demoLock');
  const signedIn = Boolean(state.user);
  if (locked) locked.style.display = signedIn ? 'none' : 'block';
  if (out) out.classList.toggle('active', signedIn);
  if (form) form.style.display = signedIn ? 'block' : 'none';
  if (lock) lock.classList.toggle('active', !signedIn);
  if (signedIn) { setText('sessionName', state.user.name); setText('sessionRole', state.user.role || 'Investigator'); }
}

function setBusy(busy) {
  const button = document.querySelector('#caseForm button[type="submit"]');
  if (button) { button.disabled = busy; button.textContent = busy ? 'Running backend analysis…' : 'Run automated prioritization'; }
  const form = $('caseForm'); if (form) form.setAttribute('aria-busy', String(busy));
}

function showError(message) {
  setText('rCaseId', `BACKEND ERROR · ${message}`);
  const result = $('resultsState'), placeholder = $('placeholderState');
  if (placeholder) placeholder.style.display = 'none';
  if (result) result.classList.add('active');
  setText('rAmount', '—'); setText('rFraud', 'The request could not be completed.');
}

function renderFactors(factors = {}) {
  const labels = { financial_impact: 'Financial impact', linked_cases: 'Linked complaints', repeated_activity: 'Repeated wallet activity', fund_movement: 'Fund movement pattern', vasp_interaction: 'VASP interaction' };
  const root = $('rFactors'); if (!root) return; root.replaceChildren();
  Object.entries(factors).forEach(([key, value]) => {
    const row = document.createElement('div'); row.className = 'factor-row';
    const label = document.createElement('span'); label.textContent = labels[key] || key.replaceAll('_', ' ');
    const bar = document.createElement('span'); bar.className = 'factor-bar'; const fill = document.createElement('i'); fill.style.width = `${Math.max(0, Math.min(100, Number(value) || 0))}%`; bar.append(fill);
    const pct = document.createElement('span'); pct.className = 'pct'; pct.textContent = `${Number(value) || 0}%`; row.append(label, bar, pct); root.append(row);
  });
}

function renderIndicators(indicators = []) {
  const root = $('rIndicators'); if (!root) return; root.replaceChildren();
  indicators.forEach((item) => { const row = document.createElement('div'); row.className = `indicator ${['high', 'critical'].includes(item.severity) ? 'warn' : 'ok'}`; const mark = document.createElement('span'); mark.className = 'mark'; mark.textContent = ['high', 'critical'].includes(item.severity) ? '⚠' : '✓'; const text = document.createElement('span'); text.textContent = `${item.description} (${item.code})`; row.append(mark, text); root.append(row); });
  if (!indicators.length) { const empty = document.createElement('div'); empty.className = 'indicator ok'; empty.textContent = 'No risk indicators were returned.'; root.append(empty); }
}

function renderFlow(transactions = []) {
  const root = $('rHops'); if (!root) return; root.replaceChildren();
  transactions.forEach((tx) => { const row = document.createElement('div'); row.className = 'hop'; const from = document.createElement('span'); from.className = 'addr'; from.textContent = `HOP ${tx.hop ?? '—'} · ${short(tx.from_address)}`; const arrow = document.createElement('span'); arrow.className = 'arrow'; arrow.textContent = '→'; const amount = document.createElement('span'); amount.className = 'amt'; amount.textContent = `${tx.amount} ${tx.asset} · ${short(tx.to_address)}`; row.append(from, arrow, amount); root.append(row); });
}

function renderVasp(attributions = []) {
  const item = attributions[0]; setText('rVaspName', item?.entity_name || 'No potential VASP association returned');
  const meta = $('rVaspMeta'); if (meta) meta.textContent = item ? `Match type: ${item.match_type}\nConfidence: ${(Number(item.confidence) * 100).toFixed(0)}%\nEvidence: ${(item.evidence || []).join?.(', ') || 'Backend evidence returned'}` : 'Backend returned no association.';
}

function renderResults(detail, priority, risk, transactions, related, attribution) {
  setText('rCaseId', detail.case_reference || detail.id); setText('rAmount', inr(detail.reported_amount)); setText('rFraud', `${detail.fraud_type || '—'} · ${detail.blockchain || 'ethereum'}`);
  const badge = $('rBadge'); if (badge) { badge.className = `risk-badge ${risk?.level || 'low'}`; badge.textContent = (risk?.level || 'low').toUpperCase(); }
  setText('rScore', risk?.score ?? 0); renderFactors(priority?.priority_factors || detail.priority_factors || {}); renderIndicators(risk?.indicators || []); renderFlow(transactions?.items || transactions || []); renderVasp(attribution || []); setText('rRelated', Array.isArray(related) ? related.length : (detail.related_case_count || 0));
  $('placeholderState')?.style && ($('placeholderState').style.display = 'none'); $('resultsState')?.classList.add('active');
}

async function runAnalysis(event) {
  event.preventDefault(); if (!state.user) { location.hash = '#login'; return; }
  const wallet = $('walletInput').value.trim(), chainLabel = $('chainInput').value, fraudLabel = $('fraudInput').value, amount = $('amountInput').value;
  if (chainLabel !== 'Ethereum') { showError('Only Ethereum is supported by the current backend MVP.'); return; }
  setBusy(true);
  try {
    const created = await api.createCase({ case_reference: `CHAINTRACE-${Date.now()}`, fraud_type: fraudLabel.toLowerCase().replaceAll(' ', '_'), reported_amount: amount || '0', currency: 'INR', reported_wallet_address: wallet, blockchain: 'ethereum', description: 'ChainTrace investigator demo submission.' });
    state.caseId = created.id; await api.analyze({ case_id: state.caseId, wallet_address: wallet, chain: 'ethereum' });
    const [detail, priority, risk, transactions, related, attribution] = await Promise.all([api.getCase(state.caseId), api.getPriority(state.caseId), api.getRisk(state.caseId), api.getTransactions(state.caseId), api.getRelated(state.caseId), api.getAttribution(state.caseId)]);
    state.report = null; renderResults(detail, priority, risk, transactions, related, attribution);
  } catch (error) { showError(error.message); } finally { setBusy(false); }
}

async function generateReport() {
  if (!state.caseId) return; const button = $('reportBtn'); if (button) button.disabled = true;
  try { state.report = await api.getReport(state.caseId); const doc = $('reportDoc'); if (doc) doc.textContent = JSON.stringify(state.report, null, 2); $('reportOut')?.classList.add('active'); } catch (error) { showError(error.message); } finally { if (button) button.disabled = false; }
}

function init() {
  setSession();
  $('loginForm')?.addEventListener('submit', (event) => { event.preventDefault(); const email = $('loginEmail').value.trim(), password = $('loginPassword').value; if (!email || !password) { $('loginError')?.classList.add('active'); return; } $('loginError')?.classList.remove('active'); state.user = { name: email.split('@')[0], email, role: document.querySelector('#roleToggle .active')?.dataset.role || 'Investigator' }; localStorage.setItem('chaintrace_user', JSON.stringify(state.user)); setSession(); });
  $('logoutBtn')?.addEventListener('click', () => { localStorage.removeItem('chaintrace_user'); state.user = null; setSession(); });
  document.querySelectorAll('#roleToggle button').forEach((button) => button.addEventListener('click', () => { document.querySelectorAll('#roleToggle button').forEach((item) => item.classList.remove('active')); button.classList.add('active'); }));
  document.addEventListener('submit', (event) => { if (event.target?.id === 'caseForm') { event.preventDefault(); event.stopImmediatePropagation(); runAnalysis(event); } }, true);
  document.addEventListener('click', (event) => { if (event.target?.closest?.('#reportBtn')) { event.preventDefault(); event.stopImmediatePropagation(); generateReport(); } }, true);
  const chain = $('chainInput'); if (chain) [...chain.options].forEach((option) => { const supported = option.textContent.trim() === 'Ethereum'; option.disabled = !supported; option.textContent = supported ? 'Ethereum' : `${option.textContent} · coming soon`; });
  document.documentElement.dataset.apiBase = API_BASE_URL;
}

init();
