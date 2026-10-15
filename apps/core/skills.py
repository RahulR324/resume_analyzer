"""Canonical skill lexicon used for extraction and gap analysis."""

from __future__ import annotations

SKILL_ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "node": "node.js",
    "nodejs": "node.js",
    "react.js": "react",
    "reactjs": "react",
    "nextjs": "next.js",
    "vuejs": "vue",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "k8s": "kubernetes",
    "gcp": "google cloud",
    "ms excel": "excel",
    "power bi": "power bi",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "tf": "tensorflow",
    "pytorch": "pytorch",
    "ci/cd": "ci/cd",
    "rest api": "rest",
    "restful": "rest",
    "html5": "html",
    "css3": "css",
    "ms word": "microsoft word",
    "c++": "c++",
    "c#": "c#",
}

TECH_SKILLS = {
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "ruby",
    "php", "swift", "kotlin", "scala", "r", "matlab", "sql", "html", "css", "sass",
    "react", "next.js", "vue", "angular", "svelte", "node.js", "express", "django",
    "flask", "fastapi", "spring", "rails", ".net", "laravel", "graphql", "rest",
    "postgresql", "mysql", "sqlite", "mongodb", "redis", "elasticsearch", "cassandra",
    "dynamodb", "aws", "azure", "google cloud", "docker", "kubernetes", "terraform",
    "ansible", "linux", "git", "github", "gitlab", "ci/cd", "jenkins", "github actions",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras", "huggingface",
    "spacy", "opencv", "airflow", "spark", "hadoop", "kafka", "snowflake", "dbt",
    "tableau", "power bi", "looker", "excel", "figma", "jira", "confluence",
    "pytest", "selenium", "playwright", "cypress", "postman", "graphql",
    "microservices", "system design", "nlp", "machine learning", "deep learning",
    "data analysis", "data engineering", "data visualization", "etl", "api design",
    "oauth", "jwt", "security", "penetration testing", "sre", "observability",
    "prometheus", "grafana", "datadog", "splunk", "webpack", "vite", "tailwind",
    "bootstrap", "redux", "celery", "rabbitmq", "nginx", "apache", "bash",
}

DOMAIN_SKILLS = {
    "product management", "agile", "scrum", "kanban", "roadmap", "stakeholder management",
    "user research", "ux", "ui design", "wireframing", "prototyping", "a/b testing",
    "growth", "seo", "sem", "content strategy", "copywriting", "brand strategy",
    "digital marketing", "email marketing", "social media", "paid ads", "analytics",
    "financial modeling", "forecasting", "budgeting", "accounting", "gaap", "ifrs",
    "sales", "negotiation", "crm", "hubspot", "salesforce", "customer success",
    "recruiting", "people operations", "training", "leadership", "mentoring",
    "project management", "pmp", "risk management", "vendor management",
    "supply chain", "operations", "lean", "six sigma", "process improvement",
    "public speaking", "technical writing", "documentation", "communication",
    "problem solving", "critical thinking", "collaboration", "time management",
    "attention to detail", "customer service", "conflict resolution",
}

CERTIFICATIONS = {
    "aws certified", "azure fundamentals", "pmp", "cpa", "cfa", "cissp", "comptia",
    "google analytics", "scrum master", "itil", "six sigma",
}

ALL_SKILLS = {skill.lower() for skill in TECH_SKILLS | DOMAIN_SKILLS | CERTIFICATIONS}


def normalize_skill(token: str) -> str:
    cleaned = " ".join(token.lower().replace("_", " ").split())
    return SKILL_ALIASES.get(cleaned, cleaned)
