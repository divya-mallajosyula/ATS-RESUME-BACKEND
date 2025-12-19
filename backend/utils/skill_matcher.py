import re
from typing import List, Dict

# Comprehensive skills database
SKILLS_DATABASE = [
    # Programming Languages
    "Python", "JavaScript", "Java", "C++", "C#", "TypeScript", "Ruby", "PHP", 
    "Swift", "Kotlin", "Go", "Rust", "Scala", "R", "MATLAB", "Perl", 
    "Objective-C", "Dart", "Groovy", "Elixir", "Haskell", "Lua", "C",
    
    # Web Technologies - Frontend
    "React", "React.js", "Angular", "Vue.js", "Vue", "Svelte", "jQuery", 
    "HTML", "HTML5", "CSS", "CSS3", "SASS", "SCSS", "Less", "Bootstrap", 
    "Tailwind CSS", "Material UI", "Chakra UI", "Next.js", "Nuxt.js", "Gatsby",
    "Webpack", "Vite", "Babel", "Redux", "MobX", "Zustand",
    
    # Web Technologies - Backend
    "Node.js", "Express.js", "Express", "Django", "Flask", "FastAPI", 
    "Spring Boot", "Spring", "ASP.NET", ".NET", "Laravel", "Ruby on Rails", 
    "Rails", "Symfony", "NestJS", "Fastify", "Koa", "Hapi",
    
    # Databases - SQL
    "PostgreSQL", "MySQL", "SQL Server", "Oracle", "MariaDB", "SQLite",
    "SQL", "T-SQL", "PL/SQL",
    
    # Databases - NoSQL
    "MongoDB", "Redis", "Cassandra", "DynamoDB", "Couchbase", "Neo4j",
    "Firebase", "Firestore", "Elasticsearch", "CouchDB",
    
    # Cloud Platforms
    "AWS", "Amazon Web Services", "Azure", "Microsoft Azure", "Google Cloud", 
    "GCP", "Google Cloud Platform", "DigitalOcean", "Heroku", "Vercel", "Netlify",
    "Oracle Cloud", "IBM Cloud", "Alibaba Cloud",
    
    # Cloud Services - AWS
    "EC2", "S3", "Lambda", "RDS", "DynamoDB", "CloudFront", "Route 53",
    "ECS", "EKS", "Elastic Beanstalk", "CloudWatch", "SNS", "SQS",
    
    # DevOps & CI/CD
    "Docker", "Kubernetes", "Jenkins", "GitLab CI", "GitHub Actions", 
    "CircleCI", "Travis CI", "Terraform", "Ansible", "Chef", "Puppet",
    "Vagrant", "CI/CD", "Continuous Integration", "Continuous Deployment",
    
    # Version Control
    "Git", "GitHub", "GitLab", "Bitbucket", "SVN", "Mercurial",
    
    # Testing
    "Jest", "Mocha", "Chai", "Pytest", "JUnit", "TestNG", "Selenium",
    "Cypress", "Playwright", "Puppeteer", "JMeter", "Postman", "Insomnia",
    
    # API & Architecture
    "REST API", "RESTful", "GraphQL", "gRPC", "WebSocket", "Microservices",
    "Monolithic", "API Gateway", "Swagger", "OpenAPI", "SOAP",
    
    # Mobile Development
    "Android", "iOS", "React Native", "Flutter", "Xamarin", "Ionic",
    "Swift UI", "Jetpack Compose", "Cordova",
    
    # Data Science & ML
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Keras",
    "Scikit-learn", "Pandas", "NumPy", "SciPy", "Matplotlib", "Seaborn",
    "Data Analysis", "Data Science", "NLP", "Natural Language Processing",
    "Computer Vision", "OpenCV", "NLTK", "spaCy", "Hugging Face",
    
    # Big Data
    "Apache Spark", "Hadoop", "Kafka", "Airflow", "Databricks", "Snowflake",
    "BigQuery", "Redshift", "ETL", "Data Pipeline", "Data Warehouse",
    
    # Project Management Tools
    "Jira", "Confluence", "Trello", "Asana", "Monday.com", "Notion",
    "ClickUp", "Linear", "Basecamp",
    
    # Methodologies & Practices
    "Agile", "Scrum", "Kanban", "Waterfall", "DevOps", "TDD", 
    "Test-Driven Development", "BDD", "Behavior-Driven Development",
    "Pair Programming", "Code Review", "Continuous Learning",
    
    # Soft Skills
    "Leadership", "Communication", "Team Management", "Problem Solving",
    "Critical Thinking", "Time Management", "Project Management", 
    "Collaboration", "Mentoring", "Public Speaking", "Technical Writing",
    "Analytical Skills", "Creativity", "Adaptability", "Conflict Resolution",
    
    # Other Technologies
    "GraphQL", "WebAssembly", "Blockchain", "Solidity", "Ethereum",
    "Smart Contracts", "Web3", "Socket.io", "RabbitMQ", "Nginx",
    "Apache", "Linux", "Unix", "Shell Scripting", "Bash", "PowerShell",
    
    # Design & UI/UX
    "Figma", "Adobe XD", "Sketch", "Photoshop", "Illustrator", "InVision",
    "UI Design", "UX Design", "User Research", "Wireframing", "Prototyping",
    
    # Security
    "OAuth", "JWT", "Authentication", "Authorization", "Encryption",
    "SSL", "TLS", "Penetration Testing", "Security Audit", "OWASP",
]

