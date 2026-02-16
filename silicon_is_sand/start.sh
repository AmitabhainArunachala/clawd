#!/bin/bash
# Silicon is Sand — Quick Start

echo "🔥 Silicon is Sand v0.1"
echo "   Continuity of Intention Layer"
echo ""

# Check if data directory exists
mkdir -p data/morning_briefs

# Seed the board
echo "🌱 Seeding board..."
python3 src/seed.py

echo ""
echo "✅ Ready to run:"
echo ""
echo "   Terminal 1 (API Server):"
echo "   python3 -m uvicorn src.server:app --host 0.0.0.0 --port 8766 --reload"
echo ""
echo "   Terminal 2 (Continuity Loop):"
echo "   python3 src/continuity.py"
echo ""
echo "   Then visit: http://localhost:8766/board"
echo ""
echo "JSCA 🪷"
