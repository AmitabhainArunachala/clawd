/**
 * Prompt Cybernetics v2.0 — Main Entry Point
 * 
 * Usage: npx tsx index.ts <command> [args]
 */

import { TaskClassifier } from './core/task-classifier';
import { PatternEvolution } from './core/pattern-evolution';
import { AutoIntegrator, enhancedSpawn } from './integration/auto-integrator';

const classifier = new TaskClassifier();
const evolution = new PatternEvolution();
const integrator = new AutoIntegrator();

async function main() {
  await integrator.init();
  
  const command = process.argv[2];
  const args = process.argv.slice(3);
  
  switch (command) {
    case 'classify':
      const task = args.join(' ') || 'Analyze the codebase';
      const analysis = classifier.analyze(task);
      console.log('\n📊 Task Classification');
      console.log('='.repeat(50));
      console.log(`Task: ${task}`);
      console.log(`Complexity: ${analysis.complexity.toUpperCase()}`);
      console.log(`Optimal Depth: ${analysis.optimalDepth} levels`);
      console.log(`Reasoning: ${analysis.reasoning}`);
      break;
      
    case 'patterns':
      await evolution.load();
      const patterns = evolution.getAllPatterns();
      console.log('\n📚 Pattern Rankings');
      console.log('='.repeat(60));
      patterns.forEach((p, i) => {
        const status = p.effectiveness >= 70 ? '🟢' : p.effectiveness >= 50 ? '🟡' : '🔴';
        console.log(`${status} ${i + 1}. ${p.name} (${p.category})`);
        console.log(`   Effectiveness: ${p.effectiveness.toFixed(1)}% | Uses: ${p.stats.uses}`);
      });
      break;
      
    case 'select':
      await evolution.load();
      const taskType = args.join(' ') || 'general';
      const optimal = evolution.selectOptimal(taskType, 3);
      console.log(`\n🎯 Optimal patterns for "${taskType}":`);
      optimal.forEach((p, i) => {
        const effectiveness = evolution.getEffectiveness(p.id);
        console.log(`${i + 1}. ${p.name} — ${effectiveness.toFixed(1)}%`);
      });
      break;
      
    case 'evolve':
      await evolution.load();
      const reports = await evolution.evolvePatterns();
      console.log('\n🧬 Evolution Report');
      console.log('='.repeat(60));
      reports.forEach(r => {
        const icon = r.action === 'maintain' ? '✅' : r.action === 'improve' ? '🔧' : r.action === 'variant' ? '🧪' : '🗑️';
        console.log(`\n${icon} ${r.patternId}: ${r.action.toUpperCase()}`);
        console.log(`   ${r.reasoning}`);
      });
      break;
      
    case 'enhance':
      const enhanceTask = args.join(' ') || 'Write a function';
      const result = await enhancedSpawn(enhanceTask);
      console.log('\n✅ Task Enhanced');
      console.log(`Original: ${result.originalTask.length} chars`);
      console.log(`Enhanced: ${result.enhancedTask.length} chars`);
      console.log(`Patterns: ${result.patterns.join(', ')}`);
      break;
      
    case 'daily':
      console.log('\n📅 Generating Daily Prompts (v2.0)');
      console.log('='.repeat(60));
      console.log('Master Prompt: Apply one evolution vector today');
      console.log('Sub-prompts: 4x daily with auto-selected patterns');
      console.log('\nKey difference from v1.0:');
      console.log('- Patterns auto-selected based on task type');
      console.log('- Effectiveness scores evolve with use');
      console.log('- Drift detection integrated');
      break;
      
    case 'status':
      const stats = integrator.getStats();
      console.log('\n📊 System Status');
      console.log('='.repeat(50));
      console.log(`Auto-integration: ${stats.enabled ? 'ENABLED' : 'DISABLED'}`);
      console.log(`Patterns available: ${stats.patternsAvailable}`);
      console.log(`Avg effectiveness: ${stats.avgEffectiveness.toFixed(1)}%`);
      break;
      
    default:
      console.log(`
╔══════════════════════════════════════════════════════════════════╗
║     PROMPT CYBERNETICS v2.0 — Recursive Self-Improvement        ║
╚══════════════════════════════════════════════════════════════════╝

Commands:
  classify "<task>"    — Analyze task complexity
  patterns             — List all patterns with effectiveness scores
  select "<tasktype>"  — Select optimal patterns for task type
  evolve               — Analyze patterns and suggest evolutions
  enhance "<task>"     — Enhance task with optimal patterns
  daily                — Show today's prompts
  status               — System status

Examples:
  npx tsx index.ts classify "Design a new framework"
  npx tsx index.ts patterns
  npx tsx index.ts enhance "Write API documentation"
  npx tsx index.ts evolve

Key Features (v2.0):
  • Dynamic recursion depth (2-6 levels based on task)
  • Real drift detection during execution
  • Pattern effectiveness tracking (auto-updates)
  • Auto-integration with subagent spawning
  • Self-evolving pattern database

The prompt engineering skill that improves its own prompt engineering.
`);
  }
}

main().catch(console.error);
