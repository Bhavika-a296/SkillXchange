# Quick Reference - Learner Skill Verification API

## Setup Complete ✅

All backend functionality is ready. No additional setup needed.

---

## API Endpoints

### 1. Submit Quiz After Learning
```
POST /api/quiz/submit-learner-quiz/
Authorization: Bearer <token>

Body:
{
    "skill_name": "python",
    "learning_session_id": 123,
    "answers": {
        "1": 0,    // question_id: answer_index
        "2": 1,
        "3": 2,
        ...
    }
}

Response:
{
    "success": true,
    "skill_name": "python",
    "score": 80,
    "correct_answers": 8,
    "total_questions": 10,
    "is_verified": true,    // true if score >= 70%
    "message": "Score: 80%. ✅ Skill Learned!",
    "results": [
        {
            "question_id": 1,
            "question": "...",
            "user_answer": 0,
            "user_answer_text": "...",
            "correct_answer_index": 0,
            "correct_answer_text": "...",
            "is_correct": true
        }
    ]
}
```

### 2. Get My Learned Skills
```
GET /api/quiz/learner-verifications/
Authorization: Bearer <token>

Response:
{
    "learner": "username",
    "learned_skills": [
        {
            "skill_name": "python",
            "score": 80,
            "is_verified": true,
            "verified_date": "2026-04-26T10:30:00Z",
            "status": "passed",
            "badge": "✓"
        }
    ],
    "total_learned": 1
}
```

### 3. Get User's Learned Skills (Public)
```
GET /api/quiz/learner-verifications/john/

Response:
{
    "learner": "john",
    "learned_skills": [
        {
            "skill_name": "python",
            "score": 80,
            "verified_date": "2026-04-26",
            "badge": "✓"
        }
    ],
    "total_learned": 1
}
```

---

## Frontend Integration Steps

### Step 1: Check if User Can Take Quiz
```javascript
const sessionData = await fetch(`/api/learning/sessions/${sessionId}/`).then(r => r.json());

if (sessionData.status === 'completed' && sessionData.can_take_quiz) {
    // Show "Take Quiz" button
}
```

### Step 2: Fetch Quiz Questions
```javascript
const quizData = await fetch(`/api/quiz/get-quiz/?skill_name=${skillName}`).then(r => r.json());
// Same as teacher quiz - returns 10 questions
```

### Step 3: Submit Quiz
```javascript
const result = await fetch('/api/quiz/submit-learner-quiz/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
        skill_name: skillName,
        learning_session_id: sessionId,
        answers: answers  // { "1": 0, "2": 1, ... }
    })
}).then(r => r.json());

if (result.is_verified) {
    // Score >= 70%: Show success, skill is now "learned"
    showSuccess(`✅ Skill Learned! Score: ${result.score}%`);
} else {
    // Score < 70%: Encourage retry
    showEncouragement(`Need 70% to mark as learned. You got ${result.score}%. Try again!`);
}
```

### Step 4: Display Learned Skills on Profile
```javascript
const learnedSkills = await fetch(`/api/quiz/learner-verifications/${username}/`).then(r => r.json());

learnedSkills.learned_skills.forEach(skill => {
    // Display: ✓ python (80%) - Verified: 2026-04-26
});
```

---

## Database Models

### LearnerSkillVerification
- **learner** (ForeignKey to User)
- **learning_session** (ForeignKey to LearningSession, optional)
- **skill_name** (CharField)
- **score** (0-100)
- **status** (pending/passed/failed)
- **is_verified** (Boolean)
- **verified_date** (DateTime, when score >= 70%)
- **created_at**, **updated_at**

**Unique**: (learner, skill_name)

### LearnerQuizAttempt
- **learner** (ForeignKey to User)
- **skill_name** (CharField)
- **answers** (JSONField with answers)
- **score** (0-100)
- **attempted_at** (DateTime)

**Note**: No unique constraint - multiple attempts allowed

---

## Key Rules

✅ **Quiz only after learning completion**
- can_take_quiz is True only if session.status == 'completed'

✅ **70% to mark as learned**
- is_verified = True only if score >= 70

✅ **One verification per skill per learner**
- Can retake if first attempt < 70%
- Best score is kept

✅ **Public profile shows only learned skills**
- Only skills with is_verified=True are public
- Shows score and verification date

✅ **No changes to existing systems**
- TeacherVerification unchanged
- Skill system unchanged
- Learning system unchanged

---

## Error Handling

### Quiz Not Found
```
GET /api/quiz/get-quiz/?skill_name=unknown
Response: 404 - No quiz found for skill
Action: Generate quiz first or wait for generation
```

### Learning Session Not Completed
```
POST /api/quiz/submit-learner-quiz/
Response: 404 - Learning session not found or not completed
Action: Only submit after learning session is completed
```

### Invalid Answers Format
```
POST /api/quiz/submit-learner-quiz/
Response: 400 - skill_name and answers are required
Action: Ensure all required fields are provided
```

---

## Testing Endpoints

### Create Test Learning Session
```bash
curl -X POST http://localhost:8000/api/learning/join/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"teacher_id": 2, "skill_name": "python", "total_days": 30}'
```

### Accept Request (as teacher)
```bash
curl -X POST http://localhost:8000/api/learning/requests/123/accept/ \
  -H "Authorization: Bearer <teacher_token>"
```

### Complete Learning (as teacher)
```bash
curl -X POST http://localhost:8000/api/learning/end/123/ \
  -H "Authorization: Bearer <teacher_token>"
```

### Check Session (as learner)
```bash
curl http://localhost:8000/api/learning/sessions/123/ \
  -H "Authorization: Bearer <learner_token>"
# Should show: "can_take_quiz": true
```

### Get Quiz
```bash
curl http://localhost:8000/api/quiz/get-quiz/?skill_name=python \
  -H "Authorization: Bearer <token>"
```

### Submit Quiz
```bash
curl -X POST http://localhost:8000/api/quiz/submit-learner-quiz/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "skill_name": "python",
    "learning_session_id": 123,
    "answers": {"1": 0, "2": 1, "3": 2, "4": 0, "5": 1, "6": 2, "7": 0, "8": 3, "9": 1, "10": 2}
  }'
```

---

## Status: READY FOR FRONTEND ✅

All backend APIs are implemented, tested, and ready for integration.
