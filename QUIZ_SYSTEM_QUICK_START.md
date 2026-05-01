# 🚀 Quick Start: AI Quiz System

## What's Implemented

✅ **Complete backend system** for teacher skill verification  
✅ **3 new database models** (SkillQuiz, TeacherVerification, TeacherQuizAttempt)  
✅ **6 API endpoints** for quiz management  
✅ **AI quiz generation** using free Ollama  
✅ **Score calculation & verification** (70% = verified)  
✅ **Public teacher profiles** to display verified skills  

---

## 1️⃣ Setup Ollama (First Time Only - 5 minutes)

### Installation
```bash
# Download from https://ollama.ai
# Then in terminal:
ollama serve

# In another terminal:
ollama pull mistral  # or: ollama pull llama2
```

That's it! Ollama runs on `http://localhost:11434`

---

## 2️⃣ Test the System

### Generate Quiz for "Python"
```bash
curl -X POST http://localhost:8000/api/quiz/generate-quiz/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"skill_name": "python", "num_questions": 5}'
```
⏳ **First quiz takes 30-60 seconds** (AI generation)

### Teacher Takes Quiz
```bash
curl -X POST http://localhost:8000/api/quiz/submit-quiz/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill_name": "python",
    "answers": {"1": 2, "2": 1, "3": 0, "4": 3, "5": 2}
  }'
```

### Check Verification
```bash
# Teacher's private view
curl http://localhost:8000/api/quiz/teacher-verifications/ \
  -H "Authorization: Token YOUR_TOKEN"

# Learner's public view
curl http://localhost:8000/api/quiz/teacher-verifications/username/
```

---

## 3️⃣ Frontend Integration (Next Steps)

### Display verified badge on teacher profile
```jsx
<div className="teacher-card">
  {teacher.verified_skills && teacher.verified_skills.length > 0 && (
    <div className="verifications">
      {teacher.verified_skills.map(v => (
        <span key={v.skill_name} className="badge">✓ {v.skill_name}</span>
      ))}
    </div>
  )}
</div>
```

### Quiz-taking form  
```jsx
// Use the existing teacher profile page
// Add "Take Verification Quiz" button → quiz modal
// Submit answers → show score + verification badge
```

---

## 📋 Database Changes

**3 new tables created** (Migration 0013):
- `SkillQuiz` - Quiz questions
- `TeacherVerification` - Verification status  
- `TeacherQuizAttempt` - All attempts

---

## 🔗 API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /api/quiz/generate-quiz/` | Create AI quiz for a skill |
| `GET /api/quiz/get-quiz/?skill_name=...` | Get quiz questions |
| `POST /api/quiz/submit-quiz/` | Submit answers & get score |
| `GET /api/quiz/teacher-verifications/` | Get teacher's verified skills |
| `GET /api/quiz/teacher-verifications/<username>/` | Public teacher verification |
| `GET /api/quiz/check-ollama/` | Check if Ollama is running |

---

## ⚙️ Configuration

Ollama settings in `quiz_generator.py`:
```python
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"  # Change to "llama2" if preferred
```

---

## 📚 Full Documentation

See: `README_QUIZ_SYSTEM.md`

---

## Verification Badge Display

**Teachers see**:
- My verified skills in profile
- Verification scores & dates
- Option to "Verify New Skill" button

**Learners see**:
- When browsing teacher profiles: "✓ Verified in Python"
- When searching: Filter by "Verified teachers"
- When booking: Teacher's verification badges prominent

---

## ✅ Status

- Backend: **READY** ✅
- Migration: **APPLIED** ✅
- Ollama Integration: **CONFIGURED** ✅
- Testing: **Use curl commands above** 

**Next**: Add UI components to frontend for quiz-taking & badge display

---

## Troubleshooting

**"Ollama not running"**
```bash
ollama serve
# In another terminal:
ollama pull mistral
```

**"Quiz generation slow"**
- Normal! First generation takes 30-60 seconds
- Subsequent quizzes are cached

**"Port 11434 in use"**
```bash
# Use different port
ollama serve --port 11435
# Update quiz_generator.py: OLLAMA_API_URL = "http://localhost:11435/..."
```

---

**Ready to go!** 🎉
