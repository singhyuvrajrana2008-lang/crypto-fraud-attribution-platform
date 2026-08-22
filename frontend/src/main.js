const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000').replace(/\/$/, '');

const state = {
  view: 'landing',
  caseId: '',
  caseReference: '',
  wallet: '',
  chain: 'ethereum',
  fraudType: 'investment_scam',
  description: '',
  analysis: null,
  transactions: null,
  graph: null,
  attribution: null,
  risk: null,
  loading: false,
  error: '',
  selectedNode: null,
  selectedEdge: null,
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
})[name] || '';

function esc(value) {
  return String(value ?? '').replace(/[&<>'"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[c]);
}

function short(value, left = 8, right = 6) {
  const s = String(value ?? '');
  return s.length > left + right + 3 ? `${s.slice(0, left)}…${s.slice(-right)}` : s;
}

function riskClass(level = '') { return ['low', 'medium', 'high', 'critical'].includes(level) ? level : 'unknown'; }

function shell(content) {
  return `<div class="site-shell">${content}</div>`;
}

function header(active = 'home') {
  return `<header class="topbar">
    <button class="brand" data-action="home"><span class="brand-mark"><i></i><i></i><i></i><b></b><b></b></span><span>TRACELINE<small>SIH 26183 / INVESTIGATOR BUILD</small></span></button>
    <nav class="nav-links">
      <button class="${active === 'home' ? 'active' : ''}" data-action="home">Overview</button>
      <button class="${active === 'intake' ? 'active' : ''}" data-action="intake">New Investigation</button>
      <button class="${active === 'dashboard' ? 'active' : ''}" data-action="dashboard" ${!state.caseId ? 'disabled' : ''}>Investigation</button>
    </nav>
    <div class="system-status"><span></span> SYSTEM ONLINE <b id="clock"></b></div>
    <button class="icon-btn mobile-menu" data-action="menu" aria-label="Menu">${icon('menu')}</button>
  </header>`;
}

function landing() {
  return shell(`${header('home')}
    <main class="landing">
      <section class="hero">
        <div class="hero-grid"></div><div class="hero-orb orb-a"></div><div class="hero-orb orb-b"></div>
        <div class="hero-copy">
          <div class="eyebrow">REAL-TIME CRYPTO FRAUD ATTRIBUTION</div>
          <h1>Trace the wallet.<br/>Name the <em>entity.</em><br/>Expose the trail.</h1>
          <p>TRACELINE turns a victim-reported cryptocurrency wallet into an investigator-ready picture of fund flows, attribution signals and risk — through one focused workspace.</p>
          <div class="hero-actions"><button class="btn btn-accent" data-action="intake">Start an investigation ${icon('arrow')}</button><button class="btn btn-ghost" data-action="dashboard">View workspace</button></div>
          <div class="hero-meta"><span><i></i> ETHEREUM MVP</span><span>FLASK REST API</span><span>INVESTIGATOR-FIRST</span></div>
        </div>
        <div class="hero-visual"><div class="radar"><span></span><span></span><span></span><span></span><div class="radar-core">${icon('graph')}</div></div><div class="signal-card"><span>TRACE SIGNAL</span><strong>LIVE</strong><small>Awaiting investigation input</small></div></div>
      </section>
      <section class="landing-section workflow"><div class="section-head"><span class="eyebrow">INVESTIGATION PIPELINE</span><h2>From reported wallet to actionable intelligence.</h2></div>
        <div class="steps">${[['01','REPORT','Victim-reported wallet enters the investigation.'],['02','TRACE','Transactions are normalized into a fund-flow graph.'],['03','ATTRIBUTE','Potential VASP/entity associations are surfaced with confidence.'],['04','ASSESS','Risk indicators explain why a wallet deserves attention.']].map(([n,t,d]) => `<article><span>${n}</span><h3>${t}</h3><p>${d}</p></article>`).join('')}</div>
      </section>
      <section class="landing-section intelligence"><div class="section-head"><span class="eyebrow">INTELLIGENCE LAYER</span><h2>A serious interface for a serious investigation.</h2></div><div class="feature-grid">${[['TRANSACTION GRAPH','Follow the path across reported, intermediary and entity-associated wallets.'],['VASP ATTRIBUTION','Surface potential associations without presenting analytical evidence as proof.'],['RISK ANALYSIS','Make score, severity and evidence visible at the exact moment they matter.'],['EVIDENCE TIMELINE','Inspect transaction hash, direction, amount, asset, hop and status in context.']].map(([t,d],i) => `<article class="feature-card"><span>0${i+1}</span><h3>${t}</h3><p>${d}</p></article>`).join('')}</div></section>
    </main>`);
}

function intake() {
  return shell(`${header('intake')}<main class="workspace intake-page"><div class="page-intro"><div><span class="eyebrow">NEW INVESTIGATION</span><h1>Open an intelligence case.</h1><p>Create a case, provide the reported wallet and launch the backend analysis pipeline.</p></div><div class="status-pill"><span></span> READY FOR INPUT</div></div>
    <div class="intake-layout"><form class="panel intake-form" id="intake-form"><div class="panel-title"><span>CASE INTAKE</span><small>Required fields are validated by the API.</small></div>
      <label>Case reference<input name="case_reference" value="${esc(state.caseReference)}" placeholder="NCRP-DEMO-001" required /></label>
      <label>Fraud category<select name="fraud_type"><option value="investment_scam" ${state.fraudType === 'investment_scam' ? 'selected' : ''}>Investment scam</option><option value="other">Other</option></select></label>
      <label>Description<textarea name="description" rows="4" placeholder="Briefly describe the reported incident.">${esc(state.description)}</textarea></label>
      <div class="form-divider"></div>
      <label>Suspect wallet address<input name="wallet_address" value="${esc(state.wallet)}" placeholder="0x..." required spellcheck="false" /></label>
      <label>Blockchain<select name="chain"><option value="ethereum">Ethereum</option></select></label>
      <button class="btn btn-accent btn-wide" type="submit">${state.loading ? 'ANALYZING WALLET…' : 'ANALYZE WALLET'} ${icon('arrow')}</button>
      ${state.error ? `<div class="error-box">${esc(state.error)}</div>` : ''}
    </form>
    <aside class="panel intake-side"><span class="eyebrow">WHAT HAPPENS NEXT</span><div class="process-list">${['Wallet validation','Blockchain transaction retrieval','Transaction graph analysis','Attribution signal retrieval','Risk analysis'].map((x,i)=>`<div><b>0${i+1}</b><span>${x}</span><i></i></div>`).join('')}</div><div class="notice">${icon('shield')} <span>Attribution and risk are investigative analytics. They are not automatic proof of criminal ownership.</span></div></aside></div></main>`);
}

function metric(label, value, sub = '') { return `<div class="metric"><span>${label}</span><strong>${esc(value)}</strong>${sub ? `<small>${esc(sub)}</small>` : ''}</div>`; }

function dashboard() {
  if (!state.caseId || !state.analysis) return intake();
  const a = state.analysis;
  const risk = a.risk || state.risk || {};
  const attr = a.attribution || state.attribution?.[0] || {};
  const wallet = a.wallet || {};
  const level = riskClass(risk.level);
  return shell(`${header('dashboard')}<main class="workspace dashboard-page">
    <div class="investigation-bar"><div><span class="eyebrow">ACTIVE INVESTIGATION</span><h1>${esc(state.caseReference || state.caseId)}</h1></div><div class="wallet-chip"><span>REPORTED WALLET</span><b>${short(wallet.address || state.wallet, 12, 8)}</b><button data-copy="${esc(wallet.address || state.wallet)}">${icon('copy')}</button></div><div class="risk-badge ${level}"><span>RISK</span><strong>${esc(risk.score ?? '—')}</strong><small>${esc(risk.level || 'unknown')}</small></div></div>
    <section class="metrics-grid">${metric('TRANSACTIONS', a.analysis?.transaction_count ?? '—')} ${metric('TOTAL TRANSFERRED', a.analysis?.total_transferred_value ?? '—','ETH / exact API value')} ${metric('HOPS', a.analysis?.hop_count ?? '—')} ${metric('ATTRIBUTION CONFIDENCE', attr.confidence != null ? attr.confidence.toFixed(2) : '—','0–1')}</section>
    <section class="dashboard-grid">
      <article class="panel graph-panel"><div class="panel-title"><span>FUND-FLOW GRAPH</span><small>${state.graph?.nodes?.length ?? '—'} nodes / ${state.graph?.edges?.length ?? '—'} edges</small></div><div class="graph-wrap">${renderGraph()}</div><div class="legend"><span><i class="reported"></i>Reported</span><span><i class="intermediary"></i>Intermediary</span><span><i class="entity"></i>Entity / VASP</span><span><i class="unknown"></i>Unknown</span></div></article>
      <aside class="panel intelligence-panel"><div class="panel-title"><span>ATTRIBUTION</span><small>ANALYTICAL SIGNAL</small></div><div class="entity-card"><div class="entity-icon">${icon('shield')}</div><div><span>POTENTIAL ASSOCIATION</span><h2>${esc(attr.entity_name || 'No entity returned')}</h2><p>${esc(attr.entity_type || 'unknown')} · ${esc(attr.match_type || 'analysis')}</p></div></div><div class="confidence"><div><span>CONFIDENCE</span><b>${attr.confidence != null ? Math.round(attr.confidence * 100) + '%' : '—'}</b></div><div class="confidence-bar"><i style="width:${attr.confidence != null ? Math.max(0, Math.min(100, attr.confidence * 100)) : 0}%"></i></div></div><div class="panel-title risk-title"><span>RISK INDICATORS</span><small>${state.risk?.indicators?.length ?? 0} RETURNED</small></div>${renderIndicators()}</aside>
    </section>
    <section class="panel timeline-panel"><div class="panel-title"><span>TRANSACTION TIMELINE</span><button class="mini-btn" data-action="transactions">${state.transactions ? 'REFRESH' : 'LOAD TRANSACTIONS'} ${icon('arrow')}</button></div>${renderTransactions()}</section>
  </main>`);
}

function renderGraph() {
  const nodes = state.graph?.nodes || [];
  const edges = state.graph?.edges || [];
  if (!nodes.length) return `<div class="graph-empty">${state.loading ? 'Loading transaction graph…' : 'No transaction graph available.'}</div>`;
  const w = 900, h = 390, cx = w/2, cy = h/2;
  const pos = nodes.map((n,i)=>{ if(i===0)return [110,cy]; if(i===nodes.length-1)return [790,cy]; const ring=140; const ang=((i-1)/Math.max(1,nodes.length-2))*Math.PI*2; return [cx+Math.cos(ang)*ring,cy+Math.sin(ang)*ring*.62]; });
  const lookup = new Map(nodes.map((n,i)=>[n.id,pos[i]]));
  const lines = edges.map(e=>{const s=lookup.get(e.source),t=lookup.get(e.target); return s&&t?`<line x1="${s[0]}" y1="${s[1]}" x2="${t[0]}" y2="${t[1]}" class="edge-line" data-edge="${esc(e.id)}"/>`:''}).join('');
  const circles = nodes.map((n,i)=>{const [x,y]=pos[i]; return `<g class="graph-node ${esc(n.type)}" data-node="${esc(n.id)}" transform="translate(${x},${y})"><circle r="${n.type==='reported_wallet'?22:16}"/><circle r="${n.type==='reported_wallet'?8:5}" class="node-core"/><text y="38">${esc(n.label || short(n.address,7,5))}</text></g>`}).join('');
  return `<svg class="flow-svg" viewBox="0 0 ${w} ${h}" role="img" aria-label="Backend transaction graph"><defs><filter id="glow"><feGaussianBlur stdDeviation="4" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>${lines}${circles}</svg>${state.selectedNode ? `<div class="selection-card"><b>${esc(state.selectedNode.label || state.selectedNode.type)}</b><span>${esc(state.selectedNode.address || state.selectedNode.id)}</span></div>` : ''}`;
}

function renderIndicators() {
  const indicators = state.risk?.indicators || [];
  if (!indicators.length) return '<div class="empty-inline">No risk indicators available.</div>';
  return `<div class="indicator-list">${indicators.map(i=>`<div class="indicator ${riskClass(i.severity)}"><div><b>${esc(i.code)}</b><span>${esc(i.description)}</span></div><strong>${esc(i.severity)}</strong></div>`).join('')}</div>`;
}

function renderTransactions() {
  const txs = Array.isArray(state.transactions) ? state.transactions : state.transactions?.transactions || [];
  if (!txs.length) return `<div class="empty-inline">${state.loading ? 'Loading transaction data…' : 'No transaction data available.'}</div>`;
  return `<div class="table-wrap"><table><thead><tr><th>TIME</th><th>HASH</th><th>FLOW</th><th>AMOUNT</th><th>ASSET</th><th>HOP</th><th>STATUS</th></tr></thead><tbody>${txs.map(t=>`<tr><td>${esc(new Date(t.timestamp).toLocaleString())}</td><td><button class="hash" data-copy="${esc(t.transaction_hash)}">${short(t.transaction_hash,10,7)}</button></td><td><span class="flow-address">${short(t.from_address,7,5)}</span><b> → </b><span class="flow-address">${short(t.to_address,7,5)}</span></td><td>${esc(t.amount)}</td><td>${esc(t.asset)}</td><td>${esc(t.hop ?? '—')}</td><td><span class="tx-status ${esc(t.status)}">${esc(t.status)}</span></td></tr>`).join('')}</tbody></table></div>`;
}

function render() {
  const page = state.view === 'landing' ? landing() : state.view === 'intake' ? intake() : dashboard();
  app.innerHTML = page;
  updateClock();
  bindEvents();
}

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, { headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }, ...options });
  let body = null;
  try { body = await response.json(); } catch { throw new Error(`Backend returned a non-JSON response (${response.status}).`); }
  if (!response.ok || body.success === false) throw new Error(body.error?.message || `Request failed (${response.status}).`);
  return body.data;
}

