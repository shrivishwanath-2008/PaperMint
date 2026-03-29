import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

# --- INIT ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-flash-latest"
model = genai.GenerativeModel(MODEL)


def extract_tagged_field(text: str, tag: str) -> str:
    match = re.search(rf"\[{tag}\]\s*(.*?)\s*\[/{tag}\]", text, re.DOTALL)
    return match.group(1).strip() if match else ""


def generate_all(prompt: str, template_type: str):
    system = f"""
Return ONLY this exact format:

[TITLE]
...
[/TITLE]

[AUTHOR]
...
[/AUTHOR]

[CONTENT]
LaTeX only
[/CONTENT]

Rules:
- No markdown
- No explanations
- Must follow tags EXACTLY

LaTeX Rules:
- No preamble
- Do NOT escape {{}} or \\
- Use clean structure

Template: {template_type}

Structure:
- article -> sections
- report -> intro, methodology, results, conclusion
- book -> chapters
- letter -> formal layout
- resume -> adaptive professional resume

Resume Rules:
- Generate a professional resume for ANY profession
- Choose sections dynamically (Education, Experience, Projects, Skills, etc.)
- Use bullet points ONLY
- Use strong action verbs
- Keep it clean and one-page

LaTeX:
- Use \\section*
- Use \\begin{{itemize}} \\item ... \\end{{itemize}}
"""

    try:
        prompt = prompt[:800]

        response = model.generate_content(
            f"{system}\n{prompt}",
            generation_config={
                "temperature": 0.6,
                "max_output_tokens": 1500,
            },
        )

        text = None

        if response.candidates:
            c = response.candidates[0]
            if c.content and c.content.parts:
                text = "".join(
                    p.text for p in c.content.parts if hasattr(p, "text")
                )

        if not text:
            raise ValueError("Empty response")

        print("RAW:", text)

        title = extract_tagged_field(text, "TITLE")
        author = extract_tagged_field(text, "AUTHOR")
        content = extract_tagged_field(text, "CONTENT")

        if not content:
            raise ValueError("No content generated")

        return title, author, content

    except Exception as e:
        print("GEMINI ERROR:", e)

        if "429" in str(e):
            return "RATE_LIMIT", None, None

        return None, None, None