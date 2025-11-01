import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_actions_and_summary(transcript: str):
    """
    Extract actionable steps and summary from YouTube transcript using OpenAI.
    
    Args:
        transcript: Full transcript text
    
    Returns:
        tuple: (actions_json_string, summary_string)
    """
    # Truncate transcript if too long (to avoid token limits)
    transcript_snippet = transcript[:10000] if len(transcript) > 10000 else transcript
    
    # --- Action Extraction ---
    action_prompt = f"""
You are an AI engineer that extracts clear, actionable steps from YouTube tutorials.

From this transcript, list concise steps with timestamps and code (if mentioned).

Return JSON in this exact format:
{{
  "steps": [
    {{ "step": "string", "timestamp": "mm:ss", "code": "optional code snippet" }},
    {{ "step": "string", "timestamp": "mm:ss", "code": "" }}
  ]
}}

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

