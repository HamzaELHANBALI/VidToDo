import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Get API key from Streamlit secrets (for cloud deployment) or environment variable (for local)
def get_openai_api_key():
    """Get OpenAI API key from Streamlit secrets or environment variable."""
    try:
        # Try Streamlit secrets first (works on Streamlit Cloud)
        import streamlit as st
        return st.secrets["OPENAI_API_KEY"]
    except (KeyError, AttributeError, RuntimeError, ImportError):
        # Fallback to environment variable (works locally with .env file)
        return os.getenv("OPENAI_API_KEY")

# Initialize client lazily to avoid issues with st.secrets at module level
def get_openai_client():
    """Get OpenAI client with API key from secrets or environment."""
    api_key = get_openai_api_key()
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in Streamlit secrets or environment variables. Please set it in .env file (local) or Streamlit Cloud secrets (deployment).")
    return OpenAI(api_key=api_key)


def extract_actions_and_summary(transcript: str):
    """
    Extract actionable steps and summary from YouTube transcript using OpenAI.
    
    Args:
        transcript: Full transcript text
    
    Returns:
        tuple: (actions_json_string, summary_string)
    """
    # Get client (will load API key from secrets or env)
    client = get_openai_client()
    
    # Truncate transcript if too long (to avoid token limits)
    transcript_snippet = transcript[:10000] if len(transcript) > 10000 else transcript
    
    # --- Action Extraction ---
    action_prompt = f"""
You are an AI engineer that extracts clear, actionable steps from YouTube tutorials.

From this transcript, extract:
1. Actionable steps with timestamps and code (if mentioned)
2. Tools mentioned in the video - when a tool (like Super Whisper, API, library, framework, etc.) is discussed, capture:
   - The tool name
   - Why it's being used (the purpose/context)
   - What part/aspect of the tool is being explained
   - How it fits into the overall workflow

IMPORTANT: If tools are mentioned, provide detailed context about their usage. Don't just mention the tool name - explain why it's needed and how it's used.

Return JSON in this exact format:
{{
  "steps": [
    {{ "step": "string", "timestamp": "mm:ss", "code": "optional code snippet", "tool_context": "optional - explain tool usage if mentioned" }},
    {{ "step": "string", "timestamp": "mm:ss", "code": "", "tool_context": "" }}
  ],
  "tools": [
    {{
      "name": "tool name",
      "timestamp": "mm:ss",
      "purpose": "why this tool is used",
      "context": "what aspect/part is explained",
      "usage": "how it fits in the workflow"
    }}
  ]
}}

Note: If no tools are mentioned, return an empty "tools" array. The "tool_context" field in steps should explain any tool usage mentioned in that specific step.

Transcript:
{transcript_snippet}
"""

    action_res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": action_prompt}],
        response_format={"type": "json_object"}
    )

    actions = action_res.choices[0].message.content

    # --- Summary ---
    summary_snippet = transcript[:4000] if len(transcript) > 4000 else transcript
    summary_prompt = f"""
Summarize this video in 3 short bullet points (max 120 words total).

Transcript:
{summary_snippet}
"""

    summary_res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": summary_prompt}]
    )

    summary = summary_res.choices[0].message.content
    return actions, summary

