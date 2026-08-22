const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000').replace(/\/$/, '');

const state = {
  view: localStorage.getItem('traceline_session') ? 'overview' : 'login',
  caseId: localStorage.getItem('traceline_case_id') || '',
  caseReference: localStorage.getItem('traceline_case_reference') || '',
  wallet: localStorage.getItem('traceline_wallet') || '',
  chain: 'ethereum',
  fraudType: 'investment_scam',
  description: '',
  analysis: null,
  transactions: null,
  graph: null,
  attribution: null,
  risk: null,
  cases: [],
  loading: false,
  error: '',
  toast: '',
  selectedNode: null,
  selectedEdge: null,
  mobileNav: false,
  user: JSON.parse(localStorage.getItem('traceline_user') || 'null'),
};

const app = document.querySelector('#app');

const icon = (name) => ({
  arrow: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>',
  graph: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="5" cy="12" r="2"/><circle cx="18" cy="6" r="2"/><circle cx="18" cy="18" r="2"/><path d="m7 11 9-4M7 13l9 4"/></svg>',
  shield: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 20 6v5c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6l8-3Z"/><path d="m9 12 2 2 4-5"/></svg>',
  search: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6"/><path d="m16 16 5 5"/></svg>',
  copy: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="8" y="8" width="11" height="11" rx="2"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/></svg>',
  menu: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg>',
  close: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg>',
  home: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m4 10 8-6 8 6v9H4z"/><path d="M9 19v-5h6v5"/></svg>',
  cases: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="5" width="16" height="15" rx="2"/><path d="M8 5V3h8v2M8 10h8M8 14h5"/></svg>',
  risk: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 20 6v5c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6l8-3Z"/><path d="M12 8v5M12 16h.01"/></svg>',
  user: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4 21c.8-4 3.5-6 8-6s7.2 2 8 6"/></svg>',
  logout: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 5H5v14h5M14 8l4 4-4 4M8 12h10"/></svg>',
  check: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12 4 4L19 6"/></svg>',
})[name] || '';

function esc(value) {
  return String(value ?? '').replace(/[&<>'"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[c]);
}
function short(value, left = 8, right = 6) {
  const s = String(value ?? '');
  return s.length > left + right + 3 ? `${s.slice(0, left)}…${s.slice(-right)}` : s;
}
function riskClass(level = '') { return ['low', 'medium', 'high', 'critical'].includes(level) ? level : 'unknown'; }
function pct(confidence) { return confidence == null ? null : Math.round(Math.max(0, Math.min(1, Number(confidence))) * 100); }
function toast(message) { state.toast = message; render(); setTimeout(() => { state.toast = ''; render(); }, 2400); }

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
  });
  let body = null;
  try { body = await response.json(); } catch { body = null; }
  if (!response.ok || body?.success === false) {
    throw new Error(body?.error?.message || `Request failed (${response.status})`);
  }
  return body?.data ?? body;
}

function saveCase() {
  localStorage.setItem('traceline_case_id', state.caseId);
  localStorage.setItem('traceline_case_reference', state.caseReference);
  localStorage.setItem('traceline_wallet', state.wallet);
}

function authRequired() { return Boolean(localStorage.getItem('traceline_session')); }
function shell(content) { return `<div class="site-shell">${content}${state.toast ? `<div class="toast">${icon('check')}<span>${esc(state.toast)}</span></div>` : ''}</div>`; }

function authLogo() { return `<div class="auth-brand"><span class="brand-mark"><i></i><i></i><i></i><b></b><b></b></span><div><strong>TRACELINE</strong><small>SIH 26183 / INVESTIGATOR BUILD</small></div></div>`; }

