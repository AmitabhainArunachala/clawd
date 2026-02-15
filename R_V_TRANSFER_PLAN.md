# R_V Transfer Plan
## mech-interp-latent-lab-phase1 → Target Environment

**Plan ID:** PULSE-004  
**Generated:** 2026-02-15 17:13 GMT+8  
**Total Audit Duration:** ~15 minutes  
**Estimated Transfer Time:** 15-30 minutes (depending on bandwidth)  
**Status:** PLANNING ONLY - DO NOT EXECUTE

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Total Size** | 118 MB |
| **Total Files** | 3,500+ files |
| **Python Files** | 372 |
| **Markdown Docs** | 717 |
| **Git History** | 79 MB (67% of total) |
| **External Dependencies** | 15 packages |
| **Internal Dependencies** | 687 cross-module imports |

**Recommendation:** Transfer in 5 chunks, prioritizing code and documentation over git history and archived results.

---

## 1. Directory Structure & Size Breakdown

```
mech-interp-latent-lab-phase1/          118 MB total
├── .git/                                79 MB  (67%) - Version control
├── results/                             17 MB  (14%) - Experimental outputs
├── archive/                             4.6 MB  (4%) - Deprecated scripts
├── src/                                 3.0 MB  (3%) - Core source code
├── docs/                                2.8 MB  (2%) - Documentation
├── R_V_PAPER/                           1.6 MB  (1%) - Publication materials
├── prompts/                             1.4 MB  (1%) - Prompt banks
├── website/                             1.1 MB  (1%) - Web assets
├── rv_toolkit/                          1.0 MB  (1%) - Reusable toolkit
├── configs/                             1.0 MB  (1%) - Configuration files
├── CANONICAL_CODE/                      212 KB    - Validated experiments
├── RECOVERED_GOLD/                       88 KB    - Critical findings
├── agent_reviews/                       152 KB    - Multi-agent audit results
├── kaizen/                              108 KB    - TPS monitoring system
├── visualizations/                      256 KB    - Manim/3D animations
├── experiments/                          72 KB    - Experiment configs
├── models/                               60 KB    - Model analysis scripts
├── scripts/                             308 KB    - Utility scripts
├── *.ipynb                              940 KB    - Jupyter notebooks
├── *.md                               ~2.0 MB    - Root documentation
└── requirements.txt                       4 KB    - Dependencies
```

---

## 2. Critical Files Inventory

### 2.1 Must-Have (Core System)
| File/Dir | Size | Purpose |
|----------|------|---------|
| `src/` | 3.0 MB | Core library (models, metrics, pipelines) |
| `rv_toolkit/` | 1.0 MB | Reusable research toolkit |
| `prompts/` | 1.4 MB | Prompt bank (333KB bank.json) |
| `requirements.txt` | 4 KB | Dependency specification |
| `config.yaml` | 4 KB | Agent swarm configuration |
| `CANONICAL_CODE/` | 212 KB | Validated experimental code |

### 2.2 High Priority (Documentation & Knowledge)
| File/Dir | Size | Purpose |
|----------|------|---------|
| `README.md` | 12 KB | Entry point documentation |
| `ARCHITECTURE.md` | 12 KB | System architecture |
| `RECOVERED_GOLD/` | 88 KB | Breakthrough findings |
| `R_V_PAPER/` | 1.6 MB | Publication figures + PDF |
| `docs/` | 2.8 MB | Full documentation |
| `agent_reviews/` | 152 KB | Multi-agent audit history |

### 2.3 Optional/Archival
| File/Dir | Size | Purpose |
|----------|------|---------|
| `.git/` | 79 MB | Full version history |
| `results/` | 17 MB | Experimental outputs (regeneratable) |
| `archive/` | 4.6 MB | Deprecated scripts |
| `visualizations/` | 256 KB | Manim animation source |

---

## 3. Dependency Analysis

### 3.1 External Dependencies (15 packages, 979 imports)

**Core ML Stack (Required):**
| Package | Count | Version Range |
|---------|-------|---------------|
| torch | 220 | >=2.1.0,<2.2.0 |
| numpy | 191 | >=1.26.0,<2.0.0 |
| transformers | 118 | >=4.36.0,<4.37.0 |
| pandas | 162 | >=2.1.0,<3.0.0 |
| scipy | 68 | >=1.12.0,<2.0.0 |
| tqdm | 101 | >=4.66.0 |

**Visualization (Optional):**
| Package | Count | Purpose |
|---------|-------|---------|
| matplotlib | 17 | Basic plotting |
| seaborn | 8 | Statistical viz |
| manim | 12 | 3D animations |

