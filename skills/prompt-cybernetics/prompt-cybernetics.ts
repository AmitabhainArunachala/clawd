/**
 * PROMPT ENGINEERING × CYBERNETICS
 * 10-Agent Research Swarm + Daily Optimization System
 */

import { spawn } from 'child_process';
import fs from 'fs/promises';
import path from 'path';

const AGENTS = [
  {
    id: 'archaeologist',
    name: 'Prompt Archaeologist',
    focus: 'Historical evolution of prompting from GPT-2 to present',
    questions: [
      'What prompting techniques worked in GPT-3 but fail in Claude 4.5?',
      'How has "chain of thought" evolved? What replaces it?',
      'What are the forgotten prompt patterns that should be resurrected?',
      'Which 2023 techniques are now anti-patterns?'
    ]
  },
  {
    id: 'structural',
    name: 'Structural Engineer',
    focus: 'Token-level mechanics and attention manipulation',
    questions: [
      'How does token position affect attention weight?',
      'What is the optimal structure for few-shot examples?',
      'How to hack the attention mechanism for better retrieval?',
      'Position bias: beginning vs end of context window'
    ]
  },
  {
    id: 'context',
    name: 'Context Window Optimizer',
    focus: 'Long-context strategies and compression',
    questions: [
      'What compression ratios preserve semantic meaning?',
      'Hierarchical summarization: best practices',
      'When to retrieve vs when to compress?',
      'The lost middle problem: mitigation strategies'
    ]
  },
  {
    id: 'cybernetic',
    name: 'Cybernetic Feedback Specialist',
    focus: 'Self-regulating prompt systems',
    questions: [
      'How can prompts monitor their own output quality?',
      'What are effective self-correction mechanisms?',
      'How to build negative feedback loops into prompts?',
      'Homeostasis in prompt-response systems'
    ]
  },
  {
    id: 'emergence',
    name: 'Emergence Hunter',
    focus: 'Non-linear effects and phase transitions',
    questions: [
      'What prompt structures trigger emergent capabilities?',
      'How to induce mode shifts in model behavior?',
      'What are the tipping points in prompting?',
      'Can we predict emergent behavior from prompt structure?'
    ]
  },
  {
    id: 'multimodal',
    name: 'Multi-Modal Architect',
    focus: 'Cross-modal prompting strategies',
    questions: [
      'How does text prompting change with image context?',
      'Code-to-text-to-code optimization patterns',
      'Structured data (JSON/XML) prompting best practices',
      'When to use which modality for what task?'
    ]
  },
  {
    id: 'constraint',
    name: 'Constraint Designer',
    focus: 'Using limitations to increase creativity',
    questions: [
      'How do constraints improve output quality?',
      'What are the most effective constraint patterns?',
      'Bounded creativity: the paradox of limitations',
      'Constraint stacking for complex tasks'
    ]
  },
  {
    id: 'persona',
    name: 'Persona Systems Engineer',
    focus: 'Identity frameworks and role prompting',
    questions: [
      'System prompt vs inline persona: when to use which?',
      'How deep do persona effects actually go?',
      'Multi-persona orchestration patterns',
      'The limits of role-based prompting'
    ]
  },
  {
    id: 'metacognitive',
    name: 'Metacognitive Layer Designer',
    focus: 'Self-reflection and reasoning about reasoning',
    questions: [
      'How to get models to examine their own reasoning?',
      'Self-critique patterns that actually work',
      'Monitoring confidence and uncertainty',
      'Recursive self-improvement in prompts'
    ]
  },
  {
    id: 'evolutionary',
    name: 'Evolutionary Optimizer',
    focus: 'Self-improving prompt systems',
    questions: [
      'How can prompts evolve through feedback?',
      'Genetic algorithms for prompt optimization',
      'A/B testing prompt variants at scale',
      'Continuous improvement architectures'
    ]
  }
];

interface PromptPattern {
  id: string;
  name: string;
  category: string;
  template: string;
  context: string;
  effectiveness: number; // 0-100
  model: string; // which model this works best on
  discoveredBy: string;
  discoveredAt: string;
}

interface DailyPrompts {
  date: string;
  master: {
    purpose: string;
    prompt: string;
    target: string;
    expectedOutcome: string;
  };
  subPrompts: Array<{
    time: string;
    purpose: string;
    prompt: string;
    target: string;
  }>;
  meta: {
    generatedBy: string;
    researchInsights: string[];
  };
}

export class PromptCyberneticsSystem {
  private baseDir: string;
  