function login() {
  return shell(`<main class="auth-page"><div class="auth-glow"></div><section class="auth-card"><div class="auth-top">${authLogo()}<span class="secure-label"><i></i> SECURE WORKSPACE</span></div><div class="auth-copy"><span class="eyebrow">INVESTIGATOR ACCESS</span><h1>Welcome back.</h1><p>Sign in to continue your cryptocurrency fraud investigations.</p></div><form id="login-form" class="auth-form"><label>Email address<input type="email" name="email" autocomplete="email" placeholder="investigator@agency.org" required /></label><label>Password<div class="password-wrap"><input type="password" name="password" autocomplete="current-password" placeholder="Enter your password" required minlength="6" /><button type="button" class="password-toggle" data-toggle-password>SHOW</button></div></label><div class="form-row"><label class="check-row"><input type="checkbox" name="remember" checked /><span>Remember me</span></label><button type="button" class="text-btn" data-action="forgot">Forgot password?</button></div><button class="btn btn-accent btn-wide" type="submit">SIGN IN ${icon('arrow')}</button><div class="demo-note">Demo authentication is stored locally in this browser because the current API contract does not define authentication endpoints.</div>${state.error ? `<div class="error-box">${esc(state.error)}</div>` : ''}</form><div class="auth-switch">New to TRACELINE? <button data-action="register">Create an investigator account</button></div></section><aside class="auth-side"><span class="eyebrow">REAL-TIME CRYPTO FRAUD ATTRIBUTION</span><h2>Follow the money.<br/><em>Surface the signal.</em></h2><div class="auth-points"><div><b>01</b><span>Trace wallet flows across transaction hops.</span></div><div><b>02</b><span>Surface potential VASP associations.</span></div><div><b>03</b><span>Explain risk with investigator-ready evidence.</span></div></div><small>Attribution and risk are analytical signals, not proof of criminal ownership.</small></aside></main>`);
}

function register() {
  return shell(`<main class="auth-page"><div class="auth-glow"></div><section class="auth-card"><div class="auth-top">${authLogo()}<span class="secure-label"><i></i> INVESTIGATOR REGISTRATION</span></div><div class="auth-copy"><span class="eyebrow">CREATE ACCOUNT</span><h1>Build your workspace.</h1><p>Create a local demo investigator profile. Backend authentication is not part of the current API contract.</p></div><form id="register-form" class="auth-form"><label>Full name<input name="name" placeholder="Investigator name" required /></label><label>Organization<input name="organization" placeholder="Agency / university / team" required /></label><label>Email address<input type="email" name="email" placeholder="investigator@agency.org" required /></label><label>Password<div class="password-wrap"><input type="password" name="password" placeholder="Minimum 6 characters" minlength="6" required /><button type="button" class="password-toggle" data-toggle-password>SHOW</button></div></label><label>Password confirmation<input type="password" name="confirm" placeholder="Repeat password" minlength="6" required /></label><label class="check-row terms"><input type="checkbox" name="terms" required /><span>I understand this workspace presents analytical signals and does not establish criminal ownership.</span></label><button class="btn btn-accent btn-wide" type="submit">CREATE ACCOUNT ${icon('arrow')}</button>${state.error ? `<div class="error-box">${esc(state.error)}</div>` : ''}</form><div class="auth-switch">Already registered? <button data-action="login">Sign in</button></div></section><aside class="auth-side compact"><span class="eyebrow">INVESTIGATOR-FIRST</span><h2>A focused workspace for the SIH 26183 MVP.</h2><p>Case intake, fund-flow visualization, transaction evidence, attribution signals and risk analysis in one interface.</p><div class="mini-terminal"><span>TRACE SIGNAL</span><b>READY</b><small>ETHEREUM / FLASK REST API</small></div></aside></main>`);
}

function brandMark() { return `<span class="brand-mark"><i></i><i></i><i></i><b></b><b></b></span>`; }
function header(active = 'overview') {
  const links = [['overview','Overview', 'home'], ['intake','New Investigation', 'search'], ['dashboard','Investigation', 'graph'], ['cases','Cases', 'cases']];
  return `<header class="topbar"><button class="brand" data-action="overview">${brandMark()}<span>TRACELINE<small>SIH 26183 / INVESTIGATOR BUILD</small></span></button><nav class="nav-links">${links.map(([key,label,ico]) => `<button class="${active === key ? 'active' : ''}" data-action="${key}">${icon(ico)}${label}</button>`).join('')}</nav><div class="system-status"><span></span> SYSTEM ONLINE <b id="clock"></b></div><button class="user-chip" data-action="profile"><span>${esc((state.user?.name || 'IN').slice(0,2).toUpperCase())}</span>${esc(state.user?.name || 'Investigator')}</button><button class="icon-btn mobile-menu" data-action="menu" aria-label="Menu">${state.mobileNav ? icon('close') : icon('menu')}</button></header>`;
}

