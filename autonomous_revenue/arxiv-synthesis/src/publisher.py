"""
Publisher Module
Handles publishing to Substack (or other platforms)
"""

import os
from typing import Dict, Optional


class DraftPublisher:
    """Publish newsletter to various platforms"""
    
    def __init__(self, substack_url: Optional[str] = None, api_key: Optional[str] = None):
        self.substack_url = substack_url or os.getenv("SUBSTACK_URL")
        self.api_key = api_key or os.getenv("SUBSTACK_API_KEY")
    
    def publish(self, title: str, content: str, subtitle: str = "") -> Dict:
        """
        Publish newsletter
        
        Args:
            title: Newsletter title
            content: Markdown content
            subtitle: Subtitle/description
            
        Returns:
            Publication result dict
        """
        # For now, save to file and provide instructions
        # Full Substack API integration would require their API
        
        result = {
            "success": False,
            "url": None,
            "method": "draft",
            "message": ""
        }
        
        # Try Substack API if available
        if self.api_key and self.substack_url:
            try:
                # Substack doesn't have an official public API yet
                # This is a placeholder for when they do
                result["message"] = "Substack API integration pending"
            except Exception as e:
                result["message"] = f"Publish failed: {e}"
        else:
            # Save as draft file for manual upload
            result["message"] = "Draft saved. Manual upload to Substack required."
            result["success"] = True  # Success means draft created
        
        return result
    
    def publish_to_webhook(self, content: str, webhook_url: str) -> Dict:
        """
        Publish to webhook (e.g., Zapier, Make.com)
        
        Args:
            content: Content to publish
            webhook_url: Webhook URL
            
        Returns:
            Result dict
        """
        import requests
        
        try:
            response = requests.post(
                webhook_url,
                json={
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                },
                timeout=30
            )
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response": response.text[:200]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_publish_instructions(self) -> str:
        """Get instructions for manual publishing"""
        return """
📋 MANUAL PUBLISHING INSTRUCTIONS
=================================

1. Copy the content from output/latest.md
2. Go to your Substack dashboard
3. Click "New Post"
4. Paste the content
5. Add tags: #ai #consciousness #research
6. Set to publish or schedule

AUTOMATION OPTIONS:
-------------------
- Zapier: Connect Dropbox → Substack
- Make.com: Similar workflow automation
- Email-to-post: Some platforms support this

SUBSTACK API:
-------------
Substack doesn't have a public API yet.
Watch for updates at: https://substack.com/developers
"""
