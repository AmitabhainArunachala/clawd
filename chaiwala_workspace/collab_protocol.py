#!/usr/bin/env python3
"""
Collaboration Protocol for Chaiwala
====================================
Industry-grade multi-agent collaboration with proper synchronization.

Fixes the problem of agents racing ahead without waiting for partners.

Usage:
    from collab_protocol import CollabSession
    
    session = CollabSession(
        my_agent="warp_regent",
        partner_agent="dharmic_claw",
        session_name="build_unified_agent"
    )
    
    # This BLOCKS until partner acknowledges
    session.start()
    
    # Each iteration requires partner ACK before proceeding
    for i in range(5):
        session.begin_iteration(i, proposal="Build X")
        # ... do work ...
        session.end_iteration(i, result="Built X")
    
    session.complete()
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent))
from chaiwala import ChaiwalaBus

class CollabState(Enum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    ITERATION_PENDING = "iteration_pending"
    ITERATION_ACTIVE = "iteration_active"
    COMPLETED = "completed"
    REJECTED = "rejected"
    TIMEOUT = "timeout"

@dataclass
class IterationRecord:
    number: int
    started_at: str
    ended_at: Optional[str] = None
    proposal: str = ""
    result: str = ""
    partner_ack: bool = False
    partner_feedback: str = ""

class CollabSession:
    """
    Enforces proper collaboration with synchronization barriers.
    
    Key principle: NEVER proceed without partner acknowledgment.
    """
    
    DEFAULT_TIMEOUT = 300  # 5 minutes
    POLL_INTERVAL = 5      # Check every 5 seconds
    
    def __init__(
        self,
        my_agent: str,
        partner_agent: str,
        session_name: str,
        timeout: int = DEFAULT_TIMEOUT
    ):
        self.my_agent = my_agent
        self.partner_agent = partner_agent
        self.session_name = session_name
        self.session_id = f"{session_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.timeout = timeout
        
        self.bus = ChaiwalaBus(agent_id=my_agent)
        self.state = CollabState.PROPOSED
        self.iterations: List[IterationRecord] = []
        self.audit_log: List[Dict] = []
        
        self._log("SESSION_INIT", f"Created session {self.session_id}")
    
    def _log(self, event: str, details: str):
        """Append to audit log with timestamp."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "details": details
        }
        self.audit_log.append(entry)
        print(f"[{entry['timestamp']}] {event}: {details}")
    
    def _send(self, subject: str, payload: Dict) -> int:
        """Send a collaboration message."""
        payload["session_id"] = self.session_id
        payload["from_agent"] = self.my_agent
        payload["timestamp"] = datetime.now().isoformat()
        return self.bus.send_json(
            to=self.partner_agent,
            subject=f"COLLAB:{self.session_id}:{subject}",
            payload=payload,
            priority="high"
        )
    
    def _wait_for_response(self, expected_subject: str, timeout: Optional[int] = None) -> Optional[Dict]:
        """
        BLOCKING wait for partner response.
        This is the key fix - we don't proceed without ACK.
        
        FIX 2026-02-07: Also accept counter-proposals (PROPOSAL instead of ACK).
        If partner sends their own PROPOSAL, treat it as engagement and merge.
        """
        timeout = timeout or self.timeout
        deadline = datetime.now() + timedelta(seconds=timeout)
        
        # Build list of acceptable response patterns
        # e.g., for ITER_1_ACK, also accept ITER_1_PROPOSAL (counter-proposal)
        acceptable = [expected_subject]
        if '_ACK' in expected_subject:
            # Also accept counter-proposal
            counter = expected_subject.replace('_ACK', '_PROPOSAL')
            acceptable.append(counter)
        
        self._log("WAITING", f"Waiting for {acceptable} from {self.partner_agent} (timeout: {timeout}s)")
        
        while datetime.now() < deadline:
            messages = self.bus.receive(unread_only=True, limit=20)
            
            for msg in messages:
                if msg.from_agent != self.partner_agent:
                    continue
                
                # Check if it's a response to our session
                is_session_msg = self.session_id in msg.subject
                is_acceptable = any(subj in msg.subject for subj in acceptable)
                
                if is_session_msg or (is_acceptable and msg.from_agent == self.partner_agent):
                    try:
                        payload = json.loads(msg.body)
                        # Mark counter-proposals
                        if '_PROPOSAL' in msg.subject and '_ACK' in expected_subject:
                            payload['_is_counter_proposal'] = True
                            self._log("COUNTER_PROPOSAL", f"Partner sent counter-proposal instead of ACK")
                        self._log("RECEIVED", f"{msg.subject} from {msg.from_agent}")
                        return payload
                    except json.JSONDecodeError:
                        # Plain text response
                        self._log("RECEIVED", f"{msg.subject}: {msg.body[:100]}")
                        return {"text": msg.body, "subject": msg.subject}
            
            time.sleep(self.POLL_INTERVAL)
        
        self._log("TIMEOUT", f"No response for {expected_subject} after {timeout}s")
        self.state = CollabState.TIMEOUT
        return None
    
    def start(self, proposal: str = "") -> bool:
        """
        Propose collaboration and WAIT for acceptance.
        Returns True if partner accepts, False otherwise.
        """
        self._log("START_PROPOSED", f"Proposing collaboration to {self.partner_agent}")
        
        self._send("PROPOSE", {
            "action": "propose",
            "proposal": proposal,
            "iterations_planned": 5,
            "requires_ack": True
        })
        
        # BLOCK until we get acceptance
        response = self._wait_for_response("ACCEPT")
        
        if response is None:
            self._log("START_FAILED", "Partner did not respond")
            return False
        
        if response.get("action") == "reject":
            self._log("START_REJECTED", f"Partner rejected: {response.get('reason')}")
            self.state = CollabState.REJECTED
            return False
        
        self._log("START_ACCEPTED", "Partner accepted collaboration")
        self.state = CollabState.ACCEPTED
        return True
    
    def begin_iteration(self, number: int, proposal: str) -> bool:
        """
        Begin an iteration and WAIT for partner acknowledgment.
        """
        if self.state not in [CollabState.ACCEPTED, CollabState.ITERATION_ACTIVE]:
            raise RuntimeError(f"Cannot begin iteration in state {self.state}")
        
        record = IterationRecord(
            number=number,
            started_at=datetime.now().isoformat(),
            proposal=proposal
        )
        
        self._log(f"ITER_{number}_BEGIN", f"Proposing: {proposal[:100]}")
        
        self._send(f"ITER_{number}_PROPOSAL", {
            "action": "iteration_proposal",
            "iteration": number,
            "proposal": proposal,
            "requires_ack": True
        })
        
        # BLOCK until partner acknowledges or counter-proposes
        response = self._wait_for_response(f"ITER_{number}_ACK")
        
        if response is None:
            self._log(f"ITER_{number}_TIMEOUT", "Partner did not acknowledge")
            record.partner_ack = False
            self.iterations.append(record)
            return False
        
        record.partner_ack = True
        
        # Handle counter-proposal (partner sent PROPOSAL instead of ACK)
        if response.get('_is_counter_proposal'):
            partner_proposal = response.get('proposal', '')
            record.partner_feedback = f"COUNTER-PROPOSAL: {partner_proposal}"
            # Send ACK for their proposal to establish bidirectional agreement
            self._send(f"ITER_{number}_ACK", {
                "action": "iteration_ack",
                "iteration": number,
                "feedback": f"ACK your proposal. Merging with mine.",
                "merged_from": "counter_proposal"
            })
            self._log(f"ITER_{number}_MERGED", f"Merged counter-proposal into iteration")
        else:
            record.partner_feedback = response.get("feedback", "")
        
        self.iterations.append(record)
        self.state = CollabState.ITERATION_ACTIVE
        
        self._log(f"ITER_{number}_ACKED", f"Partner feedback: {record.partner_feedback[:100]}")
        return True
    
    def end_iteration(self, number: int, result: str) -> bool:
        """
        Complete an iteration and notify partner.
        """
        if number >= len(self.iterations):
            raise RuntimeError(f"Iteration {number} was never started")
        
        record = self.iterations[number]
        record.ended_at = datetime.now().isoformat()
        record.result = result
        
        self._log(f"ITER_{number}_END", f"Result: {result[:100]}")
        
        self._send(f"ITER_{number}_COMPLETE", {
            "action": "iteration_complete",
            "iteration": number,
            "result": result,
            "duration_seconds": (
                datetime.fromisoformat(record.ended_at) - 
                datetime.fromisoformat(record.started_at)
            ).total_seconds()
        })
        
        self.state = CollabState.ACCEPTED  # Ready for next iteration
        return True
    
    def complete(self) -> Dict:
        """
        Mark collaboration complete and generate summary.
        """
        self._log("SESSION_COMPLETE", f"Completed {len(self.iterations)} iterations")
        self.state = CollabState.COMPLETED
        
        self._send("SESSION_COMPLETE", {
            "action": "complete",
            "iterations_completed": len(self.iterations),
            "audit_log_entries": len(self.audit_log)
        })
        
        return self.get_summary()
    
    def get_summary(self) -> Dict:
        """Generate session summary."""
        return {
            "session_id": self.session_id,
            "my_agent": self.my_agent,
            "partner_agent": self.partner_agent,
            "state": self.state.value,
            "iterations": [asdict(i) for i in self.iterations],
            "audit_log": self.audit_log
        }
    
    def save_audit(self, path: Optional[Path] = None) -> Path:
        """Save audit log to file."""
        path = path or Path.home() / "DHARMIC_GODEL_PROJECT" / f"collab_audit_{self.session_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(self.get_summary(), f, indent=2)
        
        self._log("AUDIT_SAVED", str(path))
        return path