function sidebar(active) {
  return `<aside class="sidebar ${state.mobileNav ? 'open' : ''}"><div class="sidebar-section"><span>WORKSPACE</span><button class="side-link ${active === 'overview' ? 'active' : ''}" data-action="overview">${icon('home')}Overview</button><button class="side-link ${active === 'intake' ? 'active' : ''}" data-action="intake">${icon('search')}New Investigation</button><button class="side-link ${active === 'dashboard' ? 'active' : ''}" data-action="dashboard">${icon('graph')}Investigation</button><button class="side-link ${active === 'cases' ? 'active' : ''}" data-action="cases">${icon('cases')}Cases</button></div><div class="sidebar-section"><span>INTELLIGENCE</span><button class="side-link ${active === 'risk' ? 'active' : ''}" data-action="risk">${icon('risk')}Risk Analysis</button><button class="side-link ${active === 'attribution' ? 'active' : ''}" data-action="attribution">${icon('shield')}Attribution</button></div><div class="sidebar-bottom"><div class="profile-mini"><span>${esc((state.user?.name || 'IN').slice(0,2).toUpperCase())}</span><div><b>${esc(state.user?.name || 'Investigator')}</b><small>${esc(state.user?.organization || 'SIH Investigation Team')}</small></div></div><button class="side-link" data-action="logout">${icon('logout')}Sign out</button></div></aside>`;
}
function appShell(content, active = 'overview') { return shell(`${header(active)}${sidebar(active)}<main class="app-main">${content}</main>`); }

function overview() {
  const hasCase = Boolean(state.caseId);
  const risk = state.risk || state.analysis?.risk || {};
  return appShell(`<section class="page-heading"><div><span class="eyebrow">INVESTIGATOR WORKSPACE</span><h1>Good to see you, ${esc((state.user?.name || 'Investigator').split(' ')[0])}.</h1><p>Monitor active investigations and move from a reported wallet to actionable intelligence.</p></div><button class="btn btn-accent" data-action="intake">NEW INVESTIGATION ${icon('arrow')}</button></section><section class="stat-grid"><article class="stat-card"><span>ACTIVE CASE</span><strong>${hasCase ? '01' : '00'}</strong><small>${hasCase ? esc(state.caseReference) : 'No investigation opened'}</small></article><article class="stat-card"><span>TRANSACTIONS</span><strong>${state.analysis?.analysis?.transaction_count ?? '—'}</strong><small>Current investigation</small></article><article class="stat-card"><span>RISK SCORE</span><strong class="${riskClass(risk.level)}">${risk.score ?? '—'}</strong><small>${risk.level ? esc(risk.level.toUpperCase()) : 'Awaiting analysis'}</small></article><article class="stat-card"><span>VASP SIGNAL</span><strong>${state.analysis?.attribution?.confidence != null ? `${pct(state.analysis.attribution.confidence)}%` : '—'}</strong><small>Attribution confidence</small></article></section><section class="overview-grid"><article class="panel welcome-panel"><div class="panel-title"><span>INVESTIGATION PIPELINE</span><small>SIH 26183 / MVP</small></div><div class="pipeline">${[['01','REPORT','Victim-reported wallet'],['02','TRACE','Transactions + graph'],['03','ATTRIBUTE','Potential entity signal'],['04','ASSESS','Risk + evidence']].map(([n,t,d],i)=>`<div class="pipeline-step ${hasCase && i < 2 ? 'complete' : ''}"><b>${n}</b><div><strong>${t}</strong><span>${d}</span></div><i>${hasCase && i < 2 ? icon('check') : ''}</i></div>`).join('')}</div><div class="notice">${icon('shield')}<span>Potential VASP associations and risk scores are investigative analytics, not automatic proof of criminal ownership.</span></div></article><article class="panel quick-panel"><div class="panel-title"><span>QUICK ACTIONS</span></div><button class="quick-action" data-action="intake"><span>${icon('search')}</span><div><b>Analyze a wallet</b><small>Open a new case and launch analysis</small></div>${icon('arrow')}</button><button class="quick-action" data-action="dashboard"><span>${icon('graph')}</span><div><b>Open investigation</b><small>${hasCase ? esc(state.caseReference) : 'No active case yet'}</small></div>${icon('arrow')}</button><button class="quick-action" data-action="cases"><span>${icon('cases')}</span><div><b>Review cases</b><small>Manage investigation references</small></div>${icon('arrow')}</button></article></section><section class="panel feature-strip"><div><span class="eyebrow">INTELLIGENCE LAYER</span><h2>Everything the investigator needs, without the noise.</h2></div><div class="feature-pills"><span>FUND-FLOW GRAPH</span><span>TRANSACTION EVIDENCE</span><span>ATTRIBUTION SIGNALS</span><span>RISK ANALYSIS</span></div></section>`,'overview');
}

