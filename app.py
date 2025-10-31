import os
import uuid
import secrets
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from itsdangerous import URLSafeSerializer

from parser import parse_resume, normalize_text
from analyzer import ResumeAnalyzer
from plan_generator import ImprovementPlanGenerator
from database import Database
from report_generator import ReportGenerator
from salary_analyzer import get_salary_analysis

app = FastAPI(title="ResuMatch")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

SESSION_SECRET = os.environ.get('SESSION_SECRET', secrets.token_hex(32))
serializer = URLSafeSerializer(SESSION_SECRET)

db = Database()
plan_gen = ImprovementPlanGenerator()
report_gen = ReportGenerator()

UPLOAD_DIR = "tmp/uploads"
REPORTS_DIR = "tmp/reports"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt'}


def get_session_id(request: Request) -> str:
    session_cookie = request.cookies.get('session_id')
    if session_cookie:
        try:
            return serializer.loads(session_cookie)
        except:
            pass
    return str(uuid.uuid4())


def create_session_cookie(session_id: str) -> str:
    return serializer.dumps(session_id)


def validate_filename(filename: str) -> bool:
    if not filename:
        return False
    
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False
    
    dangerous_patterns = ['.exe', '.sh', '.bat', '.cmd', '../', '..\\']
    for pattern in dangerous_patterns:
        if pattern in filename.lower():
            return False
    
    return True


@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


@app.post("/login")
async def login(request: Request, username: str = Form(...)):
    session_id = f"user_{username}_{uuid.uuid4()}"
    response = RedirectResponse(url="/app", status_code=303)
    response.set_cookie(
        key="session_id",
        value=create_session_cookie(session_id),
        httponly=True,
        max_age=86400 * 7
    )
    response.set_cookie(
        key="username",
        value=username,
        httponly=False,
        max_age=86400 * 7
    )
    return response


@app.post("/guest")
async def guest_login(request: Request):
    session_id = f"guest_{uuid.uuid4()}"
    response = RedirectResponse(url="/app", status_code=303)
    response.set_cookie(
        key="session_id",
        value=create_session_cookie(session_id),
        httponly=True,
        max_age=86400 * 7
    )
    response.set_cookie(
        key="username",
        value="Guest",
        httponly=False,
        max_age=86400 * 7
    )
    return response


@app.get("/app", response_class=HTMLResponse)
async def home_page(request: Request):
    session_id = get_session_id(request)
    username = request.cookies.get('username', 'Guest')
    
    return templates.TemplateResponse("home.html", {
        "request": request,
        "username": username
    })


@app.post("/api/analyze")
async def analyze_resume(
    request: Request,
    file: UploadFile = File(...),
    target_role: Optional[str] = Form(None),
    custom_jd: Optional[str] = Form(None),
    jd_mode: Optional[str] = Form("predefined"),
    seniority_goal: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    domain: Optional[str] = Form(None),
    career_goal: Optional[str] = Form(None),
    target_location: Optional[str] = Form(None),
    target_domain: Optional[str] = Form(None),
    timeframe: Optional[str] = Form(None)
):
    session_id = get_session_id(request)
    
    # Validate that either target_role or custom_jd is provided
    if not target_role and not custom_jd:
        raise HTTPException(status_code=400, detail="Either select a predefined role or paste a custom job description")
    
    # Validate location
    if not location or not location.strip():
        raise HTTPException(status_code=400, detail="Location is required for salary analysis")
    
    # Validate career goals
    if not career_goal or not career_goal.strip():
        raise HTTPException(status_code=400, detail="Career goal is required")
    if not target_location or not target_location.strip():
        raise HTTPException(status_code=400, detail="Target location is required")
    if not timeframe or not timeframe.strip():
        raise HTTPException(status_code=400, detail="Timeframe is required")
    
    # Determine if using custom JD based on explicit mode
    is_custom_jd = bool(jd_mode == "custom" and custom_jd and custom_jd.strip())
    
    if is_custom_jd:
        role_input = (custom_jd or "").strip()
        display_role = "Custom Role"
    else:
        role_input = target_role or ""
        display_role = target_role or "Unknown"
    
    filename = file.filename or "unknown"
    if not validate_filename(filename):
        raise HTTPException(status_code=400, detail="Invalid file type or filename")
    
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")
    
    file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{filename}")
    with open(file_path, "wb") as f:
        f.write(contents)
    
    try:
        resume_text = parse_resume(file_path, filename)
        resume_text = normalize_text(resume_text)
        
        analyzer = ResumeAnalyzer(resume_text, role_input, seniority_goal, is_custom_jd=is_custom_jd)
        analysis_result = analyzer.analyze()
        
        plan = plan_gen.generate_plan(
            analysis_result,
            role_input,
            analysis_result['career_stage'],
            current_location=location.strip(),
            current_domain=domain.strip() if domain else None,
            career_goal=career_goal.strip(),
            target_location=target_location.strip(),
            target_domain=target_domain.strip() if target_domain else None,
            timeframe=int(timeframe.strip())
        )
        analysis_result['improvement_plan'] = plan
        
        keywords = plan.get('gemini_keywords') or analyzer.generate_tailored_keywords()
        analysis_result['tailored_keywords'] = keywords
        
        # Add salary analysis
        try:
            salary_analysis = get_salary_analysis(
                role=display_role,
                location=location.strip(),
                career_stage=analysis_result['career_stage'],
                alignment_score=analysis_result['role_alignment']['score']
            )
            analysis_result['salary_analysis'] = salary_analysis
        except Exception as e:
            print(f"Salary analysis failed: {e}")
            analysis_result['salary_analysis'] = {'available': False, 'message': 'Salary data temporarily unavailable'}
        
        analysis_id = db.save_analysis(
            session_id,
            display_role,
            seniority_goal,
            filename,
            analysis_result
        )
        
        analysis_result['id'] = analysis_id
        analysis_result['filename'] = filename
        
        os.remove(file_path)
        
        return JSONResponse(content=analysis_result)
    
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/app/results/{analysis_id}", response_class=HTMLResponse)
async def results_page(request: Request, analysis_id: int):
    username = request.cookies.get('username', 'Guest')
    analysis = db.get_analysis(analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return templates.TemplateResponse("results.html", {
        "request": request,
        "username": username,
        "analysis": analysis,
        "analysis_id": analysis_id
    })


@app.get("/app/history", response_class=HTMLResponse)
async def history_page(request: Request):
    session_id = get_session_id(request)
    username = request.cookies.get('username', 'Guest')
    
    history = db.get_history(session_id, limit=5)
    
    return templates.TemplateResponse("history.html", {
        "request": request,
        "username": username,
        "history": history
    })


@app.get("/api/history")
async def get_history(request: Request):
    session_id = get_session_id(request)
    history = db.get_history(session_id, limit=5)
    return JSONResponse(content=history)


@app.get("/api/report/{analysis_id}.json")
async def download_json_report(analysis_id: int):
    analysis = db.get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    json_path = os.path.join(REPORTS_DIR, f"analysis_{analysis_id}.json")
    report_gen.generate_json(analysis, json_path)
    
    return FileResponse(
        json_path,
        media_type="application/json",
        filename=f"resume_analysis_{analysis_id}.json"
    )


@app.get("/api/report/{analysis_id}.pdf")
async def download_pdf_report(analysis_id: int):
    analysis = db.get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    pdf_path = os.path.join(REPORTS_DIR, f"analysis_{analysis_id}.pdf")
    filename = analysis.get('filename', 'resume')
    
    report_gen.generate_pdf(analysis, filename, pdf_path)
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"resume_analysis_{analysis_id}.pdf"
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
