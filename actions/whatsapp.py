import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from voice.text_to_speech import speak

# Define persistent user profile directory
PROFILE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "whatsapp_selenium_profile")

class WhatsAppAutomator:
    def __init__(self):
        self.driver = None

    def start_driver(self):
        """Initializes Chrome driver with persistent profile."""
        if self.driver:
            return True
        try:
            options = webdriver.ChromeOptions()
            options.add_argument(f"user-data-dir={PROFILE_DIR}")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            # Don't run headless because the user needs to scan the QR code initially
            options.add_argument("--start-maximized")
            
            # Disable window tracking for cleaner run
            options.add_experimental_option("excludeSwitches", ["enable-logging"])

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            return True
        except Exception as e:
            print(f"Error starting Selenium Chrome driver: {e}", file=sys.stderr)
            return False

    def send_message(self, contact_name, message_text):
        """Automates sending a WhatsApp Web message."""
        if not self.start_driver():
            return "Failed to open browser driver"

        try:
            self.driver.get("https://web.whatsapp.com")
            
            # Wait for either chat list or QR code page to load
            print("Waiting for WhatsApp Web to load...")
            # Xpath representing the main pane after login
            main_pane_xpath = "//div[@id='pane-side']"
            qr_code_xpath = "//canvas[@aria-label='Scan me!']"

            wait = WebDriverWait(self.driver, 45)
            
            try:
                # Check if QR code is visible
                wait.until(
                    EC.presence_of_element_located((By.XPATH, f"{main_pane_xpath} | {qr_code_xpath}"))
                )
                
                # If QR code canvas is found, notify the user to scan it
                qr_elements = self.driver.find_elements(By.XPATH, qr_code_xpath)
                if qr_elements and qr_elements[0].is_displayed():
                    speak("Please scan the QR code on your screen to log in to WhatsApp Web.")
                    # Wait for login to complete (chat pane appears)
                    WebDriverWait(self.driver, 120).until(
                        EC.presence_of_element_located((By.XPATH, main_pane_xpath))
                    )
                    speak("Login successful.")
            except Exception as e:
                return "WhatsApp Web loading timed out. Please check your network connection."

            print(f"Searching for contact: {contact_name}")
            # Locate search input box
            search_box_xpath = "//div[@contenteditable='true'][@data-tab='3']"
            search_box = wait.until(
                EC.element_to_be_clickable((By.XPATH, search_box_xpath))
            )
            
            search_box.click()
            search_box.clear()
            
            # Send keys one by one or directly
            search_box.send_keys(contact_name)
            time.sleep(2)
            search_box.send_keys(Keys.ENTER)
            time.sleep(2)

            # Locate chat text input box
            message_box_xpath = "//footer//div[@contenteditable='true'][@data-tab='10']"
            try:
                message_box = wait.until(
                    EC.element_to_be_clickable((By.XPATH, message_box_xpath))
                )
            except Exception:
                # If message box is not found, the contact search might have failed
                return f"Contact '{contact_name}' not found on WhatsApp."

            # Write message and send
            message_box.click()
            message_box.send_keys(message_text)
            time.sleep(1)
            message_box.send_keys(Keys.ENTER)
            
            # Wait for message sending checkmark to confirm delivery
            time.sleep(3)
            
            return f"Message sent to {contact_name} successfully."
            
        except Exception as e:
            return f"An error occurred during WhatsApp automation: {e}"
        finally:
            # We don't close the browser immediately to let the user see it sent and keep session
            pass

def ask_user_confirmation():
    """Asks the user for confirmation (handles both voice and text depending on availability)."""
    speak("Do you want me to send this message?")
    
    # Try importing voice modules to see if voice is available
    try:
        from voice.speech_to_text import listen_for_speech
        # If voice imports succeed, we can try to listen
        print("Waiting for voice confirmation...")
        user_response = listen_for_speech(timeout=5, phrase_time_limit=4)
        if user_response:
            response_clean = user_response.strip().lower()
            if any(yes in response_clean for yes in ["yes", "yeah", "yep", "sure", "send", "okay", "ok"]):
                return True
            if any(no in response_clean for no in ["no", "nope", "cancel", "don't"]):
                return False
    except Exception:
        pass
        
    # Fallback to console input confirmation
    try:
        console_input = input("Confirm send (yes/no): ").strip().lower()
        return console_input in ["yes", "y", "yeah", "ok", "send"]
    except Exception:
        return False

def handle_automated_whatsapp(command):
    """Entry point routed from the command router."""
    target = command.get("target", "")
    content = command.get("content", "")
    
    if not target or not content:
        return "WhatsApp recipient or message content unspecified"
        
    # Ask for confirmation before automating
    if not ask_user_confirmation():
        return "WhatsApp message sending cancelled."
        
    speak(f"Automating WhatsApp to send message to {target}.")
    automator = WhatsAppAutomator()
    result = automator.send_message(target, content)
    return result