function intake() {
  return appShell(`<section class="page-heading"><div><span class="eyebrow">NEW INVESTIGATION</span><h1>Open an intelligence case.</h1><p>Create a case, provide the reported wallet and launch the backend analysis pipeline.</p></div><div class="status-pill"><span></span> READY FOR INPUT</div></section><div class="intake-layout"><form class="panel intake-form" id="intake-form"><div class="panel-title"><span>CASE INTAKE</span><small>Exact API contract fields</small></div><label>Case reference<input name="case_reference" value="${esc(state.caseReference)}" placeholder="NCRP-DEMO-001" required /></label><label>Fraud category<select name="fraud_type"><option value="investment_scam" ${state.fraudType === 'investment_scam' ? 'selected' : ''}>Investment scam</option><option value="other">Other</option></select></label><label>Description<textarea name="description" rows="4" placeholder="Briefly describe the reported incident.">${esc(state.description)}</textarea></label><div class="form-divider"></div><label>Suspect wallet address<input name="wallet_address" value="${esc(state.wallet)}" placeholder="0x..." required spellcheck="false" /></label><label>Blockchain<select name="chain"><option value="ethereum">Ethereum</option></select></label><button class="btn btn-accent btn-wide" type="submit">${state.loading ? 'ANALYZING WALLET…' : 'ANALYZE WALLET'} ${icon('arrow')}</button>${state.error ? `<div class="error-box">${esc(state.error)}</div>` : ''}</form><aside class="panel process-panel"><span class="eyebrow">WHAT HAPPENS NEXT</span><div class="process-list">${['Wallet validation','Blockchain transaction retrieval','Transaction graph analysis','Attribution signal retrieval','Risk analysis'].map((x,i)=>`<div><b>0${i+1}</b><span>${x}</span><i></i></div>`).join('')}</div><div class="notice">${icon('shield')}<span>Backend responses are rendered from the API contract. No frontend graph or risk data is invented.</span></div></aside></div>`,'intake');
}

function dashboard() {
  if (!state.caseId || !state.analysis) return appShell(`<section class="empty-workspace"><div class="empty-icon">${icon('graph')}</div><span class="eyebrow">INVESTIGATION WORKSPACE</span><h1>No active investigation.</h1><p>Create or analyze a case first. This screen is always accessible now; it will populate automatically after a successful analysis.</p><button class="btn btn-accent" data-action="intake">START INVESTIGATION ${icon('arrow')}</button></section>`,'dashboard');
  const a = state.analysis;
  const risk = state.risk || a.risk || {};
  const attrs = Array.isArray(state.attribution) ? state.attribution : (a.attribution ? [a.attribution] : []);
  const attr = attrs[0] || {};
  return appShell(`<section class="investigation-head"><div><span class="eyebrow">ACTIVE INVESTIGATION</span><h1>${esc(state.caseReference || state.caseId)}</h1><div class="head-meta"><span>CASE ${esc(state.caseId)}</span><span>${esc(a.wallet?.chain || 'ethereum').toUpperCase()}</span><span>${short(a.wallet?.address || state.wallet, 14, 8)}</span></div></div><div class="head-actions"><button class="mini-btn" data-copy="${esc(a.wallet?.address || state.wallet)}">${icon('copy')} COPY WALLET</button><button class="btn btn-accent" data-action="report">VIEW REPORT ${icon('arrow')}</button></div></section><section class="metrics-grid"><div class="metric"><span>TRANSACTIONS</span><strong>${a.analysis?.transaction_count ?? '—'}</strong><small>Analyzed transaction count</small></div><div class="metric"><span>TOTAL TRANSFERRED</span><strong>${esc(a.analysis?.total_transferred_value ?? '—')}</strong><small>Exact API string value</small></div><div class="metric"><span>HOPS</span><strong>${a.analysis?.hop_count ?? '—'}</strong><small>Fund-flow depth</small></div><div class="metric risk-metric ${riskClass(risk.level)}"><span>RISK</span><strong>${risk.score ?? '—'}</strong><small>${esc(risk.level || 'awaiting analysis')}</small></div></section><section class="dashboard-grid"><article class="panel graph-panel"><div class="panel-title"><span>TRANSACTION GRAPH</span><small>${state.graph?.nodes?.length ?? 0} nodes / ${state.graph?.edges?.length ?? 0} edges</small></div><div class="graph-wrap">${renderGraph()}</div><div class="legend"><span><i class="reported"></i>Reported wallet</span><span><i class="intermediary"></i>Intermediary</span><span><i class="entity"></i>VASP / exchange</span><span><i class="unknown"></i>Unknown</span></div></article><aside class="panel intelligence-panel"><div class="panel-title"><span>ATTRIBUTION</span><small>ANALYTICAL SIGNAL</small></div><div class="entity-card"><div class="entity-icon">${icon('shield')}</div><div><span>POTENTIAL ASSOCIATION</span><h2>${esc(attr.entity_name || 'No entity returned')}</h2><p>${esc(attr.entity_type || 'unknown')} · ${esc(attr.match_type || 'unknown')}</p></div></div><div class="confidence"><div><span>CONFIDENCE</span><b>${attr.confidence != null ? `${pct(attr.confidence)}%` : '—'}</b></div><div class="confidence-bar"><i style="width:${attr.confidence != null ? pct(attr.confidence) : 0}%"></i></div></div><div class="panel-title sub-title"><span>RISK INDICATORS</span><small>${state.risk?.indicators?.length ?? 0} RETURNED</small></div>${renderIndicators()}</aside></section><section class="panel timeline-panel"><div class="panel-title"><span>TRANSACTION TIMELINE</span><button class="mini-btn" data-action="transactions">${state.loading ? 'LOADING…' : 'LOAD TRANSACTIONS'} ${icon('arrow')}</button></div>${renderTransactions()}</section>`,'dashboard');
}

