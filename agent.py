from google import genai
from config import GEMINI_API_KEY, SYSTEM_PROMPT

client = genai.Client(api_key=GEMINI_API_KEY)

def get_command(user_input):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            SYSTEM_PROMPT,
            user_input
        ]
    )

    return response.text
