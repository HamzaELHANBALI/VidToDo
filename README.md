# 🎬 YouTube Action Extractor

A Streamlit app that extracts actionable steps and summaries from YouTube tutorial videos.

## 🚀 Quick Start

1. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment:**
   ```bash
   # Create .env file and add your OpenAI API key
   echo "OPENAI_API_KEY=sk-your-key-here" > .env
   # Or manually create .env file with: OPENAI_API_KEY=sk-your-key-here
   ```

4. **Run the app:**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser:**
   Navigate to `http://localhost:8501`

## 📋 Features

- ✨ Paste any YouTube URL
- 📝 Extract transcript automatically (supports French and English)
- 🌍 Automatic language detection: tries French first, falls back to English
- 🧠 Generate summary using GPT-4o-mini
- ✅ Extract actionable steps with timestamps
- 💻 Capture code snippets when mentioned

## 🛠️ Project Structure

```
youtube-action-extractor/
├── app.py                # Main Streamlit app
├── requirements.txt      # Dependencies
├── utils/
│   ├── transcript.py     # YouTube transcript extraction
│   ├── openai_api.py     # OpenAI API integration
│   └── format.py         # Output formatting utilities
└── .env                  # Environment variables (OPENAI_API_KEY)
```

## 📦 Dependencies

- `streamlit` - Web app framework
- `openai` - OpenAI API client
- `youtube-transcript-api` - YouTube transcript extraction
- `yt-dlp` - YouTube downloader (for future Whisper fallback)
- `whisper` - Speech-to-text (for future fallback)
- `python-dotenv` - Environment variable management

## 💡 Future Improvements

- [ ] Add Whisper fallback for videos without transcripts
- [ ] Export results to Markdown/Notion/TXT
- [ ] Add caching to avoid re-fetching transcripts
- [ ] Progress bars and better UI styling
- [ ] Support for playlist URLs

## 🔐 Environment Variables

### Local Development

Create a `.env` file with:
```
OPENAI_API_KEY=sk-your-key-here
```

Or use Streamlit secrets (create `.streamlit/secrets.toml`):
```toml
OPENAI_API_KEY = "sk-your-key-here"
```

## ☁️ Deploy to Streamlit Cloud

1. **Push your code to GitHub:**
   ```bash
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect your GitHub account and select this repository
   - Set the main file path: `app.py`
   - Click "Deploy!"

3. **Add your API key securely:**
   - After deployment, click the "⚙️" icon (Settings) in the top right
   - Go to "Secrets" tab
   - Add your API key in this format:
     ```toml
     OPENAI_API_KEY = "sk-your-actual-key-here"
     ```
   - Click "Save"

4. **Redeploy if needed:**
   - The app will automatically redeploy, or you can click "Always rerun" in the menu

The app will automatically use `st.secrets` on Streamlit Cloud (no code changes needed - it's already configured!).

