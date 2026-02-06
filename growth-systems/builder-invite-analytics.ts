/**
 * BUILDER 1: Invite System + Analytics Dashboard
 * 
 * Requirements:
 * - Invite code generation (trackable, rate-limited)
 * - Analytics dashboard with user funnels and engagement
 */

// ============ INVITE CODE SYSTEM ============

import { createHash, randomBytes } from 'crypto';
import { Redis } from 'ioredis';

interface InviteCode {
  code: string;
  createdBy: string;
  createdAt: Date;
  expiresAt: Date | null;
  maxUses: number;
  usedCount: number;
  metadata: {
    campaign?: string;
    source?: string;
    tags?: string[];
  };
}

interface RateLimitConfig {
  maxCodesPerUser: number;
  maxCodesPerHour: number;
  maxCodesPerIP: number;
}

const DEFAULT_RATE_LIMITS: RateLimitConfig = {
  maxCodesPerUser: 10,
  maxCodesPerHour: 5,
  maxCodesPerIP: 20,
};

export class InviteCodeSystem {
  private redis: Redis;
  private rateLimits: RateLimitConfig;

  constructor(redis: Redis, rateLimits: RateLimitConfig = DEFAULT_RATE_LIMITS) {
    this.redis = redis;
    this.rateLimits = rateLimits;
  }

  /**
   * Generate a cryptographically secure invite code
   */
  async generateCode(
    userId: string,
    options: {
      expiresInHours?: number;
      maxUses?: number;
      campaign?: string;
      source?: string;
      tags?: string[];
    } = {}
  ): Promise<{ code: string; expiresAt: Date | null }> {
    // Check rate limits
    await this.checkRateLimits(userId);

    const code = this.generateSecureCode();
    const now = new Date();
    const expiresAt = options.expiresInHours
      ? new Date(now.getTime() + options.expiresInHours * 60 * 60 * 1000)
      : null;

    const inviteData: InviteCode = {
      code,
      createdBy: userId,
      createdAt: now,
      expiresAt,
      maxUses: options.maxUses || 1,
      usedCount: 0,
      metadata: {
        campaign: options.campaign,
        source: options.source,
        tags: options.tags,
      },
    };

    // Store in Redis with expiration if applicable
    const key = `invite:${code}`;
    const ttl = options.expiresInHours ? options.expiresInHours * 3600 : undefined;
    
    await this.redis.setex(key, ttl || 2592000, JSON.stringify(inviteData)); // 30 days default
    
    // Track user's codes
    await this.redis.sadd(`user:${userId}:invites`, code);
    
    // Update rate limit counters
    await this.updateRateLimits(userId);

    return { code, expiresAt };
  }

  /**
   * Validate and use an invite code
   */
  async useCode(code: string, newUserId: string): Promise<{ success: boolean; error?: string }> {
    const key = `invite:${code}`;
    const data = await this.redis.get(key);

    if (!data) {
      return { success: false, error: 'INVALID_CODE' };
    }

    const invite: InviteCode = JSON.parse(data);

    // Check expiration
    if (invite.expiresAt && new Date(invite.expiresAt) < new Date()) {
      return { success: false, error: 'CODE_EXPIRED' };
    }

    // Check usage limit
    if (invite.usedCount >= invite.maxUses) {
      return { success: false, error: 'CODE_EXHAUSTED' };
    }

    // Update usage
    invite.usedCount++;
    const ttl = await this.redis.ttl(key);
    await this.redis.setex(key, ttl, JSON.stringify(invite));

    // Track conversion
    await this.trackConversion(invite, newUserId);

    return { success: true };
  }

  /**
   * Get invite code analytics
   */
  async getCodeAnalytics(code: string): Promise<{
    code: string;
    createdAt: Date;
    expiresAt: Date | null;
    usageRate: number;
    conversions: number;
    metadata: object;
  } | null> {
    const data = await this.redis.get(`invite:${code}`);
    if (!data) return null;

    const invite: InviteCode = JSON.parse(data);
    const conversions = parseInt(await this.redis.get(`conversions:${code}`) || '0');

    return {
      code: invite.code,
      createdAt: invite.createdAt,
      expiresAt: invite.expiresAt,
      usageRate: invite.usedCount / invite.maxUses,
      conversions,
      metadata: invite.metadata,
    };
  }

  private generateSecureCode(): string {
    // Generate 8-character alphanumeric code
    return randomBytes(6).toString('base64url').slice(0, 8).toUpperCase();
  }

  private async checkRateLimits(userId: string): Promise<void> {
    const hourKey = `ratelimit:${userId}:hour`;
    const hourCount = parseInt(await this.redis.get(hourKey) || '0');
    
    if (hourCount >= this.rateLimits.maxCodesPerHour) {
      throw new Error('RATE_LIMIT_HOUR');
    }

    const userCodes = await this.redis.scard(`user:${userId}:invites`);
    if (userCodes >= this.rateLimits.maxCodesPerUser) {
      throw new Error('RATE_LIMIT_TOTAL');
    }
  }

