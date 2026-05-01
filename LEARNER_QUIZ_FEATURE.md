# Learner Skill Verification Feature - Implementation Guide

## Overview
This feature allows learners to verify skills they've learned by taking a quiz after completing a learning session. If they score 70% or more, the skill is marked as "learned" on their profile.

---

## Backend Implementation (Completed ✅)

### Models Added
1. **LearnerSkillVerification** - Tracks if a learner has verified a skill
2. **LearnerQuizAttempt** - Tracks individual quiz attempts

### API Endpoints Added

#### 1. Submit Learner Quiz
**POST** `/api/quiz/submit-learner-quiz/`

**Request Body:**
```json
{
    "skill_name": "python",
    "learning_session_id": 123,
    "answers": {
        "1": 0,
        "2": 1,
        "3": 2,
        "4": 0,
        "5": 3
    }
}
```

**Response (Success):**
```json
{
    "success": true,
    "skill_name": "python",
    "score": 80,
    "correct_answers": 8,
    "total_questions": 10,
    "is_verified": true,
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

#### 2. Get Learner Verifications (Private)
**GET** `/api/quiz/learner-verifications/`

**Response:**
```json
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

#### 3. Get User Learned Skills (Public)
**GET** `/api/quiz/learner-verifications/<username>/`

Returns only verified (learned) skills for public profile.

---

## Frontend Integration Guide

### Step 1: Show Quiz Option After Learning Completion

In the learning session detail view, check the `can_take_quiz` flag:

```javascript
// After fetching learning session details
const sessionData = await fetchSessionDetails(sessionId);

if (sessionData.status === 'completed' && sessionData.can_take_quiz) {
    // Show "Take Quiz" button
    showTakeQuizButton(sessionData);
}
```

### Step 2: Show Quiz Questions

When user clicks "Take Quiz", fetch the quiz the same way as teacher quiz:

```javascript
const quizData = await fetch('/api/quiz/get-quiz/?skill_name=python')
    .then(r => r.json());

// Display 10 questions with options
displayQuizQuestions(quizData.questions);
```

### Step 3: Submit Quiz Answers

Create a form to collect answers and submit:

```javascript
async function submitLearnerQuiz(skillName, sessionId, answers) {
    const response = await fetch('/api/quiz/submit-learner-quiz/', {
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
    });
    
    const result = await response.json();
    
    if (result.is_verified) {
        // Score >= 70%: Show success message and update profile
        showSuccessMessage(`✅ Skill Learned! Score: ${result.score}%`);
        updateProfileSkills();
    } else {
        // Score < 70%: Show encouragement to retry
        showRetryMessage(`Score: ${result.score}%. Need 70% to learn. Try again!`);
    }
    
    // Display detailed results
    showQuizResults(result.results);
}
```

### Step 4: Display "Learned Skills" on Profile

Show learned skills separately from "Skills Teaching":

```javascript
async function displayLearnerProfile(username) {
    // Fetch learned skills
    const learnedSkills = await fetch(`/api/quiz/learner-verifications/${username}/`)
        .then(r => r.json());
    
    // Display in profile with different badge
    learnedSkills.learned_skills.forEach(skill => {
        displaySkillBadge(skill.skill_name, '✓ Learned', skill.verified_date);
    });
}
```

### Step 5: Update Personal Dashboard

Show learner's verified skills:

```javascript
async function displayMyLearnedSkills() {
    const mySkills = await fetch('/api/quiz/learner-verifications/')
        .then(r => r.json());
    
    console.log(`You have learned ${mySkills.total_learned} skills`);
    mySkills.learned_skills.forEach(skill => {
        console.log(`${skill.skill_name}: ${skill.score}%`);
    });
}
```

---

## UI/UX Flow

### 1. Learning Session View
```
┌─────────────────────────────┐
│ Learning Session Details    │
│                             │
│ Skill: Python               │
│ Teacher: John               │
│ Duration: 30 days           │
│ Status: ✅ Completed        │
│                             │
│ [Start Quiz] ← Show only if |
│               can_take_quiz  |
└─────────────────────────────┘
```

### 2. Quiz Taking View
```
┌─────────────────────────────┐
│ Quiz: Python (10 Questions) │
│                             │
│ Q1: Question text...        │
│  ☐ Option A                 |
│  ☐ Option B                 |
│  ☑ Option C                 |
│  ☐ Option D                 |
│                             │
│ [Previous] [Next] [Submit]  |
└─────────────────────────────┘
```

### 3. Results View
```
┌─────────────────────────────┐
│ Quiz Results                │
│                             │
│ Score: 80/100 (8/10)        │
│                             │
│ ✅ Skill Learned!           │
│ (Need 70% to pass)          │
│                             │
│ Question-by-question        │
│ review below...             │
│                             │
│ [Return to Profile]         |
└─────────────────────────────┘
```

### 4. Profile View (Learned Skills Section)
```
┌─────────────────────────────┐
│ My Profile                  │
│                             │
│ Skills Learned: (3)         │
│ ✓ Python (80%)    2026-04-26
│ ✓ JavaScript (75%)2026-04-20
│ ✓ React (92%)     2026-04-15
│                             │
│ Skills Teaching: (2)        │
│ • Java                      |
│ • Django                    |
└─────────────────────────────┘
```

---

## Key Differences from Teacher Verification

| Aspect | Teacher Verification | Learner Verification |
|--------|----------------------|----------------------|
| When verified | Can teach right away | After learning + quiz |
| Quiz requirement | Required for teaching | Required to mark as learned |
| Score threshold | 70% | 70% |
| Profile display | "Verified Skills" | "Learned Skills" |
| Related to | No relation | Linked to learning session |
| Affects teaching ability | Yes | No |

---

## Testing Checklist

- [ ] Complete a learning session as learner
- [ ] Verify `can_take_quiz=true` in session details
- [ ] Fetch quiz for the skill
- [ ] Submit quiz with 70%+ score
- [ ] Verify `is_verified=true` in response
- [ ] Check profile shows skill as "learned"
- [ ] Verify only 70%+ scores are shown in public profile
- [ ] Test retaking quiz with lower score (shouldn't downgrade)
- [ ] Test retaking quiz with higher score (should update)

---

## API Status

✅ Fully implemented and ready for frontend integration
- Models created and migrated
- All endpoints functional
- Authentication required
- Error handling included

