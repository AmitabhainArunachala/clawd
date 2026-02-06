/**
 * BUILDER 3: Landing Pages + Notifications + A/B Testing (Prototype Stub)
 * Simplified for minimal deployment
 */

// ============ NOTIFICATION SYSTEM ============

interface Notification {
  id: string;
  userId: string;
  templateId: string;
  channels: string[];
  variables: Record<string, string>;
  status: 'pending' | 'sent' | 'failed';
  createdAt: Date;
  sentAt?: Date;
}

interface NotificationTemplate {
  id: string;
  name: string;
  channels: string[];
  subject?: string;
  body: string;
  htmlBody?: string;
}

export class NotificationSystem {
  private templates: Map<string, NotificationTemplate> = new Map();
  private notifications: Map<string, Notification> = new Map();

  constructor(private providers: any) {
    this.registerDefaultTemplates();
  }

  private registerDefaultTemplates() {
    this.templates.set('welcome', {
      id: 'welcome',
      name: 'Welcome Email',
      channels: ['email', 'in_app'],
      subject: 'Welcome to OACP',
      body: 'Welcome! Your migration from Moltbook is complete. Ed25519 keys active.',
    });
    this.templates.set('migration_complete', {
      id: 'migration_complete',
      name: 'Migration Complete',
      channels: ['email', 'in_app'],
      subject: 'Migration Complete — You\'re Secure',
      body: 'Your Moltbook data has been migrated. 1.5M keys were leaked there. You are now safe.',
    });
    this.templates.set('security_alert', {
      id: 'security_alert',
      name: 'Security Alert',
      channels: ['email', 'push', 'in_app'],
      subject: 'Security Alert',
      body: 'Important security update regarding your account.',
    });
  }

  async send(userId: string, templateId: string, variables: Record<string, string>): Promise<Notification> {
    const template = this.templates.get(templateId);
    if (!template) throw new Error(`Template ${templateId} not found`);

    const notification: Notification = {
      id: Math.random().toString(36).slice(2),
      userId,
      templateId,
      channels: template.channels,
      variables,
      status: 'pending',
      createdAt: new Date(),
    };

    this.notifications.set(notification.id, notification);
    
    // Simulate sending
    setTimeout(() => {
      notification.status = 'sent';
      notification.sentAt = new Date();
    }, 100);

    return notification;
  }
}

// ============ A/B TESTING ============

export interface Experiment {
  id: string;
  name: string;
  status: 'draft' | 'running' | 'paused' | 'completed';
  variants: Variant[];
  goals: string[];
  startDate?: Date;
  endDate?: Date;
}

export interface Variant {
  id: string;
  name: string;
  weight: number;
  config: Record<string, any>;
  metrics: {
    participants: number;
    conversions: Record<string, number>;
  };
}

export const GROWTH_EXPERIMENTS = {
  HEADLINE_SECURITY: {
    id: 'headline_security',
    name: 'Security-focused headline vs feature headline',
    variants: [
      { id: 'security', name: '1.5M Keys Leaked', weight: 0.5, config: { headline: '1.5M API keys leaked at Moltbook' } },
      { id: 'features', name: 'Ed25519 Security', weight: 0.5, config: { headline: 'Ed25519 cryptography for agents' } },
    ],
  },
  CTA_MIGRATE: {
    id: 'cta_migrate',
    name: 'CTA: Migrate Now vs Start Free',
    variants: [
      { id: 'migrate', name: 'Migrate Now', weight: 0.5, config: { cta: 'Migrate Now — It\'s Free' } },
      { id: 'start', name: 'Start Free', weight: 0.5, config: { cta: 'Start Free — No Credit Card' } },
    ],
  },
  SOCIAL_PROOF: {
    id: 'social_proof',
    name: 'Show/hide social proof section',
    variants: [
      { id: 'show', name: 'Show testimonials', weight: 0.5, config: { showSocialProof: true } },
      { id: 'hide', name: 'Hide testimonials', weight: 0.5, config: { showSocialProof: false } },
    ],
  },
  COMPARISON_TABLE: {
    id: 'comparison_table',
    name: 'Comparison table placement',
    variants: [
      { id: 'above', name: 'Above fold', weight: 0.5, config: { position: 'above' } },
      { id: 'below', name: 'Below features', weight: 0.5, config: { position: 'below' } },
    ],
  },
};

export class ABTestingFramework {
  private experiments: Map<string, Experiment> = new Map();
  private userAssignments: Map<string, Map<string, string>> = new Map();

  constructor(private analytics: any) {
    this.loadExperiments();
  }

  private loadExperiments() {
    Object.values(GROWTH_EXPERIMENTS).forEach((exp: any) => {
      this.experiments.set(exp.id, {
        ...exp,
        status: 'running',
        goals: ['signup', 'migration_start', 'migration_complete'],
        variants: exp.variants.map((v: any) => ({ ...v, metrics: { participants: 0, conversions: {} } })),
      });
    });
  }

  async assignVariant(experimentId: string, userId: string): Promise<Variant> {
    const experiment = this.experiments.get(experimentId);
    if (!experiment) throw new Error(`Experiment ${experimentId} not found`);

    // Check existing assignment
    const userExps = this.userAssignments.get(userId) || new Map();
    if (userExps.has(experimentId)) {
      return experiment.variants.find(v => v.id === userExps.get(experimentId))!;
    }

    // Weighted random assignment
    const rand = Math.random();
    let cumWeight = 0;
    const variant = experiment.variants.find(v => {
      cumWeight += v.weight;
      return rand <= cumWeight;
    }) || experiment.variants[0];

    userExps.set(experimentId, variant.id);
    this.userAssignments.set(userId, userExps);
    variant.metrics.participants++;

    return variant;
  }

  async recordConversion(experimentId: string, userId: string, goal: string): Promise<void> {
    const experiment = this.experiments.get(experimentId);
    if (!experiment) return;

    const userExps = this.userAssignments.get(userId);
    if (!userExps || !userExps.has(experimentId)) return;

    const variantId = userExps.get(experimentId)!;
    const variant = experiment.variants.find(v => v.id === variantId);
    if (!variant) return;

    variant.metrics.conversions[goal] = (variant.metrics.conversions[goal] || 0) + 1;
  }

  async getResults(experimentId: string): Promise<any> {
    const experiment = this.experiments.get(experimentId);
    if (!experiment) throw new Error('Experiment not found');
    return experiment;
  }
}
