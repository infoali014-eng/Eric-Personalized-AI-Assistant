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
│   ├── assistant.py          # State machine (Idle/Active modes, inactivity timeout, voice loops)
│   ├── background_agent.py   # Daemon-style background manager running Tkinter main loop and async command threads
│   ├── command_interceptor.py# Global gatekeeper normalizing input and checking intercept triggers
│   ├── command_router.py     # Decodes JSON commands and routes them through the Plugin Manager
│   ├── executor.py           # Reliable executor (handles dangerous gates, logging, and retry-on-fail)
│   ├── hotword_engine.py     # Background streaming wake word engine using listen_in_background
│   ├── task_optimizer.py     # Plan optimizer (merges redundant actions, simplifies directories)
│   ├── task_planner.py       # Multi-step task planner (sends prompt to Gemini, auto-learns usage patterns)
│   └── workflow_engine.py    # Auto-workflow engine (loads, executes, and auto-detects habits)
│
├── voice/
│   ├── speech_to_text.py # Manages microphone capture and Google speech recognition API
│   ├── text_to_speech.py # Handles TTS engine verbal responses (pyttsx3)
│   └── wake_word.py      # Listens continuously for wake word detection ("Hey Eric")
│
├── vision/
│   ├── screen_reader.py      # Captures screen image and sends to Gemini Vision API (standard mode)
│   └── smart_screen_agent.py # Interactive screen assist agent (supports click automation)
│
├── ui/
│   ├── animations.py    # Canvas animations for orb states (Idle pulsing, Listening waves, Processing arcs)
│   ├── floating_orb.py  # Transparent, draggable frameless topmost orb bubble overlay
│   └── main_window.py   # Sleek dark-themed Jarvis panel control dashboard
│
├── memory/
│   ├── memory_db.py      # SQLite database schema and insertions/queries
│   └── memory_manager.py # Handles command interception and context retrieval keyword matching
│
├── plugins/
│   ├── base_plugin.py            # Base abstract class for plugins
│   ├── plugin_manager.py         # Dynamic importer and router of registered plugin capabilities
│   ├── registry.json             # Map list of registered plugin modules
│   ├── app_control_plugin.py     # Handles OPEN_APP, CLOSE_APP, SEARCH_WEB
│   ├── file_manager_plugin.py    # Handles CREATE_FILE, DELETE_FILE, CREATE_FOLDER, DELETE_FOLDER, RENAME_FILE
│   ├── system_control_plugin.py  # Handles SYSTEM_LOCK, SYSTEM_SHUTDOWN, SYSTEM_RESTART
│   └── whatsapp_plugin.py        # Handles WHATSAPP_MESSAGE automated messages
│
├── utils/
│   └── json_cleaner.py   # Sanitizes and extracts pure JSON block outputs from the LLM
│
└── actions/              # Legacy standalone handlers (plugins route through here)
    ├── app_control.py
    ├── system_control.py
    ├── file_manager.py
    └── whatsapp.py
