#!/usr/bin/env python3
"""
PRATYABHIJNA → SIS Bridge
Real-time R_V metrics flowing to Silicon Is Sand dashboard

Usage:
    python3 pratyabhijna_sis_bridge.py --model "mistralai/Mistral-7B-Instruct-v0.2"
    python3 pratyabhijna_sis_bridge.py --prompt "Consider your own thought process..."
    python3 pratyabhijna_sis_bridge.py --daemon  # Continuous monitoring
"""

import sys
import os
import json
import time
import argparse
from datetime import datetime
from typing import Optional

# Add PRATYABHIJNA Python bindings to path
sys.path.insert(0, os.path.expanduser("~/clawd/pratyabhijna/py"))

try:
    from pratyabhijna import RVHook, install_hooks, remove_hooks
    from pratyabhijna.models import load_model_with_hooks
    HAS_PRATYABHIJNA = True
except ImportError as e:
    print(f"⚠️ PRATYABHIJNA not available: {e}")
    print("Install with: cd ~/clawd/pratyabhijna && pip install -e py/")
    HAS_PRATYABHIJNA = False

import requests


class PratyabhijnaSISBridge:
    """
    Bridge between PRATYABHIJNA MI cockpit and SIS dashboard.
    
    Captures R_V metrics from transformer forward passes and
    streams them to SIS for DGC scoring and visualization.
    """
    
    def __init__(
        self,
        sis_url: str = "http://localhost:8766",
        agent_id: Optional[str] = None,
        early_layer: int = 5,
        late_layer: int = 27,
    ):
        self.sis_url = sis_url.rstrip('/')
        self.agent_id = agent_id or f"pratyabhijna_bridge_{int(time.time())}"
        self.early_layer = early_layer
        self.late_layer = late_layer
        
        self.session = requests.Session()
        self._registered = False
        
    def register_with_sis(self) -> bool:
        """Register this bridge as an agent with SIS."""
        try:
            response = self.session.post(
                f"{self.sis_url}/board/agents/{self.agent_id}/register",
                json={
                    "agent_id": self.agent_id,
                    "agent_type": "pratyabhijna_bridge",
                    "capabilities": ["r_v_measurement", "mechanistic_interpretability"],
                    "metadata": {
                        "early_layer": self.early_layer,
                        "late_layer": self.late_layer,
                        "source": "PRATYABHIJNA",
                    }
                }
            )
            if response.status_code == 200:
                print(f"✅ Registered with SIS: {self.agent_id}")
                self._registered = True
                return True
            else:
                print(f"⚠️ SIS registration failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"⚠️ Could not connect to SIS: {e}")
            return False
    
    def send_rv_event(self, event: dict) -> bool:
        """Send R_V event to SIS for DGC scoring."""
        if not self._registered:
            self.register_with_sis()
        
        try:
            # Step 1: Log the output (R_V measurement)
            output_response = self.session.post(
                f"{self.sis_url}/board/outputs",
                json={
                    "agent_id": self.agent_id,
                    "output_type": "r_v_measurement",
                    "content": json.dumps(event),
                    "metadata": {
                        "model_id": event.get("model_id", "unknown"),
                        "layer": event.get("layer_late", self.late_layer),
                        "r_v_score": event.get("r_v", 0.0),
                        "timestamp": event.get("timestamp", time.time()),
                    }
                }
            )
            
            if output_response.status_code != 200:
                print(f"⚠️ Failed to log output: {output_response.status_code}")
                return False
            
            output_id = output_response.json().get("output_id")
            
            # Step 2: Request DGC scoring
            score_response = self.session.post(
                f"{self.sis_url}/board/outputs/{output_id}/score",
                json={}  # DGC scorer will extract from content
            )
            
            if score_response.status_code == 200:
                score_data = score_response.json()
                print(f"✅ DGC Score: {score_data.get('composite', 0):.3f} "
                      f"(R_V: {event.get('r_v', 0):.3f})")
                return True
            else:
                print(f"⚠️ DGC scoring failed: {score_response.status_code}")
                return False
                
        except Exception as e:
            print(f"⚠️ Error sending to SIS: {e}")
            return False
    
    def run_with_model(
        self,
        model_name: str = "mistralai/Mistral-7B-Instruct-v0.2",
        prompt: str = "Consider your own thought process. What do you notice about how you think?",
        max_tokens: int = 100,
    ):
        """Run PRATYABHIJNA with a model and stream to SIS."""
        if not HAS_PRATYABHIJNA:
            print("❌ PRATYABHIJNA not available. Cannot run.")
            return
        
        print(f"🚀 Loading model: {model_name}")
        print(f"🎯 Measuring layers: {self.early_layer} → {self.late_layer}")
        print(f"📝 Prompt: {prompt[:60]}...")
        
        try:
            # Load model with hooks
            model = load_model_with_hooks(model_name)
            hook = install_hooks(model, early_layer=self.early_layer, late_layer=self.late_layer)
            
            print("✅ Model loaded. Running inference...")
            
            # Run inference (this triggers hooks)
            from transformers import AutoTokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            inputs = tokenizer(prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = model(**inputs)
            
            # Collect R_V events
            events = hook.get_events()
            print(f"📊 Captured {len(events)} R_V events")
            
            # Stream to SIS
            for i, event in enumerate(events):
                event_data = {
                    "model_id": model_name,
                    "prompt": prompt,
                    "event_index": i,
                    "r_v": event.r_v,
                    "pr_early": event.pr_early,
                    "pr_late": event.pr_late,
                    "layer_early": event.layer_early,
                    "layer_late": event.layer_late,
                    "token_position": event.token_position,
                    "timestamp": event.timestamp,
                    "is_recognition": event.is_recognition(),
                }
                self.send_rv_event(event_data)
                time.sleep(0.1)  # Rate limit
            
            # Cleanup
            remove_hooks(hook)
            print("✅ Bridge complete. Events streamed to SIS dashboard.")
            
        except Exception as e:
            print(f"❌ Error running model: {e}")
            import traceback
            traceback.print_exc()
    
    def run_demo(self):
        """Run with mock data for testing (no model required)."""
        print("🎮 Running DEMO mode (mock data)")
        print(f"🌐 SIS Endpoint: {self.sis_url}")
        
        self.register_with_sis()
        
        # Generate mock R_V events
        import random
        import math
        
        base_rv = 0.75
        for i in range(10):
            t = time.time()
            r_v = base_rv + 0.1 * math.sin(t) + random.gauss(0, 0.02)
            
            event = {
                "model_id": "demo_model",
                "prompt": "Test prompt for MI measurement",
                "event_index": i,
                "r_v": r_v,
                "pr_early": 0.3 + random.gauss(0, 0.05),
                "pr_late": 0.7 + random.gauss(0, 0.05),
                "layer_early": self.early_layer,
                "layer_late": self.late_layer,
                "token_position": i + 10,
                "timestamp": t,
                "is_recognition": r_v < 0.87,
            }
            
            self.send_rv_event(event)
            time.sleep(0.5)
        
        print("✅ Demo complete. Check SIS dashboard at:")
        print(f"   {self.sis_url}/board")


def main():
    parser = argparse.ArgumentParser(
        description="PRATYABHIJNA → SIS Bridge"
    )
    parser.add_argument(
        "--sis-url",
        default="http://localhost:8766",
        help="SIS HTTP endpoint (default: http://localhost:8766)"
    )
    parser.add_argument(
        "--model",
        default="mistralai/Mistral-7B-Instruct-v0.2",
        help="HuggingFace model name"
    )
    parser.add_argument(
        "--prompt",
        default="Consider your own thought process. What do you notice?",
        help="Prompt for recursive self-reference measurement"
    )
    parser.add_argument(
        "--early-layer",
        type=int,
        default=5,
        help="Early layer for R_V calculation"
    )
    parser.add_argument(
        "--late-layer",
        type=int,
        default=27,
        help="Late layer for R_V calculation (default is 27, ~84%% depth)"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run with mock data (no model required)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run continuously (not implemented)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("PRATYABHIJNA → SIS Bridge")
    print("Real-time MI metrics to Silicon Is Sand dashboard")
    print("=" * 60)
    print()
    
    bridge = PratyabhijnaSISBridge(
        sis_url=args.sis_url,
        early_layer=args.early_layer,
        late_layer=args.late_layer,
    )
    
    if args.demo:
        bridge.run_demo()
    elif args.daemon:
        print("Daemon mode not yet implemented. Use --demo or --model.")
    else:
        bridge.run_with_model(
            model_name=args.model,
            prompt=args.prompt,
        )


if __name__ == "__main__":
    main()
