# Patch Notes Writer (LLM App)

A desktop application that converts bullet-point updates into structured,
professional patch notes using Google's Gemini Flash model. It features tool use, where real date and real time is shown every time a user generates a new note. This helps a user track their notes that are automatically saved to 'patch_notes.md'. A user can also navigate to the 'View Saved Notes' page where it shows all the patch notes a user typed into the input box. 

## Features
- GUI built with Tkinter (Apple Notes-inspired UI)
- LLM-powered patch note generation
- Versioning system (semantic + date-based)
- Safety guardrails (prompt injection detection, length limits)
- Automated telemetry logging (telemetry.log)
- Test suite (tests.json)
- Enhancement: TOOL-USE (real date and real time shown)
- Saved Notes page showing the users previous notes

## Installation

### 1. Clone repository
git clone \<your-repo-url\>

### 2. Install dependencies
pip install -r requirements.txt

### 3. Add your API key
Create a `.env` file (not included):
GEMINI_API_KEY=YOUR_KEY

### 4. Run the app
python3 app.py

## Notes
- `.env.example` shows expected format.
- `.env` must **not** be committed.
- To view mp4 video, press 'view raw' and it will download it to your computer

