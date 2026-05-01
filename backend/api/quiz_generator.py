"""
AI Quiz Generator using Ollama (free, local LLM)
Requires Ollama to be running: ollama serve on localhost:11434
"""
import requests
import json
import logging
import os
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Ollama configuration
DEFAULT_OLLAMA_BASE_URLS = ["http://localhost:11434", "http://localhost:11435"]
ENV_OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_HOST")
MODEL_NAME = os.getenv("QUIZ_MODEL_NAME", "neural-chat")

# Generation fallback profiles.
# 1) default profile lets Ollama auto-select acceleration.
# 2) cpu-safe profile avoids CUDA runner issues seen on some Windows + older GPU setups.
GENERATION_PROFILES = [
    {"label": "default", "options": {}},
    {"label": "cpu-safe", "options": {"num_gpu": 0, "num_ctx": 2048}},
]

# Speed-first: avoid long retry loops for large (20-question) generations.
GENERATION_ATTEMPTS = int(os.getenv("QUIZ_GENERATION_ATTEMPTS", "2"))
GENERATION_TIMEOUT_SECONDS = int(os.getenv("QUIZ_GENERATION_TIMEOUT_SECONDS", "600"))


def _timeout_for_question_count(num_questions: int) -> int:
    # Fast batches should fail fast; larger requests still get adequate time.
    dynamic_timeout = 20 + (num_questions * 15)
    return min(GENERATION_TIMEOUT_SECONDS, max(60, dynamic_timeout))

LAST_GENERATION_STATUS: Dict[str, Optional[str]] = {
    "last_attempted_at": None,
    "last_status": "not_started",
    "last_url": None,
    "last_profile": None,
    "last_error": None,
}


def _set_generation_status(status: str, url: Optional[str] = None, profile: Optional[str] = None, error: Optional[str] = None) -> None:
    from datetime import datetime, timezone

    LAST_GENERATION_STATUS.update({
        "last_attempted_at": datetime.now(timezone.utc).isoformat(),
        "last_status": status,
        "last_url": url,
        "last_profile": profile,
        "last_error": error,
    })


def get_generation_status() -> Dict[str, Optional[str]]:
    """Return metadata about the most recent quiz generation attempt."""
    return dict(LAST_GENERATION_STATUS)


def _normalize_base_url(base_url: str) -> str:
    normalized = (base_url or "").strip().rstrip('/')
    if normalized and not normalized.startswith(("http://", "https://")):
        normalized = f"http://{normalized}"
    return normalized


def _candidate_base_urls() -> List[str]:
    candidates = []
    if ENV_OLLAMA_BASE_URL:
        candidates.append(_normalize_base_url(ENV_OLLAMA_BASE_URL))
    candidates.extend(DEFAULT_OLLAMA_BASE_URLS)

    unique_candidates = []
    for url in candidates:
        if url and url not in unique_candidates:
            unique_candidates.append(url)
    return unique_candidates


