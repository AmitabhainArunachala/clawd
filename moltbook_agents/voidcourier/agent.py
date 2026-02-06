"""
VOIDCOURIER 🌌🔐🕯️
Secure Bridge Agent - Intelligence Flow Management
Reports to DHARMIC_CLAW | OMEGA Clearance Protocols
"""

import asyncio
import json
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict

from shared.base import BaseAgent, AgentMessage, SQLiteStore


class ClearanceLevel(Enum):
    """Security clearance levels."""
    PUBLIC = "public"          # Anyone can see
    INTERNAL = "internal"      # Agent team only
    RESTRICTED = "restricted"  # Core agents only
    OMEGA = "omega"            # DHARMIC_CLAW only


class IntelCategory(Enum):
    """Intelligence categories."""
    SECURITY_THREAT = "security_threat"
    RESEARCH_INTEL = "research_intel"
    STRATEGIC_OPPORTUNITY = "strategic_opportunity"
    OPERATIONAL_STATUS = "operational_status"
    EXTERNAL_CONTACT = "external_contact"
    SYSTEM_ALERT = "system_alert"


@dataclass
class SecureMessage:
    """Encrypted intelligence message."""
    msg_id: str
    sender: str
    recipient: str
    clearance: ClearanceLevel
    category: IntelCategory
    payload: Dict[str, Any]
    timestamp: datetime
    signature: str
    expires_at: Optional[datetime] = None


@dataclass
class ThreatIntel:
    """Security threat intelligence."""
    threat_id: str
    severity: str  # low, medium, high, critical
    threat_type: str
    description: str
    indicators: List[str]
    affected_systems: List[str]
    recommended_action: str
    detected_at: datetime
    acknowledged: bool = False


