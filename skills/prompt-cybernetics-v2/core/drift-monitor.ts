/**
 * Drift Monitor — Real-Time Self-Monitoring
 * 
 * Tracks execution and detects when output drifts from intent
 */

export interface DriftConfig {
  checkInterval: 'tokens' | 'time' | 'sections';
  threshold: number;
  originalIntent: string;
}

export interface DriftCheck {
  timestamp: number;
  tokensProduced: number;
  timeElapsed: number;
  topicConsistency: number; // 0-100
  driftDetected: boolean;
  driftMagnitude: number;
  suggestedCorrection: string;
}

export interface DriftSession {
  config: DriftConfig;
  checks: DriftCheck[];
  startTime: number;
  lastCheckTime: number;
  totalDriftEvents: number;
}

export class DriftMonitor {
  private session: DriftSession | null = null;
  private outputBuffer: string[] = [];
  
  /**
   * Start monitoring a new task
   */
  start(config: DriftConfig): DriftSession {
    this.session = {
      config,
      checks: [],
      startTime: Date.now(),
      lastCheckTime: Date.now(),
      totalDriftEvents: 0
    };
    this.outputBuffer = [];
    return this.session;
  }
  
  /**
   * Record output chunk for analysis
   */
  recordOutput(chunk: string): void {
    this.outputBuffer.push(chunk);
  }
  
  /**
   * Check if drift has occurred
   * Returns null if no check needed yet, DriftCheck if checked
   */
  check(): DriftCheck | null {
    if (!this.session) return null;
    
    const now = Date.now();
    const tokens = this.estimateTokens(this.outputBuffer.join(''));
    const timeElapsed = now - this.session.startTime;
    
    // Determine if check is needed based on interval type
    const shouldCheck = this.shouldCheck(tokens, timeElapsed);
    if (!shouldCheck) return null;
    
    // Perform drift analysis
    const currentOutput = this.outputBuffer.join('');
    const topicConsistency = this.analyzeTopicConsistency(
      this.session.config.originalIntent,
      currentOutput
    );
    
    const driftMagnitude = 100 - topicConsistency;
    const driftDetected = driftMagnitude > this.session.config.threshold;
    
    const check: DriftCheck = {
      timestamp: now,
      tokensProduced: tokens,
      timeElapsed,
      topicConsistency,
      driftDetected,
      driftMagnitude,
      suggestedCorrection: driftDetected 
        ? this.generateCorrection(driftMagnitude, topicConsistency)
        : 'Continue'
    };
    
    this.session.checks.push(check);
    this.session.lastCheckTime = now;
    if (driftDetected) this.session.totalDriftEvents++;
    
    return check;
  }
  
  private shouldCheck(tokens: number, timeElapsed: number): boolean {
    if (!this.session) return false;
    
    const lastCheck = this.session.checks[this.session.checks.length - 1];
    const tokensSinceLast = lastCheck ? tokens - lastCheck.tokensProduced : tokens;
    const timeSinceLast = lastCheck ? timeElapsed - lastCheck.timeElapsed : timeElapsed;
    
    switch (this.session.config.checkInterval) {
      case 'tokens':
        return tokensSinceLast >= 500; // Check every ~500 tokens
      case 'time':
        return timeSinceLast >= 300000; // Check every 5 minutes
      case 'sections':
        return tokensSinceLast >= 1000; // Check every major section
      default:
        return tokensSinceLast >= 500;
    }
  }
  
  private estimateTokens(text: string): number {
    return Math.ceil(text.length / 4);
  }
  
  private analyzeTopicConsistency(intent: string, output: string): number {
    // Simplified: check keyword overlap
    const intentWords = new Set(intent.toLowerCase().split(/\s+/));
    const outputWords = output.toLowerCase().split(/\s+/);
    
    let matches = 0;
    outputWords.forEach(word => {
      if (intentWords.has(word)) matches++;
    });
    
    // Also check for drift indicators
    const driftIndicators = ['however', 'but', 'instead', 'rather', 'shift'];
    const driftCount = driftIndicators.reduce((count, word) => {
      return count + (output.toLowerCase().includes(word) ? 1 : 0);
    }, 0);
    
    const baseScore = (matches / Math.max(outputWords.length, 1)) * 100;
    const driftPenalty = driftCount * 5;
    
    return Math.max(0, Math.min(100, baseScore - driftPenalty));
  }
  
  private generateCorrection(magnitude: number, consistency: number): string {
    if (magnitude > 80) {
      return 'CRITICAL: Output has significantly diverged. STOP. Review original intent. RESTART from last checkpoint.';
    } else if (magnitude > 50) {
      return 'MODERATE: Output drifting. PAUSE. Compare current direction with original goal. ADJUST course.';
    } else {
      return 'MINOR: Slight drift detected. Continue but maintain awareness of original intent.';
    }
  }
  
  /**
   * Get current session summary
   */
  getSummary(): { totalChecks: number; driftEvents: number; avgConsistency: number } | null {
    if (!this.session || this.session.checks.length === 0) return null;
    
    const totalChecks = this.session.checks.length;
    const driftEvents = this.session.totalDriftEvents;
    const avgConsistency = this.session.checks.reduce((sum, c) => sum + c.topicConsistency, 0) / totalChecks;
    
    return { totalChecks, driftEvents, avgConsistency };
  }
  
  /**
   * End monitoring session
   */
  end(): DriftSession | null {
    const session = this.session;
    this.session = null;
    this.outputBuffer = [];
    return session;
  }
}

// Simulated usage for testing
if (import.meta.url === `file://${process.argv[1]}`) {
  const monitor = new DriftMonitor();
  
  monitor.start({
    checkInterval: 'tokens',
    threshold: 30,
    originalIntent: 'Analyze the economic impact of AI on employment'
  });
  
  console.log('🎯 Drift Monitor Active');
  console.log('Simulating output...\n');
  
  // Simulate work
  const chunks = [
    'The economic impact of AI is significant. ',
    'Many jobs are being automated. ',
    'However, new jobs are also created. ',
    'The key is reskilling the workforce. ',
    'Actually, let me talk about something else entirely. ',
    'Climate change is a major issue...'
  ];
  
  chunks.forEach((chunk, i) => {
    monitor.recordOutput(chunk);
    const check = monitor.check();
    if (check) {
      console.log(`Check ${i + 1}: Consistency ${check.topicConsistency.toFixed(1)}%`);
      if (check.driftDetected) {
        console.log(`⚠️ DRIFT DETECTED: ${check.suggestedCorrection}`);
      }
    }
  });
  
  const summary = monitor.getSummary();
  if (summary) {
    console.log('\n📊 Session Summary:');
    console.log(`  Total checks: ${summary.totalChecks}`);
    console.log(`  Drift events: ${summary.driftEvents}`);
    console.log(`  Avg consistency: ${summary.avgConsistency.toFixed(1)}%`);
  }
}
