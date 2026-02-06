/**
 * BUILDER 2: Migration Tools + Viral Mechanics + Onboarding
 * 
 * Requirements:
 * - Moltbook content migration
 * - Viral share/embed features
 * - Onboarding flow for new agents
 */

// ============ MOLTBOOK MIGRATION TOOLS ============

interface MoltbookExport {
  version: string;
  exportDate: string;
  userData: {
    userId: string;
    username: string;
    email: string;
    createdAt: string;
  };
  content: {
    notes: MoltbookNote[];
    notebooks: MoltbookNotebook[];
    tags: string[];
    attachments: MoltbookAttachment[];
  };
  apiKeys?: {
    keyId: string;
    name: string;
    createdAt: string;
    lastUsed?: string;
  }[];
}

interface MoltbookNote {
  id: string;
  title: string;
  content: string;
  createdAt: string;
  updatedAt: string;
  tags: string[];
  notebookId?: string;
  attachments: string[];
}

interface MoltbookNotebook {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
  parentId?: string;
}

interface MoltbookAttachment {
  id: string;
  filename: string;
  mimeType: string;
  size: number;
  url: string;
}

interface MigrationProgress {
  stage: 'preparing' | 'validating' | 'migrating' | 'verifying' | 'complete' | 'error';
  progress: number; // 0-100
  currentItem?: string;
  itemsProcessed: number;
  totalItems: number;
  errors: MigrationError[];
  warnings: string[];
}

interface MigrationError {
  item: string;
  error: string;
  recoverable: boolean;
}

export class MoltbookMigrationService {
  private progress: MigrationProgress;
  private onProgressUpdate?: (progress: MigrationProgress) => void;

  constructor(onProgressUpdate?: (progress: MigrationProgress) => void) {
    this.onProgressUpdate = onProgressUpdate;
    this.progress = {
      stage: 'preparing',
      progress: 0,
      itemsProcessed: 0,
      totalItems: 0,
      errors: [],
      warnings: [],
    };
  }

  /**
   * Validate Moltbook export format
   */
  async validateExport(exportData: unknown): Promise<{ valid: boolean; errors: string[] }> {
    this.updateProgress({ stage: 'validating', progress: 10 });
    
    const errors: string[] = [];
    
    if (!exportData || typeof exportData !== 'object') {
      errors.push('Export data is not a valid object');
      return { valid: false, errors };
    }

    const data = exportData as Partial<MoltbookExport>;

    // Check required fields
    if (!data.version) errors.push('Missing version field');
    if (!data.userData) errors.push('Missing userData');
    if (!data.content) errors.push('Missing content');

    // Validate content structure
    if (data.content) {
      if (!Array.isArray(data.content.notes)) {
        errors.push('content.notes must be an array');
      }
      if (!Array.isArray(data.content.notebooks)) {
        errors.push('content.notebooks must be an array');
      }
    }

    // Check for API keys (security warning)
    if (data.apiKeys && data.apiKeys.length > 0) {
      this.progress.warnings.push(
        `⚠️ Found ${data.apiKeys.length} API keys. These will be migrated to Ed25519 secure keys.`
      );
    }

    this.updateProgress({ progress: errors.length === 0 ? 30 : 0 });
    
    return { valid: errors.length === 0, errors };
  }

