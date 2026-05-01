# Learner Quiz System - Visual & Usage Guide 🎓

## Feature Overview

The learner quiz verification system allows students to verify they've truly learned a skill by taking a quiz after completing a learning session. Skills verified with a score of 70% or higher appear on their profile.

## User Journey

### Step 1: Complete Learning Session
```
Learning Session Status: In Progress → Complete Learning
↓
Session marks as completed with end_date
Server response: can_take_quiz = true (if not already verified)
```

### Step 2: Take Quiz (Modal Opens)
```
┌─────────────────────────────────────────┐
│  📝 Quiz: Python Programming            │  ← Skill name
│  10 Questions • Score 0% Complete       │  ← Progress info
├─────────────────────────────────────────┤
│  ├─ Question 1 of 10                    │
│  │  What is the capital of France?      │
│  │  ⃝ London   ⃝ Paris                  │
│  │  ⃝ Berlin   ⃝ Madrid                 │
│  │                                      │
│  ├─ Question 2 of 10                    │
│  │  [More questions...]                 │
│  │                                      │
│  └─ [Submit Quiz Button]                │
└─────────────────────────────────────────┘
```

### Step 3: View Results
```
┌─────────────────────────────────────────┐
│  ✅ Skill Verified!                     │
│  Your Score: 8/10 (80%)                 │
│  Status: VERIFIED                       │
├─────────────────────────────────────────┤
│  Question Review:                       │
│  ✓ Q1: Correct                          │
│  ✓ Q2: Correct                          │
│  ✗ Q3: Incorrect (You: A, Correct: B)   │
│  ...                                    │
└─────────────────────────────────────────┘
```

### Step 4: Profile Shows Verified Skill
```
┌──────────────────────────────────────┐
│  Profile: john_doe                   │
├──────────────────────────────────────┤
│  Skills I've Learned                 │
│  ┌─────────────────────────┐         │
│  │ ✓ Python Programming    │         │
│  │   Score: 80%            │         │
│  │   Verified • Jan 15     │         │
│  └─────────────────────────┘         │
│  ┌─────────────────────────┐         │
│  │ ✓ Web Development       │         │
│  │   Score: 85%            │         │
│  │   Verified • Jan 12     │         │
│  └─────────────────────────┘         │
└──────────────────────────────────────┘
```

## Component Locations

### In Learning Session (After Completion)
```
[Learning Session Card]
├── Skill Name: "Python Programming"
├── Status: Completed ✓
├── Completed on: Jan 15, 2024
├── Points earned: 50
├── [📝 Take Quiz - Verify Skill] ← NEW BUTTON
└── [Rate & Give Feedback]
```

### In Profile (New Section)
```
[Profile Page]
├── About Me
├── Resume
├── Login Streaks
├── Learning Journey
├── Skills I've Learned      ← NEW SECTION
│   ├── ✓ Python (80%, Jan 15)
│   ├── ✓ Web Dev (85%, Jan 12)
│   └── ✓ Data Science (72%, Jan 10)
├── Badges
└── [Verification Badges]
```

## Feature Behavior

### ✅ When Quiz Button Shows:
- Session status is 'completed'
- User is the learner (not the teacher)
- User hasn't already verified this skill
- Example: `can_take_quiz = true`

### ✅ During Quiz:
- Shows 10 multiple-choice questions
- Requires all questions to be answered
- Shows real-time progress bar
- Prevents submission with unanswered questions

### ✅ After Quiz Submission:
- Backend grades the quiz (70% = pass)
- Shows detailed results with:
  - Total score and percentage
  - Question-by-question review
  - Correct answer if you got it wrong
  - Verification status badge
- Profile automatically updates if verified

### ❌ What Happens if Score < 70%:
```
Your Score: 6/10 (60%)
Status: Not Verified

You didn't meet the 70% threshold.
Consider reviewing the material or taking the quiz again.
```

## Button States & Conditions

### "Take Quiz" Button Appears When:
```javascript
// In backend response:
session.can_take_quiz === true
↓
// Conditions:
session.status === 'completed'  // Session is finished
AND
isLearner === true              // User is the student
AND
!alreadyVerified                // Skill not verified yet
```

### Button Disappears When:
- ✅ Quiz is submitted and verified (button closes modal)
- ❌ Skill already verified (can_take_quiz = false)
- ✅ User is the teacher (not the learner)

## API Response Examples

### Get Session (with can_take_quiz field):
```json
{
  "id": 123,
  "skill_name": "Python Programming",
  "status": "completed",
  "can_take_quiz": true,          // NEW FIELD
  "start_date": "2024-01-01",
  "end_date": "2024-01-15",
  "learner": "john_doe",
  "teacher": "jane_smith",
  "points_awarded_learner": 50
}
```

### Submit Quiz Response (70% = verified):
```json
{
  "score": 8,
  "total": 10,
  "percentage": 80,
  "is_verified": true,            // KEY FIELD
  "message": "Congratulations! Your skill has been verified.",
  "results": [
    {
      "question_id": 1,
      "question_text": "What is Python?",
      "user_answer_text": "A programming language",
      "correct_answer_text": "A programming language",
      "is_correct": true
    },
    // ... more results
  ]
}
```

