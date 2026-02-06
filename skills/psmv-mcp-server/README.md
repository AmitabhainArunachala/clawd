# PSMV MCP Server

MCP (Model Context Protocol) server for Persistent Semantic Memory Vault search.

## Tools

### `search_vault(query, limit?)`
Search the vault for semantically similar memories/documents.
- `query`: Search string
- `limit`: Max results (default: 10)

### `get_crown_jewel(name)`
Retrieve a specific Crown Jewel (high-value curated knowledge).
- `name`: Crown Jewel identifier

## Setup

```bash
npm install
npm run build
```

## Usage

```bash
# Development
npm run dev

# Production
npm start
```

## MCP Configuration

Add to your MCP settings:

```json
{
  "mcpServers": {
    "psmv": {
      "command": "node",
      "args": ["path/to/psmv-mcp-server/dist/index.js"],
      "env": {
        "PSMV_PATH": "~/.psmv"
      }
    }
  }
}
```

## TODO

- [ ] Connect to actual vector store (Chroma/Qdrant)
- [ ] Implement embedding generation
- [ ] Add Crown Jewel persistence layer
- [ ] Add memory ingestion tools