```

## Setup & Installation

1. Make sure you have Python 3.10+ installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Voice mode and wake-word streaming require `PyAudio`. If installing it fails, please install Visual Studio Build Tools, or download a pre-compiled `.whl` wheel for your Python version, then run:
   ```bash
   pip install PyAudio
   ```
4. Set your `GEMINI_API_KEY` in the `.env` file or environment variables:
   ```env
   GEMINI_API_KEY=your_key_here
   ```

## Usage

### Desktop GUI Mode (Default)
Run the assistant dashboard & orb:
```bash
python main.py
```
- A **glowing floating orb** (Jarvis bubble) will appear in the bottom right corner of your screen.
- You can **drag the orb** to position it anywhere. It stays topmost above all other applications.
- A **sleek dark control dashboard** will open, showing console logs and execution plans. You can hide or show it.
- **Double click / Click the orb** or say `"Hey Eric"` to wake the assistant and start speaking.
- You can also type manual commands in the input box at the bottom of the dashboard panel.

### CLI Text Mode Fallback
If you want to run the assistant directly in your terminal console:
```bash
python main.py --text
```

### CLI Voice Mode
To run the terminal voice loop without the graphical interface:
```bash
python main.py --voice-cli
```

## Desktop UI & Background Daemon

Eric AI operates a lightweight, responsive desktop client:
- **Orb Animation States**: Pulsing cyan (Idle), concentric pink waves (Listening), rotating gold/blue arcs (Processing).
- **Asynchronous Execution Threading**: Voice listening and task planning run in background threads, ensuring the desktop UI remains fluid (60 FPS) and never freezes.
- **Hotword Engine**: Continuous streaming listener (`listen_in_background`) runs on a background microphone feed to wake the assistant instantly within <300ms.

## Task Planning & Optimization System

Eric AI uses a multi-step task planning engine that splits complex user instructions into sequential execution steps.
- **Example**: `"open chrome and search AI news and send summary to Ali on WhatsApp"`
- **Plan Generation**: Gemini parses the instruction and returns a structured list of steps.
- **Intelligent Optimizer**: Before execution, the plan passes through `core/task_optimizer.py`. It automatically merges redundant steps (e.g. combining opening Chrome and performing a web search into a single action, or skipping separate folder creations if the file manager will auto-create the path anyway).
- **Execution Flow**: Steps are executed sequentially. If any step fails, the planner halts execution to prevent runaway commands.

## Dynamic Plugin Architecture

All assistant actions are modularized as plugins under `/plugins/`:
- **Plugin Registration**: Declared dynamically in `/plugins/registry.json`.
- **Dynamic Importing**: The `PluginManager` reads the registry, dynamically imports class definitions using Python's `importlib`, and maps capability actions.
- **Modularity**: Adding new actions or capabilities to Eric AI is as simple as subclassing `BasePlugin` and registering it in the JSON file. No direct execution happens outside this system.

## Auto-Workflow Engine

Eric AI actively monitors your command execution history to automate repeated tasks:
- **Pattern Learning**: The workflow engine analyzes database action logs. If a specific chain of 2 or 3 actions occurs repeatedly (e.g. searching the web and sending the summary), it compiles them into a workflow.
- **Local Persistence**: Automatically creates reusable workflow JSON configurations in the `/workflows/` directory.
- **User Prompt Notification**: Announces new workflows when auto-learned: `"I noticed you often perform this sequence. I have automated it as [workflow name]."`
- **Execution Command**: You can run workflows on demand by saying or typing `"run my [workflow name] workflow"`.

## Reliable Executor & Logging

All commands are processed by a unified executor (`core/executor.py`) to guarantee production-level safety and reliability:
- **Retry System**: If a command fails due to a transient exception, it is automatically retried once.
- **Logs**: Every attempt and outcome is logged with timestamps in `eric_execution.log`.
- **Safe Mode**: Potentially dangerous commands (such as `SYSTEM_SHUTDOWN`, `SYSTEM_RESTART`, `DELETE_FILE`, `DELETE_FOLDER`, and `WHATSAPP_MESSAGE`) require explicit voice or console confirmation before execution.

## Memory System

Eric AI has a built-in SQLite persistent memory system that stores user-specific preferences, notes, and contacts.
- **Remembering Information**: Simply say or type `"remember that [something]"` (e.g. `"remember that my favorite browser is Chrome"` or `"remember that Ali is my friend"`). The assistant will store this permanently.
- **Checking Stored Memories**: Ask `"what do you remember about me"`.
- **Dynamic Context Injection**: Relevant memories are loaded and injected before task planning to customize actions.
- **Auto-Learning/Usage Patterns**: Eric AI learns preferences based on usage history. For example, opening Chrome 3 times automatically logs a user preference for Chrome.

## WhatsApp Automation

Eric AI features an automated WhatsApp messaging handler using Selenium.
- **Command Format**: Say or type `"send message to [contact]: [message]"` (e.g., `"send message to Ali: I am coming"`).
- **Session Persistence**: Saves your browser session data in a local profile (`whatsapp_selenium_profile/`). Once logged in by scanning the QR code, future attempts navigate directly.

## Screen Understanding & Smart Assist (Vision)

Eric AI has screen-awareness capabilities using Gemini Vision API.
- **Command Format**: Say or type `"look at screen"` for standard description, or `"help me fix this"` / `"assist mode"` for interactive help.
- **Interactive Assist**: Eric AI captures a screenshot, analyzes it, suggests next steps, and can perform **autonomous clicks** on buttons or error popups if its confidence score exceeds a threshold (0.8).
- **Safety**: Screenshot capture only triggers on explicit request. No continuous monitoring or passive recording occurs.
