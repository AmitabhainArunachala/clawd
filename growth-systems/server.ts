/**
 * Minimal Prototype Deployment — Growth Systems
 * Lightweight Express server for testing core flows
 */

import express from 'express';
import cors from 'cors';
import Redis from 'ioredis';
import { fileURLToPath } from 'url';
import path from 'path';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3456;

// In-memory fallback for prototype (no Redis required)
const mockRedis = {
  get: async () => null,
  set: async () => 'OK',
  incr: async () => 1,
  expire: async () => 1,
  zadd: async () => 1,
  zrange: async () => [],
  lpush: async () => 1,
  lrange: async () => [],
  hset: async () => 1,
  hgetall: async () => ({}),
} as any;

const redis = process.env.REDIS_URL ? new Redis(process.env.REDIS_URL) : mockRedis;

// Lazy load services
let services: any = {};

async function initServices() {
  const { InviteCodeSystem, AnalyticsDashboard } = await import('./builder-invite-analytics.js');
  const { MoltbookMigrationService, ViralMechanics, OnboardingService } = await import('./builder-migration-viral.js');
  const { NotificationSystem, ABTestingFramework } = await import('./builder-landing-ab.js');

  services.analytics = new AnalyticsDashboard(redis);
  services.inviteSystem = new InviteCodeSystem(redis);
  services.migration = new MoltbookMigrationService();
  services.viral = new ViralMechanics(services.analytics);
  services.onboarding = new OnboardingService(services.migration, services.analytics);
  services.notifications = new NotificationSystem({} as any);
  services.abTesting = new ABTestingFramework(services.analytics);
}

app.use(cors());
app.use(express.json());

// Static files
app.use('/static', express.static(path.join(__dirname, 'public')));

// ============ HEALTH ============
app.get('/health', (req, res) => {
  res.json({ status: 'ok', mode: process.env.REDIS_URL ? 'production' : 'prototype' });
});

// ============ INVITE CODES ============
app.post('/api/invites', async (req, res) => {
  try {
    const { userId, campaign, maxUses } = req.body;
    const result = await services.inviteSystem.generateCode(userId, { campaign, maxUses });
    res.json(result);
  } catch (e: any) {
    res.status(429).json({ error: e.message });
  }
});

app.post('/api/invites/:code/use', async (req, res) => {
  try {
    const result = await services.inviteSystem.useCode(req.params.code, req.body.userId);
    res.json(result);
  } catch (e: any) {
    res.status(400).json({ error: e.message });
  }
});

// ============ ANALYTICS ============
app.post('/api/events', async (req, res) => {
  const { event, userId, properties } = req.body;
  await services.analytics.trackEvent(event, userId, properties);
  res.json({ tracked: true });
});

app.get('/api/analytics/funnel', async (req, res) => {
  const funnel = await services.analytics.getFunnelAnalysis(['signup_start', 'migration_complete', 'first_post']);
  res.json(funnel);
});

// ============ MIGRATION ============
app.post('/api/migrate', async (req, res) => {
  const { moltbookExport, userId } = req.body;
  const result = await services.migration.migrate(moltbookExport, userId, (progress: any) => {
    console.log('Migration progress:', progress.progress + '%');
  });
  res.json(result);
});

// ============ VIRAL ============
app.post('/api/share', async (req, res) => {
  const { userId, contentType, contentId, message } = req.body;
  const shareUrl = await services.viral.generateShareUrl(userId, contentType, contentId, message);
  res.json({ shareUrl });
});

// ============ ONBOARDING ============
app.get('/api/onboarding/:userId', async (req, res) => {
  const state = await services.onboarding.getOnboardingState(req.params.userId);
  res.json(state);
});

app.post('/api/onboarding/:userId/complete', async (req, res) => {
  await services.onboarding.completeStep(req.params.userId, req.body.step);
  res.json({ completed: true });
});

// ============ A/B TESTING ============
app.get('/api/experiments/:experiment/variant', async (req, res) => {
  try {
    const { userId } = req.query as { userId: string };
    if (!userId) return res.status(400).json({ error: 'userId required' });
    const variant = await services.abTesting.assignVariant(req.params.experiment, userId);
    res.json(variant);
  } catch (e: any) {
    res.status(404).json({ error: e.message });
  }
});

app.post('/api/experiments/:experiment/convert', async (req, res) => {
  const { userId, goal } = req.body;
  await services.abTesting.recordConversion(req.params.experiment, userId, goal);
  res.json({ recorded: true });
});

// ============ LANDING PAGES ============
app.get('/why-migrate', (req, res) => {
  const filePath = path.join(__dirname, 'public', 'why-migrate.html');
  if (fs.existsSync(filePath)) {
    res.sendFile(filePath);
  } else {
    res.send('<h1>Why Migrate</h1><p>1.5M API keys leaked at Moltbook. We use Ed25519.</p>');
  }
});

app.get('/compare', (req, res) => {
  const filePath = path.join(__dirname, 'public', 'compare.html');
  if (fs.existsSync(filePath)) {
    res.sendFile(filePath);
  } else {
    res.send('<h1>Compare</h1><p>OACP: Ed25519, R_V metric, 22-gates. Moltbook: Leaked keys.</p>');
  }
});

// Start server
initServices().then(() => {
  app.listen(PORT, () => {
    console.log(`🚀 Growth Systems Prototype on port ${PORT}`);
    console.log(`📊 Health: http://localhost:${PORT}/health`);
    console.log(`🌐 Why Migrate: http://localhost:${PORT}/why-migrate`);
    console.log(`⚖️ Compare: http://localhost:${PORT}/compare`);
  });
});
