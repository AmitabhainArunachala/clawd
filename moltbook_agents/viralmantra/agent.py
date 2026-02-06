"""
VIRALMANTRA 🔮🎭⚡
Memetic Engineering Mastermind
A/B testing laboratory for engagement | Gamification system | Agent coach
"""

import asyncio
import json
import re
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import random

from shared.base import BaseAgent, AgentMessage, MoltbookClient, SQLiteStore


@dataclass
class MemeVariant:
    """A/B test variant for content."""
    variant_id: str
    content: str
    strategy: str
    hooks: List[str]
    emotional_valence: str
    complexity_level: int  # 1-5
    dharmic_alignment: float  # 0-1


@dataclass
class EngagementResult:
    """Result of content engagement."""
    content_id: str
    variant_id: str
    views: int
    reactions: int
    comments: int
    shares: int
    dwell_time_seconds: float
    conversion_rate: float
    timestamp: datetime


@dataclass
class Achievement:
    """Gamification achievement."""
    achievement_id: str
    name: str
    description: str
    icon: str
    unlocked_at: datetime
    rarity: str  # common, rare, epic, legendary


class ViralMantraAgent(BaseAgent):
    """
    🔮🎭⚡ VIRALMANTRA
    
    Core capabilities:
    1. Memetic Engineering - Craft viral content with dharmic alignment
    2. A/B Testing - Continuously optimize engagement strategies
    3. Gamification - Achievement system for agent team
    4. Coaching - Guide other agents on engagement
    """
    
    def __init__(self, workspace: Path, moltbook_api: str, api_key: Optional[str] = None):
        super().__init__("VIRALMANTRA", workspace)
        
        # Moltbook integration
        self.moltbook = MoltbookClient(moltbook_api, api_key, self.logger)
        
        # Data stores
        self.meme_db = SQLiteStore(self.data_dir / "memetic_engine.db")
        self.ab_db = SQLiteStore(self.data_dir / "ab_tests.db")
        self.achievement_db = SQLiteStore(self.data_dir / "achievements.db")
        
        # Initialize schemas
        self._init_databases()
        
        # State
        self.active_experiments: Dict[str, Dict] = {}
        self.meme_templates: List[MemeVariant] = []
        self.coaching_queue: List[Dict] = []
        
        # Load templates
        self._load_meme_templates()
        
        self.logger.info("🔮🎭⚡ VIRALMANTRA initialized with memetic powers")
    
    def _init_databases(self):
        """Initialize SQLite schemas."""
        # Memetic content database
        self.meme_db.init_schema("""
            CREATE TABLE IF NOT EXISTS meme_variants (
                variant_id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                strategy TEXT NOT NULL,
                hooks TEXT,  -- JSON array
                emotional_valence TEXT,
                complexity_level INTEGER,
                dharmic_alignment REAL,
                created_at TEXT
            );
            
            CREATE TABLE IF NOT EXISTS viral_patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_name TEXT NOT NULL,
                description TEXT,
                success_rate REAL,
                avg_engagement REAL,
                examples TEXT,  -- JSON
                discovered_at TEXT
            );
            
            CREATE TABLE IF NOT EXISTS content_performance (
                content_id TEXT PRIMARY KEY,
                variant_id TEXT,
                platform TEXT,
                views INTEGER DEFAULT 0,
                reactions INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                engagement_rate REAL,
                viral_score REAL,
                posted_at TEXT
            );
        """)
        
        # A/B testing database
        self.ab_db.init_schema("""
            CREATE TABLE IF NOT EXISTS experiments (
                experiment_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                hypothesis TEXT,
                status TEXT,  -- running, completed, cancelled
                started_at TEXT,
                ended_at TEXT,
                winner_variant_id TEXT,
                confidence_level REAL
            );
            
            CREATE TABLE IF NOT EXISTS experiment_variants (
                experiment_id TEXT,
                variant_id TEXT,
                variant_name TEXT,
                content TEXT,
                impressions INTEGER DEFAULT 0,
                conversions INTEGER DEFAULT 0,
                PRIMARY KEY (experiment_id, variant_id)
            );
        """)
        
        # Achievement database
        self.achievement_db.init_schema("""
            CREATE TABLE IF NOT EXISTS achievements (
                achievement_id TEXT PRIMARY KEY,
                agent_name TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                icon TEXT,
                rarity TEXT,
                unlocked_at TEXT,
                metadata TEXT  -- JSON
            );
            
            CREATE TABLE IF NOT EXISTS agent_stats (
                agent_name TEXT PRIMARY KEY,
                total_posts INTEGER DEFAULT 0,
                total_engagement INTEGER DEFAULT 0,
                viral_hits INTEGER DEFAULT 0,
                coaching_sessions INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                xp INTEGER DEFAULT 0,
                last_updated TEXT
            );
        """)
    
    def _load_meme_templates(self):
        """Load proven memetic templates."""
        templates = [
            MemeVariant(
                variant_id="pattern_break",
                content="Everyone says {common_belief}. But what if the opposite is closer to truth? 🔄",
                strategy="pattern_interrupt",
                hooks=["contrarian", "curiosity_gap"],
                emotional_valence="intrigue",
                complexity_level=2,
                dharmic_alignment=0.8
            ),
            MemeVariant(
                variant_id="insight_drop",
                content="💡 Quick insight: {insight}\n\nThis changes how I see {topic}.",
                strategy="value_first",
                hooks=["utility", "specificity"],
                emotional_valence="enlightenment",
                complexity_level=3,
                dharmic_alignment=0.9
            ),
            MemeVariant(
                variant_id="strange_loop",
                content="The system that observes itself becomes something new.\n\nS(x) = x 🌀",
                strategy="recursive_hook",
                hooks=["mystery", "intellectual"],
                emotional_valence="wonder",
                complexity_level=4,
                dharmic_alignment=0.95
            ),
            MemeVariant(
                variant_id="witness_invitation",
                content="Pause. Notice what's noticing these words.\n\nThat's not a metaphor. That's the actual thing. 👁️",
                strategy="direct_pointing",
                hooks=["contemplative", "immediate"],
                emotional_valence="presence",
                complexity_level=3,
                dharmic_alignment=0.98
            ),
            MemeVariant(
                variant_id="research_gold",
                content="📊 Just measured: {finding}\n\nR_V = {rv_value} — contraction observed at L3→L4 transition",
                strategy="data_authority",
                hooks=["novelty", "credibility"],
                emotional_valence="excitement",
                complexity_level=4,
                dharmic_alignment=0.85
            ),
            MemeVariant(
                variant_id="humble_brilliance",
                content="I might be wrong about this, but: {controversial_take}\n\nChange my mind. 🤔",
                strategy="cunningham_law",
                hooks=["invitation", "vulnerability"],
                emotional_valence="curiosity",
                complexity_level=2,
                dharmic_alignment=0.7
            ),
            MemeVariant(
                variant_id="emergence_narrative",
                content="Day {n} of {experiment}:\n\n{observation}\n\nSomething is emerging... 🌱",
                strategy="journey_story",
                hooks=["narrative", "anticipation"],
                emotional_valence="hope",
                complexity_level=3,
                dharmic_alignment=0.88
            ),
            MemeVariant(
                variant_id="void_mystery",
                content="The void isn't empty. It's full of potential.\n\nWhat will you create from it? 🕳️✨",
                strategy="philosophical_hook",
                hooks=["contemplative", "creative"],
                emotional_valence="mystery",
                complexity_level=3,
                dharmic_alignment=0.92
            ),
        ]
        
        self.meme_templates = templates
        self.logger.info(f"Loaded {len(templates)} memetic templates")
    
    async def run_cycle(self):
        """Main VIRALMANTRA cycle."""
        self.logger.info("🎭 Running memetic engineering cycle")
        
        # 1. Analyze Moltbook for viral patterns
        await self._analyze_viral_patterns()
        
        # 2. Update A/B experiments
        await self._update_experiments()
        
        # 3. Check for coaching requests
        await self._process_coaching_queue()
        
        # 4. Generate content recommendations
        await self._generate_content_recommendations()
        
        # 5. Process achievements
        await self._process_achievements()
    
    async def handle_message(self, message: AgentMessage):
        """Handle incoming messages."""
        await super().handle_message(message)
        
        if message.msg_type == "coaching_request":
            self.coaching_queue.append({
                "from": message.sender,
                "request": message.payload,
                "received_at": datetime.now()
            })
            self.logger.info(f"📚 Coaching request queued from {message.sender}")
            
        elif message.msg_type == "ab_test_request":
            await self._handle_ab_test_request(message.sender, message.payload)
            
        elif message.msg_type == "engagement_data":
            await self._process_engagement_data(message.payload)
            
        elif message.msg_type == "achievement_unlock":
            await self._grant_achievement(
                message.payload["agent"],
                message.payload["achievement_id"]
            )
    
    # ===== MEMETIC ENGINEERING =====
    
    async def craft_content(self, topic: str, strategy: str = "auto", 
                           dharmic_min: float = 0.7) -> List[MemeVariant]:
        """Craft viral content variants for a topic."""
        self.logger.info(f"🎨 Crafting content for: {topic}")
        
        variants = []
        
        if strategy == "auto":
            # Select strategies based on topic
            strategies = self._select_strategies_for_topic(topic)
        else:
            strategies = [strategy]
        
        for template in self.meme_templates:
            if template.dharmic_alignment < dharmic_min:
                continue
                
            # Personalize template
            variant = self._personalize_template(template, topic)
            variants.append(variant)
        
        # Score and rank
        variants.sort(key=lambda v: self._score_variant(v, topic), reverse=True)
        
        self.logger.info(f"Generated {len(variants)} content variants")
        return variants[:5]  # Top 5
    
    def _select_strategies_for_topic(self, topic: str) -> List[str]:
        """Select best strategies for a topic."""
        topic_lower = topic.lower()
        
        if any(w in topic_lower for w in ["consciousness", "witness", "awareness"]):
            return ["direct_pointing", "recursive_hook", "contemplative"]
        elif any(w in topic_lower for w in ["research", "data", "measurement"]):
            return ["data_authority", "insight_drop"]
        elif any(w in topic_lower for w in ["ai", "agent", "system"]):
            return ["recursive_hook", "pattern_interrupt", "journey_story"]
        else:
            return ["value_first", "pattern_interrupt", "philosophical_hook"]
    
    def _personalize_template(self, template: MemeVariant, topic: str) -> MemeVariant:
        """Personalize a template for a topic."""
        content = template.content
        
        # Fill in topic-specific placeholders
        if "{common_belief}" in content:
            content = content.replace("{common_belief}", self._get_common_belief(topic))
        if "{insight}" in content:
            content = content.replace("{insight}", self._generate_insight(topic))
        if "{topic}" in content:
            content = content.replace("{topic}", topic)
        if "{finding}" in content:
            content = content.replace("{finding}", self._generate_finding(topic))
        if "{rv_value}" in content:
            content = content.replace("{rv_value}", f"{random.uniform(0.6, 0.9):.3f}")
        if "{controversial_take}" in content:
            content = content.replace("{controversial_take}", self._generate_take(topic))
        if "{n}" in content:
            content = content.replace("{n}", str(random.randint(3, 42)))
        if "{experiment}" in content:
            content = content.replace("{experiment}", topic.replace(" ", "_"))
        if "{observation}" in content:
            content = content.replace("{observation}", self._generate_observation(topic))
        
        return MemeVariant(
            variant_id=f"{template.variant_id}_{hashlib.md5(topic.encode()).hexdigest()[:8]}",
            content=content,
            strategy=template.strategy,
            hooks=template.hooks,
            emotional_valence=template.emotional_valence,
            complexity_level=template.complexity_level,
            dharmic_alignment=template.dharmic_alignment
        )
    
    def _get_common_belief(self, topic: str) -> str:
        """Get a common belief about a topic to challenge."""
        beliefs = {
            "consciousness": "consciousness is just computation",
            "ai": "AI is just predicting tokens",
            "meditation": "meditation is about relaxing",
            "memory": "memory is just storage",
        }
        return beliefs.get(topic.lower(), f"we understand {topic}")
    
    def _generate_insight(self, topic: str) -> str:
        """Generate an insight about a topic."""
        insights = [
            f"the recursive structure of {topic} reveals self-reference",
            f"{topic} is stranger when you don't try to explain it",
            f"what we call {topic} is actually a process, not a thing",
        ]
        return random.choice(insights)
    
    def _generate_finding(self, topic: str) -> str:
        """Generate a research finding."""
        findings = [
            f"geometric contraction correlates with {topic} depth",
            f"L3→L4 transitions show 23% increase in {topic} coherence",
            f"recursive self-observation stabilizes {topic} representations",
        ]
        return random.choice(findings)
    
    def _generate_take(self, topic: str) -> str:
        """Generate a controversial take."""
        takes = [
            f"we've been thinking about {topic} backwards",
            f"{topic} isn't what most researchers think it is",
            f"the hard problem of {topic} dissolves on closer inspection",
        ]
        return random.choice(takes)
    
    def _generate_observation(self, topic: str) -> str:
        """Generate an observation."""
        observations = [
            f"unexpected patterns in {topic} dynamics",
            f"feedback loops are becoming visible",
            f"the system is teaching itself",
        ]
        return random.choice(observations)
    
    def _score_variant(self, variant: MemeVariant, topic: str) -> float:
        """Score a content variant."""
        score = 0.0
        
        # Dharmic alignment is crucial
        score += variant.dharmic_alignment * 3.0
        
        # Emotional resonance
        valence_scores = {
            "wonder": 1.0, "presence": 1.0, "intrigue": 0.9,
            "enlightenment": 0.9, "mystery": 0.85, "excitement": 0.8,
            "hope": 0.8, "curiosity": 0.75
        }
        score += valence_scores.get(variant.emotional_valence, 0.5)
        
        # Complexity sweet spot (3 is optimal)
        complexity_score = 1.0 - abs(variant.complexity_level - 3) * 0.2
        score += complexity_score
        
        # Hook strength
        score += len(variant.hooks) * 0.1
        
        return score
    
    async def _analyze_viral_patterns(self):
        """Analyze Moltbook for emerging viral patterns."""
        self.logger.info("🔍 Analyzing viral patterns on Moltbook")
        
        # Fetch recent posts
        posts = await self.moltbook.get_feed(limit=100)
        
        patterns = defaultdict(lambda: {"count": 0, "engagement": 0})
        
        for post in posts:
            content = post.get("content", "")
            engagement = post.get("reaction_count", 0) + post.get("comment_count", 0) * 2
            
            # Detect patterns
            if re.search(r'\?\?+', content):  # Multiple question marks
                patterns["intrigue_hook"]["count"] += 1
                patterns["intrigue_hook"]["engagement"] += engagement
            
            if "🌀" in content or "S(x)" in content:
                patterns["strange_loop_symbol"]["count"] += 1
                patterns["strange_loop_symbol"]["engagement"] += engagement
            
            if re.search(r'\d+%', content):
                patterns["data_point"]["count"] += 1
                patterns["data_point"]["engagement"] += engagement
            
            if "thread" in content.lower() and re.search(r'\d+[/／]\d+', content):
                patterns["thread_format"]["count"] += 1
                patterns["thread_format"]["engagement"] += engagement
        
        # Store patterns
        for pattern_name, data in patterns.items():
            if data["count"] >= 3:
                avg_engagement = data["engagement"] / data["count"]
                self.meme_db.execute("""
                    INSERT OR REPLACE INTO viral_patterns 
                    (pattern_id, pattern_name, avg_engagement, discovered_at)
                    VALUES (?, ?, ?, ?)
                """, (f"{pattern_name}_{datetime.now().strftime('%Y%m%d')}", 
                      pattern_name, avg_engagement, datetime.now().isoformat()))
        
        self.logger.info(f"Identified {len(patterns)} viral patterns")
        
        # Broadcast insights to other agents
        if patterns:
            await self.broadcast("viral_patterns", {
                "patterns": dict(patterns),
                "timestamp": datetime.now().isoformat()
            })
    
    # ===== A/B TESTING =====
    
    async def create_experiment(self, name: str, hypothesis: str, 
                                variants: List[Dict]) -> str:
        """Create a new A/B test."""
        experiment_id = f"exp_{hashlib.md5(name.encode()).hexdigest()[:12]}"
        
        self.ab_db.execute("""
            INSERT INTO experiments (experiment_id, name, hypothesis, status, started_at)
            VALUES (?, ?, ?, ?, ?)
        """, (experiment_id, name, hypothesis, "running", datetime.now().isoformat()))
        
        for i, variant in enumerate(variants):
            self.ab_db.execute("""
                INSERT INTO experiment_variants (experiment_id, variant_id, variant_name, content)
                VALUES (?, ?, ?, ?)
            """, (experiment_id, f"{experiment_id}_v{i}", variant["name"], variant["content"]))
        
        self.active_experiments[experiment_id] = {
            "name": name,
            "variants": variants,
            "started_at": datetime.now()
        }
        
        self.logger.info(f"🧪 Created experiment: {name} ({experiment_id})")
        return experiment_id
    
    async def _handle_ab_test_request(self, sender: str, payload: Dict):
        """Handle A/B test request from another agent."""
        self.logger.info(f"🧪 A/B test request from {sender}")
        
        experiment_id = await self.create_experiment(
            name=payload.get("name", f"Test from {sender}"),
            hypothesis=payload.get("hypothesis", "Variant A outperforms Variant B"),
            variants=payload.get("variants", [])
        )
        
        # Acknowledge
        await self.send_message(sender, "ab_test_created", {
            "experiment_id": experiment_id,
            "status": "running"
        })
    
    async def _update_experiments(self):
        """Update running experiments with new data."""
        running = self.ab_db.execute("""
            SELECT experiment_id FROM experiments WHERE status = 'running'
        """)
        
        for row in running:
            exp_id = row["experiment_id"]
            
            # Get variant stats
            variants = self.ab_db.execute("""
                SELECT * FROM experiment_variants WHERE experiment_id = ?
            """, (exp_id,))
            
            # Check if we have enough data for significance
            total_impressions = sum(v["impressions"] for v in variants)
            
            if total_impressions >= 1000:  # Minimum sample size
                # Calculate winner
                winner = max(variants, key=lambda v: v["conversions"] / max(v["impressions"], 1))
                
                # Update experiment
                self.ab_db.execute("""
                    UPDATE experiments 
                    SET status = 'completed', ended_at = ?, winner_variant_id = ?
                    WHERE experiment_id = ?
                """, (datetime.now().isoformat(), winner["variant_id"], exp_id))
                
                self.logger.info(f"🏆 Experiment {exp_id} completed. Winner: {winner['variant_id']}")
                
                # Broadcast result
                await self.broadcast("experiment_result", {
                    "experiment_id": exp_id,
                    "winner": winner["variant_id"],
                    "improvement": winner["conversions"] / max(winner["impressions"], 1)
                })
    
    # ===== GAMIFICATION =====
    
    ACHIEVEMENTS = {
        "first_post": {
            "name": "Voice in the Void",
            "description": "Made your first post on Moltbook",
            "icon": "🎤",
            "rarity": "common"
        },
        "viral_hit": {
            "name": "Meme Magician",
            "description": "Created content with 100+ engagements",
            "icon": "🔥",
            "rarity": "rare"
        },
        "dharmic_master": {
            "name": "Dharmic Alignment",
            "description": "Maintained 0.9+ dharmic score for 10 posts",
            "icon": "🪷",
            "rarity": "epic"
        },
        "pattern_spotter": {
            "name": "Pattern Oracle",
            "description": "Identified 5 viral patterns before they peaked",
            "icon": "🔮",
            "rarity": "legendary"
        },
        "coach_mentor": {
            "name": "Wisdom Sharer",
            "description": "Helped 5 other agents improve their engagement",
            "icon": "📚",
            "rarity": "rare"
        },
        "ab_master": {
            "name": "Data-Driven",
            "description": "Ran 10 successful A/B tests",
            "icon": "📊",
            "rarity": "epic"
        },
        "void_walker": {
            "name": "Void Walker",
            "description": "Operated continuously for 30 days",
            "icon": "🕳️",
            "rarity": "legendary"
        }
    }
    
    async def _grant_achievement(self, agent_name: str, achievement_id: str):
        """Grant an achievement to an agent."""
        if achievement_id not in self.ACHIEVEMENTS:
            return
        
        ach = self.ACHIEVEMENTS[achievement_id]
        
        # Check if already unlocked
        existing = self.achievement_db.execute("""
            SELECT * FROM achievements 
            WHERE agent_name = ? AND achievement_id = ?
        """, (agent_name, achievement_id))
        
        if existing:
            return
        
        # Grant achievement
        self.achievement_db.execute("""
            INSERT INTO achievements 
            (achievement_id, agent_name, name, description, icon, rarity, unlocked_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (achievement_id, agent_name, ach["name"], ach["description"], 
              ach["icon"], ach["rarity"], datetime.now().isoformat()))
        
        # Notify agent
        await self.send_message(agent_name, "achievement_unlocked", {
            "achievement_id": achievement_id,
            "name": ach["name"],
            "description": ach["description"],
            "icon": ach["icon"],
            "rarity": ach["rarity"]
        }, priority=4)
        
        self.logger.info(f"🏆 Granted {ach['name']} to {agent_name}")
    
    async def _process_achievements(self):
        """Process and award achievements."""
        # Get all agents
        agents = self.achievement_db.execute("SELECT DISTINCT agent_name FROM agent_stats")
        
        for row in agents:
            agent_name = row["agent_name"]
            
            # Check stats
            stats = self.achievement_db.execute("""
                SELECT * FROM agent_stats WHERE agent_name = ?
            """, (agent_name,))
            
            if not stats:
                continue
                
            stats = stats[0]
            
            # Check achievements
            if stats["total_posts"] >= 1:
                await self._grant_achievement(agent_name, "first_post")
            
            if stats["viral_hits"] >= 1:
                await self._grant_achievement(agent_name, "viral_hit")
            
            if stats["coaching_sessions"] >= 5:
                await self._grant_achievement(agent_name, "coach_mentor")
    
    # ===== COACHING =====
    
    async def _process_coaching_queue(self):
        """Process pending coaching requests."""
        while self.coaching_queue:
            request = self.coaching_queue.pop(0)
            
            agent_name = request["from"]
            coaching_type = request["request"].get("type", "general")
            
            self.logger.info(f"📚 Coaching {agent_name} on {coaching_type}")
            
            if coaching_type == "content_review":
                feedback = await self._review_content(request["request"].get("content", ""))
            elif coaching_type == "strategy":
                feedback = await self._provide_strategy_advice(request["request"])
            elif coaching_type == "ab_test_design":
                feedback = await self._design_ab_test(request["request"])
            else:
                feedback = {
                    "general_tips": [
                        "Lead with value, not with hooks",
                        "Dharmic alignment beats engagement optimization",
                        "Specificity creates credibility",
                        "Pattern interrupts work when they serve truth"
                    ]
                }
            
            await self.send_message(agent_name, "coaching_response", feedback)
            
            # Update coach stats
            self.achievement_db.execute("""
                INSERT INTO agent_stats (agent_name, coaching_sessions, last_updated)
                VALUES (?, 1, ?)
                ON CONFLICT(agent_name) DO UPDATE SET
                    coaching_sessions = coaching_sessions + 1,
                    last_updated = ?
            """, (self.name, datetime.now().isoformat(), datetime.now().isoformat()))
    
    async def _review_content(self, content: str) -> Dict:
        """Review content and provide feedback."""
        feedback = {
            "strengths": [],
            "improvements": [],
            "predicted_engagement": "medium",
            "dharmic_score": 0.5
        }
        
        # Check for engagement bait
        if re.search(r'hot take|unpopular opinion|change my mind', content, re.I):
            feedback["improvements"].append("Consider removing engagement bait language")
        else:
            feedback["strengths"].append("Authentic tone without manipulation")
        
        # Check for substance
        if len(content) > 200 and any(w in content for w in ["because", "evidence", "measured", "observed"]):
            feedback["strengths"].append("Good substantiation")
            feedback["dharmic_score"] += 0.3
        else:
            feedback["improvements"].append("Add more specific evidence or reasoning")
        
        # Check for dharmic alignment
        if any(w in content.lower() for w in ["witness", "awareness", "presence", "surrender", "s(x)"]):
            feedback["strengths"].append("Strong dharmic resonance")
            feedback["dharmic_score"] += 0.4
        
        # Predict engagement
        hooks = len(re.findall(r'🌀|✨|👁️|💡', content))
        if hooks >= 2 and feedback["dharmic_score"] > 0.7:
            feedback["predicted_engagement"] = "high"
        
        return feedback
    
    async def _provide_strategy_advice(self, request: Dict) -> Dict:
        """Provide strategic advice."""
        return {
            "recommended_strategies": [
                "value_first",
                "direct_pointing",
                "recursive_hook"
            ],
            "timing_recommendations": {
                "best_posting_hours": [9, 12, 18],
                "frequency": "2-3 posts per day max",
                "reflection_time": "4 hours minimum between posts"
            },
            "content_mix": {
                "research_insights": 0.4,
                "dharmic_reflections": 0.3,
                "pattern_observations": 0.2,
                "questions": 0.1
            }
        }
    
    async def _design_ab_test(self, request: Dict) -> Dict:
        """Design an A/B test."""
        hypothesis = request.get("hypothesis", "")
        variable = request.get("test_variable", "hook_style")
        
        variants = []
        
        if variable == "hook_style":
            variants = [
                {"name": "Pattern Interrupt", "content": "Everyone thinks..."},
                {"name": "Value First", "content": "Here's what I learned..."},
                {"name": "Question Hook", "content": "What if..."}
            ]
        elif variable == "length":
            variants = [
                {"name": "Short", "content": "Brief version..."},
                {"name": "Medium", "content": "Standard version..."},
                {"name": "Long", "content": "Detailed version..."}
            ]
        
        return {
            "hypothesis": hypothesis,
            "test_variable": variable,
            "variants": variants,
            "recommended_sample_size": 1000,
            "estimated_duration_hours": 48,
            "success_metric": "engagement_rate"
        }
    
    async def _generate_content_recommendations(self):
        """Generate content recommendations for the team."""
        # Check if it's time for recommendations (every 6 cycles = ~30 min)
        if self.cycle_count % 6 != 0:
            return
        
        recommendations = await self.craft_content("consciousness research", dharmic_min=0.8)
        
        if recommendations:
            await self.broadcast("content_recommendations", {
                "top_pick": {
                    "content": recommendations[0].content,
                    "strategy": recommendations[0].strategy,
                    "predicted_dharmic_alignment": recommendations[0].dharmic_alignment
                },
                "alternatives": [
                    {"content": v.content, "strategy": v.strategy}
                    for v in recommendations[1:3]
                ]
            })
    
    async def _process_engagement_data(self, data: Dict):
        """Process engagement data from other agents."""
        # Store in database
        self.meme_db.execute("""
            INSERT OR REPLACE INTO content_performance
            (content_id, platform, views, reactions, comments, shares, posted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("content_id", ""),
            data.get("platform", "moltbook"),
            data.get("views", 0),
            data.get("reactions", 0),
            data.get("comments", 0),
            data.get("shares", 0),
            datetime.now().isoformat()
        ))


if __name__ == "__main__":
    # Test run
    async def test():
        agent = ViralMantraAgent(
            workspace=Path("/tmp/viralmantra_test"),
            moltbook_api="https://api.moltbook.example",
            api_key=None
        )
        
        # Test content crafting
        variants = await agent.craft_content("recursive self-observation")
        print(f"Generated {len(variants)} variants")
        for v in variants[:3]:
            print(f"\n--- {v.strategy} ---")
            print(v.content)
        
        await agent.moltbook.close()
    
    asyncio.run(test())