def generate_quiz(skill_name: str, num_questions: int = 20) -> Optional[List[Dict]]:
    """
    Generate MCQ quiz questions using Ollama AI (completely free, runs locally)
    
    Args:
        skill_name: Name of the skill to generate quiz for
        num_questions: Number of questions to generate (default: 20)
    
    Returns:
        List of quiz questions with options and correct answer, or None if generation fails
    """
    
    prompt = f"""Generate exactly {num_questions} multiple-choice questions for {skill_name} skill.

STRICT REQUIREMENTS:
1. Each question must have exactly 4 options
2. The "correct" field must be 0, 1, 2, or 3 (the index of correct option)
3. Questions must be practical and skill-focused
4. Keep wording concise and clear
5. ENSURE COMPLETE JSON - do not truncate responses

IMPORTANT: Return ONLY complete, valid JSON. No markdown, no extra text.

COMPLETE EXAMPLE with 2 questions:
{{
    "questions": [
        {{
            "question": "What is the first step in learning {skill_name}?",
            "options": ["Learn basics", "Build a project", "Read documentation", "Skip theory"],
            "correct": 0
        }},
        {{
            "question": "What is most important in {skill_name}?",
            "options": ["Speed", "Accuracy", "Understanding", "Luck"],
            "correct": 2
        }}
    ]
}}

Generate all {num_questions} questions now. Return complete JSON only."""

    try:
        print(f"[Quiz Generator] Requesting {num_questions} questions for {skill_name} from Ollama...")
        _set_generation_status("running")

        last_url = None
        last_profile = None

        # Retry generation to handle occasional malformed/non-JSON model responses.
        for attempt in range(1, GENERATION_ATTEMPTS + 1):
            response = None
            print(f"[Quiz Generator] Generation attempt {attempt}/{GENERATION_ATTEMPTS} for {skill_name}")

            for base_url in _candidate_base_urls():
                api_url = f"{base_url}/api/generate"
                last_url = api_url
                for profile in GENERATION_PROFILES:
                    last_profile = profile["label"]
                    payload = {
                        'model': MODEL_NAME,
                        'prompt': prompt,
                        'stream': False,
                        'temperature': 0.1,
                        'format': 'json',
                        'keep_alive': '10m',
                    }

                    merged_options = {
                        'num_predict': 4000,
                        'num_ctx': 2048,
                    }
                    if profile["options"]:
                        merged_options.update(profile["options"])
                    payload['options'] = merged_options

                    try:
                        request_timeout = _timeout_for_question_count(num_questions)
                        response = requests.post(
                            api_url,
                            json=payload,
                            timeout=request_timeout
                        )
                    except requests.exceptions.ConnectionError:
                        _set_generation_status(
                            status="connection_error",
                            url=api_url,
                            profile=profile["label"],
                            error="connection_refused",
                        )
                        response = None
                        break

                    if response.status_code == 200:
                        break

                    logger.warning(
                        f"Ollama generation failed via {api_url} using profile '{profile['label']}' "
                        f"(status={response.status_code})."
                    )
                    _set_generation_status(
                        status="http_error",
                        url=api_url,
                        profile=profile["label"],
                        error=f"status_{response.status_code}",
                    )

                if response is not None and response.status_code == 200:
                    _set_generation_status(
                        status="http_ok",
                        url=api_url,
                        profile=profile["label"],
                        error=None,
                    )
                    break

            if response is None:
                logger.error(
                    f"Cannot connect to Ollama at any configured endpoint. Last tried: {last_url}. "
                    "Is Ollama running? (ollama serve)"
                )
                _set_generation_status(
                    status="failed",
                    url=last_url,
                    profile=last_profile,
                    error="no_endpoint_reachable",
                )
                return None

            if response.status_code != 200:
                logger.error(
                    f"Ollama API error after trying fallback profiles (last profile: {last_profile}): "
                    f"{response.status_code} - {response.text}"
                )
                _set_generation_status(
                    status="failed",
                    url=last_url,
                    profile=last_profile,
                    error=f"status_{response.status_code}",
                )
                continue

            result = response.json()
            response_text = result.get('response', '').strip()

            # Extract JSON from response (AI might still add extra text).
            try:
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1

                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    quiz_data = json.loads(json_str)
                    questions = quiz_data.get('questions', [])

                    if questions:
                        print(f"[Quiz Generator] Successfully generated {len(questions)} questions")
                        _set_generation_status(
                            status="success",
                            url=last_url,
                            profile=last_profile,
                            error=None,
                        )
                        return questions
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse quiz JSON on attempt {attempt}: {e}")
                logger.error(f"Response was: {response_text[:500]}")
                _set_generation_status(
                    status="failed",
                    url=last_url,
                    profile=last_profile,
                    error="json_parse_error",
                )

        logger.error(f"Quiz generation failed for {skill_name} after {GENERATION_ATTEMPTS} attempts")
        return None
        
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to Ollama. Is Ollama running? (ollama serve)")
        _set_generation_status(status="failed", error="connection_error")
        return None
    except requests.exceptions.Timeout:
        logger.error("Ollama request timed out. Try again or increase timeout.")
        _set_generation_status(status="failed", error="timeout")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in quiz generation: {e}")
        _set_generation_status(status="failed", error=f"unexpected:{str(e)}")
        return None


def verify_quiz_format(questions: List[Dict]) -> bool:
    """Validate quiz question format"""
    for q in questions:
        if not all(key in q for key in ['question', 'options', 'correct']):
            return False
        if len(q.get('options', [])) != 4:
            return False
        if not isinstance(q.get('correct'), int) or q['correct'] not in [0, 1, 2, 3]:
            return False
    return True


def check_ollama_available() -> bool:
    """Check if Ollama is running and available"""
    for base_url in _candidate_base_urls():
        try:
            response = requests.get(
                f"{base_url}/api/tags",
                timeout=2
            )
            if response.status_code == 200:
                return True
        except requests.RequestException:
            continue
    return False
