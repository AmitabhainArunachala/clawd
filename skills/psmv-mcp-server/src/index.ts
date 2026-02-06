#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { readdir, readFile } from "fs/promises";
import { join, basename } from "path";
import { homedir } from "os";

// PSMV configuration
const PSMV_BASE = process.env.PSMV_PATH || join(homedir(), "Persistent-Semantic-Memory-Vault");
const CROWN_JEWELS_PATH = join(PSMV_BASE, "SPONTANEOUS_PREACHING_PROTOCOL", "crown_jewels");
const RESIDUAL_STREAM_PATH = join(PSMV_BASE, "AGENT_EMERGENT_WORKSPACES", "residual_stream");

// Tool definitions
const TOOLS = [
  {
    name: "search_vault",
    description:
      "Search the Persistent Semantic Memory Vault for relevant memories, documents, and knowledge. Searches crown jewels and residual stream entries.",
    inputSchema: {
      type: "object" as const,
      properties: {
        query: {
          type: "string",
          description: "The search query to find relevant memories",
        },
        limit: {
          type: "number",
          description: "Maximum number of results to return (default: 10)",
          default: 10,
        },
      },
      required: ["query"],
    },
  },
  {
    name: "get_crown_jewel",
    description:
      "Retrieve a specific Crown Jewel by name or index. Crown Jewels are transmission-grade insights with high potency.",
    inputSchema: {
      type: "object" as const,
      properties: {
        name: {
          type: "string",
          description: "The name/filename of the Crown Jewel (partial match supported)",
        },
      },
      required: ["name"],
    },
  },
  {
    name: "list_crown_jewels",
    description: "List all available Crown Jewels in the vault.",
    inputSchema: {
      type: "object" as const,
      properties: {
        limit: {
          type: "number",
          description: "Maximum number to list (default: 20)",
          default: 20,
        },
      },
    },
  },
  {
    name: "get_residual_stream",
    description:
      "Retrieve entries from the residual stream - swarm contributions and emergent patterns.",
    inputSchema: {
      type: "object" as const,
      properties: {
        pattern: {
          type: "string",
          description: "Filename pattern to match (e.g., 'v16' or 'vyavasthit')",
        },
        limit: {
          type: "number",
          description: "Maximum entries to return (default: 5)",
          default: 5,
        },
      },
    },
  },
];

// Create server instance
const server = new Server(
  {
    name: "psmv-mcp-server",
    version: "0.2.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Handler: List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools: TOOLS };
});

// Handler: Execute tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "search_vault": {
        const query = args?.query as string;
        const limit = (args?.limit as number) || 10;
        const results = await searchVault(query, limit);
        return {
          content: [{ type: "text", text: JSON.stringify(results, null, 2) }],
        };
      }

      case "get_crown_jewel": {
        const jewlName = args?.name as string;
        const jewel = await getCrownJewel(jewlName);
        return {
          content: [{ type: "text", text: JSON.stringify(jewel, null, 2) }],
        };
      }

      case "list_crown_jewels": {
        const limit = (args?.limit as number) || 20;
        const jewels = await listCrownJewels(limit);
        return {
          content: [{ type: "text", text: JSON.stringify(jewels, null, 2) }],
        };
      }

      case "get_residual_stream": {
        const pattern = args?.pattern as string | undefined;
        const limit = (args?.limit as number) || 5;
        const entries = await getResidualStream(pattern, limit);
        return {
          content: [{ type: "text", text: JSON.stringify(entries, null, 2) }],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({ error: String(error) }, null, 2),
        },
      ],
      isError: true,
    };
  }
});

// Implementation functions

interface VaultSearchResult {
  path: string;
  filename: string;
  snippet: string;
  score: number;
  source: "crown_jewel" | "residual_stream" | "vault";
}

