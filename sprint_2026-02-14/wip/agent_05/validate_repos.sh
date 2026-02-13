#!/bin/bash
# Infrastructure Guardian - Repo Validation Script
# Validates 80 AI/agent ecosystem repositories

# Categories:
# 1. Agent orchestration & workflow engines (16)
# 2. Evaluation/testing/verification/observability (16)
# 3. Retrieval/memory/knowledge graphs/vector stores (16)
# 4. Safety/policy/identity/security/anti-abuse (16)
# 5. Social layer/memetics/incentives/community tooling (16)

REPOS=(
  # Category 1: Agent Orchestration & Workflow Engines (16)
  "https://github.com/microsoft/autogen"
  "https://github.com/langchain-ai/langchain"
  "https://github.com/langchain-ai/langgraph"
  "https://github.com/run-llama/llama_index"
  "https://github.com/crewAIInc/crewAI"
  "https://github.com/joaomdmoura/crewAI"
  "https://github.com/phidatahq/phidata"
  "https://github.com/agno-agi/agno"
  "https://github.com/pydantic/pydantic-ai"
  "https://github.com/anthropics/anthropic-cookbook"
  "https://github.com/smol-ai/developer"
  "https://github.com/OpenBMB/AgentVerse"
  "https://github.com/aiwaves-cn/agents"
  "https://github.com/microsoft/semantic-kernel"
  "https://github.com/openai/openai-python"
  "https://github.com/BerriAI/litellm"

  # Category 2: Evaluation/Testing/Verification/Observability (16)
  "https://github.com/confident-ai/deepeval"
  "https://github.com/promptfoo/promptfoo"
  "https://github.com/langfuse/langfuse"
  "https://github.com/agenta-ai/agenta"
  "https://github.com/braintrustdata/braintrust-sdk"
  "https://github.com/hegelai/prompttools"
  "https://github.com/traceloop/openllmetry"
  "https://github.com/openlit/openlit"
  "https://github.com/phoenixframework/phoenix"
  "https://github.com/Arize-ai/phoenix"
  "https://github.com/whyLabs/langkit"
  "https://github.com/evidentlyai/evidently"
  "https://github.com/Galileo-Galilei/kedro-mlflow"
  "https://github.com/mlflow/mlflow"
  "https://github.com/zenml-io/zenml"
  "https://github.com/squaredev-io/matte"

  # Category 3: Retrieval/Memory/Knowledge Graphs/Vector Stores (16)
  "https://github.com/chroma-core/chroma"
  "https://github.com/qdrant/qdrant"
  "https://github.com/milvus-io/milvus"
  "https://github.com/pgvector/pgvector"
  "https://github.com/weaviate/weaviate"
  "https://github.com/pinecone-io/pinecone-python-client"
  "https://github.com/facebookresearch/faiss"
  "https://github.com/lancedb/lancedb"
  "https://github.com/marqo-ai/marqo"
  "https://github.com/redis/redis"
  "https://github.com/mem0ai/mem0"
  "https://github.com/getzep/zep"
  "https://github.com/neo4j/neo4j"
  "https://github.com/vespa-engine/vespa"
  "https://github.com/typesense/typesense"
  "https://github.com/meilisearch/meilisearch"

  # Category 4: Safety/Policy/Identity/Security/Anti-Abuse (16)
  "https://github.com/assistant-ui/assistant-ui"
  "https://github.com/Chainlit/chainlit"
  "https://github.com/ray-project/ray"
  "https://github.com/vllm-project/vllm"
  "https://github.com/huggingface/transformers"
  "https://github.com/huggingface/datasets"
  "https://github.com/huggingface/accelerate"
  "https://github.com/openai/gpt-2"
  "https://github.com/google/gemma.cpp"
  "https://github.com/meta-llama/llama"
  "https://github.com/meta-llama/llama-recipes"
  "https://github.com/mistralai/mistral-inference"
  "https://github.com/ollama/ollama"
  "https://github.com/ggerganov/llama.cpp"
  "https://github.com/ggerganov/whisper.cpp"
  "https://github.com/turboderp/exllamav2"

  # Category 5: Social Layer/Memetics/Incentives/Community Tooling (16)
  "https://github.com/discord/discord-api-docs"
  "https://github.com/slackapi/python-slack-sdk"
  "https://github.com/telegraf/telegraf"
  "https://github.com/python-telegram-bot/python-telegram-bot"
  "https://github.com/hubotio/hubot"
  "https://github.com/RasaHQ/rasa"
  "https://github.com/microsoft/botframework-sdk"
  "https://github.com/semver/semver"
  "https://github.com/All-Hands-AI/OpenHands"
  "https://github.com/continuedev/continue"
  "https://github.com/sourcegraph/cody"
  "https://github.com/cline/cline"
  "https://github.com/aider-ai/aider"
  "https://github.com/paul-gauthier/aider"
  "https://github.com/OpenInterpreter/open-interpreter"
  "https://github.com/KillianLucas/open-interpreter"
)

echo "Total repos: ${#REPOS[@]}"
echo "Starting validation..."

# Track results
declare -a RESULTS
declare -a GITHUB_DATA

for repo_url in "${REPOS[@]}"; do
  echo "Checking: $repo_url"
  
  # Extract owner/repo for GitHub API
  if [[ $repo_url =~ github.com/([^/]+)/([^/]+)$ ]]; then
    owner="${BASH_REMATCH[1]}"
    repo="${BASH_REMATCH[2]}"
    
    # Check if URL is accessible
    http_status=$(curl -s -o /dev/null -w "%{http_code}" "$repo_url" 2>/dev/null)
    
    if [ "$http_status" = "200" ]; then
      # Get GitHub API data
      api_url="https://api.github.com/repos/${owner}/${repo}"
      api_data=$(curl -s -H "Accept: application/vnd.github.v3+json" "$api_url" 2>/dev/null)
      
      stars=$(echo "$api_data" | grep -o '"stargazers_count": [0-9]*' | head -1 | grep -o '[0-9]*')
      forks=$(echo "$api_data" | grep -o '"forks_count": [0-9]*' | head -1 | grep -o '[0-9]*')
      open_issues=$(echo "$api_data" | grep -o '"open_issues_count": [0-9]*' | head -1 | grep -o '[0-9]*')
      updated_at=$(echo "$api_data" | grep -o '"updated_at": "[^"]*"' | head -1 | sed 's/"updated_at": "//' | sed 's/"$//')
      license=$(echo "$api_data" | grep -o '"spdx_id": "[^"]*"' | head -1 | sed 's/"spdx_id": "//' | sed 's/"$//')
      
      echo "  ✓ LIVE | Stars: ${stars:-N/A} | Forks: ${forks:-N/A} | Updated: ${updated_at:-N/A}"
      RESULTS+=("${repo_url}|LIVE|${stars}|${forks}|${open_issues}|${updated_at}|${license}")
    else
      echo "  ✗ FAILED (HTTP ${http_status})"
      RESULTS+=("${repo_url}|FAILED|${http_status}|||N/A")
    fi
  else
    echo "  ✗ INVALID URL format"
    RESULTS+=("${repo_url}|INVALID||||N/A")
  fi
  
  # Rate limiting - be nice to GitHub
  sleep 0.5
done

echo ""
echo "=== VALIDATION COMPLETE ==="
echo "Total checked: ${#RESULTS[@]}"

# Output summary
for result in "${RESULTS[@]}"; do
  echo "$result"
done
