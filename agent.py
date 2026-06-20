from google import genai
from config import GEMINI_API_KEY, SYSTEM_PROMPT
from memory.memory_manager import get_relevant_memory_context

client = genai.Client(api_key=GEMINI_API_KEY)

def get_command(user_input):
    # Retrieve relevant memory context based on the user's instruction keywords
    memory_context = get_relevant_memory_context(user_input)
    
    # Construct contents list combining system prompt, memory context, and user input
    contents = [SYSTEM_PROMPT]
    if memory_context:
        contents.append(memory_context)
    contents.append(user_input)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents
    )

    return response.text
