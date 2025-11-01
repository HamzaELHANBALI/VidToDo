from youtube_transcript_api import YouTubeTranscriptApi


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
        if "v=" in video_url:
            video_id = video_url.split("v=")[-1].split("&")[0]
        elif "youtu.be/" in video_url:
            video_id = video_url.split("youtu.be/")[-1].split("?")[0]
        else:
            video_id = video_url  # Assume it's already a video ID
        
        # Get transcript using the new API
        api = YouTubeTranscriptApi()
        transcript_obj = api.fetch(video_id)
        transcript_data = transcript_obj.to_raw_data()
        
        # Extract text from transcript data
        text = " ".join([t["text"] for t in transcript_data])
        return text
    except Exception as e:
        return f"Error fetching transcript: {e}"