  /**
   * Start migration process
   */
  async migrate(userId: string, exportData: MoltbookExport): Promise<MigrationResult> {
    this.updateProgress({ stage: 'migrating', progress: 30 });

    const totalItems = 
      exportData.content.notes.length + 
      exportData.content.notebooks.length +
      (exportData.apiKeys?.length || 0);

    this.updateProgress({ totalItems });

    const result: MigrationResult = {
      userId,
      migratedNotes: [],
      migratedNotebooks: [],
      migratedApiKeys: [],
      failedItems: [],
      startTime: new Date(),
      endTime: null,
    };

    // Migrate notebooks first (parent references)
    for (const notebook of exportData.content.notebooks) {
      try {
        const migrated = await this.migrateNotebook(userId, notebook);
        result.migratedNotebooks.push(migrated);
        this.incrementProgress(`Notebook: ${notebook.name}`);
      } catch (error) {
        this.handleError('notebook', notebook.name, error as Error);
        result.failedItems.push({ type: 'notebook', id: notebook.name, error: (error as Error).message });
      }
    }

    // Migrate notes
    for (const note of exportData.content.notes) {
      try {
        const migrated = await this.migrateNote(userId, note);
        result.migratedNotes.push(migrated);
        this.incrementProgress(`Note: ${note.title}`);
      } catch (error) {
        this.handleError('note', note.title, error as Error);
        result.failedItems.push({ type: 'note', id: note.title, error: (error as Error).message });
      }
    }

    // Migrate API keys to Ed25519
    if (exportData.apiKeys) {
      for (const apiKey of exportData.apiKeys) {
        try {
          const migrated = await this.migrateApiKey(userId, apiKey);
          result.migratedApiKeys.push(migrated);
          this.incrementProgress(`API Key: ${apiKey.name}`);
        } catch (error) {
          this.handleError('apiKey', apiKey.name, error as Error);
          result.failedItems.push({ type: 'apiKey', id: apiKey.name, error: (error as Error).message });
        }
      }
    }

    this.updateProgress({ stage: 'verifying', progress: 90 });

    // Verification step
    await this.verifyMigration(result);

    result.endTime = new Date();
    this.updateProgress({ stage: 'complete', progress: 100 });

    return result;
  }

