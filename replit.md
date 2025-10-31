# Resume Quality Analyzer

## Overview
A comprehensive web application that analyzes resume quality and provides actionable insights to help users improve their resumes and land their target roles. Built with FastAPI backend and HTMX + Tailwind frontend.

## Features
- **Session-based Authentication**: Username login or guest access with session cookies
- **Resume Upload & Parsing**: Supports PDF, DOCX, and TXT formats (max 5MB)
- **Rule-based Analysis Engine**: Comprehensive scoring across 4 categories (0-120 total)
  - Completeness (contact info, sections, length)
  - Summary Quality (coverage, concision, specificity, impact, evidence)
  - Education (degrees, years, thesis, GPA/honors)
  - Employment (bullets, quantification, experience years)
- **ATS Readiness Checks**: Detects formatting issues, missing sections, non-ASCII characters
- **Role Alignment**: Scores resume against target job role vocabulary
- **Career Stage Detection**: Student / Recent Graduate / Mid-Level / Senior
- **1-Year Improvement Plan**: Rule-based plan with quarterly milestones
- **Optional Gemini AI Enhancement**: Refines plans and generates tailored keywords when GOOGLE_API_KEY is set
- **Report Downloads**: JSON and PDF exports
- **Session History**: Last 5 analyses per session

## Project Structure
```
.
├── app.py                  # FastAPI application
├── parser.py              # Resume parsing (PDF/DOCX/TXT)
├── analyzer.py            # Rule-based analysis engine
├── plan_generator.py      # Improvement plan with optional Gemini
├── database.py            # SQLite storage
├── report_generator.py    # PDF/JSON report generation
├── keywords.py            # Curated keyword dictionaries
├── templates/             # Jinja2 HTML templates
│   ├── base.html
│   ├── landing.html
│   ├── home.html
│   ├── results.html
│   └── history.html
├── static/                # CSS/JS assets
├── data/                  # SQLite database
└── tmp/                   # Uploads and reports
```

## Dependencies
- FastAPI + Uvicorn
- PyMuPDF (fitz) - PDF parsing
- python-docx, docx2txt - DOCX parsing
- ReportLab - PDF report generation
- Jinja2 - Template rendering
- itsdangerous - Session management
- SQLite3 (stdlib)
- Google Generative AI (optional)

## Environment Variables
- `GOOGLE_API_KEY` (optional) - Enables Gemini AI enhancement
- `SESSION_SECRET` (optional) - Session cookie secret
- `PORT` (default: 5000) - Server port

## Recent Changes
- 2025-10-31: Enhanced URL detection - detects hyperlinked keywords (LinkedIn, GitHub, Kaggle) even when URLs are hidden
- 2025-10-31: Added detailed section-by-section feedback below overall score (Contacts/Links, Summary, Education, Employment, Misc)
- 2025-10-31: Sharpened analysis rules with specific point breakdowns (e.g., "Missing 8 points: Add 3 more metrics...")
- 2025-10-31: Enhanced Gemini AI to use real tech job descriptions for role-specific keywords and advice
- 2025-10-31: Fixed Gemini model name (gemini-pro) and now uses ALL generated keywords (not limited to 10)
- 2025-10-31: Created SCORING_SYSTEM.md explaining how each category is scored (0-30 points each)
- 2025-10-30: Initial implementation with all core features

## User Preferences
- Wants detailed, specific feedback explaining exactly why points were deducted
- Prefers realistic suggestions (especially for quantifiable metrics when exact %/$ not available)
- Wants to understand the scoring breakdown clearly
- Focuses on tech roles (ML Engineer, Data Scientist, Software Engineer, etc.)

## Architecture Decisions
- Single-service architecture (no microservices)
- Rule-based analysis as primary engine (works without AI)
- Optional Gemini enhancement for keywords and plan refinement
- Session-based storage in SQLite (no external auth)
- File size limit: 5MB for security
- Frontend uses HTMX for dynamic interactions without heavy JavaScript
