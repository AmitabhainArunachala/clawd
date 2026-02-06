/**
 * Living Leading Edge — Cron Integration System
 * 
 * Checks LIVING_LEADING_EDGE.md every cron cycle
 * Generates reports, tracks progress, suggests actions
 */

import fs from 'fs/promises';
import path from 'path';

const LLE_FILE = '/Users/dhyana/clawd/LIVING_LEADING_EDGE.md';
const LOG_FILE = '/Users/dhyana/clawd/logs/lle-checks.jsonl';

interface LLECheck {
  timestamp: string;
  dayOfWeek: string;
  budgetRemaining: number;
  activeIdeas: number;
  mediumTodosOpen: number;
  sideHustlePipeline: string[];
  suggestedAction: string;
  researchStatus: Record<string, string>;
}

interface BudgetTracker {
  date: string;
  allocated: number;
  spent: number;
  categories: {
    revenueGen: number;
    capability: number;
    knowledge: number;
  };
}

export class LivingLeadingEdge {
  private checkCount = 0;
  
  /**
   * Main check function — called every cron cycle
   */
  async check(): Promise<LLECheck> {
    this.checkCount++;
    const now = new Date();
    
    // Read current LLE file
    const content = await fs.readFile(LLE_FILE, 'utf-8');
    
    // Parse sections
    const ideas = this.extractIdeas(content);
    const todos = this.extractTodos(content);
    const sideHustles = this.extractSideHustles(content);
    const research = this.extractResearchStatus(content);
    
    // Calculate budget
    const budget = await this.calculateBudget();
    
    // Generate suggested action based on time/context
    const suggestedAction = this.generateSuggestion(now, todos, sideHustles);
    
    const check: LLECheck = {
      timestamp: now.toISOString(),
      dayOfWeek: now.toLocaleDateString('en-US', { weekday: 'long' }),
      budgetRemaining: budget.remaining,
      activeIdeas: ideas.length,
      mediumTodosOpen: todos.medium.filter(t => !t.includes('[x]')).length,
      sideHustlePipeline: sideHustles.map(s => s.name),
      suggestedAction,
      researchStatus: research
    };
    
    // Log check
    await this.logCheck(check);
    
    // Display summary
    this.displayCheck(check);
    
    return check;
  }
  
