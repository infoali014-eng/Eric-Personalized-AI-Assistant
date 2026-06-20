# Eric AI - Local Voice & Desktop Assistant

Eric AI is a real-time voice-controlled local desktop assistant that converts spoken/text instructions into structured executable commands using Gemini 2.5 and executes them on your Windows PC.

## Project Structure (Clean Architecture)

```text
Eric-AI/
├── main.py              # Application entrypoint (Runs voice mode by default; fallback to text mode)
├── agent.py             # Interfaces with Gemini API (injects relevant memory context)
├── config.py            # Holds SYSTEM_PROMPT (strict JSON mode) and settings
├── .env                 # API Key credentials (ignored by git)
│
├── core/
│   ├── assistant.py      # State machine (Idle/Active modes, inactivity timeout, voice loops, memory intercept)
│   └── command_router.py # Decodes JSON commands and routes to appropriate execution handler
│
├── voice/
│   ├── speech_to_text.py # Manages microphone capture and Google speech recognition API
│   ├── text_to_speech.py # Handles TTS engine verbal responses (pyttsx3)
│   └── wake_word.py      # Listens continuously for wake word detection ("Hey Eric")
│
├── memory/
│   ├── memory_db.py      # SQLite database schema and insertions/queries
│   └── memory_manager.py # Handles command interception and context retrieval keyword matching
│
├── utils/
│   └── json_cleaner.py   # Sanitizes and extracts pure JSON block outputs from the LLM
│
└── actions/
    ├── app_control.py    # OPEN_APP, CLOSE_APP, SEARCH_WEB, WHATSAPP_MESSAGE
    ├── system_control.py # SYSTEM_LOCK, SYSTEM_SHUTDOWN, SYSTEM_RESTART
    └── file_manager.py   # CREATE_FILE, DELETE_FILE, CREATE_FOLDER, DELETE_FOLDER, RENAME_FILE
```

## Setup & Installation

1. Make sure you have Python 3.10+ installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Voice mode requires `PyAudio`. If installing it fails, please install Visual Studio Build Tools, or download a pre-compiled `.whl` wheel for your Python version, then run:
   ```bash
   pip install PyAudio
   ```
4. Set your `GEMINI_API_KEY` in the `.env` file or environment variables:
   ```env
   GEMINI_API_KEY=your_key_here
   ```

## Usage

### Voice Mode (Default)
Run the assistant:
```bash
python main.py
```
- The assistant starts in **IDLE** mode.
- Speak "**Hey Eric**" or "**Eric**" to wake it.
- Once active, say any instruction (e.g. "open chrome", "lock laptop").
- If inactive for 15 seconds, it will return to sleep mode automatically.

### Text Mode Fallback
If you don't have a microphone or PyAudio is not installed, the app automatically falls back to interactive text mode. You can also force text mode:
```bash
python main.py --text
```

## Memory System

Eric AI has a built-in SQLite persistent memory system that stores user-specific preferences, notes, and contacts.

- **Remembering Information**: Simply say or type `"remember that [something]"` (e.g. `"remember that my favorite browser is Chrome"` or `"remember that Ali is my friend"`). The assistant will store this permanently.
- **Checking Stored Memories**: Ask `"what do you remember about me"`.
- **Dynamic Context Injection**: Before query execution, Eric AI analyzes your instructions, retrieves relevant items from memory, and injects them into the Gemini model prompt to personalize actions (e.g. preferring a specific browser or name). Memory is only sent if relevant keywords match.
