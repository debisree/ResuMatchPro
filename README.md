# Resume Quality Analyzer

A comprehensive web application that analyzes resume quality and provides actionable insights to help users land their target roles.

## Tech Stack

**Backend:**
- **FastAPI** - Modern Python web framework with automatic API documentation
- **Uvicorn** - ASGI server for running FastAPI
- **SQLite** - Lightweight database for session history
- **PyMuPDF (fitz)** - PDF parsing
- **python-docx** - DOCX parsing
- **ReportLab** - PDF report generation

**Frontend:**
- **HTMX** - Dynamic interactions without heavy JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Jinja2** - Template rendering

**Optional AI Enhancement:**
- **Google Gemini AI** - For enhanced keyword generation and plan refinement (when `GOOGLE_API_KEY` is set)

## Features

### Core Functionality
- ✅ **Session-based Authentication** - Username login or guest access with secure cookies
- ✅ **Resume Upload** - Supports PDF, DOCX, and TXT formats (max 5MB)
- ✅ **Smart Parsing** - Extracts contact info, sections, dates, and metrics
- ✅ **Rule-based Analysis** - Works completely offline without AI dependency

### Analysis Categories (0-120 Total Score)

1. **Completeness (0-30)**
   - Contact information (email, phone, URLs)
   - Required sections (summary, experience, education, skills)
   - Document length validation

2. **Summary Quality (0-30)**
   - Coverage of resume truths (roles, domains, tools)
   - Concision (stage-aware word count)
   - Specificity (distinct terms)
   - Impact density (action verbs)
   - Evidence density (metrics)
   - Faithfulness checks

3. **Education (0-30)**
   - Degree presence and types
   - Graduation years
   - Thesis/capstone projects
   - GPA and academic honors

4. **Employment (0-30)**
   - Bullet point density
   - Quantified outcomes (metrics)
   - Years of experience
   - Date ranges

### Additional Features
- 🎯 **ATS Readiness** - Checks formatting, non-ASCII characters, multi-column layouts
- 📊 **Role Alignment** - Scores resume against target job vocabulary
- 🎓 **Career Stage Detection** - Student / Recent Graduate / Mid-Level / Senior
- 📅 **1-Year Improvement Plan** - Quarterly milestones, skills, projects, networking
- 💡 **Tailored Keywords** - Action verbs and impact words for your target role
- 📥 **Download Reports** - JSON and PDF exports
- 📜 **Session History** - Last 5 analyses per session

## Quick Start

### 1. Set Up (Already Done)
All dependencies are installed and the database is initialized.

### 2. Optional: Add Gemini API Key
To enable AI-enhanced plans and keywords:
```bash
# Add GOOGLE_API_KEY in Secrets
```

Without the API key, the app works perfectly with rule-based analysis only.

### 3. Access the Application
The FastAPI server runs on port 5000. Click the Webview to access:
- **Landing Page** (`/`) - Login or continue as guest
- **Home** (`/app`) - Upload resume and specify target role
- **Results** (`/app/results/{id}`) - View detailed analysis
- **History** (`/app/history`) - View past analyses

## Usage Example

1. **Landing**: Enter your name or click "Continue as Guest"
2. **Home**: 
   - Enter target role (e.g., "Machine Learning Engineer in FinTech")
   - Select seniority goal (optional)
   - Upload your resume (PDF/DOCX/TXT)
   - Click "Analyze Resume"
3. **Results**: View your scores, ATS readiness, role alignment, and 1-year plan
4. **Download**: Get JSON or PDF reports
5. **History**: Review your past 5 analyses

## Project Structure

