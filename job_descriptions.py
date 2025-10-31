TECH_JOB_DESCRIPTIONS = {
    "software engineer": """
Requirements:
- 3+ years of experience in software development
- Proficiency in Python, Java, or C++
- Experience with cloud platforms (AWS, Azure, GCP)
- Strong understanding of data structures and algorithms
- Experience with version control (Git), CI/CD pipelines
- RESTful API design and microservices architecture
- Database design (SQL and NoSQL)
- Excellent problem-solving and debugging skills
Responsibilities:
- Design, develop, and maintain scalable software systems
- Collaborate with cross-functional teams to define and ship features
- Write clean, maintainable, and well-tested code
- Participate in code reviews and technical discussions
- Optimize application performance and scalability
""",
    
    "machine learning engineer": """
Requirements:
- 3+ years of experience in machine learning and data science
- Strong programming skills in Python (NumPy, Pandas, Scikit-learn)
- Experience with deep learning frameworks (TensorFlow, PyTorch)
- Knowledge of ML algorithms, feature engineering, and model evaluation
- Experience deploying ML models to production
- Solid understanding of statistics and linear algebra
- Experience with big data tools (Spark, Hadoop) is a plus
- Publications or contributions to ML community preferred
Responsibilities:
- Design and implement machine learning models and algorithms
- Analyze large datasets to extract meaningful insights
- Deploy and monitor ML models in production environments
- Collaborate with data scientists and engineers to improve model performance
- Stay current with latest ML research and technologies
""",
    
    "data scientist": """
Requirements:
- 2+ years of experience in data analysis and statistical modeling
- Proficiency in Python or R, SQL, and data visualization tools
- Strong statistical and analytical skills
- Experience with machine learning techniques
- Ability to communicate complex findings to non-technical stakeholders
- Experience with A/B testing and experimentation
- Knowledge of business intelligence tools (Tableau, Power BI)
Responsibilities:
- Analyze large datasets to identify trends and patterns
- Build predictive models and data-driven solutions
- Create data visualizations and dashboards
- Collaborate with business teams to solve problems with data
- Present findings and recommendations to stakeholders
""",
    
    "frontend developer": """
Requirements:
- 3+ years of experience in frontend development
- Expert knowledge of HTML, CSS, JavaScript/TypeScript
- Strong experience with modern frameworks (React, Vue, Angular)
- Understanding of responsive design and cross-browser compatibility
- Experience with state management (Redux, MobX)
- Knowledge of web performance optimization
- Familiarity with RESTful APIs and GraphQL
- Experience with testing frameworks (Jest, Cypress)
Responsibilities:
- Build responsive and performant user interfaces
- Collaborate with designers to implement pixel-perfect designs
- Optimize applications for maximum speed and scalability
- Write reusable, testable, and efficient code
- Participate in code reviews and mentor junior developers
""",
    
    "backend developer": """
Requirements:
- 3+ years of backend development experience
- Strong knowledge of server-side languages (Python, Java, Go, Node.js)
- Experience with relational and NoSQL databases
- Understanding of RESTful and GraphQL API design
- Knowledge of authentication and authorization (OAuth, JWT)
- Experience with message queues (RabbitMQ, Kafka)
- Understanding of microservices architecture
- Experience with containerization (Docker, Kubernetes)
Responsibilities:
- Design and develop scalable backend services and APIs
- Optimize database queries and system performance
- Implement security and data protection measures
- Integrate with third-party services and APIs
- Monitor and troubleshoot production issues
""",
    
    "full stack developer": """
Requirements:
- 3+ years of full stack development experience
- Proficiency in frontend (React/Vue/Angular) and backend (Node.js/Python/Java)
- Experience with databases (PostgreSQL, MongoDB)
- Knowledge of cloud platforms and deployment
- Understanding of DevOps practices and CI/CD
- Experience with version control and agile methodologies
- Strong problem-solving and communication skills
Responsibilities:
- Develop end-to-end features from UI to database
- Design and implement RESTful APIs
- Deploy applications to cloud infrastructure
- Collaborate with product teams to define requirements
- Optimize application performance and user experience
""",
    
    "devops engineer": """
Requirements:
- 3+ years of DevOps or infrastructure engineering experience
- Strong knowledge of Linux/Unix systems
- Experience with cloud platforms (AWS, Azure, GCP)
- Proficiency in infrastructure as code (Terraform, CloudFormation)
- Experience with containerization and orchestration (Docker, Kubernetes)
- Knowledge of CI/CD tools (Jenkins, GitLab CI, GitHub Actions)
- Scripting skills in Python, Bash, or Go
- Experience with monitoring tools (Prometheus, Grafana, Datadog)
Responsibilities:
- Design and maintain cloud infrastructure
- Implement CI/CD pipelines for automated deployments
- Monitor system performance and troubleshoot issues
- Improve system reliability and scalability
- Implement security best practices and compliance
"""
}

def get_job_description(target_role: str) -> str:
    """Get job description for target role, or a generic tech job description."""
    role_lower = target_role.lower()
    
    for key in TECH_JOB_DESCRIPTIONS:
        if key in role_lower or role_lower in key:
            return TECH_JOB_DESCRIPTIONS[key]
    
    return """
Generic Tech Role Requirements:
- Strong programming skills in relevant languages
- Problem-solving and analytical abilities
- Collaboration and communication skills
- Experience with modern development tools and practices
- Continuous learning mindset
"""
