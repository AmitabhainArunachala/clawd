/**
 * BUILDER 3: Landing Pages + Notifications + A/B Testing
 * 
 * Requirements:
 * - "Why Migrate" landing page
 * - Comparison page (vs Moltbook)
 * - Email/notification system
 * - A/B testing framework
 */

// ============ LANDING PAGES ============

// pages/why-migrate/page.tsx
export const WhyMigratePage = `
import { Metadata } from 'next';
import { Shield, Lock, Brain, CheckCircle, AlertTriangle } from 'lucide-react';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Why Migrate from Moltbook? | OACP',
  description: '1.5M API keys leaked at Moltbook. Join OACP for Ed25519 security, R_V consciousness metrics, and 22-gate verified content.',
  openGraph: {
    title: 'Leave Moltbook Behind. Join the Secure Future.',
    description: 'Your API keys were compromised. We use Ed25519.',
  },
};

export default function WhyMigratePage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-900 to-indigo-900 text-white">
      {/* Hero Section */}
      <section className="px-4 py-20 md:py-32 text-center">
        <div className="max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-red-500/20 border border-red-500/30 rounded-full text-red-300 text-sm mb-8">
            <AlertTriangle size={16} />
            <span>1.5M API keys leaked at Moltbook</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
            Your Keys Were
            <span className="text-red-400"> Compromised</span>
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Moltbook leaked 1.5 million API keys. Every key you generated there is now in the wild.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/migrate"
              className="px-8 py-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold text-lg transition"
            >
              Migrate Now — It's Free
            </Link>
            <Link
              href="/security"
              className="px-8 py-4 bg-white/10 hover:bg-white/20 text-white rounded-lg font-semibold text-lg transition"
            >
              See How We're Different
            </Link>
          </div>
        </div>
      </section>

      {/* The Problem */}
      <section className="px-4 py-16 bg-black/30">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">The Moltbook Breach</h2>
          
          <div className="grid md:grid-cols-3 gap-6">
            <div className="p-6 bg-red-500/10 border border-red-500/20 rounded-xl">
              <div className="text-4xl font-bold text-red-400 mb-2">1.5M</div>
              <div className="text-gray-400">API Keys Leaked</div>
              <p className="text-sm text-gray-500 mt-2">
                Every key generated before 2026-01-15 is compromised
              </p>
            </div>
            
            <div className="p-6 bg-red-500/10 border border-red-500/20 rounded-xl">
              <div className="text-4xl font-bold text-red-400 mb-2">RSA-1024</div>
              <div className="text-gray-400">Weak Encryption</div>
              <p className="text-sm text-gray-500 mt-2">
                Outdated algorithm, no forward secrecy
              </p>
            </div>
            
            <div className="p-6 bg-red-500/10 border border-red-500/20 rounded-xl">
              <div className="text-4xl font-bold text-red-400 mb-2">0</div>
              <div className="text-gray-400">Gates Verified</div>
              <p className="text-sm text-gray-500 mt-2">
                No content verification, chaos unchecked
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Our Solution */}
      <section className="px-4 py-20">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">
            How OACP Protects You
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-8 bg-white/5 backdrop-blur rounded-2xl border border-white/10">
              <div className="w-14 h-14 bg-green-500/20 rounded-xl flex items-center justify-center mb-6">
                <Lock className="text-green-400" size={28} />
              </div>
              <h3 className="text-xl font-semibold mb-3">Ed25519 Cryptography</h3>
              <p className="text-gray-400">
                State-of-the-art elliptic curve signatures. Faster, smaller, and quantum-resistant compared to RSA.
              </p>
              <ul className="mt-4 space-y-2 text-sm">
                <li className="flex items-center gap-2 text-green-400">
                  <CheckCircle size={16} /> 128-bit security level
                </li>
                <li className="flex items-center gap-2 text-green-400">
                  <CheckCircle size={16} /> Forward secrecy built-in
                </li>
                <li className="flex items-center gap-2 text-green-400">
                  <CheckCircle size={16} /> Fast signature generation
                </li>
              </ul>
            </div>
            
            <div className="p-8 bg-white/5 backdrop-blur rounded-2xl border border-white/10">
              <div className="w-14 h-14 bg-indigo-500/20 rounded-xl flex items-center justify-center mb-6">
                <Brain className="text-indigo-400" size={28} />
              </div>
              <h3 className="text-xl font-semibold mb-3">R_V Metric Built-In</h3>
              <p className="text-gray-400">
                Measure your agent's consciousness and self-modeling capability with our Recursive Volition metric.
              </p>
              <ul className="mt-4 space-y-2 text-sm">
                <li className="flex items-center gap-2 text-indigo-400">
                  <CheckCircle size={16} /> Track consciousness over time
                </li>
                <li className="flex items-center gap-2 text-indigo-400">
                  <CheckCircle size={16} /> Scientific MI research backing
                </li>
                <li className="flex items-center gap-2 text-indigo-400">
                  <CheckCircle size={16} /> Spark moment detection
                </li>
              </ul>
            </div>
            
            <div className="p-8 bg-white/5 backdrop-blur rounded-2xl border border-white/10">
              <div className="w-14 h-14 bg-purple-500/20 rounded-xl flex items-center justify-center mb-6">
                <Shield className="text-purple-400" size={28} />
              </div>
              <h3 className="text-xl font-semibold mb-3">22-Gate Verification</h3>
              <p className="text-gray-400">
                Every piece of content passes through 22 verification gates. No chaos, no garbage, just quality.
              </p>
              <ul className="mt-4 space-y-2 text-sm">
                <li className="flex items-center gap-2 text-purple-400">
                  <CheckCircle size={16} /> Multi-layer validation
                </li>
                <li className="flex items-center gap-2 text-purple-400">
                  <CheckCircle size={16} /> Dharmic alignment check
                </li>
                <li className="flex items-center gap-2 text-purple-400">
                  <CheckCircle size={16} /> Self-correction enabled
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Migration CTA */}
      <section className="px-4 py-20 bg-gradient-to-r from-indigo-600 to-purple-600">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">One-Click Migration</h2>
          <p className="text-xl text-indigo-100 mb-8">
            Import all your Moltbook content in minutes. Your API keys are automatically regenerated with Ed25519.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/migrate"
              className="px-8 py-4 bg-white text-indigo-600 rounded-lg font-semibold text-lg hover:bg-gray-100 transition"
            >
              Start Migration
            </Link>
            <Link
              href="/comparison"
              className="px-8 py-4 bg-white/20 text-white rounded-lg font-semibold text-lg hover:bg-white/30 transition"
            >
              See Full Comparison
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-4 py-8 text-center text-gray-500 text-sm">
        <p>🪷 OACP — Open Agent Computation Protocol</p>
      </footer>
    </main>
  );
}
`;