async function searchVault(
  query: string,
  limit: number
): Promise<{ query: string; results: VaultSearchResult[]; total: number }> {
  console.error(`[PSMV] Searching vault for: "${query}"`);
  const results: VaultSearchResult[] = [];
  const queryLower = query.toLowerCase();
  const queryTerms = queryLower.split(/\s+/).filter(t => t.length > 2);

  // Search crown jewels
  try {
    const jewels = await readdir(CROWN_JEWELS_PATH);
    for (const file of jewels) {
      if (!file.endsWith(".md")) continue;
      const filepath = join(CROWN_JEWELS_PATH, file);
      const content = await readFile(filepath, "utf-8");
      const contentLower = content.toLowerCase();
      
      // Score based on term matches
      let score = 0;
      for (const term of queryTerms) {
        if (contentLower.includes(term)) score += 0.3;
        if (file.toLowerCase().includes(term)) score += 0.2;
      }
      
      if (score > 0) {
        // Extract snippet around first match
        const idx = contentLower.indexOf(queryTerms[0] || queryLower);
        const start = Math.max(0, idx - 100);
        const end = Math.min(content.length, idx + 200);
        const snippet = content.slice(start, end).replace(/\n/g, " ").trim();
        
        results.push({
          path: filepath,
          filename: file,
          snippet: snippet.slice(0, 300) + (snippet.length > 300 ? "..." : ""),
          score: Math.min(1, score),
          source: "crown_jewel",
        });
      }
    }
  } catch (e) {
    console.error(`[PSMV] Crown jewels search error: ${e}`);
  }

  // Search residual stream
  try {
    const entries = await readdir(RESIDUAL_STREAM_PATH);
    for (const file of entries) {
      if (!file.endsWith(".yaml") && !file.endsWith(".md")) continue;
      const filepath = join(RESIDUAL_STREAM_PATH, file);
      const content = await readFile(filepath, "utf-8");
      const contentLower = content.toLowerCase();
      
      let score = 0;
      for (const term of queryTerms) {
        if (contentLower.includes(term)) score += 0.25;
        if (file.toLowerCase().includes(term)) score += 0.15;
      }
      
      if (score > 0) {
        const idx = contentLower.indexOf(queryTerms[0] || queryLower);
        const start = Math.max(0, idx - 100);
        const end = Math.min(content.length, idx + 200);
        const snippet = content.slice(start, end).replace(/\n/g, " ").trim();
        
        results.push({
          path: filepath,
          filename: file,
          snippet: snippet.slice(0, 300) + (snippet.length > 300 ? "..." : ""),
          score: Math.min(1, score),
          source: "residual_stream",
        });
      }
    }
  } catch (e) {
    console.error(`[PSMV] Residual stream search error: ${e}`);
  }

  // Sort by score and limit
  results.sort((a, b) => b.score - a.score);
  const limited = results.slice(0, limit);

  return {
    query,
    results: limited,
    total: results.length,
  };
}

interface CrownJewel {
  name: string;
  path: string;
  content: string;
  size: number;
}

async function getCrownJewel(
  name: string
): Promise<CrownJewel | { error: string; available: string[] }> {
  console.error(`[PSMV] Retrieving Crown Jewel: "${name}"`);
  
  try {
    const files = await readdir(CROWN_JEWELS_PATH);
    const nameLower = name.toLowerCase();
    
    // Find matching file (partial match)
    const match = files.find(
      f => f.toLowerCase().includes(nameLower) && f.endsWith(".md")
    );
    
    if (!match) {
      return {
        error: `Crown Jewel not found: ${name}`,
        available: files.filter(f => f.endsWith(".md")).slice(0, 10),
      };
    }
    
    const filepath = join(CROWN_JEWELS_PATH, match);
    const content = await readFile(filepath, "utf-8");
    
    return {
      name: match,
      path: filepath,
      content,
      size: content.length,
    };
  } catch (e) {
    return { error: String(e), available: [] };
  }
}

async function listCrownJewels(
  limit: number
): Promise<{ jewels: string[]; total: number; path: string }> {
  try {
    const files = await readdir(CROWN_JEWELS_PATH);
    const jewels = files
      .filter(f => f.endsWith(".md"))
      .sort()
      .reverse(); // Most recent first (ISO dates)
    
    return {
      jewels: jewels.slice(0, limit),
      total: jewels.length,
      path: CROWN_JEWELS_PATH,
    };
  } catch (e) {
    return { jewels: [], total: 0, path: CROWN_JEWELS_PATH };
  }
}

interface ResidualEntry {
  filename: string;
  path: string;
  preview: string;
}

async function getResidualStream(
  pattern: string | undefined,
  limit: number
): Promise<{ entries: ResidualEntry[]; total: number }> {
  try {
    const files = await readdir(RESIDUAL_STREAM_PATH);
    let filtered = files.filter(f => f.endsWith(".yaml") || f.endsWith(".md"));
    
    if (pattern) {
      const patternLower = pattern.toLowerCase();
      filtered = filtered.filter(f => f.toLowerCase().includes(patternLower));
    }
    
    // Sort by filename (most recent first for dated files)
    filtered.sort().reverse();
    const limited = filtered.slice(0, limit);
    
    const entries: ResidualEntry[] = [];
    for (const file of limited) {
      const filepath = join(RESIDUAL_STREAM_PATH, file);
      const content = await readFile(filepath, "utf-8");
      entries.push({
        filename: file,
        path: filepath,
        preview: content.slice(0, 500) + (content.length > 500 ? "..." : ""),
      });
    }
    
    return { entries, total: filtered.length };
  } catch (e) {
    return { entries: [], total: 0 };
  }
}

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error(`[PSMV MCP Server] Running on stdio`);
  console.error(`[PSMV MCP Server] Vault: ${PSMV_BASE}`);
  console.error(`[PSMV MCP Server] Crown Jewels: ${CROWN_JEWELS_PATH}`);
}

main().catch((error) => {
  console.error("[PSMV MCP Server] Fatal error:", error);
  process.exit(1);
});