```
.
├── app.py                  # FastAPI application with all endpoints
├── parser.py              # Resume parsing (PDF/DOCX/TXT extraction)
├── analyzer.py            # Rule-based analysis engine (scoring)
├── plan_generator.py      # Improvement plan generator
├── database.py            # SQLite operations
├── report_generator.py    # PDF/JSON report generation
├── keywords.py            # Curated dictionaries (tools, domains, roles, verbs)
├── templates/             # Jinja2 HTML templates
│   ├── base.html         # Base template with navigation
│   ├── landing.html      # Login/guest landing page
│   ├── home.html         # Upload and analyze page
│   ├── results.html      # Analysis results dashboard
│   └── history.html      # Session history
├── static/               # Static assets
├── data/                 # SQLite database
├── tmp/                  # Temporary uploads and reports
└── sample_resume.txt     # Sample resume for testing
```

## API Endpoints

- `GET /` - Landing page
- `POST /login` - Login with username
- `POST /guest` - Continue as guest
- `GET /app` - Home page (upload)
- `POST /api/analyze` - Analyze resume (multipart form)
- `GET /app/results/{id}` - Results page
- `GET /app/history` - History page
- `GET /api/history` - Get session history (JSON)
- `GET /api/report/{id}.json` - Download JSON report
- `GET /api/report/{id}.pdf` - Download PDF report
- `GET /health` - Health check

## Security Features

- ✅ File size limit (5MB)
- ✅ File type validation (PDF/DOCX/TXT only)
- ✅ Filename sanitization (rejects executables, path traversal)
- ✅ Session cookies with secure serialization
- ✅ Temporary file cleanup after processing

## Analysis Algorithm

### Rule-Based Scoring
The analyzer uses curated keyword dictionaries and pattern matching:

- **86 tools** (Python, TensorFlow, AWS, Docker, etc.)
- **70+ impact verbs** (optimized, deployed, led, etc.)
- **80+ domains** (FinTech, Healthcare, Manufacturing, etc.)
- **40+ role titles** (Data Scientist, ML Engineer, etc.)

### Scoring Logic
Each category has specific rubrics:
- Completeness: Section presence + contact info
- Summary: Coverage + concision + specificity + impact + evidence
- Education: Degrees + years + thesis + honors
- Employment: Bullets + metrics + experience years

### ATS Checks
- Non-ASCII character percentage
- Box-drawing/decorative characters
- Multi-column layout detection
- Table/tab usage
- Length validation
- Missing sections

## Testing

Run the included test scripts:

```bash
# Test analysis engine
python test_analysis.py

# Test full integration
python test_integration.py
```

Both tests use `sample_resume.txt` and verify:
- ✅ Resume parsing
- ✅ Analysis scoring
- ✅ Plan generation
- ✅ Database storage
- ✅ Report generation (JSON + PDF)

## Environment Variables

- `GOOGLE_API_KEY` (optional) - Enables Gemini AI enhancement
- `SESSION_SECRET` (optional) - Custom session cookie secret
- `PORT` (default: 5000) - Server port

## Why FastAPI?

FastAPI was chosen over Flask, Dash, and Streamlit because:

1. **Modern & Fast** - Built on Starlette and Pydantic
2. **Automatic API Docs** - Interactive Swagger UI at `/docs`
3. **Type Hints** - Better IDE support and validation
4. **Async Support** - Ready for scaling
5. **Easy Integration** - Works seamlessly with HTMX for dynamic UIs

Unlike Streamlit (which is great for data apps but less flexible for custom UIs) or Dash (focused on dashboards), FastAPI + HTMX gives us full control over the UI while keeping the backend simple and fast.

## Sample Analysis Results

Using `sample_resume.txt`:
- **Overall Score**: 112/120 (High Completeness)
- **Completeness**: 30/30 (Excellent)
- **Summary**: 26/30 (Strong)
- **Education**: 28/30 (Excellent)
- **Employment**: 28/30 (Excellent)
- **ATS Readiness**: Pass
- **Role Alignment**: 28% for "Machine Learning Engineer"

## Future Enhancements

- Batch resume comparison
- Resume rewriting suggestions
- Customizable scoring weights
- Job board integration for real JD analysis
- Collaborative review features for coaches

## License

Built for Replit - Educational/Portfolio Project
