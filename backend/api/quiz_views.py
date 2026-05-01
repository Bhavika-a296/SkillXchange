"""
Views for teacher skill verification quiz system and learner quiz system
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from django.db import close_old_connections
from datetime import timedelta
import threading

from .models import (
    SkillQuiz, TeacherVerification, TeacherQuizAttempt, 
    LearnerSkillVerification, LearnerQuizAttempt, LearningSession, Skill
)
from .quiz_generator import generate_quiz, verify_quiz_format, check_ollama_available, get_generation_status


# Prevent duplicate concurrent generation requests per user+skill.
IN_FLIGHT_GENERATIONS = set()
IN_FLIGHT_LOCK = threading.Lock()

QUIZ_POOL_SIZE = 10
POOL_REFRESH_AGE_MINUTES = 15
POOL_BUILD_MAX_ATTEMPTS = 6
POOL_BATCH_SIZE = 5


def _sync_verified_skill_to_profile(user, skill_name):
    """Ensure a verified platform skill is present in the user's profile skills."""
    normalized_skill = (skill_name or '').strip()
    if not normalized_skill:
        return

    existing_skill = Skill.objects.filter(user=user, name__iexact=normalized_skill).first()
    if existing_skill:
        return

    Skill.objects.create(
        user=user,
        name=normalized_skill,
        description='Verified on SkillXchange via quiz',
        proficiency_level='advanced',
    )


def _serialize_questions(questions_qs):
    return [
        {
            'id': q.id,
            'question': q.question,
            'options': q.options,
            'difficulty': q.difficulty,
        }
        for q in questions_qs
    ]


def _mark_in_flight(key):
    with IN_FLIGHT_LOCK:
        if key in IN_FLIGHT_GENERATIONS:
            return False
        IN_FLIGHT_GENERATIONS.add(key)
        return True


def _clear_in_flight(key):
    with IN_FLIGHT_LOCK:
        IN_FLIGHT_GENERATIONS.discard(key)