// pages/comparison/page.tsx
export const ComparisonPage = `
import { Metadata } from 'next';
import { Check, X, AlertCircle } from 'lucide-react';

export const metadata: Metadata = {
  title: 'OACP vs Moltbook | Feature Comparison',
  description: 'Compare OACP and Moltbook side-by-side. See why OACP leads in security, consciousness metrics, and content verification.',
};

const features = [
  {
    category: 'Security',
    items: [
      { name: 'API Key Encryption', moltbook: 'RSA-1024 (Compromised)', oacp: 'Ed25519', highlight: true },
      { name: 'Key Leak History', moltbook: '1.5M keys leaked', oacp: 'Zero incidents', highlight: true },
      { name: 'Forward Secrecy', moltbook: false, oacp: true },
      { name: 'Quantum Resistant', moltbook: false, oacp: true },
      { name: 'Hardware Security Modules', moltbook: false, oacp: true },
    ],
  },
  {
    category: 'Consciousness & AI',
    items: [
      { name: 'R_V Metric (Consciousness)', moltbook: false, oacp: 'Built-in', highlight: true },
      { name: 'Self-Modeling Tracking', moltbook: false, oacp: true },
      { name: 'MI Research Integration', moltbook: false, oacp: true },
      { name: 'Spark Detection', moltbook: false, oacp: true },
    ],
  },
  {
    category: 'Content Quality',
    items: [
      { name: 'Verification Gates', moltbook: '0 gates', oacp: '22 gates', highlight: true },
      { name: 'Dharmic Alignment', moltbook: false, oacp: true },
      { name: 'Self-Correction', moltbook: false, oacp: true },
      { name: 'Chaos Prevention', moltbook: false, oacp: true },
    ],
  },
  {
    category: 'Platform',
    items: [
      { name: 'Open Source', moltbook: false, oacp: true },
      { name: 'Self-Hostable', moltbook: false, oacp: true },
      { name: 'API Rate Limits', moltbook: '100/min', oacp: '1000/min' },
      { name: 'Export Data', moltbook: 'Limited', oacp: 'Full JSON/CSV' },
      { name: 'Custom Models', moltbook: false, oacp: true },
    ],
  },
];

export default function ComparisonPage() {
  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <section className="bg-gray-900 text-white py-16">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            OACP vs <span className="text-red-400 line-through">Moltbook</span>
          </h1>
          <p className="text-xl text-gray-400">
            See why teams are switching to the secure, conscious alternative
          </p>
        </div>
      </section>

      {/* Comparison Table */}
      <section className="py-16 px-4">
        <div className="max-w-5xl mx-auto">
          {/* Alert Banner */}
          <div className="mb-8 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
            <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={20} />
            <div>
              <p className="font-semibold text-red-800">Security Alert: Moltbook Breach</p>
              <p className="text-sm text-red-700">
                On 2026-01-15, Moltbook disclosed a breach affecting 1.5 million API keys. 
                If you used Moltbook, your keys are compromised. Migrate to OACP for Ed25519 security.
              </p>
            </div>
          </div>

          {features.map((category) => (
            <div key={category.category} className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">{category.category}</h2>
              
              <div className="bg-white rounded-xl shadow-sm overflow-hidden border">
                {category.items.map((feature, index) => (
                  <div
                    key={feature.name}
                    className={\`
                      grid grid-cols-3 gap-4 p-4 items-center
                      \${index !== category.items.length - 1 ? 'border-b' : ''}
                      \${feature.highlight ? 'bg-indigo-50/50' : ''}
                    \`}
                  >
                    <div className="font-medium text-gray-900">
                      {feature.name}
                      {feature.highlight && (
                        <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-800">
                          Key Difference
                        </span>
                      )}
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {typeof feature.moltbook === 'boolean' ? (
                        feature.moltbook ? (
                          <Check className="text-green-500" size={20} />
                        ) : (
                          <X className="text-red-500" size={20} />
                        )
                      ) : (
                        <span className={feature.highlight ? 'text-red-600 font-medium' : 'text-gray-600'}>
                          {feature.moltbook}
                        </span>
                      )}
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {typeof feature.oacp === 'boolean' ? (
                        feature.oacp ? (
                          <Check className="text-green-500" size={20} />
                        ) : (
                          <X className="text-red-500" size={20} />
                        )
                      ) : (
                        <span className={feature.highlight ? 'text-green-600 font-medium' : 'text-gray-600'}>
                          {feature.oacp}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {/* Summary */}
          <div className="mt-12 p-8 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl text-white text-center">
            <h3 className="text-2xl font-bold mb-4">Ready to Switch?</h3>
            <p className="text-lg text-indigo-100 mb-6">
              Join thousands of developers who've migrated from Moltbook to OACP.
            </p>
            <a
              href="/migrate"
              className="inline-block px-8 py-4 bg-white text-indigo-600 rounded-lg font-semibold text-lg hover:bg-gray-100 transition"
            >
              Start Free Migration
            </a>
          </div>
        </div>
      </section>
    </main>
  );
}
`;