function renderGraph() {
  const nodes = state.graph?.nodes || [];
  const edges = state.graph?.edges || [];
  if (!nodes.length) return `<div class="graph-empty">${state.loading ? 'Loading transaction graph…' : 'No transaction graph available.'}</div>`;
  const w = 900, h = 390, cx = w / 2, cy = h / 2;
  const pos = nodes.map((n, i) => { if (i === 0) return [100, cy]; if (i === nodes.length - 1) return [800, cy]; const r = 145; const a = ((i - 1) / Math.max(1, nodes.length - 2)) * Math.PI * 2; return [cx + Math.cos(a) * r, cy + Math.sin(a) * r * .62]; });
  const lookup = new Map(nodes.map((n, i) => [n.id, pos[i]]));
  const lines = edges.map(e => { const s = lookup.get(e.source), t = lookup.get(e.target); return s && t ? `<line x1="${s[0]}" y1="${s[1]}" x2="${t[0]}" y2="${t[1]}" class="edge-line" data-edge="${esc(e.id)}"/>` : ''; }).join('');
  const circles = nodes.map((n, i) => { const [x, y] = pos[i]; const type = ['reported_wallet','intermediary','exchange','vasp','unknown'].includes(n.type) ? n.type : 'unknown'; return `<g class="graph-node ${esc(type)}" data-node="${esc(n.id)}" transform="translate(${x},${y})"><circle r="${type === 'reported_wallet' ? 23 : 17}"/><circle r="${type === 'reported_wallet' ? 8 : 5}" class="node-core"/><text y="39">${esc(n.label || short(n.address, 8, 5))}</text></g>`; }).join('');
  return `<svg class="flow-svg" viewBox="0 0 ${w} ${h}" role="img" aria-label="Backend transaction graph">${lines}${circles}</svg>${state.selectedNode ? `<div class="selection-card"><b>${esc(state.selectedNode.label || state.selectedNode.type)}</b><span>${esc(state.selectedNode.address || state.selectedNode.id)}</span></div>` : ''}`;
}

function renderIndicators() {
  const indicators = state.risk?.indicators || [];
  if (!indicators.length) return '<div class="empty-inline">No risk indicators available.</div>';
  return `<div class="indicator-list">${indicators.map(i => `<div class="indicator ${riskClass(i.severity)}"><div><b>${esc(i.code)}</b><span>${esc(i.description)}</span></div><strong>${esc(i.severity)}</strong></div>`).join('')}</div>`;
}

