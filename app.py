import tkinter as tk
from tkinter import scrolledtext
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time

from guardrails import system_prompt, is_prompt_injection, length_guard
from tools import get_version_and_date
from telemetry import log_request

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Modern model
model = genai.GenerativeModel("gemini-flash-latest")


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
        + f"Current Date: {date}\n"
        + f"Version Base: {version}\n"
    )

    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, "[Working...] contacting Gemini Flash…\n")
    output_box.update()

    start = time.time()

    response = model.generate_content(full_prompt)
    latency = time.time() - start

    log_request("generate", latency, response.usage_metadata.total_token_count)

    output = response.text
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, output)

    with open("patch_notes.md", "a") as f:
        f.write("\n\n" + output)


def build_gui():
    root = tk.Tk()
    root.title("Patch Notes Writer")
    root.geometry("1200x800")
    root.configure(bg="#F8F8F5")   # subtle Apple Notes off-white

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
        insertbackground="black",  # cursor
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

    # Make disabled state visible
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
