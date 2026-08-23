# ChainTrace Frontend Integration

The Vite frontend serves the supplied ChainTrace experience as the root page. `frontend/chaintrace.html` is the byte-for-byte source copy of the supplied design. `frontend/index.html` is the Vite-served entry and keeps the same visual structure while changing the live-demo copy to describe the connected backend workflow.

The external runtime in `frontend/integration/chaintrace-runtime.js` owns the integration boundary. It preserves controlled investigator login for the hackathon demo, blocks unsupported chains with an explicit coming-soon state, creates a persisted case, triggers backend analysis, then loads and renders the case, priority, risk, transactions, related cases, VASP attribution, and investigation report endpoints. DOM updates use text nodes for backend values rather than interpolating untrusted values into HTML.

## Local development

Start Flask from the repository root with the intentional SQLite test database:

```bash
DATABASE_URL=sqlite:////tmp/chaintrace.sqlite3 REQUIRE_POSTGRES=false python3 backend/app.py
```

In a second terminal, start Vite:

```bash
cd frontend
npm install
npm run dev
```

When `VITE_API_BASE_URL` is empty, the client calls relative `/api` paths and Vite proxies those requests to `http://127.0.0.1:5000`. For a deployed frontend, set `VITE_API_BASE_URL` to the public Flask API origin before running `npm run build`; the same runtime then uses that origin directly.

## Production build

```bash
cd frontend
npm run build
```

The production bundle is generated in `frontend/dist`. The frontend requires the Flask API’s CORS policy to allow the deployed origin when `VITE_API_BASE_URL` points to a different origin. The UI’s VASP language remains intentionally qualified as a potential association, not a confirmed exchange identity.

## Supported-chain behavior

The supplied HTML lists Ethereum, Bitcoin, Tron, BNB Smart Chain, and Polygon. The current MVP backend has deterministic Ethereum demo analysis only. The runtime leaves Ethereum active and labels the remaining options as `coming soon` rather than implying unsupported live tracing.
