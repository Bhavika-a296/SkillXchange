# SkillXchange User Manual

Version: 1.0  
Date: May 1, 2026

## 1. Introduction

SkillXchange is a peer-to-peer learning platform where users can:
- teach skills
- learn skills from other users
- verify skills using quizzes
- discover people by skill
- track progress through sessions, points, and ratings

This manual explains how to set up the project, use all major features, and troubleshoot common issues.

## 2. Who This Manual Is For

- End users who want to use the app for learning and teaching
- Team members who need to run the app locally
- QA or demo users testing the complete flow

## 3. System Requirements

### Backend
- Python 3.8 or higher
- pip

### Frontend
- Node.js 14 or higher
- npm

### Optional (for AI quiz generation)
- Ollama installed and running locally
- A pulled model such as mistral

## 4. Project Structure Overview

- Root contains documentation and high-level project files
- backend contains Django API, models, and business logic
- frontend contains React application and UI
- google-meet-backend contains separate Node service for Google Meet integration

## 5. First-Time Setup

### Step 1: Backend setup

1. Open a terminal in the backend folder.
2. Create and activate a virtual environment.
3. Install dependencies.
4. Run migrations.
5. (Optional) Create admin user.
6. Start Django server.

Suggested commands:

    cd backend
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver

Backend URL:
- http://localhost:8000

### Step 2: Frontend setup

1. Open a second terminal in the frontend folder.
2. Install packages.
3. Start React app.

Suggested commands:

    cd frontend
    npm install
    npm start

Frontend URL:
- http://localhost:3000

### Step 3: Optional quiz AI setup (Ollama)

If quiz generation is enabled in your environment:

    ollama serve

In another terminal:

    ollama pull mistral

Default Ollama URL used by backend:
- http://localhost:11434

## 6. User Roles

SkillXchange supports flexible roles. A user can act as both:
- Learner: joins and completes learning sessions
- Teacher: provides sessions and earns rewards

## 7. Core User Workflows

### 7.1 Register and Login

1. Register an account.
2. Login with credentials.
3. Complete profile details.

### 7.2 Add Skills to Profile

Users can add skills to profile manually.

Important behavior:
- Skills verified by platform quizzes are now auto-added to profile skills.
- This means verified skills appear in profile skill sections and can be used for discover matching.

### 7.3 Discover by Skill

1. Open Discover section.
2. Search by skill keyword, for example python.
3. Review matching profiles.

Matching behavior:
- Profiles with verified matching skills are prioritized at the top.
- Verified match indicator appears on relevant profile cards.

### 7.4 Start a Learning Session

1. Open another user profile.
2. Click Join Learning for a selected skill.
3. Confirm session creation.

System actions:
- Points are deducted from learner when joining.
- Session status updates in learning dashboard.

### 7.5 Complete a Learning Session

1. Teacher marks session complete.
2. Session moves to completed state.
3. Points are awarded based on configuration.

### 7.6 Rate the Session

After completion:
1. Learner and teacher can rate each other.
2. Optional feedback text can be submitted.

### 7.7 Take Skill Verification Quiz

There are two quiz paths:

1. Teacher verification quiz
- Teacher takes quiz on a teaching skill
- Score 70 percent or above marks skill as verified

2. Learner verification quiz after learning completion
- Learner can take quiz for learned skill after completed session
- Score 70 percent or above verifies learned skill

Current verified-skill behavior:
- When a user passes, that skill is auto-synced into profile skills.
- Existing verified records are also backfilled into profile skills.

## 8. Points and Progress

The points system includes:
- join cost
- completion rewards for learner and teacher
- configurable defaults from admin

Progress can be tracked through:
- active sessions
- completed sessions
- learned and taught skill summaries

## 9. Leaderboard and Profile Indicators

- Leaderboard ranks users based on configured platform logic
- Verified skills and badges improve profile credibility
- Profile sections differentiate between verified and non-verified skill outcomes where applicable

## 10. Admin Guide (Basic)

Use Django Admin for configuration and monitoring:

1. Open admin panel at http://localhost:8000/admin
2. Login with admin account
3. Manage:
- users
- skills
- learning sessions
- quiz verification records
- point configurations

## 11. API and Integration References

For developers and integrators, see these docs:
- API_DOCUMENTATION.md
- INTEGRATION_GUIDE.md
- README_QUIZ_SYSTEM.md
- LEARNER_QUIZ_API_REFERENCE.md
- LEARNING_FLOW_IMPLEMENTATION.md

## 12. Troubleshooting

### App does not start

- Confirm backend dependencies installed from backend requirements file
- Confirm frontend dependencies installed from frontend package file
- Ensure backend and frontend run in separate terminals

### Frontend fails to run

Try:

    cd frontend
    npm install
    npm start

If port is busy, run on another port:

    set PORT=3001
    npm start

### Backend import or migration errors

Try:

    cd backend
    python manage.py makemigrations
    python manage.py migrate
    python manage.py check

### Quiz generation fails

- Ensure Ollama is running
- Ensure model is pulled
- Check backend logs for quiz generator errors

### Verified skills not visible immediately

- Refresh profile and discover pages
- Re-run backend server if code was recently updated
- Confirm user scored at least 70 percent

## 13. Best Practices for Demo and QA

- Use two test accounts to validate learner and teacher flows
- Complete one full cycle: discover, join, complete, quiz, verify, search
- Verify that passed skill appears in profile and discover ranking
- Capture screenshots for profile and discover states before and after quiz pass

## 14. Quick End-to-End Checklist

1. Start backend and frontend
2. Register two users
3. Add initial skills
4. Create learning session
5. Complete session
6. Submit rating
7. Take quiz and score 70 percent or above
8. Confirm skill appears in profile skills
9. Search same skill in Discover
10. Confirm verified profile appears with verified indicator near top

## 15. Support

If you face persistent setup or runtime issues:
- check project documentation files in root
- review backend server logs
- review browser developer console for frontend errors
