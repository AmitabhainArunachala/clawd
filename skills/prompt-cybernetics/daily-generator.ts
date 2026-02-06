/**
 * Daily Prompt Generator
 * 
 * Run this to generate today's 1+4 prompts based on accumulated research.
 * Usage: npx tsx daily-generator.ts
 */

import fs from 'fs/promises';
import path from 'path';

const BASE_DIR = '/Users/dhyana/clawd/skills/prompt-cybernetics';

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
}

async function loadResearchInsights(): Promise<string[]> {
  const researchDir = path.join(BASE_DIR, 'research');
  const files = await fs.readdir(researchDir).catch(() => []);
  
  const insights: string[] = [];
  
  for (const file of files.filter(f => f.endsWith('.md'))) {
    const content = await fs.readFile(path.join(researchDir, file), 'utf-8');
    // Extract bullet points and numbered lists
    const lines = content.split('\n')
      .map(l => l.trim())
      .filter(l => l.match(/^[-\*\d]\./) && l.length > 20);
    insights.push(...lines.slice(0, 3));
  }
  
  return insights;
}

async function generateDailyPrompts(): Promise<DailyPrompts> {
  const today = new Date().toISOString().split('T')[0];
  const insights = await loadResearchInsights();
  
  // Select top insights for today
  const topInsights = insights.slice(0, 5);
  
  return {
    date: today,
    master: {
      purpose: "Maximum leverage — breakthrough action",
      prompt: `Today, operate with full autonomy toward the highest-leverage outcome.

Research insights informing today:
${topInsights.map(i => `- ${i.replace(/^[-\*\d]\.\s*/, '')}`).join('\n')}

Cybernetic principles:
- Feedback: Monitor and adjust every 30 minutes
- Constraint: Do ONE thing that unlocks everything else
- Emergence: Allow solutions to arise, don't force them

Question: What is the single action that, if completed, makes everything else flow?

Execute that. Document everything.`,
      target: "OpenClaw main session",
      expectedOutcome: "Strategic breakthrough or major unblock"
    },
    subPrompts: [
      {
        time: "06:00",
        purpose: "Deep work — primary project advancement",
        prompt: "Execute on the TOP 10 project with highest priority. Work in 90-minute focused blocks. Check quality every 30 minutes. Document blockers immediately.",
        target: "Primary project subagent"
      },
      {
        time: "12:00",
        purpose: "Integration — connect across projects",
        prompt: "Review morning work. How does it connect to other active projects? Extract meta-insights. Update documentation. Synthesize learnings.",
        target: "Cross-project synthesis"
      },
      {
        time: "18:00",
        purpose: "Quality assurance — review and refine",
        prompt: "Review day's output with rigor. What errors were made? How can the process improve? Update patterns based on findings. Self-correct.",
        target: "Review and refinement"
      },
      {
        time: "00:00",
        purpose: "Preparation — prime tomorrow",
        prompt: "Set context for tomorrow. What should tomorrow-you know? Queue tasks. Prepare environment. Write tomorrow's master prompt based on today's learnings.",
        target: "Planning and preparation"
      }
    ]
  };
}

async function displayPrompts(prompts: DailyPrompts): Promise<void> {
  console.log('\n' + '='.repeat(70));
  console.log(`📅 DAILY PROMPTS — ${prompts.date}`);
  console.log('='.repeat(70));
  
  console.log('\n🔥 MASTER PROMPT (Feed once, morning):');
  console.log('-'.repeat(70));
  console.log(prompts.master.prompt);
  console.log(`\n   Target: ${prompts.master.target}`);
  console.log(`   Expected: ${prompts.master.expectedOutcome}`);
  
  console.log('\n' + '-'.repeat(70));
  console.log('⚡ SUB-PROMPTS (Feed 4x daily):');
  console.log('-'.repeat(70));
  
  for (const sub of prompts.subPrompts) {
    console.log(`\n[${sub.time}] ${sub.purpose}`);
    console.log(`Target: ${sub.target}`);
    console.log(`→ ${sub.prompt.slice(0, 80)}...`);
  }
  
  console.log('\n' + '='.repeat(70));
  console.log('💡 Usage: Feed MASTER to OpenClaw main session. Feed SUBs to relevant agents.');
  console.log('='.repeat(70) + '\n');
}

async function main() {
  const prompts = await generateDailyPrompts();
  
  // Save to file
  const outputPath = path.join(BASE_DIR, 'daily', `${prompts.date}.json`);
  await fs.mkdir(path.dirname(outputPath), { recursive: true });
  await fs.writeFile(outputPath, JSON.stringify(prompts, null, 2));
  
  // Display
  await displayPrompts(prompts);
  
  console.log(`✅ Saved to: ${outputPath}`);
}

main().catch(console.error);
