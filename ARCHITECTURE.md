# ResuMatch Architecture Documentation

## Overview

ResuMatch is a **hybrid AI-powered resume analyzer** that combines Google's Gemini 2.0 Pro AI with rule-based analysis to provide comprehensive resume evaluation and career planning.

**Philosophy:** Use AI where semantic understanding matters, use rules where objectivity is required.

---

## System Architecture

### Technology Stack

**Backend:**
- FastAPI (Python web framework)
- Uvicorn (ASGI server)
- Google Gemini 2.0 Pro Experimental (`gemini-2.0-pro-exp`)
- PostgreSQL (session storage)
- ReportLab (PDF generation)

**Frontend:**
- HTMX (dynamic interactions)
- Tailwind CSS (styling)
- Jinja2 templates

**Data Sources:**
- U.S. Bureau of Labor Statistics (BLS) May 2024 salary data
- Custom rule-based pattern matching
- Google Gemini AI semantic analysis

---

## Hybrid Analysis System

ResuMatch uses a **two-tier hybrid approach**: Gemini AI for semantic understanding + rule-based checks for objective criteria.

### Analysis Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Resume Upload (PDF/DOCX/TXT)              │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: Rule-Based Information Extraction                  │
│ ────────────────────────────────────────────────────────────│
│ • Contact Information Detection (regex patterns)            │
│   - Email addresses                                          │
│   - Phone numbers                                            │
│   - LinkedIn/Portfolio URLs                                  │
│                                                              │
│ • Date & Experience Calculation                             │
│   - Extract date ranges (2020-2023, Jan 2020 - Present)    │
│   - Calculate total years of experience                     │
│   - Detect career timeline gaps                             │
│                                                              │
│ • Section Detection (keyword matching)                      │
│   - Education, Experience, Skills, Projects                 │
│   - Summary/Objective                                        │
│   - Certifications, Awards                                  │
│                                                              │
│ • Metrics Extraction (pattern matching)                     │
│   - Numbers: "500+ users", "20 team members"               │
│   - Percentages: "30% improvement", "95% accuracy"         │
│   - Dollar amounts: "$2M revenue", "saved $50k"            │
│   - Time savings: "reduced time by 5 hours"                │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: Gemini AI Semantic Analysis (TRIES FIRST)          │
│ ────────────────────────────────────────────────────────────│
│ Model: gemini-2.0-pro-exp (Google's most capable model)    │
│                                                              │
│ • Role Alignment Scoring (0-30 points)                      │
│   - Semantic skill matching                                 │
│   - Experience relevance evaluation                         │
│   - Job title similarity analysis                           │
│   - Domain knowledge assessment                             │
│                                                              │
│ • Gap Analysis                                              │
│   - Missing critical skills                                 │
│   - Experience level shortfalls                             │
│   - Required certifications not present                     │
│   - Domain knowledge gaps                                   │
│                                                              │
│ • Strength Identification                                   │
│   - Top 3-5 qualifications for target role                 │
│   - Transferable skills from different domains             │
│   - Unique value propositions                               │
│                                                              │
│ Fallback: If API fails or key unavailable → Keyword matching│
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: Combined Scoring (0-120 Total)                     │
│ ────────────────────────────────────────────────────────────│
│ 1. Content Quality (30 points) - RULE-BASED                │
│    • Professional summary present: 5 pts                    │
│    • Work experience details: 10 pts                        │
│    • Education section: 5 pts                               │
│    • Skills section: 5 pts                                  │
│    • Additional sections (projects/certs): 5 pts            │
│                                                              │
│ 2. ATS Readiness (30 points) - RULE-BASED                  │
│    • Contact information complete: 10 pts                   │
│    • Standard section headers: 5 pts                        │
│    • No complex formatting (tables/columns): 5 pts          │
│    • Readable font and spacing: 5 pts                       │
│    • Keyword optimization: 5 pts                            │
│                                                              │
│ 3. Impact & Metrics (30 points) - HYBRID                   │
│    • Quantified achievements: 15 pts (rule-based count)    │
│    • Action verb usage: 10 pts (AI semantic + rules)       │
│    • Impact demonstration: 5 pts (AI evaluation)           │
│                                                              │
│ 4. Role Alignment (30 points) - GEMINI AI PRIMARY          │
│    • Skill match relevance: 15 pts (AI semantic)           │
│    • Experience level fit: 10 pts (AI + date calculation)  │
│    • Domain knowledge: 5 pts (AI evaluation)               │
│    Fallback: Keyword matching if Gemini unavailable        │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 4: Career Stage Detection - RULE-BASED                │
│ ────────────────────────────────────────────────────────────│
│ • Entry Level: 0-2 years experience                         │
│ • Mid-Level: 3-5 years experience                          │
│ • Senior: 6-9 years experience                             │
│ • Staff/Principal: 10+ years experience                    │
│ • Executive/C-Suite: 15+ years + leadership keywords       │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 5: Salary Analysis - BLS DATA (Rule-Based)            │
│ ────────────────────────────────────────────────────────────│
│ • Current Location Salary Distribution                      │
│   - 10th, 25th, Median, 75th, 90th percentiles            │
│   - Data source: BLS May 2024                              │
│                                                              │
│ • Target Location Salary Distribution                       │
│   - Same percentile breakdown                               │
│   - Side-by-side histogram comparison                      │
│                                                              │
│ • Relocation Impact Analysis                                │
│   - Salary gain/loss calculation                            │
│   - Cost of living considerations (visual indicators)      │
│                                                              │
│ Cities: NYC, SF, Seattle, Austin, Boston, Chicago, Denver, │
│         Atlanta, Miami, Remote                              │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 6: Improvement Plan Generation - GEMINI AI            │
│ ────────────────────────────────────────────────────────────│
│ Model: gemini-2.0-pro-exp (2M token context)               │
│                                                              │
│ Generates personalized 6-month or 1-year roadmap:          │
│                                                              │
│ • Skill Development Plan                                    │
│   - Priority skills to learn (1-3 critical gaps)           │
│   - Learning resources and certifications                  │
│   - Practice project suggestions                           │
│                                                              │
│ • Resume Enhancement Strategy                               │
│   - Content improvements (achievements to add)             │
│   - Formatting fixes (ATS optimization)                    │
│   - Keyword optimization                                    │
│                                                              │
│ • Career Action Items                                       │
│   - Networking strategies                                   │
│   - Portfolio/GitHub improvements                           │
│   - Interview preparation focus areas                      │
│                                                              │
│ • Timeline & Milestones                                     │
│   - Month-by-month action plan                             │
│   - Checkpoint goals                                        │
│   - Progress tracking metrics                              │
│                                                              │
│ Fallback: Generic template-based plan if Gemini unavailable│
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│             Results Display & Export Options                 │
│                                                              │
│ • Web UI (HTML results page)                                │
│ • JSON export (machine-readable)                            │
│ • PDF report (formatted document with charts)              │
└─────────────────────────────────────────────────────────────┘
```

---

## AI vs Rule-Based Breakdown

### What Uses Gemini 2.0 Pro AI

| Component | AI Usage | Fallback |
|-----------|----------|----------|
| **Role Alignment Scoring** | Semantic skill matching, experience relevance | Keyword matching |
| **Gap Analysis** | Identifies missing skills with context | Pattern matching for keywords |
| **Strength Matching** | Finds transferable skills and unique value | Lists detected keywords |
| **Improvement Plans** | Personalized roadmap with reasoning | Generic template |
| **Skill Relevance** | Understands context (React vs React Native) | Exact string matching |
| **Impact Evaluation** | Evaluates achievement significance | Counts action verbs |

### What Uses Rule-Based Analysis

| Component | Method | Reason |
|-----------|--------|--------|
| **Contact Detection** | Regex patterns | Objective (email exists or doesn't) |
| **Date Extraction** | Date parsing algorithms | Deterministic calculation |
| **Years of Experience** | Date range math | Simple arithmetic |
| **Section Detection** | Keyword matching | Standard headers (Education, Skills) |
| **Metrics Extraction** | Pattern matching | Numbers, percentages, dollar amounts |
| **ATS Formatting** | Document structure analysis | Objective criteria |
| **Career Stage** | Experience year thresholds | Industry-standard ranges |
| **Salary Data** | BLS dataset lookup | Real market data |

---

## Gemini 2.0 Pro Model Details

### Model Configuration

```python
# analyzer.py
self.model = genai.GenerativeModel('gemini-2.0-pro-exp')

# plan_generator.py  
self.model = genai.GenerativeModel('gemini-2.0-pro-exp')
```

### Capabilities

**Context Window:** 2 million tokens (~1.5 million words)
- Can analyze very large resumes and job descriptions
- Maintains context across multiple analysis steps

**Strengths:**
- Best-in-class reasoning and coding performance
- Enhanced multimodal understanding
- Superior world knowledge and common sense
- Complex prompt handling

**Use Cases in ResuMatch:**
1. **Role Alignment:** Understands nuanced skill relationships
2. **Gap Analysis:** Identifies not just missing skills but *why* they matter
3. **Plan Generation:** Creates contextual, actionable improvement plans
4. **Semantic Matching:** Goes beyond keywords to understand equivalencies

### Fallback Mechanism

```python
if self.gemini_available:
    try:
        # Use Gemini AI for semantic analysis
        alignment_score = self._analyze_with_gemini()
    except Exception:
        # Fallback to keyword matching
        alignment_score = self._keyword_fallback()
else:
    # API key not available
    alignment_score = self._keyword_fallback()
```

**When Fallback Triggers:**
- `GOOGLE_API_KEY` environment variable not set
- API request fails (network issue, quota exceeded)
- Gemini library not installed
- Model returns invalid response

**Fallback Quality:**
- Still functional but less intelligent
- Uses keyword matching instead of semantic understanding
- Cannot detect transferable skills or context
- Generic improvement plans instead of personalized

---

## Scoring System Detail

### Total Score: 0-120 Points

```
Excellent: 90-120 points
Good: 70-89 points  
Needs Work: 50-69 points
Weak: 0-49 points
```

### Category Breakdown

#### 1. Content Quality (0-30 points) - RULE-BASED

```python
# Checks performed:
- Professional summary present: 5 pts
- Work experience with details: 10 pts
- Education section exists: 5 pts
- Skills section present: 5 pts
- Additional sections (projects/certifications): 5 pts
```

**Logic:** Simple boolean checks for section presence + content length thresholds.

#### 2. ATS Readiness (0-30 points) - RULE-BASED

```python
# Checks performed:
- Email + phone present: 10 pts
- Standard section headers: 5 pts
- No tables/columns detected: 5 pts
- Clean formatting (no special characters): 5 pts
- Keywords from job description: 5 pts
```

**Logic:** Pattern matching for contact info, document structure analysis for formatting.

#### 3. Impact & Metrics (0-30 points) - HYBRID

```python
# Rule-based portion:
- Count of quantified achievements: up to 15 pts
- Action verb usage count: up to 10 pts

# AI portion:
- Gemini evaluates impact quality: up to 5 pts
- Assesses whether metrics are meaningful
```

**Logic:** Counts metrics with rules, uses AI to evaluate significance.

#### 4. Role Alignment (0-30 points) - AI PRIMARY

```python
# Gemini AI analysis:
- Semantic skill matching: up to 15 pts
- Experience level fit: up to 10 pts  
- Domain knowledge relevance: up to 5 pts

# Fallback (keyword matching):
- Counts overlapping keywords from job description
- Basic title similarity check
```

**Logic:** Gemini provides nuanced scoring; fallback uses simple keyword overlap percentage.

---

## Data Sources

### 1. User Input
- Resume file (PDF/DOCX/TXT)
- Target role (predefined or custom job description)
- Current & target locations (10 cities + remote)
- Career goal (promotion/pivot/lateral move)
- Timeframe (6 months / 1 year)
- Domain specialization (optional)

### 2. BLS (Bureau of Labor Statistics) Data
- **Source:** May 2024 Occupational Employment and Wage Statistics
- **Coverage:** 800+ occupations across 10 major U.S. cities
- **Data Points:** 10th, 25th, 50th (median), 75th, 90th percentiles
- **Format:** Embedded Python dictionaries in `salary_analyzer.py`
- **Update Frequency:** BLS releases annually; data manually updated

### 3. Pattern Libraries (Rule-Based)
```python
# analyzer.py constants:
SECTION_HINTS = ['education', 'experience', 'skills', ...]
ROLE_TITLES = ['engineer', 'developer', 'manager', ...]
DOMAIN_HINTS = ['machine learning', 'cloud', 'frontend', ...]
TOOL_HINTS = ['python', 'react', 'docker', ...]
IMPACT_VERBS = ['achieved', 'led', 'built', ...]
METRIC_PATTERNS = [r'\d+%', r'\$\d+', r'\d+ (users|customers)', ...]
```

### 4. Gemini AI Knowledge
- General world knowledge (programming languages, industries, skills)
- Semantic understanding of role requirements
- Career development best practices
- Resume writing conventions

---

## Session & Data Management

### Session Storage (PostgreSQL)

```python
# database.py
- User sessions stored in PostgreSQL
- Session data: user_id, created_at, last_accessed
- Resume analysis results cached per session
- Session timeout: 24 hours (configurable)
```

### File Handling

**Uploads:**
- Accepted formats: PDF, DOCX, TXT
- Max size: 10MB (configurable in FastAPI)
- Processing: Extracted to plain text using PyMuPDF (PDF) or python-docx (DOCX)
- Storage: Temporary (deleted after analysis)

**Exports:**
- JSON: Full analysis results in machine-readable format
- PDF: Formatted report with charts (matplotlib + ReportLab)
- Generated on-demand, not persisted

### Environment Variables

```bash
# Required for AI features:
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional:
SESSION_SECRET=random_secret_for_session_cookies
PORT=5000  # Server port
```

---

## Security Considerations

### API Key Management
- API keys stored in environment variables only
- Never committed to repository
- Never exposed in client-side code
- Session secrets use cryptographically secure random generation

### File Upload Safety
- File type validation (magic number checking)
- Size limits enforced
- Temporary file cleanup after processing
- No execution of uploaded content

### Data Privacy
- Resume content not persisted long-term
- Session data expires automatically
- No third-party analytics
- AI analysis sent to Google Gemini API (see Google's privacy policy)

---

## Performance Characteristics

### Analysis Speed

**With Gemini AI:**
- Resume parsing: ~0.5-1 second
- Gemini analysis: ~2-4 seconds
- Total: ~3-5 seconds per resume

**Without Gemini (Fallback):**
- Resume parsing: ~0.5-1 second  
- Rule-based analysis: ~0.2-0.5 seconds
- Total: ~1-2 seconds per resume

### Scalability

**Current Design:**
- Synchronous processing (one resume at a time per session)
- Suitable for: Individual users, career coaches
- Bottleneck: Gemini API rate limits (Google's quotas)

**Potential Optimizations:**
- Add async/await for concurrent requests
- Implement request queuing for high volume
- Cache common job description analyses
- Use Gemini 2.0 Flash for faster responses (trade quality for speed)

---

## Error Handling

### Graceful Degradation

```python
# Three-tier fallback system:

1. Try Gemini AI analysis
   ↓ (if fails)
2. Use keyword-based analysis  
   ↓ (if fails)
3. Return basic structure with warnings
```

### User-Facing Errors

**Gemini API Unavailable:**
```
⚙️ AI analysis unavailable - using keyword matching fallback
Results may be less accurate. Check your API key configuration.
```

**Invalid Resume Format:**
```
❌ Unable to parse resume. Please upload PDF, DOCX, or TXT format.
```

**Missing Target Role:**
```
⚠️ No target role specified - showing general resume quality only
```

---

## Future Enhancements

### Potential AI Upgrades
- **Resume rewriting:** Let Gemini rewrite resume sections
- **Cover letter generation:** Auto-generate personalized cover letters
- **Interview prep:** Generate likely interview questions for role
- **Skill gap learning paths:** Link to specific courses/resources

### Potential Rule Enhancements
- **More BLS data:** Expand to all U.S. cities and counties
- **Company-specific data:** Salary ranges for FAANG, startups, etc.
- **Industry benchmarks:** Compare against industry-specific standards
- **Multi-language support:** Parse resumes in languages beyond English

### Architecture Improvements
- **Async processing:** Handle multiple resumes concurrently
- **Caching layer:** Redis for common analyses
- **A/B testing:** Compare Gemini 2.0 Flash vs Pro performance
- **Batch processing:** Upload and analyze multiple resumes at once

---

## Development Setup

### Local Installation

```bash
# Clone repository
git clone <repository-url>
cd resumatch

# Install dependencies (requires Python 3.11+)
pip install -r requirements.txt
# OR with uv (faster):
uv pip install -r requirements.txt

# Set environment variables
export GOOGLE_API_KEY="your_api_key_here"
export SESSION_SECRET="random_secret_string"

# Run development server
uvicorn app:app --host 0.0.0.0 --port 5000 --reload
```

### Testing AI vs Fallback

**Test with Gemini:**
```bash
export GOOGLE_API_KEY="valid_key"
# Uploads will show: 🤖 AI Analysis: Gemini 2.0 Pro
```

**Test fallback mode:**
```bash
unset GOOGLE_API_KEY
# Uploads will show: ⚙️ Keyword Analysis (Gemini unavailable)
```

---

## Code Organization

```
resumatch/
├── app.py                    # FastAPI application, routes
├── analyzer.py               # Hybrid resume analysis (AI + rules)
├── plan_generator.py         # Gemini-powered improvement plans
├── salary_analyzer.py        # BLS data & salary comparison
├── database.py               # PostgreSQL session management
├── utils.py                  # Text extraction (PDF/DOCX/TXT)
├── templates/
│   ├── home.html            # Upload interface
│   ├── results.html         # Analysis results display
│   └── base.html            # Base template
├── static/                   # CSS/JS (Tailwind via CDN)
├── pyproject.toml           # Python dependencies
├── replit.md                # Project overview & changelog
└── ARCHITECTURE.md          # This file
```

---

## API Reference (Internal)

### `ResumeAnalyzer` Class

```python
class ResumeAnalyzer:
    def __init__(
        self,
        resume_text: str,
        target_role: Optional[str] = None,
        seniority_goal: Optional[str] = None,
        is_custom_jd: bool = False
    )
    
    def analyze(self) -> Dict:
        """
        Returns complete analysis with 0-120 score breakdown
        
        Uses Gemini AI for role alignment if available,
        falls back to keyword matching otherwise.
        """
```

### `PlanGenerator` Class

```python
class PlanGenerator:
    def __init__(self, api_key: Optional[str] = None)
    
    def generate_plan(
        self,
        analysis_result: Dict,
        career_goal: str,
        timeframe: str,
        domain: Optional[str] = None
    ) -> Dict:
        """
        Generates personalized improvement plan using Gemini 2.0 Pro
        
        Falls back to generic template if Gemini unavailable
        """
```

### `SalaryAnalyzer` Class

```python
class SalaryAnalyzer:
    def analyze_salary(
        self,
        target_role: str,
        current_location: str,
        target_location: str
    ) -> Dict:
        """
        Returns salary comparison with BLS data
        
        Includes percentile distributions and relocation impact
        """
```

---

## Troubleshooting

### "AI Analysis Unavailable"

**Cause:** `GOOGLE_API_KEY` not set or invalid

**Solution:**
```bash
export GOOGLE_API_KEY="your_valid_api_key"
# Restart server
```

### Low Role Alignment Scores

**With AI:** Resume likely doesn't match target role semantically
**Without AI:** Not enough keyword overlap - try custom job description

### Salary Data "No data available"

**Cause:** Role or location combination not in BLS dataset

**Solution:** Try predefined roles from dropdown instead of custom job description

---

## License & Attribution

**BLS Data:**
- Source: U.S. Bureau of Labor Statistics, May 2024
- Public domain (U.S. government data)
- Citation required when displaying salary information

**Gemini AI:**
- Powered by Google Gemini 2.0 Pro
- Subject to Google's Gemini API terms of service
- API usage tracked and subject to quotas

---

**Last Updated:** November 1, 2025  
**Version:** 2.0 (Gemini 2.0 Pro upgrade)
