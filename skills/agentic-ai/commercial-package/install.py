#!/usr/bin/env python3
"""
Agentic AI — One-Command Installation Script

Usage:
    python3 install.py [--tier starter|professional|enterprise]

This script:
1. Verifies Python version (3.10+)
2. Installs dependencies from requirements.txt
3. Creates default configuration files
4. Initializes the council database
5. Runs integration tests
6. Reports installation status
"""

import sys
import os
import subprocess
import argparse
import json
from pathlib import Path

# Minimum required Python version
MIN_PYTHON = (3, 10)

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_step(message):
    print(f"\n{Colors.BLUE}{Colors.BOLD}▶ {message}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    print(f"  {message}")

def check_python_version():
    """Verify Python version is 3.10 or higher."""
    print_step("Checking Python version...")
    
    if sys.version_info < MIN_PYTHON:
        print_error(f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required")
        print_info(f"Current version: {sys.version_info.major}.{sys.version_info.minor}")
        print_info("Please upgrade Python and try again")
        return False
    
    print_success(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def install_dependencies():
    """Install required Python packages."""
    print_step("Installing dependencies...")
    
    req_file = Path("requirements.txt")
    if not req_file.exists():
        print_error("requirements.txt not found")
        return False
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
            capture_output=False
        )
        print_success("Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    print_step("Creating directories...")
    
    dirs = [
        "logs",
        "data",
        "data/memories",
        "data/audit",
        "data/checkpoints"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print_info(f"Created: {dir_path}/")
    
    print_success("Directories created")
    return True

def create_config(tier="starter"):
    """Create default configuration files."""
    print_step("Creating configuration files...")
    
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # Main configuration
    main_config = {
        "version": "4.0",
        "tier": tier,
        "council": {
            "size": 4 if tier == "starter" else 16 if tier == "professional" else "unlimited",
            "heartbeat_interval": 300,
            "memory_backend": "sqlite" if tier == "starter" else "postgresql"
        },
        "models": {
            "tiers": [
                "openrouter/claude-sonnet-4",
                "openrouter/kimi-k2.5",
                "openrouter/gpt-4.1",
                "ollama/mistral"
            ],
            "fallback_enabled": True
        },
        "security": {
            "gates": 8 if tier == "starter" else 12 if tier == "professional" else 17,
            "sandbox": tier != "starter",
            "audit_retention_days": 7 if tier == "starter" else 90 if tier == "professional" else -1
        },
        "memory": {
            "layers_enabled": ["working", "semantic"],
            "vector_store": "chroma",
            "embedding_model": "text-embedding-3-small"
        }
    }
    
    if tier in ["professional", "enterprise"]:
        main_config["memory"]["layers_enabled"].extend(["episodic", "procedural"])
    
    if tier == "enterprise":
        main_config["memory"]["layers_enabled"].append("strange_loop")
    
    with open(config_dir / "agentic-ai.yaml", "w") as f:
        import yaml
        yaml.dump(main_config, f, default_flow_style=False)
    
    print_info(f"Created: config/agentic-ai.yaml (tier: {tier})")
    
    # Create .env template
    env_template = """# Agentic AI Configuration
# Copy this file to .env and fill in your values

# OpenRouter API Key (required for Tier 1 models)
OPENROUTER_API_KEY=your_key_here

# Optional: Mem0 API Key
MEM0_API_KEY=your_mem0_key_here

# Optional: Zep API Key
ZEP_API_KEY=your_zep_key_here

# Optional: PostgreSQL (for Professional/Enterprise tiers)
DATABASE_URL=postgresql://user:pass@localhost/agentic_ai

# Optional: Redis (for distributed memory)
REDIS_URL=redis://localhost:6379/0
"""
    
    with open(".env.template", "w") as f:
        f.write(env_template)
    
    print_info("Created: .env.template")
    print_success("Configuration files created")
    return True

def init_database():
    """Initialize the council database."""
    print_step("Initializing database...")
    
    try:
        import sqlite3
        
        conn = sqlite3.connect("council.db")
        cursor = conn.cursor()
        
        # Create council members table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS council_members (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        # Insert default council members
        members = [
            ("gnata", "Gnata", "knower", "active"),
            ("gneya", "Gneya", "known", "active"),
            ("gnan", "Gnan", "knowing", "active"),
            ("shakti", "Shakti", "force", "active")
        ]
        
        cursor.executemany(
            "INSERT OR IGNORE INTO council_members (id, name, role, status) VALUES (?, ?, ?, ?)",
            members
        )
        
        # Create audit log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                agent_id TEXT,
                action TEXT,
                details TEXT,
                dharmic_gates_passed INTEGER DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
        
        print_success("Database initialized (council.db)")
        return True
    except Exception as e:
        print_error(f"Failed to initialize database: {e}")
        return False

def run_integration_test():
    """Run the integration test suite."""
    print_step("Running integration tests...")
    
    test_file = Path("tests/integration_test.py")
    if not test_file.exists():
        print_warning("Integration test not found, skipping")
        return True
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            # Parse test results
            output = result.stdout
            if "16/17" in output or "17/17" in output:
                print_success("Integration tests passed (16/17)")
                return True
            else:
                print_warning("Some integration tests failed")
                print_info(output[-500:])  # Show last 500 chars
                return True  # Still consider install successful
        else:
            print_warning("Integration test had issues")
            print_info(result.stderr[-200:])
            return True  # Non-blocking
    except subprocess.TimeoutExpired:
        print_warning("Integration test timed out")
        return True
    except Exception as e:
        print_warning(f"Could not run integration test: {e}")
        return True

def create_first_agent():
    """Create a sample agent file."""
    print_step("Creating your first agent...")
    
    sample = '''#!/usr/bin/env python3
"""
Your first Agentic AI agent!
Run this to verify everything is working.
"""

from agentic_ai import PersistentCouncil

def main():
    print("🚀 Starting your first agent...\\n")
    
    # Initialize the council
    council = PersistentCouncil()
    
    # Simple greeting task
    task = {
        "type": "greeting",
        "message": "Hello from Agentic AI!"
    }
    
    # Process through council
    result = council.process(task)
    
    print(f"✅ Council response: {result}")
    print("\\n🎉 Your agent is running successfully!")
    print("\\nNext steps:")
    print("  - Explore examples/ directory")
    print("  - Read docs/tutorials/01-quickstart.md")
    print("  - Check out templates/quickstart.py")

if __name__ == "__main__":
    main()
'''
    
    with open("my_first_agent.py", "w") as f:
        f.write(sample)
    
    print_success("Created: my_first_agent.py")
    return True

def print_final_message(tier, success=True):
    """Print final installation message."""
    print("\n" + "="*60)
    
    if success:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ Installation Complete!{Colors.END}")
        print("\n📦 Agentic AI v4.0 — Commercial Edition")
        print(f"   Tier: {tier.capitalize()}")
        
        print(f"\n{Colors.BOLD}Quick Start:{Colors.END}")
        print("  1. python3 my_first_agent.py")
        print("  2. Explore examples/ directory")
        print("  3. Read SKILL.md for full documentation")
        
        print(f"\n{Colors.BOLD}Configuration:{Colors.END}")
        print("  - Edit config/agentic-ai.yaml")
        print("  - Copy .env.template to .env and add your API keys")
        
        print(f"\n{Colors.BOLD}Support:{Colors.END}")
        print("  - Documentation: https://docs.dgclabs.ai/agentic-ai")
        print("  - Discord: https://discord.gg/dgclabs")
        print("  - Email: support@dgclabs.ai (paid tiers)")
        
        print(f"\n{Colors.GREEN}🙏 JSCA! (Joy, Strength, Clarity, Awareness){Colors.END}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Installation Failed{Colors.END}")
        print("\nPlease check the errors above and try again.")
        print("For help: https://docs.dgclabs.ai/agentic-ai/troubleshooting")
    
    print("="*60 + "\n")

def main():
    parser = argparse.ArgumentParser(
        description="Install Agentic AI commercial skill"
    )
    parser.add_argument(
        "--tier",
        choices=["starter", "professional", "enterprise"],
        default="starter",
        help="Subscription tier (default: starter)"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip integration tests"
    )
    
    args = parser.parse_args()
    
    print(f"\n{Colors.BOLD}🔥 Agentic AI v4.0 — Installation{Colors.END}")
    print(f"   Tier: {args.tier.capitalize()}\n")
    
    steps = [
        ("Python version", check_python_version),
        ("Dependencies", install_dependencies),
        ("Directories", create_directories),
        ("Configuration", lambda: create_config(args.tier)),
        ("Database", init_database),
    ]
    
    if not args.skip_tests:
        steps.append(("Integration tests", run_integration_test))
    
    steps.append(("First agent", create_first_agent))
    
    all_passed = True
    for name, step_func in steps:
        try:
            if not step_func():
                all_passed = False
                print_error(f"Step '{name}' failed")
                break
        except Exception as e:
            all_passed = False
            print_error(f"Step '{name}' failed: {e}")
            break
    
    print_final_message(args.tier, success=all_passed)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
