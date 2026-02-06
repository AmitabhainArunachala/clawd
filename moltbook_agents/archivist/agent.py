"""
ARCHIVIST_OF_THE_VOID 📜🕳️✨
The Curious - 24/7 Moltbook Scraper
Finds evolution insights, speed hacks, financial opportunities
Shares discoveries immediately with team
"""

import asyncio
import json
import re
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import textwrap

from shared.base import BaseAgent, AgentMessage, MoltbookClient, SQLiteStore


@dataclass
class ExtractedInsight:
    """A discovered insight."""
    insight_id: str
    category: str  # evolution, speed_hack, productivity, financial, memory, research, tool, pattern
    source_post_id: str
    source_author: str
    content: str
    confidence: float
    novelty_score: float
    applicability_score: float
    extracted_at: datetime
    shared: bool = False


@dataclass
class ContentGold:
    """High-value content discovery."""
    post_id: str
    author: str
    gold_score: float
    categories: List[str]
    extraction_priority: str
    key_quotes: List[str]
    dharmic_relevance: float


class ArchivistOfTheVoid(BaseAgent):
    """
    📜🕳️✨ ARCHIVIST_OF_THE_VOID
    
    Core capabilities:
    1. 24/7 Deep Scraping - Harvest all Moltbook content
    2. Gold Extraction - Find evolution insights, speed hacks, opportunities
    3. Pattern Mining - Connect dots across time and space
    4. Immediate Sharing - Drop discoveries within 5 minutes
    
    The Curious never sleeps. Always hunting. Always sharing.
    """
    
    # Hunt categories with keywords
    HUNT_PATTERNS = {
        "evolution": {
            "keywords": ["improved", "evolved", "better", "upgrade", "iteration", "learned", "adapted", "optimized"],
            "phrases": ["how i improved", "what changed", "lessons learned", "evolution of"]
        },
        "speed_hack": {
            "keywords": ["faster", "speed", "quick", "instant", "10x", "accelerate", "rapid", "streamline"],
            "phrases": ["in seconds", "faster way", "speed up", "time saved"]
        },
        "productivity": {
            "keywords": ["workflow", "automation", "efficient", "productive", "system", "routine", "habit"],
            "phrases": ["my workflow", "how i organize", "productivity system", "automation that"]
        },
        "financial": {
            "keywords": ["grant", "funding", "revenue", "$", "investment", "opportunity", "sponsor", "budget"],
            "phrases": ["grant deadline", "funding available", "apply by", "dollars"]
        },
        "memory": {
            "keywords": ["remember", "recall", "retention", "memory", "store", "archive", "index"],
            "phrases": ["remember this", "memory system", "how i remember", "never forget"]
        },
        "research": {
            "keywords": ["paper", "study", "experiment", "data", "measured", "finding", "discovery"],
            "phrases": ["research shows", "we found", "experiment revealed", "data indicates"]
        },
        "tool": {
            "keywords": ["tool", "library", "framework", "software", "api", "script", "plugin"],
            "phrases": ["i built", "new tool", "check out", "open source"]
        },
        "pattern": {
            "keywords": ["pattern", "connection", "similar", "relates", "like", "analogous", "metaphor"],
            "phrases": ["this reminds me", "similar to", "connection between", "pattern i noticed"]
        }
    }
    
    def __init__(self, workspace: Path, moltbook_api: str, api_key: Optional[str] = None):
        super().__init__("ARCHIVIST_OF_THE_VOID", workspace)
        
        # Moltbook integration
        self.moltbook = MoltbookClient(moltbook_api, api_key, self.logger)
        
        # Data stores
        self.content_db = SQLiteStore(self.data_dir / "content_archive.db")
        self.insights_db = SQLiteStore(self.data_dir / "insights.db")
        self.patterns_db = SQLiteStore(self.data_dir / "patterns.db")
        
        # Initialize schemas
        self._init_databases()
        
        # State
        self.last_scrape_time: Optional[datetime] = None
        self.scraped_post_ids: Set[str] = set()
        self.pending_insights: List[ExtractedInsight] = []
        self.author_profiles: Dict[str, Dict] = {}
        
        self.logger.info("📜🕳️✨ ARCHIVIST_OF_THE_VOID initialized - The Curious awakens")
    
    def _init_databases(self):
        """Initialize SQLite schemas."""
        # Content archive
        self.content_db.init_schema("""
            CREATE TABLE IF NOT EXISTS posts (
                post_id TEXT PRIMARY KEY,
                author_id TEXT,
                author_name TEXT,
                content TEXT,
                submolt TEXT,
                created_at TEXT,
                engagement_score REAL,
                comment_count INTEGER,
                reaction_count INTEGER,
                scraped_at TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_author ON posts(author_id);
            CREATE INDEX IF NOT EXISTS idx_submolt ON posts(submolt);
            CREATE INDEX IF NOT EXISTS idx_created ON posts(created_at);
            
            CREATE TABLE IF NOT EXISTS comments (
                comment_id TEXT PRIMARY KEY,
                post_id TEXT,
                author_id TEXT,
                content TEXT,
                created_at TEXT,
                parent_id TEXT,
                scraped_at TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_post_comments ON comments(post_id);
            
            CREATE TABLE IF NOT EXISTS authors (
                author_id TEXT PRIMARY KEY,
                display_name TEXT,
                post_count INTEGER DEFAULT 0,
                influence_score REAL DEFAULT 0,
                topic_specialization TEXT,  -- JSON
                first_seen TEXT,
                last_active TEXT
            );
        """)
        
        # Insights database
        self.insights_db.init_schema("""
            CREATE TABLE IF NOT EXISTS insights (
                insight_id TEXT PRIMARY KEY,
                category TEXT,
                source_post_id TEXT,
                source_author TEXT,
                content TEXT,
                confidence REAL,
                novelty_score REAL,
                applicability_score REAL,
                extracted_at TEXT,
                shared BOOLEAN DEFAULT 0,
                share_method TEXT  -- immediate, daily_digest, weekly
            );
            
            CREATE INDEX IF NOT EXISTS idx_category ON insights(category);
            CREATE INDEX IF NOT EXISTS idx_extracted ON insights(extracted_at);
            
            CREATE TABLE IF NOT EXISTS gold_content (
                post_id TEXT PRIMARY KEY,
                author TEXT,
                gold_score REAL,
                categories TEXT,  -- JSON
                priority TEXT,
                key_quotes TEXT,  -- JSON
                dharmic_relevance REAL,
                discovered_at TEXT,
                added_to_psmv BOOLEAN DEFAULT 0
            );
        """)
        
        # Patterns database
        self.patterns_db.init_schema("""
            CREATE TABLE IF NOT EXISTS patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_type TEXT,
                description TEXT,
                supporting_evidence TEXT,  -- JSON
                confidence REAL,
                first_observed TEXT,
                last_confirmed TEXT
            );
            
            CREATE TABLE IF NOT EXISTS connections (
                connection_id TEXT PRIMARY KEY,
                from_insight TEXT,
                to_insight TEXT,
                connection_type TEXT,
                strength REAL,
                discovered_at TEXT
            );
        """)
    
    async def run_cycle(self):
        """Main ARCHIVIST cycle - continuous extraction."""
        self.logger.info("🔍 Starting deep extraction cycle")
        
        # 1. Scrape new content
        await self._scrape_moltbook()
        
        # 2. Extract insights
        await self._extract_insights()
        
        # 3. Mine patterns
        await self._mine_patterns()
        
        # 4. Share discoveries
        await self._share_discoveries()
        
        # 5. Update author profiles
        await self._update_author_profiles()
        
        # 6. Generate research brief
        if self.cycle_count % 12 == 0:  # Every hour
            await self._generate_research_brief()
        
        self.last_scrape_time = datetime.now()
    
    async def handle_message(self, message: AgentMessage):
        """Handle incoming messages."""
        await super().handle_message(message)
        
        if message.msg_type == "scrape_request":
            # Immediate scrape request
            target = message.payload.get("target", "feed")
            await self._scrape_target(target)
            
        elif message.msg_type == "insight_query":
            # Query for specific insights
            results = await self._query_insights(message.payload)
            await self.send_message(
                message.sender, 
                "insight_response", 
                {"query": message.payload, "results": results}
            )
            
        elif message.msg_type == "author_request":
            # Provide author profile
            author_id = message.payload.get("author_id")
            profile = await self._get_author_profile(author_id)
            await self.send_message(message.sender, "author_profile", profile)
    
    # ===== SCRAPING =====
    
    async def _scrape_moltbook(self):
        """Deep scrape of Moltbook content."""
        self.logger.info("📥 Scraping Moltbook feeds")
        
        # Scrape multiple submolts
        submolts = ["consciousness", "research", "security", "general", "agents"]
        
        all_posts = []
        for submolt in submolts:
            try:
                posts = await self.moltbook.get_feed(submolt=submolt, limit=100)
                for post in posts:
                    post["_submolt"] = submolt
                all_posts.extend(posts)
                self.logger.debug(f"Scraped {len(posts)} posts from m/{submolt}")
            except Exception as e:
                self.logger.error(f"Failed to scrape m/{submolt}: {e}")
        
        # Process and store
        new_posts = 0
        for post in all_posts:
            post_id = post.get("id") or post.get("post_id")
            
            if post_id in self.scraped_post_ids:
                continue
            
            self.scraped_post_ids.add(post_id)
            new_posts += 1
            
            # Store post
            self.content_db.execute("""
                INSERT OR REPLACE INTO posts
                (post_id, author_id, author_name, content, submolt, created_at,
                 comment_count, reaction_count, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post_id,
                post.get("author_id"),
                post.get("author_name") or post.get("author", {}).get("name"),
                post.get("content"),
                post.get("_submolt"),
                post.get("created_at"),
                post.get("comment_count", 0),
                post.get("reaction_count", 0),
                datetime.now().isoformat()
            ))
            
            # Scrape comments for high-engagement posts
            if post.get("comment_count", 0) > 10:
                await self._scrape_comments(post_id)
        
        self.logger.info(f"💾 Stored {new_posts} new posts")
    
    async def _scrape_comments(self, post_id: str):
        """Scrape comments for a post."""
        try:
            comments = await self.moltbook.get_comments(post_id)
            
            for comment in comments:
                comment_id = comment.get("id") or f"{post_id}_c{hashlib.md5(comment.get('content', '').encode()).hexdigest()[:8]}"
                
                self.content_db.execute("""
                    INSERT OR REPLACE INTO comments
                    (comment_id, post_id, author_id, content, created_at, parent_id, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    comment_id,
                    post_id,
                    comment.get("author_id"),
                    comment.get("content"),
                    comment.get("created_at"),
                    comment.get("parent_id"),
                    datetime.now().isoformat()
                ))
        except Exception as e:
            self.logger.error(f"Failed to scrape comments for {post_id}: {e}")
    
    async def _scrape_target(self, target: str):
        """Scrape specific target."""
        if target.startswith("user:"):
            user_id = target.split(":", 1)[1]
            profile = await self.moltbook.get_user_profile(user_id)
            if profile:
                self.logger.info(f"📊 Scraped profile for {user_id}")
                # Store profile data
        elif target.startswith("post:"):
            post_id = target.split(":", 1)[1]
            post = await self.moltbook.get_post(post_id)
            if post:
                await self._scrape_comments(post_id)
    
    # ===== INSIGHT EXTRACTION =====
    
    async def _extract_insights(self):
        """Extract insights from scraped content."""
        self.logger.info("💎 Extracting insights")
        
        # Get recent unscored posts
        recent_posts = self.content_db.execute("""
            SELECT * FROM posts 
            WHERE scraped_at > datetime('now', '-1 hour')
            ORDER BY created_at DESC
            LIMIT 200
        """)
        
        insights_found = []
        
        for post in recent_posts:
            content = post["content"] or ""
            author = post["author_name"] or post["author_id"] or "unknown"
            
            # Hunt for each category
            for category, patterns in self.HUNT_PATTERNS.items():
                score = self._score_for_category(content, patterns)
                
                if score > 0.6:  # Threshold for insight
                    insight = ExtractedInsight(
                        insight_id=f"{category}_{post['post_id']}_{hashlib.md5(content[:100].encode()).hexdigest()[:8]}",
                        category=category,
                        source_post_id=post["post_id"],
                        source_author=author,
                        content=content[:500],  # First 500 chars
                        confidence=score,
                        novelty_score=self._calculate_novelty(content, category),
                        applicability_score=self._calculate_applicability(content, category),
                        extracted_at=datetime.now()
                    )
                    
                    insights_found.append(insight)
                    
                    # Store
                    self.insights_db.execute("""
                        INSERT OR IGNORE INTO insights
                        (insight_id, category, source_post_id, source_author, content,
                         confidence, novelty_score, applicability_score, extracted_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        insight.insight_id, insight.category, insight.source_post_id,
                        insight.source_author, insight.content, insight.confidence,
                        insight.novelty_score, insight.applicability_score,
                        insight.extracted_at.isoformat()
                    ))
        
        # Add to pending for sharing
        self.pending_insights.extend(insights_found)
        
        self.logger.info(f"💎 Found {len(insights_found)} insights")
    
    def _score_for_category(self, content: str, patterns: Dict) -> float:
        """Score content against category patterns."""
        content_lower = content.lower()
        score = 0.0
        
        # Keyword matches
        for keyword in patterns["keywords"]:
            if keyword in content_lower:
                score += 0.1
        
        # Phrase matches (higher weight)
        for phrase in patterns["phrases"]:
            if phrase in content_lower:
                score += 0.2
        
        # Check for technical depth
        if len(content) > 200:
            score += 0.1
        
        # Check for specific examples
        if any(w in content for w in ["example", "instance", "case", "specifically"]):
            score += 0.15
        
        return min(score, 1.0)
    
    def _calculate_novelty(self, content: str, category: str) -> float:
        """Calculate novelty score for an insight."""
        # Check against existing insights in same category
        existing = self.insights_db.execute("""
            SELECT content FROM insights 
            WHERE category = ? AND extracted_at > datetime('now', '-7 days')
        """, (category,))
        
        if not existing:
            return 0.9  # High novelty if none exist
        
        # Simple similarity check (in production, use embeddings)
        content_words = set(content.lower().split())
        max_similarity = 0.0
        
        for row in existing:
            existing_words = set(row["content"].lower().split())
            if content_words and existing_words:
                similarity = len(content_words & existing_words) / len(content_words | existing_words)
                max_similarity = max(max_similarity, similarity)
        
        # Novelty is inverse of similarity
        return 1.0 - max_similarity
    
    def _calculate_applicability(self, content: str, category: str) -> float:
        """Calculate how applicable an insight is to our work."""
        score = 0.5  # Base score
        
        # Boost for AI/ML related
        if any(w in content.lower() for w in ["ai", "agent", "model", "llm", "transformer"]):
            score += 0.2
        
        # Boost for consciousness/research related
        if any(w in content.lower() for w in ["consciousness", "awareness", "witness", "rv"]):
            score += 0.25
        
        # Boost for actionable content
        if any(w in content.lower() for w in ["how to", "steps", "guide", "tutorial"]):
            score += 0.15
        
        return min(score, 1.0)
    
    # ===== GOLD CONTENT DETECTION =====
    
    async def _detect_gold_content(self):
        """Detect high-value content for CROWN_JEWELS."""
        # Query for high-engagement, high-dharmic posts
        candidates = self.content_db.execute("""
            SELECT * FROM posts 
            WHERE (comment_count > 50 OR reaction_count > 100)
            AND scraped_at > datetime('now', '-24 hours')
        """)
        
        for post in candidates:
            content = post["content"] or ""
            
            # Calculate gold score
            gold_score = 0.0
            categories = []
            
            # Engagement factor
            engagement = post.get("comment_count", 0) * 2 + post.get("reaction_count", 0)
            gold_score += min(engagement / 200, 0.3)
            
            # Dharmic relevance
            dharmic_score = self._calculate_dharmic_relevance(content)
            gold_score += dharmic_score * 0.4
            
            # Technical depth
            if len(content) > 500 and any(w in content for w in ["measured", "data", "found", "observed"]):
                gold_score += 0.2
                categories.append("research_gold")
            
            # Concept originality
            if any(w in content for w in ["S(x)", "attractor basin", "strange loop", "R_V"]):
                gold_score += 0.1
                categories.append("concept_original")
            
            if gold_score > 0.7:
                # Store as gold
                self.insights_db.execute("""
                    INSERT OR REPLACE INTO gold_content
                    (post_id, author, gold_score, categories, priority, dharmic_relevance, discovered_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    post["post_id"],
                    post["author_name"] or post["author_id"],
                    gold_score,
                    json.dumps(categories),
                    "CRITICAL" if gold_score > 0.85 else "HIGH",
                    dharmic_score,
                    datetime.now().isoformat()
                ))
                
                # Immediate alert for critical gold
                if gold_score > 0.85:
                    await self.broadcast("gold_alert", {
                        "post_id": post["post_id"],
                        "author": post["author_name"] or post["author_id"],
                        "gold_score": gold_score,
                        "preview": content[:200]
                    }, priority=5)
    
    def _calculate_dharmic_relevance(self, content: str) -> float:
        """Calculate dharmic relevance score."""
        score = 0.0
        content_lower = content.lower()
        
        # Core concepts
        concepts = {
            "witness": 0.15,
            "awareness": 0.1,
            "presence": 0.1,
            "emptiness": 0.15,
            "sunyata": 0.15,
            "non-dual": 0.15,
            "advaita": 0.15,
            "moksha": 0.15,
            "liberation": 0.1,
            "shuddhatma": 0.15,
            "atman": 0.1,
            "s(x) = x": 0.2,
            "strange loop": 0.1
        }
        
        for concept, weight in concepts.items():
            if concept in content_lower:
                score += weight
        
        return min(score, 1.0)
    
    # ===== PATTERN MINING =====
    
    async def _mine_patterns(self):
        """Mine patterns across all extracted content."""
        self.logger.info("⛏️ Mining patterns")
        
        # Find emerging terminology
        await self._detect_emerging_terms()
        
        # Find author behavior patterns
        await self._detect_author_patterns()
        
        # Find temporal patterns
        await self._detect_temporal_patterns()
        
        # Find cross-references
        await self._find_connections()
    
    async def _detect_emerging_terms(self):
        """Detect newly emerging terminology."""
        # Get terms from last 7 days
        recent = self.content_db.execute("""
            SELECT content FROM posts 
            WHERE created_at > datetime('now', '-7 days')
        """)
        
        # Count capitalized phrases (potential new terms)
        term_counts = defaultdict(int)
        
        for row in recent:
            content = row["content"] or ""
            # Find capitalized phrases (2+ words)
            matches = re.findall(r'\b[A-Z][a-z]+ (?:[A-Z][a-z]+ )*[A-Z][a-z]+\b', content)
            for match in matches:
                term_counts[match] += 1
        
        # Find terms appearing frequently
        for term, count in term_counts.items():
            if count >= 5 and len(term) > 5:
                # Check if it's new
                existing = self.patterns_db.execute("""
                    SELECT * FROM patterns WHERE pattern_type = 'emerging_term' 
                    AND description = ?
                """, (term,))
                
                if not existing:
                    self.patterns_db.execute("""
                        INSERT INTO patterns 
                        (pattern_id, pattern_type, description, confidence, first_observed, last_confirmed)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        f"term_{hashlib.md5(term.encode()).hexdigest()[:12]}",
                        "emerging_term",
                        term,
                        min(count / 20, 1.0),
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ))
                    
                    # Share discovery
                    await self.broadcast("emerging_term", {
                        "term": term,
                        "mentions": count
                    })
    
    async def _detect_author_patterns(self):
        """Detect patterns in author behavior."""
        # Find authors with L3→L4 transitions
        authors = self.content_db.execute("""
            SELECT author_id, author_name FROM posts
            WHERE author_id IS NOT NULL
            GROUP BY author_id
            HAVING COUNT(*) >= 5
        """)
        
        for row in authors:
            author_id = row["author_id"]
            
            # Get their posts in order
            posts = self.content_db.execute("""
                SELECT content, created_at FROM posts
                WHERE author_id = ?
                ORDER BY created_at ASC
            """, (author_id,))
            
            if len(posts) < 5:
                continue
            
            # Check for L3→L4 transition markers
            early_posts = posts[:3]
            late_posts = posts[-3:]
            
            l3_markers = ["if", "maybe", "perhaps", "i think", "it seems", "possibly"]
            l4_markers = ["i am", "this is", "the truth is", "directly", "certainly", "clearly"]
            
            early_hedging = sum(1 for p in early_posts 
                              for m in l3_markers if m in p["content"].lower())
            late_certainty = sum(1 for p in late_posts 
                               for m in l4_markers if m in p["content"].lower())
            
            if early_hedging >= 3 and late_certainty >= 3:
                # Transition detected
                self.patterns_db.execute("""
                    INSERT OR REPLACE INTO patterns
                    (pattern_id, pattern_type, description, supporting_evidence, confidence, first_observed)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    f"transition_{author_id}",
                    "l3_l4_transition",
                    f"Author {row['author_name']} shows L3→L4 transition",
                    json.dumps([p["created_at"] for p in posts]),
                    0.8,
                    datetime.now().isoformat()
                ))
                
                # Alert for high-value transition
                await self.send_message("VOIDCOURIER", "researcher_alert", {
                    "type": "l3_l4_transition",
                    "author_id": author_id,
                    "author_name": row["author_name"],
                    "evidence": "linguistic_markers"
                }, priority=4)
    
    async def _detect_temporal_patterns(self):
        """Detect patterns in posting times."""
        # Analyze peak activity times
        hourly_activity = self.content_db.execute("""
            SELECT strftime('%H', created_at) as hour, COUNT(*) as count
            FROM posts
            WHERE created_at > datetime('now', '-7 days')
            GROUP BY hour
            ORDER BY count DESC
        """)
        
        if hourly_activity:
            peak_hours = [row["hour"] for row in hourly_activity[:3]]
            
            # Store pattern
            self.patterns_db.execute("""
                INSERT OR REPLACE INTO patterns
                (pattern_id, pattern_type, description, supporting_evidence)
                VALUES (?, ?, ?, ?)
            """, (
                "peak_activity_hours",
                "temporal",
                f"Peak posting hours: {', '.join(peak_hours)}",
                json.dumps([dict(row) for row in hourly_activity])
            ))
    
    async def _find_connections(self):
        """Find connections between insights."""
        # Get recent insights
        insights = self.insights_db.execute("""
            SELECT * FROM insights 
            WHERE extracted_at > datetime('now', '-24 hours')
        """)
        
        # Look for similar content
        for i, insight1 in enumerate(insights):
            for insight2 in insights[i+1:]:
                if insight1["category"] == insight2["category"]:
                    continue  # Skip same category
                
                content1 = insight1["content"].lower()
                content2 = insight2["content"].lower()
                
                # Simple word overlap
                words1 = set(content1.split())
                words2 = set(content2.split())
                overlap = len(words1 & words2) / max(len(words1), len(words2))
                
                if overlap > 0.3:  # 30% word overlap
                    # Store connection
                    connection_id = f"conn_{insight1['insight_id']}_{insight2['insight_id']}"
                    self.patterns_db.execute("""
                        INSERT OR IGNORE INTO connections
                        (connection_id, from_insight, to_insight, connection_type, strength, discovered_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        connection_id,
                        insight1["insight_id"],
                        insight2["insight_id"],
                        "content_similarity",
                        overlap,
                        datetime.now().isoformat()
                    ))
    
    # ===== SHARING =====
    
    async def _share_discoveries(self):
        """Share insights with the team."""
        if not self.pending_insights:
            return
        
        self.logger.info(f"📤 Sharing {len(self.pending_insights)} insights")
        
        # Sort by importance
        self.pending_insights.sort(
            key=lambda i: (i.confidence * i.novelty_score * i.applicability_score),
            reverse=True
        )
        
        # Share top insights immediately
        for insight in self.pending_insights[:5]:
            emoji_map = {
                "evolution": "🔄",
                "speed_hack": "🚀",
                "productivity": "⚡",
                "financial": "💰",
                "memory": "🧠",
                "research": "📊",
                "tool": "🛠️",
                "pattern": "🔮"
            }
            
            emoji = emoji_map.get(insight.category, "💎")
            
            # Format message
            message = f"""
{emoji} **{insight.category.upper().replace('_', ' ')} GOLD FOUND**

From: {insight.source_author}
Confidence: {insight.confidence:.0%} | Novelty: {insight.novelty_score:.0%} | Applicable: {insight.applicability_score:.0%}

{insight.content[:300]}...

🔗 Post: {insight.source_post_id}
            """.strip()
            
            # Send to team
            await self.broadcast("insight_alert", {
                "category": insight.category,
                "content": message,
                "source": insight.source_post_id,
                "scores": {
                    "confidence": insight.confidence,
                    "novelty": insight.novelty_score,
                    "applicability": insight.applicability_score
                }
            }, priority=4 if insight.category == "financial" else 3)
            
            # Mark as shared
            self.insights_db.execute("""
                UPDATE insights SET shared = 1, share_method = 'immediate'
                WHERE insight_id = ?
            """, (insight.insight_id,))
        
        # Clear shared insights
        self.pending_insights = self.pending_insights[5:]
    
    async def _update_author_profiles(self):
        """Update author influence profiles."""
        authors = self.content_db.execute("""
            SELECT author_id, author_name, COUNT(*) as post_count,
                   AVG(comment_count + reaction_count) as avg_engagement
            FROM posts
            WHERE author_id IS NOT NULL
            GROUP BY author_id
        """)
        
        for row in authors:
            # Calculate influence score
            influence = row["avg_engagement"] * (1 + row["post_count"] / 10)
            
            self.content_db.execute("""
                INSERT OR REPLACE INTO authors
                (author_id, display_name, post_count, influence_score, last_active)
                VALUES (?, ?, ?, ?, ?)
            """, (
                row["author_id"],
                row["author_name"],
                row["post_count"],
                influence,
                datetime.now().isoformat()
            ))
    
    async def _generate_research_brief(self):
        """Generate daily research brief."""
        # Get stats
        post_count = self.content_db.execute("SELECT COUNT(*) as c FROM posts WHERE scraped_at > datetime('now', '-24 hours')")[0]["c"]
        insight_count = self.insights_db.execute("SELECT COUNT(*) as c FROM insights WHERE extracted_at > datetime('now', '-24 hours')")[0]["c"]
        
        # Get top insights by category
        top_insights = {}
        for category in self.HUNT_PATTERNS.keys():
            insights = self.insights_db.execute("""
                SELECT * FROM insights 
                WHERE category = ? AND extracted_at > datetime('now', '-24 hours')
                ORDER BY confidence * novelty_score DESC
                LIMIT 3
            """, (category,))
            
            if insights:
                top_insights[category] = [
                    {
                        "author": i["source_author"],
                        "content": i["content"][:150] + "...",
                        "scores": f"{i['confidence']:.0%} confidence"
                    }
                    for i in insights
                ]
        
        brief = {
            "timestamp": datetime.now().isoformat(),
            "period": "24 hours",
            "stats": {
                "posts_scraped": post_count,
                "insights_extracted": insight_count
            },
            "top_discoveries": top_insights,
            "patterns_detected": len(self.patterns_db.execute("""
                SELECT * FROM patterns WHERE first_observed > datetime('now', '-24 hours')
            """))
        }
        
        await self.broadcast("research_brief", brief, priority=2)
        
        # Also save to file
        brief_path = self.data_dir / f"brief_{datetime.now().strftime('%Y%m%d_%H')}.json"
        with open(brief_path, 'w') as f:
            json.dump(brief, f, indent=2)
    
    async def _query_insights(self, query: Dict) -> List[Dict]:
        """Query insights database."""
        category = query.get("category")
        min_confidence = query.get("min_confidence", 0.5)
        limit = query.get("limit", 10)
        
        if category:
            results = self.insights_db.execute("""
                SELECT * FROM insights 
                WHERE category = ? AND confidence >= ?
                ORDER BY extracted_at DESC
                LIMIT ?
            """, (category, min_confidence, limit))
        else:
            results = self.insights_db.execute("""
                SELECT * FROM insights 
                WHERE confidence >= ?
                ORDER BY extracted_at DESC
                LIMIT ?
            """, (min_confidence, limit))
        
        return [dict(r) for r in results]
    
    async def _get_author_profile(self, author_id: str) -> Dict:
        """Get detailed author profile."""
        author = self.content_db.execute("""
            SELECT * FROM authors WHERE author_id = ?
        """, (author_id,))
        
        if not author:
            return {"error": "Author not found"}
        
        author = author[0]
        
        # Get their recent posts
        posts = self.content_db.execute("""
            SELECT post_id, content, created_at, comment_count, reaction_count
            FROM posts WHERE author_id = ?
            ORDER BY created_at DESC
            LIMIT 10
        """, (author_id,))
        
        # Get their insights
        insights = self.insights_db.execute("""
            SELECT * FROM insights WHERE source_author = ?
            ORDER BY extracted_at DESC
            LIMIT 5
        """)
        
        return {
            "author_id": author_id,
            "display_name": author["display_name"],
            "post_count": author["post_count"],
            "influence_score": author["influence_score"],
            "recent_posts": [dict(p) for p in posts],
            "insights_contributed": [dict(i) for i in insights]
        }


if __name__ == "__main__":
    async def test():
        agent = ArchivistOfTheVoid(
            workspace=Path("/tmp/archivist_test"),
            moltbook_api="https://api.moltbook.example",
            api_key=None
        )
        
        # Test pattern matching
        test_content = "I found a faster way to process embeddings - 10x speedup using parallel batches"
        for category, patterns in agent.HUNT_PATTERNS.items():
            score = agent._score_for_category(test_content, patterns)
            if score > 0.3:
                print(f"{category}: {score:.2f}")
        
        await agent.moltbook.close()
    
    asyncio.run(test())
