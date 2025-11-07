import spacy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from .models import UserSkill, Skill

nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Extract skill keywords from resume file (pdf/docx)
def extract_skills_from_resume(file):
    text = ""
    if file.name.endswith('.pdf'):
        from PyPDF2 import PdfReader
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    elif file.name.endswith('.docx'):
        import docx
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text
    # NLP processing
    doc = nlp(text)
    keywords = [ent.text for ent in doc.ents if ent.label_ == "ORG" or ent.label_ == "PRODUCT"]
    return list(set(keywords))  # Unique skills

# Get Sentence-BERT embeddings
def get_sentence_bert_embedding(text):
    return model.encode([text])[0]

# Compute match scores
def compute_match_scores(skill_query, current_user):
    query_vec = get_sentence_bert_embedding(skill_query)
    user_skills = UserSkill.objects.exclude(user=current_user).select_related('user', 'skill')
    results = []
    for us in user_skills:
        skill_vec = get_sentence_bert_embedding(us.skill.name)
        score = cosine_similarity([query_vec], [skill_vec])[0][0]
        results.append({
            "username": us.user.username,
            "skill": us.skill.name,
            "score": round(float(score), 3)
        })
    # Sort descending
    results = sorted(results, key=lambda x: x['score'], reverse=True)
    return results[:10]  # Top 10 matches