**Dev/Testing:**
| Package | Count | Purpose |
|---------|-------|---------|
| pytest | 5 | Testing framework |
| sklearn | 3 | ML utilities |

### 3.2 Internal Dependencies (687 imports)

**High Fan-In Modules (Critical):**
```
prompts.loader           103 incoming deps  ← Universal prompt loading
src.core.models           99 incoming deps  ← Foundation model interface
src.metrics.rv            75 incoming deps  ← Core R_V metric
src.pipelines.registry    58 incoming deps  ← Central pipeline registry
```

**Dependency Chain:**
```
scripts/ → pipelines/ → metrics/ → core/
    ↓           ↓           ↓         ↓
  high     moderate      high     critical
```

**Circular Dependencies (6 self-loops detected):**
- `NOV_16_Mixtral_free_play.py`
- `REUSABLE_PROMPT_BANK` (init file)
- `src.core.model_physics`
- `src.metrics.baseline_suite`
- `mistral_patching_FINAL.py`
- `test_ssh_paramiko.py`

*Note: These are module-level self-imports, likely re-export patterns. Safe to ignore.*

---

## 4. Chunked Transfer Strategy

### Strategy Rationale
- **Chunk 1-3:** Core functionality (can run immediately after)
- **Chunk 4:** Documentation (needed for understanding)
- **Chunk 5:** Git history (optional, use shallow clone for speed)
- **Chunk 6:** Large results (can regenerate, transfer selectively)

### Transfer Chunks

#### **CHUNK 1: Core Source** ⭐ CRITICAL FIRST
| Item | Size | Time Est. |
|------|------|-----------|
| `src/` | 3.0 MB | ~30s |
| `rv_toolkit/` | 1.0 MB | ~10s |
| `prompts/` | 1.4 MB | ~15s |
| `scripts/` | 308 KB | ~5s |
| `CANONICAL_CODE/` | 212 KB | ~3s |
| `models/` | 60 KB | ~2s |
| `experiments/` | 72 KB | ~2s |
| `configs/` | 1.0 MB | ~10s |
| `requirements*.txt` | 8 KB | instant |
| `config.yaml` | 4 KB | instant |
| **CHUNK 1 TOTAL** | **~7.1 MB** | **~2 min** |

**Validation Post-Transfer:**
```bash
pip install -r requirements.txt
python -c "from src.core.models import load_model; print('Core OK')"
python -c "from rv_toolkit import R_VToolkit; print('Toolkit OK')"
```

---

#### **CHUNK 2: Documentation & Knowledge**
| Item | Size | Time Est. |
|------|------|-----------|
| `README.md` | 12 KB | instant |
| `ARCHITECTURE.md` | 12 KB | instant |
| `docs/` | 2.8 MB | ~30s |
| `RECOVERED_GOLD/` | 88 KB | ~3s |
| `R_V_PAPER/` | 1.6 MB | ~20s |
| `agent_reviews/` | 152 KB | ~5s |
| `kaizen/` | 108 KB | ~3s |
| Root `*.md` files | ~500 KB | ~10s |
| `REUSABLE_PROMPT_BANK/` | 344 KB | ~5s |
| **CHUNK 2 TOTAL** | **~5.6 MB** | **~1.5 min** |

---

#### **CHUNK 3: Analysis & Visualization**
| Item | Size | Time Est. |
|------|------|-----------|
| `*.ipynb` notebooks | 940 KB | ~10s |
| `visualizations/` | 256 KB | ~5s |
| `website/` | 1.1 MB | ~15s |
| `product/` | 24 KB | instant |
| `references/` | 8 KB | instant |
| **CHUNK 3 TOTAL** | **~2.3 MB** | **~30s** |

---

#### **CHUNK 4: Archive (Deprecated Code)**
| Item | Size | Time Est. |
|------|------|-----------|
| `archive/` | 4.6 MB | ~1 min |
| **CHUNK 4 TOTAL** | **4.6 MB** | **~1 min** |

*Note: Archive contains historical scripts. Not needed for new work but useful for reference.*

---

#### **CHUNK 5: Git History** ⚠️ OPTIONAL
| Item | Size | Time Est. |
|------|------|-----------|
| `.git/` (full) | 79 MB | ~5-10 min |
| `.git/` (shallow, depth=10) | ~5 MB | ~30s |
| **CHUNK 5 TOTAL (full)** | **79 MB** | **~10 min** |