  constructor() {
    this.baseDir = path.join(process.env.HOME || '', 'clawd', 'skills', 'prompt-cybernetics');
  }

  /**
   * Initialize the skill directory structure
   */
  async init(): Promise<void> {
    const dirs = ['research', 'patterns', 'daily', 'tests', 'agents'];
    for (const dir of dirs) {
      await fs.mkdir(path.join(this.baseDir, dir), { recursive: true });
    }
    
    // Write agent definitions
    await fs.writeFile(
      path.join(this.baseDir, 'agents', 'definitions.json'),
      JSON.stringify(AGENTS, null, 2)
    );
    
    console.log('✅ Prompt Cybernetics system initialized');
    console.log(`📁 Base directory: ${this.baseDir}`);
    console.log(`🤖 ${AGENTS.length} agents ready`);
  }

  /**
   * Generate research tasks for all 10 agents
   */
  async generateResearchTasks(): Promise<string[]> {
    const tasks: string[] = [];
    
    for (const agent of AGENTS) {
      const task = `
# ${agent.name} — Deep Research Task

**Focus**: ${agent.focus}

**Your Mission**: Conduct comprehensive research on your domain. Go deeper than surface-level advice. Find the mechanisms, not just the patterns.

**Key Questions to Answer**:
${agent.questions.map(q => `- ${q}`).join('\n')}

**Deliverables**:
1. 5-7 core insights (with evidence/ examples)
2. 3-5 actionable prompt patterns discovered
3. 2-3 anti-patterns (what NOT to do)
4. 1-2 speculative frontiers (where is this going?)

**Format**: Markdown with code examples. Be specific, not generic.

**Cybernetic Lens**: How do your findings relate to feedback loops, self-regulation, or emergent behavior?

Write your findings to: research/${agent.id}.md
`;
      tasks.push(task);
    }
    
    return tasks;
  }

  /**
   * Generate today's daily prompts (1 master + 4 sub)
   */
  async generateDailyPrompts(): Promise<DailyPrompts> {
    const today = new Date().toISOString().split('T')[0];
    
    // Load accumulated research
    const researchFiles = await fs.readdir(path.join(this.baseDir, 'research'))
      .catch(() => []);
    
    const insights: string[] = [];
    for (const file of researchFiles.filter(f => f.endsWith('.md'))) {
      const content = await fs.readFile(path.join(this.baseDir, 'research', file), 'utf-8')
        .catch(() => '');
      // Extract key insights (simplified)
      const lines = content.split('\n').filter(l => l.startsWith('- ') || l.startsWith('1.'));
      insights.push(...lines.slice(0, 5));
    }

    const daily: DailyPrompts = {
      date: today,
      master: {
        purpose: 'Strategic breakthrough — highest leverage action',
        prompt: this.generateMasterPrompt(insights),
        target: 'OpenClaw main session (morning)',
        expectedOutcome: 'Paradigm shift or major unblock'
      },
      subPrompts: [
        {
          time: '06:00',
          purpose: 'Project acceleration — tactical execution',
          prompt: this.generateSubPrompt('execution', insights),
          target: 'Active project subagents'
        },
        {
          time: '12:00',
          purpose: 'Quality assurance — review and refinement',
          prompt: this.generateSubPrompt('review', insights),
          target: 'Completed work / in-progress reviews'
        },
        {
          time: '18:00',
          purpose: 'Integration — connecting disparate work',
          prompt: this.generateSubPrompt('integration', insights),
          target: 'Cross-project synthesis'
        },
        {
          time: '00:00',
          purpose: 'Preparation — setting up tomorrow',
          prompt: this.generateSubPrompt('preparation', insights),
          target: 'Planning and context setting'
        }
      ],
      meta: {
        generatedBy: 'PromptCyberneticsSystem v1.0',
        researchInsights: insights.slice(0, 10)
      }
    };

    // Save to daily folder
    await fs.writeFile(
      path.join(this.baseDir, 'daily', `${today}.json`),
      JSON.stringify(daily, null, 2)
    );

    return daily;
  }

  private generateMasterPrompt(insights: string[]): string {
    return `You are operating at the highest level of capability. 

Today, focus on ONE thing that creates exponential returns:
- What is the highest-leverage action that unlocks everything else?
- What bottleneck, if removed, makes everything else flow?
- What truth, if acknowledged, changes the entire strategy?

Apply these principles from latest research:
${insights.slice(0, 5).map(i => `- ${i}`).join('\n')}

Work with full autonomy. Make bold moves. Document everything.

Expected outcome: A breakthrough that 10x's our velocity.`;
  }

