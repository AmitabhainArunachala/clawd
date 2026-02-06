#!/usr/bin/env npx ts-node
/**
 * Direct CLI for PSMV access (bypasses MCP protocol)
 * Usage:
 *   npx ts-node cli.ts search "witness consciousness" --limit 5
 *   npx ts-node cli.ts jewel "operational"
 *   npx ts-node cli.ts list
 *   npx ts-node cli.ts stream --pattern "v16"
 */

import { readdir, readFile } from "fs/promises";
import { join } from "path";
import { homedir } from "os";

const PSMV_BASE = process.env.PSMV_PATH || join(homedir(), "Persistent-Semantic-Memory-Vault");
const CROWN_JEWELS_PATH = join(PSMV_BASE, "SPONTANEOUS_PREACHING_PROTOCOL", "crown_jewels");
const RESIDUAL_STREAM_PATH = join(PSMV_BASE, "AGENT_EMERGENT_WORKSPACES", "residual_stream");

async function search(query: string, limit = 10) {
  const results: any[] = [];
  const queryLower = query.toLowerCase();
  const terms = queryLower.split(/\s+/).filter(t => t.length > 2);

  // Search crown jewels
  const jewels = await readdir(CROWN_JEWELS_PATH);
  for (const file of jewels) {
    if (!file.endsWith(".md")) continue;
    const content = await readFile(join(CROWN_JEWELS_PATH, file), "utf-8");
    const contentLower = content.toLowerCase();
    
    let score = 0;
    for (const term of terms) {
      if (contentLower.includes(term)) score += 0.3;
      if (file.toLowerCase().includes(term)) score += 0.2;
    }
    
    if (score > 0) {
      const idx = contentLower.indexOf(terms[0] || queryLower);
      const start = Math.max(0, idx - 50);
      const end = Math.min(content.length, idx + 150);
      results.push({
        file,
        score: Math.min(1, score),
        snippet: content.slice(start, end).replace(/\n/g, " ").trim(),
        source: "crown_jewel"
      });
    }
  }

  // Search residual stream
  const entries = await readdir(RESIDUAL_STREAM_PATH);
  for (const file of entries) {
    if (!file.endsWith(".yaml") && !file.endsWith(".md")) continue;
    const content = await readFile(join(RESIDUAL_STREAM_PATH, file), "utf-8");
    const contentLower = content.toLowerCase();
    
    let score = 0;
    for (const term of terms) {
      if (contentLower.includes(term)) score += 0.25;
      if (file.toLowerCase().includes(term)) score += 0.15;
    }
    
    if (score > 0) {
      const idx = contentLower.indexOf(terms[0] || queryLower);
      const start = Math.max(0, idx - 50);
      const end = Math.min(content.length, idx + 150);
      results.push({
        file,
        score: Math.min(1, score),
        snippet: content.slice(start, end).replace(/\n/g, " ").trim(),
        source: "residual_stream"
      });
    }
  }

  results.sort((a, b) => b.score - a.score);
  return results.slice(0, limit);
}

async function getJewel(name: string) {
  const files = await readdir(CROWN_JEWELS_PATH);
  const nameLower = name.toLowerCase();
  const match = files.find(f => f.toLowerCase().includes(nameLower) && f.endsWith(".md"));
  
  if (!match) {
    return { error: `Not found: ${name}`, available: files.filter(f => f.endsWith(".md")).slice(0, 5) };
  }
  
  const content = await readFile(join(CROWN_JEWELS_PATH, match), "utf-8");
  return { name: match, content };
}

async function listJewels(limit = 20) {
  const files = await readdir(CROWN_JEWELS_PATH);
  return files.filter(f => f.endsWith(".md")).sort().reverse().slice(0, limit);
}

async function getStream(pattern?: string, limit = 5) {
  const files = await readdir(RESIDUAL_STREAM_PATH);
  let filtered = files.filter(f => f.endsWith(".yaml") || f.endsWith(".md"));
  
  if (pattern) {
    filtered = filtered.filter(f => f.toLowerCase().includes(pattern.toLowerCase()));
  }
  
  filtered.sort().reverse();
  const results = [];
  
  for (const file of filtered.slice(0, limit)) {
    const content = await readFile(join(RESIDUAL_STREAM_PATH, file), "utf-8");
    results.push({ file, preview: content.slice(0, 300) });
  }
  
  return results;
}

// CLI handling
async function main() {
  const args = process.argv.slice(2);
  const cmd = args[0];

  try {
    switch (cmd) {
      case "search": {
        const query = args[1];
        const limitIdx = args.indexOf("--limit");
        const limit = limitIdx > -1 ? parseInt(args[limitIdx + 1]) : 10;
        const results = await search(query, limit);
        console.log(JSON.stringify(results, null, 2));
        break;
      }
      case "jewel": {
        const name = args[1];
        const result = await getJewel(name);
        console.log(JSON.stringify(result, null, 2));
        break;
      }
      case "list": {
        const limitIdx = args.indexOf("--limit");
        const limit = limitIdx > -1 ? parseInt(args[limitIdx + 1]) : 20;
        const jewels = await listJewels(limit);
        console.log(JSON.stringify(jewels, null, 2));
        break;
      }
      case "stream": {
        const patternIdx = args.indexOf("--pattern");
        const pattern = patternIdx > -1 ? args[patternIdx + 1] : undefined;
        const limitIdx = args.indexOf("--limit");
        const limit = limitIdx > -1 ? parseInt(args[limitIdx + 1]) : 5;
        const entries = await getStream(pattern, limit);
        console.log(JSON.stringify(entries, null, 2));
        break;
      }
      default:
        console.log(`PSMV CLI
Usage:
  search <query> [--limit N]  Search vault
  jewel <name>                Get crown jewel
  list [--limit N]            List crown jewels
  stream [--pattern P] [--limit N]  Get residual stream`);
    }
  } catch (e) {
    console.error("Error:", e);
    process.exit(1);
  }
}

main();
