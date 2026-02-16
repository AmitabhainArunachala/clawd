#!/bin/bash
# PRATYABHIJNA Quick Test - Fast validation without compilation

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     PRATYABHIJNA Quick Test                                   ║"
echo "║     Validate without building                                 ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

PASSED=0
FAILED=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $2"
        ((FAILED++))
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $2"
        ((FAILED++))
    fi
}

echo "📁 Structure Check"
echo "───────────────────────────────────────────────────────────────"
check_file "core/Cargo.toml" "Rust core manifest"
check_file "core/src/main.rs" "Rust broker entry point"
check_file "core/src/lib.rs" "Rust library root"
check_dir "core/src/svd" "SVD engine module"
check_file "core/src/websocket/mod.rs" "WebSocket module"
check_file "core/src/database/mod.rs" "Database module"
check_file "core/src/recognition/mod.rs" "Recognition detector"

echo ""
echo "🐍 Python Bridge Check"
echo "───────────────────────────────────────────────────────────────"
check_file "py/Cargo.toml" "PyO3 FFI manifest"
check_file "py/src/lib.rs" "PyO3 bindings"
check_file "py/python/pratyabhijna/__init__.py" "Python package init"
check_file "py/python/pratyabhijna/models.py" "Model loader"
check_file "py/python/pratyabhijna/hooks/__init__.py" "TransformerLens hooks"

echo ""
echo "📊 Cockpit Dashboard Check"
echo "───────────────────────────────────────────────────────────────"
check_file "cockpit/app.py" "Main Dash application"
check_file "cockpit/mock_server.py" "Mock WebSocket server"
check_file "cockpit/requirements.txt" "Python dependencies"
check_file "cockpit/components/metric_cards.py" "Metric cards component"
check_file "cockpit/components/rv_chart.py" "R_V chart component"
check_file "cockpit/components/heatmap.py" "Heatmap component"
check_file "cockpit/components/model_comparison.py" "Model comparison component"

echo ""
echo "📚 Documentation Check"
echo "───────────────────────────────────────────────────────────────"
check_file "README.md" "Project README"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "📊 RESULTS: $PASSED passed, $FAILED failed"
echo "═══════════════════════════════════════════════════════════════"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ PRATYABHIJNA structure complete!${NC}"
    echo ""
    echo "🚀 To run the dashboard (no Rust needed):"
    echo "   cd ~/clawd/pratyabhijna/cockpit"
    echo "   pip3 install -r requirements.txt"
    echo "   python3 app.py"
    echo ""
    echo "🔧 To build and run full system:"
    echo "   cd ~/clawd/pratyabhijna/core && cargo build --release"
    echo "   ./target/release/pratyabhijna-core"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠️  Some components missing${NC}"
    exit 1
fi
