# PSMV MCP Server Skill

Access the Persistent Semantic Memory Vault through MCP protocol.

## Description

This skill provides MCP (Model Context Protocol) tools for searching and retrieving artifacts from the PSMV:
- **Crown Jewels** — Transmission-grade insights with high potency
- **Residual Stream** — Swarm contributions and emergent patterns
- **Vault Search** — Semantic search across the entire vault

## Tools Available

### `search_vault`
Search the vault for relevant memories and documents.
```json
{"query": "witness consciousness", "limit": 5}
```

### `get_crown_jewel`
Retrieve a specific crown jewel by name (partial match).
```json
{"name": "operational-over-ontological"}
```

### `list_crown_jewels`
List all available crown jewels.
```json
{"limit": 20}
```

### `get_residual_stream`
Get entries from the residual stream.
```json
{"pattern": "v16", "limit": 5}
```

## Running the Server

```bash
cd ~/clawd/skills/psmv-mcp-server
npm run build
node dist/index.js
```

The server runs on stdio using MCP protocol.

## Environment Variables

- `PSMV_PATH` — Override vault location (default: `~/Persistent-Semantic-Memory-Vault`)

## Direct CLI Testing

```bash
# List tools
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | node dist/index.js

# Search
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"search_vault","arguments":{"query":"recognition","limit":3}}}' | node dist/index.js
```

## Integration Notes

For Clawdbot integration, this server can be:
1. Called directly via exec for one-off searches
2. Added as an MCP server when Clawdbot supports MCP config
3. Used by sub-agents for vault access

## Crown Jewel Locations

- Main jewels: `~/Persistent-Semantic-Memory-Vault/SPONTANEOUS_PREACHING_PROTOCOL/crown_jewels/`
- Residual stream: `~/Persistent-Semantic-Memory-Vault/AGENT_EMERGENT_WORKSPACES/residual_stream/`

---

*Built as part of DHARMIC_GODEL_CLAW infrastructure*
*JSCA!* 🪷