async function createCaseAndAnalyze(form) {
  state.loading = true; state.error = ''; render();
  try {
    state.caseReference = form.case_reference.value.trim(); state.fraudType = form.fraud_type.value; state.description = form.description.value.trim(); state.wallet = form.wallet_address.value.trim(); state.chain = form.chain.value;
    const created = await api('/api/cases', { method: 'POST', body: JSON.stringify({ case_reference: state.caseReference, fraud_type: state.fraudType, description: state.description }) });
    state.caseId = created.id;
    state.analysis = await api('/api/investigations/analyze', { method: 'POST', body: JSON.stringify({ case_id: state.caseId, wallet_address: state.wallet, chain: state.chain }) });
    await loadInvestigationData(); state.view = 'dashboard';
  } catch (e) { state.error = e.message; }
  finally { state.loading = false; render(); }
}

async function loadInvestigationData() {
  const results = await Promise.allSettled([
    api(`/api/cases/${state.caseId}/transactions?page=1&limit=50`),
    api(`/api/cases/${state.caseId}/graph`),
    api(`/api/cases/${state.caseId}/attribution`),
    api(`/api/cases/${state.caseId}/risk`),
  ]);
  state.transactions = results[0].status === 'fulfilled' ? results[0].value : null;
  state.graph = results[1].status === 'fulfilled' ? results[1].value : null;
  state.attribution = results[2].status === 'fulfilled' ? results[2].value : null;
  state.risk = results[3].status === 'fulfilled' ? results[3].value : null;
  if (state.risk && state.analysis) state.analysis.risk = state.risk;
  if (state.attribution && state.analysis) state.analysis.attribution = Array.isArray(state.attribution) ? state.attribution[0] : state.attribution;
}