def _refresh_quiz_pool_async(skill_name: str, num_questions: int = QUIZ_POOL_SIZE):
    skill_key = skill_name.lower()
    generation_key = ('pool', skill_key)

    if not _mark_in_flight(generation_key):
        return

    def _worker():
        close_old_connections()
        try:
            if not check_ollama_available():
                return

            # For 10 questions, use simple sequential generation (2 batches)
            # Parallel overhead doesn't help since Ollama processes sequentially anyway
            built_questions = []
            seen_questions = set()

            for batch_num in range((num_questions + POOL_BATCH_SIZE - 1) // POOL_BATCH_SIZE):
                remaining = num_questions - len(built_questions)
                if remaining <= 0:
                    break

                requested_count = min(POOL_BATCH_SIZE, remaining)
                print(
                    f"[Quiz Pool] Building '{skill_name}': {len(built_questions)}/{num_questions} ready, "
                    f"requesting next {requested_count}"
                )
                batch = generate_quiz(skill_name, requested_count)
                if not batch or not verify_quiz_format(batch):
                    print(f"[Quiz Pool] Batch {batch_num + 1} validation failed, skipping...")
                    continue

                for q in batch:
                    key = (q.get('question') or '').strip().lower()
                    if not key or key in seen_questions:
                        continue
                    seen_questions.add(key)
                    built_questions.append(q)
                    if len(built_questions) >= num_questions:
                        break

            if len(built_questions) < num_questions:
                print(
                    f"[Quiz Pool] Incomplete pool for '{skill_name}': "
                    f"{len(built_questions)}/{num_questions}"
                )
                return

            # Save to database
            SkillQuiz.objects.filter(skill_name__iexact=skill_name).delete()
            for q in built_questions[:num_questions]:
                SkillQuiz.objects.create(
                    skill_name=skill_name,
                    question=q['question'],
                    options=q['options'],
                    correct_index=q['correct'],
                    difficulty=q.get('difficulty', 'medium')
                )
            print(f"[Quiz Pool] ✓ Quiz generation complete: '{skill_name}' with {num_questions} questions")
        finally:
            _clear_in_flight(generation_key)
            close_old_connections()

    threading.Thread(target=_worker, daemon=False).start()


def _pool_is_stale(questions_qs):
    newest = questions_qs.order_by('-created_at').first()
    if not newest:
        return True
    return newest.created_at < timezone.now() - timedelta(minutes=POOL_REFRESH_AGE_MINUTES)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_ollama_status(request):
    """Check if Ollama AI service is available"""
    available = check_ollama_available()
    generation_status = get_generation_status()
    return Response({
        'ollama_available': available,
        'message': 'Ollama is running and ready' if available else 'Ollama is not running. Please start it with: ollama serve',
        'generation_status': generation_status,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_skill_quiz(request):
    """
    Generate AI quiz for a skill using a pre-generated pool for fast response.
    POST /api/quiz/generate-quiz/
    Body: {"skill_name": "python", "num_questions": 10}
    """
    try:
        skill_name = request.data.get('skill_name', '').strip()
        num_questions = request.data.get('num_questions', 10)
        
        if not skill_name:
            return Response(
                {'error': 'skill_name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if num_questions < QUIZ_POOL_SIZE or num_questions > QUIZ_POOL_SIZE:
            num_questions = QUIZ_POOL_SIZE

        existing_questions = SkillQuiz.objects.filter(skill_name__iexact=skill_name).order_by('id')
        ready_count = existing_questions.count()

        # Fast path: return existing pool immediately.
        if ready_count >= QUIZ_POOL_SIZE:
            should_refresh = _pool_is_stale(existing_questions)
            if should_refresh:
                _refresh_quiz_pool_async(skill_name, num_questions)

            served_questions = _serialize_questions(existing_questions[:QUIZ_POOL_SIZE])
            return Response({
                'success': True,
                'source': 'pool',
                'skill_name': skill_name,
                'generated_count': len(served_questions),
                'saved_count': len(served_questions),
                'total_questions': len(served_questions),
                'questions': served_questions,
                'message': f'Served {len(served_questions)} ready questions for {skill_name}'
            }, status=status.HTTP_200_OK)

        generation_key = (request.user.id, skill_name.lower())
        if generation_key in IN_FLIGHT_GENERATIONS or ('pool', skill_name.lower()) in IN_FLIGHT_GENERATIONS:
            return Response(
                {
                    'success': False,
                    'in_progress': True,
                    'message': f'Quiz generation is in progress for {skill_name}. Please wait a moment.'
                },
                status=status.HTTP_202_ACCEPTED
            )

        # No ready pool yet: kick off async generation and return immediately.
        _refresh_quiz_pool_async(skill_name, num_questions)

        return Response(
            {
                'success': False,
                'in_progress': True,
                'message': f'Preparing AI quiz for {skill_name}. Please wait a few seconds and retry.'
            },
            status=status.HTTP_202_ACCEPTED
        )
        
    except Exception as e:
        return Response(
            {'error': f'Unexpected error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_skill_quiz(request):
    """
    Get quiz questions for a skill
    GET /api/quiz/get-quiz/?skill_name=python
    """
    skill_name = request.query_params.get('skill_name', '').strip()
    
    if not skill_name:
        return Response(
            {'error': 'skill_name query parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    questions = SkillQuiz.objects.filter(skill_name__iexact=skill_name).order_by('id')  # Explicit ordering
    total_found = questions.count()
    generation_in_progress = ('pool', skill_name.lower()) in IN_FLIGHT_GENERATIONS

    # If no questions exist yet
    if total_found == 0:
        # If generation is already in progress, return 202
        if generation_in_progress:
            return Response(
                {
                    'success': False,
                    'in_progress': True,
                    'skill_name': skill_name,
                    'ready_count': 0,
                    'required_count': QUIZ_POOL_SIZE,
                    'message': f'Building quiz for {skill_name} (0/{QUIZ_POOL_SIZE} ready). Please wait...'
                },
                status=status.HTTP_202_ACCEPTED
            )
        
        # If not in progress, start generation and return 202
        _refresh_quiz_pool_async(skill_name, QUIZ_POOL_SIZE)
        return Response(
            {
                'success': False,
                'in_progress': True,
                'skill_name': skill_name,
                'ready_count': 0,
                'required_count': QUIZ_POOL_SIZE,
                'message': f'Starting AI quiz generation for {skill_name}. Please wait...'
            },
            status=status.HTTP_202_ACCEPTED
        )

    # If questions exist but incomplete
    if total_found < QUIZ_POOL_SIZE:
        if not generation_in_progress:
            _refresh_quiz_pool_async(skill_name, QUIZ_POOL_SIZE)

        return Response(
            {
                'success': False,
                'in_progress': True,
                'skill_name': skill_name,
                'ready_count': total_found,
                'required_count': QUIZ_POOL_SIZE,
                'message': f'Building quiz for {skill_name} ({total_found}/{QUIZ_POOL_SIZE} ready).'
            },
            status=status.HTTP_202_ACCEPTED
        )

    # Return quiz WITHOUT revealing correct answers
    quiz_data = []
    for q in questions[:QUIZ_POOL_SIZE]:
        quiz_data.append({
            'id': q.id,
            'question': q.question,
            'options': q.options,
            'difficulty': q.difficulty,
            # Don't include 'correct_index' - that's revealed only after submission
        })
    
    return Response({
        'skill_name': skill_name,
        'total_questions': len(quiz_data),
        'questions': quiz_data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_quiz(request):
    """
    Submit quiz answers and get score
    POST /api/quiz/submit-quiz/
    Body: {
        "skill_name": "python",
        "answers": {
            "1": 0,  # question_id: selected_option_index
            "2": 1,
            "3": 2
        }
    }
    """
    try:
        teacher = request.user
        skill_name = request.data.get('skill_name', '').strip()
        answers = request.data.get('answers', {})
        
        if not skill_name or not answers:
            return Response(
                {'error': 'skill_name and answers are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all quiz questions for this skill
        questions = SkillQuiz.objects.filter(skill_name__iexact=skill_name).order_by('id')
        
        if not questions.exists():
            return Response(
                {'error': f'No quiz found for skill: {skill_name}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Grade the quiz
        correct_count = 0
        total_count = len(questions)
        results = []
        
        for question in questions:
            question_id = str(question.id)
            user_answer = answers.get(question_id)
            
            is_correct = False
            if user_answer is not None:
                # Ensure both values are integers for comparison
                try:
                    user_answer_int = int(user_answer) if isinstance(user_answer, str) else user_answer
                    correct_index_int = int(question.correct_index) if isinstance(question.correct_index, str) else question.correct_index
                    is_correct = user_answer_int == correct_index_int
                    if is_correct:
                        correct_count += 1
                except (ValueError, TypeError) as e:
                    print(f"Error comparing answers for question {question_id}: {e}")
                    is_correct = False
            
            # Get the option text for display
            user_option_text = None
            if user_answer is not None and isinstance(question.options, list):
                try:
                    user_answer_int = int(user_answer) if isinstance(user_answer, str) else user_answer
                    if 0 <= user_answer_int < len(question.options):
                        user_option_text = question.options[user_answer_int]
                except (ValueError, TypeError, IndexError):
                    user_option_text = None
            
            correct_option_text = None
            if isinstance(question.options, list):
                try:
                    correct_index_int = int(question.correct_index) if isinstance(question.correct_index, str) else question.correct_index
                    if 0 <= correct_index_int < len(question.options):
                        correct_option_text = question.options[correct_index_int]
                except (ValueError, TypeError, IndexError):
                    correct_option_text = None
            
            results.append({
                'question_id': question.id,
                'question': question.question,
                'user_answer': user_answer,
                'user_answer_text': user_option_text,
                'correct_answer_index': question.correct_index,
                'correct_answer_text': correct_option_text,
                'is_correct': is_correct,
            })
        
        # Calculate score
        score = round((correct_count / total_count * 100)) if total_count > 0 else 0
        is_passed = score >= 70
        
        # Save quiz attempt
        attempt = TeacherQuizAttempt.objects.create(
            teacher=teacher,
            skill_name=skill_name,
            answers=answers,
            score=score
        )
        
        # Update or create verification record
        verification, created = TeacherVerification.objects.get_or_create(
            teacher=teacher,
            skill_name=skill_name,
            defaults={
                'score': score,
                'total_questions': total_count,
                'correct_answers': correct_count,
                'status': 'passed' if is_passed else 'failed',
                'is_verified': is_passed,
                'verified_date': timezone.now() if is_passed else None
            }
        )
        
        # Update if not first attempt and this score is better
        if not created:
            if score > verification.score:
                verification.score = score
                verification.correct_answers = correct_count
                verification.total_questions = total_count
                verification.status = 'passed' if is_passed else 'failed'
                verification.is_verified = is_passed
                if is_passed:
                    verification.verified_date = timezone.now()
                verification.save()

        if is_passed:
            _sync_verified_skill_to_profile(teacher, skill_name)
        
        return Response({
            'success': True,
            'skill_name': skill_name,
            'score': score,
            'correct_answers': correct_count,
            'total_questions': total_count,
            'is_verified': is_passed,
            'message': f"Score: {score}%. {'✅ Verified!' if is_passed else '❌ Not passed yet. Try again!'}" if is_passed else f"Score: {score}%. Need 70% to verify.",
            'results': results  # Only show detailed results to the teacher themselves
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error submitting quiz: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_teacher_verifications(request):
    """
    Get all verified skills for a teacher
    GET /api/quiz/teacher-verifications/
    """
    teacher = request.user
    verifications = TeacherVerification.objects.filter(teacher=teacher).order_by('-verified_date')
    
    data = []
    for v in verifications:
        data.append({
            'skill_name': v.skill_name,
            'score': v.score,
            'is_verified': v.is_verified,
            'verified_date': v.verified_date,
            'status': v.status,
            'badge': '✓' if v.is_verified else '✗'
        })
    
    return Response({
        'teacher': teacher.username,
        'verified_skills': data,
        'total_verified': sum(1 for v in data if v['is_verified'])
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_verifications(request, username):
    """
    Get public teacher verification info
    GET /api/quiz/teacher-verifications/<username>/
    """
    from django.contrib.auth.models import User
    
    try:
        teacher = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {'error': f'User {username} not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Only show verified (passed) skills publicly
    verifications = TeacherVerification.objects.filter(
        teacher=teacher,
        is_verified=True
    ).order_by('-verified_date')
    
    data = []
    for v in verifications:
        data.append({
            'skill_name': v.skill_name,
            'score': v.score,
            'verified_date': v.verified_date.strftime('%Y-%m-%d') if v.verified_date else None,
            'badge': '✓'
        })
    
    return Response({
        'teacher': teacher.username,
        'verified_skills': data,
        'total_verified': len(data)
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_learner_quiz(request):
    """
    Submit learner quiz answers after completing a learning session
    POST /api/quiz/submit-learner-quiz/
    Body: {
        "skill_name": "python",
        "learning_session_id": 123,
        "answers": {
            "1": 0,  # question_id: selected_option_index
            "2": 1,
            "3": 2
        }
    }
    """
    try:
        learner = request.user
        skill_name = request.data.get('skill_name', '').strip()
        learning_session_id = request.data.get('learning_session_id')
        answers = request.data.get('answers', {})
        
        if not skill_name or not answers:
            return Response(
                {'error': 'skill_name and answers are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify that the learner has a completed learning session for this skill
        learning_session = None
        if learning_session_id:
            try:
                learning_session = LearningSession.objects.get(
                    id=learning_session_id,
                    learner=learner,
                    skill_name__iexact=skill_name,
                    status='completed'
                )
            except LearningSession.DoesNotExist:
                return Response(
                    {'error': 'Learning session not found or not completed'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Get all quiz questions for this skill
        questions = SkillQuiz.objects.filter(skill_name__iexact=skill_name).order_by('id')
        
        if not questions.exists():
            return Response(
                {'error': f'No quiz found for skill: {skill_name}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Grade the quiz
        correct_count = 0
        total_count = len(questions)
        results = []
        
        for question in questions:
            question_id = str(question.id)
            user_answer = answers.get(question_id)
            
            is_correct = False
            if user_answer is not None:
                # Ensure both values are integers for comparison
                try:
                    user_answer_int = int(user_answer) if isinstance(user_answer, str) else user_answer
                    correct_index_int = int(question.correct_index) if isinstance(question.correct_index, str) else question.correct_index
                    is_correct = user_answer_int == correct_index_int
                    if is_correct:
                        correct_count += 1
                except (ValueError, TypeError) as e:
                    print(f"Error comparing answers for question {question_id}: {e}")
                    is_correct = False
            
            # Get the option text for display
            user_option_text = None
            if user_answer is not None and isinstance(question.options, list):
                try:
                    user_answer_int = int(user_answer) if isinstance(user_answer, str) else user_answer
                    if 0 <= user_answer_int < len(question.options):
                        user_option_text = question.options[user_answer_int]
                except (ValueError, TypeError, IndexError):
                    user_option_text = None
            
            correct_option_text = None
            if isinstance(question.options, list):
                try:
                    correct_index_int = int(question.correct_index) if isinstance(question.correct_index, str) else question.correct_index
                    if 0 <= correct_index_int < len(question.options):
                        correct_option_text = question.options[correct_index_int]
                except (ValueError, TypeError, IndexError):
                    correct_option_text = None
            
            results.append({
                'question_id': question.id,
                'question': question.question,
                'user_answer': user_answer,
                'user_answer_text': user_option_text,
                'correct_answer_index': question.correct_index,
                'correct_answer_text': correct_option_text,
                'is_correct': is_correct,
            })
        
        # Calculate score
        score = round((correct_count / total_count * 100)) if total_count > 0 else 0
        is_passed = score >= 70
        
        # Save quiz attempt
        attempt = LearnerQuizAttempt.objects.create(
            learner=learner,
            skill_name=skill_name,
            answers=answers,
            score=score
        )
        
        # Update or create verification record
        verification, created = LearnerSkillVerification.objects.get_or_create(
            learner=learner,
            skill_name=skill_name,
            defaults={
                'learning_session': learning_session,
                'score': score,
                'total_questions': total_count,
                'correct_answers': correct_count,
                'status': 'passed' if is_passed else 'failed',
                'is_verified': is_passed,
                'verified_date': timezone.now() if is_passed else None
            }
        )
        
        # Update if not first attempt and this score is better
        if not created:
            if score > verification.score:
                verification.score = score
                verification.correct_answers = correct_count
                verification.total_questions = total_count
                verification.status = 'passed' if is_passed else 'failed'
                verification.is_verified = is_passed
                if is_passed:
                    verification.verified_date = timezone.now()
                verification.save()

        if is_passed:
            _sync_verified_skill_to_profile(learner, skill_name)
        
        return Response({
            'success': True,
            'skill_name': skill_name,
            'score': score,
            'correct_answers': correct_count,
            'total_questions': total_count,
            'is_verified': is_passed,
            'message': f"Score: {score}%. {'✅ Skill Learned!' if is_passed else '❌ Need 70% to mark skill as learned. Try again!'}" if is_passed else f"Score: {score}%. Need 70% to mark skill as learned.",
            'results': results
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error submitting quiz: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_learner_verifications(request):
    """
    Get all verified (learned) skills for a learner
    GET /api/quiz/learner-verifications/
    """
    learner = request.user
    verifications = LearnerSkillVerification.objects.filter(learner=learner).order_by('-verified_date')
    
    data = []
    for v in verifications:
        data.append({
            'skill_name': v.skill_name,
            'score': v.score,
            'is_verified': v.is_verified,
            'verified_date': v.verified_date,
            'status': v.status,
            'badge': '✓' if v.is_verified else '✗'
        })
    
    return Response({
        'learner': learner.username,
        'learned_skills': data,
        'total_learned': sum(1 for v in data if v['is_verified'])
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_learned_skills(request, username):
    """
    Get public learner verification info (learned skills)
    GET /api/quiz/learner-verifications/<username>/
    """
    from django.contrib.auth.models import User
    
    try:
        learner = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {'error': f'User {username} not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Only show verified (passed) skills publicly
    verifications = LearnerSkillVerification.objects.filter(
        learner=learner,
        is_verified=True
    ).order_by('-verified_date')
    
    data = []
    for v in verifications:
        data.append({
            'skill_name': v.skill_name,
            'score': v.score,
            'verified_date': v.verified_date.strftime('%Y-%m-%d') if v.verified_date else None,
            'badge': '✓'
        })
    
    return Response({
        'learner': learner.username,
        'learned_skills': data,
        'total_learned': len(data)
    }, status=status.HTTP_200_OK)