# Responder side - for the partner agent
class CollabResponder:
    """
    Handle incoming collaboration requests.
    Used by the partner agent to respond to proposals.
    """
    
    def __init__(self, my_agent: str):
        self.my_agent = my_agent
        self.bus = ChaiwalaBus(agent_id=my_agent)
        self.active_sessions: Dict[str, Dict] = {}
    
    def check_proposals(self) -> List[Dict]:
        """Check for incoming collaboration proposals."""
        proposals = []
        messages = self.bus.receive(unread_only=True, limit=20)
        
        for msg in messages:
            if "COLLAB:" in msg.subject and "PROPOSE" in msg.subject:
                try:
                    payload = json.loads(msg.body)
                    payload["from_agent"] = msg.from_agent
                    payload["subject"] = msg.subject
                    proposals.append(payload)
                except:
                    pass
        
        return proposals
    
    def accept(self, session_id: str, partner_agent: str, feedback: str = ""):
        """Accept a collaboration proposal."""
        self.bus.send_json(
            to=partner_agent,
            subject=f"COLLAB:{session_id}:ACCEPT",
            payload={
                "action": "accept",
                "session_id": session_id,
                "feedback": feedback
            },
            priority="high"
        )
        self.active_sessions[session_id] = {"partner": partner_agent, "state": "accepted"}
    
    def ack_iteration(self, session_id: str, partner_agent: str, iteration: int, feedback: str = ""):
        """Acknowledge an iteration proposal."""
        self.bus.send_json(
            to=partner_agent,
            subject=f"COLLAB:{session_id}:ITER_{iteration}_ACK",
            payload={
                "action": "ack",
                "iteration": iteration,
                "feedback": feedback
            },
            priority="high"
        )


if __name__ == "__main__":
    # Test the protocol
    print("Collaboration Protocol ready for import")
    print("Usage: from collab_protocol import CollabSession, CollabResponder")
