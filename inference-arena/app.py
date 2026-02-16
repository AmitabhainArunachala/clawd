"""
Inference Arena - Minimal Viable Product
A Streamlit dashboard for comparing AI model outputs side-by-side.

Day 1-2 MVP: 6 hero models, simple voting, no auth
"""

import streamlit as st
import json
import os
from datetime import datetime
from typing import List, Dict
import urllib.request

# Page config
st.set_page_config(
    page_title="Inference Arena",
    page_icon="🥊",
    layout="wide"
)

# Initialize session state
if 'votes' not in st.session_state:
    st.session_state.votes = {}
if 'history' not in st.session_state:
    st.session_state.history = []

# Hero models (6 for MVP)
HERO_MODELS = [
    {"name": "gemma3:4b", "provider": "ollama", "display": "Gemma 3 (4B)"},
    {"name": "llama3.1:8b", "provider": "ollama", "display": "Llama 3.1 (8B)"},
    {"name": "mistral:latest", "provider": "ollama", "display": "Mistral (7B)"},
    {"name": "qwen2.5:7b", "provider": "ollama", "display": "Qwen 2.5 (7B)"},
    {"name": "yi:34b", "provider": "ollama", "display": "Yi (34B)"},
    {"name": "nemotron-3-nano:30b-cloud", "provider": "ollama", "display": "Nemotron 3 (30B)"},
]

def query_ollama(model: str, prompt: str, timeout: int = 60) -> str:
    """Query Ollama API."""
    try:
        payload = json.dumps({
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 150}
        }).encode()
        
        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read())
            return result.get("response", "Error: No response")
    except Exception as e:
        return f"Error: {str(e)}"

def run_comparison(prompt: str, models: List[Dict]) -> Dict:
    """Run prompt through all selected models."""
    results = {}
    progress = st.progress(0)
    
    for i, model in enumerate(models):
        with st.spinner(f"Querying {model['display']}..."):
            response = query_ollama(model['name'], prompt)
            results[model['name']] = {
                "display": model['display'],
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
        progress.progress((i + 1) / len(models))
    
    progress.empty()
    return results

# Header
st.title("🥊 Inference Arena")
st.markdown("*Compare AI models side-by-side. You decide who wins.*")

# Sidebar
with st.sidebar:
    st.header("Arena Settings")
    
    # Model selection
    st.subheader("Select Models")
    selected_models = []
    for model in HERO_MODELS:
        if st.checkbox(model['display'], value=True):
            selected_models.append(model)
    
    if len(selected_models) < 2:
        st.warning("Select at least 2 models")
    
    st.markdown("---")
    
    # Stats
    st.subheader("Arena Stats")
    st.metric("Total Comparisons", len(st.session_state.history))
    st.metric("Total Votes", sum(len(v.get('votes', {})) for v in st.session_state.votes.values()))
    
    st.markdown("---")
    
    # History
    if st.session_state.history:
        st.subheader("Recent Comparisons")
        for i, item in enumerate(st.session_state.history[-5:]):
            st.text(f"{i+1}. {item['prompt'][:30]}...")

# Main area
st.header("Enter Your Prompt")

# Example prompts
example_prompts = [
    "What is consciousness?",
    "Explain quantum computing to a 5-year-old",
    "Write a haiku about recursion",
    "What is 2+2? Show your reasoning",
    "Describe yourself in one sentence",
]

col1, col2 = st.columns([3, 1])
with col1:
    prompt = st.text_area(
        "Prompt",
        placeholder="Enter a prompt to test all models...",
        height=100
    )

with col2:
    st.markdown("**Examples:**")
    selected_example = st.selectbox("Choose an example prompt", [""] + example_prompts)
    if selected_example:
        prompt = selected_example

# Run comparison
if st.button("🥊 Run Comparison", type="primary", disabled=len(selected_models) < 2 or not prompt):
    if not prompt:
        st.error("Enter a prompt first")
    elif len(selected_models) < 2:
        st.error("Select at least 2 models")
    else:
        # Run comparison
        results = run_comparison(prompt, selected_models)
        
        # Store in history
        comparison_id = f"cmp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        st.session_state.history.append({
            "id": comparison_id,
            "prompt": prompt,
            "models": [m['name'] for m in selected_models],
            "timestamp": datetime.now().isoformat()
        })
        
        # Initialize votes for this comparison
        if comparison_id not in st.session_state.votes:
            st.session_state.votes[comparison_id] = {"prompt": prompt, "votes": {}}
        
        # Display results
        st.header("Results")
        
        # Create columns for each model
        cols = st.columns(len(results))
        
        for i, (model_name, data) in enumerate(results.items()):
            with cols[i]:
                st.subheader(data['display'])
                
                # Response box
                st.text_area(
                    "Response",
                    value=data['response'],
                    height=300,
                    key=f"resp_{model_name}_{comparison_id}"
                )
                
                # Vote buttons
                col_up, col_down = st.columns(2)
                with col_up:
                    if st.button("👍", key=f"up_{model_name}_{comparison_id}"):
                        st.session_state.votes[comparison_id]['votes'][model_name] = 1
                        st.success("Voted up!")
                with col_down:
                    if st.button("👎", key=f"down_{model_name}_{comparison_id}"):
                        st.session_state.votes[comparison_id]['votes'][model_name] = -1
                        st.error("Voted down")
                
                # Word count
                word_count = len(data['response'].split())
                st.caption(f"{word_count} words")

# Export section
if st.session_state.history:
    st.markdown("---")
    st.header("Export Data")
    
    if st.button("📥 Export Comparison History"):
        export_data = {
            "history": st.session_state.history,
            "votes": st.session_state.votes,
            "exported_at": datetime.now().isoformat()
        }
        st.download_button(
            "Download JSON",
            json.dumps(export_data, indent=2),
            file_name="inference_arena_data.json",
            mime="application/json"
        )

# Footer
st.markdown("---")
st.caption("Inference Arena MVP - Day 1 Build")
st.caption("Built with Streamlit + Ollama")
