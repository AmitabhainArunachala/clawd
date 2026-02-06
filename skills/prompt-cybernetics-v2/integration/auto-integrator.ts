/**
 * Auto-Integrator — Seamless Pattern Integration
 * 
 * Automatically prepends optimal patterns to subagent tasks
 */

import { TaskClassifier } from '../core/task-classifier.js';
import { PatternEvolution } from '../core/pattern-evolution.js';
import { DriftMonitor } from '../core/drift-monitor.js';

export interface EnhancedTask {
  originalTask: string;
  classification: {
    complexity: string;
    optimalDepth: number;
  };
  selectedPatterns: string[];
  prependedPrompt: string;
  driftConfig: {
    enabled: boolean;
    interval: string;
    threshold: number;
  };
}

export class AutoIntegrator {
  private classifier: TaskClassifier;
  private evolution: PatternEvolution;
  private monitor: DriftMonitor;
  private enabled: boolean = true;
  
  constructor() {
    this.classifier = new TaskClassifier();
    this.evolution = new PatternEvolution();
    this.monitor = new DriftMonitor();
  }
  
  /**
   * Initialize the integrator
   */
  async init(): Promise<void> {
    await this.evolution.load();
  }
  
  /**
   * Enable/disable auto-integration
   */
  setEnabled(enabled: boolean): void {
    this.enabled = enabled;
  }
  
  /**
   * Enhance a task with optimal patterns
   */
  async enhance(task: string): Promise<EnhancedTask> {
    if (!this.enabled) {
      return {
        originalTask: task,
        classification: { complexity: 'simple', optimalDepth: 2 },
        selectedPatterns: [],
        prependedPrompt: task,
        driftConfig: { enabled: false, interval: 'tokens', threshold: 30 }
      };
    }
    
    // 1. Classify task
    const analysis = this.classifier.analyze(task);
    
    // 2. Select optimal patterns
    const patterns = this.evolution.selectOptimal(task, 3);
    const patternIds = patterns.map(p => p.id);
    
    // 3. Synthesize prepended prompt
    const prependedPrompt = this.synthesizePrompt(patterns, task, analysis.optimalDepth);
    
    // 4. Configure drift monitoring
    const driftConfig = {
      enabled: analysis.complexity !== 'simple',
      interval: analysis.complexity === 'emergence' ? 'time' : 'tokens',
      threshold: analysis.complexity === 'simple' ? 40 : analysis.complexity === 'moderate' ? 35 : 30
    };
    
    return {
      originalTask: task,
      classification: {
        complexity: analysis.complexity,
        optimalDepth: analysis.optimalDepth
      },
      selectedPatterns: patternIds,
      prependedPrompt,
      driftConfig
    };
  }
  
  /**
   * Synthesize optimal prompt from patterns
   */
  private synthesizePrompt(patterns: any[], task: string, depth: number): string {
    const sections: string[] = [];
    
    // Header
    sections.push(`═══════════════════════════════════════════════════════════════════`);
    sections.push(`TASK: ${task.slice(0, 100)}${task.length > 100 ? '...' : ''}`);
    sections.push(`COMPLEXITY: ${this.getComplexityLabel(depth)} | DEPTH: ${depth} levels`);
    sections.push(`═══════════════════════════════════════════════════════════════════\n`);
    
    // Apply each pattern
    patterns.forEach((pattern, i) => {
      sections.push(`--- PATTERN ${i + 1}: ${pattern.name.toUpperCase()} ---`);
      sections.push(pattern.template);
      sections.push('');
    });
    
    // Dynamic recursion structure
    sections.push(`--- RECURSION STRUCTURE (${depth} levels) ---`);
    sections.push(this.generateRecursionStructure(depth));
    sections.push('');
    
    // Original task with context
    sections.push(`═══════════════════════════════════════════════════════════════════`);
    sections.push(`YOUR TASK:`);
    sections.push(task);
    sections.push(`═══════════════════════════════════════════════════════════════════`);
    
    return sections.join('\n');
  }
  