function renderTransactions() {
  const txs = Array.isArray(state.transactions) ? state.transactions : state.transactions?.transactions || [];
  if (!txs.length) return `<div class="empty-inline">${state.loading ? 'Loading transaction data…' : 'No transaction data available.'}</div>`;
  return `<div class="table-wrap"><table><thead><tr><th>TIME</th><th>HASH</th><th>FLOW</th><th>AMOUNT</th><th>ASSET</th><th>HOP</th><th>STATUS</th></tr></thead><tbody>${txs.map(t => `<tr><td>${esc(t.timestamp ? new Date(t.timestamp).toLocaleString() : '—')}</td><td><button class="hash-btn" data-copy="${esc(t.transaction_hash)}">${esc(short(t.transaction_hash, 10, 8))}</button></td><td><span class="flow-cell">${esc(short(t.from_address, 7, 5))} <i>→</i> ${esc(short(t.to_address, 7, 5))}</span></td><td>${esc(t.amount)}</td><td>${esc(t.asset)}</td><td>${esc(t.hop)}</td><td><span class="status ${esc(t.status)}">${esc(t.status)}</span></td></tr>`).join('')}</tbody></table></div>`;
}

function cases() {
  const rows = state.cases.length ? state.cases : (state.caseId ? [{ id: state.caseId, case_reference: state.caseReference, fraud_type: state.fraudType, status: state.analysis?.analysis?.status || 'active' }] : []);
  return appShell(`<section class="page-heading"><div><span class="eyebrow">CASE MANAGEMENT</span><h1>Investigation cases.</h1><p>Review case references and open the current investigator workspace.</p></div><button class="btn btn-accent" data-action="intake">NEW CASE ${icon('arrow')}</button></section><section class="panel cases-panel"><div class="panel-title"><span>CASE REGISTER</span><small>${rows.length} visible</small></div>${rows.length ? `<div class="table-wrap"><table><thead><tr><th>CASE REFERENCE</th><th>CASE ID</th><th>FRAUD TYPE</th><th>STATUS</th><th></th></tr></thead><tbody>${rows.map(c => `<tr><td><b>${esc(c.case_reference || '—')}</b></td><td>${esc(short(c.id, 10, 6))}</td><td>${esc(c.fraud_type || '—')}</td><td><span class="status confirmed">${esc(c.status || 'active')}</span></td><td><button class="mini-btn" data-open-case="${esc(c.id)}">OPEN ${icon('arrow')}</button></td></tr>`).join('')}</tbody></table></div>` : `<div class="empty-state">${icon('cases')}<h2>No cases yet.</h2><p>Create your first investigation to populate the case register.</p><button class="btn btn-accent" data-action="intake">CREATE FIRST CASE</button></div>`}</section>`,'cases');
}

function riskPage() {
  const risk = state.risk || state.analysis?.risk;
  return appShell(`<section class="page-heading"><div><span class="eyebrow">RISK ANALYSIS</span><h1>Explain the risk signal.</h1><p>Scores and indicators returned by the backend are presented without changing their datatype or meaning.</p></div></section><section class="risk-overview"><article class="risk-score-card ${riskClass(risk?.level)}"><span>RISK SCORE</span><strong>${risk?.score ?? '—'}</strong><small>${esc(risk?.level || 'No active analysis')}</small></article><article class="panel risk-detail"><div class="panel-title"><span>INDICATORS</span><small>${risk?.indicators?.length || 0} RETURNED</small></div>${renderIndicators()}</article></section>`,'risk');
}

function attributionPage() {
  const attrs = Array.isArray(state.attribution) ? state.attribution : (state.analysis?.attribution ? [state.analysis.attribution] : []);
  return appShell(`<section class="page-heading"><div><span class="eyebrow">ATTRIBUTION</span><h1>Potential entity associations.</h1><p>Investigative signals are shown with confidence and evidence context. They are not declarations of criminal ownership.</p></div></section><section class="attribution-grid">${attrs.length ? attrs.map(a => `<article class="panel attribution-card"><div class="entity-icon">${icon('shield')}</div><span>POTENTIAL VASP ASSOCIATION</span><h2>${esc(a.entity_name || 'Unknown entity')}</h2><p>${esc(a.entity_type || 'unknown')} · ${esc(a.match_type || 'unknown')}</p><div class="confidence"><div><span>CONFIDENCE</span><b>${a.confidence != null ? `${pct(a.confidence)}%` : '—'}</b></div><div class="confidence-bar"><i style="width:${a.confidence != null ? pct(a.confidence) : 0}%"></i></div></div><div class="evidence-box"><span>EVIDENCE</span><p>${esc(a.evidence || 'No evidence detail returned by the API.')}</p></div></article>`).join('') : `<div class="empty-state">${icon('shield')}<h2>No attribution signal available.</h2><p>Run a wallet analysis to retrieve backend attribution data.</p></div>`}</section>`,'attribution');
}

