import re
from memory.memory_db import insert_memory, get_all_memories, search_memories

# Short-term session memory (in-memory dict)
_session_memory = {}

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "else", "when", 
    "where", "why", "how", "what", "who", "whom", "this", "that", "these",
    "those", "is", "am", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "to", "from", "in", "on", 
    "at", "by", "for", "with", "about", "against", "of", "my", "your",
    "his", "her", "its", "our", "their", "me", "you", "him", "us", "them"
}

def save_short_term(key, value):
    """Saves a key-value pair to the session-only memory."""
    _session_memory[key] = value

def get_short_term(key):
    """Retrieves a value from session-only memory."""
    return _session_memory.get(key)

def process_memory_command(user_input):
    """
    Checks if the input is a request to remember something or retrieve memory.
    Returns a success message if it's a memory command, or None if it's a standard command.
    """
    user_input_lower = user_input.lower().strip()
    
    # Check for "remember that X" command
    match = re.match(r"^remember\s+that\s+(.+)$", user_input_lower)
    if match:
        content = match.group(1).strip()
        # Classify category based on content keywords
        category = "note"
        if any(kw in content for kw in ["friend", "ali", "ahmad", "contact", "call"]):
            category = "contact"
        elif any(kw in content for kw in ["prefer", "default", "like", "favorite"]):
            category = "preference"
        elif any(kw in content for kw in ["command", "run"]):
            category = "command"
            
        success = insert_memory(category, content)
        if success:
            return f"I will remember that {content}"
        else:
            return "Failed to save that to my memory"
            
    # Check for "what do you remember about me"
    if "what do you remember" in user_input_lower:
        memories = get_all_memories()
        if not memories:
            return "I don't remember anything about you yet."
            
        output = "Here is what I remember about you:\n"
        for cat, content, _ in memories:
            output += f"- [{cat.capitalize()}] {content}\n"
        return output
        
    return None

def get_relevant_memory_context(user_input):
    """
    Extracts keywords from user input, queries the database for matching entries,
    and returns a formatted context string, or an empty string if no relevant memories exist.
    """
    # Clean input and extract keywords
    words = re.findall(r"\b\w+\b", user_input.lower())
    keywords = [w for w in words if w not in STOP_WORDS and len(w) > 2]
    
    if not keywords:
        return ""
        
    matches = search_memories(keywords)
    if not matches:
        return ""
        
    # Build context string
    context_lines = []
    for cat, content in matches:
        context_lines.append(f"User {cat}: {content}")
        
    return "\n[Relevant Memories]\n" + "\n".join(context_lines) + "\n"
