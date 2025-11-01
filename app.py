import streamlit as st
from utils.transcript import get_transcript
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

url = st.text_input("Paste a YouTube video link", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Analyze Video", type="primary"):
    if not url:
        st.warning("Please enter a YouTube URL")
        st.stop()
    
    with st.spinner("Fetching transcript..."):
        transcript = get_transcript(url)
    
    if transcript.startswith("Error"):
        st.error(transcript)
    else:
        if not st.session_state.get("transcript", None):
            st.session_state["transcript"] = transcript
        
        with st.spinner("Analyzing with GPT..."):
            try:
                actions, summary = extract_actions_and_summary(transcript)
            except Exception as e:
                st.error(f"Error calling OpenAI API: {e}")
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

