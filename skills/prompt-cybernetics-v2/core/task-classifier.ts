/**
 * Task Classifier — Dynamic Recursion Depth Selection
 * 
 * Analyzes task complexity and recommends optimal recursion depth
 */

export type ComplexityLevel = 'simple' | 'moderate' | 'complex' | 'emergence';
export type RecursionDepth = 2 | 3 | 4 | 5 | 6;

export interface TaskAnalysis {
  complexity: ComplexityLevel;
  optimalDepth: RecursionDepth;
  reasoning: string;
  indicators: {
    length: number;      // task length in tokens (approx)
    ambiguity: number;   // 0-100 (keyword analysis)
    stakes: number;      // 0-100 (importance words)
    novelty: number;     // 0-100 (unusual terms)
  };
}

interface ComplexityIndicators {
  simple: string[];
  moderate: string[];
  complex: string[];
  emergence: string[];
}

const INDICATORS: ComplexityIndicators = {
  simple: [
    'summarize', 'fix', 'correct', 'translate', 'convert',
    'hello', 'simple', 'basic', 'quick', 'short',
    'list', 'count', 'find', 'get', 'show'
  ],
  moderate: [
    'analyze', 'compare', 'explain', 'describe', 'outline',
    'improve', 'refine', 'optimize', 'restructure',
    'step by step', 'detailed', 'comprehensive'
  ],
  complex: [
    'design', 'create', 'develop', 'implement', 'architect',
    'synthesize', 'integrate', 'orchestrate', 'engineer',
    'system', 'framework', 'protocol', 'methodology'
  ],
  emergence: [
    'discover', 'invent', 'breakthrough', 'paradigm', 'novel',
    'consciousness', 'emergence', 'phase transition',
    'reconcile', 'unify', 'revolutionary', 'fundamental',
    'theory', 'philosophy', 'metacognition', 'recursive'
  ]
};

export class TaskClassifier {
  /**
   * Analyze task and recommend optimal recursion depth
   */
  analyze(task: string): TaskAnalysis {
    const lowerTask = task.toLowerCase();
    
    // Calculate indicators
    const length = this.estimateTokens(task);
    const ambiguity = this.calculateAmbiguity(task);
    const stakes = this.calculateStakes(task);
    const novelty = this.calculateNovelty(task);
    
    // Score each complexity level
    const scores = {
      simple: this.scoreLevel(lowerTask, INDICATORS.simple),
      moderate: this.scoreLevel(lowerTask, INDICATORS.moderate),
      complex: this.scoreLevel(lowerTask, INDICATORS.complex),
      emergence: this.scoreLevel(lowerTask, INDICATORS.emergence)
    };
    
    // Adjust based on indicators
    if (length > 500) scores.complex += 20;
    if (ambiguity > 60) scores.moderate += 15;
    if (stakes > 70) scores.complex += 15;
    if (novelty > 60) scores.emergence += 20;
    
    // Determine winner
    const complexity = this.selectComplexity(scores);
    const optimalDepth = this.depthForComplexity(complexity);
    
    return {
      complexity,
      optimalDepth,
      reasoning: this.generateReasoning(complexity, scores, { length, ambiguity, stakes, novelty }),
      indicators: { length, ambiguity, stakes, novelty }
    };
  }
  
  private estimateTokens(text: string): number {
    // Rough estimate: ~4 chars per token
    return Math.ceil(text.length / 4);
  }
  
  private calculateAmbiguity(task: string): number {
    // Ambiguous words: could, might, maybe, perhaps, possibly
    const ambiguousWords = ['could', 'might', 'maybe', 'perhaps', 'possibly', 'unclear', 'vague'];
    let count = 0;
    ambiguousWords.forEach(word => {
      if (task.toLowerCase().includes(word)) count++;
    });
    return Math.min(count * 25, 100);
  }
  
  private calculateStakes(task: string): number {
    // High-stakes words: critical, important, essential, must, vital
    const stakesWords = ['critical', 'important', 'essential', 'must', 'vital', 'crucial', 'key'];
    let count = 0;
    stakesWords.forEach(word => {
      if (task.toLowerCase().includes(word)) count++;
    });
    return Math.min(count * 20 + 20, 100); // Base 20 for any task
  }
  
  private calculateNovelty(task: string): number {
    // Novelty indicators: new, unique, first, unprecedented, original
    const noveltyWords = ['new', 'unique', 'first', 'unprecedented', 'original', 'invent', 'create'];
    let count = 0;
    noveltyWords.forEach(word => {
      if (task.toLowerCase().includes(word)) count++;
    });
    return Math.min(count * 20, 100);
  }
  
  private scoreLevel(task: string, indicators: string[]): number {
    let score = 0;
    indicators.forEach(word => {
      if (task.includes(word)) score += 25;
    });
    return Math.min(score, 100);
  }
  
  private selectComplexity(scores: Record<ComplexityLevel, number>): ComplexityLevel {
    let maxScore = 0;
    let winner: ComplexityLevel = 'simple';
    
    (Object.keys(scores) as ComplexityLevel[]).forEach(level => {
      if (scores[level] > maxScore) {
        maxScore = scores[level];
        winner = level;
      }
    });
    
    return winner;
  }
  
  private depthForComplexity(complexity: ComplexityLevel): RecursionDepth {
    const map: Record<ComplexityLevel, RecursionDepth> = {
      simple: 2,
      moderate: 3,
      complex: 4,
      emergence: 5
    };
    return map[complexity];
  }
  
  private generateReasoning(
    complexity: ComplexityLevel,
    scores: Record<ComplexityLevel, number>,
    indicators: { length: number; ambiguity: number; stakes: number; novelty: number }
  ): string {
    const reasons: string[] = [];
    
    if (indicators.length > 500) reasons.push(`Long task (${indicators.length} tokens)`);
    if (indicators.ambiguity > 50) reasons.push(`High ambiguity (${indicators.ambiguity}%)`);
    if (indicators.stakes > 60) reasons.push(`High stakes (${indicators.stakes}%)`);
    if (indicators.novelty > 50) reasons.push(`High novelty (${indicators.novelty}%)`);
    
    return `Classified as ${complexity} (scores: simple=${scores.simple}, moderate=${scores.moderate}, complex=${scores.complex}, emergence=${scores.emergence}). ${reasons.join(', ') || 'Standard complexity.'}`;
  }
}

// CLI usage
if (import.meta.url === `file://${process.argv[1]}`) {
  const classifier = new TaskClassifier();
  const task = process.argv[2] || 'Analyze the current codebase';
  const result = classifier.analyze(task);
  
  console.log('\n📊 Task Analysis');
  console.log('='.repeat(50));
  console.log(`Task: ${task.slice(0, 80)}...`);
  console.log(`Complexity: ${result.complexity.toUpperCase()}`);
  console.log(`Optimal Depth: ${result.optimalDepth} levels`);
  console.log(`Reasoning: ${result.reasoning}`);
  console.log('\nIndicators:');
  console.log(`  Length: ${result.indicators.length} tokens`);
  console.log(`  Ambiguity: ${result.indicators.ambiguity}%`);
  console.log(`  Stakes: ${result.indicators.stakes}%`);
  console.log(`  Novelty: ${result.indicators.novelty}%`);
}