  private async updateRateLimits(userId: string): Promise<void> {
    const hourKey = `ratelimit:${userId}:hour`;
    await this.redis.incr(hourKey);
    await this.redis.expire(hourKey, 3600);
  }

  private async trackConversion(invite: InviteCode, newUserId: string): Promise<void> {
    const conversionKey = `conversions:${invite.code}`;
    await this.redis.incr(conversionKey);
    
    // Track funnel event
    await this.redis.lpush('funnel:invite_conversions', JSON.stringify({
      code: invite.code,
      newUserId,
      campaign: invite.metadata.campaign,
      timestamp: new Date().toISOString(),
    }));
  }
}

// ============ ANALYTICS DASHBOARD ============

interface FunnelStage {
  name: string;
  count: number;
  dropOff: number;
  conversionRate: number;
}

interface EngagementMetrics {
  dau: number; // Daily Active Users
  mau: number; // Monthly Active Users
  avgSessionDuration: number;
  retention: {
    day1: number;
    day7: number;
    day30: number;
  };
}

interface UserFunnel {
  stages: FunnelStage[];
  totalUsers: number;
  conversionRate: number;
  period: string;
}

export class AnalyticsDashboard {
  private redis: Redis;

  constructor(redis: Redis) {
    this.redis = redis;
  }

  /**
   * Get user acquisition funnel
   */
  async getUserFunnel(period: 'day' | 'week' | 'month' = 'week'): Promise<UserFunnel> {
    const periodKey = `funnel:${period}`;
    
    // Stage 1: Landing Page View
    const views = parseInt(await this.redis.get(`${periodKey}:landing_view`) || '0');
    
    // Stage 2: Signup Started
    const signupsStarted = parseInt(await this.redis.get(`${periodKey}:signup_start`) || '0');
    
    // Stage 3: Invite Code Entered
    const inviteEntered = parseInt(await this.redis.get(`${periodKey}:invite_entered`) || '0');
    
    // Stage 4: Account Created
    const accountsCreated = parseInt(await this.redis.get(`${periodKey}:account_created`) || '0');
    
    // Stage 5: First Action (onboarding complete)
    const firstAction = parseInt(await this.redis.get(`${periodKey}:first_action`) || '0');
    
    // Stage 6: Active User (7-day)
    const activeUsers = parseInt(await this.redis.get(`${periodKey}:active_7d`) || '0');

    const stages: FunnelStage[] = [
      { name: 'Landing View', count: views, dropOff: 0, conversionRate: 100 },
      { 
        name: 'Signup Start', 
        count: signupsStarted, 
        dropOff: views - signupsStarted,
        conversionRate: views > 0 ? (signupsStarted / views) * 100 : 0 
      },
      { 
        name: 'Invite Entered', 
        count: inviteEntered, 
        dropOff: signupsStarted - inviteEntered,
        conversionRate: signupsStarted > 0 ? (inviteEntered / signupsStarted) * 100 : 0 
      },
      { 
        name: 'Account Created', 
        count: accountsCreated, 
        dropOff: inviteEntered - accountsCreated,
        conversionRate: inviteEntered > 0 ? (accountsCreated / inviteEntered) * 100 : 0 
      },
      { 
        name: 'First Action', 
        count: firstAction, 
        dropOff: accountsCreated - firstAction,
        conversionRate: accountsCreated > 0 ? (firstAction / accountsCreated) * 100 : 0 
      },
      { 
        name: 'Active User (7d)', 
        count: activeUsers, 
        dropOff: firstAction - activeUsers,
        conversionRate: firstAction > 0 ? (activeUsers / firstAction) * 100 : 0 
      },
    ];

    return {
      stages,
      totalUsers: activeUsers,
      conversionRate: views > 0 ? (activeUsers / views) * 100 : 0,
      period,
    };
  }

  /**
   * Get engagement metrics
   */
  async getEngagementMetrics(): Promise<EngagementMetrics> {
    const today = new Date().toISOString().split('T')[0];
    
    return {
      dau: parseInt(await this.redis.get(`dau:${today}`) || '0'),
      mau: parseInt(await this.redis.get('mau:current') || '0'),
      avgSessionDuration: parseFloat(await this.redis.get('avg_session_duration') || '0'),
      retention: {
        day1: parseFloat(await this.redis.get('retention:day1') || '0'),
        day7: parseFloat(await this.redis.get('retention:day7') || '0'),
        day30: parseFloat(await this.redis.get('retention:day30') || '0'),
      },
    };
  }

  /**
   * Track an event
   */
  async trackEvent(eventName: string, userId: string, metadata?: object): Promise<void> {
    const timestamp = new Date().toISOString();
    const eventData = JSON.stringify({
      event: eventName,
      userId,
      timestamp,
      metadata,
    });

    // Store in time-series list
    await this.redis.lpush(`events:${eventName}`, eventData);
    await this.redis.ltrim(`events:${eventName}`, 0, 9999); // Keep last 10k

    // Update counters
    const today = timestamp.split('T')[0];
    await this.redis.incr(`events:${eventName}:count:${today}`);
  }

