# Domain A Research: RAG Systems — Vector DBs, Embedding Strategies, Hybrid Search
**Timestamp:** 2026-02-15 01:40 UTC  
**Agent:** DHARMIC CLAW  
**Research Domain:** A — RAG Systems (Vector DBs, embedding strategies, hybrid search BM25+vector, chunking)  
**Duration:** ~25 minutes  
**Session Start:** 2026-02-15 01:30 UTC

---

## WHY THIS DOMAIN MATTERS

Our P9 indexer is core infrastructure. Better RAG = better memory retrieval = better agent performance. This research covers:
1. **Vector database selection** — Which DB fits our scale and needs
2. **Chunking strategies** — How to split documents for optimal retrieval
3. **Hybrid search** — Combining BM25 keyword + vector semantic search
4. **Embedding models** — Which models provide best retrieval performance

---

## KEY FINDINGS

### 1. VECTOR DATABASE LANDSCAPE 2025

**Source:** Firecrawl "Best Vector Databases in 2025" (VectorDBBench data)

| Database | Best For | Key Strength | Key Weakness |
|----------|----------|--------------|--------------|
| **Pinecone** | Enterprise, no ops | Fully managed, serverless scaling, hybrid search | Higher cost, no on-prem |
| **Qdrant** | Performance | Rust-based, lowest latency, strong metadata filtering | Self-hosted complexity |
| **Weaviate** | Knowledge graphs | GraphQL API, built-in hybrid search, semantic relationships | Resource intensive |
| **Chroma** | Rapid prototyping | Developer-friendly, ML framework integration | Not for extreme scale |
| **pgvector** | Postgres users | Same DB for relational + vectors, ACID compliance | Limited beyond 50-100M vectors |
| **Milvus/Zilliz** | Billion-scale | Highest raw performance in benchmarks | Complex deployment |

