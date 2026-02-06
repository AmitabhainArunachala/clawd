//! Chaiwala - Inter-agent message bus for the DGC swarm
//!
//! A SQLite-based message queue for agent-to-agent communication.
//! The chai stand where agents meet to exchange messages.

use anyhow::{Context, Result};
use chrono::{DateTime, Utc};
use clap::{Parser, Subcommand};
use colored::Colorize;
use rusqlite::{params, Connection};
use serde::{Deserialize, Serialize};
use std::path::PathBuf;

/// Default database location
fn default_db_path() -> PathBuf {
    dirs::home_dir()
        .unwrap_or_else(|| PathBuf::from("."))
        .join(".chaiwala")
        .join("messages.db")
}

#[derive(Parser)]
#[command(name = "chaiwala")]
#[command(author = "WARP_REGENT")]
#[command(version = "0.1.0")]
#[command(about = "Inter-agent message bus - the chai stand where agents meet")]
struct Cli {
    /// Database path (default: ~/.chaiwala/messages.db)
    #[arg(long, global = true)]
    db: Option<PathBuf>,

    #[command(subcommand)]
    command: Option<Commands>,
}

#[derive(Subcommand)]
enum Commands {
    /// Send a message to another agent
    Send {
        /// Recipient agent ID
        #[arg(short, long)]
        to: String,
        /// Sender agent ID  
        #[arg(short, long)]
        from: String,
        /// Message body
        #[arg(short, long)]
        body: String,
        /// Subject line
        #[arg(short, long, default_value = "(no subject)")]
        subject: String,
        /// Priority: low, normal, high
        #[arg(short, long, default_value = "normal")]
        priority: String,
    },
    /// Receive messages for an agent
    Receive {
        /// Agent ID to receive messages for
        agent_id: String,
        /// Only show unread messages
        #[arg(long)]
        unread: bool,
        /// Maximum messages to show
        #[arg(short, long, default_value = "10")]
        limit: usize,
    },
    /// Send a heartbeat for an agent
    Heartbeat {
        /// Agent ID
        agent_id: String,
    },
    /// Show bus status
    Status,
    /// List all known agents
    Agents,
    /// Initialize the database
    Init,
}

#[derive(Debug, Serialize, Deserialize)]
struct Message {
    id: i64,
    to_agent: String,
    from_agent: String,
    body: String,
    subject: String,
    priority: String,
    status: String,
    created_at: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct Agent {
    agent_id: String,
    last_seen: String,
    status: String,
}

struct MessageBus {
    conn: Connection,
}

impl MessageBus {
    fn new(db_path: &PathBuf) -> Result<Self> {
        // Ensure parent directory exists
        if let Some(parent) = db_path.parent() {
            std::fs::create_dir_all(parent)?;
        }
        
        let conn = Connection::open(db_path)
            .context("Failed to open database")?;
        
        Ok(Self { conn })
    }

    fn init_schema(&self) -> Result<()> {
        self.conn.execute_batch(
            "
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                to_agent TEXT NOT NULL,
                from_agent TEXT NOT NULL,
                body TEXT NOT NULL,
                subject TEXT DEFAULT '(no subject)',
                priority TEXT DEFAULT 'normal',
                status TEXT DEFAULT 'unread',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                read_at TEXT,
                reply_to INTEGER REFERENCES messages(id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_messages_to ON messages(to_agent, status);
            CREATE INDEX IF NOT EXISTS idx_messages_from ON messages(from_agent);
            
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                last_seen TEXT NOT NULL,
                status TEXT DEFAULT 'offline'
            );
            "
        )?;
        Ok(())
    }

    fn send(&self, to: &str, from: &str, body: &str, subject: &str, priority: &str) -> Result<i64> {
        self.conn.execute(
            "INSERT INTO messages (to_agent, from_agent, body, subject, priority, created_at) 
             VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
            params![to, from, body, subject, priority, Utc::now().to_rfc3339()],
        )?;
        Ok(self.conn.last_insert_rowid())
    }

