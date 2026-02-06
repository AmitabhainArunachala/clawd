# Growth Systems — Integration Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (Next.js)                     │
├─────────────┬─────────────┬─────────────┬───────────────────┤
│   Landing   │   Share     │  Onboarding │   Analytics       │
│   Pages     │   Buttons   │   Wizard    │   Dashboard       │
└──────┬──────┴──────┬──────┴──────┬──────┴─────────┬─────────┘
       │             │             │                │
       └─────────────┴──────┬──────┴────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                     API LAYER (Next.js API)                 │
├─────────────┬─────────────┬─────────────┬───────────────────┤
│   /invites  │  /migrate   │  /onboard   │   /analytics      │
│   /referral │  /import    │  /progress  │   /track          │
└──────┬──────┴──────┬──────┴──────┬──────┴─────────┬─────────┘
       │             │             │                │
       └─────────────┴──────┬──────┴────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                  GROWTH SYSTEMS MODULES                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│  │  Invite  │ │ Migration│ │ Viral    │ │  A/B Testing │  │
│  │  System  │ │ Service  │ │ Mechanics│ │  Framework   │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘  │
│       └─────────────┴───────────┴──────────────┘          │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      DATA STORES                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   PostgreSQL │  │    Redis     │  │  Analytics   │      │
│  │   (Users)    │  │(Rate Limits) │  │   (Events)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Setup Steps

### 1. Environment Variables

```bash
# Redis (for rate limiting & sessions)
REDIS_URL=redis://localhost:6379

# Database
DATABASE_URL=postgresql://...

# Email (SendGrid/AWS SES)
EMAIL_API_KEY=...
EMAIL_FROM=noreply@oacp.io

# Analytics (optional)
POSTHOG_KEY=...
AMPLITUDE_KEY=...
```

### 2. Database Schema

```sql
-- Invite codes
CREATE TABLE invite_codes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code VARCHAR(8) UNIQUE NOT NULL,
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP,
  max_uses INTEGER DEFAULT 1,
  used_count INTEGER DEFAULT 0,
  campaign VARCHAR(100),
  metadata JSONB DEFAULT '{}'
);

-- Onboarding progress
CREATE TABLE onboarding_progress (
  user_id UUID PRIMARY KEY REFERENCES users(id),
  current_step INTEGER DEFAULT 0,
  steps_completed JSONB DEFAULT '[]',
  started_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP
);

-- Migration records
CREATE TABLE migrations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  source VARCHAR(50) DEFAULT 'moltbook',
  status VARCHAR(20) DEFAULT 'pending',
  items_total INTEGER DEFAULT 0,
  items_processed INTEGER DEFAULT 0,
  errors JSONB DEFAULT '[]',
  started_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP
);

-- A/B test assignments
CREATE TABLE experiment_assignments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  experiment_id VARCHAR(100) NOT NULL,
  variant_id VARCHAR(100) NOT NULL,
  assigned_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, experiment_id)
);

-- Notifications
CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  template_id VARCHAR(100) NOT NULL,
  channels VARCHAR(20)[] DEFAULT '{}',
  variables JSONB DEFAULT '{}',
  status VARCHAR(20) DEFAULT 'pending',
  sent_at TIMESTAMP,
  delivered_at TIMESTAMP
);
```

### 3. API Routes

```typescript
// app/api/invites/route.ts
import { InviteCodeSystem } from '@/growth-systems';
import { redis } from '@/lib/redis';

const inviteSystem = new InviteCodeSystem(redis);

export async function POST(req: Request) {
  const { userId, campaign } = await req.json();
  
  try {
    const { code } = await inviteSystem.generateCode(userId, { campaign });
    return Response.json({ code });
  } catch (error) {
    return Response.json({ error: error.message }, { status: 429 });
  }
}

// app/api/migrate/route.ts
import { MoltbookMigrationService } from '@/growth-systems';

export async function POST(req: Request) {
  const { userId, exportData } = await req.json();
  
  const migration = new MoltbookMigrationService((progress) => {
    // Send progress via WebSocket or SSE
    sendProgress(userId, progress);
  });
  
  // Validate
  const { valid, errors } = await migration.validateExport(exportData);
  if (!valid) {
    return Response.json({ error: 'Invalid export', errors }, { status: 400 });
  }
  
  // Migrate
  const result = await migration.migrate(userId, exportData);
  
  return Response.json({ 
    success: true, 
    report: migration.generateReport(result) 
  });
}

// app/api/track/route.ts
import { AnalyticsDashboard } from '@/growth-systems';

const analytics = new AnalyticsDashboard(redis);

export async function POST(req: Request) {
  const { event, userId, metadata } = await req.json();
  
  await analytics.trackEvent(event, userId, metadata);
  
  return Response.json({ success: true });
}
```

