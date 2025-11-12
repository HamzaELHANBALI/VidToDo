# VidToDo - Project Architecture Documentation

## 📐 System Overview

**VidToDo** (YouTube Action Extractor) is a Streamlit-based web application that transforms YouTube tutorial videos into actionable step-by-step guides. The system extracts transcripts from YouTube videos, uses AI to analyze them, and presents structured, actionable steps with timestamps, code snippets, and summaries.

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (Streamlit Web Application)                  │
│                         (app.py)                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ User Input: YouTube URL
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    URL PROCESSING LAYER                         │
│              (utils/transcript.py - extract_video_id)           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Video ID
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CACHING LAYER                                │
│              (Dual Cache System)                                │
│  ┌──────────────────────┐  ┌──────────────────────┐           │
│  │  Streamlit Cache     │  │  File-Based Cache    │           │
│  │  (In-Memory, TTL)    │  │  (Persistent, TTL)   │           │
│  │  (utils/cache.py)    │  │  (utils/cache.py)    │           │
│  └──────────────────────┘  └──────────────────────┘           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Cache Miss → Fetch
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              TRANSCRIPT EXTRACTION LAYER                        │
│              (utils/transcript.py - get_transcript)             │
│                    YouTube Transcript API                       │
│              (youtube-transcript-api library)                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Raw Transcript Text
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CACHING LAYER                                │
│              (Store Transcript in Cache)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Transcript
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              AI ANALYSIS LAYER                                  │
│              (utils/openai_api.py)                              │
│                    OpenAI GPT-4o-mini API                       │
│  ┌────────────────────────┐  ┌────────────────────────┐       │
│  │  Action Extraction     │  │  Summary Generation    │       │
│  │  (JSON Format)         │  │  (Text Format)         │       │
│  └────────────────────────┘  └────────────────────────┘       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Actions JSON + Summary
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CACHING LAYER                                │
│              (Store Analysis in Cache)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Cached/New Results
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              FORMATTING & PARSING LAYER                         │
│              (utils/format.py - parse_actions_json)             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Parsed Steps + Summary
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                           │
│                    (app.py - UI Rendering)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Summary    │  │    Steps     │  │    Tools     │         │
│  │    Card      │  │    Cards     │  │    Section   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Component Breakdown

### 1. **Frontend/UI Layer** (`app.py`)

**Purpose**: Main entry point and user interface orchestration

**Responsibilities**:
- Streamlit web application setup and configuration
- User input handling (YouTube URL)
- UI rendering and styling (custom CSS)
- Component orchestration and data flow management
- Error handling and user feedback
- Display of results (summary, steps, tools, metrics)

**Key Functions**:
- `get_cached_transcript(video_id)`: Wraps transcript fetching with dual caching
- `get_cached_analysis(video_id, transcript)`: Wraps AI analysis with dual caching

**Dependencies**:
- `utils.transcript` - For video ID extraction and transcript fetching
- `utils.openai_api` - For AI analysis
- `utils.format` - For parsing JSON results
- `utils.cache` - For persistent caching

**Interactions**:
- Receives user input (YouTube URL)
- Calls `extract_video_id()` to parse URL
- Calls `get_cached_transcript()` which internally uses `get_transcript()`
- Calls `get_cached_analysis()` which internally uses `extract_actions_and_summary()`
- Calls `parse_actions_json()` to format results
- Renders all results in the UI

---

### 2. **Transcript Extraction Module** (`utils/transcript.py`)

**Purpose**: Extract video transcripts from YouTube

**Responsibilities**:
- Extract video ID from various YouTube URL formats
- Fetch transcript from YouTube using `youtube-transcript-api`
- Handle multiple languages (French, English with fallback)
- Comprehensive error handling for YouTube API issues

**Key Functions**:

