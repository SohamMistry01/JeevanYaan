import os
import pandas as pd
from datetime import datetime

LOG_FILE = "tool_usage_log.csv"

def log_response_metadata(metadata, tool_name):
    """
    Extracts usage details from the response metadata and appends it to a CSV file.
    """
    if not metadata:
        return

    try:
        # Extract the nested token usage dictionary
        token_usage = metadata.get("token_usage", {})
        completion_details = token_usage.get("completion_tokens_details", {})

        # Prepare the data row
        data = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "model_name": metadata.get("model_name", "unknown"),
            "prompt_tokens": token_usage.get("prompt_tokens", 0),
            "completion_tokens": token_usage.get("completion_tokens", 0),
            "reasoning_tokens": completion_details.get("reasoning_tokens", 0),
            "total_tokens": token_usage.get("total_tokens", 0),
            "prompt_time": token_usage.get("prompt_time", 0.0),
            "completion_time": token_usage.get("completion_time", 0.0),
            "queue_time": token_usage.get("queue_time", 0.0),
            "total_time": token_usage.get("total_time", 0.0),
        }

        df = pd.DataFrame([data])
        
        # Check if file exists to determine if we need to write the header
        header = not os.path.exists(LOG_FILE)
        
        # Append to CSV
        df.to_csv(LOG_FILE, mode='a', header=header, index=False)
        
    except Exception as e:
        print(f"Error logging metadata for {tool_name}: {e}")