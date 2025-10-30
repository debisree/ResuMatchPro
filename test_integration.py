import os
from database import Database
from parser import parse_resume, normalize_text
from analyzer import ResumeAnalyzer
from plan_generator import ImprovementPlanGenerator
from report_generator import ReportGenerator

print("Testing integration...")

db = Database()
plan_gen = ImprovementPlanGenerator()
report_gen = ReportGenerator()

resume_file = "sample_resume.txt"
target_role = "Data Scientist in Healthcare"
session_id = "test_session_123"

print("\n1. Parsing resume...")
resume_text = parse_resume(resume_file, resume_file)
resume_text = normalize_text(resume_text)

print("2. Analyzing resume...")
analyzer = ResumeAnalyzer(resume_text, target_role, "Mid")
analysis_result = analyzer.analyze()

print("3. Generating improvement plan...")
plan = plan_gen.generate_plan(analysis_result, target_role, analysis_result['career_stage'])
analysis_result['improvement_plan'] = plan
keywords = analyzer.generate_tailored_keywords()
analysis_result['tailored_keywords'] = keywords

print("4. Saving to database...")
analysis_id = db.save_analysis(session_id, target_role, "Mid", resume_file, analysis_result)
print(f"   Saved with ID: {analysis_id}")

print("5. Retrieving from database...")
retrieved = db.get_analysis(analysis_id)
print(f"   Retrieved: {retrieved['filename']}, Score: {retrieved['overall_score']}")

print("6. Getting history...")
history = db.get_history(session_id, limit=5)
print(f"   History items: {len(history)}")

print("7. Generating JSON report...")
json_path = "tmp/reports/test_report.json"
os.makedirs("tmp/reports", exist_ok=True)
report_gen.generate_json(retrieved, json_path)
print(f"   JSON saved to: {json_path}")

print("8. Generating PDF report...")
pdf_path = "tmp/reports/test_report.pdf"
report_gen.generate_pdf(retrieved, resume_file, pdf_path)
print(f"   PDF saved to: {pdf_path}")

print("\n" + "="*60)
print("INTEGRATION TEST PASSED!")
print("="*60)
print(f"All components working correctly:")
print(f"  - Resume parsing: ✓")
print(f"  - Analysis engine: ✓")
print(f"  - Plan generation: ✓")
print(f"  - Database storage: ✓")
print(f"  - Report generation (JSON): ✓")
print(f"  - Report generation (PDF): ✓")
