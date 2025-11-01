import streamlit as st
from utils.transcript import get_transcript, extract_video_id
from utils.openai_api import extract_actions_and_summary
from utils.format import parse_actions_json
import json

st.set_page_config(
    page_title="YouTube Action Extractor",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
        color: #1f2937;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #6b7280;
        padding-bottom: 1.5rem;
        font-size: 1.1rem;
        font-weight: 400;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        color: #333 !important;
    }
    .info-box p, .info-box b, .info-box {
        color: #333 !important;
        margin: 0;
    }
    .step-card {
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 0.75rem;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        color: #1f2937 !important;
    }
    .step-card h3, .step-card p, .step-card * {
        color: #1f2937 !important;
    }
    .step-card code {
        background-color: #e8f4f8 !important;
        color: #667eea !important;
        padding: 0.25rem 0.5rem !important;
        border-radius: 0.25rem !important;
        font-weight: 600 !important;
    }
    /* Fix code tags in general to have better contrast */
    code {
        background-color: #f3f4f6 !important;
        color: #667eea !important;
        padding: 0.2rem 0.4rem !important;
        border-radius: 0.25rem !important;
    }
    .summary-card {
        padding: 1.5rem;
        border-radius: 0.75rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 0.5rem;
        height: 3rem;
        font-size: 1.1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Header - Clean and modern
st.markdown('<h1 class="main-header">🎬 YouTube Action Extractor</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Transform YouTube tutorials into actionable step-by-step guides with AI</p>', unsafe_allow_html=True)

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

# Input section with better styling
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    url = st.text_input(
        "📺 YouTube Video URL", 
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="visible"
    )
    
    st.markdown(
        '<div class="info-box" style="color: #333; background-color: #e8f4f8; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #667eea; margin-bottom: 1rem;">'
        '<span style="color: #333;"><strong>💡 Tip:</strong> Supports French and English videos. Results are cached for 24 hours to save tokens!</span>'
        '</div>', 
        unsafe_allow_html=True
    )

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    analyze_button = st.button("🚀 Analyze Video", type="primary", use_container_width=True)

if analyze_button:
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
        st.error(f"❌ {transcript}")
    else:
        # Get cached analysis (won't call OpenAI API if already cached - saves tokens!)
        with st.spinner("🤖 Analyzing with AI..."):
            try:
                actions, summary = get_cached_analysis(video_id, transcript)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.stop()

        st.markdown("---")
        
        # Video metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📹 Video ID", video_id[:20] + "...")
        with col2:
            steps = parse_actions_json(actions)
            st.metric("📋 Steps Found", len(steps) if steps else 0)
        with col3:
            transcript_length = len(transcript.split())
            st.metric("📝 Transcript Words", f"{transcript_length:,}")

        # Display Summary in a styled card
        st.markdown("---")
        st.markdown("### 🧠 Video Summary")
        with st.container():
            # Process summary to add line breaks for bullets
            # First, normalize newlines
            summary_formatted = summary.replace('\r\n', '\n').replace('\r', '\n')
            
            # Handle bullet points - ensure they're on separate lines
            summary_formatted = summary_formatted.replace('• ', '\n• ').replace('- ', '\n- ').replace('* ', '\n* ')
            
            # Split by newlines and process each line
            lines = summary_formatted.split('\n')
            formatted_lines = []
            for line in lines:
                line = line.strip()
                if line:  # Skip empty lines
                    formatted_lines.append(line)
            
            # Join with HTML breaks
            summary_html = '<br>'.join(formatted_lines)
            
            st.markdown(f'<div class="summary-card"><p style="margin:0; font-size:1.1rem; line-height:1.8; white-space: pre-wrap;">{summary_html}</p></div>', unsafe_allow_html=True)

        # Parse tools if available
        try:
            parsed_actions = json.loads(actions)
            tools = parsed_actions.get("tools", [])
        except:
            tools = []
        
        # Display Tools Section (if any tools mentioned)
        if tools:
            st.markdown("---")
            st.markdown("### 🛠️ Tools & Technologies")
            st.info(f"📦 Found {len(tools)} tool(s) discussed in this video")
            
            for tool in tools:
                tool_name = tool.get("name", "Unknown Tool")
                tool_timestamp = tool.get("timestamp", "N/A")
                tool_purpose = tool.get("purpose", "")
                tool_context = tool.get("context", "")
                tool_usage = tool.get("usage", "")
                
                with st.expander(f"🔧 **{tool_name}** ⏱️ `{tool_timestamp}`", expanded=True):
                    if tool_purpose:
                        st.markdown(f"**🎯 Purpose:** {tool_purpose}")
                    if tool_context:
                        st.markdown(f"**📖 Context:** {tool_context}")
                    if tool_usage:
                        st.markdown(f"**⚙️ Usage:** {tool_usage}")
        
        # Display Actionable Steps
        st.markdown("---")
        st.markdown("### ✅ Actionable Steps")
        
        if not steps:
            st.warning("⚠️ No actionable steps found in this video.")
        else:
            st.info(f"📊 Found {len(steps)} actionable step(s) from this video")
        
        # Display steps in styled cards
        for idx, step in enumerate(steps, 1):
            timestamp = step.get("timestamp", "N/A")
            step_text = step.get("step", "")
            code = step.get("code", "")
            tool_context = step.get("tool_context", "")
            
            # Step card with better styling
            with st.container():
                st.markdown(
                    f"""
                    <div class="step-card" style="color: #1f2937;">
                        <h3 style="color: #1f2937;">Step {idx} ⏱️ <code style="background-color: #e8f4f8; color: #667eea; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-weight: 600;">{timestamp}</code></h3>
                        <p style="color: #1f2937;"><strong>📝 Action:</strong> {step_text}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Display tool context if mentioned in this step
                if tool_context and tool_context.strip():
                    st.markdown(f"**🛠️ Tool Context:** {tool_context}")
                
                if code and code.strip():
                    st.markdown("**💻 Code Snippet:**")
                    st.code(code, language="python")
            
            if idx < len(steps):
                st.markdown("<br>", unsafe_allow_html=True)
        
        # Sidebar with info
        with st.sidebar:
            st.markdown("### ℹ️ About")
            st.markdown("""
            **YouTube Action Extractor** transforms tutorial videos into:
            - ✅ Clear step-by-step guides
            - 📋 Actionable items with timestamps
            - 💻 Code snippets (when available)
            - 🧠 Quick summaries
            """)
            
            st.markdown("### ⚡ Features")
            st.markdown("""
            - 🌍 French & English support
            - 💾 Smart caching (24h)
            - 🤖 Powered by GPT-4o-mini
            - ⚡ Fast & efficient
            """)
            
            st.markdown("### 🔒 Privacy")
            st.markdown("""
            - API keys stay secure
            - No video data stored
            - Cached locally only
            """)

