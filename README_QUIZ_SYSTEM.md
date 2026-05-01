# Teacher Skill Verification Quiz System

## Overview
This system uses **free local AI (Ollama)** to generate skill verification quizzes for teachers. Teachers take quizzes to earn verification badges, building trust with learners.

## Features
✅ **Free & No API Costs** - Ollama runs locally on your server  
✅ **AI-Generated Quizzes** - Automatically creates skill-specific questions  
✅ **Teacher Verification Badges** - Teachers earn "✓ Verified" badges  
✅ **Learner Trust** - Learners can see which teachers are verified  
✅ **Public Profiles** - Display verified skills on teacher profiles  

---

## Setup Instructions

### Step 1: Install Ollama (One-time setup)

**Windows/Mac/Linux:**
1. Download from https://ollama.ai
2. Install and run: `ollama serve`
3. In a new terminal, download a model:
   ```bash
   ollama pull mistral   # Lightweight & fast (4GB)
   # OR
   ollama pull llama2    # More powerful (7GB)
   ```
4. Server runs on `http://localhost:11434`

**Verify it's working:**
```bash
curl http://localhost:11434/api/tags
# Should show list of installed models
```

### Step 2: Backend is Ready
All code is already implemented:
- ✅ Models: `SkillQuiz`, `TeacherVerification`, `TeacherQuizAttempt`
- ✅ Views: Quiz generation, submission, verification display
- ✅ API Endpoints: All quiz endpoints live
- ✅ Database: Migration 0013 applied

### Step 3: Test the System

#### 1. Check if Ollama is Available
```bash
curl http://localhost:8000/api/quiz/check-ollama/
```
Response:
```json
{
  "ollama_available": true,
  "message": "Ollama is running and ready"
}
```

#### 2. Generate Quiz for a Skill
```bash
curl -X POST http://localhost:8000/api/quiz/generate-quiz/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill_name": "python",
    "num_questions": 5
  }'
```

Response:
```json
{
  "success": true,
  "skill_name": "python",
  "generated_count": 5,
  "saved_count": 5,
  "message": "Successfully generated and saved 5 questions for python"
}
```

#### 3. Get Quiz Questions (Without Answers)
```bash
curl http://localhost:8000/api/quiz/get-quiz/?skill_name=python \
  -H "Authorization: Token YOUR_TOKEN"
```

Response:
```json
{
  "skill_name": "python",
  "total_questions": 5,
  "questions": [
    {
      "id": 1,
      "question": "Which of the following is a mutable data type in Python?",
      "options": ["tuple", "string", "list", "int"],
      "difficulty": "easy"
    }
  ]
}
```

#### 4. Submit Quiz Answers
```bash
curl -X POST http://localhost:8000/api/quiz/submit-quiz/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill_name": "python",
    "answers": {
      "1": 2,
      "2": 1,
      "3": 0,
      "4": 3,
      "5": 1
    }
  }'
```

Response:
```json
{
  "success": true,
  "skill_name": "python",
  "score": 80,
  "correct_answers": 4,
  "total_questions": 5,
  "is_verified": true,
  "message": "Score: 80%. ✅ Verified!"
}
```

#### 5. Get Teacher's Verified Skills
```bash
curl http://localhost:8000/api/quiz/teacher-verifications/ \
  -H "Authorization: Token YOUR_TOKEN"
```

Response:
```json
{
  "teacher": "john_doe",
  "verified_skills": [
    {
      "skill_name": "python",
      "score": 85,
      "is_verified": true,
      "verified_date": "2025-03-15T10:30:00Z",
      "badge": "✓"
    }
  ],
  "total_verified": 1
}
```

#### 6. Get Public Teacher Profile (Without Auth)
```bash
curl http://localhost:8000/api/quiz/teacher-verifications/john_doe/
```

Response:
```json
{
  "teacher": "john_doe",
  "verified_skills": [
    {
      "skill_name": "python",
      "score": 85,
      "verified_date": "2025-03-15",
      "badge": "✓"
    }
  ],
  "total_verified": 1
}
```

---