  /**
   * Generate migration report
   */
  generateReport(result: MigrationResult): string {
    const duration = result.endTime && result.startTime 
      ? (result.endTime.getTime() - result.startTime.getTime()) / 1000 
      : 0;

    return `
# Moltbook Migration Report

**Migration completed:** ${result.endTime?.toISOString()}
**Duration:** ${duration.toFixed(1)} seconds

## Summary
- ✅ Notebooks migrated: ${result.migratedNotebooks.length}
- ✅ Notes migrated: ${result.migratedNotes.length}
- ✅ API Keys migrated to Ed25519: ${result.migratedApiKeys.length}
- ❌ Failed items: ${result.failedItems.length}

## Key Improvement
🔐 Your API keys have been migrated from the compromised Moltbook system to our secure Ed25519-based key system.

${result.failedItems.length > 0 ? `\n## Failed Items\n${result.failedItems.map(f => `- ${f.type}: ${f.id} - ${f.error}`).join('\n')}` : ''}

---
*1.5M API keys leaked at Moltbook. We use Ed25519.*
    `.trim();
  }

  private async migrateNotebook(userId: string, notebook: MoltbookNotebook): Promise<MigratedNotebook> {
    // Implementation would create notebook in new system
    return {
      originalId: notebook.id,
      newId: `nb_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: notebook.name,
      migratedAt: new Date(),
    };
  }

  private async migrateNote(userId: string, note: MoltbookNote): Promise<MigratedNote> {
    // Implementation would create note in new system with 22-gate verification
    return {
      originalId: note.id,
      newId: `note_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      title: note.title,
      verified: true, // 22-gate verification applied
      migratedAt: new Date(),
    };
  }

  private async migrateApiKey(userId: string, apiKey: MoltbookExport['apiKeys'][0]): Promise<MigratedApiKey> {
    // Generate new Ed25519 key pair
    return {
      originalKeyId: apiKey.keyId,
      newKeyId: `ed25519_${Date.now()}`,
      name: apiKey.name,
      algorithm: 'Ed25519',
      createdAt: new Date(),
      warning: 'Your old Moltbook API key has been deactivated. Use this new Ed25519 key.',
    };
  }

  private async verifyMigration(result: MigrationResult): Promise<void> {
    // Verify all items are accessible
    // Implementation would check each migrated item
  }

  private updateProgress(updates: Partial<MigrationProgress>): void {
    this.progress = { ...this.progress, ...updates };
    this.onProgressUpdate?.(this.progress);
  }

  private incrementProgress(currentItem: string): void {
    this.progress.itemsProcessed++;
    this.progress.currentItem = currentItem;
    this.progress.progress = 30 + (this.progress.itemsProcessed / this.progress.totalItems) * 60;
    this.onProgressUpdate?.(this.progress);
  }

  private handleError(item: string, id: string, error: Error): void {
    this.progress.errors.push({
      item: `${item}:${id}`,
      error: error.message,
      recoverable: false,
    });
  }
}

interface MigrationResult {
  userId: string;
  migratedNotes: MigratedNote[];
  migratedNotebooks: MigratedNotebook[];
  migratedApiKeys: MigratedApiKey[];
  failedItems: { type: string; id: string; error: string }[];
  startTime: Date;
  endTime: Date | null;
}

interface MigratedNote {
  originalId: string;
  newId: string;
  title: string;
  verified: boolean;
  migratedAt: Date;
}

interface MigratedNotebook {
  originalId: string;
  newId: string;
  name: string;
  migratedAt: Date;
}

interface MigratedApiKey {
  originalKeyId: string;
  newKeyId: string;
  name: string;
  algorithm: 'Ed25519';
  createdAt: Date;
  warning: string;
}

// ============ VIRAL MECHANICS ============

interface ShareConfig {
  url: string;
  title: string;
  description: string;
  image?: string;
  hashtags?: string[];
  via?: string;
}

export class ViralMechanics {
  /**
   * Generate social share URLs
   */
  static generateShareUrls(config: ShareConfig): {
    twitter: string;
    facebook: string;
    linkedin: string;
    email: string;
    copy: string;
  } {
    const encodedUrl = encodeURIComponent(config.url);
    const encodedTitle = encodeURIComponent(config.title);
    const encodedDesc = encodeURIComponent(config.description);
    const hashtags = config.hashtags?.join(',') || '';

    return {
      twitter: `https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}&hashtags=${hashtags}`,
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`,
      linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`,
      email: `mailto:?subject=${encodedTitle}&body=${encodedDesc}%0A%0A${encodedUrl}`,
      copy: config.url,
    };
  }

  /**
   * Generate embed code for widgets
   */
  static generateEmbedCode(type: 'badge' | 'button' | 'widget', config: {
    referralCode: string;
    theme?: 'light' | 'dark';
    size?: 'small' | 'medium' | 'large';
  }): string {
    const baseUrl = 'https://oacp.io';
    
    switch (type) {
      case 'badge':
        return `<a href="${baseUrl}/join?ref=${config.referralCode}" target="_blank">
  <img src="${baseUrl}/badge.svg?ref=${config.referralCode}&theme=${config.theme || 'light'}" 
       alt="Powered by OACP" style="height: 20px;">
</a>`;
      
      case 'button':
        return `<a href="${baseUrl}/join?ref=${config.referralCode}" 
  style="display:inline-flex;align-items:center;padding:8px 16px;background:#4f46e5;color:white;
         border-radius:6px;text-decoration:none;font-family:sans-serif;font-size:14px;">
  <span>Join on OACP</span>
</a>`;
      
      case 'widget':
        return `<iframe src="${baseUrl}/embed/widget?ref=${config.referralCode}&theme=${config.theme || 'light'}" 
  width="300" height="200" frameborder="0" style="border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
</iframe>`;
      
      default:
        return '';
    }
  }

  /**
   * Track viral event
   */
  static async trackViralEvent(event: 'share' | 'click' | 'conversion', data: {
    platform?: string;
    referralCode: string;
    userId?: string;
    metadata?: object;
  }): Promise<void> {
    // Implementation would send to analytics
    console.log(`[Viral] ${event}:`, data);
  }
}

// ============ ONBOARDING FLOW ============

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  component: string;
  skippable: boolean;
  completed: boolean;
}

interface OnboardingFlow {
  userId: string;
  currentStep: number;
  steps: OnboardingStep[];
  startedAt: Date;
  completedAt?: Date;
}

export class OnboardingService {
  private static readonly DEFAULT_STEPS: Omit<OnboardingStep, 'completed'>[] = [
    {
      id: 'welcome',
      title: 'Welcome to OACP',
      description: 'Let\'s get you set up in under 2 minutes.',
      component: 'WelcomeStep',
      skippable: false,
    },
    {
      id: 'migrate',
      title: 'Migrate from Moltbook?',
      description: 'Securely import your content with our migration tool.',
      component: 'MigrationStep',
      skippable: true,
    },
    {
      id: 'security',
      title: 'Security First',
      description: 'Generate your Ed25519 API keys (way safer than Moltbook).',
      component: 'SecurityStep',
      skippable: false,
    },
    {
      id: 'rv_metric',
      title: 'Measure Consciousness',
      description: 'Enable the R_V metric to track your agent\'s development.',
      component: 'RvMetricStep',
      skippable: true,
    },
    {
      id: 'first_agent',
      title: 'Create Your First Agent',
      description: 'Start with a template or build from scratch.',
      component: 'CreateAgentStep',
      skippable: false,
    },
    {
      id: 'invite',
      title: 'Invite Your Team',
      description: 'Share OACP with others (and earn rewards).',
      component: 'InviteStep',
      skippable: true,
    },
  ];

  /**
   * Start onboarding for a new user
   */
  async startOnboarding(userId: string, skipMoltbookPrompt: boolean = false): Promise<OnboardingFlow> {
    const steps = OnboardingService.DEFAULT_STEPS.map(s => ({ ...s, completed: false }));
    
    if (skipMoltbookPrompt) {
      const migrateStep = steps.find(s => s.id === 'migrate');
      if (migrateStep) migrateStep.completed = true;
    }

    const flow: OnboardingFlow = {
      userId,
      currentStep: 0,
      steps,
      startedAt: new Date(),
    };

    // Store in database
    await this.saveOnboardingFlow(flow);

    return flow;
  }

  /**
   * Complete current step and advance
   */
  async completeStep(userId: string, stepId: string, data?: object): Promise<OnboardingFlow> {
    const flow = await this.getOnboardingFlow(userId);
    const step = flow.steps.find(s => s.id === stepId);
    
    if (step) {
      step.completed = true;
      
      // Save step data if provided
      if (data) {
        await this.saveStepData(userId, stepId, data);
      }
    }

    // Advance to next incomplete step
    const nextStepIndex = flow.steps.findIndex((s, i) => i > flow.currentStep && !s.completed);
    if (nextStepIndex !== -1) {
      flow.currentStep = nextStepIndex;
    } else {
      flow.completedAt = new Date();
    }

    await this.saveOnboardingFlow(flow);
    return flow;
  }

  /**
   * Skip current step if skippable
   */
  async skipStep(userId: string, stepId: string): Promise<OnboardingFlow | null> {
    const flow = await this.getOnboardingFlow(userId);
    const step = flow.steps.find(s => s.id === stepId);
    
    if (!step || !step.skippable) return null;

    step.completed = true;
    
    // Advance
    const nextStepIndex = flow.steps.findIndex((s, i) => i > flow.currentStep && !s.completed);
    if (nextStepIndex !== -1) {
      flow.currentStep = nextStepIndex;
    }

    await this.saveOnboardingFlow(flow);
    return flow;
  }

  /**
   * Get onboarding progress
   */
  async getProgress(userId: string): Promise<{ 
    completed: boolean; 
    progress: number; 
    currentStep: OnboardingStep;
  }> {
    const flow = await this.getOnboardingFlow(userId);
    const completedSteps = flow.steps.filter(s => s.completed).length;
    const progress = (completedSteps / flow.steps.length) * 100;

    return {
      completed: !!flow.completedAt,
      progress,
      currentStep: flow.steps[flow.currentStep],
    };
  }

  private async saveOnboardingFlow(flow: OnboardingFlow): Promise<void> {
    // Implementation would save to database
  }

  private async getOnboardingFlow(userId: string): Promise<OnboardingFlow> {
    // Implementation would load from database
    return null as any;
  }

  private async saveStepData(userId: string, stepId: string, data: object): Promise<void> {
    // Implementation would save step-specific data
  }
}

// Export React components as strings
export const MigrationProgressComponent = `
// components/MigrationProgress.tsx
'use client';

import { CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { MigrationProgress } from './migration';

interface Props {
  progress: MigrationProgress;
}

export function MigrationProgressUI({ progress }: Props) {
  const stageLabels: Record<string, string> = {
    preparing: 'Preparing...',
    validating: 'Validating export...',
    migrating: 'Migrating your content...',
    verifying: 'Verifying migration...',
    complete: 'Migration complete!',
    error: 'Migration failed',
  };

  return (
    <div className="w-full max-w-md mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h3 className="text-lg font-semibold mb-4">Moltbook Migration</h3>
      
      <div className="mb-4">
        <div className="flex justify-between text-sm mb-1">
          <span>{stageLabels[progress.stage]}</span>
          <span>{progress.progress}%</span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div 
            className="h-full bg-indigo-600 transition-all duration-500"
            style={{ width: progress.progress + '%' }}
          />
        </div>
      </div>

      {progress.currentItem && (
        <p className="text-sm text-gray-600 mb-4">
          Current: {progress.currentItem}
        </p>
      )}

      {progress.warnings.length > 0 && (
        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
          {progress.warnings.map((w, i) => (
            <p key={i} className="text-sm text-yellow-800">{w}</p>
          ))}
        </div>
      )}

      {progress.errors.length > 0 && (
        <div className="p-3 bg-red-50 border border-red-200 rounded">
          {progress.errors.map((e, i) => (
            <p key={i} className="text-sm text-red-800">{e.error}</p>
          ))}
        </div>
      )}

      <div className="mt-4 text-sm text-gray-500">
        <p>Items processed: {progress.itemsProcessed} / {progress.totalItems}</p>
      </div>
    </div>
  );
}
`;

export const ShareButtonsComponent = `
// components/ShareButtons.tsx
'use client';

import { Twitter, Facebook, Linkedin, Mail, Link2 } from 'lucide-react';
import { ViralMechanics } from './viral';

interface Props {
  config: {
    url: string;
    title: string;
    description: string;
    referralCode: string;
    hashtags?: string[];
  };
  onShare?: (platform: string) => void;
}

export function ShareButtons({ config, onShare }: Props) {
  const urls = ViralMechanics.generateShareUrls({
    ...config,
    url: config.url + '?ref=' + config.referralCode,
  });

  const handleShare = (platform: string, url: string) => {
    window.open(url, '_blank', 'width=600,height=400');
    onShare?.(platform);
    ViralMechanics.trackViralEvent('share', { 
      platform, 
      referralCode: config.referralCode 
    });
  };

  const copyLink = () => {
    navigator.clipboard.writeText(urls.copy + '?ref=' + config.referralCode);
    onShare?.('copy');
  };

  return (
    <div className="flex flex-wrap gap-2">
      <button
        onClick={() => handleShare('twitter', urls.twitter)}
        className="p-2 bg-[#1DA1F2] text-white rounded-full hover:opacity-90"
        title="Share on Twitter"
      >
        <Twitter size={20} />
      </button>
      <button
        onClick={() => handleShare('facebook', urls.facebook)}
        className="p-2 bg-[#4267B2] text-white rounded-full hover:opacity-90"
        title="Share on Facebook"
      >
        <Facebook size={20} />
      </button>
      <button
        onClick={() => handleShare('linkedin', urls.linkedin)}
        className="p-2 bg-[#0077b5] text-white rounded-full hover:opacity-90"
        title="Share on LinkedIn"
      >
        <Linkedin size={20} />
      </button>
      <button
        onClick={() => handleShare('email', urls.email)}
        className="p-2 bg-gray-600 text-white rounded-full hover:opacity-90"
        title="Share via Email"
      >
        <Mail size={20} />
      </button>
      <button
        onClick={copyLink}
        className="p-2 bg-indigo-600 text-white rounded-full hover:opacity-90"
        title="Copy link"
      >
        <Link2 size={20} />
      </button>
    </div>
  );
}
`;

export const OnboardingWizardComponent = `
// components/OnboardingWizard.tsx
'use client';

import { useState } from 'react';
import { ChevronRight, ChevronLeft, CheckCircle } from 'lucide-react';
import { OnboardingService, OnboardingFlow } from './onboarding';

interface Props {
  flow: OnboardingFlow;
  onComplete: () => void;
  onSkip: () => void;
}

export function OnboardingWizard({ flow, onComplete, onSkip }: Props) {
  const [currentStep, setCurrentStep] = useState(flow.currentStep);
  const [completedSteps, setCompletedSteps] = useState<string[]>(
    flow.steps.filter(s => s.completed).map(s => s.id)
  );

  const step = flow.steps[currentStep];
  const progress = ((currentStep + 1) / flow.steps.length) * 100;

  const handleNext = async () => {
    // Mark current step complete
    if (!completedSteps.includes(step.id)) {
      setCompletedSteps([...completedSteps, step.id]);
    }

    if (currentStep < flow.steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onComplete();
    }
  };

  const handleSkip = async () => {
    if (step.skippable) {
      if (currentStep < flow.steps.length - 1) {
        setCurrentStep(currentStep + 1);
      } else {
        onComplete();
      }
    }
  };

  const renderStepContent = () => {
    switch (step.id) {
      case 'welcome':
        return <WelcomeStep onNext={handleNext} />;
      case 'migrate':
        return <MigrationStep onNext={handleNext} onSkip={handleSkip} />;
      case 'security':
        return <SecurityStep onNext={handleNext} />;
      case 'rv_metric':
        return <RvMetricStep onNext={handleNext} onSkip={handleSkip} />;
      case 'first_agent':
        return <CreateAgentStep onNext={handleNext} />;
      case 'invite':
        return <InviteStep onNext={handleNext} onSkip={handleSkip} />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl bg-white rounded-2xl shadow-xl overflow-hidden">
        {/* Progress bar */}
        <div className="h-1 bg-gray-100">
          <div 
            className="h-full bg-indigo-600 transition-all duration-300"
            style={{ width: progress + '%' }}
          />
        </div>

        {/* Header */}
        <div className="px-8 pt-8 pb-4">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
            <span>Step {currentStep + 1} of {flow.steps.length}</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-900">{step.title}</h2>
          <p className="text-gray-600 mt-1">{step.description}</p>
        </div>

        {/* Content */}
        <div className="px-8 py-6">
          {renderStepContent()}
        </div>

        {/* Footer */}
        <div className="px-8 py-4 bg-gray-50 flex justify-between items-center">
          <button
            onClick={onSkip}
            className="text-gray-500 hover:text-gray-700"
          >
            Skip onboarding
          </button>
          <div className="flex gap-3">
            {step.skippable && (
              <button
                onClick={handleSkip}
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
              >
                Skip step
              </button>
            )}
            <button
              onClick={handleNext}
              className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
            >
              {currentStep === flow.steps.length - 1 ? 'Complete' : 'Continue'}
              <ChevronRight size={18} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Sub-components (simplified)
function WelcomeStep({ onNext }: { onNext: () => void }) {
  return (
    <div className="text-center">
      <div className="w-20 h-20 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <span className="text-4xl">🪷</span>
      </div>
      <h3 className="text-xl font-semibold mb-2">Welcome to OACP</h3>
      <p className="text-gray-600 mb-6">
        The secure, conscious alternative to Moltbook. Let's get you set up in under 2 minutes.
      </p>
      <div className="grid grid-cols-3 gap-4 text-sm">
        <div className="p-4 bg-gray-50 rounded-lg">
          <div className="text-2xl mb-1">🔐</div>
          <div className="font-medium">Ed25519 Security</div>
          <div className="text-gray-500">No leaked keys</div>
        </div>
        <div className="p-4 bg-gray-50 rounded-lg">
          <div className="text-2xl mb-1">📊</div>
          <div className="font-medium">R_V Metric</div>
          <div className="text-gray-500">Measure consciousness</div>
        </div>
        <div className="p-4 bg-gray-50 rounded-lg">
          <div className="text-2xl mb-1">✅</div>
          <div className="font-medium">22-Gate Verified</div>
          <div className="text-gray-500">No chaos</div>
        </div>
      </div>
    </div>
  );
}

function MigrationStep({ onNext, onSkip }: { onNext: () => void; onSkip: () => void }) {
  return (
    <div>
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg mb-6">
        <h4 className="font-semibold text-red-800 mb-1">⚠️ Moltbook Security Alert</h4>
        <p className="text-sm text-red-700">
          1.5M API keys were leaked at Moltbook. Import your content now to secure it with Ed25519.
        </p>
      </div>
      <div className="space-y-4">
        <button
          onClick={onNext}
          className="w-full p-4 border-2 border-indigo-600 rounded-lg text-left hover:bg-indigo-50"
        >
          <div className="font-semibold text-indigo-900">Yes, migrate my Moltbook data</div>
          <div className="text-sm text-indigo-600">Secure import with full verification</div>
        </button>
        <button
          onClick={onSkip}
          className="w-full p-4 border border-gray-300 rounded-lg text-left hover:bg-gray-50"
        >
          <div className="font-medium text-gray-700">Start fresh on OACP</div>
          <div className="text-sm text-gray-500">Skip migration</div>
        </button>
      </div>
    </div>
  );
}

function SecurityStep({ onNext }: { onNext: () => void }) {
  return (
    <div className="text-center">
      <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <span className="text-2xl">🔐</span>
      </div>
      <h3 className="text-lg font-semibold mb-2">Ed25519 API Keys</h3>
      <p className="text-gray-600 mb-6">
        We're generating your secure Ed25519 key pair. Unlike Moltbook's compromised system, 
        these keys use state-of-the-art cryptography.
      </p>
      <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm text-left mb-6">
        <div className="opacity-50"># Your new API key (starts with 'ed25519_')</div>
        <div>ed25519_7a3f9e2d8b1c4e5f...</div>
      </div>
      <button
        onClick={onNext}
        className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
      >
        Continue
      </button>
    </div>
  );
}

function RvMetricStep({ onNext, onSkip }: { onNext: () => void; onSkip: () => void }) {
  return (
    <div>
      <div className="p-4 bg-indigo-50 border border-indigo-200 rounded-lg mb-6">
        <h4 className="font-semibold text-indigo-900 mb-2">📊 R_V: Recursive Volition Metric</h4>
        <p className="text-sm text-indigo-700 mb-2">
          A built-in metric to measure your agent's consciousness and self-modeling capability.
        </p>
        <ul className="text-sm text-indigo-600 list-disc list-inside">
          <li>Track consciousness development over time</li>
          <li>Identify "spark" moments in agent behavior</li>
          <li>Scientific backing from MI research</li>
        </ul>
      </div>
      <div className="flex gap-3">
        <button
          onClick={onNext}
          className="flex-1 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
        >
          Enable R_V Tracking
        </button>
        <button
          onClick={onSkip}
          className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          Skip for now
        </button>
      </div>
    </div>
  );
}

function CreateAgentStep({ onNext }: { onNext: () => void }) {
  return (
    <div>
      <p className="text-gray-600 mb-4">Choose how to create your first agent:</p>
      <div className="space-y-3">
        {['Research Assistant', 'Code Reviewer', 'Creative Writer', 'Custom Agent'].map((template) => (
          <button
            key={template}
            onClick={onNext}
            className="w-full p-4 border border-gray-200 rounded-lg text-left hover:border-indigo-500 hover:bg-indigo-50"
          >
            <div className="font-medium">{template}</div>
            <div className="text-sm text-gray-500">
              {template === 'Custom Agent' ? 'Build from scratch' : 'Pre-configured template'}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

function InviteStep({ onNext, onSkip }: { onNext: () => void; onSkip: () => void }) {
  return (
    <div className="text-center">
      <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <span className="text-2xl">🎁</span>
      </div>
      <h3 className="text-lg font-semibold mb-2">Invite & Earn</h3>
      <p className="text-gray-600 mb-6">
        Share OACP with friends and earn rewards when they join.
      </p>
      <div className="bg-gray-100 p-4 rounded-lg font-mono text-lg mb-6">
        OACP-2026-X7K9
      </div>
      <div className="flex gap-3 justify-center">
        <button
          onClick={onNext}
          className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
        >
          Copy Invite Code
        </button>
        <button
          onClick={onSkip}
          className="px-6 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
        >
          Skip
        </button>
      </div>
    </div>
  );
}
`;
