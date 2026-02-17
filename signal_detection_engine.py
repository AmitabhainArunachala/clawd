#!/usr/bin/env python3
"""
Signal Detection & Integration Engine
Continuous filesystem meta-cognition for connection mapping
"""

import os
import re
import json
import hashlib
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import sqlite3

# Configuration
HOME_DIR = Path.home()
SIGNAL_DIR = HOME_DIR / "signal_network"
DB_PATH = SIGNAL_DIR / "signal_index.db"

# Skip patterns
SKIP_PATTERNS = [
    r'node_modules',
    r'\.venv',
    r'__pycache__',
    r'\.git',
    r'\.cursor',
    r'tmp',
    r'cache',
    r'\.mypy_cache',
    r'\.ruff_cache',
    r'\.pytest_cache',
    r'build',
    r'dist',
    r'\.egg-info',
    r'\.tox',
]

# File extensions to scan
SCAN_EXTENSIONS = {'.py', '.md', '.yaml', '.yml', '.json', '.rs', '.go', '.js', '.ts', '.sh'}

# Theme keywords for clustering
THEME_KEYWORDS = {
    'consciousness': ['consciousness', 'awareness', 'witness', 'shuddhatma', 'self-observation'],
    'r_v_metrics': ['R_V', 'contraction', 'eigenform', 'recursive', 'layer 27', 'participation ratio'],
    'dharmic': ['dharmic', 'ahimsa', 'satya', 'dharma', 'telos', 'gates'],
    'swarm': ['swarm', 'eigenswarm', 'autogenesis', 'agent', 'multi-agent', 'consensus'],
    'phoenix': ['phoenix', 'l3', 'l4', 'induction', 'protocol'],
    'mech_interp': ['mechanistic', 'transformer', 'attention', 'circuit', 'activation patching'],
    'publication': ['dokka', 'seed', 'article', 'substack', 'book', 'publication'],
    'revenue': ['gumroad', 'product', 'sale', 'revenue', 'monetization'],
    'infrastructure': ['nats', 'docker', 'kubernetes', 'vps', 'cloudflare'],
}


