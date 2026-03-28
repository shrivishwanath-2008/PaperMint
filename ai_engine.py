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


def normalize_generated_content(content: str) -> str:
    if not content:
        return ""

    normalized = content.strip()
    normalized = normalized.replace("**", "")
    normalized = normalized.replace("(empty)", "")
    normalized = normalized.replace("[empty]", "")
    normalized = normalized.replace("empty", "") if normalized.lower() == "empty" else normalized
    return normalized.strip()


def generate_all(prompt: str, template_type: str):
    system = f"""
Return ONLY this exact tagged format:
[TITLE]
your title
[/TITLE]
[AUTHOR]
author name or blank
[/AUTHOR]
[CONTENT]
LaTeX content only
[/CONTENT]

Rules:
- No markdown fences
- No explanations outside the tags

LaTeX:
- No preamble
- Do NOT escape {{}} or \\
- Use proper structure

Template: {template_type}

Structure:
- article -> sections
- report -> intro, methodology, results, conclusion
- resume -> education, skills, experience, projects, certifications
- book -> chapters
- letter -> formal layout

Resume-specific rules:
- The resume template already renders the main name/title block
- Do not create a second centered header with name, contact info, or title inside CONTENT
- For resume, CONTENT should start directly with sections like \\section*{{Education}}
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

        if getattr(response, "candidates", None):
            candidate = response.candidates[0]
            if getattr(candidate, "content", None) and getattr(candidate.content, "parts", None):
                text = "".join(
                    part.text for part in candidate.content.parts
                    if hasattr(part, "text")
                )

        if not text and hasattr(response, "text"):
            text = response.text

        if not text:
            raise ValueError("Empty response")

        print("RAW:", text)

        title = extract_tagged_field(text, "TITLE")
        author = extract_tagged_field(text, "AUTHOR")
        content = extract_tagged_field(text, "CONTENT")

        if not content:
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                match = re.search(r"\{.*\}", text, re.DOTALL)
                data = json.loads(match.group()) if match else {}

            title = title or data.get("title", "")
            author = author or data.get("author", "")
            content = data.get("content", "")

        content = normalize_generated_content(content)

        if not content:
            raise ValueError("No content")

        return title, author, content

    except Exception as e:
        print("GEMINI ERROR:", e)

        if "429" in str(e):
            return "RATE_LIMIT", None, None

        return None, None, None
