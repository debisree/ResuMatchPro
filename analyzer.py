import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from keywords import (
    SECTION_HINTS, TOOL_HINTS, DOMAIN_HINTS, ROLE_TITLES,
    IMPACT_VERBS, EDUCATION_KEYWORDS, LEADERSHIP_KEYWORDS,
    METRIC_PATTERNS, ROLE_VOCABULARIES
)
from parser import (
    detect_sections, count_bullets_in_section, extract_metrics,
    extract_emails, extract_phones, extract_urls, extract_years,
    extract_date_ranges, calculate_years_experience, get_text_window
)
from job_descriptions import get_job_description


class ResumeAnalyzer:
    def __init__(self, resume_text: str, target_role: Optional[str] = None, seniority_goal: Optional[str] = None):
        self.text = resume_text.lower()
        self.original_text = resume_text
        self.target_role = target_role.lower() if target_role else None
        self.seniority_goal = seniority_goal
        
        self.emails = extract_emails(resume_text)
        self.phones = extract_phones(resume_text)
        self.urls = extract_urls(resume_text)
        self.years = extract_years(resume_text)
        self.date_ranges = extract_date_ranges(resume_text)
        self.years_experience = calculate_years_experience(self.date_ranges)
        
        self.sections = detect_sections(resume_text, SECTION_HINTS)
        self.metrics = extract_metrics(resume_text, METRIC_PATTERNS)
        
        self.resume_truths = self._extract_resume_truths()
    
    def _extract_resume_truths(self) -> Dict[str, List[str]]:
        truths = {
            'roles': [],
            'domains': [],
            'tools': [],
            'metrics': self.metrics,
            'achievements': []
        }
        
        for role in ROLE_TITLES:
            if role in self.text:
                truths['roles'].append(role)
        
        for domain in DOMAIN_HINTS:
            if domain in self.text:
                truths['domains'].append(domain)
        
        for tool in TOOL_HINTS:
            if tool in self.text:
                truths['tools'].append(tool)
        
        for verb in IMPACT_VERBS:
            if verb in self.text:
                truths['achievements'].append(verb)
        
        return truths
    
    def detect_career_stage(self) -> str:
        exp = self.years_experience
        
        has_leadership = any(kw in self.text for kw in LEADERSHIP_KEYWORDS)
        
        if exp < 1:
            return "Student"
        elif exp < 2:
            return "Recent Graduate"
        elif exp < 8:
            return "Mid-Level" if has_leadership else "Mid-Level"
        else:
            return "Senior"
    
    def score_completeness(self) -> Dict:
        score = 0
        max_score = 30
        details = []
        warnings = []
        
        if self.emails:
            score += 4
        else:
            details.append("Missing: Email address")
        
        if self.phones:
            score += 3
        else:
            details.append("Missing: Phone number")
        
        if self.urls['linkedin'] or self.urls['github'] or self.urls['portfolio']:
            score += 2
        else:
            details.append("Missing: LinkedIn, GitHub, or portfolio URL")
        
        if 'summary' in self.sections:
            score += 5
        else:
            details.append("Missing: Professional summary or objective")
        
        if 'experience' in self.sections:
            score += 6
        else:
            details.append("Missing: Work experience section")
        
        if 'education' in self.sections:
            score += 6
        else:
            details.append("Missing: Education section")
        
        if 'skills' in self.sections:
            score += 3
        else:
            details.append("Missing: Skills section")
        
        word_count = len(self.original_text.split())
        if 200 <= word_count <= 800:
            score += 1
        else:
            if word_count < 200:
                details.append(f"Resume is too short ({word_count} words)")
            else:
                details.append(f"Resume is too long ({word_count} words)")
        
        additional_sections = ['projects', 'leadership', 'research', 'publications', 
                              'awards', 'certifications', 'volunteer', 'opensource']
        thin_sections = []
        for sec in additional_sections:
            if sec in self.sections:
                line_num = self.sections[sec]['line_number']
                bullet_count = count_bullets_in_section(self.original_text, line_num)
                if bullet_count < 2:
                    thin_sections.append(sec.title())
        
        if thin_sections:
            warnings.append(f"Thin sections (< 2 bullets): {', '.join(thin_sections)}")
        
        return {
            'score': score,
            'max_score': max_score,
            'details': details,
            'warnings': warnings,
            'band': self._get_band(score, max_score)
        }
    
    def score_summary(self) -> Dict:
        score = 0
        max_score = 30
        details = []
        
        if 'summary' not in self.sections:
            return {
                'score': 0,
                'max_score': max_score,
                'details': ['No summary section found'],
                'band': 'Needs Attention'
            }
        
        summary_line = self.sections['summary']['line_number']
        next_section_line = None
        
        section_lines = sorted([s['line_number'] for s in self.sections.values()])
        for line in section_lines:
            if line > summary_line:
                next_section_line = line
                break
        
        lines = self.original_text.split('\n')
        if next_section_line:
            summary_text = '\n'.join(lines[summary_line:next_section_line])
        else:
            summary_text = '\n'.join(lines[summary_line:summary_line + 10])
        
        summary_window = get_text_window(summary_text, 150)
        summary_lower = summary_window.lower()
        
        coverage_score = 0
        if any(role in summary_lower for role in self.resume_truths['roles'][:3]):
            coverage_score += 2
        if any(domain in summary_lower for domain in self.resume_truths['domains'][:2]):
            coverage_score += 2
        if any(tool in summary_lower for tool in self.resume_truths['tools'][:5]):
            coverage_score += 2
        if len(self.resume_truths['metrics']) > 0 and any(str(m) in summary_window for m in self.resume_truths['metrics'][:2]):
            coverage_score += 2
        score += min(coverage_score, 8)
        
        word_count = len(summary_window.split())
        stage = self.detect_career_stage()
        if stage in ["Student", "Recent Graduate"]:
            ideal_range = (50, 100)
        else:
            ideal_range = (75, 150)
        
        if ideal_range[0] <= word_count <= ideal_range[1]:
            score += 4
        elif word_count < ideal_range[0]:
            score += 2
            details.append(f"Summary is too brief ({word_count} words). Aim for {ideal_range[0]}-{ideal_range[1]} words.")
        else:
            score += 1
            details.append(f"Summary is too long ({word_count} words). Aim for {ideal_range[0]}-{ideal_range[1]} words.")
        
        distinct_domains = len(set([d for d in DOMAIN_HINTS if d in summary_lower]))
        distinct_tools = len(set([t for t in TOOL_HINTS if t in summary_lower]))
        distinct_roles = len(set([r for r in ROLE_TITLES if r in summary_lower]))
        
        specificity = min(distinct_domains + distinct_tools + distinct_roles, 6)
        score += specificity
        if specificity < 3:
            details.append("Add more specific tools, domains, or role keywords")
        
        impact_count = sum(1 for verb in IMPACT_VERBS if verb in summary_lower)
        impact_density = (impact_count / max(word_count, 1)) * 50
        impact_score = min(int(impact_density * 6), 6)
        score += impact_score
        if impact_score == 0:
            details.append("Start sentences with strong action verbs: 'Developed', 'Led', 'Architected', 'Optimized', 'Built' instead of passive phrases")
        elif impact_score < 3:
            details.append(f"Use 2-3 more impact verbs in summary. Examples: 'Spearheaded', 'Drove', 'Engineered', 'Scaled', 'Delivered'")
        
        evidence_count = len([m for m in METRIC_PATTERNS if re.search(m, summary_window, re.IGNORECASE)])
        evidence_density = (evidence_count / max(word_count, 1)) * 50
        evidence_score = min(int(evidence_density * 4), 4)
        score += evidence_score
        if evidence_score == 0:
            details.append("Add 1-2 quantifiable achievements in summary: 'Built system serving 10K+ users' or 'Reduced processing time by 40%'")
        elif evidence_score < 2:
            details.append("Add one more metric to strengthen summary impact (team size, project scale, or performance improvement)")
        
        faithfulness_penalty = 0
        if any(kw in summary_lower for kw in ['led', 'managed', 'leadership']):
            if not any(kw in self.text for kw in LEADERSHIP_KEYWORDS):
                faithfulness_penalty -= 2
                details.append("Leadership claims in summary not supported by resume")
        
        if 'award' in summary_lower or 'recognition' in summary_lower:
            if 'awards' not in self.sections:
                faithfulness_penalty -= 1
        
        score = max(0, score + faithfulness_penalty)
        
        return {
            'score': score,
            'max_score': max_score,
            'details': details if details else ['Summary is well-crafted'],
            'band': self._get_band(score, max_score)
        }
    
    def score_education(self) -> Dict:
        score = 0
        max_score = 30
        details = []
        
        if 'education' not in self.sections:
            return {
                'score': 0,
                'max_score': max_score,
                'details': ['No education section found'],
                'band': 'Needs Attention'
            }
        
        score += 8
        
        degree_count = sum(1 for keyword in EDUCATION_KEYWORDS if keyword in self.text)
        degree_score = min(degree_count * 2, 10)
        score += degree_score
        
        if degree_score == 0:
            details.append("Include your degree type: Bachelor's (BS/BA), Master's (MS/MA), or PhD")
        elif degree_score < 4:
            details.append("Specify full degree name (e.g., 'BS Computer Science' or 'Master of Business Administration')")
        
        if self.years:
            year_score = min(len(self.years), 7)
            score += year_score
            if year_score < 7:
                details.append(f"Gained {year_score} points for dates. Add more years/dates to reach full {7-year_score} additional points")
        else:
            details.append("Missing 7 points: Add graduation year (e.g., 'BS Computer Science, 2020' or 'Expected May 2025')")
        
        thesis_found = 'thesis' in self.text or 'capstone' in self.text or 'dissertation' in self.text
        if thesis_found:
            score += 2
        else:
            if self.detect_career_stage() in ["Student", "Recent Graduate"]:
                details.append("Missing 2 points: Add thesis/capstone/final project to reach 29-30/30")
            else:
                details.append("Optional: Add thesis/capstone/dissertation if applicable (+2 points)")
        
        gpa_pattern = r'(?:gpa|grade point average)[:\s]+(\d+\.\d+)'
        gpa_match = re.search(gpa_pattern, self.text, re.IGNORECASE)
        
        honors_keywords = ['honors', 'summa cum laude', 'magna cum laude', 'cum laude', 
                          'dean\'s list', 'distinction', 'merit']
        has_honors = any(kw in self.text for kw in honors_keywords)
        
        if gpa_match:
            gpa = float(gpa_match.group(1))
            if gpa >= 3.5:
                score += 3
            elif gpa >= 3.0:
                score += 1
            else:
                details.append("GPA < 3.0 - consider removing unless required")
        elif has_honors:
            score += 3
        else:
            if self.detect_career_stage() in ["Student", "Recent Graduate"]:
                details.append("Missing 3 points: Add GPA if >= 3.0 or academic honors (Dean's List, Cum Laude, etc.)")
            else:
                details.append("Optional: Add GPA (if 3.5+) or academic honors for +1 to +3 points")
        
        return {
            'score': score,
            'max_score': max_score,
            'details': details if details else ['Education section is complete'],
            'band': self._get_band(score, max_score)
        }
    
    def score_employment(self) -> Dict:
        score = 0
        max_score = 30
        details = []
        
        if 'experience' not in self.sections:
            return {
                'score': 0,
                'max_score': max_score,
                'details': ['No experience section found'],
                'band': 'Needs Attention'
            }
        
        score += 8
        
        exp_line = self.sections['experience']['line_number']
        bullet_count = count_bullets_in_section(self.original_text, exp_line)
        
        bullet_score = min(bullet_count // 2, 6)
        score += bullet_score
        if bullet_count == 0:
            details.append(f"Missing {6-bullet_score} points: Add 8-12 bullet points describing your responsibilities and achievements")
        elif bullet_count < 6:
            details.append(f"Missing {6-bullet_score} points: Have {bullet_count} bullets, add {8-bullet_count} more for optimal impact (aim for 8-12 total)")
        elif bullet_count < 8:
            details.append(f"Good! {bullet_count} bullets present. Consider adding 1-2 more to showcase full impact")
        
        metrics_in_exp = len(self.metrics)
        quantified_score = min(metrics_in_exp, 8)
        score += quantified_score
        if metrics_in_exp == 0:
            details.append(f"Missing {8-quantified_score} points: Add quantifiable outcomes - Examples: 'Served 10K+ users', 'Reduced costs by 30%', 'Led team of 5', 'Improved performance by 2x', 'Completed in 3 months'")
        elif metrics_in_exp < 3:
            details.append(f"Missing {8-quantified_score} points: Have {metrics_in_exp} metric(s). Add {5-metrics_in_exp} more - try: team size, user counts, time saved, % improvements, project budget/scope")
        elif metrics_in_exp < 5:
            details.append(f"Missing {8-quantified_score} points: Strong with {metrics_in_exp} metrics! Add {8-metrics_in_exp} more if possible (even approximate numbers like '50+ clients' count)")
        elif metrics_in_exp < 8:
            details.append(f"Excellent! {metrics_in_exp} metrics found. Add {8-metrics_in_exp} more to reach perfect score")
        
        exp_years = self.years_experience
        if exp_years < 1:
            exp_score = 2
        elif exp_years < 3:
            exp_score = 4
        elif exp_years < 8:
            exp_score = 6
        else:
            exp_score = 8
        score += exp_score
        
        if not self.date_ranges:
            details.append("Missing points: Add date ranges for all positions (e.g., 'June 2020 - Present' or '2019-2021')")
        
        return {
            'score': score,
            'max_score': max_score,
            'details': details if details else ['Employment section is strong'],
            'band': self._get_band(score, max_score)
        }
    
    def check_ats_readiness(self) -> Dict:
        signals = []
        recommendations = []
        
        non_ascii_count = sum(1 for c in self.original_text if ord(c) > 127)
        non_ascii_pct = (non_ascii_count / max(len(self.original_text), 1)) * 100
        if non_ascii_pct > 5:
            signals.append(f"High non-ASCII character usage ({non_ascii_pct:.1f}%)")
            recommendations.append("Replace special characters with ASCII equivalents")
        
        decorative_chars = ['│', '┤', '╡', '╢', '╖', '╕', '╣', '║', '╗', '╝', '╜', '╛', 
                           '┐', '└', '┴', '┬', '├', '─', '┼', '╞', '╟', '╚', '╔', '╩', 
                           '╦', '╠', '═', '╬', '╧', '╨', '╤', '╥', '╙', '╘', '╒', '╓', 
                           '╫', '╪', '┘', '┌', '█', '▄', '▌', '▐', '▀']
        if any(c in self.original_text for c in decorative_chars):
            signals.append("Contains decorative box-drawing characters")
            recommendations.append("Remove decorative borders and use simple formatting")
        
        lines = self.original_text.split('\n')
        short_lines = [l for l in lines if 0 < len(l.strip()) < 20]
        if len(short_lines) > len(lines) * 0.3:
            signals.append("Possible multi-column layout detected")
            recommendations.append("Use single-column layout for better ATS parsing")
        
        tab_count = self.original_text.count('\t')
        pipe_count = self.original_text.count('|')
        if tab_count > 20 or pipe_count > 10:
            signals.append("Excessive tabs or pipes detected")
            recommendations.append("Avoid using tabs or tables; use simple bullet points")
        
        word_count = len(self.original_text.split())
        if word_count < 200:
            signals.append(f"Resume is very short ({word_count} words)")
            recommendations.append("Expand resume with more detail (aim for 400-700 words)")
        elif word_count > 1000:
            signals.append(f"Resume is very long ({word_count} words)")
            recommendations.append("Condense resume to 1-2 pages (400-700 words)")
        
        try:
            import fitz as pymupdf
            if pymupdf is not None:
                signals.append("Note: Scanned PDF detection requires runtime analysis")
        except ImportError:
            pass
        
        if not self.emails:
            signals.append("Missing email address")
            recommendations.append("Add email in contact section")
        
        if not self.phones:
            signals.append("Missing phone number")
            recommendations.append("Add phone number in contact section")
        
        mandatory_sections = ['experience', 'education']
        missing = [s for s in mandatory_sections if s not in self.sections]
        if missing:
            signals.append(f"Missing mandatory sections: {', '.join(missing)}")
            recommendations.append(f"Add {', '.join(missing)} section(s)")
        
        verdict = "Pass" if len(signals) <= 2 else "At Risk"
        
        return {
            'verdict': verdict,
            'signals': signals if signals else ["No major ATS issues detected"],
            'recommendations': recommendations if recommendations else ["Resume is ATS-ready"]
        }
    
    def _extract_requirements_from_jd(self, job_description: str) -> List[str]:
        """Extract key requirements/keywords from job description using curated keyword matching."""
        requirements = []
        jd_lower = job_description.lower()
        
        # Extract technical terms: camelCase or PascalCase (e.g., TensorFlow, PyTorch, MLflow)
        camel_pattern = r'\b([A-Z][a-z]+[A-Z][a-zA-Z]*)\b'
        for match in re.finditer(camel_pattern, job_description):
            requirements.append(match.group(1).lower())
        
        # Match ALLCAPS technical acronyms (e.g., AWS, GCP, ML, AI, CI/CD)
        acronym_pattern = r'\b([A-Z]{2,}(?:/[A-Z]{2,})*)\b'
        
        # Blacklist: common non-technical ALLCAPS words
        acronym_blacklist = {
            'EEO', 'AA', 'ADA', 'EEOC', 'OFCCP', 'FMLA', 'FLSA', 'EOE',
            'US', 'USA', 'UK', 'EU', 'CA', 'NY', 'SF', 'TX', 'FL', 'IL', 'WA',
            'OR', 'AND', 'THE', 'FOR', 'WITH', 'FROM', 'INTO', 'THIS', 'THAT',
            'ARE', 'WE', 'OUR', 'YOU', 'YOUR', 'ALL', 'ANY', 'NOT', 'BUT', 'AN',
            'BS', 'BA', 'MS', 'MA', 'MBA', 'PHD', 'MD', 'JD',
            'CEO', 'CTO', 'CFO', 'VP', 'SVP', 'EVP', 'HR', 'PM', 'QA', 'BI',
            'REQUIREMENTS', 'RESPONSIBILITIES', 'EXPERIENCE', 'KNOWLEDGE', 
            'SKILLS', 'EDUCATION', 'QUALIFICATIONS'
        }
        
        for match in re.finditer(acronym_pattern, job_description):
            term = match.group(1)
            # Split on slash and check each part against blacklist
            parts = term.split('/')
            all_parts_clean = all(part not in acronym_blacklist for part in parts)
            if all_parts_clean and term not in acronym_blacklist:
                requirements.append(term.lower())
        
        # Comprehensive keyword lists (expanded from original)
        tech_keywords = {
            # Programming languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'go', 'rust', 'ruby', 
            'php', 'swift', 'kotlin', 'scala', 'r', 'sql', 'bash', 'shell', 'c#', 'perl',
            
            # AI/ML specific
            'llm', 'llms', 'large language model', 'prompt engineering', 'fine-tuning',
            'rag', 'retrieval augmented generation', 'embedding', 'embeddings', 
            'vector database', 'pinecone', 'weaviate', 'chroma', 'faiss',
            'transformer', 'attention mechanism', 'gpt', 'bert', 'openai', 'anthropic',
            'ai safety', 'ai alignment', 'model evaluation', 'hallucination',
            
            # ML/Data Science
            'machine learning', 'deep learning', 'neural network', 'cnn', 'rnn', 'lstm',
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
            'feature engineering', 'model deployment', 'mlops', 'mlflow', 'kubeflow',
            'data science', 'statistical modeling', 'statistics', 'linear algebra',
            'optimization', 'gradient descent', 'backpropagation',
            
            # Web frameworks
            'react', 'vue', 'angular', 'svelte', 'next.js', 'nuxt', 'gatsby',
            'node.js', 'express', 'fastapi', 'flask', 'django', 'spring', 'laravel',
            
            # Cloud platforms
            'aws', 'azure', 'gcp', 'google cloud', 'cloud platform', 'lambda',
            'ec2', 's3', 'dynamodb', 'cloudformation', 'serverless', 'cloud functions',
            'cloud run', 'app engine', 'elastic beanstalk',
            
            # DevOps/Infrastructure
            'docker', 'kubernetes', 'k8s', 'jenkins', 'gitlab ci', 'github actions',
            'circleci', 'terraform', 'pulumi', 'ansible', 'chef', 'puppet',
            'infrastructure as code', 'iac', 'containerization', 'orchestration',
            
            # Databases
            'postgresql', 'postgres', 'mysql', 'mongodb', 'redis', 'elasticsearch',
            'dynamodb', 'cassandra', 'nosql', 'relational', 'database design',
            
            # Monitoring/Observability
            'prometheus', 'grafana', 'datadog', 'new relic', 'splunk', 'elk',
            'monitoring', 'logging', 'observability', 'alerting',
            
            # Architecture/Design
            'microservices', 'api', 'rest', 'restful', 'graphql', 'grpc',
            'event-driven', 'message queue', 'kafka', 'rabbitmq', 'pub/sub',
            'scalability', 'high availability', 'load balancing', 'caching',
            
            # Security
            'security', 'authentication', 'authorization', 'oauth', 'jwt', 'saml',
            'encryption', 'compliance', 'gdpr', 'hipaa', 'soc2',
            
            # Testing
            'testing', 'unit test', 'integration test', 'e2e', 'tdd', 'test-driven',
            'jest', 'pytest', 'cypress', 'selenium', 'playwright',
            
            # Methodologies
            'agile', 'scrum', 'kanban', 'ci/cd', 'continuous integration',
            'continuous deployment', 'devops', 'gitops',
            
            # Leadership/Management
            'leadership', 'mentoring', 'coaching', 'project management',
            'stakeholder management', 'team lead', 'technical lead',
            'people management', 'performance review', 'hiring', 'onboarding',
            
            # Data/Analytics
            'analytics', 'data visualization', 'tableau', 'power bi', 'looker',
            'data warehouse', 'etl', 'data pipeline', 'spark', 'hadoop', 'airflow',
            'a/b testing', 'experimentation', 'business intelligence',
            
            # Frontend specific
            'html', 'css', 'sass', 'responsive design', 'accessibility', 'wcag',
            'seo', 'web performance', 'core web vitals', 'state management',
            'redux', 'mobx', 'zustand', 'recoil',
            
            # Version control
            'git', 'github', 'gitlab', 'bitbucket', 'version control', 'code review'
        }
        
        # Check JD for all keywords
        for keyword in tech_keywords:
            if keyword in jd_lower:
                requirements.append(keyword)
        
        # Extract numbers + years for experience requirements
        exp_pattern = r'(\d+)\+?\s*years?'
        if re.search(exp_pattern, jd_lower):
            requirements.append('experience')
        
        # Remove duplicates and filter out very short terms
        requirements = list(set(req for req in requirements if len(req) > 1))
        
        return requirements
    
    def calculate_role_alignment(self) -> Dict:
        if not self.target_role:
            return {
                'score': 0,
                'level': self.detect_career_stage(),
                'alignment_details': 'No target role specified',
                'gaps': []
            }
        
        # Get the actual job description for this role
        job_description = get_job_description(self.target_role)
        
        # Extract requirements from the job description
        required_skills = self._extract_requirements_from_jd(job_description)
        
        if not required_skills:
            # Fallback to old method if no requirements extracted
            return {
                'score': 0,
                'level': self.detect_career_stage(),
                'alignment_details': f'Could not extract requirements for {self.target_role}',
                'gaps': []
            }
        
        # Check which requirements are present in resume
        matched_skills = [skill for skill in required_skills if skill in self.text]
        missing_skills = [skill for skill in required_skills if skill not in self.text]
        
        # Calculate alignment score
        alignment_score = int((len(matched_skills) / len(required_skills)) * 100)
        
        # Get top 8 gaps for feedback
        gaps = missing_skills[:8]
        
        level = self.detect_career_stage()
        
        # Create detailed alignment message
        if alignment_score >= 80:
            alignment_msg = f"Excellent match! Resume covers {len(matched_skills)}/{len(required_skills)} key requirements for {self.target_role}"
        elif alignment_score >= 60:
            alignment_msg = f"Good fit with room to improve. Resume covers {len(matched_skills)}/{len(required_skills)} requirements for {self.target_role}"
        elif alignment_score >= 40:
            alignment_msg = f"Moderate alignment. Resume covers {len(matched_skills)}/{len(required_skills)} requirements for {self.target_role}"
        else:
            alignment_msg = f"Low alignment. Resume covers {len(matched_skills)}/{len(required_skills)} requirements for {self.target_role}. Consider building more relevant experience."
        
        return {
            'score': alignment_score,
            'level': level,
            'alignment_details': alignment_msg,
            'gaps': gaps,
            'matched_skills': matched_skills[:5],  # Show top 5 matches
            'total_required': len(required_skills)
        }
    
    def generate_tailored_keywords(self, gemini_keywords: Optional[List[str]] = None) -> List[str]:
        if gemini_keywords:
            return gemini_keywords
        
        missing_verbs = [v for v in IMPACT_VERBS if v not in self.text]
        return missing_verbs[:15]
    
    def _get_band(self, score: int, max_score: int) -> str:
        pct = (score / max_score) * 100
        if pct >= 93:
            return "Excellent"
        elif pct >= 80:
            return "Strong"
        elif pct >= 60:
            return "Fair"
        else:
            return "Needs Attention"
    
    def analyze(self) -> Dict:
        completeness = self.score_completeness()
        summary = self.score_summary()
        education = self.score_education()
        employment = self.score_employment()
        
        total_score = completeness['score'] + summary['score'] + education['score'] + employment['score']
        total_max = 120
        
        overall_pct = (total_score / total_max) * 100
        if overall_pct >= 85:
            verdict = "High Completeness"
        elif overall_pct >= 65:
            verdict = "Medium Completeness"
        else:
            verdict = "Low Completeness"
        
        ats = self.check_ats_readiness()
        role_alignment = self.calculate_role_alignment()
        
        return {
            'overall_score': total_score,
            'max_score': total_max,
            'verdict': verdict,
            'completeness': completeness,
            'summary': summary,
            'education': education,
            'employment': employment,
            'ats_readiness': ats,
            'role_alignment': role_alignment,
            'career_stage': self.detect_career_stage(),
            'target_role': self.target_role or 'Not specified'
        }