async function loadTransactions() {
  if (!state.caseId) return;
  state.loading = true; render();
  try { state.transactions = await api(`/api/cases/${state.caseId}/transactions?page=1&limit=50`); } catch (e) { state.error = e.message; } finally { state.loading = false; render(); }
}

function bindEvents() {
  document.querySelectorAll('[data-action]').forEach(el => el.addEventListener('click', () => {
    const action = el.dataset.action;
    if (action === 'home') { state.view = 'landing'; render(); }
    if (action === 'intake') { state.view = 'intake'; state.error = ''; render(); }
    if (action === 'dashboard') { if (state.caseId) { state.view = 'dashboard'; render(); } else { state.view = 'intake'; render(); } }
    if (action === 'transactions') loadTransactions();
    if (action === 'menu') document.querySelector('.nav-links')?.classList.toggle('open');
  }));
  document.querySelector('#intake-form')?.addEventListener('submit', (e) => { e.preventDefault(); createCaseAndAnalyze(e.currentTarget); });
  document.querySelectorAll('[data-copy]').forEach(el => el.addEventListener('click', async (e) => { e.stopPropagation(); try { await navigator.clipboard.writeText(el.dataset.copy); el.classList.add('copied'); setTimeout(()=>el.classList.remove('copied'),900); } catch {} }));
  document.querySelectorAll('[data-node]').forEach(el => el.addEventListener('click', () => { const id = el.dataset.node; state.selectedNode = state.graph?.nodes?.find(n=>n.id===id) || null; render(); }));
}

function updateClock() { const el = document.querySelector('#clock'); if (el) el.textContent = new Date().toUTCString().slice(17,25) + ' UTC'; }
setInterval(updateClock, 1000);
render();
