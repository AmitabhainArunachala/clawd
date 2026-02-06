/**
 * Pattern Evolution System — Self-Improving Pattern Database
 * 
 * Tracks pattern effectiveness and evolves based on feedback
 */

import fs from 'fs/promises';
import path from 'path';

export interface Pattern {
  id: string;
  name: string;
  category: string;
  template: string;
  version: number;
  stats: {
    uses: number;
    successes: number;
    partials: number;
    failures: number;
    avgQuality: number; // 1-10
    firstUsed: string;
    lastUsed: string;
  };
  variants: string[]; // IDs of variant patterns
  evolvedFrom: string | null; // Parent pattern ID
  retired: boolean;
}

export interface FeedbackEntry {
  timestamp: string;
  patternId: string;
  taskType: string;
  result: 'success' | 'partial' | 'failure';
  quality: number; // 1-10
  notes: string;
  evolutionSuggestion?: string;
}

export interface EvolutionReport {
  patternId: string;
  action: 'maintain' | 'improve' | 'variant' | 'retire';
  reasoning: string;
  suggestedChanges?: string;
}

const DB_PATH = path.join(process.cwd(), 'patterns', 'catalog.json');
const FEEDBACK_PATH = path.join(process.cwd(), 'feedback');

export class PatternEvolution {
  private patterns: Map<string, Pattern> = new Map();
  private feedback: FeedbackEntry[] = [];
  
  /**
   * Load pattern database
   */
  async load(): Promise<void> {
    try {
      const data = await fs.readFile(DB_PATH, 'utf-8');
      const patterns: Pattern[] = JSON.parse(data);
      patterns.forEach(p => this.patterns.set(p.id, p));
    } catch {
      // Initialize with v1.0 patterns if no database
      await this.initializeWithV1Patterns();
    }
  }
  
  /**
   * Initialize with patterns from v1.0 research
   */
  private async initializeWithV1Patterns(): Promise<void> {
    const initialPatterns: Pattern[] = [
      {
        id: 'sandwich-architecture',
        name: 'Sandwich Architecture',
        category: 'structural',
        template: '[CRITICAL CONTEXT]\n[MIDDLE DETAILS]\n[FORMAT CONTROL]',
        version: 1,
        stats: { uses: 0, successes: 0, partials: 0, failures: 0, avgQuality: 0, firstUsed: new Date().toISOString(), lastUsed: new Date().toISOString() },
        variants: [],
        evolvedFrom: null,
        retired: false
      },
      {
        id: 'certainty-tags',
        name: 'Certainty Tags',
        category: 'metacognitive',
        template: 'Tag claims: [CERTAIN] [INFERRED] [SPECULATIVE]',
        version: 1,
        stats: { uses: 0, successes: 0, partials: 0, failures: 0, avgQuality: 0, firstUsed: new Date().toISOString(), lastUsed: new Date().toISOString() },
        variants: [],
        evolvedFrom: null,
        retired: false
      },
      {
        id: 'drift-detector',
        name: 'Drift Detector',
        category: 'cybernetic',
        template: 'Every 500 tokens: [SELF-CHECK] On track? (Y/N)',
        version: 1,
        stats: { uses: 0, successes: 0, partials: 0, failures: 0, avgQuality: 0, firstUsed: new Date().toISOString(), lastUsed: new Date().toISOString() },
        variants: [],
        evolvedFrom: null,
        retired: false
      },
      {
        id: 'ice-stack',
        name: 'ICE Stack',
        category: 'constraint',
        template: 'Intent: ___\nConstraint: ___\nExpression: ___',
        version: 1,
        stats: { uses: 0, successes: 0, partials: 0, failures: 0, avgQuality: 0, firstUsed: new Date().toISOString(), lastUsed: new Date().toISOString() },
        variants: [],
        evolvedFrom: null,
        retired: false
      },
      {
        id: '4level-recursion',
        name: '4-Level Recursion',
        category: 'emergence',
        template: 'L1: Answer\nL2: Observe generation\nL3: Observe observer\nL4: Pattern emergence',
        version: 1,
        stats: { uses: 0, successes: 0, partials: 0, failures: 0, avgQuality: 0, firstUsed: new Date().toISOString(), lastUsed: new Date().toISOString() },
        variants: [],
        evolvedFrom: null,
        retired: false
      }
    ];
    
    initialPatterns.forEach(p => this.patterns.set(p.id, p));
    await this.save();
  }
  