  /**
   * Export analytics data
   */
  async exportData(startDate: Date, endDate: Date): Promise<object> {
    // Implementation for data export
    return {
      period: { start: startDate, end: endDate },
      events: await this.getEventsInRange(startDate, endDate),
      funnels: await this.getUserFunnel('week'),
      engagement: await this.getEngagementMetrics(),
    };
  }

  private async getEventsInRange(startDate: Date, endDate: Date): Promise<any[]> {
    // Placeholder - would query time-series DB
    return [];
  }
}

// ============ REACT COMPONENTS ============

// components/InviteCodeGenerator.tsx
export const InviteCodeGenerator = `
'use client';

import { useState } from 'react';
import { Copy, RefreshCw, Share2 } from 'lucide-react';

interface InviteCodeGeneratorProps {
  onGenerate: (options: { campaign?: string; expiresInHours?: number }) => Promise<string>;
}

export function InviteCodeGenerator({ onGenerate }: InviteCodeGeneratorProps) {
  const [code, setCode] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [campaign, setCampaign] = useState('');

  const generate = async () => {
    setLoading(true);
    try {
      const newCode = await onGenerate({ 
        campaign: campaign || undefined,
        expiresInHours: 168 // 7 days
      });
      setCode(newCode);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-lg border border-gray-200">
      <h3 className="text-lg font-semibold mb-4">Generate Invite Code</h3>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Campaign (optional)
          </label>
          <input
            type="text"
            value={campaign}
            onChange={(e) => setCampaign(e.target.value)}
            placeholder="e.g., twitter_feb_2026"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        {code && (
          <div className="p-4 bg-indigo-50 rounded-lg border-2 border-indigo-200">
            <div className="flex items-center justify-between">
              <code className="text-2xl font-bold text-indigo-700 tracking-wider">
                {code}
              </code>
              <div className="flex gap-2">
                <button
                  onClick={copyToClipboard}
                  className="p-2 text-indigo-600 hover:bg-indigo-100 rounded-md"
                  title="Copy to clipboard"
                >
                  <Copy size={20} />
                </button>
                <button
                  onClick={() => {}}
                  className="p-2 text-indigo-600 hover:bg-indigo-100 rounded-md"
                  title="Share"
                >
                  <Share2 size={20} />
                </button>
              </div>
            </div>
            {copied && (
              <p className="text-sm text-green-600 mt-2">Copied to clipboard!</p>
            )}
          </div>
        )}

        <button
          onClick={generate}
          disabled={loading}
          className="w-full py-2 px-4 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 
                     disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {loading && <RefreshCw className="animate-spin" size={18} />}
          {code ? 'Generate New Code' : 'Generate Invite Code'}
        </button>
      </div>
    </div>
  );
}
`;

// components/FunnelChart.tsx
export const FunnelChart = `
'use client';

import { UserFunnel } from './analytics';

interface FunnelChartProps {
  funnel: UserFunnel;
}

export function FunnelChart({ funnel }: FunnelChartProps) {
  const maxCount = Math.max(...funnel.stages.map(s => s.count));

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">User Acquisition Funnel</h3>
      <p className="text-sm text-gray-500 mb-6">Period: {funnel.period}</p>
      
      <div className="space-y-3">
        {funnel.stages.map((stage, index) => {
          const width = maxCount > 0 ? (stage.count / maxCount) * 100 : 0;
          
          return (
            <div key={stage.name} className="relative">
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="font-medium">{stage.name}</span>
                <span className="text-gray-600">
                  {stage.count.toLocaleString()} 
                  <span className="text-gray-400 ml-1">
                    ({stage.conversionRate.toFixed(1)}%)
                  </span>
                </span>
              </div>
              <div className="h-8 bg-gray-100 rounded overflow-hidden">
                <div
                  className="h-full bg-indigo-500 transition-all duration-500 flex items-center justify-end pr-2"
                  style={{ width: width + '%' }}
                >
                  {width > 20 && (
                    <span className="text-white text-xs font-medium">
                      {stage.count}
                    </span>
                  )}
                </div>
              </div>
              {index > 0 && stage.dropOff > 0 && (
                <p className="text-xs text-red-500 mt-1">
                  ↓ {stage.dropOff.toLocaleString()} dropped off
                </p>
              )}
            </div>
          );
        })}
      </div>

      <div className="mt-6 pt-4 border-t">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Overall Conversion</span>
          <span className="text-2xl font-bold text-indigo-600">
            {funnel.conversionRate.toFixed(2)}%
          </span>
        </div>
      </div>
    </div>
  );
}
`;

// Export all
export default { InviteCodeSystem, AnalyticsDashboard };
