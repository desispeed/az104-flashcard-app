import express from 'express';
import { timingSafeEqual } from 'node:crypto';
import { getContainers } from './docker.js';

const PORT = Number(process.env.PORT || 8080);
const API_TOKEN = process.env.API_TOKEN || '';

if (!API_TOKEN) {
  console.error('FATAL: API_TOKEN is not set. Refusing to start without auth.');
  process.exit(1);
}

/**
 * Hosts to monitor, supplied as JSON via the HOSTS_JSON env var, e.g.
 *   [{"name":"MacBook","dockerHost":""},
 *    {"name":"GCP VM","dockerHost":"ssh://you@VM_EXTERNAL_IP"}]
 * An empty dockerHost means "the local Docker daemon".
 */
let hosts = [];
try {
  hosts = JSON.parse(process.env.HOSTS_JSON || '[]');
  if (!Array.isArray(hosts)) throw new Error('HOSTS_JSON must be a JSON array');
} catch (err) {
  console.error(`FATAL: could not parse HOSTS_JSON: ${err.message}`);
  process.exit(1);
}

if (hosts.length === 0) {
  console.warn('WARNING: no hosts configured in HOSTS_JSON; /api/containers will be empty.');
}

const app = express();
app.disable('x-powered-by');

// Constant-time bearer-token check on every route except health.
app.use((req, res, next) => {
  if (req.path === '/api/health') return next();

  const header = req.get('authorization') || '';
  const presented = header.startsWith('Bearer ') ? header.slice(7) : '';
  const a = Buffer.from(presented);
  const b = Buffer.from(API_TOKEN);
  const ok = a.length === b.length && timingSafeEqual(a, b);
  if (!ok) {
    return res.status(401).json({ error: 'unauthorized' });
  }
  next();
});

app.get('/api/health', (_req, res) => {
  res.json({ ok: true, hosts: hosts.map((h) => h.name) });
});

app.get('/api/containers', async (_req, res) => {
  const results = await Promise.all(
    hosts.map(async (h) => {
      try {
        return { host: h.name, ok: true, error: null, containers: await getContainers(h) };
      } catch (err) {
        return {
          host: h.name,
          ok: false,
          error: String(err.message || err).slice(0, 500),
          containers: [],
        };
      }
    })
  );
  res.json({ hosts: results, fetchedAt: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(`container-monitor listening on :${PORT} | hosts: ${hosts.map((h) => h.name).join(', ') || '(none)'}`);
});
