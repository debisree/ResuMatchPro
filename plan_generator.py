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
                self.model = genai.GenerativeModel('gemini-pro')
            except Exception:
                self.gemini_available = False
    
    def generate_plan(
        self, 
        analysis_result: Dict, 
        target_role: str, 
        career_stage: str,
        current_location: str = "",
        current_domain: Optional[str] = None,
        career_goal: str = "promotion",
        target_location: str = "",
        target_domain: Optional[str] = None,
        timeframe: int = 12
    ) -> Dict:
        plan = self._generate_rule_based_plan(
            analysis_result, target_role, career_stage,
            current_location, current_domain, career_goal,
            target_location, target_domain, timeframe
        )
        
        if self.gemini_available:
            try:
                enhanced_plan = self._enhance_with_gemini(
                    plan, analysis_result, target_role, career_stage,
                    current_location, current_domain, career_goal,
                    target_location, target_domain, timeframe
                )
                return enhanced_plan
            except Exception as e:
                print(f"Gemini enhancement failed: {e}")
                return plan
        
        return plan
    
    def _generate_rule_based_plan(
        self, 
        analysis: Dict, 
        target_role: str, 
        career_stage: str,
        current_location: str = "",
        current_domain: Optional[str] = None,
        career_goal: str = "promotion",
        target_location: str = "",
        target_domain: Optional[str] = None,
        timeframe: int = 12
    ) -> Dict:
        plan = {
            'skills_to_acquire': [],
            'projects_to_build': [],
            'portfolio_signals': [],
            'networking_applications': [],
            'immediate_actions': [],
            'short_term': [],
            'long_term': [],
            'career_goal_context': {
                'goal_type': career_goal,
                'current_location': current_location,
                'target_location': target_location,
                'current_domain': current_domain,
                'target_domain': target_domain,
                'timeframe_months': timeframe,
                'is_relocation': current_location != target_location,
                'is_domain_change': current_domain != target_domain
            }
        }
        
        gaps = analysis.get('role_alignment', {}).get('gaps', [])
        completeness_issues = analysis.get('completeness', {}).get('details', [])
        summary_issues = analysis.get('summary', {}).get('details', [])
        alignment_score = analysis.get('role_alignment', {}).get('score', 0)
        
        # Detailed skills acquisition with learning path
        for gap in gaps[:8]:
            skill_detail = self._get_skill_learning_path(gap, target_role, career_stage)
            plan['skills_to_acquire'].append(skill_detail)
        
        # Customized project recommendations based on role and gaps
        project_recommendations = self._generate_project_recommendations(
            target_role, career_stage, gaps, alignment_score
        )
        plan['projects_to_build'].extend(project_recommendations)
        
        # Portfolio and profile improvements
        portfolio_improvements = self._generate_portfolio_improvements(
            completeness_issues, target_role, alignment_score
        )
        plan['portfolio_signals'].extend(portfolio_improvements)
        
        # Networking and application strategy
        networking_strategy = self._generate_networking_strategy(
            career_stage, target_role, alignment_score
        )
        plan['networking_applications'].extend(networking_strategy)
        
        # Timeline recommendations (point-wise instead of quarterly)
        timeline = self._generate_timeline_recommendations(
            career_stage, alignment_score, gaps, career_goal, 
            current_location, target_location, current_domain, target_domain, timeframe
        )
        plan['immediate_actions'] = timeline['immediate']
        plan['short_term'] = timeline['short_term']
        plan['long_term'] = timeline['long_term']
        
        return plan
    
    def _get_skill_learning_path(self, skill: str, target_role: str, career_stage: str) -> str:
        skill_lower = skill.lower()
        
        # Programming languages
        if any(lang in skill_lower for lang in ['python', 'javascript', 'java', 'c++', 'go', 'rust']):
            return f"Master {skill} through hands-on projects - complete 3-5 real-world projects, contribute to open source, and earn relevant certification (e.g., Python PCEP, Java OCA)"
        
        # Cloud platforms
        if any(cloud in skill_lower for cloud in ['aws', 'azure', 'gcp', 'cloud']):
            return f"Gain {skill} proficiency - complete official certification (e.g., AWS Solutions Architect, Azure Administrator), build 2-3 cloud-hosted projects with CI/CD"
        
        # Data science/ML
        if any(ds in skill_lower for ds in ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit']):
            return f"Build {skill} expertise - complete Coursera ML specialization or fast.ai course, implement 3-5 ML models on real datasets, participate in 2-3 Kaggle competitions"
        
        # Databases
        if any(db in skill_lower for db in ['sql', 'postgresql', 'mongodb', 'database']):
            return f"Develop {skill} competency - design and implement 3 complex database schemas, optimize query performance, learn indexing and transaction management, earn MySQL/PostgreSQL certification"
        
        # DevOps/Infrastructure
        if any(devops in skill_lower for devops in ['docker', 'kubernetes', 'jenkins', 'ci/cd', 'terraform']):
            return f"Master {skill} - set up complete CI/CD pipeline for 2-3 projects, containerize applications, automate deployments, earn relevant certification (CKA for Kubernetes)"
        
        # Generic fallback
        return f"Acquire {skill} through structured learning - enroll in top-rated course (Udemy/Coursera), practice with 3-5 hands-on projects, build portfolio demonstrating proficiency"
    
    def _generate_project_recommendations(self, target_role: str, career_stage: str, gaps: List[str], alignment_score: int) -> List[str]:
        projects = []
        role_lower = target_role.lower()
        
        # Role-specific project recommendations
        if 'data scientist' in role_lower or 'machine learning' in role_lower:
            projects.append("Build end-to-end ML pipeline: data collection → preprocessing → model training → deployment with Flask/FastAPI → monitoring. Document all steps and results.")
            projects.append("Complete 3-5 Kaggle competitions in different domains (NLP, Computer Vision, Time Series). Achieve top 20% ranking in at least one competition.")
            projects.append("Create a production-ready ML project with A/B testing, model versioning (MLflow), and automated retraining pipeline. Deploy on AWS/GCP.")
        
        elif 'full stack' in role_lower or 'software engineer' in role_lower:
            projects.append("Build a complete CRUD application with authentication, database (PostgreSQL/MongoDB), REST API, and modern frontend (React/Vue). Deploy on cloud with CI/CD.")
            projects.append("Contribute to 2-3 popular open source projects - fix bugs, add features, improve documentation. Get at least 3 PRs merged.")
            projects.append("Create a microservices architecture project with 3-4 services, API gateway, message queue (RabbitMQ/Kafka), and Docker/Kubernetes deployment.")
        
        elif 'frontend' in role_lower:
            projects.append("Build 3-5 responsive, accessible web applications using modern framework (React/Vue/Angular) with state management, routing, and API integration.")
            projects.append("Create a component library with Storybook documentation, unit tests (Jest), and publish to npm. Demonstrate reusability and best practices.")
            projects.append("Develop a Progressive Web App (PWA) with offline support, push notifications, and optimal performance (Lighthouse score 90+).")
        
        elif 'backend' in role_lower or 'api' in role_lower:
            projects.append("Design and implement RESTful API with authentication (JWT/OAuth), rate limiting, caching (Redis), and comprehensive API documentation (Swagger).")
            projects.append("Build a scalable backend system handling 10,000+ requests/second - use load balancing, database optimization, and horizontal scaling strategies.")
            projects.append("Create microservices with event-driven architecture using message queues (RabbitMQ/Kafka), implement circuit breaker pattern, and monitoring (Prometheus/Grafana).")
        
        elif 'devops' in role_lower or 'cloud' in role_lower:
            projects.append("Implement complete CI/CD pipeline using Jenkins/GitLab CI with automated testing, security scanning, and multi-environment deployments (dev/staging/prod).")
            projects.append("Set up Kubernetes cluster with auto-scaling, monitoring (Prometheus), logging (ELK stack), and deploy 3-4 microservices with zero-downtime deployments.")
            projects.append("Build Infrastructure as Code (IaC) using Terraform/CloudFormation - create reusable modules for VPC, compute, storage, and implement disaster recovery.")
        
        elif 'data analyst' in role_lower:
            projects.append("Create 3-5 interactive dashboards using Tableau/Power BI analyzing real datasets (sales, marketing, operations) with actionable insights and KPI tracking.")
            projects.append("Perform comprehensive data analysis project: data cleaning → exploratory analysis → statistical testing → visualization → business recommendations. Document findings in professional report.")
            projects.append("Build automated reporting system using Python (Pandas, Matplotlib) that generates weekly/monthly reports from database queries and emails stakeholders.")
        
        # Add career-stage specific additions
        if career_stage in ["Student", "Recent Graduate"]:
            projects.append("Complete 2-3 online courses with certificates (Coursera, edX, Udacity) in core technologies for " + target_role + " role.")
        elif career_stage == "Mid-Level":
            projects.append("Lead a technical initiative at work or in open source - mentor others, make architectural decisions, and document learnings in technical blog posts.")
        
        return projects[:6]  # Limit to top 6 most relevant
    
    def _generate_portfolio_improvements(self, completeness_issues: List[str], target_role: str, alignment_score: int) -> List[str]:
        improvements = []
        
        # Check for missing elements
        issues_str = ' '.join(completeness_issues)
        
        if 'LinkedIn' in issues_str or 'portfolio' in issues_str:
            improvements.append("Create professional LinkedIn profile: professional photo, compelling headline, detailed experience with quantified achievements, 5+ recommendations, 500+ connections")
            improvements.append("Build portfolio website showcasing 4-6 best projects with live demos, source code (GitHub), detailed case studies (problem → solution → impact), and technical blog posts")
        
        if 'GitHub' in issues_str:
            improvements.append("Build strong GitHub presence: 4-6 pinned repositories with excellent README files, consistent contribution graph (green squares), contributions to popular open source projects")
        
        improvements.append("Quantify every achievement with metrics: 'Improved performance by 40%', 'Reduced costs by $50K annually', 'Led team of 5 engineers', 'Processed 1M+ records daily'")
        improvements.append("Rewrite bullet points using STAR method (Situation → Task → Action → Result) with powerful action verbs (architected, optimized, spearheaded, orchestrated)")
        improvements.append("Add technical skills section with proficiency levels: Expert (Python, SQL), Advanced (AWS, Docker), Intermediate (Kubernetes). Match keywords from " + target_role + " job descriptions")
        
        if alignment_score < 60:
            improvements.append("Create 'Relevant Projects' section highlighting work that aligns with " + target_role + " requirements, even if from side projects or coursework")
        
        improvements.append("Get resume professionally reviewed by 2-3 industry professionals in " + target_role + " field. Incorporate feedback and A/B test different versions")
        
        return improvements[:8]
    
    def _generate_networking_strategy(self, career_stage: str, target_role: str, alignment_score: int) -> List[str]:
        strategy = []
        
        strategy.append("Conduct 10-15 informational interviews with professionals in " + target_role + " positions at target companies - prepare thoughtful questions, build genuine relationships")
        strategy.append("Join 3-5 relevant communities: Reddit (r/datascience, r/webdev), Discord servers, Slack groups. Actively participate, answer questions, share knowledge")
        strategy.append("Attend 5-10 industry events: local meetups, tech conferences, workshops. Present a lightning talk or poster if possible. Follow up with meaningful connections")
        
        if career_stage in ["Student", "Recent Graduate"]:
            strategy.append("Apply for internships and entry-level positions: target 50-100 applications over 3-6 months. Tailor resume and cover letter for each application")
            strategy.append("Leverage university career services, alumni network, and career fairs. Request referrals from alumni working at target companies")
        elif career_stage == "Mid-Level":
            strategy.append("Target 30-50 companies where you want to work. Get warm introductions through mutual connections. Apply for mid-level/senior positions matching your experience")
            strategy.append("Build thought leadership: write technical blog posts (2-4 per month), contribute to industry discussions on LinkedIn/Twitter, share project learnings")
        else:
            strategy.append("Leverage your network for direct referrals to senior/leadership positions. Focus on quality over quantity - target 15-20 companies strategically")
            strategy.append("Establish thought leadership: speak at conferences, write authoritative articles, mentor others, contribute to industry standards/open source governance")
        
        if alignment_score < 50:
            strategy.append("Consider contract/freelance projects in " + target_role + " to build experience while job searching. Use platforms like Upwork, Toptal, or direct client outreach")
        
        strategy.append("Prepare for interviews: practice 50+ coding problems (LeetCode/HackerRank), rehearse behavioral questions (STAR method), do mock interviews with peers/professionals")
        strategy.append("Follow up systematically: send thank-you notes after interviews, maintain relationship with recruiters, ask for feedback on rejections to improve")
        
        return strategy[:10]
    
    def _generate_timeline_recommendations(
        self, 
        career_stage: str, 
        alignment_score: int, 
        gaps: List[str],
        career_goal: str = "promotion",
        current_location: str = "",
        target_location: str = "",
        current_domain: Optional[str] = None,
        target_domain: Optional[str] = None,
        timeframe: int = 12
    ) -> Dict:
        timeline = {
            'immediate': [],  # 0-1 month
            'short_term': [],  # 1-6 months
            'long_term': []  # 6-12 months (only for 12-month timeline)
        }
        
        is_relocation = current_location != target_location
        is_domain_change = current_domain != target_domain if current_domain and target_domain else False
        is_pivot = career_goal == "pivot"
        is_lateral = career_goal == "lateral_move"
        
        # Immediate actions (0-1 month) - Career goal specific
        timeline['immediate'].append("Update resume with quantified achievements and ATS-friendly formatting. Get it reviewed by 2-3 professionals")
        
        if is_pivot:
            timeline['immediate'].append(f"Research {target_domain or 'target domain'} industry: read 5-10 industry reports, follow key influencers, join domain-specific communities")
            timeline['immediate'].append("Reframe existing experience to highlight transferable skills relevant to new career path")
        elif is_lateral:
            timeline['immediate'].append(f"Research {target_domain or 'target domain'} industry: understand key players, trends, and how your current skills translate")
            timeline['immediate'].append("Highlight transferable skills and domain-agnostic achievements (e.g., scalability, performance optimization, problem-solving)")
        else:
            timeline['immediate'].append("Optimize LinkedIn profile showcasing readiness for promotion to next level with leadership achievements")
        
        timeline['immediate'].append("Identify top 3-5 skill gaps and enroll in relevant online courses (Coursera, Udemy, edX)")
        
        if alignment_score < 50:
            timeline['immediate'].append("Start first portfolio project addressing biggest skill gap - dedicate 10-15 hours/week")
        
        if is_relocation:
            timeline['immediate'].append(f"Join {target_location}-specific professional groups (LinkedIn, Meetup) and start building local network")
        
        # Short-term actions (1-6 months)
        if is_domain_change:
            timeline['short_term'].append(f"Complete 2-3 domain-specific projects showcasing expertise in {target_domain or 'target industry'} - focus on industry-relevant problems")
            timeline['short_term'].append(f"Earn domain-specific certification or complete specialized training program in {target_domain or 'target field'}")
        else:
            timeline['short_term'].append("Complete 2-3 significant portfolio projects with detailed documentation, live demos, and GitHub repositories")
            timeline['short_term'].append("Earn 1-2 relevant certifications (AWS, Google Cloud, specific technologies) to validate skills")
        
        if is_relocation:
            timeline['short_term'].append(f"Network actively in {target_location}: attend 4-6 local meetups/conferences, conduct informational interviews with professionals in target city")
            timeline['short_term'].append(f"Research {target_location} job market: identify top employers, typical salary ranges, cost of living considerations")
        else:
            timeline['short_term'].append("Conduct 5-10 informational interviews and expand professional network by 50+ meaningful connections")
        
        timeline['short_term'].append("Contribute to 2-3 open source projects - get at least 3 pull requests merged")
        
        if is_pivot:
            timeline['short_term'].append("Build transitional narrative: create compelling story explaining career pivot, emphasizing transferable skills and genuine interest")
            timeline['short_term'].append("Seek mentorship from 2-3 professionals who successfully made similar career transitions")
        elif is_lateral:
            timeline['short_term'].append(f"Build domain-specific portfolio: create 2-3 projects solving {target_domain or 'target industry'} problems using your existing technical skills")
            timeline['short_term'].append(f"Network with professionals in {target_domain or 'target domain'}: conduct 5-8 informational interviews to understand industry expectations")
            timeline['short_term'].append("Emphasize consistency: maintain same seniority level while demonstrating domain adaptability through relevant projects")
        else:
            timeline['short_term'].append("Demonstrate leadership: lead initiatives, mentor others, take on stretch assignments to showcase promotion readiness")
        
        timeline['short_term'].append("Start applying to positions: tailor resume for each application, aim for 20-30 quality applications")
        timeline['short_term'].append("Practice technical interviews: solve 50+ coding problems, do 3-5 mock interviews")
        
        if career_stage in ["Student", "Recent Graduate"]:
            timeline['short_term'].append("Build strong foundation in core technologies through structured courses and hands-on practice (20+ hours/week)")
        
        # For 6-month timeline, add closing actions to short-term and skip long-term
        if timeframe == 6:
            timeline['short_term'].append("⏰ 6-month accelerated timeline: Intensify efforts - dedicate 15-20 hours/week to upskilling, networking, and applications")
            timeline['short_term'].append("Target 40-50 quality applications over next 4-5 months with systematic follow-ups")
            timeline['short_term'].append("Secure multiple offers through strategic networking and strong interview performance. Negotiate compensation package")
            
            if alignment_score >= 70:
                timeline['short_term'].append("Focus on interview preparation and applications - you're already well-qualified, now it's about landing the right opportunity quickly")
            else:
                timeline['short_term'].append("Parallel track: continue skill building while actively applying - demonstrate learning trajectory during interviews")
            
            # DO NOT populate long_term for 6-month timeline
            timeline['long_term'] = []
        
        # Long-term actions (6-12 months) - ONLY for 12-month timeline
        else:
            timeline['long_term'].append("Achieve measurable expertise: portfolio with 5-6 production-quality projects, 2-3 certifications, strong GitHub presence")
            
            if is_pivot:
                timeline['long_term'].append(f"Establish credibility in {target_domain or 'new field'}: publish 5-8 industry-specific articles/case studies, speak at domain conferences")
                timeline['long_term'].append("Complete career transition: secure role in new field, leverage transferable skills while continuing to build domain expertise")
            elif is_lateral:
                timeline['long_term'].append(f"Become domain expert: publish 3-5 technical articles about applying your skills to {target_domain or 'target industry'} challenges")
                timeline['long_term'].append(f"Secure lateral move: target companies in {target_domain or 'target domain'} where your technical expertise is valued at same seniority level")
                timeline['long_term'].append("Position as domain switcher: show you bring fresh perspective from previous domain while understanding new industry context")
            else:
                timeline['long_term'].append("Establish thought leadership: publish 10-15 technical blog posts, give 2-3 talks at meetups, mentor 2-3 people")
                timeline['long_term'].append("Position for promotion: take ownership of high-impact projects, demonstrate strategic thinking and leadership capabilities")
            
            if is_relocation:
                timeline['long_term'].append(f"Execute relocation to {target_location}: secure job offer, plan move logistics, establish connections before relocating")
            
            timeline['long_term'].append("Expand to 50-70 total applications with systematic follow-ups. Convert at least 10% to interviews")
            timeline['long_term'].append("Secure multiple offers through strategic networking and strong technical interviews. Negotiate compensation package")
            
            if alignment_score >= 70:
                timeline['long_term'].append("Focus on interview preparation and applications - you're already well-qualified, now it's about landing the right opportunity")
            else:
                timeline['long_term'].append("Continue skill building while applying - demonstrate learning trajectory and growth mindset during interviews")
        
        return timeline
    
    def _enhance_with_gemini(
        self, 
        base_plan: Dict, 
        analysis: Dict, 
        target_role: str, 
        career_stage: str,
        current_location: str = "",
        current_domain: Optional[str] = None,
        career_goal: str = "promotion",
        target_location: str = "",
        target_domain: Optional[str] = None,
        timeframe: int = 12
    ) -> Dict:
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
                keywords = [k.strip() for k in keywords_line.split(',') if k.strip()]
            
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
            
            base_plan['gemini_keywords'] = keywords
            
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
                keywords = [k.strip() for k in response.text.split(',') if k.strip()]
                return keywords
            except Exception:
                pass
        
        from keywords import IMPACT_VERBS
        return IMPACT_VERBS[:10]
