import os
import sys
import time
import pyautogui
from PIL import Image
from google import genai
from google.genai import types
from config import GEMINI_API_KEY
from voice.text_to_speech import speak
from utils.json_cleaner import clean_and_parse_json

# Confidence threshold for autonomous clicks
CONFIDENCE_THRESHOLD = 0.8

def capture_and_assist():
    """
    Captures the screen, sends it to Gemini Vision to analyze context (errors, buttons, apps),
    returns suggestions, and optionally executes high-confidence clicks autonomously.
    """
    try:
        temp_path = "assist_screenshot.png"
        print("Capturing screen for Assist Mode...")
        screenshot = pyautogui.screenshot()
        screenshot.save(temp_path)
        
        img = Image.open(temp_path)
        
        api_key = GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return "Gemini API key is not configured. Please set GEMINI_API_KEY."
            
        client = genai.Client(api_key=api_key)
        
        # Screen resolution info to guide coordinates
        width, height = pyautogui.size()
        
        prompt = f"""You are Eric AI's Visual Assist Agent. Analyze this screen capture.
Current screen resolution: {width}x{height} pixels.

Determine:
1. What is currently on the screen (applications, errors, text).
2. What is the most appropriate next step to help the user.
3. If there is a clear next step (e.g., clicking 'OK' on an error dialog, clicking a close button, opening a specific menu), provide the approximate (x, y) coordinates of where to click in the range [0 to {width}] for X and [0 to {height}] for Y.
4. Estimate your confidence level (0.0 to 1.0) in the action and the coordinates.

Return ONLY a strict JSON object with this format (no markdown, no ``` backticks, no extra text):
{{
  "analysis": "clear description of what is on screen",
  "next_step": "suggested instruction or explanation",
  "confidence": 0.95,
  "click_position": {{"x": 500, "y": 400}}
}}
If no action or click is needed, set click_position to null.
"""

        print("Analyzing screen with Gemini Vision...")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[img, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        # Clean up screenshot file
        try:
            os.remove(temp_path)
        except Exception:
            pass
            
        result_text = response.text.strip()
        print(f"Gemini Assist Output: {result_text}")
        
        data = clean_and_parse_json(result_text)
        analysis = data.get("analysis", "")
        next_step = data.get("next_step", "")
        confidence = data.get("confidence", 0.0)
        click_pos = data.get("click_position")
        
        # Speak/print the analysis and advice
        speak(f"Screen Analysis: {analysis}")
        speak(f"Suggested Next Step: {next_step}")
        
        # Autonomous action click
        if click_pos and isinstance(click_pos, dict):
            cx = click_pos.get("x")
            cy = click_pos.get("y")
            if cx is not None and cy is not None:
                if confidence >= CONFIDENCE_THRESHOLD:
                    speak(f"Performing automatic click at position {cx}, {cy} (Confidence: {confidence})")
                    # Smooth mouse move and click
                    pyautogui.moveTo(cx, cy, duration=1.0)
                    pyautogui.click()
                else:
                    speak(f"I found a button at {cx}, {cy}, but my confidence of {confidence} is below the threshold of {CONFIDENCE_THRESHOLD} for auto action.")
                    
        return f"Assist completed: {next_step}"
        
    except Exception as e:
        print(f"Error in visual assist mode: {e}", file=sys.stderr)
        return f"Failed to complete assist mode: {e}"