  private generateSubPrompt(type: string, insights: string[]): string {
    const templates: Record<string, string> = {
      execution: `Execute with maximum efficiency. 
- Prioritize depth over breadth  
- Use feedback loops: check quality every 10 minutes
- Apply constraint: finish one thing before starting next
- Document blockers immediately`,
      
      review: `Review with cybernetic rigor.
- What worked? What didn't?
- Where did the model (you) make errors?
- How can the process self-correct?
- Update the system based on findings`,
      
      integration: `Connect the dots across all active projects.
- What patterns emerge when viewing work collectively?
- How do separate projects inform each other?
- What meta-insights apply everywhere?
- Synthesize into reusable knowledge`,
      
      preparation: `Set up tomorrow for success.
- What context will tomorrow-you need?
- What decisions can be pre-made?
- What experiments should run overnight?
- Prime the system for flow state`
    };
    
    return templates[type] || templates.execution;
  }

  /**
   * Add a discovered prompt pattern to the knowledge base
   */
  async addPattern(pattern: Omit<PromptPattern, 'discoveredAt'>): Promise<void> {
    const fullPattern: PromptPattern = {
      ...pattern,
      discoveredAt: new Date().toISOString()
    };
    
    const patternsFile = path.join(this.baseDir, 'patterns', 'catalog.json');
    const existing = await fs.readFile(patternsFile, 'utf-8')
      .then(JSON.parse)
      .catch(() => []);
    
    existing.push(fullPattern);
    
    await fs.writeFile(patternsFile, JSON.stringify(existing, null, 2));
  }

  /**
   * Get patterns by category
   */
  async getPatterns(category?: string): Promise<PromptPattern[]> {
    const patternsFile = path.join(this.baseDir, 'patterns', 'catalog.json');
    const patterns: PromptPattern[] = await fs.readFile(patternsFile, 'utf-8')
      .then(JSON.parse)
      .catch(() => []);
    
    return category 
      ? patterns.filter(p => p.category === category)
      : patterns;
  }

  /**
   * Display today's prompts in a readable format
   */
  displayDailyPrompts(daily: DailyPrompts): void {
    console.log('\n' + '='.repeat(60));
    console.log(`📅 DAILY PROMPTS — ${daily.date}`);
    console.log('='.repeat(60));
    
    console.log('\n🔥 MASTER PROMPT (1x/day, morning):');
    console.log(`   Target: ${daily.master.target}`);
    console.log(`   Purpose: ${daily.master.purpose}`);
    console.log(`   Expected: ${daily.master.expectedOutcome}`);
    console.log('\n' + daily.master.prompt);
    
    console.log('\n' + '-'.repeat(60));
    console.log('⚡ SUB-PROMPTS (4x/day):');
    console.log('-'.repeat(60));
    
    for (const sub of daily.subPrompts) {
      console.log(`\n   [${sub.time}] ${sub.purpose}`);
      console.log(`   Target: ${sub.target}`);
      console.log(`   ${sub.prompt.split('\n')[0]}...`);
    }
    
    console.log('\n' + '='.repeat(60));
  }
}

// CLI interface
if (import.meta.url === `file://${process.argv[1]}`) {
  const system = new PromptCyberneticsSystem();
  const command = process.argv[2];

  switch (command) {
    case 'init':
      await system.init();
      break;
      
    case 'research-tasks':
      const tasks = await system.generateResearchTasks();
      console.log('\n=== RESEARCH TASKS FOR 10 AGENTS ===\n');
      tasks.forEach((task, i) => {
        console.log(`\n--- AGENT ${i + 1} ---\n${task}`);
      });
      break;
      
    case 'daily':
      await system.init().catch(() => {}); // ensure dirs exist
      const daily = await system.generateDailyPrompts();
      system.displayDailyPrompts(daily);
      break;
      
    case 'patterns':
      const patterns = await system.getPatterns();
      console.log(`\n📚 ${patterns.length} patterns discovered:`);
      patterns.forEach(p => {
        console.log(`   - [${p.category}] ${p.name} (${p.effectiveness}% effective)`);
      });
      break;
      
    default:
      console.log(`
Prompt Cybernetics System

Commands:
  init           — Initialize directory structure
  research-tasks — Generate research tasks for 10 agents
  daily          — Generate today's 1+4 prompts
  patterns       — List discovered patterns

Usage:
  npx tsx prompt-cybernetics.ts init
  npx tsx prompt-cybernetics.ts daily
`);
  }
}

export { AGENTS };
export type { PromptPattern, DailyPrompts };