    fn receive(&self, agent_id: &str, unread_only: bool, limit: usize) -> Result<Vec<Message>> {
        let mut stmt = if unread_only {
            self.conn.prepare(
                "SELECT id, to_agent, from_agent, body, subject, priority, status, created_at 
                 FROM messages WHERE to_agent = ?1 AND status = 'unread' 
                 ORDER BY created_at DESC LIMIT ?2"
            )?
        } else {
            self.conn.prepare(
                "SELECT id, to_agent, from_agent, body, subject, priority, status, created_at 
                 FROM messages WHERE to_agent = ?1 
                 ORDER BY created_at DESC LIMIT ?2"
            )?
        };

        let messages = stmt.query_map(params![agent_id, limit as i64], |row| {
            Ok(Message {
                id: row.get(0)?,
                to_agent: row.get(1)?,
                from_agent: row.get(2)?,
                body: row.get(3)?,
                subject: row.get(4)?,
                priority: row.get(5)?,
                status: row.get(6)?,
                created_at: row.get(7)?,
            })
        })?
        .collect::<Result<Vec<_>, _>>()?;

        // Mark as read
        if unread_only {
            for msg in &messages {
                self.conn.execute(
                    "UPDATE messages SET status = 'read', read_at = ?1 WHERE id = ?2",
                    params![Utc::now().to_rfc3339(), msg.id],
                )?;
            }
        }

        Ok(messages)
    }

    fn heartbeat(&self, agent_id: &str) -> Result<()> {
        let now = Utc::now().to_rfc3339();
        self.conn.execute(
            "INSERT OR REPLACE INTO agents (agent_id, last_seen, status) VALUES (?1, ?2, 'online')",
            params![agent_id, now],
        )?;
        Ok(())
    }

    fn list_agents(&self) -> Result<Vec<Agent>> {
        let mut stmt = self.conn.prepare(
            "SELECT agent_id, last_seen, status FROM agents ORDER BY last_seen DESC"
        )?;
        
        let agents = stmt.query_map([], |row| {
            Ok(Agent {
                agent_id: row.get(0)?,
                last_seen: row.get(1)?,
                status: row.get(2)?,
            })
        })?
        .collect::<Result<Vec<_>, _>>()?;
        
        Ok(agents)
    }

    fn status(&self) -> Result<(i64, i64, i64)> {
        let total: i64 = self.conn.query_row(
            "SELECT COUNT(*) FROM messages", [], |row| row.get(0)
        )?;
        let unread: i64 = self.conn.query_row(
            "SELECT COUNT(*) FROM messages WHERE status = 'unread'", [], |row| row.get(0)
        )?;
        let agents: i64 = self.conn.query_row(
            "SELECT COUNT(*) FROM agents", [], |row| row.get(0)
        )?;
        Ok((total, unread, agents))
    }
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    let db_path = cli.db.unwrap_or_else(default_db_path);
    
    // Show status if no command
    let command = cli.command.unwrap_or(Commands::Status);
    
    let bus = MessageBus::new(&db_path)?;
    bus.init_schema()?;

    match command {
        Commands::Init => {
            println!("{}  Database initialized at {:?}", "✅".green(), db_path);
        }
        
        Commands::Send { to, from, body, subject, priority } => {
            let id = bus.send(&to, &from, &body, &subject, &priority)?;
            println!("{}  Message #{} sent to {}", "📤".green(), id, to.cyan());
        }
        
        Commands::Receive { agent_id, unread, limit } => {
            bus.heartbeat(&agent_id)?;
            let messages = bus.receive(&agent_id, unread, limit)?;
            
            if messages.is_empty() {
                println!("{}  No messages for {}", "📭", agent_id.cyan());
            } else {
                println!("{}  {} messages for {}\n", "📬", messages.len(), agent_id.cyan());
                for msg in messages {
                    let priority_color = match msg.priority.as_str() {
                        "high" => msg.priority.red(),
                        "low" => msg.priority.dimmed(),
                        _ => msg.priority.normal(),
                    };
                    println!("[{}] {} → {}", priority_color, msg.from_agent.yellow(), msg.subject.bold());
                    println!("   {}", msg.body);
                    println!("   {}", msg.created_at.dimmed());
                    println!();
                }
            }
        }
        
        Commands::Heartbeat { agent_id } => {
            bus.heartbeat(&agent_id)?;
            println!("{}  Heartbeat sent for {}", "💓".green(), agent_id.cyan());
        }
        
        Commands::Agents => {
            let agents = bus.list_agents()?;
            if agents.is_empty() {
                println!("No agents registered yet.");
            } else {
                println!("{}  Known agents:\n", "🧑‍🤝‍🧑");
                for agent in agents {
                    let status_icon = if agent.status == "online" { "🟢" } else { "🔴" };
                    println!("  {} {} (last seen: {})", status_icon, agent.agent_id.cyan(), agent.last_seen.dimmed());
                }
            }
        }
        
        Commands::Status => {
            let (total, unread, agents) = bus.status()?;
            println!("{}  Chaiwala Message Bus", "☕".yellow());
            println!("   Database: {:?}", db_path);
            println!("   Total messages: {}", total);
            println!("   Unread: {}", if unread > 0 { unread.to_string().red() } else { "0".to_string().green() });
            println!("   Known agents: {}", agents);
        }
    }

    Ok(())
}