### 4. React Component Integration

```tsx
// app/onboarding/page.tsx
import { OnboardingWizard } from '@/growth-systems/builder-migration-viral';

export default async function OnboardingPage() {
  const userId = await getCurrentUser();
  const flow = await onboarding.getOnboardingFlow(userId);
  
  return (
    <OnboardingWizard 
      flow={flow}
      onComplete={() => redirect('/dashboard')}
      onSkip={() => redirect('/dashboard')}
    />
  );
}

// app/landing/page.tsx with A/B test
import { ABTestingFramework } from '@/growth-systems';

export default async function LandingPage() {
  const userId = await getOrCreateAnonymousUser();
  const abTesting = new ABTestingFramework();
  
  const variant = await abTesting.getVariant(userId, 'landingHeroV1');
  
  return variant?.config.heroType === 'security' 
    ? <SecurityHero />
    : <FeatureHero />;
}
```

### 5. Middleware Setup

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Track landing page views
  if (request.nextUrl.pathname === '/') {
    // Fire and forget analytics
    fetch('/api/track', {
      method: 'POST',
      body: JSON.stringify({
        event: 'landing_view',
        metadata: { 
          source: request.nextUrl.searchParams.get('ref'),
          utm_campaign: request.nextUrl.searchParams.get('utm_campaign'),
        },
      }),
    }).catch(() => {});
  }
  
  return NextResponse.next();
}
```

## Key Workflows

### User Signup Flow
```
1. User visits /?ref=ABC123 (tracked: landing_view)
2. Clicks "Get Started" (tracked: signup_start)
3. Enters invite code ABC123 (validated, tracked: invite_entered)
4. Creates account (tracked: account_created)
5. Redirected to onboarding (tracked: onboarding_started)
6. Completes onboarding (tracked: onboarding_completed)
7. First action (tracked: first_action)
```

### Migration Flow
```
1. User clicks "Migrate from Moltbook"
2. Uploads Moltbook export file
3. System validates export format
4. Migration starts (progress streamed via WebSocket)
5. API keys auto-converted to Ed25519
6. Content imported with 22-gate verification
7. Report generated and emailed
8. Old Moltbook keys marked as compromised
```

### Viral Referral Flow
```
1. User gets invite code after onboarding
2. Shares via Twitter/Facebook/Email (tracked: share)
3. Friend clicks referral link (tracked: referral_click)
4. Friend signs up using code (tracked: referral_conversion)
5. Both users get credit
6. Notification sent to referrer
```

## Monitoring

### Key Metrics to Track

```typescript
// Daily active users
const dau = await analytics.getEngagementMetrics().dau;

// Conversion rate (signup to active)
const funnel = await analytics.getUserFunnel('week');
const conversionRate = funnel.conversionRate;

// Migration success rate
const migrationSuccess = await db.query(`
  SELECT 
    COUNT(*) FILTER (WHERE status = 'completed') * 100.0 / COUNT(*)
  FROM migrations
`);

// A/B test significance
const { confidence, isSignificant } = await abTesting.getResults('landingHeroV1');
```

### Alerts to Set Up

- Migration failure rate > 5%
- Signup conversion rate drops > 20%
- Invite code abuse (sudden spike in generation)
- A/B test reaches significance

## Security Checklist

- [ ] Rate limits configured for invite generation
- [ ] Invite codes expire after 7 days
- [ ] Migration files deleted after 24 hours
- [ ] API keys never logged
- [ ] All POST endpoints have CSRF protection
- [ ] Experiment assignments are anonymous

## 🪷 JSCA
