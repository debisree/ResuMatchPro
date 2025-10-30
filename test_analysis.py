import sys
from parser import parse_resume, normalize_text
from analyzer import ResumeAnalyzer
from plan_generator import ImprovementPlanGenerator

resume_file = "sample_resume.txt"
target_role = "Machine Learning Engineer"

try:
    print("Testing resume analysis...")
    print(f"Parsing {resume_file}...")
    
    resume_text = parse_resume(resume_file, resume_file)
    resume_text = normalize_text(resume_text)
    
    print(f"Resume text length: {len(resume_text)} characters")
    print(f"\nAnalyzing for role: {target_role}")
    
    analyzer = ResumeAnalyzer(resume_text, target_role, None)
    analysis_result = analyzer.analyze()
    
    print(f"\n{'='*60}")
    print("ANALYSIS RESULTS")
    print(f"{'='*60}")
    print(f"Overall Score: {analysis_result['overall_score']}/{analysis_result['max_score']}")
    print(f"Verdict: {analysis_result['verdict']}")
    print(f"Career Stage: {analysis_result['career_stage']}")
    print(f"\nCompleteness: {analysis_result['completeness']['score']}/30 ({analysis_result['completeness']['band']})")
    print(f"Summary: {analysis_result['summary']['score']}/30 ({analysis_result['summary']['band']})")
    print(f"Education: {analysis_result['education']['score']}/30 ({analysis_result['education']['band']})")
    print(f"Employment: {analysis_result['employment']['score']}/30 ({analysis_result['employment']['band']})")
    print(f"\nATS Readiness: {analysis_result['ats_readiness']['verdict']}")
    print(f"Role Alignment: {analysis_result['role_alignment']['score']}%")
    
    print(f"\n{'='*60}")
    print("Generating improvement plan...")
    plan_gen = ImprovementPlanGenerator()
    plan = plan_gen.generate_plan(analysis_result, target_role, analysis_result['career_stage'])
    
    print(f"Skills to acquire: {len(plan.get('skills_to_acquire', []))} items")
    print(f"Projects to build: {len(plan.get('projects_to_build', []))} items")
    print(f"Quarterly milestones: {len(plan.get('quarterly_milestones', {}))} quarters")
    
    print(f"\n{'='*60}")
    print("TEST PASSED - Analysis completed successfully!")
    print(f"{'='*60}")
    
except Exception as e:
    print(f"\nERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
