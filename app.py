import tkinter as tk
from tkinter import scrolledtext
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time
from datetime import datetime
from guardrails import system_prompt, is_prompt_injection, length_guard
from tools import get_version_and_date
from telemetry import log_request
from external_api import fetch_current_time

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-flash-latest")


def safe_extract_text(response):
    try:
        return response.text.strip()
    except Exception:
        pass

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

    return ""

def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def show_main_screen(main_frame):
    clear_frame(main_frame)

    tk.Label(
        main_frame,
        text="Your Bullet Notes:",
        font=("Helvetica Neue", 17, "bold"),
        fg="black",
        bg="#F8F8F5"
    ).pack(anchor="w", padx=20, pady=(20, 5))

    input_box = scrolledtext.ScrolledText(
        main_frame,
        width=120, height=10,
        font=("Helvetica Neue", 14),
        bg="#F8F8F5",
        fg="black",
        insertbackground="black",
        borderwidth=2,
        relief="solid"
    )
    input_box.pack(padx=20)

    # Generate Button
    global output_box
    generate_btn = tk.Button(
        main_frame,
        text="Generate Patch Notes",
        font=("Helvetica Neue", 14, "bold"),
        bg="black",
        fg="black",
        activebackground="#000000",
        activeforeground="white",
        width=28,
        height=2,
        borderwidth=3,
        relief="raised",
        command=lambda: generate_patch_notes(input_box.get("1.0", tk.END), output_box)
    )
    generate_btn.pack(pady=20)

    tk.Label(
        main_frame,
        text="Generated Output:",
        font=("Helvetica Neue", 17, "bold"),
        fg="black",
        bg="#F8F8F5"
    ).pack(anchor="w", padx=20, pady=(0, 5))

    output_box = scrolledtext.ScrolledText(
        main_frame,
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

# Saved Notes Page
def show_saved_notes(main_frame):
    clear_frame(main_frame)

    # Link back to the main page
    back_label = tk.Label(
        main_frame,
        text="← Back to Generator",
        font=("Helvetica Neue", 14, "underline", "bold"),
        fg="black",
        bg="#F8F8F5",
        cursor="arrow"
    )
    back_label.pack(anchor="w", padx=20, pady=(20, 5))
    back_label.bind("<Button-1>", lambda e: show_main_screen(main_frame))

    tk.Label(
        main_frame,
        text="Saved Patch Notes",
        font=("Helvetica Neue", 20, "bold"),
        fg="black",
        bg="#F8F8F5"
    ).pack(pady=10)

    notes_box = scrolledtext.ScrolledText(
        main_frame,
        width=120,
        height=30,
        font=("Helvetica Neue", 13),
        bg="white",
        fg="black",
        borderwidth=2,
        relief="solid"
    )
    notes_box.pack(padx=20, pady=10)

    try:
        with open("patch_notes.md", "r") as f:
            notes_box.insert(tk.END, f.read())
    except FileNotFoundError:
        notes_box.insert(tk.END, "No saved notes found.")

    notes_box.config(state="disabled")


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

    text = safe_extract_text(response)

    # TOOL USE
    if text.strip() == "[TOOL] fetch_time" or "[TOOL] fetch_time" in text:

        api_time = fetch_current_time()
        log_request("tool", latency, response.usage_metadata.total_token_count)

        
        output_box.delete("1.0", tk.END)

        if api_time is None:
            output_box.insert(tk.END, "Tool Error: Could not fetch real datetime.\n")
            return

        try:
            real_dt = datetime.fromisoformat(api_time.replace("Z", "+00:00"))
            real_date_str = real_dt.strftime("%B %d, %Y") # real date in "Month Day, Year"
            real_time_str = real_dt.strftime("%I:%M:%S %p") # real time in 12-hour AM/PM
        except Exception:
            real_date_str = api_time
            real_time_str = ""

        followup_prompt = (
            system_prompt()
            + "\nFetched real-world datetime (using tool):\n"
            + f"{real_date_str} — {real_time_str}\n\n"
            + f"User Bullets:\n{user_text}\n"
        )

        follow_response = model.generate_content(followup_prompt)
        final_text = safe_extract_text(follow_response)
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, final_text)

        with open("patch_notes.md", "a") as f:
            f.write("\n\n" + final_text)

        return

    log_request("none", latency, response.usage_metadata.total_token_count)

    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, text)

    with open("patch_notes.md", "a") as f:
        f.write("\n\n" + text)


# Building the GUI 
def build_gui():
    root = tk.Tk()
    root.title("Patch Notes Writer")
    root.geometry("1200x800")
    root.configure(bg="#F8F8F5")
    sidebar = tk.Frame(root, bg="#E308AD", width=220)
    sidebar.pack(side="left", fill="y")

    tk.Label(
        sidebar,
        text="Patch Notes",
        font=("Helvetica Neue", 22, "bold"),
        fg="black",
        bg="#E308AD"
    ).pack(pady=20)

    tk.Label(
        sidebar,
        text="Enter bullet points\non the right →",
        font=("Helvetica Neue", 13),
        fg="black",
        bg="#E308AD"
    ).pack(pady=10)

    
    view_label = tk.Label(
        sidebar,
        text="View Saved Notes",
        font=("Helvetica Neue", 14, "underline", "bold"),
        fg="black",
        bg="#E308AD",
        cursor="arrow"
    )
    view_label.pack(pady=25)
    view_label.bind("<Button-1>", lambda e: show_saved_notes(main))

    # main page
    global main
    main = tk.Frame(root, bg="#F8F8F5")
    main.pack(side="right", fill="both", expand=True)

    show_main_screen(main)
    root.mainloop()

if __name__ == "__main__":
    build_gui()