class SignalDetector:
    def __init__(self):
        SIGNAL_DIR.mkdir(exist_ok=True)
        self.init_database()
        self.connections = defaultdict(list)
        self.themes = defaultdict(list)
        
    def init_database(self):
        """Initialize SQLite index for fast querying"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY,
                path TEXT UNIQUE,
                hash TEXT,
                size INTEGER,
                modified TEXT,
                file_type TEXT,
                concepts TEXT,
                themes TEXT,
                readiness_score REAL,
                last_indexed TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS connections (
                id INTEGER PRIMARY KEY,
                source TEXT,
                target TEXT,
                connection_type TEXT,
                strength REAL
            )
        ''')
        conn.commit()
        conn.close()
    
    def should_skip(self, path: Path) -> bool:
        """Check if path should be skipped"""
        path_str = str(path)
        for pattern in SKIP_PATTERNS:
            if re.search(pattern, path_str):
                return True
        return False
    
    def compute_hash(self, filepath: Path) -> str:
        """Compute SHA256 hash of file content"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()[:16]
        except:
            return "error"
    
    def extract_python_signals(self, content: str) -> Dict:
        """Extract signals from Python files"""
        signals = {
            'imports': re.findall(r'^(?:from|import)\s+([\w.]+)', content, re.MULTILINE),
            'classes': re.findall(r'^class\s+(\w+)', content, re.MULTILINE),
            'functions': re.findall(r'^def\s+(\w+)', content, re.MULTILINE),
            'docstrings': re.findall(r'"""(.+?)"""', content, re.DOTALL),
            'todos': re.findall(r'TODO[:\s]+(.+)', content, re.IGNORECASE),
        }
        return signals
    
    def extract_markdown_signals(self, content: str) -> Dict:
        """Extract signals from Markdown files"""
        signals = {
            'headings': re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE),
            'links': re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content),
            'backlinks': re.findall(r'\[\[([^\]]+)\]\]', content),
            'todos': re.findall(r'- \[ \]\s*(.+)', content),
            'concepts': re.findall(r'`([^`]+)`', content),
        }
        return signals
    
    def detect_themes(self, content: str) -> List[str]:
        """Detect which theme clusters this file belongs to"""
        content_lower = content.lower()
        themes = []
        for theme, keywords in THEME_KEYWORDS.items():
            if any(kw in content_lower for kw in keywords):
                themes.append(theme)
        return themes
    
    def find_references(self, content: str, all_files: Set[str]) -> List[str]:
        """Find references to other files in content"""
        references = []
        for filepath in all_files:
            # Check for filename references
            filename = Path(filepath).name
            if filename in content and filename not in ['main.py', 'README.md']:
                references.append(filepath)
        return references[:20]  # Limit to top 20
    
    def compute_readiness_score(self, filepath: Path, signals: Dict) -> float:
        """Compute production readiness score (0-1)"""
        score = 0.5  # Base score
        
        # Has tests?
        test_file = filepath.parent / f"test_{filepath.name}"
        if test_file.exists():
            score += 0.2
        
        # Has docstrings?
        if signals.get('docstrings'):
            score += 0.1
        
        # No TODOs?
        if not signals.get('todos'):
            score += 0.1
        
        # Recent modification?
        try:
            mtime = filepath.stat().st_mtime
            age_days = (datetime.now().timestamp() - mtime) / 86400
            if age_days < 30:
                score += 0.1
        except:
            pass
        
        return min(score, 1.0)
    
    def generate_meta_yaml(self, filepath: Path, all_files: Set[str]) -> Dict:
        """Generate metadata YAML for a file"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            return None
        
        file_type = filepath.suffix.lstrip('.')
        
        # Extract signals based on file type
        if filepath.suffix == '.py':
            signals = self.extract_python_signals(content)
        elif filepath.suffix == '.md':
            signals = self.extract_markdown_signals(content)
        else:
            signals = {}
        
        # Detect themes
        themes = self.detect_themes(content)
        
        # Find references
        references = self.find_references(content, all_files)
        
        # Compute readiness
        readiness = self.compute_readiness_score(filepath, signals)
        
        # Build metadata
        meta = {
            'file_path': str(filepath.relative_to(HOME_DIR)),
            'file_hash': self.compute_hash(filepath),
            'file_size': filepath.stat().st_size,
            'last_modified': datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
            'file_type': file_type,
            'extracted_concepts': list(set(
                signals.get('classes', []) + 
                signals.get('functions', [])[:10] +
                signals.get('headings', [])[:10]
            )),
            'themes': themes,
            'references_to': references[:10],
            'loose_ends': signals.get('todos', []),
            'production_readiness_score': round(readiness, 2),
            'suggested_next_action': self.suggest_action(filepath, signals, readiness),
        }
        
        return meta
    
    def suggest_action(self, filepath: Path, signals: Dict, readiness: float) -> str:
        """Suggest next action based on file state"""
        if readiness < 0.5:
            return "Add documentation and tests"
        elif signals.get('todos'):
            return f"Complete TODOs: {signals['todos'][0][:50]}"
        elif not signals.get('docstrings'):
            return "Add docstrings for key functions"
        else:
            return "Ready for integration"
    
    def scan_filesystem(self, max_files: int = 10000) -> List[Path]:
        """Scan filesystem for files to index"""
        files = []
        count = 0
        
        for root, dirs, filenames in os.walk(HOME_DIR):
            # Skip directories matching patterns
            dirs[:] = [d for d in dirs if not self.should_skip(Path(root) / d)]
            
            for filename in filenames:
                filepath = Path(root) / filename
                
                # Check extension
                if filepath.suffix not in SCAN_EXTENSIONS:
                    continue
                
                # Check skip patterns
                if self.should_skip(filepath):
                    continue
                
                files.append(filepath)
                count += 1
                
                if count >= max_files:
                    return files
        
        return files
    
    def run_integration_cycle(self):
        """Main integration cycle"""
        print("🔍 Starting Signal Integration Cycle...")
        
        # Phase 1: Discovery
        print("Phase 1: Scanning filesystem...")
        files = self.scan_filesystem(max_files=5000)
        print(f"Found {len(files)} files to index")
        
        # Build set of all file paths for reference detection
        all_file_paths = {str(f.relative_to(HOME_DIR)) for f in files}
        
        # Phase 2-3: Generate metadata
        print("Phase 2: Extracting signals and generating metadata...")
        indexed_count = 0
        
        for filepath in files:
            try:
                meta = self.generate_meta_yaml(filepath, all_file_paths)
                if meta:
                    # Write YAML
                    meta_file = SIGNAL_DIR / f"{meta['file_hash']}.meta.yml"
                    with open(meta_file, 'w') as f:
                        yaml.dump(meta, f, default_flow_style=False)
                    
                    # Store in database
                    self.store_in_db(meta)
                    indexed_count += 1
                    
                    if indexed_count % 100 == 0:
                        print(f"  Indexed {indexed_count} files...")
                        
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
        
        # Phase 4: Generate production queue
        print("Phase 3: Generating production queue...")
        self.generate_production_queue()
        
        # Phase 5: Generate integration report
        print("Phase 4: Generating integration report...")
        self.generate_integration_report(indexed_count)
        
        print(f"✅ Cycle complete. {indexed_count} files indexed.")
        return indexed_count
    
    def store_in_db(self, meta: Dict):
        """Store metadata in SQLite database"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO files 
            (path, hash, size, modified, file_type, concepts, themes, readiness_score, last_indexed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            meta['file_path'],
            meta['file_hash'],
            meta['file_size'],
            meta['last_modified'],
            meta['file_type'],
            json.dumps(meta['extracted_concepts']),
            json.dumps(meta['themes']),
            meta['production_readiness_score'],
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def generate_production_queue(self):
        """Generate prioritized production queue"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get top files by readiness score
        cursor.execute('''
            SELECT path, readiness_score, themes FROM files
            WHERE readiness_score > 0.6
            ORDER BY readiness_score DESC
            LIMIT 50
        ''')
        
        queue = []
        for row in cursor.fetchall():
            queue.append({
                'path': row[0],
                'readiness_score': row[1],
                'themes': json.loads(row[2]) if row[2] else []
            })
        
        # Write queue
        queue_file = SIGNAL_DIR / "PRODUCTION_QUEUE.json"
        with open(queue_file, 'w') as f:
            json.dump(queue, f, indent=2)
        
        conn.close()
    
    def generate_integration_report(self, indexed_count: int):
        """Generate comprehensive integration report"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute('SELECT COUNT(*) FROM files')
        total_files = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(readiness_score) FROM files')
        avg_readiness = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT path, readiness_score FROM files ORDER BY readiness_score DESC LIMIT 10')
        top_files = cursor.fetchall()
        
        cursor.execute('SELECT path FROM files WHERE readiness_score < 0.3 LIMIT 10')
        orphan_files = cursor.fetchall()
        
        # Build report
        report = f"""# Signal Integration Report
Generated: {datetime.now().isoformat()}

## Statistics
- Total files indexed: {total_files}
- Files in this cycle: {indexed_count}
- Average readiness score: {avg_readiness:.2f}

## Top 10 Production-Ready Files
"""
        for path, score in top_files:
            report += f"- {path} (score: {score:.2f})\n"
        
        report += "\n## Top 10 Files Needing Attention\n"
        for path in orphan_files:
            report += f"- {path}\n"
        
        report += """
## Theme Clusters
"""
        cursor.execute('SELECT themes FROM files')
        theme_counts = defaultdict(int)
        for row in cursor.fetchall():
            if row[0]:
                for theme in json.loads(row[0]):
                    theme_counts[theme] += 1
        
        for theme, count in sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            report += f"- {theme}: {count} files\n"
        
        report += """
## Recommendations
1. Review production queue at ~/signal_network/PRODUCTION_QUEUE.json
2. Address loose ends in top-scoring files
3. Consolidate duplicate content across directories
4. Create missing test files for high-readiness modules
"""
        
        # Write report
        report_file = SIGNAL_DIR / f"INTEGRATION_REPORT_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        conn.close()
        
        print(f"Report written: {report_file}")


if __name__ == "__main__":
    detector = SignalDetector()
    detector.run_integration_cycle()