#### `extract_video_id(video_url: str) -> str`
- **Input**: YouTube URL (full URL or video ID)
- **Output**: Extracted video ID string
- **Logic**: 
  - Handles `youtube.com/watch?v=VIDEO_ID` format
  - Handles `youtu.be/VIDEO_ID` format
  - Handles direct video ID input
- **Returns**: Clean video ID

#### `get_transcript(video_url: str) -> str`
- **Input**: YouTube URL or video ID
- **Output**: Transcript text or error message string
- **Logic**:
  1. Extracts video ID using `extract_video_id()`
  2. Calls `YouTubeTranscriptApi.fetch()` with language preference (fr, en)
  3. Processes transcript data into plain text
  4. Handles various error cases (disabled transcripts, unavailable videos, IP blocks, etc.)
- **Error Handling**: Returns descriptive error messages for:
  - `TranscriptsDisabled`: Transcripts not available
  - `NoTranscriptFound`: No captions available
  - `VideoUnavailable`: Invalid video URL
  - `IpBlocked` / `RequestBlocked`: YouTube IP blocking
  - `YouTubeRequestFailed`: General API failures

**Dependencies**:
- `youtube-transcript-api` library
- YouTube's transcript service (external API)

**Interactions**:
- Called by `app.py` via `get_cached_transcript()`
- Communicates with YouTube's transcript API
- Returns transcript text or error messages to caller

---

### 3. **AI Analysis Module** (`utils/openai_api.py`)

**Purpose**: Analyze transcripts using OpenAI API to extract actionable steps and generate summaries

**Responsibilities**:
- Manage OpenAI API client initialization
- Handle API key retrieval from Streamlit secrets or environment variables
- Extract actionable steps from transcripts
- Generate video summaries
- Format responses as JSON and text

**Key Functions**:

#### `get_openai_api_key() -> str`
- **Purpose**: Retrieve API key from multiple sources
- **Priority**:
  1. Streamlit secrets (`st.secrets["OPENAI_API_KEY"]`) - for cloud deployment
  2. Environment variable (`os.getenv("OPENAI_API_KEY")`) - for local development
- **Returns**: API key string or raises error if not found

#### `get_openai_client() -> OpenAI`
- **Purpose**: Initialize OpenAI client with proper API key
- **Returns**: Configured OpenAI client instance
- **Error Handling**: Raises `ValueError` if API key not found

#### `extract_actions_and_summary(transcript: str) -> tuple[str, str]`
- **Input**: Full transcript text
- **Output**: Tuple of (actions_json_string, summary_string)
- **Process**:
  1. **Transcript Truncation**: Limits transcript to 10,000 characters for action extraction
  2. **Action Extraction**:
     - Creates detailed prompt for GPT-4o-mini
     - Requests JSON format response
     - Extracts: steps (with timestamps, code, tool_context), tools (with purpose, context, usage)
  3. **Summary Generation**:
     - Uses first 4,000 characters of transcript
     - Requests 3 bullet points, max 120 words
  4. **API Calls**: Makes two separate API calls:
     - `client.chat.completions.create()` for actions (JSON mode)
     - `client.chat.completions.create()` for summary (text mode)
- **Returns**: `(actions_json_string, summary_string)`

**Dependencies**:
- `openai` library
- `python-dotenv` for environment variable loading
- `streamlit` (for secrets access)
- OpenAI API service (external)

**Interactions**:
- Called by `app.py` via `get_cached_analysis()`
- Communicates with OpenAI GPT-4o-mini API
- Returns structured JSON (actions) and text (summary) to caller

---

### 4. **Formatting Module** (`utils/format.py`)

**Purpose**: Parse and format AI-generated JSON responses

**Responsibilities**:
- Parse JSON strings into Python dictionaries
- Extract steps from structured JSON
- Format timestamps (if needed in future)

**Key Functions**:

#### `parse_actions_json(actions_json_string: str) -> List[Dict[str, Any]]`
- **Input**: JSON string containing actions
- **Output**: List of step dictionaries
- **Logic**:
  1. Parses JSON string using `json.loads()`
  2. Extracts `steps` array from JSON structure
  3. Handles edge cases (direct list, missing steps key)
  4. Returns empty list on parse errors
