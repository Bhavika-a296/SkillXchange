import PyPDF2
import nltk
import json
import os
from typing import List, Tuple

# Prevent PyTorch meta tensor issues with newer versions
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '0'

# Heavy ML libraries are imported lazily inside functions to avoid import-time
# failures when running management commands (migrate, collectstatic, etc.).

def ensure_nltk_data():
    """Ensure all required NLTK data is downloaded"""
    # Try to download essential packages
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        nltk.download('maxent_ne_chunker', quiet=True)
        nltk.download('words', quiet=True)
    except Exception as e:
        print(f"Warning: Could not download NLTK data: {str(e)}")
        print("Continuing with fallback tokenization methods...")
    
    # Verify punkt tokenizer is accessible
    try:
        nltk.data.load('tokenizers/punkt/english.pickle')
    except:
        try:
            # One more attempt to download punkt specifically
            nltk.download('punkt', quiet=True)
        except:
            print("Warning: Could not load punkt tokenizer. Using fallback methods.")


# Initialize NLTK data
ensure_nltk_data()

print("[SkillMatch] ============================================")
print("[SkillMatch] utils_safe.py MODULE LOADED/RELOADED")
print("[SkillMatch] ============================================")

# Initialize the BERT model lazily
_model = None
_model_load_failed = False
_model_load_attempts = 0
_max_load_attempts = 10  # Increased to allow retries after server restart

def get_model(force_reload=False):
    """Lazily load the SentenceTransformer model. If the package isn't
    available in the environment (for example on CI or when running simple
    management commands), this will return None and the caller should handle
    the fallback behavior gracefully.
    """
    global _model, _model_load_failed, _model_load_attempts
    
    # If force reload requested, reset state
    if force_reload:
        print(f"[SkillMatch] Force reloading model...")
        _model = None
        _model_load_failed = False
        _model_load_attempts = 0
    
    # If we already have a working model, return it
    if _model is not None:
        return _model
    
    # If we've exceeded max attempts and haven't been asked to force reload, give up
    if _model_load_failed and _model_load_attempts >= _max_load_attempts and not force_reload:
        print(f"[SkillMatch] Model load failed after {_model_load_attempts} attempts, giving up")
        return None
        
    if _model is None and _model_load_attempts < _max_load_attempts:
        try:
            from sentence_transformers import SentenceTransformer
            import torch
            import os
            
            _model_load_attempts += 1
            print(f"[SkillMatch] Loading model (attempt {_model_load_attempts}/{_max_load_attempts})...")
            
            # Set environment variables
            os.environ['TRANSFORMERS_OFFLINE'] = '0'
            os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
            
            # CRITICAL FIX for PyTorch 2.8.0+: Disable meta device initialization
            # This prevents "Cannot copy out of meta tensor" error
            try:
                import torch._dynamo
                torch._dynamo.config.suppress_errors = True
            except:
                pass
            
            # Disable meta device to prevent PyTorch 2.7+ meta tensor errors
            os.environ['PYTORCH_JIT'] = '0'
            os.environ['TOKENIZERS_PARALLELISM'] = 'false'
            
            # Load model
            print(f"[SkillMatch] Loading SentenceTransformer model...")
            
            # Using PyTorch 2.3.1 which doesn't have meta tensor issues
            _model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
            
            # Model loads on CPU by default, no need to move it
            print(f"[SkillMatch] Model loaded successfully on CPU")
            
            # Test the model with a simple encoding to ensure it works
            test_result = _model.encode("test", show_progress_bar=False)
            print(f"[SkillMatch] ✓ Model loaded successfully, embedding dimension: {test_result.shape[0]}")
            _model_load_failed = False
            
        except Exception as e:
            # Do not raise here — allow the application to continue without
            # embeddings. Log a warning so developers know heavy deps are
            # unavailable.
            print(f"[SkillMatch] ERROR: Could not load SentenceTransformer model: {e}")
            import traceback
            traceback.print_exc()
            _model = None
            _model_load_failed = True
            
    return _model