**Shallow Clone Alternative:**
```bash
git clone --depth=10 <repo-url>
# vs full history:
git clone <repo-url>
```

---

#### **CHUNK 6: Results (Regeneratable)** ⚠️ SELECTIVE
| Item | Size | Priority |
|------|------|----------|
| `results/canonical/` | 2.0 MB | HIGH - Keep validated results |
| `results/discovery/` | 2.0 MB | HIGH - Key findings |
| `results/circuit_mapping/` | 1.4 MB | MED - Recent work |
| `results/archive/` | 3.2 MB | LOW - Superseded results |
| Other results | ~8 MB | LOW - Can regenerate |
| **CHUNK 6 TOTAL** | **~17 MB** | **~3 min** |

**Selective Transfer Strategy:**
1. Always transfer: `results/canonical/`, `results/discovery/`
2. Conditional: Recent circuit mapping results (check dates)
3. Skip: `results/archive/` (old superseded runs)

---

## 5. Transfer Commands

### Option A: Full Archive + Extract (Recommended)
```bash
# On source machine
cd ~
tar czf mech-interp-transfer.tar.gz \
  --exclude='.git/objects/pack/*' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.pytest_cache' \
  --exclude='results/archive/superseded' \
  mech-interp-latent-lab-phase1/

# Size: ~40 MB (vs 118 MB original)
# Transfer via rsync/scp
rsync -avz --progress mech-interp-transfer.tar.gz target:/path/

# On target machine
cd /destination
tar xzf mech-interp-transfer.tar.gz
cd mech-interp-latent-lab-phase1
pip install -r requirements.txt
```

### Option B: Git Clone (Cleanest)
```bash
# On target machine
git clone --depth=10 https://github.com/AmitabhainArunachala/mech-interp-latent-lab-phase1.git
cd mech-interp-latent-lab-phase1

# Download large files separately (results, docs)
rsync -avz source:~/mech-interp-latent-lab-phase1/results/canonical/ ./results/canonical/
rsync -avz source:~/mech-interp-latent-lab-phase1/docs/ ./docs/
rsync -avz source:~/mech-interp-latent-lab-phase1/R_V_PAPER/ ./R_V_PAPER/

pip install -r requirements.txt
```

### Option C: Chunked Transfer (Most Control)
```bash
#!/bin/bash
# transfer_chunks.sh

SOURCE=~/mech-interp-latent-lab-phase1
TARGET=user@host:/path/

# Chunk 1: Core (7.1 MB)
rsync -avz --progress \
  $SOURCE/src/ $SOURCE/rv_toolkit/ $SOURCE/prompts/ \
  $SOURCE/scripts/ $SOURCE/CANONICAL_CODE/ \
  $SOURCE/models/ $SOURCE/experiments/ \
  $SOURCE/configs/ $SOURCE/requirements*.txt $SOURCE/config.yaml \
  $TARGET/

# Chunk 2: Docs (5.6 MB)
rsync -avz --progress \
  $SOURCE/README.md $SOURCE/ARCHITECTURE.md \
  $SOURCE/docs/ $SOURCE/RECOVERED_GOLD/ \
  $SOURCE/R_V_PAPER/ $SOURCE/agent_reviews/ \
  $SOURCE/kaizen/ $SOURCE/*.md \
  $SOURCE/REUSABLE_PROMPT_BANK/ \
  $TARGET/

# Chunk 3: Viz (2.3 MB)
rsync -avz --progress \
  $SOURCE/*.ipynb $SOURCE/visualizations/ \
  $SOURCE/website/ $SOURCE/product/ $SOURCE/references/ \
  $TARGET/

# Chunk 4: Archive (4.6 MB)
rsync -avz --progress \
  $SOURCE/archive/ \
  $TARGET/

# Chunk 5: Git (optional, 79 MB)
rsync -avz --progress \
  $SOURCE/.git/ \
  $TARGET/

# Chunk 6: Results (selective, ~6 MB essential)
rsync -avz --progress \
  $SOURCE/results/canonical/ $SOURCE/results/discovery/ \
  $SOURCE/results/circuit_mapping/ \
  $TARGET/results/
```

---

## 6. Post-Transfer Validation Checklist

### 6.1 File Integrity
- [ ] All Python files present (372 expected)
- [ ] `requirements.txt` readable
- [ ] `src/core/models.py` accessible
- [ ] `prompts/bank.json` valid JSON

