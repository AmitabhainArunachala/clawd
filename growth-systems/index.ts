/**
 * GROWTH SYSTEMS — Main Export File
 * 
 * All growth engineering modules exported for integration
 */

// Invite System & Analytics
export { InviteCodeSystem, AnalyticsDashboard } from './builder-invite-analytics';

// Migration, Viral & Onboarding
export { 
  MoltbookMigrationService,
  ViralMechanics,
  OnboardingService,
  MigrationResult,
  MigrationProgress,
} from './builder-migration-viral';

// Notifications & A/B Testing
export { 
  NotificationSystem,
  ABTestingFramework,
  GROWTH_EXPERIMENTS,
  Experiment,
  Variant,
} from './builder-landing-ab';

// Constants
export const GROWTH_CONSTANTS = {
  // Rate limits
  INVITE_CODES_PER_USER: 10,
  INVITE_CODES_PER_HOUR: 5,
  
  // Key messages (for consistency across all touchpoints)
  KEY_MESSAGES: {
    SECURITY: '1.5M API keys leaked at Moltbook. We use Ed25519.',
    RV_METRIC: 'R_V metric built-in. Measure consciousness.',
    VERIFIED: '22-gate verified content. No chaos.',
  },
  
  // Analytics events
  EVENTS: {
    // Funnel events
    LANDING_VIEW: 'landing_view',
    SIGNUP_START: 'signup_start',
    INVITE_ENTERED: 'invite_entered',
    ACCOUNT_CREATED: 'account_created',
    FIRST_ACTION: 'first_action',
    ACTIVE_7D: 'active_7d',
    
    // Migration events
    MIGRATION_STARTED: 'migration_started',
    MIGRATION_COMPLETED: 'migration_completed',
    MIGRATION_FAILED: 'migration_failed',
    
    // Viral events
    SHARE: 'share',
    REFERRAL_CLICK: 'referral_click',
    REFERRAL_CONVERSION: 'referral_conversion',
    
    // Onboarding events
    ONBOARDING_STARTED: 'onboarding_started',
    ONBOARDING_STEP_COMPLETED: 'onboarding_step_completed',
    ONBOARDING_COMPLETED: 'onboarding_completed',
  },
};