## API Endpoints Summary

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/quiz/check-ollama/` | GET | ✓ | Check if Ollama is running |
| `/api/quiz/generate-quiz/` | POST | ✓ | Generate AI quiz for a skill |
| `/api/quiz/get-quiz/` | GET | ✓ | Get quiz questions (no answers) |
| `/api/quiz/submit-quiz/` | POST | ✓ | Submit answers and get score |
| `/api/quiz/teacher-verifications/` | GET | ✓ | Get teacher's verified skills |
| `/api/quiz/teacher-verifications/<username>/` | GET | ✗ | Get public teacher verification |

---

## Database Models

### SkillQuiz
```python
{
  "id": 1,
  "skill_name": "python",
  "question": "What is a mutable data type?",
  "options": ["tuple", "string", "list", "int"],
  "correct_index": 2,  # Index of correct option
  "difficulty": "easy",
  "created_at": "2025-03-15T10:00:00Z"
}
```

### TeacherVerification
```python
{
  "id": 1,
  "teacher": 5,  # User ID
  "skill_name": "python",
  "score": 85,  # 0-100
  "total_questions": 5,
  "correct_answers": 4,
  "status": "passed",  # or "failed" or "pending"
  "is_verified": true,  # True if score >= 70
  "verified_date": "2025-03-15T10:30:00Z",
  "created_at": "2025-03-15T10:20:00Z"
}
```

### TeacherQuizAttempt (All Attempts)
```python
{
  "id": 1,
  "teacher": 5,
  "skill_name": "python",
  "answers": {
    "1": 2,
    "2": 1,
    "3": 0
  },
  "score": 85,
  "attempted_at": "2025-03-15T10:30:00Z"
}
```

---

## Frontend Integration (Coming Soon)

### Display Teacher Verification Badge
```jsx
// Show on teacher profile
{teacher.is_verified && <span className="badge">✓ Verified</span>}
```

### Quiz Submission Form
```jsx
const [answers, setAnswers] = useState({});

const handleSubmit = async () => {
  const res = await api.post('/quiz/submit-quiz/', {
    skill_name: skillName,
    answers: answers
  });
  
  if (res.data.is_verified) {
    alert(`✅ You're verified in ${skillName}!`);
  }
};
```

---

## Troubleshooting

### "Ollama is not running"
```bash
# In a terminal, start Ollama
ollama serve

# Make sure model is downloaded
ollama pull mistral
```

### "Quiz generation timeout"
- First quiz generation can take 30-60 seconds (AI generation)
- Subsequent quizzes are faster
- Check server logs for Ollama activity

### "Questions format is invalid"
- Ollama sometimes returns malformed JSON
- Just regenerate - usually succeeds on retry

### "Port 11434 already in use"
```bash
# Change Ollama port
ollama serve --port 11435
# Update this in quiz_generator.py
```

---

## Verification Pass/Fail Criteria

**Score >= 70%** = ✅ **VERIFIED** (Can use as teacher)  
**Score < 70%** = ❌ **Not Verified** (Can retake)  

---

## Future Enhancements

1. **Skill-Specific Question Banks** - Curate best questions
2. **Difficulty Levels** - Filter easy/medium/hard
3. **Timed Quizzes** - 15-minute limit per quiz
4. **Multiple Attempts** - Track best score
5. **Admin Review** - Manual verification for critical skills
6. **Certificate PDFs** - Download verification certificates

---

## Setup Checklist

- [ ] Ollama installed and running (`ollama serve`)
- [ ] Model downloaded (`ollama pull mistral`)
- [ ] Migration applied (`migrate`)
- [ ] API endpoints accessible
- [ ] Quiz generation working (POST `/api/quiz/generate-quiz/`)
- [ ] Teacher can take quiz (POST `/api/quiz/submit-quiz/`)
- [ ] Verification displays on profile (GET `/api/quiz/teacher-verifications/<username>/`)

---

**Status**: ✅ Ready to use!  
**Cost**: 💰 Completely free (local AI)  
**Time to generate quiz**: ⏱️ 30-60 seconds per skill (first time)
