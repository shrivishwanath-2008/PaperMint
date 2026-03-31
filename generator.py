import subprocess
import os
from string import Template
from fastapi import HTTPException


def create_pdf(content, filename, template_type, title, author):
    template_dir = "latex_templates"
    template_file = os.path.join(template_dir, f"{template_type}.tex")
    tex_file = f"{filename}.tex"
    pdf_file = f"{filename}.pdf"

    if not os.path.exists(template_file):
        template_file = os.path.join(template_dir, "article.tex")

    with open(template_file, "r", encoding="utf-8") as f:
        template = Template(f.read())

    tex_code = template.substitute(
        content=content,
        title=title,
        author=author,
        date=""
    )

    with open(tex_file, "w", encoding="utf-8") as f:
        f.write(tex_code)

    try:
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", tex_file],
            stdout=None,
            stderr=None,
            check=True
        )

        if not os.path.exists(pdf_file):
            raise Exception("PDF not created")

        return pdf_file

    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="LaTeX failed")