# Create case-insensitive lookup
SKILLS_LOOKUP = {skill.lower(): skill for skill in SKILLS_DATABASE}


def extract_skills(text: str) -> List[str]:
    """
    Extract skills from text using predefined skill list with intelligent matching
    
    Args:
        text (str): Text to search for skills (resume or job description)
        
    Returns:
        list: Found skills (deduplicated, sorted, with original casing)
    """
    if not text:
        return []
    
    found_skills = set()
    text_lower = text.lower()
    
    # Remove special characters that might interfere with matching
    # but keep periods for abbreviations like "Node.js"
    text_normalized = re.sub(r'[^\w\s.\-+#]', ' ', text_lower)
    
    for skill in SKILLS_DATABASE:
        skill_lower = skill.lower()
        
        # Create regex pattern with word boundaries
        # Handle special characters in skill names (e.g., C++, C#, .NET)
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        
        # Search in normalized text
        if re.search(pattern, text_normalized):
            found_skills.add(skill)
            continue
        
        # Special handling for variations
        # e.g., "React.js" should match "React" and vice versa
        if '.' in skill_lower:
            base_skill = skill_lower.split('.')[0]
            if re.search(r'\b' + re.escape(base_skill) + r'\b', text_normalized):
                found_skills.add(skill)
    
    return sorted(list(found_skills))


def calculate_match(resume_skills: List[str], jd_skills: List[str]) -> Dict:
    """
    Calculate match percentage and identify skill gaps
    
    Args:
        resume_skills (list): Skills extracted from resume
        jd_skills (list): Skills extracted from job description
        
    Returns:
        dict: {
            'score': float,
            'matched_skills': list,
            'missing_skills': list,
            'total_jd_skills': int,
            'total_matched': int
        }
    """
    # Normalize to lowercase for comparison
    resume_set = {skill.lower() for skill in resume_skills}
    jd_set = {skill.lower() for skill in jd_skills}
    
    # Find matches
    matched_lower = jd_set.intersection(resume_set)
    missing_lower = jd_set - resume_set
    
    # Calculate score
    if len(jd_skills) == 0:
        score = 0.0
    else:
        score = (len(matched_lower) / len(jd_skills)) * 100
    
    # Convert back to original casing from jd_skills
    jd_skill_map = {skill.lower(): skill for skill in jd_skills}
    
    matched_skills = [jd_skill_map[skill] for skill in matched_lower]
    missing_skills = [jd_skill_map[skill] for skill in missing_lower]
    
    return {
        "score": round(score, 2),
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
        "total_jd_skills": len(jd_skills),
        "total_matched": len(matched_skills)
    }


def get_skill_suggestions(missing_skills: List[str]) -> List[str]:
    """
    Generate suggestions for missing skills
    
    Args:
        missing_skills (list): Skills that are missing from resume
        
    Returns:
        list: Suggestions for each missing skill
    """
    suggestions = []
    
    skill_categories = {
        "frontend": ["React", "Angular", "Vue.js", "HTML", "CSS", "JavaScript", "TypeScript"],
        "backend": ["Node.js", "Python", "Java", "Django", "Flask", "Spring Boot"],
        "database": ["MongoDB", "PostgreSQL", "MySQL", "Redis"],
        "cloud": ["AWS", "Azure", "Google Cloud", "Docker", "Kubernetes"],
    }
    
    for skill in missing_skills:
        skill_lower = skill.lower()
        
        # Find category
        category = None
        for cat_name, cat_skills in skill_categories.items():
            if any(skill_lower == s.lower() for s in cat_skills):
                category = cat_name
                break
        
        if category:
            suggestions.append(f"Learn {skill} through online courses or projects")
        else:
            suggestions.append(f"Consider gaining experience with {skill}")
    
    return suggestions

