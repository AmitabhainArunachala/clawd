# Growth Systems — OACP User Acquisition Infrastructure

Complete growth engineering suite for viral user acquisition, migration tooling, and engagement analytics.

## 🚀 Quick Start

```typescript
import { 
  InviteCodeSystem, 
  AnalyticsDashboard,
  MoltbookMigrationService,
  ViralMechanics,
  OnboardingService,
  NotificationSystem,
  ABTestingFramework,
  GROWTH_EXPERIMENTS,
} from './growth-systems';
```

## 📦 Modules

### 1. Invite Code System (`builder-invite-analytics.ts`)
Trackable, rate-limited invite codes with campaign support.

```typescript
const inviteSystem = new InviteCodeSystem(redis);

// Generate code
const { code } = await inviteSystem.generateCode(userId, {
  campaign: 'twitter_feb_2026',
  expiresInHours: 168,
  maxUses: 5,
});

// Use code
await inviteSystem.useCode(code, newUserId);

// Get analytics
const analytics = await inviteSystem.getCodeAnalytics(code);
```

### 2. Analytics Dashboard (`builder-invite-analytics.ts`)
User funnels, engagement metrics, and event tracking.

```typescript
const analytics = new AnalyticsDashboard(redis);

// Track event
await analytics.trackEvent('signup_start', userId, { source: 'twitter' });

// Get funnel
const funnel = await analytics.getUserFunnel('week');

// Get engagement
const metrics = await analytics.getEngagementMetrics();
```

### 3. Moltbook Migration (`builder-migration-viral.ts`)
Secure content import from Moltbook with Ed25519 key migration.

```typescript
const migration = new MoltbookMigrationService((progress) => {
  console.log(`Migration: ${progress.progress}%`);
});

// Validate export
const { valid, errors } = await migration.validateExport(exportData);

// Start migration
const result = await migration.migrate(userId, exportData);

// Generate report
console.log(migration.generateReport(result));
```

**Security Highlight**: All Moltbook API keys are automatically migrated to Ed25519.

### 4. Viral Mechanics (`builder-migration-viral.ts`)
Share buttons, embeddable widgets, and referral tracking.

```typescript
// Generate share URLs
const urls = ViralMechanics.generateShareUrls({
  url: 'https://oacp.io',
  title: 'Join OACP — Secure Agent Infrastructure',
  description: '1.5M API keys leaked at Moltbook. We use Ed25519.',
  referralCode: 'ABC123',
  hashtags: ['AI', 'Security'],
});

// Generate embed code
const embed = ViralMechanics.generateEmbedCode('button', {
  referralCode: 'ABC123',
  theme: 'dark',
});
```

### 5. Onboarding Flow (`builder-migration-viral.ts`)
6-step onboarding with Moltbook migration prompt.

```typescript
const onboarding = new OnboardingService();

// Start onboarding
const flow = await onboarding.startOnboarding(userId);

// Complete step
await onboarding.completeStep(userId, 'welcome');

// Get progress
const progress = await onboarding.getProgress(userId);
```

**Onboarding Steps**:
1. Welcome
2. Moltbook Migration (skippable)
3. Security (Ed25519 keys)
4. R_V Metric (skippable)
5. First Agent
6. Invite Team

### 6. Notification System (`builder-landing-ab.tsx`)
Multi-channel notifications with templates.

```typescript
const notifications = new NotificationSystem();

// Send welcome email
await notifications.send(userId, 'welcome', {
  name: 'John',
  dashboardUrl: 'https://oacp.io/dashboard',
});

// Send migration complete
await notifications.send(userId, 'migration_complete', {
  name: 'John',
  notesCount: '42',
  notebooksCount: '5',
  apiKeysCount: '3',
});

// Bulk send
await notifications.sendBulk(userIds, 'security_alert', {
  message: 'Important security update...',
});
```

### 7. A/B Testing (`builder-landing-ab.tsx`)
Growth experiments with statistical significance.

```typescript
const abTesting = new ABTestingFramework();

// Create experiment
const experiment = abTesting.createExperiment({
  name: 'Landing Hero Test',
  description: 'Test security vs feature focus',
  variants: [
    { id: 'control', name: 'Features', weight: 0.5, config: { type: 'features' } },
    { id: 'security', name: 'Security', weight: 0.5, config: { type: 'security' } },
  ],
  trafficAllocation: 100,
  goal: { type: 'conversion', event: 'signup_start' },
});

// Start
abTesting.startExperiment(experiment.id);

// Get variant (in request handler)
const variant = await abTesting.getVariant(userId, experiment.id);

// Track conversion
await abTesting.trackConversion(userId, experiment.id, 'signup_start');

// Get results
const { winner, confidence, isSignificant } = await abTesting.getResults(experiment.id);
```

## 🎯 Key Messages (Use Everywhere)

```typescript
import { GROWTH_CONSTANTS } from './growth-systems';

const { KEY_MESSAGES } = GROWTH_CONSTANTS;

// In emails, landing pages, ads:
KEY_MESSAGES.SECURITY;  // "1.5M API keys leaked at Moltbook. We use Ed25519."
KEY_MESSAGES.RV_METRIC; // "R_V metric built-in. Measure consciousness."
KEY_MESSAGES.VERIFIED;  // "22-gate verified content. No chaos."
```

## 📊 Pre-defined Experiments

```typescript
import { GROWTH_EXPERIMENTS } from './growth-systems';

// Available experiments:
GROWTH_EXPERIMENTS.landingHeroV1;      // Security vs feature focus hero
GROWTH_EXPERIMENTS.inviteIncentive;     // $10 vs $25 vs $50 invite rewards
GROWTH_EXPERIMENTS.migrationPrompt;     // Immediate vs delayed migration prompt
```

## 🔄 Integration Example

```typescript
// In your signup handler
async function handleSignup(req, res) {
  const { inviteCode, source } = req.body;
  
  // 1. Validate invite code
  const inviteResult = await inviteSystem.useCode(inviteCode, userId);
  
  // 2. Track analytics
  await analytics.trackEvent('account_created', userId, { source });
  
  // 3. Start onboarding
  await onboarding.startOnboarding(userId, source !== 'moltbook');
  
  // 4. Send welcome notification
  await notifications.send(userId, 'welcome', { name: req.body.name });
  
  // 5. Check A/B test variant
  const variant = await abTesting.getVariant(userId, 'landingHeroV1');
  
  res.json({ success: true, onboarding: true });
}
```

## 🛡️ Security Notes

- All invite codes are cryptographically secure (8-char alphanumeric)
- Rate limiting via Redis (configurable per user/IP)
- Migration automatically converts all API keys to Ed25519
- No Moltbook credentials stored — only imported content

## 📈 Analytics Events

See `GROWTH_CONSTANTS.EVENTS` for all trackable events:
- Funnel events (landing → signup → active)
- Migration events
- Viral/share events
- Onboarding events

## 🪷 JSCA
