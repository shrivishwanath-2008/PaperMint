import os
import re
from unittest import result

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from generator import create_pdf
from ai_engine import generate_all


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


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
            "templates": ["article", "resume"],
        }
    )


def clean_filename(text: str):
    if not text:
        return "document"

    text = str(text).strip().lower()
    text = re.sub(r'[^a-z0-9 ]', '', text)
    return "_".join(text.split())[:40] or "document"


def fix_title(title: str, content: str):
    if not title:
        title = ""

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

    content = str(content)

    # remove logs / garbage
    content = content.split("This is pdfTeX")[0]
    content = content.split("FALLBACK:")[0]

    # remove full document if present
    if "\\documentclass" in content:
        match = re.search(r"\\begin\{document\}(.*?)\\end\{document\}", content, re.DOTALL)
        if match:
            content = match.group(1)

    content = re.sub(r"\\documentclass.*", "", content)
    content = re.sub(r"\\usepackage.*", "", content)
    content = re.sub(r"\\begin\{document\}", "", content)
    content = re.sub(r"\\end\{document\}", "", content)

    # fix item
    content = re.sub(r"(?m)^item ", r"\\item ", content)

    # fix itemize
    if "\\item" in content and "\\begin{itemize}" not in content:
        content = "\\begin{itemize}\n" + content

    if "\\begin{itemize}" in content and "\\end{itemize}" not in content:
        content += "\n\\end{itemize}"

    # fix sections
    lines = []
    for line in content.split("\n"):
        if "\\section*" in line and not line.strip().endswith("}"):
            line += "}"
        lines.append(line)
    content = "\n".join(lines)

    # balance braces
    if content.count("{") > content.count("}"):
        content += "}" * (content.count("{") - content.count("}"))

    return content.strip()

@app.post("/generate-ui")
async def generate_ui(
    content: str = Form(...),
    template_type: str = Form("article"),
):
    title, author, latex_content, error = generate_all(content, template_type)

    if error or not latex_content or len(latex_content.strip()) < 20:
        return JSONResponse(
            {
                "ok": False,
                "error": error or "Document generation failed."
            },
            status_code=200
        )

    if template_type == "resume":
        title = ""
    else:
        title = fix_title(title, content)
    latex_content = clean_latex(latex_content)

    if not latex_content or len(latex_content.strip()) < 20:
        print("FALLBACK: empty content")
        
        

    temp_filename = f"temp_{os.getpid()}"

    pdf_path = create_pdf(
        content=latex_content,
        filename=temp_filename,
        template_type=template_type,
        title=title,
        author=""
    )

    final_filename = f"{clean_filename(title)}.pdf"

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=final_filename
    )