function reportPage() {
  return appShell(`<section class="page-heading"><div><span class="eyebrow">INVESTIGATION REPORT</span><h1>${esc(state.caseReference || 'Current case')}</h1><p>Investigator-ready summary from the report endpoint.</p></div><button class="btn btn-ghost" data-action="dashboard">BACK TO INVESTIGATION</button></section><section class="panel report-card"><div class="report-banner"><div>${brandMark()}<div><b>TRACELINE</b><span>SIH 26183 INVESTIGATION REPORT</span></div></div><span>${new Date().toLocaleDateString()}</span></div><div class="report-grid"><div><span>CASE ID</span><b>${esc(state.caseId)}</b></div><div><span>CASE REFERENCE</span><b>${esc(state.caseReference)}</b></div><div><span>WALLET</span><b>${esc(state.wallet)}</b></div><div><span>CHAIN</span><b>ETHEREUM</b></div></div><div class="notice">${icon('shield')}<span>Attribution and risk are investigative analytics. This report must not be treated as automatic proof of criminal ownership.</span></div></section>`,'dashboard');
}

function render() {
  if (!authRequired()) { app.innerHTML = state.view === 'register' ? register() : login(); bind(); return; }
  if (['login','register'].includes(state.view)) state.view = 'overview';
  const views = { overview, intake, dashboard, cases, risk: riskPage, attribution: attributionPage, report: reportPage };
  app.innerHTML = (views[state.view] || overview)();
  bind(); updateClock();
}

function setView(view) { state.view = view; state.error = ''; state.mobileNav = false; render(); window.scrollTo({ top: 0, behavior: 'smooth' }); }

async function createAndAnalyze(form) {
  state.loading = true; state.error = ''; render();
  try {
    const data = new FormData(form);
    state.caseReference = String(data.get('case_reference') || '').trim();
    state.fraudType = String(data.get('fraud_type') || '');
    state.description = String(data.get('description') || '').trim();
    state.wallet = String(data.get('wallet_address') || '').trim();
    state.chain = String(data.get('chain') || 'ethereum');
    if (!/^0x[a-fA-F0-9]{40}$/.test(state.wallet)) throw new Error('Enter a valid 42-character Ethereum wallet address.');
    const created = await api('/api/cases', { method: 'POST', body: JSON.stringify({ case_reference: state.caseReference, fraud_type: state.fraudType, description: state.description }) });
    state.caseId = created.id;
    saveCase();
    const analysis = await api('/api/investigations/analyze', { method: 'POST', body: JSON.stringify({ case_id: state.caseId, wallet_address: state.wallet, chain: state.chain }) });
    state.analysis = analysis;
    state.risk = analysis.risk || null;
    state.attribution = analysis.attribution ? [analysis.attribution] : [];
    await loadInvestigationData(false);
    state.loading = false;
    state.view = 'dashboard';
    toast('Investigation analyzed successfully');
  } catch (error) {
    state.loading = false; state.error = error.message || 'Unable to complete the investigation.'; render();
  }
}

async function loadInvestigationData(showLoading = true) {
  if (!state.caseId) return;
  if (showLoading) { state.loading = true; render(); }
  try {
    const [graph, attribution, risk] = await Promise.all([
      api(`/api/cases/${encodeURIComponent(state.caseId)}/graph`),
      api(`/api/cases/${encodeURIComponent(state.caseId)}/attribution`),
      api(`/api/cases/${encodeURIComponent(state.caseId)}/risk`),
    ]);
    state.graph = graph;
    state.attribution = Array.isArray(attribution) ? attribution : (attribution?.attributions || []);
    state.risk = risk;
  } catch (error) {
    state.error = error.message || 'Some investigation data could not be loaded.';
  } finally { state.loading = false; }
}

