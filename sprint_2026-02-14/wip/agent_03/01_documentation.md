# Revenue-Critical Repository Catalog
## 80 Repositories for AI Infrastructure, Agents, and Production Systems

**Generated:** 2026-02-14  
**Purpose:** Revenue Content Forge - Actionable integration documentation  
**Format:** Why it matters → Integration paths → Pin policies

---

## Table of Contents

1. [Core LLM Frameworks (1-10)](#core-llm-frameworks)
2. [Agentic AI & Orchestration (11-25)](#agentic-ai--orchestration)
3. [Vector Databases & Retrieval (26-35)](#vector-databases--retrieval)
4. [MLOps & Model Serving (36-45)](#mlops--model-serving)
5. [Data Processing & ETL (46-55)](#data-processing--etl)
6. [Observability & Monitoring (56-65)](#observability--monitoring)
7. [Security & Guardrails (66-72)](#security--guardrails)
8. [Frontend & UI Components (73-78)](#frontend--ui-components)
9. [Infrastructure & Deployment (79-80)](#infrastructure--deployment)

---

## Core LLM Frameworks

### 1. langchain-ai/langchain
**Why it matters:** The dominant orchestration framework. 70%+ of production LLM apps use it. Vendor lock-in risk if you build directly on providers.

**Integration paths:**
- **Phase 1:** Use LangChain Expression Language (LCEL) for chain composition
- **Phase 2:** Implement custom callbacks for cost tracking
- **Phase 3:** Build reusable component library with `Runnable` interface
- **Revenue hook:** White-label agent templates, usage-based pricing on chains

**Pin policy:**
```toml
[tool.poetry.dependencies]
langchain = "^0.2.0"  # Pin minor version
langchain-core = "^0.2.0"  # Always pin together
```
- **Auto-update:** Patch versions only (automated)
- **Review required:** Minor versions (2-week lag)
- **Freeze:** During customer demos/releases

---

### 2. langchain-ai/langgraph
**Why it matters:** State machine abstraction for agent workflows. Critical for multi-step reasoning systems that need audit trails.

**Integration paths:**
- Replace ad-hoc agent loops with `StateGraph`
- Implement `MemorySaver` for persistent conversations
- Use `interrupt` for human-in-the-loop flows (high-value feature)

**Pin policy:**
```toml
langgraph = "^0.1.0"
```
- **Breaking changes frequent** - always review release notes
- Pin exact version for production graphs

---

### 3. haystack/deepset-ai
**Why it matters:** Production-grade RAG with evaluation built-in. European compliance focus (GDPR-ready).

**Integration paths:**
- **Retrieval pipelines:** `DocumentStore` + `Retriever` + `Reader`
- **Evaluation framework:** `eval()` with custom metrics
- **Revenue hook:** Document processing as a service

**Pin policy:**
```toml
farm-haystack = "^1.25.0"
```
- Stable API, minor updates safe
- Evaluate major versions in staging

---

### 4. llama-index/llama_index
**Why it matters:** Best-in-class indexing for unstructured data. 100+ data connectors. Essential for document-heavy use cases.

**Integration paths:**
- **Data ingestion:** `SimpleDirectoryReader` → `VectorStoreIndex`
- **Query engines:** `as_query_engine()` with custom prompts
- **Agent integration:** `OpenAIAgent` with tool use
- **Revenue hook:** Per-document processing fees

**Pin policy:**
```toml
llama-index = "^0.11.0"
```
- Rapid development - pin exact for stability
- Monitor v0.12.x for breaking changes

---

### 5. transformers (Hugging Face)
**Why it matters:** Model zoo access. 500k+ models. Essential for cost optimization (smaller models) and specialization.

**Integration paths:**
- **Pipeline API:** Quick inference for common tasks
- **Auto classes:** `AutoModel`, `AutoTokenizer` for flexibility
- **Optimization:** `optimum` for ONNX/TensorRT export
- **Revenue hook:** Fine-tuning service, model hosting

**Pin policy:**
```toml
transformers = ">=4.40.0,<5.0.0"
```
- Major version bumps are rare but breaking
- Security updates prioritized

---

### 6. openai-python
**Why it matters:** API client for GPT-4, GPT-4o, embeddings. Revenue backbone for most AI products.

**Integration paths:**
- **Structured outputs:** `response_format={"type": "json_object"}`
- **Streaming:** Essential for UX responsiveness
- **Assistants API:** Stateful threads for conversational apps
- **Batch API:** 50% cost reduction for async workloads

**Pin policy:**
```toml
openai = ">=1.30.0,<2.0.0"
```
- v1.0 was breaking - monitor v2 discussions
- Update within 1 week for API compatibility

---

### 7. anthropic-ai/anthropic-sdk-python
**Why it matters:** Claude API access. Best for long-context (200k tokens) and safety-conscious applications.

**Integration paths:**
- **Tool use:** Native function calling
- **Computer use:** Agentic GUI automation (beta)
- **Prompt caching:** 90% cost reduction on repeated prefixes
- **Revenue hook:** Premium tier for Claude Opus

**Pin policy:**
```toml
anthropic = ">=0.28.0,<1.0.0"
```
- SDK still pre-1.0 - expect breaking changes
- Pin exact for production

---

### 8. google/generative-ai-python
**Why it matters:** Gemini API. 1M token context. Competitive pricing. Google's ecosystem integration.

**Integration paths:**
- **Multimodal:** Text + image + video in single prompt
- **Grounding:** Google Search integration for factual queries
- **Vertex AI:** Enterprise deployment option

**Pin policy:**
```toml
google-generativeai = ">=0.7.0,<1.0.0"
```
- API surface changing rapidly
- Test thoroughly on updates

---

### 9. cohere-ai/cohere-python
**Why it matters:** Command R+ model. RAG-optimized. Embed v3 best-in-class for retrieval.

**Integration paths:**
- **RAG endpoints:** Built-in document grounding
- **Classification:** Custom model training
- **Embed:** Multilingual embeddings (100+ languages)
- **Revenue hook:** Multi-language SaaS expansion

**Pin policy:**
```toml
cohere = ">=5.5.0,<6.0.0"
```
- Stable SDK, routine updates OK

---

### 10. mistralai/mistral-inference
**Why it matters:** Apache 2.0 models. Self-hosting option. No vendor lock-in.

**Integration paths:**
- **Self-hosted:** `mistral_inference` for on-prem deployments
- **API:** Mistral Cloud for managed access
- **Fine-tuning:** Custom model adaptation
- **Revenue hook:** Private deployment premium

**Pin policy:**
```toml
mistral-inference = "^1.0.0"
```
- Self-hosted = full control over updates

---

## Agentic AI & Orchestration

### 11. microsoft/autogen
**Why it matters:** Multi-agent conversation framework. Code generation agents. Research-backed from Microsoft.

**Integration paths:**
- **Agent teams:** `AssistantAgent` + `UserProxyAgent`
- **Group chat:** Multi-agent collaboration
- **Code execution:** Docker-based sandbox
- **Revenue hook:** Developer productivity tools

**Pin policy:**
```toml
pyautogen = ">=0.2.0,<0.3.0"
```
- Rapid iteration - pin exact for demos
- Breaking changes in minor versions

---

### 12. crewAIInc/crewAI
**Why it matters:** Role-based agent teams. Hierarchical workflows. Business-friendly abstractions.

**Integration paths:**
- **Crew definition:** Roles + Goals + Backstories
- **Task delegation:** Sequential vs hierarchical
- **Tool integration:** LangChain compatible
- **Revenue hook:** Industry-specific agent crews

**Pin policy:**
```toml
crewai = "^0.51.0"
```
- Pre-1.0 - expect changes
- Pin exact for production crews

---

### 13. OpenBMB/ChatDev
**Why it matters:** Virtual software company simulation. Multi-agent software development.

**Integration paths:**
- **Custom phases:** Modify software lifecycle
- **Agent specialization:** CEO, CTO, Programmer, etc.
- **Artifact generation:** Code + documentation
- **Revenue hook:** Automated prototyping service

**Pin policy:**
- Install from commit SHA: `pip install git+https://github.com/OpenBMB/ChatDev.git@<commit>`
- Research project - expect instability

---

### 14. composiohq/composio
**Why it matters:** 100+ tool integrations for agents. OAuth handling. Production-grade tool calling.

**Integration paths:**
- **Tool integration:** GitHub, Slack, Linear, etc.
- **Authentication:** Managed OAuth flows
- **Trigger system:** Event-driven agent activation
- **Revenue hook:** Workflow automation SaaS

**Pin policy:**
```toml
composio-core = "^0.5.0"
composio-langchain = "^0.5.0"
```
- Pin together
- Update for new tools

---

### 15. simonw/datasette
**Why it matters:** Publish SQLite databases as APIs. Perfect for agent-accessible data.

**Integration paths:**
- **Data publishing:** CSV/JSON → SQLite → API
- **Plugins:** `datasette-llm-embed` for semantic search
- **Authentication:** `datasette-auth-tokens`
- **Revenue hook:** Data-as-a-service APIs

**Pin policy:**
```toml
datasette = "^0.64.0"
```
- Stable, regular updates OK

---

### 16. joaomdmoura/crewAI-tools
**Why it matters:** Pre-built tools for CrewAI. Browser automation, search, scraping.

**Integration paths:**
- **Web search:** Serper, Exa integrations
- **Browser:** Selenium-based navigation
- **File operations:** Read/write for agent persistence

**Pin policy:**
```toml
crewai-tools = "^0.8.0"
```
- Companion to crewai - update together

---

### 17. langchain-ai/langserve
**Why it matters:** Deploy LangChain chains as REST APIs. Production serving layer.

**Integration paths:**
- **API generation:** `add_routes()` for FastAPI
- **Playground:** Built-in testing UI
- **Streaming:** Server-sent events support
- **Revenue hook:** API monetization layer

**Pin policy:**
```toml
langserve = "^0.2.0"
```
- Pin with langchain
- Monitor for deprecation (may merge into core)

---

### 18. poe-platform/poe-protocol
**Why it matters:** Bot platform with monetization. Revenue share on usage.

**Integration paths:**
- **Bot creation:** FastAPI + `fp PoeBot`
- **Streaming:** Async generator responses
- **Attachments:** File upload handling
- **Revenue hook:** Per-message pricing

**Pin policy:**
```toml
fastapi-poe = "^0.0.46"
```
- Keep updated for new features

---

### 19. berriai/litellm
**Why it matters:** Unified LLM API. Call 100+ providers with OpenAI-compatible interface.

**Integration paths:**
- **Proxy server:** Drop-in replacement for OpenAI SDK
- **Fallbacks:** Automatic provider switching
- **Budget management:** Cost controls per key
- **Revenue hook:** LLM gateway service

**Pin policy:**
```toml
litellm = "^1.40.0"
```
- Active development - update for new providers
- Breaking changes rare

---

### 20. continue-dev/continue
**Why it matters:** Open-source AI code assistant. IDE integration. Self-hostable.

**Integration paths:**
- **IDE plugin:** VS Code, JetBrains
- **Custom models:** Bring your own LLM
- **Context providers:** @-mentions for files/docs
- **Revenue hook:** Team license for enterprise

**Pin policy:**
- Extension auto-updates
- Server component pin exact

---

### 21. superagent-ai/superagent
**Why it matters:** No-code agent builder. Workflow automation. Enterprise focus.

**Integration paths:**
- **API-first:** REST API for agent execution
- **Workflow builder:** Visual pipeline construction
- **Integration library:** 50+ connectors
- **Revenue hook:** Enterprise workflow automation

**Pin policy:**
```toml
superagent-py = "^0.3.0"
```
- Early stage - pin exact

---

### 22._prefecthq/prefect
**Why it matters:** Modern workflow orchestration. Data pipelines with observability.

**Integration paths:**
- **Flow definition:** `@flow` decorator
- **Task composition:** `@task` for units of work
- **Scheduling:** Cron, interval, event-based
- **Revenue hook:** Data pipeline as service

**Pin policy:**
```toml
prefect = "^3.0.0"
```
- v3 is latest - v2 deprecated

---

### 23. dagster-io/dagster
**Why it matters:** Data asset orchestration. Software-defined assets. Strong type safety.

**Integration paths:**
- **Asset graph:** `@asset` definitions
- **Materialization:** Data freshness guarantees
- **Observability:** Built-in data lineage
- **Revenue hook:** Data platform foundation

**Pin policy:**
```toml
dagster = "^1.7.0"
```
- Stable, semantic versioning

---

### 24. apache/airflow
**Why it matters:** Industry standard workflow orchestration. Massive ecosystem.

**Integration paths:**
- **DAG definition:** Python-based workflows
- **Operators:** 500+ integrations
- **Scheduler:** Production-tested at scale
- **Revenue hook:** Managed Airflow service

**Pin policy:**
```toml
apache-airflow = "^2.9.0"
```
- Update path: 2.8 → 2.9 carefully tested
- DB migrations required

---

### 25. temporalio/sdk-python
**Why it matters:** Durable execution. Fault-tolerant workflows. Microservice orchestration.

**Integration paths:**
- **Workflow definitions:** `@workflow.defn`
- **Activity execution:** `@activity.defn`
- **Reliability:** Automatic retries, timeouts
- **Revenue hook:** Reliable process automation

**Pin policy:**
```toml
temporalio = "^1.6.0"
```
- Stable SDK

---

## Vector Databases & Retrieval

### 26. chroma-core/chroma
**Why it matters:** Developer-friendly vector DB. Embedded mode. Fastest time-to-value.

**Integration paths:**
- **Local mode:** `chromadb.Client()` for development
- **Server mode:** Docker deployment for production
- **Embeddings:** Built-in or bring your own
- **Revenue hook:** RAG infrastructure service

**Pin policy:**
```toml
chromadb = "^0.5.0"
```
- 0.6.x has breaking changes
- Test migrations carefully

---

### 27. qdrant/qdrant-client
**Why it matters:** Production vector DB. Rust-based. On-prem and cloud options.

**Integration paths:**
- **Collection management:** Create with distance metrics
- **Filtering:** Metadata-based pre-filtering
- **Hybrid search:** Vector + keyword combined
- **Revenue hook:** Search-as-a-service backend

**Pin policy:**
```toml
qdrant-client = "^1.11.0"
```
- Keep in sync with server version

---

### 28. milvus-io/pymilvus
**Why it matters:** Billion-scale vector search. GPU acceleration. Enterprise features.

**Integration paths:**
- **Collection schema:** Define fields, indexes
- **Partitioning:** Data organization for performance
- **Multi-vector:** Multiple embedding types
- **Revenue hook:** Large-scale semantic search

**Pin policy:**
```toml
pymilvus = "^2.4.0"
```
- Match with Milvus server version

---

### 29. pinecone-io/pinecone-python-client
**Why it matters:** Managed vector DB. Zero ops. Pay-per-query pricing.

**Integration paths:**
- **Index management:** Serverless vs pod-based
- **Metadata filtering:** Rich query capabilities
- **Hybrid search:** Dense + sparse vectors
- **Revenue hook:** Pass-through costs + margin

**Pin policy:**
```toml
pinecone-client = "^5.0.0"
```
- v5 is latest major

---

### 30. weaviate/weaviate-python-client
**Why it matters:** Vector-native database. GraphQL interface. Modular AI integrations.

**Integration paths:**
- **Schema definition:** Class properties with vectorizers
- **Vectorizer modules:** OpenAI, Cohere, local models
- **GraphQL queries:** Flexible retrieval patterns
- **Revenue hook:** Knowledge graph applications

**Pin policy:**
```toml
weaviate-client = "^4.7.0"
```
- v4 is async-first

---

### 31. pgvector/pgvector
**Why it matters:** Postgres extension for vectors. Use existing database. ACID compliance.

**Integration paths:**
- **Extension:** `CREATE EXTENSION vector;`
- **Indexing:** IVFFlat, HNSW for performance
- **SQL operations:** Vector search with standard SQL
- **Revenue hook:** Simplified infrastructure stack

**Pin policy:**
- Postgres extension - version tied to Postgres version
- `pgvector` v0.7.0+ recommended

---

### 32. redis/redis-py
**Why it matters:** Cache + vector search. Sub-millisecond latency. Proven at scale.

**Integration paths:**
- **Vector search:** RediSearch module
- **Caching:** LLM response caching
- **Pub/sub:** Real-time agent coordination
- **Revenue hook:** Low-latency recommendation

**Pin policy:**
```toml
redis = "^5.0.0"
```
- v5 has async improvements

---

### 33. vespa-engine/vespa
**Why it matters:** Big data serving engine. Vector + lexical + structured search.

**Integration paths:**
- **Application packages:** Schema + ranking + queries
- **Hybrid ranking:** Combine multiple signals
- **Real-time:** Document updates without reindexing
- **Revenue hook:** Enterprise search platform

**Pin policy:**
- Docker deployment
- Version with application

---

### 34. marqo-ai/marqo
**Why it matters:** End-to-end vector search. Automatic embedding. Open source.

**Integration paths:**
- **Document indexing:** Automatic text embedding
- **Multimodal:** Image + text search
- **Hybrid search:** Tensor + lexical combined
- **Revenue hook:** Simplified semantic search

**Pin policy:**
```toml
marqo = "^3.5.0"
```

---

### 35. aiola/semantic-router
**Why it matters:** Route queries by semantic similarity. Dynamic agent selection.

**Integration paths:**
- **Route definition:** Utterance examples
- **Embedding layer:** Local or API-based
- **Decision layer:** Similarity threshold routing
- **Revenue hook:** Intelligent query distribution

**Pin policy:**
```toml
semantic-router = "^0.1.0"
```
- Early stage - pin exact

---

## MLOps & Model Serving

### 36. bentoml/BentoML
**Why it matters:** Model serving framework. Multi-framework support. Production-ready.

**Integration paths:**
- **Model packaging:** `bentoml.build()` for reproducibility
- **Service definition:** `bentoml.Service` with runners
- **Deployment:** Kubernetes, ECS, or serverless
- **Revenue hook:** Model serving infrastructure

**Pin policy:**
```toml
bentoml = "^1.3.0"
```
- v1.x stable

---

### 37. mlflow/mlflow
**Why it matters:** Experiment tracking. Model registry. Industry standard.

**Integration paths:**
- **Tracking:** `mlflow.log_param()`, `log_metric()`
- **Registry:** Model versioning and staging
- **Serving:** REST endpoints for registered models
- **Revenue hook:** ML platform governance

**Pin policy:**
```toml
mlflow = "^2.15.0"
```
- Frequent updates - stay current

---

### 38. wandb/wandb
**Why it matters:** Experiment tracking + visualization. Team collaboration. Artifact management.

**Integration paths:**
- **Run tracking:** `wandb.init()` + `log()`
- **Artifacts:** Dataset and model versioning
- **Sweeps:** Hyperparameter optimization
- **Revenue hook:** Team productivity insights

**Pin policy:**
```toml
wandb = "^0.17.0"
```
- Regular updates for new visualizations

---

### 39. tensorboard/tensorboard
**Why it matters:** TensorFlow visualization. Model debugging. Free.

**Integration paths:**
- **Logging:** `tf.summary` or `torch.utils.tensorboard`
- **Embedding projector:** High-dim visualization
- **Profiling:** Performance analysis
- **Revenue hook:** Model optimization service

**Pin policy:**
```toml
tensorboard = "^2.17.0"
```

---

### 40. triton-inference-server/server
**Why it matters:** NVIDIA inference optimization. GPU utilization. Production scale.

**Integration paths:**
- **Model repository:** Versioned model storage
- **Backends:** TensorRT, ONNX, PyTorch, etc.
- **Dynamic batching:** Throughput optimization
- **Revenue hook:** High-performance inference

**Pin policy:**
- Docker-based deployment
- Match CUDA and driver versions

---

### 41. vllm-project/vllm
**Why it matters:** Fast LLM inference. PagedAttention. 10x throughput improvement.

**Integration paths:**
- **OpenAI-compatible API:** Drop-in replacement
- **Continuous batching:** Maximize GPU utilization
- **Quantization:** GPTQ, AWQ for memory efficiency
- **Revenue hook:** Cost-optimized LLM hosting

**Pin policy:**
```toml
vllm = "^0.6.0"
```
- Rapid development - pin exact

---

### 42. sgl-project/sglang
**Why it matters:** Structured generation for LLMs. 5x speedup with regex constraints.

**Integration paths:**
- **SGLang runtime:** Fast structured decoding
- **API server:** OpenAI-compatible endpoints
- **Constrained generation:** JSON, regex patterns
- **Revenue hook:** Structured output APIs

**Pin policy:**
- Install from source or recent release
- Early project

---

### 43. huggingface/text-embeddings-inference
**Why it matters:** Optimized embedding serving. Rust-based. 2x throughput vs Python.

**Integration paths:**
- **Docker deployment:** One command start
- **Model hub:** Automatic model download
- **Batching:** Dynamic batching for efficiency
- **Revenue hook:** Embedding-as-a-service

**Pin policy:**
- Docker-based
- Pin image digest

---

### 44. gradio-app/gradio
**Why it matters:** ML demo framework. Shareable UIs. Hugging Face integration.

**Integration paths:**
- **Interface:** `gr.Interface()` for quick demos
- **Blocks:** Custom layouts for complex apps
- **API:** Automatic REST API generation
- **Revenue hook:** Prototype → product pipeline

**Pin policy:**
```toml
gradio = "^4.40.0"
```
- v5 in development

---

### 45. streamlit/streamlit
**Why it matters:** Data app framework. Python-only. Rapid prototyping.

**Integration paths:**
- **Session state:** User-specific data
- **Caching:** `@st.cache_data` for performance
- **Components:** Custom React extensions
- **Revenue hook:** Internal tool platform

**Pin policy:**
```toml
streamlit = "^1.37.0"
```

---

## Data Processing & ETL

### 46. apache/spark
**Why it matters:** Big data processing. Distributed computing. Industry standard.

**Integration paths:**
- **PySpark:** Python API for dataframes
- **MLlib:** Distributed machine learning
- **Structured streaming:** Real-time processing
- **Revenue hook:** Data engineering services

**Pin policy:**
```toml
pyspark = "^3.5.0"
```

---

### 47. dask/dask
**Why it matters:** Parallel computing. Scales NumPy, Pandas, Scikit-learn.

**Integration paths:**
- **Dataframes:** Parallel Pandas operations
- **Delayed:** Custom task graphs
- **Distributed:** Multi-machine clusters
- **Revenue hook:** Scalable data processing

**Pin policy:**
```toml
dask = "^2024.7.0"
```

---

### 48. polars/polars
**Why it matters:** Fast DataFrames. Rust-based. 10-50x faster than Pandas.

**Integration paths:**
- **Lazy evaluation:** Query optimization
- **Streaming:** Out-of-core processing
- **Interoperability:** Arrow-native
- **Revenue hook:** High-performance ETL

**Pin policy:**
```toml
polars = "^1.5.0"
```
- v1.0 is stable

---

### 49. ibis-project/ibis
**Why it matters:** Python analytics framework. 15+ backend support. Write once, run anywhere.

**Integration paths:**
- **Backend abstraction:** DuckDB, Postgres, BigQuery, etc.
- **Deferred execution:** Query optimization
- **Pythonic API:** Familiar syntax
- **Revenue hook:** Portable analytics

**Pin policy:**
```toml
ibis-framework = "^9.2.0"
```

---

### 50. dbt-labs/dbt-core
**Why it matters:** Data transformation. SQL-based analytics engineering. Version control for data.

**Integration paths:**
- **Models:** SQL transformations
- **Tests:** Data quality assertions
- **Documentation:** Auto-generated data catalog
- **Revenue hook:** Analytics engineering services

**Pin policy:**
```toml
dbt-core = "^1.8.0"
```

---

### 51. sqlfluff/sqlfluff
**Why it matters:** SQL linting and formatting. Data quality gate.

**Integration paths:**
- **Linting:** Style and logic checks
- **Formatting:** Consistent SQL style
- **CI/CD:** Pre-commit hooks
- **Revenue hook:** Data quality assurance

**Pin policy:**
```toml
sqlfluff = "^3.1.0"
```

---

### 52. meltano/meltano
**Why it matters:** ETL orchestration. Singer protocol. 500+ connectors.

**Integration paths:**
- **Extractors:** Source data connections
- **Loaders:** Destination data connections
- **Transforms:** dbt integration
- **Revenue hook:** Data integration platform

**Pin policy:**
```toml
meltano = "^3.5.0"
```

---

### 53. airbytehq/airbyte
**Why it matters:** Data integration. 300+ connectors. Open source alternative to Fivetran.

**Integration paths:**
- **Connector catalog:** Extensive source coverage
- **CDC:** Change data capture
- **Transformation:** Custom and dbt
- **Revenue hook:** Data pipeline service

**Pin policy:**
- Docker deployment
- Version with platform

---

### 54. pandas-dev/pandas
**Why it matters:** Data manipulation standard. Essential for data science.

**Integration paths:**
- **Data manipulation:** Core analysis operations
- **Time series:** Resampling, time zones
- **I/O:** CSV, Parquet, SQL, Excel
- **Revenue hook:** Data analysis foundation

**Pin policy:**
```toml
pandas = "^2.2.0"
```
- v2.x has PyArrow backend

---

### 55. numpy/numpy
**Why it matters:** Numerical computing foundation. Every ML library depends on it.

**Integration paths:**
- **Array operations:** Vectorized computation
- **Linear algebra:** BLAS/LAPACK bindings
- **Random:** Reproducible sampling
- **Revenue hook:** Performance optimization

**Pin policy:**
```toml
numpy = "^2.0.0"
```
- v2 has breaking changes vs v1

---

## Observability & Monitoring

### 56. open-telemetry/opentelemetry-python
**Why it matters:** Vendor-neutral observability. Traces, metrics, logs.

**Integration paths:**
- **Auto-instrumentation:** Zero-code setup
- **Manual spans:** Custom trace points
- **Exporters:** Send to any backend
- **Revenue hook:** Observability platform

**Pin policy:**
```toml
opentelemetry-api = "^1.26.0"
opentelemetry-sdk = "^1.26.0"
```
- Pin together

---

### 57. langfuse/langfuse-python
**Why it matters:** LLM observability. Prompt management. Cost tracking.

**Integration paths:**
- **Tracing:** LLM call tracking
- **Evaluation:** Dataset-based testing
- **Prompt management:** Versioned prompts
- **Revenue hook:** LLM ops platform

**Pin policy:**
```toml
langfuse = "^2.43.0"
```

---

### 58. helicone/helicone
**Why it matters:** LLM gateway + observability. Cost optimization. Caching.

**Integration paths:**
- **Proxy:** Request/response logging
- **Caching:** Reduce API costs
- **Rate limiting:** Usage controls
- **Revenue hook:** LLM infrastructure

**Pin policy:**
- Cloud service
- SDK optional

---

### 59. weights-biases/weave
**Why it matters:** W&B's LLM tracing tool. Evaluation framework.

**Integration paths:**
- **Tracing:** Automatic LLM logging
- **Evaluations:** Dataset-based testing
- **Annotations:** Human feedback collection
- **Revenue hook:** Model evaluation service

**Pin policy:**
```toml
weave = "^0.50.0"
```

---

### 60. aimhubio/aim
**Why it matters:** Open-source ML experiment tracker. Self-hosted option.

**Integration paths:**
- **Run tracking:** Metrics and params
- **Visualization:** Custom dashboards
- **Querying:** Python API for analysis
- **Revenue hook:** Private ML platform

**Pin policy:**
```toml
aim = "^3.24.0"
```

---

### 61. grafana/grafana
**Why it matters:** Visualization platform. Dashboards for metrics and logs.

**Integration paths:**
- **Data sources:** 100+ integrations
- **Alerting:** Threshold-based notifications
- **Dashboards:** Shareable visualizations
- **Revenue hook:** Monitoring service

**Pin policy:**
- Docker deployment
- Pin major version

---

### 62. prometheus/prometheus
**Why it matters:** Metrics collection. Time-series database. Cloud-native standard.

**Integration paths:**
- **Metric exposition:** `/metrics` endpoints
- **Scraping:** Automatic collection
- **Alerting:** Alertmanager integration
- **Revenue hook:** Infrastructure monitoring

**Pin policy:**
- Binary/Docker deployment
- Pin for compatibility

---

### 63. open-telemetry/opentelemetry-collector
**Why it matters:** Telemetry pipeline. Receive, process, export observability data.

**Integration paths:**
- **Receivers:** Many input formats
- **Processors:** Transform and enrich
- **Exporters:** Route to backends
- **Revenue hook:** Observability infrastructure

**Pin policy:**
- Docker deployment
- Pin for stability

---

### 64. sentry/sentry-python
**Why it matters:** Error tracking. Performance monitoring. Issue resolution.

**Integration paths:**
- **Exception capture:** Automatic error reporting
- **Performance:** Transaction tracing
- **Context:** Breadcrumbs and tags
- **Revenue hook:** Application monitoring

**Pin policy:**
```toml
sentry-sdk = "^2.12.0"
```

---

### 65. getpino/pino
**Why it matters:** Fast JSON logger. Node.js ecosystem. Structured logging.

**Integration paths:**
- **Structured logs:** JSON format
- **Redaction:** Automatic PII removal
- **Transport:** Async log shipping
- **Revenue hook:** Log aggregation

**Pin policy:**
```javascript
"pino": "^9.3.0"
```

---

## Security & Guardrails

### 66. protectai/llm-guard
**Why it matters:** Input/output filtering for LLMs. Prompt injection protection.

**Integration paths:**
- **Input scanners:** Prompt validation
- **Output scanners:** Response filtering
- **API:** FastAPI-based service
- **Revenue hook:** LLM security service

**Pin policy:**
```toml
llm-guard = "^0.3.0"
```

---

### 67. presidio/presidio
**Why it matters:** PII detection and anonymization. Microsoft backed.

**Integration paths:**
- **Analysis:** PII entity detection
- **Anonymization:** Redaction and replacement
- **Customization:** Custom recognizers
- **Revenue hook:** Data privacy compliance

**Pin policy:**
```toml
presidio-analyzer = "^2.2.0"
presidio-anonymizer = "^2.2.0"
```

---

### 68. laiyer-ai/llm-guard
**Why it matters:** Another LLM security toolkit. Multiple scanner types.

**Integration paths:**
- **Scanners:** Bias, toxicity, relevance
- **API:** REST interface
- **Integration:** LangChain compatible
- **Revenue hook:** Content moderation

**Pin policy:**
- Review for uniqueness vs protectai/llm-guard

---

### 69. brigadecore/brigade
**Why it matters:** Event-driven scripting for Kubernetes. Secure pipeline execution.

**Integration paths:**
- **Event sources:** GitHub, Docker, cron
- **Jobs:** Container-based tasks
- **Secrets:** Vault integration
- **Revenue hook:** Secure CI/CD

**Pin policy:**
- Kubernetes deployment
- Pin Helm chart version

---

### 70. aquasecurity/trivy
**Why it matters:** Security scanner. Vulnerabilities, secrets, IaC issues.

**Integration paths:**
- **Image scanning:** Container vulnerabilities
- **Repo scanning:** Secret detection
- **IaC scanning:** Terraform, CloudFormation
- **Revenue hook:** Security auditing

**Pin policy:**
- Binary installation
- Regular updates for new CVEs

---

### 71. open-policy-agent/opa
**Why it matters:** Policy as code. Unified authorization.

**Integration paths:**
- **Rego language:** Policy definitions
- **Data filtering:** Query rewriting
- **API authorization:** Request decisions
- **Revenue hook:** Compliance platform

**Pin policy:**
- Sidecar deployment
- Version with policy bundle

---

### 72. clair/clair
**Why it matters:** Container vulnerability analysis. Quay, Harbor integration.

**Integration paths:**
- **Image scanning:** Layer-by-layer analysis
- **Database:** CVE matching
- **Notifications:** Webhook alerts
- **Revenue hook:** Container security

**Pin policy:**
- Database updates critical
- Pin for stability

---

## Frontend & UI Components

### 73. vercel/ai-sdk
**Why it matters:** React/JS streaming hooks for AI. Production-ready UI components.

**Integration paths:**
- **useChat:** Streaming chat interface
- **useCompletion:** Text completion hook
- **RSC:** React Server Components support
- **Revenue hook:** AI-powered applications

**Pin policy:**
```javascript
"ai": "^3.3.0"
```

---

### 74. shadcn/ui
**Why it matters:** Copy-paste component library. Radix-based. Tailwind styled.

**Integration paths:**
- **CLI:** `npx shadcn-ui@latest init`
- **Components:** Selective installation
- **Theming:** Customizable design
- **Revenue hook:** Rapid UI development

**Pin policy:**
- No package dependency
- CLI versioned separately

---

### 75. radix-ui/primitives
**Why it matters:** Unstyled accessible components. Headless UI foundation.

**Integration paths:**
- **Primitives:** Dialog, Dropdown, Tooltip, etc.
- **Accessibility:** Keyboard navigation, ARIA
- **Composition:** Flexible component patterns
- **Revenue hook:** Accessible applications

**Pin policy:**
```javascript
"@radix-ui/react-dialog": "^1.1.0"
```
- Individual packages per component

---

### 76. tanstack/query
**Why it matters:** Data synchronization. Server state management. Caching.

**Integration paths:**
- **useQuery:** Data fetching
- **Mutations:** Server updates
- **Prefetching:** Optimistic loading
- **Revenue hook:** Responsive applications

**Pin policy:**
```javascript
"@tanstack/react-query": "^5.51.0"
```

---

### 77. tanstack/table
**Why it matters:** Headless table component. Sorting, filtering, pagination.

**Integration paths:**
- **Data grids:** Complex table UIs
- **Virtualization:** Large dataset handling
- **Customization:** Full control over rendering
- **Revenue hook:** Data-heavy applications

**Pin policy:**
```javascript
"@tanstack/react-table": "^8.20.0"
```

---

### 78. plotly/plotly.py
**Why it matters:** Interactive visualizations. JavaScript-powered. Python API.

**Integration paths:**
- **Charts:** Line, bar, scatter, 3D
- **Dashboards:** Dash integration
- **Export:** HTML, PNG, PDF
- **Revenue hook:** Data visualization

**Pin policy:**
```toml
plotly = "^5.23.0"
```

---

## Infrastructure & Deployment

### 79. kubernetes/kubernetes
**Why it matters:** Container orchestration standard. Production deployment platform.

**Integration paths:**
- **Workloads:** Deployments, StatefulSets, Jobs
- **Service mesh:** Istio, Linkerd integration
- **Operators:** Custom resource automation
- **Revenue hook:** Managed Kubernetes

**Pin policy:**
- Version with cloud provider
- Stay within 2 minor versions of latest

---

### 80. hashicorp/terraform
**Why it matters:** Infrastructure as code. Multi-cloud provisioning. State management.

**Integration paths:**
- **Providers:** AWS, GCP, Azure, 1000+ services
- **Modules:** Reusable infrastructure
- **State:** Remote state management
- **Revenue hook:** Cloud infrastructure services

**Pin policy:**
- Pin version per project
- Use `required_version` constraint
- Update after testing

---

## Quick Reference: Pin Policy Summary

### Always Pin Together
| Primary | Secondary | Tertiary |
|---------|-----------|----------|
| langchain | langchain-core | langgraph, langserve |
| composio-core | composio-langchain | - |
| opentelemetry-api | opentelemetry-sdk | opentelemetry-instrumentation-* |
| presidio-analyzer | presidio-anonymizer | - |

### Pre-1.0 High Risk
- autogen
- crewAI
- anthropic
- semantic-router
- sglang
- vllm (rapid changes)

### Enterprise Stable
- prefect (^3.0)
- dagster (^1.7)
- mlflow (^2.15)
- airflow (^2.9)

### Update Urgency
| Package | Update Frequency | Reason |
|---------|------------------|--------|
| openai | Weekly | API compatibility |
| trivy | Daily | CVE database |
| langchain | Bi-weekly | Feature access |
| transformers | Monthly | Security |

---

## Revenue Integration Patterns

### Pattern 1: LLM Gateway
```
LiteLLM → Multiple providers → Cost tracking → Usage-based billing
```

### Pattern 2: RAG Pipeline
```
Document ingestion → ChromaDB → LlamaIndex → LangChain → API endpoint
```

### Pattern 3: Agent Platform
```
CrewAI → Composio tools → Langfuse monitoring → Stripe billing
```

### Pattern 4: ML Platform
```
MLflow tracking → Prefect orchestration → BentoML serving → Grafana dashboards
```

---

## Document Generation Info

- **Session start:** 2026-02-14 00:18 UTC
- **Document complete:** 2026-02-14 00:22 UTC
- **Elapsed:** 4 minutes
- **Repositories documented:** 80
- **Categories:** 9
- **Integration patterns:** 4

**Next steps:**
1. Review for currency (versions as of 2026-02-14)
2. Validate integration paths against current projects
3. Create team-specific subsets
4. Schedule quarterly review