### 6.2 Environment Setup
```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify imports
python -c "
import torch
import transformers
import numpy
import pandas
print(f'PyTorch: {torch.__version__}')
print(f'Transformers: {transformers.__version__}')
print('Core deps OK')
"

# 4. Verify source imports
python -c "
from src.core.models import load_model
from src.metrics.rv import compute_rv_score
from rv_toolkit import R_VToolkit
print('Internal imports OK')
"

# 5. Quick smoke test
python -c "
from prompts.loader import load_prompt_bank
bank = load_prompt_bank()
print(f'Loaded {len(bank)} prompts')
"
```

### 6.3 Functional Validation
- [ ] Load prompt bank without errors
- [ ] Import src.core.models successfully
- [ ] Import src.metrics.rv successfully
- [ ] Run `reproduce_results.py --dry-run` if available

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Git corruption during transfer | Low | High | Use rsync with checksums; keep backup |
| Missing dependencies on target | Medium | High | Run requirements.txt; verify versions |
| Path/symlink issues | Low | Medium | One symlink detected (swarm-link), check validity |
| Large results bloating transfer | Medium | Low | Use selective transfer for results/ |
| Binary file corruption | Low | High | Verify checksums post-transfer |

---

## 8. Special Considerations

### 8.1 Symlinks
**Detected:** `swarm-link` → `/Users/dhyana/Persistent-Semantic-Memory-Vault/AGENT_EMERGENT_WORKSPACES`

**Action:** This is an external workspace link. Either:
- Skip during transfer (will be broken symlink)
- Create equivalent directory structure on target
- Remove if not needed

### 8.2 Model Weights
- **No model weights included** (good - they're large)
- Models downloaded via HuggingFace at runtime
- Requires HF_TOKEN for some models (check `.secrets/` if exists)

### 8.3 Hardware Assumptions
Target environment needs:
- CUDA 12.1 (for GPU) or MPS (for Mac) or CPU fallback
- 16GB+ RAM recommended
- 20GB+ disk for models + workspace

### 8.4 Secrets/Credentials
- Check `.secrets/` directory (4KB, likely small)
- May contain API keys (HuggingFace, etc.)
- Handle separately with secure transfer if needed

---

## 9. Summary & Recommendations

### Quick Transfer (Minimal Working System)
```
Chunks 1-3 only: ~15 MB, ~5 minutes
Includes: Core code, docs, viz
Excludes: Git history, archived results
Status: Ready to run experiments
```

### Full Transfer (Complete Archive)
```
All chunks: ~118 MB, ~20-30 minutes
Includes: Everything
Status: Complete historical record
```

### Recommended Approach
1. **Immediate:** Transfer Chunks 1-3 (15 MB) → Start working
2. **Background:** Transfer Chunk 6 results selectively
3. **Optional:** Transfer Chunk 5 git history if needed
4. **Skip:** Chunk 4 archive/ unless specifically needed

---

## Appendix A: File Type Summary

| Extension | Count | Purpose |
|-----------|-------|---------|
| .json | 1,161 | Results, configs, metadata |
| .md | 717 | Documentation |
| .py | 372 | Source code |
| .txt | 226 | Logs, outputs, notes |
| .pyc | 161 | Compiled Python (can exclude) |
| .csv | 115 | Experimental data |
| .jsonl | 99 | Streaming results |
| .sh | 28 | Shell scripts |
| .png | 23 | Figures, visualizations |
| .ipynb | 5 | Jupyter notebooks |

---

## Appendix B: Directory Tree (Key Paths)

```
mech-interp-latent-lab-phase1/
├── src/                          # Core library
│   ├── core/                     # Models, patching, hooks
│   ├── metrics/                  # R_V, behavior scoring
│   ├── pipelines/                # Experimental pipelines
│   ├── steering/                 # Activation patching
│   └── utils/                    # Helpers
├── rv_toolkit/                   # Reusable toolkit
│   ├── rv_toolkit/               # Main package
│   ├── experiments/              # Example experiments
│   └── tests/                    # Test suite
├── prompts/                      # Prompt management
│   ├── loader.py                 # Universal loader
│   └── bank.json                 # Prompt database
├── scripts/                      # Utility scripts
├── CANONICAL_CODE/               # Validated experiments
├── RECOVERED_GOLD/               # Breakthrough findings
├── R_V_PAPER/                    # Publication materials
├── docs/                         # Documentation
├── results/                      # Experimental outputs
└── archive/                      # Historical scripts
```

---

*Plan generated by subagent PULSE-004-RV-Plan*  
*For questions, see ARCHITECTURE.md or README.md in source directory*