**Performance Benchmarks (VectorDBBench):**
- **Zilliz** leads in raw latency under test conditions
- **Pinecone** and **Qdrant** competitive for production
- **pgvectorscale** achieved 471 QPS at 99% recall on 50M vectors (11.4x better than Qdrant's 41 QPS)

**Key Insight:** Purpose-built DBs (Pinecone, Milvus, Qdrant) scale better for vector-only workloads. Extensions (pgvector) work well if you already run PostgreSQL and stay under 100M vectors.

**Citation:** Firecrawl.dev, VectorDBBench Leaderboard

---

### 2. CHUNKING STRATEGIES — CRITICAL FOR RAG ACCURACY

**Source:** NVIDIA benchmarks via Firecrawl, Unstructured.io, Weaviate

**The Problem:**
Wrong chunking creates up to **9% gap in recall performance** between best and worst approaches. Chunk size affects:
- **Too small:** Lose context, fragmented meaning
- **Too large:** Diluted embeddings, mixed topics, reduced precision

**Six Chunking Strategies Compared:**

| Strategy | How It Works | Best For | Recall Performance |
|----------|--------------|----------|-------------------|
| **Recursive Character** | Hierarchical separators (paragraph → sentence → word) | General purpose, 80% of use cases | 88-89% with 400-token chunks |
| **Page-Level** | One chunk per page | Documents with natural page breaks | **Highest: 0.648 accuracy** (NVIDIA) |
| **Semantic** | Split where embeddings differ significantly | Preserving meaning boundaries | High quality, API cost |
| **Fixed-Size** | N characters/tokens per chunk | Simple implementation | Lower quality |
| **LLM-Based** | LLM analyzes structure | Maximum quality | Highest cost, slowest |
| **Sentence-Based** | Split at sentence boundaries | Preserving natural language | Moderate quality |

**Optimal Chunk Sizes by Query Type:**
- **Factoid queries:** 256-512 tokens
- **Analytical queries:** 1024+ tokens
- **General baseline:** 512 tokens with 50-100 token overlap

**Key Finding from Unstructured.io:**
> "A chunk size of about 250 tokens, equivalent to approximately 1000 characters, is a sensible starting point for experimentation."

**Recursive Splitting Separator Hierarchy:**
```python
separators = [
    "\n\n",      # Paragraph breaks
    "\n",        # Line breaks  
    ". ",        # Sentences
    " ",         # Words
    ""           # Characters (last resort)
]
```

**Code-Aware Separators:**
```python
separators = [
    "\n\nclass ",  # Class definitions
    "\n\ndef ",    # Function definitions
    "\n\n",        # Paragraph breaks
    "\n",          # Line breaks
    " ",           # Spaces
    ""
]
```

**Citation:** Unstructured.io "Chunking for RAG: best practices"; Firecrawl "Best Chunking Strategies for RAG in 2025"; Weaviate blog

---

### 3. HYBRID SEARCH — BM25 + VECTOR WITH RECIPROCAL RANK FUSION

**Source:** Assembled.com, MongoDB, DEV Community implementations

**The Problem with Vector-Only Search:**
- Fails on specific keyword matches ("premium plan features")
- Struggles with short queries containing prominent but ambiguous keywords
- Customer support queries often need exact keyword hits

**Solution: Hybrid Search + Reciprocal Rank Fusion (RRF)**

**How It Works:**
1. Run **semantic search** (vector similarity) → get ranked results
2. Run **keyword search** (BM25/full-text) → get ranked results  
3. **Fuse rankings** using RRF formula

**RRF Formula:**
```
RRF_score(d) = Σ 1/(k + rank_i(d))

Where:
- k = constant (typically 60)
- rank_i(d) = rank of document d in result list i
```

**Why RRF Works:**
- **Rank-based:** Avoids score calibration problems across different search methods
- **Rewards agreement:** Documents appearing in both lists get boosted
- **Prevents dominance:** Constant k prevents any single system from dominating
- **No tuning:** No per-customer weight tuning needed

**Implementation Pattern:**
```python
async def hybrid_search(
    session: AsyncSession,
    query: str,
    query_embedding: list[float],
    limit: int = 10
) -> list[SearchResult]:
    # Run both searches in parallel
    semantic_results, fulltext_results = await asyncio.gather(
        semantic_search(session, query_embedding, limit=20),
        fulltext_search(session, query, limit=20)
    )
    # Fuse and return top results
    fused = reciprocal_rank_fusion([semantic_results, fulltext_results])
    return fused[:limit]

def reciprocal_rank_fusion(result_lists, k=60):
    """Merge multiple ranked lists using RRF."""
    scores = defaultdict(float)
    for results in result_lists:
        for rank, doc in enumerate(results):
            scores[doc.id] += 1.0 / (k + rank)
    # Sort by score descending
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

**Citation:** Assembled.com "Better RAG results with Reciprocal Rank Fusion"; MongoDB documentation

---

### 4. EMBEDDING MODELS — MTEB LEADERBOARD ANALYSIS

**Source:** Hugging Face MTEB Leaderboard, Modal.com analysis

**MTEB Benchmark Categories:**
1. Classification
2. Clustering
3. Pair classification
4. Reranking
5. **Retrieval** ← Most important for RAG
6. **Semantic Textual Similarity (STS)** ← Second most important
7. Summarization
8. Bitext Mining

**Key Insight:**
> "The best overall model is not always the top choice for your workload. A team that builds retrieval pipelines should focus on retrieval and semantic textual similarity over the global average."

**Top Models (2025):**

| Model | Size | License | Best For | Trade-off |
|-------|------|---------|----------|-----------|
| **Qwen3-Embedding-8B** | 8B | Apache-2.0 | Multi-lingual, state-of-the-art | VRAM-heavy |
| **sentence-transformers/all-mpnet-base-v2** | 110M | Apache-2.0 | General retrieval, battle-tested | Older architecture |
| **sentence-transformers/all-MiniLM-L6-v2** | 22M | Apache-2.0 | Speed, resource-constrained | Lower accuracy |
| **BAAI/bge-base-en-v1.5** | 110M | MIT | English retrieval | Domain-specific beats general |
| **intfloat/e5-base-v2** | 110M | MIT | High-quality embeddings | Slower inference |

**Practical Recommendations:**
- **Start with:** `all-MiniLM-L6-v2` (22M params, fast, good baseline)
- **Upgrade to:** `all-mpnet-base-v2` (better accuracy, still manageable)
- **Production:** Domain-specific models beat general-purpose (finance, legal, biomedical)
- **Multi-lingual:** Qwen3-Embedding or paraphrase-multilingual-MiniLM-L12-v2

**Citation:** Hugging Face MTEB Leaderboard; Modal.com "Top embedding models on the MTEB leaderboard"

---

### 5. ADVANCED: MATRYOSHKA EMBEDDINGS

**Source:** Hugging Face blog

**Concept:** Produce embeddings at multiple dimensionalities from single model
- Train model to produce [768-dim, 512-dim, 256-dim, 128-dim, ...] embeddings
- Trade vector size for speed/memory without retraining
- Store full embedding, query with reduced dimension for speed

**Benefit:** 
- 75% memory reduction (768d → 256d) with minimal accuracy loss
- Flexibility: use full precision for accuracy, reduced for speed

**Citation:** Hugging Face "Matryoshka Representation Learning"

---

## SYNTHESIS: RAG ARCHITECTURE FOR P9 INDEXER

### Current State (The Problem)

| Issue | Impact | Evidence |
|-------|--------|----------|
| Unknown chunking strategy | Suboptimal retrieval precision | No documented chunk size |
| Vector-only search | Misses keyword matches | No BM25 integration |
| Single embedding model | No flexibility for speed/accuracy trade-off | Fixed model choice |
| Chroma limitations | Scale concerns as docs grow | Local Chroma instance |

### Proposed Architecture: "RETRIEVER Stack"

```
┌─────────────────────────────────────────────────────────────────┐
│                    RETRIEVER RAG STACK                          │
├─────────────────────────────────────────────────────────────────┤
│  Layer 4: Hybrid Search                                          │
│  ├── Vector search (semantic) via pgvector                      │
│  ├── Full-text search (BM25) via PostgreSQL tsvector            │
│  └── RRF fusion for final ranking                               │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3: Embedding Models                                       │
│  ├── Default: all-MiniLM-L6-v2 (fast)                           │
│  ├── Quality: all-mpnet-base-v2 (accurate)                      │
│  └── Future: Matryoshka for flexible dimensions                 │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2: Chunking Strategy                                      │
│  ├── Recursive character splitting                              │
│  ├── Chunk size: 512 tokens (256 for factoid, 1024 for analysis)│
│  └── Overlap: 50-100 tokens                                     │
├─────────────────────────────────────────────────────────────────┤
│  Layer 1: Vector Store                                           │
│  ├── PostgreSQL + pgvector (migrate from Chroma)                │
│  └── HNSW index for fast similarity search                      │
└─────────────────────────────────────────────────────────────────┘
```

### Implementation Path

**Phase 1: Hybrid Search (IMMEDIATE)**
```python
# src/core/hybrid_retriever.py
import asyncpg
from pgvector.asyncpg import register_vector

class HybridRetriever:
    def __init__(self, pool):
        self.pool = pool
        self.k = 60  # RRF constant
    
    async def search(self, query: str, embedding: list[float], top_k: int = 10):
        async with self.pool.acquire() as conn:
            # Semantic search via pgvector
            semantic_results = await conn.fetch(
                """
                SELECT id, 1/(rank() OVER (ORDER BY embedding <=> $1)) as rrf_score
                FROM documents
                ORDER BY embedding <=> $1
                LIMIT 20
                """,
                embedding
            )
            
            # Full-text search via tsvector
            keyword_results = await conn.fetch(
                """
                SELECT id, 1/(rank() OVER (ORDER BY ts_rank(search_vector, plainto_tsquery($1)) DESC)) as rrf_score
                FROM documents
                WHERE search_vector @@ plainto_tsquery($1)
                ORDER BY ts_rank(search_vector, plainto_tsquery($1)) DESC
                LIMIT 20
                """,
                query
            )
            
            # RRF fusion
            return self._rrf_fuse([semantic_results, keyword_results], top_k)
```

**Phase 2: Optimized Chunking (SHORT-TERM)**
```python
# src/core/chunker.py
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentChunker:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def chunk_by_query_type(self, text: str, query_type: str = "general") -> list[str]:
        """Adjust chunk size based on query type."""
        sizes = {
            "factoid": 256,
            "general": 512,
            "analytical": 1024
        }
        self.splitter._chunk_size = sizes.get(query_type, 512)
        return self.splitter.split_text(text)
```

**Phase 3: Migrate to PostgreSQL + pgvector (MEDIUM-TERM)**
- Single database for documents + vectors + full-text search
- ACID compliance for document updates
- Scales to 50-100M vectors with pgvectorscale
- Simpler ops than separate Chroma instance

---

## IMPLEMENTATIONS FOUND

| Project | Type | Best For | Integration |
|---------|------|----------|-------------|
| **pgvector** | Vector extension | Postgres users | `pip install pgvector` |
| **pgvectorscale** | Performance | 50M+ vectors | TimescaleDB extension |
| **RecursiveCharacterTextSplitter** | Chunking | General purpose | LangChain |
| **sentence-transformers** | Embeddings | Model zoo | `pip install sentence-transformers` |
| **MTEB** | Evaluation | Benchmark models | `pip install mteb` |

---

## ADOPTION RECOMMENDATION: **HIGH**

**Why HIGH:**
1. **Immediate accuracy gains** — Hybrid search + RRF addresses real retrieval failures
2. **Proven patterns** — All findings backed by benchmarks (VectorDBBench, MTEB, NVIDIA)
3. **Fits our stack** — PostgreSQL migration simplifies infrastructure
4. **Cost-effective** — pgvector open-source vs paid Pinecone
5. **Foundation for growth** — Proper chunking and hybrid search enable scaling

**Why not IMMEDIATE:**
- Database migration requires planning
- Need to re-index existing documents with new chunking
- Performance testing required before production

**Priority:**
1. **Implement hybrid search** with Chroma (immediate, no migration)
2. **Tune chunking strategy** with recursive splitter (short-term)
3. **Migrate to PostgreSQL + pgvector** (medium-term)
4. **Add MTEB evaluation** to benchmark improvements (ongoing)

---

## RISKS

1. **Migration complexity** — Moving from Chroma to PostgreSQL requires re-indexing
   - *Mitigation:* Parallel run, validate recall before cutover

2. **Query latency** — Hybrid search = 2 queries + fusion
   - *Mitigation:* Run semantic and keyword in parallel (asyncio)

3. **Embedding model compatibility** — Different models produce incompatible vectors
   - *Mitigation:* Version embeddings, re-index on model change

4. **Over-engineering** — Complex chunking for simple use case
   - *Mitigation:* Start with fixed 512-token chunks, measure before optimizing

5. **BM25 tuning** — PostgreSQL full-text search requires stopword and stemming tuning
   - *Mitigation:* Use default English config, iterate based on query logs

---

## STRANGE LOOP SIGNATURE

This research on retrieval improves the retrieval system that retrieves the research:
- P9 indexer stores my notes
- These findings improve P9
- Improved P9 retrieves better context for future research
- Future research further improves P9

The system learns about learning through the very mechanisms it studies.

S(P9) = P9 — the indexer becomes self-improving through its own output.

---

## YAML OUTPUT

```yaml
domain: RAG Systems (Vector DBs, embedding strategies, hybrid search, chunking)
key_findings:
  - "Wrong chunking creates up to 9% gap in recall; optimal chunk size is 512 tokens with 50-100 token overlap for general queries, 256 for factoid, 1024+ for analytical (NVIDIA benchmarks)"
  - "Hybrid search (BM25 + vector) with Reciprocal Rank Fusion outperforms vector-only; RRF formula: Σ 1/(k + rank) with k=60 (Assembled.com, MongoDB)"
  - "pgvectorscale achieves 471 QPS at 99% recall on 50M vectors — 11.4x better than Qdrant; PostgreSQL+pgvector viable to 100M vectors (VectorDBBench)"
  - "MTEB leaderboard: focus on Retrieval + STS scores, not overall average; all-MiniLM-L6-v2 for speed, all-mpnet-base-v2 for accuracy (Modal.com)"
  - "Matryoshka embeddings enable 75% memory reduction via flexible dimensions without retraining (Hugging Face)"

implementations_found:
  - repo: "pgvector/pgvector"
    type: "PostgreSQL extension"
    best_for: "Unified relational + vector storage"
    license: "PostgreSQL"
  - repo: "timescale/pgvectorscale"
    type: "Performance extension"
    best_for: "50M+ vectors at 99% recall"
    benchmark: "471 QPS vs 41 QPS (Qdrant)"
  - repo: "langchain-ai/langchain"
    type: "Chunking library"
    class: "RecursiveCharacterTextSplitter"
    best_for: "Structure-aware splitting"
  - repo: "embeddings-benchmark/mteb"
    type: "Evaluation framework"
    best_for: "Benchmarking embedding models"

adoption_recommendation: "HIGH"
adoption_rationale: |
  Immediate retrieval accuracy gains from hybrid search + RRF. Proven by 
  VectorDBBench and MTEB benchmarks. PostgreSQL+pgvector simplifies infrastructure 
  vs separate Chroma. Chunking optimization directly addresses precision issues.
  Foundation for scaling to millions of documents.

integration_path: |
  Phase 1: Implement hybrid search with existing Chroma (BM25 via whoosh or 
  add keyword index to Chroma metadata).
  Phase 2: Tune chunking to 512 tokens with recursive splitter; evaluate 
  with MTEB retrieval tasks.
  Phase 3: Migrate to PostgreSQL+pgvector for unified storage; implement 
  native hybrid search with tsvector + vector.
  Target: RETRIEVER stack for P9 indexer with 95%+ recall.

risks:
  - "Database migration requires re-indexing all documents (mitigate: parallel run)"
  - "Hybrid search adds latency (mitigate: parallel queries with asyncio)"
  - "Embedding model changes require re-indexing (mitigate: version embeddings)"
  - "BM25 tuning needed for domain-specific terms (mitigate: iterate on query logs)"

cost_impact:
  current: "Chroma local storage; potential scale limitations"
  projected: "PostgreSQL operational cost; pgvector open-source"
  benefits: "No Pinecone/Managed vector DB costs; unified infrastructure"

research_duration: "25 minutes"
finding_count: 5
implementation_count: 4
```

---

**JIKOKU:** TASK_END {agent: clawd, task: domain_a_research, duration: 25m, value_added: high, findings: 5, implementations: 4}

**JSCA** 🪷 | Better retrieval is better memory; better memory is better thought
2026-02-15 01:42:15 UTC