### Get Learned Skills (Own Profile):
```json
{
  "verified_skills": [
    {
      "skill_name": "Python Programming",
      "score": 80,
      "is_verified": true,
      "verification_date": "2024-01-15",
      "status": "verified"
    },
    {
      "skill_name": "Web Development",
      "score": 60,
      "is_verified": false,
      "verification_date": "2024-01-16",
      "status": "failed"
    }
  ]
}
```

### Get Learned Skills (Public Profile - other's username):
```json
// Only shows verified skills with is_verified=true
{
  "verified_skills": [
    {
      "skill_name": "Python Programming",
      "score": 80,
      "is_verified": true,
      "verification_date": "2024-01-15"
    },
    {
      "skill_name": "Web Development",
      "score": 85,
      "is_verified": true,
      "verification_date": "2024-01-14"
    }
  ]
}
```

## User-Facing Messages

### When Viewing Completed Session:
```
✨ Session Completed!
📝 Take Quiz - Verify Skill    ← Button appears here
```

### During Quiz:
```
✋ Please answer all questions (7/10)  ← Error if incomplete
```

### Quiz Results - Passed:
```
✅ Skill Verified!
Your Score: 8/10 (80%)
Status: VERIFIED

Congratulations! This skill now appears on your profile.
```

### Quiz Results - Failed:
```
❌ Not Verified
Your Score: 6/10 (60%)
Status: NOT VERIFIED

You need 70% to verify this skill. Try again!
```

## Mobile Responsiveness

### Mobile View (max-width: 768px):
```
┌─ [LearningSession] ─────────┐
│ Python Programming          │
│ Status: Completed ✓         │
│ [📝 Take Quiz Button]       │
│                             │
│ Modal:                      │
│ ┌───────────────────────┐   │
│ │  Quiz: Python    [✕]  │   │
│ │  Question 1/10        │   │
│ │  Full width content   │   │
│ │  [Submit]             │   │
│ └───────────────────────┘   │
└─────────────────────────────┘

Profile:
┌─ Skills I've Learned ───────┐
│ ✓ Python (80%)              │
│ ✓ Web Dev (85%)             │
│ ✓ Data Science (72%)        │
└─────────────────────────────┘
```

## Styling Details

### "Take Quiz" Button:
- **Color:** Purple/Blue gradient (`linear-gradient(135deg, #667eea 0%, #764ba2 100%)`)
- **Hover:** Scale up (1.05x) + shadow effect
- **Icon:** 📝 (pencil emoji)
- **Text:** "Take Quiz - Verify Skill"

### Skill Badges (on Profile):
- **Color:** Green gradient (`linear-gradient(135deg, #48bb78 0%, #38a169 100%)`)
- **Badge:** Green checkmark (✓)
- **Info:** Skill name, score, verification date
- **Layout:** Responsive grid (auto-fit columns)

### Quiz Modal:
- **Background:** Semi-transparent dark overlay (rgba(0, 0, 0, 0.6))
- **Width:** 900px max, 100% on mobile
- **Height:** 90vh max with scroll
- **Close Button:** X in top-right corner

## Feature Integration Points

### ✅ Completed Integration:
1. **Backend APIs:** All 3 endpoints fully functional
2. **React Components:** LearnerQuiz and LearnerSkills created
3. **LearningSession:** Quiz button added to completion section
4. **Profile Page:** Learned skills section added
5. **Styling:** All CSS files created and styled
6. **Modal Flow:** Quiz modal integrates seamlessly

### 🔄 Data Flow:
```
User completes session
  ↓
Backend: can_take_quiz = true (if not verified)
  ↓
Frontend: "Take Quiz" button appears
  ↓
Click button → Quiz modal opens
  ↓
LearnerQuiz fetches 10 questions from /quiz/get-quiz/
  ↓
User answers all questions
  ↓
Submit → POST to /quiz/submit-learner-quiz/
  ↓
Backend scores, creates LearnerSkillVerification record
  ↓
Response: is_verified = true/false
  ↓
Frontend: Shows results
  ↓
If verified: Page reloads
  ↓
Profile: Shows new verified skill with ✓ badge
```

## Testing Scenarios

### Scenario 1: Successful Verification
```
1. User searches "Python" → Finds teacher
2. Starts learning session
3. Completes learning → Session.status = 'completed'
4. Sees "Take Quiz" button
5. Takes 10-question quiz
6. Scores 80% → is_verified = true
7. Button closes modal
8. Page reloads
9. Profile shows "✓ Python (80%)"
```

### Scenario 2: Failed Verification
```
1. User takes quiz
2. Scores 60% → is_verified = false
3. Shows failure message
4. Can retake quiz (button still available)
5. Scores 72% on retry → is_verified = true
6. Profile updates
```

### Scenario 3: Already Verified
```
1. User has already verified "Python"
2. Visits learning session
3. "Take Quiz" button does NOT appear
4. can_take_quiz = false (because already verified)
5. Only "Rate & Give Feedback" button shows
```

## Summary

The learner quiz verification system provides:
- ✅ **Skill validation** through 10-question quizzes
- ✅ **70% passing threshold** to maintain quality
- ✅ **Profile badges** to showcase verified skills
- ✅ **Distinction between attempted and verified** skills
- ✅ **Seamless modal integration** without page navigation
- ✅ **Mobile-responsive design** for all devices
- ✅ **Privacy-aware** (only show verified to public profiles)

This allows learners to prove they've mastered a skill and build a credible portfolio of verified competencies.