- **Returns**: List of dictionaries, each containing:
  - `step`: Action description
  - `timestamp`: Time in video (mm:ss format)
  - `code`: Optional code snippet
  - `tool_context`: Optional tool usage explanation

#### `format_timestamp(seconds: float) -> str`
- **Purpose**: Convert seconds to mm:ss format
- **Input**: Time in seconds (float)
- **Output**: Formatted string (e.g., "05:23")
- **Note**: Currently defined but not actively used in main flow

**Dependencies**:
- Python standard library (`json`, `typing`)

**Interactions**:
- Called by `app.py` to parse AI-generated JSON
- Receives JSON string from AI analysis
- Returns structured Python data for UI rendering

---

### 5. **Caching Module** (`utils/cache.py`)

**Purpose**: Provide persistent, file-based caching system

**Responsibilities**:
- Store transcripts and analysis results on disk
- Retrieve cached data with TTL (Time To Live) validation
- Manage cache file organization
- Provide cache statistics and cleanup utilities

**Key Functions**:

#### `get_cache_file(cache_type: str, key: str) -> Path`
- **Purpose**: Generate cache file path
- **Input**: 
  - `cache_type`: 'transcript' or 'analysis'
  - `key`: Video ID (sanitized for filename)
- **Output**: Path object to cache file
- **Logic**: Creates filename like `transcript_VIDEO_ID.json` or `analysis_VIDEO_ID.json`
- **Storage**: Files stored in `.cache/` directory

#### `load_from_cache(cache_type: str, key: str, ttl: int) -> Optional[Any]`
- **Purpose**: Load cached data if valid
- **Input**:
  - `cache_type`: 'transcript' or 'analysis'
  - `key`: Video ID
  - `ttl`: Time to live in seconds
- **Output**: Cached data if valid, `None` if expired/missing
- **Logic**:
  1. Checks if cache file exists
  2. Loads JSON data
  3. Validates timestamp against TTL
  4. Returns data if valid, deletes file if expired
  5. Handles corrupted files gracefully
- **TTL Behavior**: 
  - Transcripts: 3600 seconds (1 hour)
  - Analysis: 86400 seconds (24 hours)

#### `save_to_cache(cache_type: str, key: str, data: Any) -> None`
- **Purpose**: Save data to cache file
- **Input**:
  - `cache_type`: 'transcript' or 'analysis'
  - `key`: Video ID
  - `data`: Any serializable data
