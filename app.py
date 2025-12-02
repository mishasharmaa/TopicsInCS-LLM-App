import tkinter as tk
from tkinter import scrolledtext
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time
from datetime import datetime   # <-- needed for real 12-hour time

from guardrails import system_prompt, is_prompt_injection, length_guard
from tools import get_version_and_date
from telemetry import log_request
from external_api import fetch_current_time  # <-- TOOL USE

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Modern model
model = genai.GenerativeModel("gemini-flash-latest")


# ---------------------------------------
# SAFE TEXT EXTRACTOR FOR GEMINI FLASH
# ---------------------------------------
def safe_extract_text(response):
    """
    Extracts text safely from Gemini Flash responses, even when
    no .text part exists (tool call, safety block, etc.).
    """
    # Try simple access
    try:
        return response.text.strip()
    except Exception:
        pass

    # Try parsing candidates manually
    try:
        if hasattr(response, "candidates"):
            parts = []
            for c in response.candidates:
                if hasattr(c, "content") and c.content:
                    for p in c.content.parts:
                        if hasattr(p, "text"):
                            parts.append(p.text)
            if parts:
                return "\n".join(parts).strip()
    except:
        pass

    return ""  # Fallback when no text at all


# ---------------------------------------
# PATCH-NOTE GENERATION
# ---------------------------------------
def generate_patch_notes(user_text, output_box):
    if not length_guard(user_text):
        output_box.insert(tk.END, "Error: Input too long.\n")
        return

    if is_prompt_injection(user_text):
        output_box.insert(tk.END, "Request blocked: unsafe instruction.\n")
        return

    version, date = get_version_and_date()

    full_prompt = (
        system_prompt()
        + f"\nUser Bullets:\n{user_text}\n"
        + f"(If needed, you may call the time tool.)\n"
        + f"Fallback Local Date: {date}\n"
        + f"Version Base: {version}\n"
    )

    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, "[Working...] contacting Gemini Flash…\n")
    output_box.update()

    start = time.time()
    response = model.generate_content(full_prompt)
    latency = time.time() - start

    # SAFELY extract model text
    text = safe_extract_text(response)

    # ---------------------------------------
    # TOOL CALL CHECK
    # ---------------------------------------
    if text.strip() == "[TOOL] fetch_time" or "[TOOL] fetch_time" in text:

        api_time = fetch_current_time()

        # Log tool use
        log_request("tool", latency, response.usage_metadata.total_token_count)

        if api_time is None:
            output_box.delete("1.0", tk.END)
            output_box.insert(tk.END, "Tool Error: Could not fetch real datetime.\n")
            return

        # ---------------------------------------------
        # Format REAL date + REAL time (12-hour format)
        # ---------------------------------------------
        try:
            real_dt = datetime.fromisoformat(api_time.replace("Z", "+00:00"))
            real_date_str = real_dt.strftime("%B %d, %Y")
            real_time_str = real_dt.strftime("%I:%M:%S %p")  # 12-hour time
        except Exception:
            real_date_str = api_time
            real_time_str = ""

        # ---------------------------------------------
        # Follow-up prompt once tool result is ready
        # ---------------------------------------------
        followup_prompt = (
            system_prompt()
            + f"\nTool Result Datetime: {api_time}\n"
            + f"Real Date: {real_date_str}\n"
            + f"Real Time: {real_time_str}\n"
            + f"User Bullets:\n{user_text}\n"
        )

        follow_response = model.generate_content(followup_prompt)
        final_text = safe_extract_text(follow_response)

        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, final_text)

        with open("patch_notes.md", "a") as f:
            f.write("\n\n" + final_text)

        return

    # ---------------------------------------
    # NO TOOL → NORMAL FLOW
    # ---------------------------------------
    log_request("none", latency, response.usage_metadata.total_token_count)

    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, text)

    with open("patch_notes.md", "a") as f:
        f.write("\n\n" + text)


# ---------------------------------------
# GUI: UNCHANGED
# ---------------------------------------
def build_gui():
    root = tk.Tk()
    root.title("Patch Notes Writer")
    root.geometry("1200x800")
    root.configure(bg="#F8F8F5")

    # SIDEBAR 
    sidebar = tk.Frame(root, bg="#FFE7A0", width=220)
    sidebar.pack(side="left", fill="y")

    tk.Label(
        sidebar,
        text="Patch Notes",
        font=("Helvetica Neue", 22, "bold"),
        fg="black",
        bg="#FFE7A0"
    ).pack(pady=20)

    tk.Label(
        sidebar,
        text="Enter bullet points\non the right →",
        font=("Helvetica Neue", 13),
        fg="black",
        bg="#FFE7A0"
    ).pack(pady=10)

    # MAIN AREA 
    main = tk.Frame(root, bg="#F8F8F5")
    main.pack(side="right", fill="both", expand=True)

    tk.Label(
        main,
        text="Your Bullet Notes:",
        font=("Helvetica Neue", 17, "bold"),
        fg="black",
        bg="#F8F8F5"
    ).pack(anchor="w", padx=20, pady=(20, 5))

    # Text input box
    input_box = scrolledtext.ScrolledText(
        main,
        width=120, height=10,
        font=("Helvetica Neue", 14),
        bg="white",
        fg="black",
        insertbackground="black",
        borderwidth=2,
        relief="solid"
    )
    input_box.pack(padx=20)

    # Button 
    generate_btn = tk.Button(
        main,
        text="Generate Patch Notes",
        font=("Helvetica Neue", 14, "bold"),
        bg="black",
        fg="black",
        activebackground="#333333",
        activeforeground="white",
        width=28,
        height=2,
        borderwidth=3,
        relief="raised",
        command=lambda: generate_patch_notes(input_box.get("1.0", tk.END), output_box)
    )
    generate_btn.pack(pady=20)

    generate_btn.configure(disabledforeground="#777777")

    tk.Label(
        main,
        text="Generated Output:",
        font=("Helvetica Neue", 17, "bold"),
        fg="black",
        bg="#F8F8F5"
    ).pack(anchor="w", padx=20, pady=(0, 5))

    # Output box
    output_box = scrolledtext.ScrolledText(
        main,
        width=120,
        height=15,
        font=("Helvetica Neue", 14),
        bg="white",
        fg="black",
        insertbackground="black",
        borderwidth=2,
        relief="solid"
    )
    output_box.pack(padx=20, pady=(0, 20))

    root.mainloop()


if __name__ == "__main__":
    build_gui()
