COMMON_SKILLS = {
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'swift', 'kotlin',
    'go', 'rust', 'scala', 'perl', 'r', 'matlab', 'sql', 'html', 'css',
    
    # Frameworks & Libraries
    'react', 'angular', 'vue', 'django', 'flask', 'spring', 'node.js', 'express',
    'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn', 'bootstrap',
    
    # Cloud & DevOps
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab', 'terraform',
    'ansible', 'vagrant', 'prometheus', 'grafana',
    
    # Databases
    'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sqlite',
    'cassandra', 'dynamodb',
    
    # Tools & Platforms
    'git', 'github', 'bitbucket', 'jira', 'confluence', 'slack', 'vscode',
    'intellij', 'eclipse', 'postman',
    
    # Methodologies & Concepts
    'agile', 'scrum', 'kanban', 'tdd', 'ci/cd', 'devops', 'microservices',
    'rest api', 'graphql', 'oauth',
    
    # Soft Skills
    'leadership', 'communication', 'teamwork', 'problem solving',
    'project management', 'time management', 'analytical', 'creativity',
    
    # Business & Analytics
    'product management', 'data analysis', 'business intelligence',
    'market research', 'seo', 'digital marketing', 'content strategy',
    
    # Design
    'ui/ux', 'photoshop', 'illustrator', 'figma', 'sketch', 'adobe xd',
    'indesign', 'after effects',
}


def get_skill_vocabulary():
    """Return the known skill vocabulary used for extraction.

    This combines the curated common skills list with any skills already stored
    in the database so newly added skills can be matched without code changes.
    """
    vocabulary = {skill.lower() for skill in COMMON_SKILLS}

    try:
        from .models import Skill

        vocabulary.update(
            skill_name.strip().lower()
            for skill_name in Skill.objects.values_list('name', flat=True)
            if skill_name
        )
    except Exception:
        # Database may not be ready during migrations or first startup.
        pass

    return vocabulary