async function loadTransactions() {
  if (!state.caseId) return;
  state.loading = true; render();
  try { state.transactions = await api(`/api/cases/${encodeURIComponent(state.caseId)}/transactions?page=1&limit=50`); }
  catch (error) { state.error = error.message || 'Transaction data could not be loaded.'; }
  finally { state.loading = false; render(); }
}

async function loadReport() {
  if (!state.caseId) return;
  state.loading = true; render();
  try { await api(`/api/cases/${encodeURIComponent(state.caseId)}/report`); state.view = 'report'; }
  catch (error) { state.error = error.message || 'Report data could not be loaded.'; }
  finally { state.loading = false; render(); }
}

function bind() {
  document.querySelectorAll('[data-action]').forEach((el) => el.addEventListener('click', async () => {
    const action = el.dataset.action;
    if (action === 'login') return setView('login');
    if (action === 'register') return setView('register');
    if (action === 'overview' || action === 'home') return setView('overview');
    if (action === 'intake') return setView('intake');
    if (action === 'dashboard') return setView('dashboard');
    if (action === 'cases') return setView('cases');
    if (action === 'risk') return setView('risk');
    if (action === 'attribution') return setView('attribution');
    if (action === 'report') return loadReport();
    if (action === 'transactions') return loadTransactions();
    if (action === 'menu') { state.mobileNav = !state.mobileNav; return render(); }
    if (action === 'profile') return toast(`${state.user?.name || 'Investigator'} · ${state.user?.organization || 'Workspace'}`);
    if (action === 'logout') { localStorage.removeItem('traceline_session'); state.user = null; state.view = 'login'; return render(); }
    if (action === 'forgot') return toast('Demo mode: password reset is not connected to an authentication API yet.');
  }));

  const intakeForm = document.querySelector('#intake-form');
  if (intakeForm) intakeForm.addEventListener('submit', (e) => { e.preventDefault(); createAndAnalyze(intakeForm); });
  const loginForm = document.querySelector('#login-form');
  if (loginForm) loginForm.addEventListener('submit', (e) => { e.preventDefault(); const fd = new FormData(loginForm); state.user = JSON.parse(localStorage.getItem('traceline_user') || 'null') || { name: String(fd.get('email')).split('@')[0], organization: 'Investigation Team', email: fd.get('email') }; localStorage.setItem('traceline_user', JSON.stringify(state.user)); localStorage.setItem('traceline_session', 'local-demo'); state.view = 'overview'; state.error = ''; render(); });
  const registerForm = document.querySelector('#register-form');
  if (registerForm) registerForm.addEventListener('submit', (e) => { e.preventDefault(); const fd = new FormData(registerForm); if (fd.get('password') !== fd.get('confirm')) { state.error = 'Passwords do not match.'; return render(); } state.user = { name: fd.get('name'), organization: fd.get('organization'), email: fd.get('email') }; localStorage.setItem('traceline_user', JSON.stringify(state.user)); localStorage.setItem('traceline_session', 'local-demo'); state.view = 'overview'; state.error = ''; render(); });
  document.querySelectorAll('[data-toggle-password]').forEach(btn => btn.addEventListener('click', () => { const input = btn.parentElement.querySelector('input'); input.type = input.type === 'password' ? 'text' : 'password'; btn.textContent = input.type === 'password' ? 'SHOW' : 'HIDE'; }));
  document.querySelectorAll('[data-copy]').forEach(btn => btn.addEventListener('click', async () => { try { await navigator.clipboard.writeText(btn.dataset.copy); toast('Copied to clipboard'); } catch { toast('Copy unavailable in this browser'); } }));
  document.querySelectorAll('[data-node]').forEach(node => node.addEventListener('click', () => { const item = (state.graph?.nodes || []).find(n => String(n.id) === node.dataset.node); state.selectedNode = item || null; render(); }));
  document.querySelectorAll('[data-open-case]').forEach(btn => btn.addEventListener('click', async () => { state.caseId = btn.dataset.openCase; saveCase(); try { state.analysis = await api(`/api/cases/${encodeURIComponent(state.caseId)}`); state.caseReference = state.analysis.case_reference || state.caseReference; await loadInvestigationData(false); setView('dashboard'); } catch (e) { state.error = e.message; render(); } }));
}

function updateClock() { const el = document.querySelector('#clock'); if (el) el.textContent = new Date().toISOString().slice(11, 19) + ' UTC'; }
setInterval(updateClock, 1000);
render();
