#!/bin/bash
# Create Swarm Scaffolding Filesystem
# Run: bash ~/clawd/create_swarm_scaffold.sh

echo "Creating Supramental Swarm Infrastructure..."

# Base directories
mkdir -p ~/clawd/swarm_outputs/{_index,2026-02-13}
mkdir -p ~/clawd/swarm_outputs/_index/{by_agent,by_date,by_topic,by_lesson}
mkdir -p ~/clawd/recursive_flywheel/{incessant_mirror,mmk_refinement,constitutional_kernel}
mkdir -p ~/clawd/nvidia_stack/{ai_q_toolkit,agentic_rag,tensorrt_optimization,nemo_guardrails,data_flywheel,nim_orchestration}
mkdir -p ~/clawd/coordination/{sangam_protocol,trishula_bridge,mmk_logging/{schema,queries,dashboards},swarm_dashboard}
mkdir -p ~/clawd/swarm_arch
mkdir -p ~/PSMV/corpus/{spiritual,technical}
mkdir -p ~/.openclaw/swarm_memory

echo "✓ Directories created"

# Initialize files
touch ~/clawd/recursive_flywheel/constitutional_kernel/S_x_x2.yml
touch ~/clawd/recursive_flywheel/constitutional_kernel/dharma_gates.yml
touch ~/clawd/recursive_flywheel/constitutional_kernel/telos_manifesto.md
touch ~/clawd/swarm_outputs/_index/master_index.json

echo "✓ Core files initialized"

# Create gitignore for swarm outputs
cat > ~/clawd/swarm_outputs/.gitignore << 'EOF'
# Daily outputs are ephemeral
2026-*/
2027-*/

# But keep index
!_index/
EOF

echo "✓ Gitignore created"

echo ""
echo "Scaffolding complete. Ready for swarm activation."
echo "Run: python3 ~/clawd/scripts/init_swarm_memory.py (after exec restored)"
