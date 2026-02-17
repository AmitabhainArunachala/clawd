"""
Silicon is Sand — HTTP Delivery to Agents
Actual POST delivery (not stubbed)
"""

import requests
import time
from typing import Dict, Optional
from datetime import datetime

AGENT_ENDPOINTS = {
    # Hardcoded for v0.2 — v0.3 will auto-discover
    "agni_opus46_20260216": "http://157.245.193.15:8080/activate",
    "codex_53_20260216": "http://localhost:8081/activate",
    "dharmic_clawd_kimi_20260216": "http://localhost:8082/activate",
    "rushabdev_20260216": "http://167.172.95.184:8083/activate"
}

class AgentDelivery:
    def __init__(self, timeout=30, max_retries=3):
        self.timeout = timeout
        self.max_retries = max_retries
    
    def deliver_prompt(self, agent_id: str, prompt: str, context: dict) -> dict:
        """Deliver re-prompt to agent via HTTP POST"""
        endpoint = AGENT_ENDPOINTS.get(agent_id)
        if not endpoint:
            return {
                "delivered": False,
                "error": f"No endpoint configured for {agent_id}",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        payload = {
            "agent_id": agent_id,
            "prompt": prompt,
            "context": context,
            "timestamp": datetime.utcnow().isoformat(),
            "urgency": "high"  # Overnight build urgency
        }
        
        for attempt in range(self.max_retries):
            try:
                resp = requests.post(
                    endpoint,
                    json=payload,
                    timeout=self.timeout,
                    headers={"Content-Type": "application/json"}
                )
                if resp.status_code == 200:
                    return {
                        "delivered": True,
                        "agent_id": agent_id,
                        "endpoint": endpoint,
                        "response_code": resp.status_code,
                        "timestamp": datetime.utcnow().isoformat(),
                        "attempt": attempt + 1
                    }
                else:
                    # Non-200, retry
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
            except requests.RequestException as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return {
                        "delivered": False,
                        "agent_id": agent_id,
                        "endpoint": endpoint,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat(),
                        "attempts": self.max_retries
                    }
        
        return {
            "delivered": False,
            "agent_id": agent_id,
            "error": "Max retries exceeded",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def ping_agent(self, agent_id: str) -> bool:
        """Quick health check if agent is reachable"""
        endpoint = AGENT_ENDPOINTS.get(agent_id, "").replace("/activate", "/health")
        if not endpoint:
            return False
        try:
            resp = requests.get(endpoint, timeout=5)
            return resp.status_code == 200
        except:
            return False

# Singleton
delivery = AgentDelivery()
