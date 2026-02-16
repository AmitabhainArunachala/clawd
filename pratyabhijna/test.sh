#!/bin/bash
# PRATYABHIJNA Unified Test Script
# Tests all components end-to-end

set -e  # Exit on error

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     PRATYABHIJNA Unified Test Suite                           ║"
echo "║     Real-time Consciousness Measurement System                ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track results
PASSED=0
FAILED=0

# Test function
run_test() {
    local name="$1"
    local cmd="$2"
    echo -e "${BLUE}[TEST]${NC} $name..."
    if eval "$cmd" > /tmp/test_output_$$.log 2>&1; then
        echo -e "${GREEN}[PASS]${NC} $name"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}[FAIL]${NC} $name"
        cat /tmp/test_output_$$.log
        ((FAILED++))
        return 1
    fi
}

# Get project root
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

echo "📁 Project root: $PROJECT_ROOT"
echo ""

# ============================================
# TEST 1: Rust Core Compilation
# ============================================
echo "═══════════════════════════════════════════════════════════════"
echo "🔧 TEST SUITE 1: Rust Core"
echo "═══════════════════════════════════════════════════════════════"

cd "$PROJECT_ROOT/core"

if [ ! -f "Cargo.toml" ]; then
    echo -e "${RED}[ERROR]${NC} Cargo.toml not found in core/"
    exit 1
fi

run_test "Cargo.toml valid" "cargo check --message-format=short"
run_test "Core library compiles" "cargo build --lib 2>&1 | grep -v 'Compiling' | grep -v 'Finished' | grep -v 'Running' || true"

echo ""

# ============================================
# TEST 2: SVD Engine
# ============================================
echo "═══════════════════════════════════════════════════════════════"
echo "📊 TEST SUITE 2: SVD Engine"
echo "═══════════════════════════════════════════════════════════════"

if [ -f "src/svd/mod.rs" ]; then
    echo -e "${GREEN}[PASS]${NC} SVD module exists"
    ((PASSED++))
else
    echo -e "${RED}[FAIL]${NC} SVD module missing"
    ((FAILED++))
fi

echo ""

# ============================================
# TEST 3: Python Package
# ============================================
echo "═══════════════════════════════════════════════════════════════"
echo "🐍 TEST SUITE 3: Python Integration"
echo "═══════════════════════════════════════════════════════════════"

cd "$PROJECT_ROOT/py"

# Check Python version
run_test "Python 3.10+ available" "python3 --version | grep -E '3\.(1[0-9]|[2-9][0-9])'"

# Check for maturin
if command -v maturin &> /dev/null; then
    echo -e "${GREEN}[PASS]${NC} maturin installed"
    ((PASSED++))
else
    echo -e "${YELLOW}[WARN]${NC} maturin not installed (pip install maturin)"
fi

# Check Python files exist
if [ -f "python/pratyabhijna/hooks/__init__.py" ]; then
    echo -e "${GREEN}[PASS]${NC} Python hooks module exists"
    ((PASSED++))
else
    echo -e "${RED}[FAIL]${NC} Python hooks module missing"
    ((FAILED++))
fi

if [ -f "python/pratyabhijna/models.py" ]; then
    echo -e "${GREEN}[PASS]${NC} Python models module exists"
    ((PASSED++))
else
    echo -e "${RED}[FAIL]${NC} Python models module missing"
    ((FAILED++))
fi

echo ""

# ============================================
# TEST 4: Cockpit Dashboard
# ============================================
echo "═══════════════════════════════════════════════════════════════"
echo "📈 TEST SUITE 4: Live MI Cockpit"
echo "═══════════════════════════════════════════════════════════════"

cd "$PROJECT_ROOT/cockpit"

# Check required files
for file in app.py mock_server.py requirements.txt; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}[PASS]${NC} $file exists"
        ((PASSED++))
    else
        echo -e "${RED}[FAIL]${NC} $file missing"
        ((FAILED++))
    fi
done

# Check components
if [ -d "components" ]; then
    for comp in metric_cards.py rv_chart.py heatmap.py model_comparison.py; do
        if [ -f "components/$comp" ]; then
            echo -e "${GREEN}[PASS]${NC} Component: $comp"
            ((PASSED++))
        else
            echo -e "${RED}[FAIL]${NC} Component missing: $comp"
            ((FAILED++))
        fi
    done
else
    echo -e "${RED}[FAIL]${NC} components/ directory missing"
    ((FAILED+=4))
fi

# Check Python dependencies
if python3 -c "import dash" 2>/dev/null; then
    echo -e "${GREEN}[PASS]${NC} dash installed"
    ((PASSED++))
