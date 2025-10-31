import os
from typing import Dict, List, Optional
from job_descriptions import get_job_description

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class ImprovementPlanGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('GOOGLE_API_KEY')
        self.gemini_available = GEMINI_AVAILABLE and self.api_key
        
        if self.gemini_available:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception:
                self.gemini_available = False
    
    def generate_plan(self, analysis_result: Dict, target_role: str, career_stage: str) -> Dict:
        plan = self._generate_rule_based_plan(analysis_result, target_role, career_stage)
        
        if self.gemini_available:
            try:
                enhanced_plan = self._enhance_with_gemini(plan, analysis_result, target_role, career_stage)
                return enhanced_plan
            except Exception as e:
                print(f"Gemini enhancement failed: {e}")
                return plan
        
        return plan
    
    def _generate_rule_based_plan(self, analysis: Dict, target_role: str, career_stage: str) -> Dict:
        plan = {
            'skills_to_acquire': [],
            'projects_to_build': [],
            'portfolio_signals': [],
            'networking_applications': [],
            'quarterly_milestones': {
                'Q1': [],
                'Q2': [],
                'Q3': [],
                'Q4': []
            }
        }
        
        gaps = analysis.get('role_alignment', {}).get('gaps', [])
        completeness_issues = analysis.get('completeness', {}).get('details', [])
        summary_issues = analysis.get('summary', {}).get('details', [])
        
        for gap in gaps[:5]:
            plan['skills_to_acquire'].append(f"Learn {gap.title()}")
        
        if career_stage in ["Student", "Recent Graduate"]:
            plan['projects_to_build'].extend([
                "Build 2-3 end-to-end projects demonstrating skills in " + target_role,
                "Contribute to 1-2 open source projects in relevant domain",
                "Complete online certifications or courses in key technologies"
            ])
        elif career_stage == "Mid-Level":
            plan['projects_to_build'].extend([
                "Lead a complex technical project with measurable impact",
                "Publish technical blog posts or speak at meetups",
                "Mentor junior team members or contribute to knowledge sharing"
            ])
        else:
            plan['projects_to_build'].extend([
                "Drive strategic initiatives with cross-functional impact",
                "Contribute to open source or industry standards",
                "Build thought leadership through publications and speaking"
            ])
        
        if 'Missing: LinkedIn, GitHub, or portfolio URL' in completeness_issues:
            plan['portfolio_signals'].append("Create LinkedIn profile highlighting key achievements")
            plan['portfolio_signals'].append("Build GitHub portfolio with 3-5 polished projects")
        
        plan['portfolio_signals'].append("Quantify all achievements with metrics (%, $, scale)")
        plan['portfolio_signals'].append("Document projects with clear problem/solution/impact structure")
        
        plan['networking_applications'].extend([
            "Join professional communities and attend industry events",
            "Network with 5-10 professionals in target role via informational interviews",
            "Apply to 10-15 relevant positions tailored to target role",
            "Get resume reviewed by 2-3 industry professionals"
        ])
        
        plan['quarterly_milestones']['Q1'] = [
            "Complete skills gap analysis and enroll in 1-2 courses",
            "Update resume with quantified achievements",
            "Start building portfolio project #1"
        ]
        
        plan['quarterly_milestones']['Q2'] = [
            "Complete portfolio project #1 with documentation",
            "Start portfolio project #2",
            "Begin networking with target companies"
        ]
        
        plan['quarterly_milestones']['Q3'] = [
            "Complete portfolio project #2",
            "Polish LinkedIn and GitHub profiles",
            "Apply to 5-10 positions and gather feedback"
        ]
        
        plan['quarterly_milestones']['Q4'] = [
            "Complete any remaining projects",
            "Intensify job applications (10-15 companies)",
            "Prepare for technical interviews and behavioral questions",
            "Secure interviews and offers in target role"
        ]
        
        return plan
    
    def _enhance_with_gemini(self, base_plan: Dict, analysis: Dict, target_role: str, career_stage: str) -> Dict:
        job_description = get_job_description(target_role)
        
        prompt = f"""You are a career advisor helping someone transition to a {target_role} role. 

Typical {target_role} Job Description:
{job_description}

Current career stage: {career_stage}
Resume analysis summary:
- Overall score: {analysis.get('overall_score', 0)}/120
- Role alignment: {analysis.get('role_alignment', {}).get('score', 0)}%
- Key gaps: {', '.join(analysis.get('role_alignment', {}).get('gaps', [])[:5])}

Based on the job description requirements above, provide:
1. 6-10 tailored impact keywords/action verbs that match this role's requirements
2. One refined, specific suggestion for each section based on what employers want

Keep response concise and actionable. Format as:
KEYWORDS: keyword1, keyword2, keyword3, ...
SKILLS: one specific skill recommendation aligned with job requirements
PROJECTS: one specific project recommendation that demonstrates required skills
PORTFOLIO: one specific portfolio recommendation to stand out to hiring managers
NETWORKING: one specific networking recommendation to break into this field
"""
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text
            
            keywords = []
            if 'KEYWORDS:' in text:
                keywords_line = text.split('KEYWORDS:')[1].split('\n')[0]
                keywords = [k.strip() for k in keywords_line.split(',')]
            
            if 'SKILLS:' in text:
                skills_line = text.split('SKILLS:')[1].split('\n')[0].strip()
                if skills_line:
                    base_plan['skills_to_acquire'].insert(0, skills_line)
            
            if 'PROJECTS:' in text:
                projects_line = text.split('PROJECTS:')[1].split('\n')[0].strip()
                if projects_line:
                    base_plan['projects_to_build'].insert(0, projects_line)
            
            if 'PORTFOLIO:' in text:
                portfolio_line = text.split('PORTFOLIO:')[1].split('\n')[0].strip()
                if portfolio_line:
                    base_plan['portfolio_signals'].insert(0, portfolio_line)
            
            if 'NETWORKING:' in text:
                networking_line = text.split('NETWORKING:')[1].split('\n')[0].strip()
                if networking_line:
                    base_plan['networking_applications'].insert(0, networking_line)
            
            base_plan['gemini_keywords'] = keywords[:10]
            
        except Exception as e:
            print(f"Error enhancing plan with Gemini: {e}")
        
        return base_plan
    
    def get_tailored_keywords(self, analysis: Dict, target_role: str) -> List[str]:
        if self.gemini_available:
            job_description = get_job_description(target_role)
            
            prompt = f"""Based on this {target_role} job description:
{job_description}

List 6-10 powerful action verbs and impact keywords that would resonate with hiring managers for this role.
Focus on verbs that demonstrate the required skills and responsibilities.

Return only the keywords, comma-separated."""
            
            try:
                response = self.model.generate_content(prompt)
                keywords = [k.strip() for k in response.text.split(',')]
                return keywords[:10]
            except Exception:
                pass
        
        from keywords import IMPACT_VERBS
        return IMPACT_VERBS[:10]
