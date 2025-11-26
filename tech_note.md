# Technical Note – Patch Note Writer (Assignment 2)

## 1. Overview

PatchNoteRM-2.0 is a desktop application that uses an LLM (Gemini Flash Latest) to transform raw developer bullet points into structured, professional-grade patch notes. The system includes prompt safety mechanisms, category classification, semantic versioning, RAG-style seed data, telemetry logging, and a Tkinter graphical interface.

This design follows the assignment requirements while simulating a realistic internal developer tool that could exist inside a modern software company.

---

## 2. Architecture Summary

The application consists of the following modules:

### `app.py`
- Tkinter GUI for interaction.
- Connects user input to the LLM.
- Controls the generation pipeline.
- Appends results to `patch_notes.md`.

### `guardrails.py`
- Houses the system prompt.
- Implements:
  - Prompt injection blocker
  - Length restrictions
  - Safety gates
- Enforces formatting + structure rules.

### `tools.py`
- Implements version bump engine (semantic + date-based).
- Provides utilities reused by the main app.

### `telemetry.py`
- Logs:
  - timestamp
  - latency of LLM calls
  - token usage

### `tests.json`
- Contains automated evaluation samples required by the assignment.
- Ensures correct:
  - category detection,
  - prompt injection defense,
  - refusal behavior,
  - version handling.

---

## 3. LLM Prompt Design

The core of the system is a structured system prompt that instructs the LLM on:

- Patch note formatting  
- Release category classification  
- Severity detection  
- Version bump logic  
- Safety constraints  
- Tone consistency  

The format follows a real-world release manager template with sections:
- Summary  
- Breaking Changes  
- Security  
- Performance  
- Stability  
- UI/UX  
- QoL  
- Infrastructure  

This structure ensures consistency across all inputs.

---

## 4. Guardrails & Safety

The system rejects unsafe inputs using:
- Substring detection for jailbreak-like phrases
- Length restriction to prevent model overload
- Fallback protection in the UI

If a user attempts prompt injection, the app outputs:


---

## 5. Versioning Strategy

The versioning system uses:
- **YYYY.MM.DD.X** format
- Automatic increment when multiple patch notes are generated on the same day
- Semantic bump driven by categories:
  - Breaking Changes → Major bump
  - Security fix → Major bump
  - New features / performance → Minor
  - Bugs/UI → Patch

---

## 6. Telemetry

Each LLM call logs:


This simulates observability in real deployment pipelines.

---

## 7. GUI Design

Built using Tkinter with:
- Apple Notes-inspired layout
- Visible cursor
- High-contrast buttons
- Clean font styling

The UI runs locally and does not expose the API key.

---

## 8. Testing

The app uses `tests.json` which contains 15 evaluation cases verifying:
- Category mapping
- Safety behavior
- Refusals
- Formatting rules

These tests ensure the LLM consistently meets the required behaviors.

---

## 9. Conclusion

This solution demonstrates:
- Strong LLM design
- Safety-aware prompt engineering
- Realistic developer tooling
- GUI integration
- Logging + testing practices

It fulfills all assignment requirements while maintaining robust engineering quality.