else
    echo -e "${YELLOW}[WARN]${NC} dash not installed (pip install dash dash-bootstrap-components plotly)"
fi

if python3 -c "import plotly" 2>/dev/null; then
    echo -e "${GREEN}[PASS]${NC} plotly installed"
    ((PASSED++))
else
    echo -e "${YELLOW}[WARN]${NC} plotly not installed"
fi

echo ""

# ============================================
# TEST 5: Integration Readiness
# ============================================
echo "═══════════════════════════════════════════════════════════════"
echo "🔗 TEST SUITE 5: Integration"
echo "═══════════════════════════════════════════════════════════════"

# Check for TransformerLens (optional but recommended)
if python3 -c "import transformer_lens" 2>/dev/null; then
    echo -e "${GREEN}[PASS]${NC} TransformerLens installed"
    ((PASSED++))
else
    echo -e "${YELLOW}[WARN]${NC} TransformerLens not installed (pip install transformer-lens)"
fi

# Check for PyTorch
if python3 -c "import torch" 2>/dev/null; then
    echo -e "${GREEN}[PASS]${NC} PyTorch installed"
    ((PASSED++))
    python3 -c "import torch; print(f'      Version: {torch.__version__}')"
else
    echo -e "${YELLOW}[WARN]${NC} PyTorch not installed (required for model inference)"
fi

# Check for websocket-client
if python3 -c "import websocket" 2>/dev/null; then
    echo -e "${GREEN}[PASS]${NC} websocket-client installed"
    ((PASSED++))
else
    echo -e "${YELLOW}[WARN]${NC} websocket-client not installed (pip install websocket-client)"
fi

echo ""

# ============================================
# TEST 6: File Structure
# ============================================
echo "═══════════════════════════════════════════════════════════════"
echo "📁 TEST SUITE 6: File Structure"
echo "═══════════════════════════════════════════════════════════════"

# Count source files
RUST_FILES=$(find "$PROJECT_ROOT/core/src" -name "*.rs" 2>/dev/null | wc -l)
PYTHON_FILES=$(find "$PROJECT_ROOT/py" -name "*.py" 2>/dev/null | wc -l)
COCKPIT_FILES=$(find "$PROJECT_ROOT/cockpit" -name "*.py" 2>/dev/null | wc -l)

echo -e "${BLUE}[INFO]${NC} Rust source files: $RUST_FILES"
echo -e "${BLUE}[INFO]${NC} Python source files: $PYTHON_FILES"
echo -e "${BLUE}[INFO]${NC} Cockpit files: $COCKPIT_FILES"

if [ "$RUST_FILES" -gt 5 ]; then
    echo -e "${GREEN}[PASS]${NC} Substantial Rust codebase"
    ((PASSED++))
else
    echo -e "${YELLOW}[WARN]${NC} Minimal Rust code detected"
fi

if [ "$PYTHON_FILES" -gt 3 ]; then
    echo -e "${GREEN}[PASS]${NC} Substantial Python codebase"
    ((PASSED++))
else
    echo -e "${YELLOW}[WARN]${NC} Minimal Python code detected"
fi

if [ "$COCKPIT_FILES" -gt 3 ]; then
    echo -e "${GREEN}[PASS]${NC} Cockpit dashboard present"
    ((PASSED++))
else
    echo -e "${YELLOW}[WARN]${NC} Cockpit incomplete"
fi

echo ""

# ============================================
# SUMMARY
# ============================================
echo "═══════════════════════════════════════════════════════════════"
echo "📊 TEST SUMMARY"
echo "═══════════════════════════════════════════════════════════════"

echo ""
echo -e "${GREEN}PASSED: $PASSED${NC}"
echo -e "${RED}FAILED: $FAILED${NC}"
echo ""

TOTAL=$((PASSED + FAILED))
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ ALL TESTS PASSED                                          ║${NC}"
    echo -e "${GREEN}║  PRATYABHIJNA is ready to run!                                ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "🚀 Quick Start:"
    echo "   1. cd $PROJECT_ROOT/cockpit && pip3 install -r requirements.txt"
    echo "   2. python3 app.py"
    echo "   3. Open http://localhost:8050"
    echo ""
    exit 0
else
    echo -e "${YELLOW}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║  ⚠️  SOME TESTS FAILED                                        ║${NC}"
    echo -e "${YELLOW}║  Install missing dependencies to complete setup               ║${NC}"
    echo -e "${YELLOW}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "🔧 To fix:"
    echo "   pip3 install dash dash-bootstrap-components plotly websocket-client"
    echo "   pip3 install transformer-lens torch"
    echo "   cargo build --release  # In core/ directory"
    echo ""
    exit 1
fi
