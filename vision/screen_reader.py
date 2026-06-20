import os
import sys
import pyautogui
from PIL import Image
from google import genai
from config import GEMINI_API_KEY

def capture_and_analyze_screen():
    """
    Captures a screenshot of the user's screen and uses Gemini Vision
    to analyze it and describe what is visible and what to do next.
    """
    try:
        # Save temporary screenshot
        temp_path = "temp_screenshot.png"
        print("Capturing screen...")
        screenshot = pyautogui.screenshot()
        screenshot.save(temp_path)
        
        # Load image via PIL
        img = Image.open(temp_path)
        
        # Initialize Gemini Client
        api_key = GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return "Gemini API key is not configured. Please set GEMINI_API_KEY."
            
        client = genai.Client(api_key=api_key)
        
        # Prepare prompt
        prompt = "What is on this screen and what should I do next?"
        print("Sending screen image to Gemini Vision...")
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[img, prompt]
        )
        
        # Clean up temporary screenshot
        try:
            os.remove(temp_path)
        except Exception:
            pass
            
        return response.text
        
    except Exception as e:
        print(f"Error in screen reader analysis: {e}", file=sys.stderr)
        return f"Failed to analyze screen due to an error: {e}"