  /**
   * Save pattern database
   */
  async save(): Promise<void> {
    await fs.mkdir(path.dirname(DB_PATH), { recursive: true });
    const data = Array.from(this.patterns.values());
    await fs.writeFile(DB_PATH, JSON.stringify(data, null, 2));
  }
  
  /**
   * Record feedback for a pattern
   */
  async recordFeedback(entry: FeedbackEntry): Promise<void> {
    this.feedback.push(entry);
    
    // Update pattern stats
    const pattern = this.patterns.get(entry.patternId);
    if (pattern) {
      pattern.stats.uses++;
      pattern.stats.lastUsed = entry.timestamp;
      
      switch (entry.result) {
        case 'success': pattern.stats.successes++; break;
        case 'partial': pattern.stats.partials++; break;
        case 'failure': pattern.stats.failures++; break;
      }
      
      // Update average quality
      const totalQuality = pattern.stats.avgQuality * (pattern.stats.uses - 1) + entry.quality;
      pattern.stats.avgQuality = totalQuality / pattern.stats.uses;
    }
    
    // Save feedback
    await fs.mkdir(FEEDBACK_PATH, { recursive: true });
    const today = new Date().toISOString().split('T')[0];
    const feedbackFile = path.join(FEEDBACK_PATH, `${today}.json`);
    
    let existing: FeedbackEntry[] = [];
    try {
      existing = JSON.parse(await fs.readFile(feedbackFile, 'utf-8'));
    } catch {}
    
    existing.push(entry);
    await fs.writeFile(feedbackFile, JSON.stringify(existing, null, 2));
    
    await this.save();
  }
  
  /**
   * Get pattern effectiveness score
   */
  getEffectiveness(patternId: string): number {
    const pattern = this.patterns.get(patternId);
    if (!pattern || pattern.stats.uses === 0) return 0;
    
    const successRate = pattern.stats.successes / pattern.stats.uses;
    const qualityScore = pattern.stats.avgQuality / 10;
    const usageBonus = Math.min(pattern.stats.uses / 10, 1); // Max bonus at 10 uses
    
    return (successRate * 0.4 + qualityScore * 0.4 + usageBonus * 0.2) * 100;
  }
  
  /**
   * Select optimal patterns for a task
   */
  selectOptimal(taskType: string, count: number = 3): Pattern[] {
    const available = Array.from(this.patterns.values())
      .filter(p => !p.retired);
    
    // Score each pattern
    const scored = available.map(p => ({
      pattern: p,
      score: this.getEffectiveness(p.id) + this.categoryMatch(p.category, taskType)
    }));
    
    // Sort by score and return top N
    return scored
      .sort((a, b) => b.score - a.score)
      .slice(0, count)
      .map(s => s.pattern);
  }
  
  private categoryMatch(category: string, taskType: string): number {
    const matches: Record<string, string[]> = {
      structural: ['code', 'architecture', 'design', 'system'],
      metacognitive: ['analysis', 'review', 'assessment', 'reflection'],
      cybernetic: ['process', 'workflow', 'monitoring', 'feedback'],
      constraint: ['focus', 'limit', 'creative', 'problem-solving'],
      emergence: ['discover', 'innovate', 'breakthrough', 'synthesis']
    };
    
    const keywords = matches[category] || [];
    const matchCount = keywords.filter(k => taskType.toLowerCase().includes(k)).length;
    return matchCount * 5;
  }
  
