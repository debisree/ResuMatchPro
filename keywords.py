SECTION_HINTS = {
    "summary": ["summary", "objective", "profile", "about", "professional summary", "career objective"],
    "experience": ["experience", "employment", "work history", "professional experience", "work experience"],
    "education": ["education", "academic background", "qualifications", "academic history"],
    "skills": ["skills", "technical skills", "core competencies", "technical competencies", "proficiencies"],
    "projects": ["projects", "personal projects", "side projects", "portfolio"],
    "leadership": ["leadership", "leadership experience"],
    "research": ["research", "research experience"],
    "publications": ["publications", "papers", "articles"],
    "awards": ["awards", "honors", "achievements", "recognitions"],
    "certifications": ["certifications", "certificates", "licenses"],
    "volunteer": ["volunteer", "volunteering", "community service", "volunteer work"],
    "opensource": ["open source", "opensource", "oss contributions"],
    "misc": ["interests", "hobbies", "activities", "additional information"]
}

TOOL_HINTS = [
    "python", "r", "sql", "pyspark", "spark", "mlflow", "tensorflow", "pytorch",
    "sklearn", "scikit-learn", "xgboost", "lightgbm", "keras", "tableau", "power bi",
    "dash", "plotly", "flask", "django", "streamlit", "airflow", "dbt", "snowflake",
    "bigquery", "databricks", "sagemaker", "azure", "aws", "gcp", "docker",
    "kubernetes", "terraform", "git", "linux", "jupyter", "pandas", "numpy",
    "scipy", "statsmodels", "seaborn", "matplotlib", "excel", "jira", "confluence",
    "slack", "redis", "mongodb", "postgresql", "mysql", "cassandra", "elasticsearch",
    "kafka", "spark streaming", "flink", "hadoop", "hive", "presto", "redshift",
    "lambda", "ec2", "s3", "emr", "glue", "athena", "kinesis", "cloud functions",
    "cloud run", "vertex ai", "azure ml", "jenkins", "circleci", "github actions",
    "gitlab ci", "travis ci", "ansible", "puppet", "chef", "prometheus", "grafana",
    "datadog", "new relic", "splunk", "looker", "mode", "metabase", "superset"
]

DOMAIN_HINTS = [
    "manufacturing", "steel", "healthcare", "fintech", "financial services",
    "retail", "ecommerce", "e-commerce", "adtech", "advertising", "martech",
    "government", "gov", "defense", "nuclear", "semiconductor", "telecom",
    "telecommunications", "insurance", "logistics", "supply chain", "automotive",
    "pharma", "pharmaceutical", "biotech", "education", "edtech", "gaming",
    "entertainment", "media", "social media", "saas", "b2b", "b2c", "enterprise",
    "startup", "consulting", "real estate", "proptech", "agriculture", "agtech",
    "energy", "cleantech", "oil and gas", "construction", "hospitality", "travel",
    "transportation", "aerospace", "legal", "legaltech", "hr", "hrtech", "cybersecurity",
    "security", "fraud detection", "risk management", "credit", "banking", "payments",
    "blockchain", "cryptocurrency", "web3", "iot", "robotics", "autonomous vehicles"
]

ROLE_TITLES = [
    "data scientist", "machine learning engineer", "ml engineer", "data engineer",
    "analytics engineer", "research scientist", "applied scientist", "quant",
    "quantitative analyst", "data analyst", "business analyst", "mlops engineer",
    "ai engineer", "deep learning engineer", "nlp engineer", "computer vision engineer",
    "engineering manager", "product manager", "technical program manager", "tpm",
    "researcher", "postdoc", "phd student", "intern", "software engineer",
    "backend engineer", "frontend engineer", "full stack engineer", "devops engineer",
    "site reliability engineer", "sre", "platform engineer", "infrastructure engineer",
    "cloud engineer", "security engineer", "qa engineer", "test engineer",
    "principal engineer", "staff engineer", "senior engineer", "lead engineer",
    "architect", "solutions architect", "technical architect", "head of data",
    "head of ml", "head of engineering", "vp engineering", "cto", "chief data officer"
]

