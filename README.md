# Patch Notes Writer (LLM App)

    A desktop application that converts bullet-point updates into structured,
professional patch notes using Google's Gemini Flash model. It features tool use, where real date and real time is shown every time a user generates a new notes. This helps a user track their notes that are automatically saved to 'patch_notes.md'
---
## Features
- GUI built with Tkinter (Apple Notes-inspired UI)
- LLM-powered patch note generation
- Versioning system (semantic + date-based)
- Safety guardrails (prompt injection detection, length limits)
- Automated telemetry logging
- Test suite (tests.json)
- Enhancement: TOOL-USE (real date and real time shown)
---
## Installation

### 1. Clone repository
git clone <your-repo-url>

### 2. Install dependencies
pip install -r requirements.txt

### 3. Add your API key
Create a `.env` file (not included):
GEMINI_API_KEY=YOUR_KEY

### 4. Run the app
python3 app.py
---
## Notes
- `.env.example` shows expected format.
- `.env` must **not** be committed.
