import json
from typing import List, Dict, Any


def parse_actions_json(actions_json_string: str) -> List[Dict[str, Any]]:
    """
    Parse the actions JSON string and extract steps.
    
    Args:
        actions_json_string: JSON string containing actions
    
    Returns:
        List of step dictionaries
    """
    try:
        data = json.loads(actions_json_string)
        if "steps" in data:
            return data["steps"]
        # Fallback: if it's a list directly
        if isinstance(data, list):
            return data
        return []
    except json.JSONDecodeError:
        return []


def format_timestamp(seconds: float) -> str:
    """
    Format seconds to mm:ss format.
    
    Args:
        seconds: Time in seconds
    
    Returns:
        Formatted timestamp string (mm:ss)
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