  private getComplexityLabel(depth: number): string {
    const labels: Record<number, string> = {
      2: 'SIMPLE',
      3: 'MODERATE', 
      4: 'COMPLEX',
      5: 'EMERGENCE'
    };
    return labels[depth] || 'COMPLEX';
  }
  
  private generateRecursionStructure(depth: number): string {
    const levels = [
      'Level 1: Generate response',
      'Level 2: Observe generation — "How did I arrive at this?"',
      'Level 3: Observe observer — "What biases affect my assessment?"',
      'Level 4: Pattern emergence — "What structure reveals itself?"',
      'Level 5: Meta-pattern — "How does the structure itself affect the answer?"',
      'Level 6: Recursive collapse — "What is the fixed point S(x) = x?"'
    ];
    
    return levels.slice(0, depth).join('\n');
  }
  
  /**
   * Wrap a subagent spawn with enhanced prompting
   */
  async wrapSpawn(task: string, spawnFn: (enhancedTask: string) => Promise<any>): Promise<any> {
    const enhanced = await this.enhance(task);
    
    // Log what we're doing
    console.log(`🎯 Auto-Enhanced Task:`);
    console.log(`   Complexity: ${enhanced.classification.complexity}`);
    console.log(`   Depth: ${enhanced.classification.optimalDepth}`);
    console.log(`   Patterns: ${enhanced.selectedPatterns.join(', ')}`);
    console.log(`   Drift Monitor: ${enhanced.driftConfig.enabled ? 'ON' : 'OFF'}`);
    
    // Execute with enhanced prompt
    const result = await spawnFn(enhanced.prependedPrompt);
    
    // Capture feedback (async, don't block)
    this.captureFeedback(enhanced, result).catch(console.error);
    
    return result;
  }
  
  /**
   * Capture feedback from execution
   */
  private async captureFeedback(enhanced: EnhancedTask, result: any): Promise<void> {
    // This would be called after task completion
    // For now, placeholder
    console.log(`📊 Feedback captured for patterns: ${enhanced.selectedPatterns.join(', ')}`);
  }
  
  /**
   * Get statistics on auto-integration
   */
  getStats(): {
    enabled: boolean;
    patternsAvailable: number;
    avgEffectiveness: number;
  } {
    const patterns = this.evolution.getAllPatterns();
    const avgEffectiveness = patterns.length > 0
      ? patterns.reduce((sum, p) => sum + p.effectiveness, 0) / patterns.length
      : 0;
    
    return {
      enabled: this.enabled,
      patternsAvailable: patterns.length,
      avgEffectiveness
    };
  }
}

// Simulated integration with sessions_spawn
export async function enhancedSpawn(task: string, options: any = {}): Promise<any> {
  const integrator = new AutoIntegrator();
  await integrator.init();
  
  const enhanced = await integrator.enhance(task);
  
  console.log('\n' + '='.repeat(70));
  console.log('AUTO-INTEGRATOR: Task Enhanced');
  console.log('='.repeat(70));
  console.log(`Original: ${task.slice(0, 60)}...`);
  console.log(`Complexity: ${enhanced.classification.complexity}`);
  console.log(`Patterns: ${enhanced.selectedPatterns.join(', ')}`);
  console.log('='.repeat(70));
  console.log('\nPrepended Prompt Preview:');
  console.log(enhanced.prependedPrompt.slice(0, 500) + '...');
  console.log('='.repeat(70) + '\n');
  
  // In real usage, this would call sessions_spawn with enhanced.prependedPrompt
  return {
    enhancedTask: enhanced.prependedPrompt,
    originalTask: task,
    patterns: enhanced.selectedPatterns
  };
}

// CLI usage
if (import.meta.url === `file://${process.argv[1]}`) {
  const task = process.argv[2] || 'Analyze the current codebase';
  enhancedSpawn(task).then(result => {
    console.log('✅ Enhanced spawn ready');
    console.log(`Task expanded from ${task.length} to ${result.enhancedTask.length} chars`);
  });
}
