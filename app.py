import streamlit as st
from utils.transcript import get_transcript, extract_video_id
from utils.openai_api import extract_actions_and_summary
from utils.format import parse_actions_json
import json

st.set_page_config(
    page_title="YouTube Action Extractor",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 YouTube Action Extractor")
st.markdown("Paste a YouTube URL to extract actionable steps and a summary from tutorial videos.")

# Cache configuration - cache by video ID to avoid reprocessing
@st.cache_data(ttl=3600)  # Cache transcripts for 1 hour
def get_cached_transcript(video_id: str):
    """Cached transcript fetching by video ID."""
    return get_transcript(video_id)

@st.cache_data(ttl=86400)  # Cache OpenAI analysis for 24 hours (save tokens!)
def get_cached_analysis(video_id: str, transcript: str):
    """Cached OpenAI analysis by video ID - won't call API if already processed."""
    try:
        return extract_actions_and_summary(transcript)
    except Exception as e:
        raise Exception(f"Error calling OpenAI API: {e}")

url = st.text_input("Paste a YouTube video link", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Analyze Video", type="primary"):
    if not url:
        st.warning("Please enter a YouTube URL")
        st.stop()
    
    # Extract video ID for caching
    try:
        video_id = extract_video_id(url)
    except Exception as e:
        st.error(f"Invalid YouTube URL: {e}")
        st.stop()
    
    # Get cached transcript (won't fetch again if same video was processed)
    with st.spinner("Fetching transcript..."):
        transcript = get_cached_transcript(video_id)
    
    if transcript.startswith("Error"):
        st.error(transcript)
    else:
        # Get cached analysis (won't call OpenAI API if already cached - saves tokens!)
        with st.spinner("Analyzing with GPT..."):
            try:
                actions, summary = get_cached_analysis(video_id, transcript)
            except Exception as e:
                st.error(str(e))
                st.stop()

        # Display Summary
        st.subheader("🧠 Summary")
        st.write(summary)

        # Display Actionable Steps
        st.subheader("✅ Actionable Steps")
        steps = parse_actions_json(actions)
        
        if steps:
            for idx, step in enumerate(steps, 1):
                with st.container():
                    timestamp = step.get("timestamp", "N/A")
                    step_text = step.get("step", "")
                    code = step.get("code", "")
                    
                    st.markdown(f"**Step {idx}** ({timestamp}) — {step_text}")
                    
                    if code and code.strip():
                        st.code(code, language="python")
                    
                    st.divider()
        else:
            # Fallback: display raw JSON if parsing failed
            st.text("Raw output:")
            st.text(actions)
            
            # Try to parse as direct JSON
            try:
                parsed = json.loads(actions)
                st.json(parsed)
            except:
                pass