- **Logic**:
  1. Creates cache data structure with timestamp
  2. Writes JSON to file
  3. Handles write errors silently (doesn't break app)
- **Storage Format**:
  ```json
  {
    "timestamp": 1234567890.123,
    "data": <actual cached data>
  }
  ```

#### `clear_cache(cache_type: Optional[str] = None) -> None`
- **Purpose**: Delete cache files
- **Input**: Optional cache type filter
- **Logic**: Deletes matching cache files

#### `get_cache_size() -> dict`
- **Purpose**: Get cache statistics
- **Output**: Dictionary with file counts and total size

**Dependencies**:
- Python standard library (`os`, `json`, `time`, `pathlib`)

**Interactions**:
- Called by `app.py` caching wrapper functions
- Used before external API calls (transcript, OpenAI)
- Used after successful API calls to persist results
- Provides persistence across app restarts (unlike Streamlit's in-memory cache)

---

## 🔄 Data Flow Diagram

### Complete Request Flow

```
1. USER INPUT
   └─> User enters YouTube URL in Streamlit UI
       └─> app.py receives URL string

2. URL PROCESSING
   └─> app.py calls extract_video_id(url)
       └─> utils/transcript.py extracts video ID
           └─> Returns: video_id (string)

3. TRANSCRIPT CACHING CHECK
   └─> app.py calls get_cached_transcript(video_id)
       ├─> Checks Streamlit cache (@st.cache_data)
       └─> If miss: Checks file cache (utils/cache.py)
           ├─> If hit: Returns cached transcript
           └─> If miss: Proceeds to fetch

4. TRANSCRIPT FETCHING
   └─> app.py calls get_transcript(video_id)
       └─> utils/transcript.py
           ├─> Calls YouTubeTranscriptApi.fetch()
           ├─> Processes transcript data
           └─> Returns: transcript_text (string) or error_message

5. TRANSCRIPT CACHING STORAGE
   └─> app.py saves transcript to cache
       ├─> Streamlit cache (automatic via @st.cache_data)
       └─> File cache (utils/cache.py - save_to_cache())

6. AI ANALYSIS CACHING CHECK
   └─> app.py calls get_cached_analysis(video_id, transcript)
       ├─> Checks Streamlit cache (@st.cache_data)
       └─> If miss: Checks file cache (utils/cache.py)
           ├─> If hit: Returns cached (actions, summary)
           └─> If miss: Proceeds to analyze

7. AI ANALYSIS
   └─> app.py calls extract_actions_and_summary(transcript)
       └─> utils/openai_api.py
           ├─> Truncates transcript (10k chars for actions, 4k for summary)
           ├─> API Call 1: Action extraction (JSON mode)
           │   └─> Returns: actions_json_string
           └─> API Call 2: Summary generation (text mode)
               └─> Returns: summary_string
           └─> Returns: (actions_json_string, summary_string)

8. ANALYSIS CACHING STORAGE
   └─> app.py saves analysis to cache
       ├─> Streamlit cache (automatic via @st.cache_data)
       └─> File cache (utils/cache.py - save_to_cache())

9. FORMATTING
   └─> app.py calls parse_actions_json(actions_json_string)
       └─> utils/format.py
           ├─> Parses JSON string
           ├─> Extracts steps array
           └─> Returns: List[Dict] of steps

10. UI RENDERING
    └─> app.py renders results
        ├─> Metrics (video ID, step count, word count)
        ├─> Summary card (styled HTML)
        ├─> Tools section (if tools found)
        └─> Actionable steps (numbered cards with timestamps, code, tool context)
```

---

## 🗂️ File Structure & Dependencies

```
VidToDo/
│
├── app.py                          # Main application entry point
│   ├── Imports: streamlit, utils modules
│   ├── UI Components: Headers, inputs, buttons, displays
│   ├── Caching Wrappers: get_cached_transcript, get_cached_analysis
│   └── Main Flow: URL → Video ID → Transcript → Analysis → Display
│
├── utils/
│   ├── __init__.py                 # Package initialization
│   │
│   ├── transcript.py               # YouTube transcript extraction
│   │   ├── extract_video_id()     # URL parsing
│   │   ├── get_transcript()        # Transcript fetching
│   │   └── Dependencies: youtube-transcript-api
│   │
│   ├── openai_api.py               # AI analysis integration
│   │   ├── get_openai_api_key()   # Key retrieval
│   │   ├── get_openai_client()     # Client initialization
│   │   ├── extract_actions_and_summary()  # Main analysis function
│   │   └── Dependencies: openai, python-dotenv, streamlit (for secrets)
│   │
│   ├── format.py                   # JSON parsing and formatting
│   │   ├── parse_actions_json()    # Parse AI JSON response
│   │   ├── format_timestamp()      # Time formatting utility
│   │   └── Dependencies: json (stdlib)
│   │
│   └── cache.py                    # Persistent file-based caching
│       ├── get_cache_file()        # Path generation
│       ├── load_from_cache()      # Cache retrieval with TTL
│       ├── save_to_cache()         # Cache storage
│       ├── clear_cache()           # Cache cleanup
│       ├── get_cache_size()        # Cache statistics
│       └── Dependencies: os, json, time, pathlib (stdlib)
│
├── .cache/                         # Cache directory (auto-created)
│   ├── transcript_VIDEO_ID.json    # Cached transcripts
│   └── analysis_VIDEO_ID.json      # Cached analysis results
│
├── requirements.txt                 # Python dependencies
│   ├── streamlit                   # Web framework
│   ├── openai                      # OpenAI API client
│   ├── youtube-transcript-api      # YouTube transcript extraction
│   ├── yt-dlp                      # YouTube downloader (future use)
│   ├── whisper                     # Speech-to-text (future use)
│   └── python-dotenv               # Environment variable management
│
├── .env                            # Environment variables (local)
│   └── OPENAI_API_KEY=sk-...       # API key for local development
│
└── README.md                        # Project documentation
```

---

## 🔌 External Dependencies & APIs

### 1. **YouTube Transcript API** (via `youtube-transcript-api`)
- **Purpose**: Fetch video transcripts/captions
- **Interaction**: Called by `utils/transcript.py`
- **Data Flow**: Video ID → Transcript text
- **Error Handling**: Comprehensive error messages for various failure modes
- **Language Support**: French (primary), English (fallback)

### 2. **OpenAI GPT-4o-mini API** (via `openai` library)
- **Purpose**: AI-powered analysis of transcripts
- **Interaction**: Called by `utils/openai_api.py`
- **Data Flow**: Transcript text → JSON actions + text summary
- **API Calls**: Two separate calls per analysis
  - Action extraction (JSON mode)
  - Summary generation (text mode)
- **Authentication**: API key from Streamlit secrets or `.env` file

### 3. **Streamlit Framework**
- **Purpose**: Web application framework
- **Features Used**:
  - UI components (text inputs, buttons, containers)
  - Caching (`@st.cache_data`)
  - Secrets management (`st.secrets`)
  - Custom CSS styling
  - Session state management

---

## 💾 Caching Strategy

### Dual-Layer Caching System

**Layer 1: Streamlit In-Memory Cache**
- **Mechanism**: `@st.cache_data` decorator
- **Scope**: Application session
- **TTL**: 
  - Transcripts: 3600 seconds (1 hour)
  - Analysis: 86400 seconds (24 hours)
- **Advantage**: Fast, no I/O
- **Limitation**: Lost on app restart

**Layer 2: File-Based Persistent Cache**
- **Mechanism**: JSON files in `.cache/` directory
- **Scope**: Persistent across app restarts
- **TTL**: Same as Streamlit cache
- **Advantage**: Survives restarts, reduces API calls
- **Storage**: 
  - Format: `{timestamp: float, data: Any}`
  - Files: `transcript_VIDEO_ID.json`, `analysis_VIDEO_ID.json`

**Cache Flow**:
1. Check Streamlit cache first (fastest)
2. If miss, check file cache (persistent)
3. If miss, fetch from API
4. Save to both caches after successful fetch

---

## 🔐 Security & Configuration

### API Key Management

**Local Development**:
- Uses `.env` file with `OPENAI_API_KEY`
- Loaded via `python-dotenv` in `openai_api.py`

**Cloud Deployment (Streamlit Cloud)**:
- Uses `st.secrets["OPENAI_API_KEY"]`
- Configured in Streamlit Cloud dashboard
- Falls back to environment variable if secrets unavailable

**Priority Order**:
1. Streamlit secrets (cloud)
2. Environment variable (local)

---

## 🎨 UI Component Structure

### Main Components (app.py)

1. **Header Section**
   - Title: "🎬 YouTube Action Extractor"
   - Subtitle: Description text
   - Custom CSS styling

2. **Input Section**
   - Text input for YouTube URL
   - Info box with tips
   - Analyze button

3. **Results Section** (conditional rendering)
   - **Metrics Row**: Video ID, Step count, Word count
   - **Summary Card**: Styled gradient card with bullet points
   - **Tools Section**: Expandable cards for each tool mentioned
   - **Steps Section**: Numbered cards with:
     - Timestamp (code-styled)
     - Action description
     - Tool context (if applicable)
     - Code snippets (if available)

4. **Sidebar**
   - About section
   - Features list
   - Privacy information

---

## 🔄 Error Handling Flow

### Transcript Errors
```
get_transcript() → Error Detection
├─> TranscriptsDisabled → User-friendly message
├─> NoTranscriptFound → Helpful suggestions
├─> VideoUnavailable → URL validation message
├─> IpBlocked/RequestBlocked → Detailed troubleshooting guide
└─> Generic Exception → Error message with context
```

### AI Analysis Errors
```
extract_actions_and_summary() → Error Detection
├─> API Key Missing → ValueError with setup instructions
├─> API Call Failure → Exception with error details
└─> JSON Parse Failure → Handled in format.py (returns empty list)
```

### Cache Errors
```
load_from_cache() → Error Handling
├─> File Not Found → Returns None (cache miss)
├─> Corrupted JSON → Deletes file, returns None
├─> Expired TTL → Deletes file, returns None
└─> Write Failure → Silent failure (doesn't break app)
```

---

## 📊 Data Structures

### Transcript Data
- **Type**: `str`
- **Content**: Plain text transcript from YouTube
- **Source**: YouTube Transcript API
- **Storage**: Cached as string in both cache layers

### Actions JSON Structure
```json
{
  "steps": [
    {
      "step": "Action description",
      "timestamp": "mm:ss",
      "code": "optional code snippet",
      "tool_context": "optional tool explanation"
    }
  ],
  "tools": [
    {
      "name": "Tool name",
      "timestamp": "mm:ss",
      "purpose": "Why tool is used",
      "context": "What aspect is explained",
      "usage": "How it fits in workflow"
    }
  ]
}
```

### Summary Data
- **Type**: `str`
- **Format**: 3 bullet points, max 120 words
- **Content**: High-level video overview

### Cache File Structure
```json
{
  "timestamp": 1234567890.123,
  "data": <actual cached data (transcript string or [actions, summary] tuple)>
}
```

---

## 🚀 Execution Flow Summary

1. **User Interaction**: User enters YouTube URL and clicks "Analyze"
2. **URL Processing**: Extract video ID from URL
3. **Cache Check**: Check both cache layers for transcript
4. **Transcript Fetch**: If cache miss, fetch from YouTube API
5. **Cache Store**: Save transcript to both cache layers
6. **Analysis Cache Check**: Check both cache layers for analysis
7. **AI Analysis**: If cache miss, call OpenAI API (2 calls)
8. **Cache Store**: Save analysis to both cache layers
9. **Formatting**: Parse JSON actions into structured data
10. **Rendering**: Display all results in styled UI components

---

## 🔮 Future Architecture Considerations

### Potential Enhancements (from README)
- **Whisper Integration**: Fallback for videos without transcripts
  - Would add: `utils/whisper_fallback.py`
  - Would use: `yt-dlp` to download audio, `whisper` to transcribe
- **Export Functionality**: Export to Markdown/Notion/TXT
  - Would add: `utils/export.py`
- **Playlist Support**: Process multiple videos
  - Would modify: `app.py` to handle multiple video IDs
  - Would add: Batch processing logic

---

## 📝 Key Design Patterns

1. **Separation of Concerns**: Each module has a single, clear responsibility
2. **Dual Caching**: Fast in-memory + persistent file-based caching
3. **Error Resilience**: Comprehensive error handling at each layer
4. **Modularity**: Utils modules are independent and testable
5. **Configuration Flexibility**: Supports both local (.env) and cloud (secrets) configs
6. **Progressive Enhancement**: Cache-first approach reduces API calls

---

This architecture document provides a comprehensive overview of how each component interacts within the VidToDo system. Use this information to generate visual diagrams, flowcharts, or component interaction diagrams.