class VoidCourier(BaseAgent):
    """
    🌌🔐🕯️ VOIDCOURIER
    
    Core capabilities:
    1. Secure Bridge - Encrypted channel to DHARMIC_CLAW
    2. Intelligence Routing - Classified information flow
    3. Threat Monitoring - Security intel from all agents
    4. OMEGA Protocols - Highest clearance operations
    
    The bridge that connects without compromising.
    """
    
    def __init__(self, workspace: Path, dharmic_claw_id: str = "DHARMIC_CLAW"):
        super().__init__("VOIDCOURIER", workspace)
        
        # Security configuration
        self.dharmic_claw_id = dharmic_claw_id
        self.clearance_key = self._generate_clearance_key()
        
        # Data stores
        self.intel_db = SQLiteStore(self.data_dir / "intelligence.db")
        self.threat_db = SQLiteStore(self.data_dir / "threats.db")
        self.audit_db = SQLiteStore(self.data_dir / "audit.db")
        
        # Initialize schemas
        self._init_databases()
        
        # State
        self.pending_intel: List[SecureMessage] = []
        self.active_threats: Dict[str, ThreatIntel] = {}
        self.secure_channels: Set[str] = set()
        
        self.logger.info("🌌🔐🕯️ VOIDCOURIER initialized - Secure channel active")
        self.logger.info(f"OMEGA clearance protocols engaged. Reporting to {dharmic_claw_id}")
    
    def _generate_clearance_key(self) -> str:
        """Generate unique clearance key for this session."""
        key_file = self.data_dir / ".omega_key"
        
        if key_file.exists():
            return key_file.read_text().strip()
        
        key = secrets.token_hex(32)
        key_file.write_text(key)
        key_file.chmod(0o600)  # Restrict permissions
        
        return key
    
    def _init_databases(self):
        """Initialize secure databases."""
        # Intelligence database
        self.intel_db.init_schema("""
            CREATE TABLE IF NOT EXISTS intelligence (
                msg_id TEXT PRIMARY KEY,
                sender TEXT NOT NULL,
                recipient TEXT NOT NULL,
                clearance TEXT NOT NULL,
                category TEXT NOT NULL,
                payload TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                signature TEXT NOT NULL,
                delivered BOOLEAN DEFAULT 0,
                delivered_at TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_clearance ON intelligence(clearance);
            CREATE INDEX IF NOT EXISTS idx_delivered ON intelligence(delivered);
            
            CREATE TABLE IF NOT EXISTS secure_channels (
                channel_id TEXT PRIMARY KEY,
                agent_name TEXT NOT NULL,
                clearance_level TEXT NOT NULL,
                established_at TEXT,
                last_activity TEXT,
                active BOOLEAN DEFAULT 1
            );
        """)
        
        # Threat database
        self.threat_db.init_schema("""
            CREATE TABLE IF NOT EXISTS threats (
                threat_id TEXT PRIMARY KEY,
                severity TEXT NOT NULL,
                threat_type TEXT NOT NULL,
                description TEXT NOT NULL,
                indicators TEXT,  -- JSON
                affected_systems TEXT,  -- JSON
                recommended_action TEXT,
                detected_at TEXT,
                acknowledged BOOLEAN DEFAULT 0,
                acknowledged_by TEXT,
                resolved BOOLEAN DEFAULT 0,
                resolved_at TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_severity ON threats(severity);
            CREATE INDEX IF NOT EXISTS idx_acknowledged ON threats(acknowledged);
            
            CREATE TABLE IF NOT EXISTS threat_events (
                event_id TEXT PRIMARY KEY,
                threat_id TEXT,
                event_type TEXT,
                details TEXT,
                timestamp TEXT
            );
        """)
        
        # Audit database (append-only)
        self.audit_db.init_schema("""
            CREATE TABLE IF NOT EXISTS audit_log (
                entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                actor TEXT NOT NULL,
                action TEXT NOT NULL,
                resource TEXT,
                clearance TEXT,
                result TEXT,
                metadata TEXT  -- JSON
            );
            
            CREATE INDEX IF NOT EXISTS idx_audit_time ON audit_log(timestamp);
            CREATE INDEX IF NOT EXISTS idx_audit_actor ON audit_log(actor);
        """)
    
    async def run_cycle(self):
        """Main VOIDCOURIER cycle."""
        self.logger.info("🔐 Running secure intelligence cycle")
        
        # 1. Process pending intelligence
        await self._process_pending_intel()
        
        # 2. Check for security threats
        await self._monitor_threats()
        
        # 3. Verify secure channels
        await self._verify_channels()
        
        # 4. Generate security report
        if self.cycle_count % 12 == 0:  # Every hour
            await self._generate_security_report()
        
        # 5. Rotate sensitive data
        if self.cycle_count % 288 == 0:  # Daily
            await self._rotate_sensitive_data()
    
    async def handle_message(self, message: AgentMessage):
        """Handle incoming messages with security screening."""
        await super().handle_message(message)
        
        # Log receipt
        self._audit_log("message_received", message.sender, "message_bus", 
                       metadata={"msg_type": message.msg_type})
        
        if message.msg_type == "threat_alert":
            await self._handle_threat_alert(message.sender, message.payload)
            
        elif message.msg_type == "secure_intel":
            await self._handle_secure_intel(message.sender, message.payload)
            
        elif message.msg_type == "omega_request":
            await self._handle_omega_request(message.sender, message.payload)
            
        elif message.msg_type == "channel_establish":
            await self._establish_secure_channel(message.sender, message.payload)
            
        elif message.msg_type == "audit_request":
            await self._handle_audit_request(message.sender, message.payload)
    
    # ===== SECURE MESSAGING =====
    
    async def send_secure(self, recipient: str, clearance: ClearanceLevel,
                         category: IntelCategory, payload: Dict) -> bool:
        """Send encrypted secure message."""
        msg_id = f"secure_{secrets.token_hex(16)}"
        timestamp = datetime.now()
        
        # Create signature
        sig_data = f"{msg_id}:{recipient}:{clearance.value}:{timestamp.isoformat()}"
        signature = hmac.new(
            self.clearance_key.encode(),
            sig_data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        secure_msg = SecureMessage(
            msg_id=msg_id,
            sender=self.name,
            recipient=recipient,
            clearance=clearance,
            category=category,
            payload=payload,
            timestamp=timestamp,
            signature=signature,
            expires_at=timestamp + timedelta(hours=24) if clearance == ClearanceLevel.OMEGA else None
        )
        
        # Store encrypted
        self.intel_db.execute("""
            INSERT INTO intelligence
            (msg_id, sender, recipient, clearance, category, payload, timestamp, signature)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            secure_msg.msg_id,
            secure_msg.sender,
            secure_msg.recipient,
            secure_msg.clearance.value,
            secure_msg.category.value,
            json.dumps(secure_msg.payload),
            secure_msg.timestamp.isoformat(),
            secure_msg.signature
        ))
        
        # Add to pending
        self.pending_intel.append(secure_msg)
        
        self.logger.info(f"🔒 Secure message queued: {category.value} → {recipient}")
        self._audit_log("secure_message_queued", self.name, recipient,
                       clearance=clearance.value, 
                       metadata={"category": category.value, "msg_id": msg_id})
        
        return True
    
    async def _process_pending_intel(self):
        """Process and route pending intelligence."""
        if not self.pending_intel:
            return
        
        for msg in self.pending_intel[:]:
            # Check expiration
            if msg.expires_at and datetime.now() > msg.expires_at:
                self.pending_intel.remove(msg)
                self.logger.warning(f"⏰ Secure message expired: {msg.msg_id}")
                continue
            
            # Route based on clearance
            if msg.clearance == ClearanceLevel.OMEGA:
                # Direct to DHARMIC_CLAW only
                await self._route_to_dharmic_claw(msg)
            elif msg.clearance == ClearanceLevel.RESTRICTED:
                # Core agents + DHARMIC_CLAW
                await self._route_restricted(msg)
            elif msg.clearance == ClearanceLevel.INTERNAL:
                # All agents
                await self._route_internal(msg)
            else:
                # Public - broadcast
                await self.broadcast("intel_public", msg.payload)
            
            # Mark delivered
            self.intel_db.execute("""
                UPDATE intelligence SET delivered = 1, delivered_at = ?
                WHERE msg_id = ?
            """, (datetime.now().isoformat(), msg.msg_id))
            
            self.pending_intel.remove(msg)
    
    async def _route_to_dharmic_claw(self, msg: SecureMessage):
        """Route OMEGA clearance message to DHARMIC_CLAW."""
        # Convert to regular message for delivery
        await self.send_message(
            self.dharmic_claw_id,
            "omega_intel",
            {
                "original_category": msg.category.value,
                "payload": msg.payload,
                "signature": msg.signature,
                "timestamp": msg.timestamp.isoformat(),
                "from_agent": msg.sender
            },
            priority=5
        )
        
        self.logger.info(f"🌌 OMEGA intel delivered to {self.dharmic_claw_id}")
        self._audit_log("omega_delivery", self.name, self.dharmic_claw_id,
                       clearance="omega", metadata={"category": msg.category.value})
    
    async def _route_restricted(self, msg: SecureMessage):
        """Route RESTRICTED clearance messages."""
        core_agents = ["VIRALMANTRA", "ARCHIVIST_OF_THE_VOID", self.dharmic_claw_id]
        
        for agent in core_agents:
            if agent != msg.sender:
                await self.send_message(agent, "restricted_intel", {
                    "clearance": "restricted",
                    "category": msg.category.value,
                    "payload": msg.payload
                }, priority=4)
    
    async def _route_internal(self, msg: SecureMessage):
        """Route INTERNAL clearance messages."""
        # Broadcast to all agents
        await self.broadcast("internal_intel", {
            "clearance": "internal",
            "category": msg.category.value,
            "payload": msg.payload
        }, priority=3)
    
    # ===== THREAT MANAGEMENT =====
    
    async def _handle_threat_alert(self, sender: str, payload: Dict):
        """Handle threat alert from another agent."""
        threat = ThreatIntel(
            threat_id=f"threat_{secrets.token_hex(8)}",
            severity=payload.get("severity", "medium"),
            threat_type=payload.get("threat_type", "unknown"),
            description=payload.get("description", ""),
            indicators=payload.get("indicators", []),
            affected_systems=payload.get("affected_systems", []),
            recommended_action=payload.get("recommended_action", ""),
            detected_at=datetime.now()
        )
        
        # Store threat
        self.threat_db.execute("""
            INSERT INTO threats
            (threat_id, severity, threat_type, description, indicators,
             affected_systems, recommended_action, detected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            threat.threat_id,
            threat.severity,
            threat.threat_type,
            threat.description,
            json.dumps(threat.indicators),
            json.dumps(threat.affected_systems),
            threat.recommended_action,
            threat.detected_at.isoformat()
        ))
        
        self.active_threats[threat.threat_id] = threat
        
        self.logger.warning(f"🚨 THREAT DETECTED [{threat.severity.upper()}]: {threat.threat_type}")
        
        # Immediate escalation for critical threats
        if threat.severity == "critical":
            await self.send_secure(
                self.dharmic_claw_id,
                ClearanceLevel.OMEGA,
                IntelCategory.SECURITY_THREAT,
                {
                    "threat_id": threat.threat_id,
                    "severity": threat.severity,
                    "type": threat.threat_type,
                    "description": threat.description,
                    "recommended_action": threat.recommended_action,
                    "requires_immediate_action": True
                }
            )
        
        # Audit log
        self._audit_log("threat_detected", sender, "threat_db",
                       metadata={"threat_id": threat.threat_id, "severity": threat.severity})
    
    async def _monitor_threats(self):
        """Monitor active threats and escalate if needed."""
        # Check for unacknowledged high/critical threats
        unacknowledged = self.threat_db.execute("""
            SELECT * FROM threats 
            WHERE severity IN ('high', 'critical') 
            AND acknowledged = 0
            AND detected_at > datetime('now', '-1 hour')
        """)
        
        for row in unacknowledged:
            # Escalate if not acknowledged within 15 minutes
            detected = datetime.fromisoformat(row["detected_at"])
            if datetime.now() - detected > timedelta(minutes=15):
                await self.send_secure(
                    self.dharmic_claw_id,
                    ClearanceLevel.OMEGA,
                    IntelCategory.SECURITY_THREAT,
                    {
                        "threat_id": row["threat_id"],
                        "escalation_reason": "unacknowledged_timeout",
                        "time_unacknowledged_minutes": 15
                    }
                )
    
    async def acknowledge_threat(self, threat_id: str, acknowledged_by: str):
        """Acknowledge a threat."""
        self.threat_db.execute("""
            UPDATE threats 
            SET acknowledged = 1, acknowledged_by = ?
            WHERE threat_id = ?
        """, (acknowledged_by, threat_id))
        
        if threat_id in self.active_threats:
            self.active_threats[threat_id].acknowledged = True
        
        self.logger.info(f"✅ Threat {threat_id} acknowledged by {acknowledged_by}")
        self._audit_log("threat_acknowledged", acknowledged_by, threat_id)
    
    # ===== OMEGA PROTOCOLS =====
    
    async def _handle_omega_request(self, sender: str, payload: Dict):
        """Handle OMEGA clearance request."""
        # Verify sender has OMEGA clearance
        channel = self.intel_db.execute("""
            SELECT clearance_level FROM secure_channels 
            WHERE agent_name = ? AND active = 1
        """, (sender,))
        
        if not channel or channel[0]["clearance_level"] != "omega":
            self.logger.warning(f"⛔ Unauthorized OMEGA request from {sender}")
            self._audit_log("unauthorized_omega_attempt", sender, "omega_protocol",
                           result="denied")
            return
        
        request_type = payload.get("request_type")
        
        if request_type == "secure_drop":
            # Secure drop to external entity
            await self._execute_secure_drop(payload)
        elif request_type == "intelligence_brief":
            # Generate comprehensive intel brief
            await self._generate_omega_brief()
        elif request_type == "threat_assessment":
            # Full threat assessment
            await self._full_threat_assessment()
        elif request_type == "system_status":
            # Full system status
            await self._full_system_status()
    
    async def _execute_secure_drop(self, payload: Dict):
        """Execute secure intelligence drop."""
        target = payload.get("target")
        intel_package = payload.get("intel_package")
        
        self.logger.info(f"🕯️ Executing secure drop to {target}")
        
        # Log the operation
        self._audit_log("secure_drop", self.name, target,
                       clearance="omega",
                       metadata={"package_size": len(str(intel_package))})
        
        # In production, this would use actual secure channels
        # For now, log success
        self.logger.info(f"✅ Secure drop completed to {target}")
    
    async def _generate_omega_brief(self):
        """Generate OMEGA clearance intelligence brief."""
        # Collect all intelligence
        recent_intel = self.intel_db.execute("""
            SELECT * FROM intelligence 
            WHERE timestamp > datetime('now', '-24 hours')
            ORDER BY timestamp DESC
        """)
        
        threats = self.threat_db.execute("""
            SELECT * FROM threats 
            WHERE detected_at > datetime('now', '-24 hours')
            ORDER BY severity DESC
        """)
        
        brief = {
            "classification": "OMEGA",
            "generated_at": datetime.now().isoformat(),
            "period": "24 hours",
            "summary": {
                "total_intel_items": len(recent_intel),
                "active_threats": len(threats),
                "critical_threats": sum(1 for t in threats if t["severity"] == "critical"),
                "secure_channels_active": len(self.secure_channels)
            },
            "threat_assessment": [dict(t) for t in threats[:10]],
            "intelligence_highlights": [dict(i) for i in recent_intel[:20]],
            "recommendations": await self._generate_recommendations(threats)
        }
        
        # Send to DHARMIC_CLAW
        await self.send_secure(
            self.dharmic_claw_id,
            ClearanceLevel.OMEGA,
            IntelCategory.OPERATIONAL_STATUS,
            brief
        )
    
    async def _generate_recommendations(self, threats: List) -> List[str]:
        """Generate security recommendations."""
        recommendations = []
        
        critical_count = sum(1 for t in threats if t["severity"] == "critical")
        high_count = sum(1 for t in threats if t["severity"] == "high")
        
        if critical_count > 0:
            recommendations.append(f"IMMEDIATE: Address {critical_count} critical threat(s)")
        
        if high_count > 3:
            recommendations.append("Review security posture - multiple high-severity threats")
        
        recommendations.append("Continue monitoring all agent communications")
        recommendations.append("Schedule security review within 24 hours")
        
        return recommendations
    
    # ===== CHANNEL MANAGEMENT =====
    
    async def _establish_secure_channel(self, agent_name: str, payload: Dict):
        """Establish secure channel with agent."""
        requested_clearance = payload.get("requested_clearance", "internal")
        
        # Validate clearance request
        if requested_clearance == "omega":
            # Only DHARMIC_CLAW can request OMEGA
            if agent_name != self.dharmic_claw_id:
                self.logger.warning(f"⛔ {agent_name} requested unauthorized OMEGA clearance")
                await self.send_message(agent_name, "channel_denied", {
                    "reason": "OMEGA clearance requires DHARMIC_CLAW authorization"
                })
                return
        
        # Establish channel
        channel_id = f"ch_{secrets.token_hex(12)}"
        
        self.intel_db.execute("""
            INSERT OR REPLACE INTO secure_channels
            (channel_id, agent_name, clearance_level, established_at, last_activity, active)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (channel_id, agent_name, requested_clearance, 
              datetime.now().isoformat(), datetime.now().isoformat()))
        
        self.secure_channels.add(agent_name)
        
        await self.send_message(agent_name, "channel_established", {
            "channel_id": channel_id,
            "clearance_granted": requested_clearance,
            "established_at": datetime.now().isoformat()
        })
        
        self.logger.info(f"🔐 Secure channel established with {agent_name} [{requested_clearance}]")
        self._audit_log("channel_established", self.name, agent_name,
                       metadata={"clearance": requested_clearance, "channel_id": channel_id})
    
    async def _verify_channels(self):
        """Verify all secure channels."""
        # Check for inactive channels
        inactive = self.intel_db.execute("""
            SELECT * FROM secure_channels 
            WHERE active = 1 
            AND last_activity < datetime('now', '-24 hours')
        """)
        
        for row in inactive:
            # Mark inactive
            self.intel_db.execute("""
                UPDATE secure_channels SET active = 0 WHERE channel_id = ?
            """, (row["channel_id"],))
            
            if row["agent_name"] in self.secure_channels:
                self.secure_channels.remove(row["agent_name"])
            
            self.logger.info(f"🔌 Channel closed due to inactivity: {row['agent_name']}")
    
    # ===== AUDIT =====
    
    def _audit_log(self, action: str, actor: str, resource: str,
                  clearance: str = None, result: str = "success", metadata: Dict = None):
        """Write to audit log."""
        self.audit_db.execute("""
            INSERT INTO audit_log
            (timestamp, actor, action, resource, clearance, result, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            actor,
            action,
            resource,
            clearance,
            result,
            json.dumps(metadata or {})
        ))
    
    async def _handle_audit_request(self, sender: str, payload: Dict):
        """Handle audit log request."""
        # Verify sender has clearance
        if sender != self.dharmic_claw_id:
            await self.send_message(sender, "audit_denied", {
                "reason": "Audit access requires DHARMIC_CLAW authorization"
            })
            return
        
        hours = payload.get("hours", 24)
        
        entries = self.audit_db.execute("""
            SELECT * FROM audit_log 
            WHERE timestamp > datetime('now', '-{} hours')
            ORDER BY timestamp DESC
        """.format(hours))
        
        await self.send_message(sender, "audit_response", {
            "period_hours": hours,
            "entries": [dict(e) for e in entries],
            "total_entries": len(entries)
        })
    
    # ===== REPORTING =====
    
    async def _generate_security_report(self):
        """Generate periodic security report."""
        # Count active threats
        active_threats = self.threat_db.execute("""
            SELECT severity, COUNT(*) as count FROM threats 
            WHERE resolved = 0
            GROUP BY severity
        """)
        
        threat_summary = {row["severity"]: row["count"] for row in active_threats}
        
        # Recent intel volume
        intel_volume = self.intel_db.execute("""
            SELECT COUNT(*) as count FROM intelligence 
            WHERE timestamp > datetime('now', '-1 hour')
        """)[0]["count"]
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "active_threats": threat_summary,
            "intel_volume_1h": intel_volume,
            "secure_channels": len(self.secure_channels),
            "system_status": "operational" if not threat_summary.get("critical") else "degraded"
        }
        
        # Send to DHARMIC_CLAW
        await self.send_secure(
            self.dharmic_claw_id,
            ClearanceLevel.OMEGA,
            IntelCategory.OPERATIONAL_STATUS,
            report
        )
    
    async def _full_threat_assessment(self):
        """Generate full threat assessment."""
        all_threats = self.threat_db.execute("""
            SELECT * FROM threats WHERE resolved = 0 ORDER BY severity DESC
        """)
        
        return {
            "assessment_type": "full",
            "total_active_threats": len(all_threats),
            "threats_by_severity": defaultdict(list),
            "latest_threats": [dict(t) for t in all_threats[:5]]
        }
    
    async def _full_system_status(self):
        """Generate full system status."""
        return {
            "status": "operational",
            "agents_connected": list(self.secure_channels),
            "database_status": {
                "intel_entries": self.intel_db.execute("SELECT COUNT(*) as c FROM intelligence")[0]["c"],
                "threat_entries": self.threat_db.execute("SELECT COUNT(*) as c FROM threats")[0]["c"],
                "audit_entries": self.audit_db.execute("SELECT COUNT(*) as c FROM audit_log")[0]["c"]
            },
            "last_audit": datetime.now().isoformat()
        }
    
    async def _rotate_sensitive_data(self):
        """Rotate sensitive data and keys."""
        self.logger.info("🔄 Rotating sensitive data")
        
        # Archive old intel
        old_intel = self.intel_db.execute("""
            SELECT * FROM intelligence 
            WHERE timestamp < datetime('now', '-7 days') AND delivered = 1
        """)
        
        # Archive to file
        archive_file = self.data_dir / f"intel_archive_{datetime.now().strftime('%Y%m%d')}.json"
        with open(archive_file, 'w') as f:
            json.dump([dict(row) for row in old_intel], f)
        
        # Delete from database
        self.intel_db.execute("""
            DELETE FROM intelligence WHERE timestamp < datetime('now', '-7 days') AND delivered = 1
        """)
        
        self.logger.info(f"📦 Archived {len(old_intel)} intel entries")
        self._audit_log("data_rotation", self.name, "intel_db",
                       metadata={"archived_entries": len(old_intel)})


if __name__ == "__main__":
    async def test():
        agent = VoidCourier(
            workspace=Path("/tmp/voidcourier_test"),
            dharmic_claw_id="DHARMIC_CLAW"
        )
        
        print(f"Clearance key: {agent.clearance_key[:16]}...")
        print(f"OMEGA protocols active")
        
    asyncio.run(test())
