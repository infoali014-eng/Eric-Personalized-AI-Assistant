# Eric AI - Local Desktop Assistant

Eric AI is a local desktop assistant that converts natural language user instructions into structured executable JSON commands and executes them on your Windows PC.

## Supported Actions

1. **OPEN_APP**: Opens a specified application (e.g., "open chrome" or "start notepad").
2. **CLOSE_APP**: Closes an active application (e.g., "close chrome").
3. **CREATE_FILE**: Creates a new file at a specified path with optional content.
4. **DELETE_FILE**: Deletes a file at a specified path.
5. **CREATE_FOLDER**: Creates a new directory.
6. **DELETE_FOLDER**: Recursively deletes a directory.
7. **RENAME_FILE**: Renames or moves a file.
8. **SYSTEM_LOCK**: Locks the Windows operating system.
9. **SYSTEM_SHUTDOWN**: Shuts down the PC.
10. **SYSTEM_RESTART**: Restarts the PC.
11. **SEARCH_WEB**: Performs a web search using your default web browser.
12. **WHATSAPP_MESSAGE**: Prepares and opens a WhatsApp message via WhatsApp Web.

## Action JSON Schema

The actions follow this strict JSON format:

```json
{
  "action": "ACTION_NAME",
  "target": "optional target app/file/person",
  "content": "optional message or file content",
  "path": "optional file path"
}
```

## Setup & Installation

1. Make sure you have Python 3.10+ installed.
2. Clone the repository.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set your `GEMINI_API_KEY` environment variable:
   ```cmd
   set GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Usage

### Interactive Mode

To run the interactive loop:
```bash
python eric_ai.py
```

### CLI Mode

To parse and execute a single command directly from the terminal:
```bash
python eric_ai.py open chrome
```
```bash
python eric_ai.py create file test.txt with content Hello World
```
