import os
import re
from unittest import result

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from generator import create_pdf
from ai_engine import generate_all


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ---------------- ROUTES ---------------- #

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/app", response_class=HTMLResponse)
async def app_page(request: Request):
    return templates.TemplateResponse(
        "app.html",
        {
            "request": request,
            "templates": ["article", "book", "letter", "report", "resume"],
        }
    )


# ---------------- HELPERS ---------------- #

def clean_filename(text: str):
    text = text.strip().lower()
    text = re.sub(r'[^a-z0-9 ]', '', text)
    return "_".join(text.split())[:40] or "document"


def fix_title(title: str, content: str):
    if not title or title.lower() in ["empty", "document"]:
        if "resume" in content.lower():
            return "Resume"
        elif "report" in content.lower():
            return "Report"
        return content[:40]
    return title[:80]


def clean_latex(content: str):
    if not content:
        return ""

    content = content.replace("**", "")
    content = content.replace("(empty)", "")

    content = content.replace("\\{", "{").replace("\\}", "}")
    content = re.sub(r"(?<!\\)&", r"\\&", content)
    content = re.sub(r"(?<!\\)%", r"\\%", content)
    content = re.sub(r"(?<!\\)#", r"\\#", content)

    if "\\item" in content and "\\begin{itemize}" not in content:
        content = "\\begin{itemize}\n" + content + "\n\\end{itemize}"

    return content.strip()


# ---------------- GENERATE ---------------- #

@app.post("/generate-ui")
async def generate_ui(
    content: str = Form(...),
    template_type: str = Form("article"),
):
    result = generate_all(content, template_type)


    if not result or not result[2]:
        return HTMLResponse(
            content="GENERATION_FAILED",
            status_code=200
        )

    title, author, latex_content = result

    title = fix_title(title, content)
    latex_content = clean_latex(latex_content)

    if not latex_content:
        raise ValueError("Generated document body is empty")

    temp_filename = f"temp_{os.getpid()}"

    pdf_path = create_pdf(
        content=latex_content,
        filename=temp_filename,
        template_type=template_type,
        title=title,
        author=author or "",
    )

    final_filename = f"{clean_filename(title)}.pdf"

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=final_filename
    )
