# Patch Notes Writer (LLM App)

A desktop application that converts bullet-point updates into structured,
professional patch notes using Google's Gemini Flash model. It features tool use, where real date and real time is shown every time a user generates a new note. This helps a user track their notes that are automatically saved to `patch_notes.md`. A user can also navigate to the 'View Saved Notes' page where it shows all the patch notes a user typed into the input box. 

## Features
- GUI built with Tkinter (Apple Notes-inspired UI)
- LLM-powered patch note generation
- Versioning system (semantic + date-based)
- Safety guardrails (prompt injection detection, length limits)
- Automated telemetry logging (`telemetry.log`)
- Test suite (`tests.json`)
- Enhancement: TOOL-USE (real date and real time shown)
- Saved Notes page showing the users previous notes

## Chosen Enhancement
My chosen enchancement is **tool use**. When the model needs accurate time and date, it calls a tool instead of using a local date. My model print has a tool-call token `[TOOL] fetch_time`, my backend detects this, calls `external_api.py,` which triggers either the WorldTimeAPI or TimeAPI, and then sends the real time datetime to the model. Finally, the model printsout the real date and real 24 hour time in the header. 

In `external_api.py`: 

```python
def fetch_current_time():
    try:
        r = requests.get("https://worldtimeapi.org/api/timezone/America/Toronto", timeout=4)
        
    try:
        r = requests.get("https://timeapi.io/api/Time/current/zone?timeZone=America/Toronto", timeout=4)
```
These lines calls the external APIs to fetch live date and time. 

In `app.py`:

```python
if text.strip() == "[TOOL] fetch_time" or "[TOOL] fetch_time" in text:
        api_time = fetch_current_time()
```
This line is where I detect the tool call and fetch the real time. 

```python 
real_date_str = real_dt.strftime("%B %d, %Y") # real date in "Month Day, Year"
real_time_str = real_dt.strftime("%I:%M:%S %p") # real time in 12-hour AM/PM
```
This line is where I format into 12-hour time and pass it back to the model. 

## Running eval.py
To print out the passing rate of the app, run `python3 eval.py.` Sometimes the passing rate is 15/18 or 16/18 and sometime it can be 2/18 or 4/18. 

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

## Google API Key 

1. Go to 'https://aistudio.google.com/welcome'
2. Use your personal email to login 
3. Press 'View API Keys' 
4. Press 'Create API Key'
5. Name your key and select 'Default Gemini Project' 
6. Select create key

## Notes
- `.env.example` shows expected format.
- `.env` must **not** be committed.
- To view mp4 video, press 'view raw' and it will download it to your computer

