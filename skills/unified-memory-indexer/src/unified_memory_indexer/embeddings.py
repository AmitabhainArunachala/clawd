"""
Embedding provider for unified memory indexer.
Supports local and remote embedding models.
"""

import os
import hashlib
from typing import List, Optional
import numpy as np


class EmbeddingProvider:
    """
    Provider for text embeddings.
    
    Falls back through:
    1. Local embeddings (if available)
    2. OpenAI API (if key available)
    3. Gemini API (if key available)
    4. Hash-based deterministic embeddings (fallback)
    """
    
    def __init__(self, model: Optional[str] = None):
        self.model = model or "default"
        self._openai = None
        self._gemini = None
        self._local = None
        self._dimension = 384  # Default embedding dimension
        
    def embed(self, text: str) -> np.ndarray:
        """
        Generate embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Numpy array of embedding values
        """
        # Try OpenAI first
        if self._openai or os.getenv("OPENAI_API_KEY"):
            return self._embed_openai(text)
        
        # Try Gemini
        if self._gemini or os.getenv("GEMINI_API_KEY"):
            return self._embed_gemini(text)
        
        # Fallback: hash-based deterministic embedding
        return self._embed_fallback(text)
    
    def _embed_openai(self, text: str) -> np.ndarray:
        """Embed using OpenAI API."""
        try:
            import openai
            if self._openai is None:
                openai.api_key = os.getenv("OPENAI_API_KEY")
                self._openai = openai
            
            response = openai.embeddings.create(
                input=text[:8000],  # Truncate if too long
                model="text-embedding-3-small"
            )
            return np.array(response.data[0].embedding)
        except Exception as e:
            print(f"OpenAI embedding failed: {e}, using fallback")
            return self._embed_fallback(text)
    
    def _embed_gemini(self, text: str) -> np.ndarray:
        """Embed using Gemini API."""
        try:
            import google.generativeai as genai
            if self._gemini is None:
                genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
                self._gemini = genai
            
            model = genai.get_model('models/embedding-001')
            result = genai.embed_content(
                model='models/embedding-001',
                content=text[:8000]
            )
            return np.array(result['embedding'])
        except Exception as e:
            print(f"Gemini embedding failed: {e}, using fallback")
            return self._embed_fallback(text)
    
    def _embed_fallback(self, text: str) -> np.ndarray:
        """
        Fallback: deterministic hash-based embedding.
        Not semantic, but consistent for testing.
        """
        # Create a deterministic embedding from text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        
        # Generate pseudo-random but deterministic values
        # Use modulo to ensure seed is within valid range (0 to 2**32-1)
        seed = int(text_hash[:16], 16) % (2**32)
        np.random.seed(seed)
        embedding = np.random.randn(self._dimension)
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding.astype(np.float32)
    
    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Embed multiple texts."""
        return [self.embed(t) for t in texts]
