import json
import re

def clean_and_parse_json(raw_text):
    """
    Cleans the raw text to extract a JSON block and parses it.
    Supports removing markdown blocks, backticks, and any text surrounding the JSON.
    """
    if not raw_text:
        raise ValueError("Empty response received")
    
    # Strip whitespace
    text = raw_text.strip()
    
    # Try parsing directly
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
        
    # Regex to find anything between the first '{' and the last '}'
    match = re.search(r'(\{.*\})', text, re.DOTALL)
    if match:
        json_candidate = match.group(1)
        try:
            return json.loads(json_candidate)
        except json.JSONDecodeError:
            # Try cleaning up common issues like markdown code block wraps (```json ... ```)
            cleaned = json_candidate.replace("```json", "").replace("```", "").strip()
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse cleaned JSON block: {e}")
                
    raise ValueError("No JSON object found in the response")