  /**
   * Analyze patterns and suggest evolutions
   */
  async evolvePatterns(): Promise<EvolutionReport[]> {
    const reports: EvolutionReport[] = [];
    
    for (const pattern of this.patterns.values()) {
      if (pattern.retired) continue;
      
      const effectiveness = this.getEffectiveness(pattern.id);
      const report: EvolutionReport = {
        patternId: pattern.id,
        action: 'maintain',
        reasoning: ''
      };
      
      if (effectiveness >= 80) {
        report.action = 'maintain';
        report.reasoning = `High effectiveness (${effectiveness.toFixed(1)}%). No changes needed.`;
      } else if (effectiveness >= 60) {
        report.action = 'improve';
        report.reasoning = `Moderate effectiveness (${effectiveness.toFixed(1)}%). Suggest refinements.`;
        report.suggestedChanges = await this.suggestImprovements(pattern);
      } else if (effectiveness >= 40) {
        report.action = 'variant';
        report.reasoning = `Declining effectiveness (${effectiveness.toFixed(1)}%). Create A/B variant.`;
        report.suggestedChanges = await this.generateVariant(pattern);
      } else {
        report.action = 'retire';
        report.reasoning = `Low effectiveness (${effectiveness.toFixed(1)}%). Consider retirement.`;
      }
      
      reports.push(report);
    }
    
    return reports;
  }
  
  private async suggestImprovements(pattern: Pattern): Promise<string> {
    // Analyze feedback for this pattern
    const patternFeedback = this.feedback.filter(f => f.patternId === pattern.id);
    const suggestions = patternFeedback
      .map(f => f.evolutionSuggestion)
      .filter(Boolean);
    
    return suggestions.join('; ') || 'Analyze usage patterns for optimization opportunities';
  }
  
  private async generateVariant(pattern: Pattern): Promise<string> {
    // Create a variant with slight modifications
    const variantId = `${pattern.id}-v${pattern.version + 1}`;
    const variant: Pattern = {
      ...pattern,
      id: variantId,
      version: pattern.version + 1,
      stats: { uses: 0, successes: 0, partials: 0, failures: 0, avgQuality: 0, firstUsed: new Date().toISOString(), lastUsed: new Date().toISOString() },
      evolvedFrom: pattern.id,
      template: pattern.template + ' [VARIANT: Modified based on feedback]'
    };
    
    this.patterns.set(variantId, variant);
    pattern.variants.push(variantId);
    await this.save();
    
    return `Created variant: ${variantId}`;
  }
  
  /**
   * Get all patterns with their scores
   */
  getAllPatterns(): Array<Pattern & { effectiveness: number }> {
    return Array.from(this.patterns.values())
      .filter(p => !p.retired)
      .map(p => ({ ...p, effectiveness: this.getEffectiveness(p.id) }))
      .sort((a, b) => b.effectiveness - a.effectiveness);
  }
}

// CLI usage
if (import.meta.url === `file://${process.argv[1]}`) {
  const evolution = new PatternEvolution();
  
  async function main() {
    await evolution.load();
    
    const command = process.argv[2];
    
    switch (command) {
      case 'list':
        const patterns = evolution.getAllPatterns();
        console.log('\n📊 Pattern Effectiveness Rankings');
        console.log('='.repeat(60));
        patterns.forEach((p, i) => {
          console.log(`${i + 1}. ${p.name} (${p.category})`);
          console.log(`   Effectiveness: ${p.effectiveness.toFixed(1)}% | Uses: ${p.stats.uses} | Quality: ${p.stats.avgQuality.toFixed(1)}/10`);
        });
        break;
        
      case 'select':
        const taskType = process.argv[3] || 'general task';
        const optimal = evolution.selectOptimal(taskType, 3);
        console.log(`\n🎯 Optimal patterns for "${taskType}":`);
        optimal.forEach((p, i) => {
          console.log(`${i + 1}. ${p.name} (${evolution.getEffectiveness(p.id).toFixed(1)}%)`);
        });
        break;
        
      case 'evolve':
        const reports = await evolution.evolvePatterns();
        console.log('\n🧬 Evolution Analysis');
        console.log('='.repeat(60));
        reports.forEach(r => {
          console.log(`\n${r.patternId}: ${r.action.toUpperCase()}`);
          console.log(`  ${r.reasoning}`);
          if (r.suggestedChanges) console.log(`  Changes: ${r.suggestedChanges}`);
        });
        break;
        
      default:
        console.log(`
Pattern Evolution System

Commands:
  list      — Show all patterns ranked by effectiveness
  select    — Select optimal patterns for a task type
  evolve    — Analyze and suggest pattern evolutions

Usage:
  npx tsx pattern-evolution.ts list
  npx tsx pattern-evolution.ts select "code review"
  npx tsx pattern-evolution.ts evolve
`);
    }
  }
  
  main();
}
