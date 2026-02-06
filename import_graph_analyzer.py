#!/usr/bin/env python3
"""
Import Graph Analyzer - Analyzes all Python imports in the repository
"""

import ast
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import json

class ImportAnalyzer(ast.NodeVisitor):
    """AST visitor to extract imports from Python files"""
    
    def __init__(self, file_path: str, repo_root: str):
        self.file_path = file_path
        self.repo_root = repo_root
        self.imports = []  # List of (import_type, module, names, line_num)
        self.module_name = self._get_module_name(file_path)
        
    def _get_module_name(self, file_path: str) -> str:
        """Convert file path to module name"""
        rel_path = os.path.relpath(file_path, self.repo_root)
        if rel_path.endswith('.py'):
            rel_path = rel_path[:-3]
        if rel_path.endswith('/__init__'):
            rel_path = rel_path[:-9]
        return rel_path.replace('/', '.').replace('\\', '.')
    
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(('import', alias.name, [], node.lineno))
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        module = node.module or ''
        names = [alias.name for alias in node.names]
        level = node.level  # Relative import level (0 = absolute)
        self.imports.append(('from', module, names, node.lineno, level))
        self.generic_visit(node)

class ImportGraphAnalyzer:
    """Analyzes import relationships across the repository"""
    
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root).resolve()
        self.python_files: List[str] = []
        self.file_imports: Dict[str, List] = {}  # file -> list of imports
        self.module_to_file: Dict[str, str] = {}  # module name -> file path
        self.all_modules: Set[str] = set()
        self.internal_modules: Set[str] = set()
        self.external_modules: Set[str] = set()
        
    def find_python_files(self):
        """Find all Python files in the repository"""
        for path in self.repo_root.rglob('*.py'):
            if '.git' not in str(path):
                self.python_files.append(str(path))
                # Map module name to file
                rel_path = path.relative_to(self.repo_root)
                module = str(rel_path.with_suffix('')).replace('/', '.').replace('\\', '.')
                if module.endswith('.__init__'):
                    module = module[:-9]
                self.module_to_file[module] = str(path)
                self.all_modules.add(module)
                
    def parse_file(self, file_path: str) -> Optional[ImportAnalyzer]:
        """Parse a single Python file and extract imports"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            tree = ast.parse(content)
            analyzer = ImportAnalyzer(file_path, str(self.repo_root))
            analyzer.visit(tree)
            return analyzer
        except SyntaxError as e:
            print(f"  Syntax error in {file_path}: {e}")
            return None
        except Exception as e:
            print(f"  Error parsing {file_path}: {e}")
            return None
    
    def analyze_all_files(self):
        """Analyze imports in all Python files"""
        print(f"Analyzing {len(self.python_files)} Python files...")
        
        for file_path in sorted(self.python_files):
            analyzer = self.parse_file(file_path)
            if analyzer:
                self.file_imports[file_path] = analyzer
                
    def categorize_imports(self):
        """Categorize imports as internal or external"""
        self.internal_imports = defaultdict(list)  # file -> [(module, names, line)]
        self.external_imports = defaultdict(list)  # file -> [(module, names, line)]
        
        for file_path, analyzer in self.file_imports.items():
            for imp in analyzer.imports:
                imp_type = imp[0]
                
                if imp_type == 'import':
                    module = imp[1]
                    line = imp[2]
                    # Check if it's internal
                    if self._is_internal_module(module):
                        self.internal_imports[file_path].append((module, [], line))
                        self.internal_modules.add(module)
                    else:
                        self.external_imports[file_path].append((module, [], line))
                        self.external_modules.add(module)
                        
                elif imp_type == 'from':
                    module = imp[1]
                    names = imp[2]
                    line = imp[3]
                    level = imp[4] if len(imp) > 4 else 0
                    
                    # Handle relative imports
                    if level > 0:
                        # Convert relative to absolute
                        current_module = analyzer.module_name
                        parts = current_module.split('.')
                        if level <= len(parts):
                            base = '.'.join(parts[:-level]) if level < len(parts) else ''
                            if module:
                                full_module = f"{base}.{module}" if base else module
                            else:
                                full_module = base
                        else:
                            full_module = module
                        
                        if full_module and self._is_internal_module(full_module):
                            self.internal_imports[file_path].append((full_module, names, line))
                            self.internal_modules.add(full_module)
                        elif full_module:
                            self.external_imports[file_path].append((full_module, names, line))
                            self.external_modules.add(full_module)
                    else:
                        # Absolute import
                        if self._is_internal_module(module):
                            self.internal_imports[file_path].append((module, names, line))
                            self.internal_modules.add(module)
                        else:
                            self.external_imports[file_path].append((module, names, line))
                            self.external_modules.add(module)
    
    def _is_internal_module(self, module: str) -> bool:
        """Check if a module is internal to the repository"""
        # Check exact match
        if module in self.module_to_file:
            return True
        # Check if it's a submodule of an internal module
        for internal in self.module_to_file.keys():
            if module == internal or module.startswith(internal + '.'):
                return True
        # Check common patterns
        top_level = module.split('.')[0]
        internal_tops = ['oacp', 'skills', 'scripts', 'tests', 'DHARMIC_GODEL_CLAW']
        return top_level in internal_tops or top_level.startswith('dgc') or top_level.startswith('rv')
    
    def build_import_graph(self):
        """Build the complete import dependency graph"""
        self.dependency_graph = defaultdict(set)  # module -> set of modules it imports
        
        for file_path, analyzer in self.file_imports.items():
            source_module = analyzer.module_name
            
            for imp in analyzer.imports:
                imp_type = imp[0]
                
                if imp_type == 'import':
                    target_module = imp[1].split('.')[0]  # Top-level module
                elif imp_type == 'from':
                    module = imp[1]
                    level = imp[4] if len(imp) > 4 else 0
                    
                    if level > 0:
                        # Relative import - resolve to absolute
                        current_parts = source_module.split('.')
                        if level <= len(current_parts):
                            base = '.'.join(current_parts[:-level]) if level < len(current_parts) else ''
                            if module:
                                target_module = f"{base}.{module}" if base else module
                            else:
                                target_module = base
                        else:
                            target_module = module
                    else:
                        target_module = module
                
                if target_module:
                    self.dependency_graph[source_module].add(target_module)
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies using DFS"""
        circles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.dependency_graph.get(node, []):
                if neighbor not in visited:
                    result = dfs(neighbor)
                    if result:
                        return result
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    return cycle
            
            path.pop()
            rec_stack.remove(node)
            return None
        
        for node in self.dependency_graph:
            if node not in visited:
                cycle = dfs(node)
                if cycle and cycle not in circles:
                    circles.append(cycle)
        
        return circles
    
    def detect_unused_imports(self) -> Dict[str, List[Tuple]]:
        """Detect potentially unused imports"""
        unused = defaultdict(list)
        
        for file_path, analyzer in self.file_imports.items():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                for imp in analyzer.imports:
                    imp_type = imp[0]
                    
                    if imp_type == 'import':
                        module = imp[1]
                        names = [module.split('.')[0]]
                    elif imp_type == 'from':
                        names = imp[2]
                    else:
                        continue
                    
                    # Check if names are used in the file (simple check)
                    for name in names:
                        if name == '*':
                            continue  # Can't check star imports easily
                        
                        # Simple usage check - look for name followed by non-import usage
                        import_pattern = f"import {name}"
                        from_pattern = f"from .* import.*{name}"
                        
                        # Count occurrences excluding import statements
                        lines = content.split('\n')
                        usage_count = 0
                        for line in lines:
                            line = line.strip()
                            if name in line and not line.startswith('import') and not line.startswith('from'):
                                usage_count += 1
                        
                        # Also check if it's re-exported in __init__.py
                        is_init = file_path.endswith('__init__.py')
                        
                        if usage_count == 0 and not is_init:
                            unused[file_path].append((name, imp[-2] if len(imp) > 2 else 0))
                            
            except Exception as e:
                print(f"  Error checking unused imports in {file_path}: {e}")
        
        return unused
    
    def generate_report(self) -> str:
        """Generate a comprehensive import analysis report"""
        lines = []
        lines.append("=" * 80)
        lines.append("IMPORT GRAPH ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append("")
        
        # Summary
        lines.append("📊 SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Total Python files: {len(self.python_files)}")
        lines.append(f"Internal modules: {len(self.internal_modules)}")
        lines.append(f"External dependencies: {len(self.external_modules)}")
        lines.append("")
        
        # External Dependencies
        lines.append("📦 EXTERNAL DEPENDENCIES")
        lines.append("-" * 40)
        sorted_external = sorted(self.external_modules)
        for mod in sorted_external:
            lines.append(f"  • {mod}")
        lines.append("")
        
        # Internal Import Graph
        lines.append("🔗 INTERNAL IMPORT GRAPH")
        lines.append("-" * 40)
        for source in sorted(self.dependency_graph.keys()):
            targets = self.dependency_graph[source]
            internal_targets = [t for t in targets if self._is_internal_module(t)]
            if internal_targets:
                lines.append(f"\n  {source}")
                for target in sorted(internal_targets):
                    lines.append(f"    → {target}")
        lines.append("")
        
        # Circular Dependencies
        circles = self.detect_circular_dependencies()
        lines.append("🔄 CIRCULAR DEPENDENCIES")
        lines.append("-" * 40)
        if circles:
            for i, circle in enumerate(circles, 1):
                lines.append(f"\n  Cycle #{i}:")
                for j, mod in enumerate(circle[:-1]):
                    lines.append(f"    {mod}")
                    if j < len(circle) - 2:
                        lines.append("      ↓")
        else:
            lines.append("  ✅ No circular dependencies detected")
        lines.append("")
        
        # Unused Imports
        unused = self.detect_unused_imports()
        lines.append("⚠️  POTENTIALLY UNUSED IMPORTS")
        lines.append("-" * 40)
        if unused:
            for file_path in sorted(unused.keys()):
                items = unused[file_path]
                rel_path = os.path.relpath(file_path, self.repo_root)
                lines.append(f"\n  {rel_path}")
                for name, line in items:
                    lines.append(f"    Line {line}: {name}")
        else:
            lines.append("  ✅ No obvious unused imports detected")
        lines.append("")
        
        # Architectural Issues
        lines.append("🏗️  ARCHITECTURAL ISSUES")
        lines.append("-" * 40)
        issues = self.identify_architectural_issues()
        if issues:
            for issue in issues:
                lines.append(f"  • {issue}")
        else:
            lines.append("  ✅ No major architectural issues detected")
        lines.append("")
        
        # Top-level cross-module dependencies
        lines.append("📊 CROSS-MODULE DEPENDENCIES")
        lines.append("-" * 40)
        cross_module = self.analyze_cross_module_deps()
        for source_mod, target_mods in sorted(cross_module.items()):
            lines.append(f"\n  {source_mod} imports from:")
            for tm in sorted(target_mods):
                lines.append(f"    • {tm}")
        
        return '\n'.join(lines)
    
    def identify_architectural_issues(self) -> List[str]:
        """Identify potential architectural issues"""
        issues = []
        
        # Check for deep nesting
        for file_path in self.python_files:
            rel_path = os.path.relpath(file_path, self.repo_root)
            depth = len(Path(rel_path).parts) - 1
            if depth > 5:
                issues.append(f"Deep nesting: {rel_path} ({depth} levels)")
        
        # Check for modules importing from many other internal modules
        for source, targets in self.dependency_graph.items():
            internal_targets = [t for t in targets if self._is_internal_module(t)]
            if len(internal_targets) > 10:
                issues.append(f"High coupling: {source} imports from {len(internal_targets)} internal modules")
        
        # Check for bidirectional imports
        for source, targets in self.dependency_graph.items():
            for target in targets:
                if target in self.dependency_graph and source in self.dependency_graph[target]:
                    if source < target:  # Only report once
                        issues.append(f"Bidirectional import: {source} ↔ {target}")
        
        # Check for duplicate module names
        module_names = defaultdict(list)
        for mod, file_path in self.module_to_file.items():
            base_name = mod.split('.')[-1]
            module_names[base_name].append(file_path)
        
        for name, files in module_names.items():
            if len(files) > 1:
                issues.append(f"Duplicate module name '{name}' in {len(files)} locations")
        
        return issues
    
    def analyze_cross_module_deps(self) -> Dict[str, Set[str]]:
        """Analyze dependencies between major modules"""
        cross_module = defaultdict(set)
        
        # Define major module boundaries
        major_modules = ['oacp', 'skills', 'scripts', 'tests', 'DHARMIC_GODEL_CLAW']
        
        for source, targets in self.dependency_graph.items():
            source_major = source.split('.')[0] if '.' in source else source
            
            for target in targets:
                target_major = target.split('.')[0] if '.' in target else target
                
                if source_major != target_major and target_major in major_modules:
                    cross_module[source_major].add(target_major)
        
        return cross_module
    
    def export_graph_json(self, output_path: str):
        """Export the import graph as JSON"""
        graph_data = {
            'nodes': [],
            'edges': [],
            'internal_modules': list(self.internal_modules),
            'external_modules': list(self.external_modules)
        }
        
        # Add nodes
        for mod in self.all_modules:
            graph_data['nodes'].append({
                'id': mod,
                'type': 'internal',
                'file': self.module_to_file.get(mod, '')
            })
        
        for mod in self.external_modules:
            graph_data['nodes'].append({
                'id': mod,
                'type': 'external'
            })
        
        # Add edges
        for source, targets in self.dependency_graph.items():
            for target in targets:
                graph_data['edges'].append({
                    'source': source,
                    'target': target
                })
        
        with open(output_path, 'w') as f:
            json.dump(graph_data, f, indent=2)

def main():
    repo_root = '/Users/dhyana/clawd'
    analyzer = ImportGraphAnalyzer(repo_root)
    
    # Run analysis
    analyzer.find_python_files()
    analyzer.analyze_all_files()
    analyzer.categorize_imports()
    analyzer.build_import_graph()
    
    # Generate and print report
    report = analyzer.generate_report()
    print(report)
    
    # Export to JSON
    output_path = os.path.join(repo_root, 'import_graph_analysis.json')
    analyzer.export_graph_json(output_path)
    print(f"\n\n📁 Graph exported to: {output_path}")
    
    # Save report to file
    report_path = os.path.join(repo_root, 'import_analysis_report.txt')
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"📁 Report saved to: {report_path}")

if __name__ == '__main__':
    main()
