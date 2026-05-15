# PaperMint

<p align="center">
  <img src="static/papermint-logo.png" width="300">
</p>

<h3 align="center">
AI-Powered LaTeX PDF Generation Platform
</h3>

<p align="center">
Generate professional PDF documents from simple prompts using AI, FastAPI, and LaTeX.
</p>

---

# Overview

PaperMint is a modern AI-powered document generation platform that converts natural language prompts into professionally formatted PDF documents.

Instead of manually formatting resumes, articles, reports, or notes, users simply describe what they want — PaperMint automatically generates structured content, formats it using LaTeX, and returns a downloadable PDF.

The project combines:
- AI-generated content
- FastAPI backend architecture
- LaTeX rendering
- Modern frontend UI
- Automated PDF compilation

---

# Features

- AI-powered document generation
- Professional LaTeX PDF formatting
- Resume generation
- Article generation
- Formula sheet support
- Modern dark-themed UI
- Animated interactive background
- Loading animations
- Instant PDF download
- FastAPI backend
- Gemini AI integration
- Docker-ready deployment

---

# Tech Stack

## Frontend
- HTML
- CSS
- JavaScript

## Backend
- FastAPI
- Python

## AI Integration
- Google Gemini API

## PDF Engine
- LaTeX
- pdflatex

## Deployment
- Docker
- Railway

---

# How It Works

```text
User Prompt
    ↓
FastAPI Backend
    ↓
Gemini AI
    ↓
Structured LaTeX Generation
    ↓
pdflatex Compilation
    ↓
Downloadable PDF
```
# Frontend
The frontend provides:

- prompt input
- template selection
- animated UI
- loading states
- PDF download support

The interface follows a modern AI-startup inspired design with:

- dark theme
- dotted animated background
- cursor glow effects
- smooth transitions
- glassmorphism styling

# Backend
The backend is built using FastAPI.

Main responsibilities:

- API routing
- request handling
- AI communication
- LaTeX generation
- PDF compilation
- file response handling

# AI Engine
PaperMint uses the Gemini API to generate structured document content.

The AI generates:

- titles
- author sections
- formatted content
- LaTeX-compatible structures

Structured tags are used internally to improve reliability.

# Why LaTeX?
PaperMint uses LaTeX because it provides:

- professional typography
- clean layouts
- academic-quality PDFs
- better mathematical formatting
- highly consistent document structure

Compared to traditional HTML-to-PDF systems, LaTeX produces significantly cleaner results.

# Installation
## Clone Repository:
```text
git clone https://github.com/yourusername/PaperMint.git
cd PaperMint
```
## Create Virtual Environment
- Windows
```text
python -m venv venv
venv\Scripts\activate
```
- macOS/Linux
```text
python3 -m venv venv
source venv/bin/activate
```

## Install Dependencies
```text
pip install -r requirements.txt
```

# Environment Variables
Create a new .env file:

```text
GEMINI_API_KEY=your_api_key_here
```

# Run Locally
```text
uvicorn main:app --reload
```
Open:
```text
http://127.0.0.1:8000
```

# Current Templates
PaperMint currently supports:

- Resume
- Article

Planned templates:

- Research papers
- Reports
- Notes
- Formula sheets
- Invoices

# Challenges Faced
This project involved solving several technical challenges:

- AI-generated malformed LaTeX
- Broken PDF compilation
- Template conflicts
- Deployment optimization
- Large Docker image sizes
- Dynamic environment configuration
- AI output normalization

# Future Improvements
Planned improvements include:

- Live PDF preview
- User authentication
- Cloud PDF storage
- More templates
- Streaming generation
- Real-time collaboration
- Advanced LaTeX validation

# Core Idea:
PaperMint combines:

- AI-generated structured content
- deterministic LaTeX rendering

to automate the creation of professional documents from simple prompts.

# License
MIT License

# Author
Build by Shri Vishwanath