IMPACT_VERBS = [
    "optimized", "automated", "accelerated", "reduced", "improved", "increased",
    "scaled", "stabilized", "launched", "deployed", "migrated", "orchestrated",
    "streamlined", "hardened", "benchmarked", "refactored", "designed", "built",
    "delivered", "led", "owned", "drove", "instrumented", "monitored", "implemented",
    "developed", "created", "established", "architected", "engineered", "maintained",
    "enhanced", "integrated", "collaborated", "coordinated", "managed", "supervised",
    "trained", "mentored", "presented", "published", "researched", "analyzed",
    "evaluated", "validated", "tested", "debugged", "troubleshot", "resolved",
    "achieved", "exceeded", "outperformed", "won", "awarded", "recognized",
    "spearheaded", "pioneered", "innovated", "transformed", "revolutionized",
    "modernized", "consolidated", "standardized", "unified", "simplified",
    "eliminated", "prevented", "mitigated", "minimized", "maximized"
]

ROLE_VOCABULARIES = {
    "data scientist": [
        "python", "r", "sql", "machine learning", "statistical analysis", "sklearn",
        "pandas", "numpy", "jupyter", "experimentation", "a/b testing", "hypothesis testing",
        "regression", "classification", "clustering", "feature engineering", "model evaluation",
        "cross-validation", "data visualization", "tableau", "matplotlib", "seaborn",
        "predictive modeling", "time series", "forecasting", "causal inference"
    ],
    "machine learning engineer": [
        "python", "tensorflow", "pytorch", "model deployment", "mlops", "docker",
        "kubernetes", "ci/cd", "model serving", "inference", "latency optimization",
        "scalability", "monitoring", "model versioning", "feature store", "mlflow",
        "kubeflow", "sagemaker", "vertex ai", "rest api", "grpc", "batch processing",
        "real-time predictions", "containerization", "cloud platforms", "aws", "gcp", "azure"
    ],
    "data engineer": [
        "sql", "python", "spark", "pyspark", "airflow", "etl", "data pipeline",
        "data warehouse", "snowflake", "redshift", "bigquery", "kafka", "streaming",
        "batch processing", "dbt", "data modeling", "dimensional modeling", "schema design",
        "data quality", "data governance", "aws", "gcp", "azure", "s3", "glue",
        "databricks", "presto", "hive", "orchestration", "workflow management"
    ],
    "analytics engineer": [
        "sql", "dbt", "data modeling", "dimensional modeling", "python", "data warehouse",
        "snowflake", "bigquery", "redshift", "tableau", "looker", "data visualization",
        "etl", "elt", "data transformation", "analytics", "business intelligence",
        "git", "version control", "testing", "data quality", "documentation"
    ],
    "research scientist": [
        "phd", "publications", "research", "experimentation", "statistical analysis",
        "machine learning", "deep learning", "python", "pytorch", "tensorflow",
        "paper writing", "peer review", "conferences", "journals", "hypothesis testing",
        "experimental design", "novel algorithms", "state-of-the-art", "sota",
        "literature review", "collaboration", "interdisciplinary"
    ],
    "mlops engineer": [
        "mlops", "model deployment", "ci/cd", "docker", "kubernetes", "monitoring",
        "mlflow", "kubeflow", "sagemaker", "vertex ai", "infrastructure as code",
        "terraform", "ansible", "python", "model serving", "feature store",
        "data versioning", "model versioning", "automated training", "automated deployment",
        "observability", "logging", "metrics", "alerting", "cloud platforms"
    ]
}

EDUCATION_KEYWORDS = [
    "bachelor", "bs", "ba", "bsc", "master", "ms", "ma", "msc", "mba",
    "phd", "doctorate", "md", "jd", "undergraduate", "graduate", "postgraduate",
    "degree", "diploma", "certificate", "associate", "aa", "as"
]

LEADERSHIP_KEYWORDS = [
    "led", "managed", "supervised", "mentored", "trained", "coached", "directed",
    "spearheaded", "pioneered", "coordinated", "organized", "facilitated",
    "team lead", "tech lead", "technical lead", "project lead", "manager",
    "leadership", "team of", "cross-functional", "stakeholder management"
]

METRIC_PATTERNS = [
    r'\d+%',
    r'\d+x',
    r'\$\d+[kmb]?',
    r'\d+[kmb]?\+?\s*(users|customers|transactions|records|rows|gb|tb|queries|requests)',
    r'(reduced|increased|improved|decreased)\s+by\s+\d+',
    r'\d+\s*(seconds|minutes|hours|days|weeks|months)',
    r'from\s+\d+.*to\s+\d+',
]