  private extractIdeas(content: string): string[] {
    const match = content.match(/### Active Ideas[\s\S]*?(?=### Idea Backlog)/);
    if (!match) return [];
    
    return match[0]
      .split('\n')
      .filter(line => line.match(/^#### \d+\./))
      .map(line => line.replace(/^#### \d+\.\s*/, ''));
  }
  
  private extractTodos(content: string): { medium: string[]; long: string[] } {
    const mediumMatch = content.match(/## 📋 MEDIUM-TERM TODO[\s\S]*?(?=## 📋 LONG-TERM TODO)/);
    const longMatch = content.match(/## 📋 LONG-TERM TODO[\s\S]*?(?=## 🔄 CYBERNETIC)/);
    
    return {
      medium: mediumMatch ? mediumMatch[0].split('\n').filter(l => l.includes('- [')) : [],
      long: longMatch ? longMatch[0].split('\n').filter(l => l.includes('- [')) : []
    };
  }
  
  private extractSideHustles(content: string): Array<{ name: string; status: string }> {
    const match = content.match(/## 💼 SIDE HUSTLES[\s\S]*?(?=## 🔬 RESEARCH)/);
    if (!match) return [];
    
    return match[0]
      .split('### ')
      .slice(1)
      .map(section => {
        const name = section.split('\n')[0];
        const status = section.includes('Status: Ready') ? 'Ready' : 
                      section.includes('Status: Active') ? 'Active' : 'Backlog';
        return { name, status };
      });
  }
  
  private extractResearchStatus(content: string): Record<string, string> {
    const match = content.match(/### Investigation Path[\s\S]*?(?=### Expected Outcome)/);
    if (!match) return {};
    
    const steps = match[0].match(/#### Step \d+:.*?(?=#### Step \d+:|### Expected|$)/gs) || [];
    
    return steps.reduce((acc, step, i) => {
      const title = step.match(/#### Step \d+: (.*)/)?.[1] || `Step ${i + 1}`;
      const hasAction = step.includes('Action:');
      acc[title] = hasAction ? 'In Progress' : 'Not Started';
      return acc;
    }, {} as Record<string, string>);
  }
  
  private async calculateBudget(): Promise<{ remaining: number; spent: number }> {
    const today = new Date().toISOString().split('T')[0];
    const logDir = path.dirname(LOG_FILE);
    
    try {
      const files = await fs.readdir(logDir);
      const todayChecks = await Promise.all(
        files
          .filter(f => f.includes(today))
          .map(f => fs.readFile(path.join(logDir, f), 'utf-8'))
      );
      
      // Parse spending from logs (placeholder logic)
      const spent = todayChecks.length * 0.5; // $0.50 per check avg
      return { remaining: 50 - spent, spent };
    } catch {
      return { remaining: 50, spent: 0 };
    }
  }
  
  private generateSuggestion(
    now: Date, 
    todos: { medium: string[] }, 
    sideHustles: Array<{ name: string; status: string }>
  ): string {
    const hour = now.getHours();
    const openTodos = todos.medium.filter(t => !t.includes('[x]'));
    const readyHustles = sideHustles.filter(s => s.status === 'Ready');
    
    // Morning: Focus on high-priority todos
    if (hour >= 6 && hour < 12) {
      if (openTodos.length > 0) {
        return `Morning focus: Complete "${openTodos[0].replace(/- \[ \] /, '').slice(0, 50)}..."`;
      }
      return 'Morning: Review brainstorm ideas for new opportunities';
    }
    
    // Afternoon: Side hustle execution
    if (hour >= 12 && hour < 18) {
      if (readyHustles.length > 0) {
        return `Launch ready side hustle: ${readyHustles[0].name}`;
      }
      return 'Afternoon: Research Nvidia/Kimi partnership progress';
    }
    
    // Evening: Planning and reflection
    return 'Evening: Update LIVING_LEADING_EDGE.md with today\'s progress';
  }
  
  private async logCheck(check: LLECheck): Promise<void> {
    await fs.mkdir(path.dirname(LOG_FILE), { recursive: true });
    const line = JSON.stringify(check) + '\n';
    await fs.appendFile(LOG_FILE, line);
  }
  
  private displayCheck(check: LLECheck): void {
    console.log('\n' + '='.repeat(60));
    console.log('🧠 LIVING LEADING EDGE — Cron Check');
    console.log('='.repeat(60));
    console.log(`Time: ${check.timestamp}`);
    console.log(`Budget: $${check.budgetRemaining.toFixed(2)} remaining of $50`);
    console.log(`Active Ideas: ${check.activeIdeas}`);
    console.log(`Open Todos: ${check.mediumTodosOpen}`);
    console.log(`Side Hustles: ${check.sideHustlePipeline.join(', ')}`);
    console.log('\n💡 Suggested Action:');
    console.log(`   ${check.suggestedAction}`);
    console.log('='.repeat(60) + '\n');
  }
  
  /**
   * Generate daily summary report
   */
  async dailyReport(): Promise<void> {
    const checks = await this.loadTodayChecks();
    
    console.log('\n📊 LIVING LEADING EDGE — Daily Summary');
    console.log('='.repeat(60));
    console.log(`Checks today: ${checks.length}`);
    console.log(`Avg budget remaining: $${(checks.reduce((s, c) => s + c.budgetRemaining, 0) / checks.length).toFixed(2)}`);
    console.log(`Research items tracked: ${Object.keys(checks[0]?.researchStatus || {}).length}`);
    console.log('\nTop Suggestions Given:');
    const suggestions = checks.map(c => c.suggestedAction);
    suggestions.slice(-5).forEach((s, i) => console.log(`  ${i + 1}. ${s.slice(0, 60)}...`));
  }
  
  private async loadTodayChecks(): Promise<LLECheck[]> {
    try {
      const content = await fs.readFile(LOG_FILE, 'utf-8');
      const today = new Date().toISOString().split('T')[0];
      return content
        .split('\n')
        .filter(l => l.trim())
        .map(l => JSON.parse(l))
        .filter(c => c.timestamp.startsWith(today));
    } catch {
      return [];
    }
  }
}

// CLI usage
if (import.meta.url === `file://${process.argv[1]}`) {
  const lle = new LivingLeadingEdge();
  const command = process.argv[2];
  
  switch (command) {
    case 'check':
      lle.check();
      break;
    case 'report':
      lle.dailyReport();
      break;
    default:
      console.log(`
Living Leading Edge — Cron Integration

Commands:
  check   — Run LLE check (call from cron)
  report  — Generate daily summary

Cron setup:
  0 * * * * cd ~/clawd && npx tsx lle-cron.ts check
  0 22 * * * cd ~/clawd && npx tsx lle-cron.ts report
`);
  }
}

export { LLECheck, BudgetTracker };