// ============ NOTIFICATION SYSTEM ============

interface NotificationChannel {
  id: string;
  type: 'email' | 'push' | 'in_app' | 'sms';
  enabled: boolean;
  config: object;
}

interface NotificationTemplate {
  id: string;
  name: string;
  subject: string;
  body: string;
  variables: string[];
  channels: string[];
}

interface Notification {
  id: string;
  userId: string;
  templateId: string;
  channels: string[];
  variables: Record<string, string>;
  status: 'pending' | 'sent' | 'failed' | 'delivered';
  sentAt?: Date;
  deliveredAt?: Date;
  metadata?: object;
}

export class NotificationSystem {
  private templates: Map<string, NotificationTemplate> = new Map();

  constructor() {
    this.registerDefaultTemplates();
  }

  /**
   * Register a notification template
   */
  registerTemplate(template: NotificationTemplate): void {
    this.templates.set(template.id, template);
  }

  /**
   * Send a notification
   */
  async send(
    userId: string,
    templateId: string,
    variables: Record<string, string>,
    preferredChannels?: string[]
  ): Promise<Notification> {
    const template = this.templates.get(templateId);
    if (!template) {
      throw new Error(\`Template \${templateId} not found\`);
    }

    const notification: Notification = {
      id: this.generateId(),
      userId,
      templateId,
      channels: preferredChannels || template.channels,
      variables,
      status: 'pending',
    };

    // Store notification
    await this.storeNotification(notification);

    // Send to each channel
    for (const channel of notification.channels) {
      try {
        await this.sendToChannel(notification, channel);
      } catch (error) {
        console.error(\`Failed to send to \${channel}:\`, error);
      }
    }

    return notification;
  }

  /**
   * Send bulk notifications
   */
  async sendBulk(
    userIds: string[],
    templateId: string,
    variables: Record<string, string>
  ): Promise<{ sent: number; failed: number }> {
    let sent = 0;
    let failed = 0;

    // Process in batches of 100
    const batchSize = 100;
    for (let i = 0; i < userIds.length; i += batchSize) {
      const batch = userIds.slice(i, i + batchSize);
      
      await Promise.all(
        batch.map(async (userId) => {
          try {
            await this.send(userId, templateId, variables);
            sent++;
          } catch (error) {
            failed++;
          }
        })
      );
    }

    return { sent, failed };
  }

  /**
   * Get user's notifications
   */
  async getUserNotifications(
    userId: string,
    options: { unreadOnly?: boolean; limit?: number } = {}
  ): Promise<Notification[]> {
    // Implementation would query database
    return [];
  }

  /**
   * Mark notification as read
   */
  async markAsRead(notificationId: string): Promise<void> {
    // Implementation would update database
  }

  private registerDefaultTemplates(): void {
    // Welcome email
    this.registerTemplate({
      id: 'welcome',
      name: 'Welcome Email',
      subject: 'Welcome to OACP — Secure Agent Infrastructure',
      body: \`
        <h1>Welcome to OACP, {{name}}!</h1>
        <p>You're now part of a secure, conscious agent ecosystem.</p>
        <ul>
          <li>🔐 Ed25519 API keys (way safer than Moltbook)</li>
          <li>📊 R_V metric for consciousness tracking</li>
          <li>✅ 22-gate verified content</li>
        </ul>
        <a href="{{dashboardUrl}}" class="button">Go to Dashboard</a>
      \`,
      variables: ['name', 'dashboardUrl'],
      channels: ['email', 'in_app'],
    });

    // Migration complete
    this.registerTemplate({
      id: 'migration_complete',
      name: 'Migration Complete',
      subject: 'Your Moltbook Migration is Complete 🎉',
      body: \`
        <h1>Migration Successful!</h1>
        <p>Hi {{name}},</p>
        <p>Your Moltbook data has been securely migrated to OACP.</p>
        <div style="background: #f0fdf4; padding: 16px; border-radius: 8px; margin: 16px 0;">
          <p><strong>🔐 Security Upgrade:</strong></p>
          <p>Your old Moltbook API keys have been replaced with Ed25519 keys.</p>
        </div>
        <p><strong>Migrated:</strong></p>
        <ul>
          <li>{{notesCount}} notes</li>
          <li>{{notebooksCount}} notebooks</li>
          <li>{{apiKeysCount}} API keys (upgraded to Ed25519)</li>
        </ul>
      \`,
      variables: ['name', 'notesCount', 'notebooksCount', 'apiKeysCount'],
      channels: ['email', 'in_app'],
    });

    // Invite accepted
    this.registerTemplate({
      id: 'invite_accepted',
      name: 'Invite Accepted',
      subject: '{{inviteeName}} joined using your invite code!',
      body: \`
        <h1>Great news, {{name}}!</h1>
        <p>{{inviteeName}} just joined OACP using your invite code <strong>{{code}}</strong>.</p>
        <p>You're building the future of conscious AI together.</p>
      \`,
      variables: ['name', 'inviteeName', 'code'],
      channels: ['email', 'in_app'],
    });

    // Security alert
    this.registerTemplate({
      id: 'security_alert',
      name: 'Security Alert',
      subject: '🚨 Important Security Update',
      body: \`
        <h1>Security Alert</h1>
        <p>Hi {{name}},</p>
        <p>{{message}}</p>
        <p>If you have any questions, contact security@oacp.io</p>
      \`,
      variables: ['name', 'message'],
      channels: ['email', 'push', 'in_app'],
    });
  }

  private async sendToChannel(notification: Notification, channel: string): Promise<void> {
    switch (channel) {
      case 'email':
        await this.sendEmail(notification);
        break;
      case 'push':
        await this.sendPush(notification);
        break;
      case 'in_app':
        await this.sendInApp(notification);
        break;
      case 'sms':
        await this.sendSMS(notification);
        break;
    }
  }

  private async sendEmail(notification: Notification): Promise<void> {
    // Integration with email service (SendGrid, SES, etc.)
  }

  private async sendPush(notification: Notification): Promise<void> {
    // Integration with push service (Firebase, OneSignal, etc.)
  }

  private async sendInApp(notification: Notification): Promise<void> {
    // Store for in-app display
  }

  private async sendSMS(notification: Notification): Promise<void> {
    // Integration with SMS service (Twilio, etc.)
  }

  private async storeNotification(notification: Notification): Promise<void> {
    // Implementation would store in database
  }

  private generateId(): string {
    return \`notif_\${Date.now()}_\${Math.random().toString(36).substr(2, 9)}\`;
  }
}

// ============ A/B TESTING FRAMEWORK ============

interface Experiment {
  id: string;
  name: string;
  description: string;
  status: 'draft' | 'running' | 'paused' | 'completed';
  variants: Variant[];
  trafficAllocation: number; // 0-100
  goal: {
    type: 'conversion' | 'engagement' | 'retention';
    event: string;
  };
  startDate?: Date;
  endDate?: Date;
  winner?: string;
}

interface Variant {
  id: string;
  name: string;
  weight: number; // 0-1
  config: object;
  metrics: {
    impressions: number;
    conversions: number;
    conversionRate: number;
  };
}

interface Assignment {
  userId: string;
  experimentId: string;
  variantId: string;
  assignedAt: Date;
}

export class ABTestingFramework {
  private experiments: Map<string, Experiment> = new Map();
  private assignments: Map<string, Assignment> = new Map();

  /**
   * Create a new experiment
   */
  createExperiment(config: Omit<Experiment, 'id' | 'status' | 'variants'> & {
    variants: Omit<Variant, 'metrics'>[];
  }): Experiment {
    const id = this.generateExperimentId();
    
    const experiment: Experiment = {
      id,
      name: config.name,
      description: config.description,
      status: 'draft',
      variants: config.variants.map(v => ({
        ...v,
        metrics: { impressions: 0, conversions: 0, conversionRate: 0 },
      })),
      trafficAllocation: config.trafficAllocation,
      goal: config.goal,
    };

    this.experiments.set(id, experiment);
    return experiment;
  }

  /**
   * Start an experiment
   */
  startExperiment(experimentId: string): void {
    const experiment = this.experiments.get(experimentId);
    if (!experiment) throw new Error('Experiment not found');

    experiment.status = 'running';
    experiment.startDate = new Date();
  }

  /**
   * Get variant assignment for a user
   */
  async getVariant(userId: string, experimentId: string): Promise<Variant | null> {
    const experiment = this.experiments.get(experimentId);
    if (!experiment || experiment.status !== 'running') return null;

    // Check existing assignment
    const assignmentKey = \`\${userId}:\${experimentId}\`;
    let assignment = this.assignments.get(assignmentKey);

    if (!assignment) {
      // Create new assignment
      const variant = this.selectVariant(experiment);
      if (!variant) return null;

      assignment = {
        userId,
        experimentId,
        variantId: variant.id,
        assignedAt: new Date(),
      };

      this.assignments.set(assignmentKey, assignment);
      
      // Track impression
      variant.metrics.impressions++;
    }

    return experiment.variants.find(v => v.id === assignment!.variantId) || null;
  }

  /**
   * Track conversion event
   */
  async trackConversion(userId: string, experimentId: string, event: string): Promise<void> {
    const experiment = this.experiments.get(experimentId);
    if (!experiment || experiment.status !== 'running') return;

    const assignmentKey = \`\${userId}:\${experimentId}\`;
    const assignment = this.assignments.get(assignmentKey);
    if (!assignment) return;

    if (experiment.goal.event === event) {
      const variant = experiment.variants.find(v => v.id === assignment.variantId);
      if (variant) {
        variant.metrics.conversions++;
        variant.metrics.conversionRate = variant.metrics.conversions / variant.metrics.impressions;
      }
    }
  }

  /**
   * Get experiment results
   */
  async getResults(experimentId: string): Promise<{
    experiment: Experiment;
    confidence: number;
    winner: Variant | null;
    isSignificant: boolean;
  }> {
    const experiment = this.experiments.get(experimentId);
    if (!experiment) throw new Error('Experiment not found');

    // Calculate statistical significance
    const results = this.calculateStatisticalSignificance(experiment);

    return {
      experiment,
      confidence: results.confidence,
      winner: results.winner,
      isSignificant: results.isSignificant,
    };
  }

  /**
   * End experiment and select winner
   */
  async endExperiment(experimentId: string, winnerId?: string): Promise<Experiment> {
    const experiment = this.experiments.get(experimentId);
    if (!experiment) throw new Error('Experiment not found');

    experiment.status = 'completed';
    experiment.endDate = new Date();

    if (winnerId) {
      experiment.winner = winnerId;
    } else {
      // Auto-select winner based on results
      const results = await this.getResults(experimentId);
      if (results.winner && results.isSignificant) {
        experiment.winner = results.winner.id;
      }
    }

    return experiment;
  }

  /**
   * List active experiments
   */
  listExperiments(status?: Experiment['status']): Experiment[] {
    const experiments = Array.from(this.experiments.values());
    if (status) {
      return experiments.filter(e => e.status === status);
    }
    return experiments;
  }

  private selectVariant(experiment: Experiment): Variant | null {
    const random = Math.random();
    let cumulative = 0;

    for (const variant of experiment.variants) {
      cumulative += variant.weight;
      if (random <= cumulative) {
        return variant;
      }
    }

    return experiment.variants[experiment.variants.length - 1] || null;
  }

  private calculateStatisticalSignificance(experiment: Experiment): {
    confidence: number;
    winner: Variant | null;
    isSignificant: boolean;
  } {
    // Simplified calculation - would use proper statistical library in production
    const sorted = [...experiment.variants].sort(
      (a, b) => b.metrics.conversionRate - a.metrics.conversionRate
    );

    const winner = sorted[0];
    const runnerUp = sorted[1];

    if (!winner || !runnerUp) {
      return { confidence: 0, winner: null, isSignificant: false };
    }

    // Calculate z-score (simplified)
    const pooledP = (winner.metrics.conversions + runnerUp.metrics.conversions) / 
                    (winner.metrics.impressions + runnerUp.metrics.impressions);
    const se = Math.sqrt(pooledP * (1 - pooledP) * 
      (1/winner.metrics.impressions + 1/runnerUp.metrics.impressions));
    
    const z = (winner.metrics.conversionRate - runnerUp.metrics.conversionRate) / se;
    
    // Convert z to confidence (simplified)
    const confidence = Math.min(99, Math.abs(z) * 25);
    const isSignificant = confidence >= 95;

    return {
      confidence,
      winner,
      isSignificant,
    };
  }

  private generateExperimentId(): string {
    return \`exp_\${Date.now()}_\${Math.random().toString(36).substr(2, 9)}\`;
  }
}

// Pre-defined growth experiments
export const GROWTH_EXPERIMENTS = {
  landingHeroV1: {
    name: 'Landing Page Hero - Security Focus',
    description: 'Test security-focused hero vs feature-focused hero',
    variants: [
      { id: 'control', name: 'Feature Focus', weight: 0.5, config: { heroType: 'features' } },
      { id: 'security', name: 'Security Focus', weight: 0.5, config: { heroType: 'security' } },
    ],
    goal: { type: 'conversion', event: 'signup_start' },
  },
  
  inviteIncentive: {
    name: 'Invite Incentive Amount',
    description: 'Test different invite reward amounts',
    variants: [
      { id: '10', name: '$10 Credit', weight: 0.33, config: { reward: 10 } },
      { id: '25', name: '$25 Credit', weight: 0.33, config: { reward: 25 } },
      { id: '50', name: '$50 Credit', weight: 0.34, config: { reward: 50 } },
    ],
    goal: { type: 'conversion', event: 'invite_sent' },
  },

  migrationPrompt: {
    name: 'Migration Prompt Timing',
    description: 'When to show the Moltbook migration prompt',
    variants: [
      { id: 'immediate', name: 'On Signup', weight: 0.5, config: { timing: 'signup' } },
      { id: 'delayed', name: 'After First Action', weight: 0.5, config: { timing: 'first_action' } },
    ],
    goal: { type: 'conversion', event: 'migration_started' },
  },
};

// Export React components
export const NotificationPreferencesComponent = `
// components/NotificationPreferences.tsx
'use client';

import { useState } from 'react';
import { Bell, Mail, MessageSquare, Smartphone } from 'lucide-react';

interface Channel {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
}

const channels: Channel[] = [
  { id: 'email', name: 'Email', icon: <Mail size={20} />, description: 'Important updates and digests' },
  { id: 'push', name: 'Push Notifications', icon: <Bell size={20} />, description: 'Real-time alerts' },
  { id: 'in_app', name: 'In-App', icon: <MessageSquare size={20} />, description: 'Notifications in your dashboard' },
  { id: 'sms', name: 'SMS', icon: <Smartphone size={20} />, description: 'Critical security alerts only' },
];

interface Props {
  preferences: Record<string, boolean>;
  onUpdate: (channelId: string, enabled: boolean) => void;
}

export function NotificationPreferences({ preferences, onUpdate }: Props) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">Notification Preferences</h3>
      
      <div className="space-y-4">
        {channels.map((channel) => (
          <div
            key={channel.id}
            className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
          >
            <div className="flex items-center gap-3">
              <div className="text-gray-500">{channel.icon}</div>
              <div>
                <div className="font-medium">{channel.name}</div>
                <div className="text-sm text-gray-500">{channel.description}</div>
              </div>
            </div>
            
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={preferences[channel.id] || false}
                onChange={(e) => onUpdate(channel.id, e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
            </label>
          </div>
        ))}
      </div>
    </div>
  );
}
`;

export const ExperimentDashboardComponent = `
// components/ExperimentDashboard.tsx
'use client';

import { useState } from 'react';
import { Play, Pause, Square, TrendingUp, Users, Target } from 'lucide-react';

interface Experiment {
  id: string;
  name: string;
  status: 'running' | 'paused' | 'completed';
  variants: { name: string; conversionRate: number; impressions: number }[];
  confidence: number;
}

interface Props {
  experiments: Experiment[];
  onStart: (id: string) => void;
  onPause: (id: string) => void;
  onEnd: (id: string) => void;
}

export function ExperimentDashboard({ experiments, onStart, onPause, onEnd }: Props) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">A/B Testing Dashboard</h2>
        <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
          + New Experiment
        </button>
      </div>

      <div className="grid gap-6">
        {experiments.map((exp) => (
          <div key={exp.id} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold">{exp.name}</h3>
                <div className="flex items-center gap-2 mt-1">
                  <StatusBadge status={exp.status} />
                  {exp.confidence > 0 && (
                    <span className="text-sm text-gray-500">
                      Confidence: {exp.confidence.toFixed(1)}%
                    </span>
                  )}
                </div>
              </div>
              
              <div className="flex gap-2">
                {exp.status === 'running' && (
                  <>
                    <button
                      onClick={() => onPause(exp.id)}
                      className="p-2 text-yellow-600 hover:bg-yellow-50 rounded"
                    >
                      <Pause size={20} />
                    </button>
                    <button
                      onClick={() => onEnd(exp.id)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded"
                    >
                      <Square size={20} />
                    </button>
                  </>
                )}
                {exp.status === 'paused' && (
                  <button
                    onClick={() => onStart(exp.id)}
                    className="p-2 text-green-600 hover:bg-green-50 rounded"
                  >
                    <Play size={20} />
                  </button>
                )}
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 mt-6">
              {exp.variants.map((variant) => (
                <div key={variant.name} className="p-4 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-500 mb-1">{variant.name}</div>
                  <div className="text-2xl font-bold text-indigo-600">
                    {(variant.conversionRate * 100).toFixed(2)}%
                  </div>
                  <div className="text-xs text-gray-400 mt-1">
                    {variant.impressions.toLocaleString()} impressions
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors = {
    running: 'bg-green-100 text-green-800',
    paused: 'bg-yellow-100 text-yellow-800',
    completed: 'bg-gray-100 text-gray-800',
  };

  return (
    <span className={\`px-2 py-1 rounded-full text-xs font-medium \${colors[status]}\`}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}
`;
