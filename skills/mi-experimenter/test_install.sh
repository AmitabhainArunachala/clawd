#!/bin/bash
# Quick test script for mi-experimenter

export PYTHONPATH="$HOME/clawd/skills:$HOME/mech-interp-latent-lab-phase1"

echo "🔬 MI Experimenter Smoke Test"
echo "============================="
echo ""

python3 -c "
from mi_experimenter import RVCausalValidator, ModelLoader, HookManager
from mi_experimenter import CrossArchitectureSuite, MLPAblator

print('✓ RVCausalValidator imported')
print('✓ ModelLoader imported')
print('✓ HookManager imported')
print('✓ CrossArchitectureSuite imported')
print('✓ MLPAblator imported')
print('')
print('All core imports successful!')
print('Python path configured correctly.')
"
