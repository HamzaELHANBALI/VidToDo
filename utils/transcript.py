from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    IpBlocked,
    RequestBlocked,
    YouTubeRequestFailed,
    CouldNotRetrieveTranscript
)


def extract_video_id(video_url: str) -> str:
    """
    Extract video ID from YouTube URL.
    
    Args:
        video_url: YouTube video URL (full URL or video ID)
    
    Returns:
        str: Video ID
    """
    if "v=" in video_url:
        return video_url.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in video_url:
        return video_url.split("youtu.be/")[-1].split("?")[0]
    else:
        return video_url  # Assume it's already a video ID


def get_transcript(video_url: str):
    """
    Extract transcript from YouTube video URL.
    
    Args:
        video_url: YouTube video URL (full URL or video ID)
    
    Returns:
        str: Transcript text or error message
    """
    try:
        # Extract video ID from URL
        video_id = extract_video_id(video_url)
        
        # Get transcript using the new API
        # Try French first, automatically fall back to English if not available
        api = YouTubeTranscriptApi()
        # languages parameter: tries French first, then English if French not available
        transcript_obj = api.fetch(video_id, languages=('fr', 'en'))
        transcript_data = transcript_obj.to_raw_data()
        
        # Extract text from transcript data
        text = " ".join([t["text"] for t in transcript_data])
        return text
    except TranscriptsDisabled:
        return "Error: Transcripts are disabled for this video."
    except NoTranscriptFound:
        return "Error: No transcript found for this video. The video may not have captions enabled."
    except VideoUnavailable:
        return "Error: Video is unavailable. Please check if the video URL is correct."
    except (IpBlocked, RequestBlocked) as e:
        error_msg = str(e)
        detailed_msg = """Error: YouTube has blocked requests from your IP address.

This usually happens because:
• Too many requests from your IP (rate limiting)
• Using a cloud provider IP (AWS, GCP, Azure, etc.) which YouTube blocks
• Temporary IP ban

Solutions:
• Wait 10-15 minutes and try again
• Use a VPN or different network (for local development)
• For Streamlit Cloud: Consider using proxies or accept occasional failures
• Try again from a different location/network

Note: On Streamlit Cloud, requests come from cloud provider IPs which YouTube often blocks."""
        return detailed_msg
    except (YouTubeRequestFailed, CouldNotRetrieveTranscript) as e:
        error_msg = str(e)
        if "IP" in error_msg.upper() or "blocked" in error_msg.lower():
            detailed_msg = """Error: YouTube is blocking requests from your IP address.

This usually happens because:
• Too many requests from your IP
• Using a cloud provider IP (AWS, GCP, Azure, etc.) which YouTube blocks
• Temporary rate limiting by YouTube

Solutions:
• Wait 10-15 minutes and try again
• Use a VPN or different network
• Consider using proxies (see youtube-transcript-api documentation)
• Try again from a different location/network"""
            return detailed_msg
        return f"Error fetching transcript: {error_msg}"
    except Exception as e:
        error_msg = str(e)
        # Check if it's an IP blocking error
        if "IP" in error_msg.upper() or "blocked" in error_msg.lower() or "requestblocked" in error_msg.lower():
            return """Error: YouTube is blocking requests from your IP address.

Common causes:
• Too many requests (rate limiting)
• Using a cloud provider IP
• Temporary IP ban

What you can do:
• Wait 10-15 minutes before trying again
• Use a VPN or different network connection
• Try accessing from a different location
• Consider using proxies for production use

If this persists, you may need to use proxy services or wait longer between requests."""
        return f"Error fetching transcript: {error_msg}"

