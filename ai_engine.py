# from curses import flash
from email.mime import text
import os
import json
from pydoc import text
import re
from urllib import response
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-2.5-flash"
model = genai.GenerativeModel(MODEL)


def extract_tagged_field(text: str, tag: str) -> str:
    if not text:
        return ""

    match = re.search(rf"\[{tag}\]\s*(.*?)\s*\[/{tag}\]", text, re.DOTALL)
    if match:
        value = match.group(1)
        return str(value).strip() if value else ""

    if tag == "CONTENT":
        match = re.search(rf"\[{tag}\]\s*(.*)", text, re.DOTALL)
        if match:
            value = match.group(1)
            return str(value).strip() if value else ""

    return ""


def normalize_generated_content(content: str) -> str:
    if not content:
        return ""

    normalized = str(content).strip()
    normalized = normalized.replace("**", "")
    normalized = normalized.replace("(empty)", "")
    normalized = normalized.replace("[empty]", "")

    if normalized.lower() == "empty":
        return ""

    return str(normalized).strip()


def generate_all(prompt: str, template_type: str):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None, None, None, "GEMINI_API_KEY is missing."

    system = f'''
Return ONLY this format:

[TITLE]
[/TITLE]

[AUTHOR]
[/AUTHOR]

[CONTENT]
[/CONTENT]

RULES:
- Must include ALL tags and close them
- Output must end with [/CONTENT]
- No markdown, no explanations
- LaTeX only inside CONTENT

Template: {template_type}

Resume:
- No title
- Sections: Education, Experience, Projects, Skills
- Use \\section*
- Use \\begin{{itemize}} \\item ... \\end{{itemize}}
'''

    text = None

    # ✅ retry system
    for attempt in range(2):
        try:
            response = model.generate_content(
                f"{system}\n{prompt}",
                generation_config={
                    "temperature": 0.6,
                    "max_output_tokens": 2000,
                },
            )

            # extract safely
            if hasattr(response, "text") and response.text:
                text = response.text

            if not text:
                raise ValueError("Empty AI response")

            text = str(text)

            # reject bad outputs
            if len(text) < 100:
                raise ValueError("Too short")

            if not text.strip().endswith("[/CONTENT]"):
                print("FIXING: adding closing tag")
                text += "\n[/CONTENT]"
            break  # success

        except Exception as e:
            print(f"Attempt {attempt+1} failed:", e)
            text = None

    if not text:
        return None, None, None, "AI failed. Try again."

    # extract fields
    title = extract_tagged_field(text, "TITLE")
    author = extract_tagged_field(text, "AUTHOR")
    content = extract_tagged_field(text, "CONTENT")

    if not content:
        print("FALLBACK: using raw text")
        content = text

    content = normalize_generated_content(content)

    if not content:
        print("FALLBACK: using raw text")
        content = text

    return title, author, content, None