def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from uploaded PDF file."""
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def normalize_skill_name(skill_name: str) -> str:
    """Normalize skill names before storing/matching."""
    if not skill_name:
        return ""
    return " ".join(skill_name.strip().lower().split())


def is_valid_skill_name(candidate: str) -> bool:
    """Return True only for plausible skill names."""
    import re

    candidate = normalize_skill_name(candidate)
    if not candidate:
        return False

    stop_words = {
        'and', 'or', 'with', 'for', 'the', 'a', 'an', 'to', 'of', 'in', 'on',
        'at', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be', 'this',
        'that', 'it', 'i', 'you', 'we', 'they', 'he', 'she', 'my', 'our',
        'your', 'their', 'experience', 'project', 'projects', 'resume',
        'summary', 'education', 'college', 'university', 'certificate',
        'certification', 'internship', 'work', 'skills', 'technical',
        'board', 'pursuing', 'completed', 'analyzed', 'activities', 'training'
    }
    if candidate in stop_words:
        return False

    if '@' in candidate or 'http' in candidate or '.com' in candidate:
        return False

    months = {
        'jan', 'january', 'feb', 'february', 'mar', 'march', 'apr', 'april',
        'may', 'jun', 'june', 'jul', 'july', 'aug', 'august', 'sep',
        'september', 'oct', 'october', 'nov', 'november', 'dec', 'december'
    }
    if any(m in candidate for m in months):
        return False

    if re.search(r'\b(19|20)\d{2}\b', candidate):
        return False
    if re.fullmatch(r'\d+(?:[./-]\d+)*', candidate):
        return False

    # reject username-like tokens (letters followed by long digit suffix)
    if re.fullmatch(r'[a-z]+\d{3,}', candidate):
        return False

    if len(candidate) < 2 or len(candidate) > 30:
        return False

    words_in_candidate = candidate.split()
    if len(words_in_candidate) > 3:
        return False

    return True


def extract_skills_from_text(text: str) -> List[str]:
    """Extract skills from text using regex and a predefined skills list."""
    from .skills_data import get_skill_vocabulary
    import re

    skill_vocabulary = get_skill_vocabulary()
    
    # Clean and normalize text
    text = text.lower()
    found_skills = set()
    
    # First, look for exact matches of multi-word skills
    for skill in skill_vocabulary:
        if ' ' in skill:
            # Look for the skill with word boundaries
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text):
                normalized_skill = normalize_skill_name(skill)
                if is_valid_skill_name(normalized_skill):
                    found_skills.add(normalized_skill)
    
    # Split text into words using regex
    # This will match any sequence of word characters (letters, numbers, underscores)
    words = re.findall(r'\b\w+\b', text)
    
    # Check single words against skills list
    for word in words:
        if word in skill_vocabulary:
            normalized_word = normalize_skill_name(word)
            if is_valid_skill_name(normalized_word):
                found_skills.add(normalized_word)
    
    # Look for technical patterns
    for word in words:
        # Check for common technical patterns
        if len(word) > 2:  # Ignore very short words
            # Common technical patterns
            if (any(char.isdigit() for char in word) or  # Contains numbers (e.g., sql2019)
                word.endswith(('js', 'db', 'ml', 'ai', 'ui', 'ux', 'py')) or  # Common technical suffixes
                word.startswith(('py', 'js', 'ng', 'rx'))):  # Common technical prefixes
                if word in skill_vocabulary:
                    normalized_word = normalize_skill_name(word)
                    if is_valid_skill_name(normalized_word):
                        found_skills.add(normalized_word)
    
    # Look for consecutive words that might form skills
    text_with_boundaries = ' ' + text + ' '
    for i in range(len(words) - 1):
        two_words = ' ' + words[i] + ' ' + words[i + 1] + ' '
        if two_words in text_with_boundaries:
            compound = (words[i] + ' ' + words[i + 1]).lower()
            if compound in skill_vocabulary:
                normalized_compound = normalize_skill_name(compound)
                if is_valid_skill_name(normalized_compound):
                    found_skills.add(normalized_compound)

    # Fallback extraction: conservative parsing of likely skill sections only.
    # Keep this strict to avoid storing resume noise as skills.
    dotted_whitelist = {
        'node.js', 'next.js', 'vue.js', 'react.js', 'express.js'
    }

    def is_valid_fallback_skill(candidate: str) -> bool:
        if not is_valid_skill_name(candidate):
            return False

        # If dotted token is unknown and contains multiple words/chunks, reject it.
        if '.' in candidate and candidate not in dotted_whitelist and candidate not in skill_vocabulary:
            return False

        # Reject very long hyphenated phrase fragments.
        if candidate.count('-') > 2 and candidate not in skill_vocabulary:
            return False

        if candidate not in skill_vocabulary:
            # For unknown skills, require a technical-looking token.
            technical_hint = (
                any(ch in candidate for ch in ('+', '#', '/', '-')) or
                any(ch.isdigit() for ch in candidate) or
                candidate.endswith(('js', 'sql', 'ml', 'ai', 'api', 'db', 'devops'))
            )
            if not technical_hint:
                return False

        return True

    # Prefer parsing around lines that likely contain skill lists.
    likely_skill_chunks = []
    normalized_text = text.replace('\r', '\n')
    for line in normalized_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        if 'skill' in line or 'technology' in line or 'tools' in line:
            likely_skill_chunks.append(line)

    # If resume text is flattened into one line, still inspect the whole text,
    # but split aggressively by common list separators.
    if not likely_skill_chunks:
        likely_skill_chunks = [normalized_text]

    for chunk in likely_skill_chunks:
        # Remove heading prefix if present (e.g., "Technical Skills:").
        if ':' in chunk:
            chunk = chunk.split(':', 1)[1]

        raw_candidates = re.split(r'[,|\n•;]+', chunk)
        for raw in raw_candidates:
            candidate = normalize_skill_name(raw.strip(" .,:;()[]{}\t"))
            if is_valid_fallback_skill(candidate):
                found_skills.add(candidate)

    # Safety cap to avoid runaway extraction from noisy resumes.
    if len(found_skills) > 50:
        found_skills = set(sorted(found_skills)[:50])
    
    return sorted(list(found_skills))


def get_skill_embedding(skill_text: str) -> List[float]:
    """Get BERT embedding for a skill."""
    
    model = get_model()
    if model is None:
        # Fallback: return an empty list to indicate embedding unavailable.
        print(f"[SkillMatch] ERROR: Model is None, cannot create embedding for '{skill_text}'")
        return []
    try:
        embedding = model.encode([skill_text], show_progress_bar=False)[0]
        result = embedding.tolist()
        return result
    except Exception as e:
        print(f"[SkillMatch] ERROR: Failed to encode skill '{skill_text}': {e}")
        import traceback
        traceback.print_exc()
        return []


def calculate_skill_similarity(skill_embedding: List[float], target_embedding: List[float]) -> float:
    """Calculate cosine similarity between two skill embeddings."""
    # If either embedding is missing, fall back to 0.0 similarity
    if not skill_embedding or not target_embedding:
        return 0.0
    try:
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity
        embedding1 = np.array(skill_embedding).reshape(1, -1)
        embedding2 = np.array(target_embedding).reshape(1, -1)
        similarity = float(cosine_similarity(embedding1, embedding2)[0][0])
        return similarity
    except Exception as e:
        print(f"[SkillMatch] Error calculating similarity: {e}")
        return 0.0


def find_matching_users(desired_skill: str, all_skills: List[Tuple[int, str, List[float]]]) -> List[Tuple[int, float]]:
    """
    Find users with similar skills using cosine similarity.
    Returns list of (user_id, similarity_score) tuples.
    """
    desired_embedding = get_skill_embedding(desired_skill)
    desired_text = (desired_skill or '').strip().lower()

    def lexical_score(skill_name: str) -> float:
        candidate = (skill_name or '').strip().lower()
        if not desired_text or not candidate:
            return 0.0
        if candidate == desired_text:
            return 1.0
        if desired_text in candidate or candidate in desired_text:
            return 0.85
        desired_parts = set(desired_text.replace('/', ' ').replace('-', ' ').split())
        candidate_parts = set(candidate.replace('/', ' ').replace('-', ' ').split())
        if desired_parts and candidate_parts:
            overlap = len(desired_parts & candidate_parts)
            if overlap:
                return overlap / max(len(desired_parts), len(candidate_parts))
        if candidate.startswith(desired_text) or desired_text.startswith(candidate):
            return 0.75
        return 0.0
    
    matches = []
    for user_id, skill_name, embedding in all_skills:
        similarity = 0.0
        # If we have embeddings, use cosine similarity
        if embedding and desired_embedding:
            similarity = calculate_skill_similarity(embedding, desired_embedding)
        else:
            # Fallback: use lexical similarity when embeddings are unavailable
            similarity = lexical_score(skill_name)

        matches.append((user_id, similarity))

    # Sort by similarity score in descending order
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[:10]  # Return top 10 matches


def find_matching_users_for_skills(desired_skills: List[str], all_skills: List[Tuple[int, str, List[float]]]) -> List[dict]:
    """
    Find users that best match a list of desired skills.
    Returns a list of dicts with keys: user_id, match_score, matching_skills
    """
    # Precompute embeddings for desired skills
    desired_embeddings = {s: get_skill_embedding(s) for s in desired_skills}
    desired_skill_text = {s: (s or '').strip().lower() for s in desired_skills}

    def lexical_score(skill_name: str, desired_skill: str) -> float:
        candidate = (skill_name or '').strip().lower()
        desired_text = desired_skill_text.get(desired_skill, '')
        if not desired_text or not candidate:
            return 0.0
        if candidate == desired_text:
            return 1.0
        if desired_text in candidate or candidate in desired_text:
            return 0.85
        desired_parts = set(desired_text.replace('/', ' ').replace('-', ' ').split())
        candidate_parts = set(candidate.replace('/', ' ').replace('-', ' ').split())
        if desired_parts and candidate_parts:
            overlap = len(desired_parts & candidate_parts)
            if overlap:
                return overlap / max(len(desired_parts), len(candidate_parts))
        if candidate.startswith(desired_text) or desired_text.startswith(candidate):
            return 0.75
        return 0.0

    # Map user_id -> desired_skill -> max similarity observed
    user_skill_max = {}
    user_matching_names = {}

    for user_id, skill_name, embedding in all_skills:
        user_skill_max.setdefault(user_id, {s: 0.0 for s in desired_skills})
        user_matching_names.setdefault(user_id, set())

        for ds in desired_skills:
            ds_embed = desired_embeddings.get(ds) or []
            
            # If embeddings are available, use semantic similarity.
            # Otherwise fall back to lexical similarity so exact skill matches
            # still produce non-zero scores when the model cannot load.
            if ds_embed and embedding:
                try:
                    sim = calculate_skill_similarity(embedding, ds_embed)
                except Exception:
                    sim = 0.0
            else:
                sim = lexical_score(skill_name, ds)

            # update max similarity for this desired skill for this user
            if sim > user_skill_max[user_id][ds]:
                user_skill_max[user_id][ds] = sim

            # Only highlight exact matches (case-insensitive)
            try:
                if skill_name and skill_name.lower() == ds.lower():
                    user_matching_names[user_id].add(skill_name)
            except Exception:
                pass

    # Aggregate scores per user (average of per-desired-skill max similarities)
    results = []
    for user_id, per_ds in user_skill_max.items():
        scores = list(per_ds.values()) if per_ds else [0.0]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        results.append({
            'user_id': user_id,
            'match_score': avg_score,
            'matching_skills': sorted(list(user_matching_names.get(user_id, [])))
        })

    # Sort by match_score desc and return top 10
    results.sort(key=lambda x: x['match_score'], reverse=True)
    return results[:10]


# Pre-load model at module import time (only if running management commands)
# Temporarily disabled to allow server startup
# import sys
# if 'manage.py' in sys.argv[0] and ('runserver' in sys.argv or 'run' in sys.argv):
#     print("[SkillMatch] Pre-loading model at startup...")
#     try:
#         _startup_model = get_model(force_reload=False)
#         if _startup_model:
#             print("[SkillMatch] ✓ Model pre-loaded successfully at startup")
#         else:
#             print("[SkillMatch] ✗ Model pre-load failed at startup")
#     except Exception as e:
#         print(f"[SkillMatch] ✗ Error pre-loading model at startup: {e}")

