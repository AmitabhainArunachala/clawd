/**
 * Enhanced Sessions Spawn — v2.0 Integration
 * 
 * Automatically applies prompt cybernetics to all subagent spawns
 */

import { spawn } from 'child_process';
import { TaskClassifier } from '../core/task-classifier';
import { PatternEvolution } from '../core/pattern-evolution';

const classifier = new TaskClassifier();
const evolution = new PatternEvolution();
let initialized = false;

async function init() {
  if (!initialized) {
    await evolution.load();
    initialized = true;
  }
}

/**
 * Enhanced spawn with auto-applied prompt patterns
 */
export async function enhancedSpawn(task: string, options: any = {}) {
  await init();
  
  // 1. Classify task
  const analysis = classifier.analyze(task);
  
  // 2. Select optimal patterns
  const patterns = evolution.selectOptimal(task, 3);
  
  // 3. Build enhanced task
  const enhancedTask = buildEnhancedTask(task, analysis, patterns);
  
  // 4. Log enhancement
  console.log(`\n🎯 Enhanced Spawn (v2.0)`);
  console.log(`   Original: ${task.slice(0, 60)}...`);
  console.log(`   Complexity: ${analysis.complexity} | Depth: ${analysis.optimalDepth}`);
  console.log(`   Patterns: ${patterns.map(p => p.name).join(', ')}`);
  console.log(`   Expanded: ${task.length} → ${enhancedTask.length} chars\n`);
  
  // 5. Return enhanced for manual use OR spawn directly
  if (options.execute === false) {
    return {
      originalTask: task,
      enhancedTask,
      analysis,
      patterns: patterns.map(p => ({ id: p.id, name: p.name, template: p.template }))
    };
  }
  
  // For actual execution, return the enhanced task to feed to sessions_spawn
  return enhancedTask;
}

function buildEnhancedTask(task: string, analysis: any, patterns: any[]): string {
  const sections: string[] = [];
  
  // Header
  sections.push(`═══ ENHANCED TASK ═══ Complexity: ${analysis.complexity.toUpperCase()} | Depth: ${analysis.optimalDepth} levels ═══`);
  sections.push('');
  
  // Apply each pattern
  patterns.forEach((p, i) => {
    sections.push(`[PATTERN ${i + 1}: ${p.name.toUpperCase()}]`);
    sections.push(p.template);
    sections.push('');
  });
  
  // Dynamic recursion structure
  sections.push(`[RECURSION STRUCTURE: ${analysis.optimalDepth} levels]`);
  sections.push(generateRecursion(analysis.optimalDepth));
  sections.push('');
  
  // Original task
  sections.push(`═══ YOUR TASK ═══`);
  sections.push(task);
  sections.push('═══ END ENHANCEMENT ═══');
  
  return sections.join('\n');
}

function generateRecursion(depth: number): string {
  const levels = [
    'L1: Generate initial response',
    'L2: Observe generation process — what assumptions?',
    'L3: Observe the observer — what biases?',
    'L4: Pattern emergence — what structure reveals itself?',
    'L5: Meta-pattern — how does structure affect answer?',
    'L6: Fixed point — what is S(x) = x here?'
  ];
  return levels.slice(0, depth).join('\n');
}

/**
 * Quick wrapper for immediate use
 */
export async function spawnWithV2(task: string, label: string, options: any = {}) {
  const enhanced = await enhancedSpawn(task, { execute: false });
  
  console.log('\n' + '='.repeat(70));
  console.log('ENHANCED TASK READY FOR sessions_spawn');
  console.log('='.repeat(70));
  console.log(`Label: ${label}`);
  console.log(`Task Length: ${enhanced.enhancedTask.length} chars`);
  console.log(`Patterns Applied: ${enhanced.patterns.length}`);
  console.log('='.repeat(70));
  console.log('\nCopy this task into your sessions_spawn:');
  console.log('\n```');
  console.log(enhanced.enhancedTask);
  console.log('```\n');
  
  return enhanced;
}

// CLI usage
if (import.meta.url === `file://${process.argv[1]}`) {
  const task = process.argv[2] || 'Analyze the current system';
  const label = process.argv[3] || 'enhanced-subagent';
  
  spawnWithV2(task, label);
}
