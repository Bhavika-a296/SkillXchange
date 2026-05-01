# SkillXchange - Complete Presentation README

**Date:** May 1, 2026  
**Project:** SkillXchange - Peer-to-Peer Skill Exchange Platform  
**Tagline:** Connect. Learn. Teach. Verify. Earn. 🚀

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Problem & Solution](#problem--solution)
3. [Core Features](#core-features)
4. [Technical Architecture](#technical-architecture)
5. [Complete Feature Breakdown](#complete-feature-breakdown)
6. [New Functionalities (Latest)](#new-functionalities-latest)
7. [User Workflows](#user-workflows)
8. [Demonstration Flow](#demonstration-flow)
9. [Database & System Design](#database--system-design)
10. [Presentation Speaking Points](#presentation-speaking-points)

---

## Project Overview

### What is SkillXchange?

SkillXchange is a **full-stack peer-to-peer learning platform** that enables users to exchange skills in a gamified, verified ecosystem. Users can:
- **Teach** skills they know
- **Learn** skills they want
- **Earn Points** by teaching others
- **Spend Points** to learn from others
- **Get Verified** through AI-generated quizzes
- **Build Trust** through ratings and badges

### Core Value Proposition

1. **Free Learning** - No subscription fees, point-based economy
2. **AI-Verified Skills** - Credibility through automated quizzes
3. **Smart Matching** - Semantic skill matching using BERT embeddings
4. **Real-time Communication** - Instant messaging with file sharing
5. **Gamification** - Badges, points, streaks, and leaderboard

### Target Users

- Students seeking affordable skill development
- Professionals looking to share expertise
- Lifelong learners in any domain
- Community-driven knowledge builders

---

## Problem & Solution

### Current Problems in Skill Exchange

| Problem | Impact |
|---------|--------|
| **High Cost of Learning** | Many can't afford professional courses or tutors |
| **Lack of Practice Platforms** | Limited real-world skill application opportunities |
| **Poor Skill Matching** | Hard to find the right teacher for specific needs |
| **No Trust Signals** | Learners don't know if a teacher is actually qualified |
| **Time Inflexibility** | Traditional learning has rigid schedules |
| **No Motivation** | Limited incentive for experts to share knowledge |

### Our Solution

✅ **Point-Based Economy** - Free exchange through earned rewards  
✅ **AI Skill Verification** - Instant credibility through quizzes  
✅ **BERT Embeddings** - Find teachers even with different skill names  
✅ **Verified Badges** - Trust signals on profiles  
✅ **Flexible Sessions** - Users choose duration and schedule  
✅ **Gamified System** - Points, badges, streaks keep users engaged  

---

## Core Features

### Feature Matrix

| # | Feature | Who Developed | Type | Status |
|---|---------|---------------|------|--------|
| 1 | Authentication & Profiles | Foundation | Core | ✅ Complete |
| 2 | AI-Powered Skill Matching | Foundation | AI/ML | ✅ Complete |
| 3 | Resume Upload & Parsing | Foundation | Automation | ✅ Complete |
| 4 | User Discovery & Connections | Foundation | Social | ✅ Complete |
| 5 | Real-Time Messaging | Foundation | Realtime | ✅ Complete |
| 6 | Notification System | Foundation | UX | ✅ Complete |
| 7 | Learning Request Workflow | Advanced | Business Logic | ✅ Complete |
| 8 | Points Economy | Advanced | Gamification | ✅ Complete |
| 9 | Learning Session Tracking | Advanced | Progress | ✅ Complete |
| 10 | Mutual Ratings & Feedback | Advanced | Trust | ✅ Complete |
| 11 | Badge Achievement System | Advanced | Gamification | ✅ Complete |
| 12 | Teacher Verification Quiz | Advanced | Verification | ✅ Complete |
| 13 | **Learner Verification Quiz** | **Advanced** | **Verification** | **✅ Complete** |
| 14 | **Verified Skills Auto-Sync** | **Advanced** | **Integration** | **✅ Complete** |
| 15 | **Discover Ranking by Verified** | **Advanced** | **Search** | **✅ Complete** |

---

## Technical Architecture

### System Components

```
┌────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                        │
│              Port 3000 - User Interface Layer                 │
└────────────────┬─────────────────────────────────────────────┘
                 │ HTTP/WebSocket
                 ↓
┌────────────────────────────────────────────────────────────────┐
│                    API Gateway (Django)                        │
│     Port 8000 - REST API + WebSocket Handler                 │
│                                                                │
│  ├─ Authentication & Auth                                    │
│  ├─ User Profiles & Skills                                  │
│  ├─ Learning Sessions & Workflow                            │
│  ├─ Quiz Generation & Verification                          │
│  ├─ Points & Transactions                                   │
│  ├─ Messaging & Notifications                               │
│  └─ AI/ML Processing                                        │
└────────────┬──────────────────────┬──────────────┬─────────┘
             │                      │              │
             ↓                      ↓              ↓
      ┌─────────────┐      ┌─────────────┐  ┌─────────────┐
      │  SQLite DB  │      │  Ably RTM   │  │ Transformers│
      │  (Persist)  │      │  (Messages) │  │  (ML Model) │
      └─────────────┘      └─────────────┘  └─────────────┘
```

### Technology Stack

#### Backend
- **Framework**: Django 5.2.6
- **API**: Django REST Framework 3.16.1
- **Database**: SQLite (Development) / PostgreSQL (Production-ready)
- **Authentication**: Token-based (DRF)
- **AI/ML**: 
  - sentence-transformers 5.1.0 (BERT)
  - scikit-learn 1.7.2 (similarity)
  - nltk 3.9.1 (text processing)
  - torch 2.3.1 (deep learning)
- **Real-time**: Ably SDK 2.1.1
- **PDF Processing**: PyPDF2 3.0.1

#### Frontend
- **Framework**: React 19.1.1
- **Routing**: React Router DOM 7.9.1
- **HTTP**: Axios 1.12.2
- **Real-time**: Ably SDK 2.14.0
- **Styling**: Pure CSS3 (responsive, modern design)

#### Deployment-Ready
- **WSGI Server**: Gunicorn
- **Reverse Proxy**: Compatible with Nginx
- **Static Files**: WhiteNoise integration
- **Environment**: Docker-ready structure

---

## Complete Feature Breakdown

### 1. User Authentication & Profile Management

**What it does:**
- Secure user registration and login
- Profile customization with bio, avatar, location
- Resume upload and parsing
- Skill management (add/remove/verify)

**How it works:**
```
Register → Validate Email/Username → Hash Password → Token Generated
   ↓
Login → Verify Credentials → Issue Auth Token → Access Protected Routes
```

**Technology:**
- Django Token Authentication
- Password hashing (PBKDF2 + SHA256)
- Protected API endpoints
- React Context for state management

**What to say:**
> "We built secure authentication using token-based auth. Users register once and can instantly access the platform. Their profile becomes their learning/teaching resume."

---

### 2. AI-Powered Skill Matching

**What it does:**
- Intelligently matches learners with teachers
- Handles skill name variations and synonyms
- Returns ranked results by similarity score

**Algorithm:**
```python
Process:
1. Load BERT model (paraphrase-MiniLM-L6-v2)
2. Encode search query into 384-dim vector
3. Compare against all user skill embeddings
4. Calculate cosine similarity scores
5. Filter by threshold (0.4) and rank by score
6. Return top matches ordered by relevance

Example:
  "Python" ↔ "Python Programming" = 0.92 match ✓
  "ML" ↔ "Machine Learning" = 0.87 match ✓
  "Cooking" ↔ "Python" = 0.12 match ✗
```

**Technology:**
- sentence-transformers (BERT model)
- scikit-learn cosine_similarity
- Vector embeddings (384 dimensions)

**What to say:**
> "Our matching algorithm uses advanced AI embeddings. When a student searches for 'Python,' we don't just look for exact matches. We understand that 'Python Programming', 'Python Dev', and 'Python' are similar skills. This semantic understanding powers our discovery engine."

---

### 3. Learning Request & Approval Workflow

**What it does:**
- Learner requests to learn from a teacher
- Teacher reviews and approves/rejects
- Session starts only after approval
- Points deducted on approval (not request)

**Workflow:**
```
┌─────────────────────────────────────────────────────────────┐
│ 1. Learner browses Discover                               │
│    Finds a teacher with desired skill                     │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Learner clicks "Join Learning"                          │
│    Creates learning request (status: pending)              │
│    Points NOT deducted yet                                 │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Teacher receives notification                           │
│    Reviews request with learner details                    │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
        ┌──────────┴──────────┐
        ↓                     ↓
    APPROVE              REJECT
        ↓                     ↓
  Points Deducted      Session Cancelled
  Session Starts       No Points Deducted
  Status: Active
```

**Key Features:**
- Validation before approval (points check)
- Instant notifications to both parties
- Session tracking with timestamps
- Request history maintained

**What to say:**
> "The request-approval workflow gives control to teachers. They can review who wants to learn from them before the session starts. This prevents accidental point loss and builds trust."

---

### 4. Point Economy System

**What it does:**
- Creates sustainable peer-to-peer economy
- Motivates both teaching and learning
- Tracks all transactions transparently

**Economy Model:**

| Action | Points | When | User |
|--------|--------|------|------|
| **Start Session** | -100 | On approval | Learner |
| **Complete Session** | +50 | On completion | Learner |
| **Teach Session** | +150 | On completion | Teacher |
| **Initial Balance** | 1000 | On signup | All Users |

**Net Impact:**
- Learner: Spend 100, Earn 50 = **-50 net** per skill
- Teacher: Earn 150 = **+150 net** per skill
- System encourages teaching over learning

**Configuration:**
All values are configurable via Django Admin:
```
PointConfiguration table:
  join_learning_cost: 100
  learning_completion_reward_learner: 50
  learning_completion_reward_teacher: 150
  initial_user_points: 1000
```

**Transparency:**
Every transaction logged in PointTransaction table:
```
User → Learner
Amount → -100
Type → "join_learning"
Related → learning_session_id
Timestamp → 2026-05-01 10:30:00
```

**What to say:**
> "We created a self-sustaining economy. Teachers earn 150 points for each person they teach, learners pay 100 to learn but earn back 50 on completion. This balance incentivizes knowledge sharing while keeping the system sustainable."

---

### 5. Learning Session Lifecycle

**What it does:**
- Tracks session from creation to completion
- Shows real-time progress
- Manages session duration and dates

**Session States:**

```
pending_approval
      ↓
    (reject) → rejected
      ↓ (approve)
    active
      ↓
  in_progress (after acceptance)
      ↓
  completed
      ↓
  rated (both rated each other)
```

**Progress Calculation:**
```
Days Elapsed = Current Date - Session Start Date
Days Remaining = Session Duration - Days Elapsed
Progress % = (Days Elapsed / Duration) × 100

Example:
Duration: 30 days
Current: Day 10
Progress: (10/30) × 100 = 33.3%
Remaining: 20 days
```

**UI Display:**
- Progress bar showing percentage
- Days remaining count
- Status indicator (badge)
- Completion button (when approved)

**What to say:**
> "Each session is tracked from start to finish. Users can see exactly how many days have passed and how much time is left. Progress is calculated automatically based on the session duration they agreed to."

---

### 6. Mutual Rating & Feedback System

**What it does:**
- After session completion, both users can rate each other
- 5-star rating with optional written feedback
- Builds trust and accountability

**Rating Features:**
- Star rating (1-5 stars)
- Written feedback (optional, up to 500 chars)
- Skill-specific feedback
- Average rating displayed on profile
- Public visibility of ratings

**Logic:**
```
1. Session marked as completed by either party
2. Both users receive notification: "Rate your session"
3. Can rate independently at different times
4. Rating saved with timestamp
5. Average calculated across all ratings
6. Displayed prominently on profile
```

**Trust Impact:**
- High-rated users get more learning requests
- Low-rated users face consequences
- Community self-regulates quality
- New users can build credibility quickly

**What to say:**
> "After a session ends, both learner and teacher rate each other. This creates trust signals on the platform. A teacher with a 4.8 star average is clearly doing a great job. Ratings make the community accountable and trustworthy."

---

### 7. Badge Achievement System

**What it does:**
- Awards milestone badges for skill accumulation
- Motivates consistent platform usage
- Displays on profile with visual indicators

**Badge Types & Thresholds:**

| Badge | Requirement | Icon | Color | Type |
|-------|-------------|------|-------|------|
| Learner Bronze | 3 skills learned | 🥉 | Bronze | Learner |
| Learner Silver | 5 skills learned | 🥈 | Silver | Learner |
| Learner Gold | 10 skills learned | 🥇 | Gold | Learner |
| Teacher Bronze | 3 skills taught | 📚 | Bronze | Teacher |
| Teacher Silver | 5 skills taught | 📖 | Silver | Teacher |
| Teacher Gold | 10 skills taught | 👑 | Gold | Teacher |

**Awarding Logic:**

```python
def check_and_award_badges(user):
    # Count unique completed skills as learner
    learner_skills = LearningSession.objects
        .filter(learner=user, status='completed')
        .values('skill_name')
        .distinct()
        .count()
    
    # Count unique completed skills as teacher
    teacher_skills = LearningSession.objects
        .filter(teacher=user, status='completed')
        .values('skill_name')
        .distinct()
        .count()
    
    # Check thresholds: 3, 5, 10
    thresholds = [3, 5, 10]
    
    # Award badges automatically
    for threshold in thresholds:
        if learner_skills >= threshold:
            Badge.objects.get_or_create(
                user=user,
                badge_type=f'learner_{threshold}'
            )
```

**Trigger Points:**
- Automatically checked after session completion
- Can't be revoked once earned
- Multiple badges can be earned
- Notifications sent when earned

**What to say:**
> "We gamified learning with milestone-based badges. When a user learns their third skill, they earn a bronze badge. Five skills? Silver. Ten skills? Gold. Badges are automatic and visible on profiles—they're proof of dedication and skill diversity."

---

### 8. Real-Time Messaging System

**What it does:**
- Instant one-on-one messaging between users
- File sharing (images, documents, resumes)
- Message history persistence
- Unread message indicators

**Technology:**
- Ably Realtime API (WebSocket-based)
- Pub/Sub channels for instant delivery
- Database persistence for history
- Real-time presence detection

**Features:**
```
User A ──→ Message ──→ Ably Channel ──→ User B
           (sent instantly)     (persisted)

Features:
✓ Message history (searchable)
✓ File attachments up to 10MB
✓ Unread message count
✓ Typing indicators
✓ Online/offline status
✓ Message timestamps
```

**What to say:**
> "We use Ably for real-time messaging. When a learner needs clarification mid-session, they can instantly chat with their teacher. Messages are delivered in under 100ms and stored permanently for reference."

---

### 9. Notification System

**What it does:**
- Alerts users about important platform events
- Different notification types for different events
- Read/unread tracking
- Quick action links

**Notification Types:**

| Event | When | Who Gets | Action |
|-------|------|----------|--------|
| Learning request | Someone requests to learn | Teacher | Review request |
| Request approved | Teacher approves | Learner | Start session |
| Request rejected | Teacher rejects | Learner | Browse again |
| Session completed | Either party marks done | Both | Rate each other |
| Badge earned | Threshold reached | Learner/Teacher | View profile |
| New message | Message received | Recipient | Open chat |
| Rating received | After rating | Both | View feedback |

**Display Strategy:**
1. **Toast Popup** - Instant visual feedback (5-second auto-hide)
2. **Notification Center** - Persistent list with history
3. **Badge Count** - Unread count on bell icon

**What to say:**
> "Notifications keep users informed without overwhelming them. They see a toast when something important happens, but notifications disappear once read. This reduces clutter while keeping the platform engaging."

---

### 10. Teacher Skill Verification Quiz

**What it does:**
- AI-generated quizzes to verify teacher expertise
- Score 70%+ = Verified badge on profile
- Increases credibility and learner confidence

**Quiz Generation Process:**

```
1. Teacher initiates verification for skill (e.g., "Python")
2. System calls Ollama local AI model
3. AI generates 10 multiple-choice questions
4. Questions cached for future use
5. Teacher takes quiz in timed format
6. Answers graded automatically
7. Score calculated (0-100%)
8. If score >= 70%: Mark as verified
9. Verified badge appears on teacher profile
```

**Quiz Details:**
- **Duration**: ~10 minutes
- **Questions**: 10 multiple-choice (4 options each)
- **Passing Score**: 70% (7 out of 10)
- **Multiple Attempts**: Yes, best score kept
- **Time Limit**: None (self-paced)

**Verification Badge:**
- Public profile displays "✓ Verified in Python"
- Shows score and verification date
- Prominently featured in Discover cards
- Increases match ranking priority

**What to say:**
> "Teachers can prove their skills through AI-generated quizzes. If they score 70% or higher, they get a verified badge. This builds trust instantly—learners know this teacher has been tested and proven competent in that skill."

---

### 11. Learner Skill Verification Quiz (NEW!)

**What it does:**
- After completing a learning session, learner can take a quiz
- Score 70%+ = Skill marked as "Learned" on profile
- Creates verified learning outcomes
- Auto-synced to profile skills

**Workflow:**

```
1. Learning session completed
2. Learner sees "Take Quiz" button
3. Learner takes quiz (same questions as teacher verification)
4. Score calculated instantly
5. If score >= 70%:
   ✓ Mark as "Learned" 
   ✓ Add to profile skills
   ✓ Appear in Discover search
   ✓ Get notification
6. If score < 70%:
   ✗ Can retake anytime
   ✗ Best score kept
```

**Key Differences from Teacher Quiz:**
- **Prerequisite**: Must have completed learning session
- **Auto-Sync**: Score updates profile skills automatically
- **Profile Impact**: Verified learned skills appear in "Your Skills"
- **Discover Impact**: Verified learners appear in skill searches

**How It Works:**
```
Teacher teaches Python → Learner completes → Takes quiz
                                                   ↓
                                            Score >= 70%?
                                           /              \
                                          /                \
                                       YES                 NO
                                        ↓                   ↓
                                   Verified             Try Again
                                   Badge ✓              Later
                                   Added to 
                                   Profile Skills
                                   Searchable in
                                   Discover
```

**What to say:**
> "Learners don't just complete sessions—they can verify what they learned through a quiz. When they score 70% or higher, that skill automatically appears in their profile. This creates a verified learning record that builds credibility and makes them discoverable as someone who knows that skill."

---

### 12. Verified Skills Auto-Sync to Profile (NEW!)

**What it does:**
- When a quiz is passed (70%+), skill is automatically added to user's profile
- Both teacher and learner verified skills are synced
- Creates single source of truth for skill ownership
- Enables downstream features (discover search, profile display)

**Auto-Sync Process:**

```
User passes quiz (Score >= 70%)
         ↓
Trigger: _sync_verified_skill_to_profile()
         ↓
Check: Does skill already exist in Skill table?
    ↙                                      ↘
  YES (skip)                            NO (create)
    ↓                                      ↓
Continue                            Create Skill record
                                   - name: "Python"
                                   - proficiency: "advanced"
                                   - description: "Verified on SkillXchange"
                                   - user: current_user
                                   ↓
                                Skill now appears in:
                                • Your Skills section
                                • Profile public view
                                • Discover search pool
                                • Skill matching queries
```

**Backfill Process:**
All existing verified skills (historical) were backfilled:
- 3 new skills created from teacher verifications
- 2 skills already present (no duplicates)
- Result: Immediate consistency for existing users

**Technical Implementation:**
```python
def _sync_verified_skill_to_profile(user, skill_name):
    """Ensure verified skill is in user's profile skills."""
    # Normalize skill name
    normalized = skill_name.strip()
    if not normalized:
        return
    
    # Check if already exists (case-insensitive)
    if Skill.objects.filter(user=user, name__iexact=normalized).exists():
        return  # Already present, skip
    
    # Create skill record
    Skill.objects.create(
        user=user,
        name=normalized,
        description='Verified on SkillXchange via quiz',
        proficiency_level='advanced'
    )
    # Skill now discoverable and appears in profile
```

**Impact:**
- ✅ Single source of truth for verified skills
- ✅ Profile skills always match verification status
- ✅ Discover search includes all verified skills
- ✅ No data inconsistency between modules
- ✅ Backward compatible (existing data backfilled)

**What to say:**
> "When someone passes a verification quiz, we automatically add that skill to their profile. This means verified skills immediately appear in their 'Your Skills' section and they become discoverable for that skill. It's a seamless integration that keeps the platform data consistent."

---

### 13. Discover Search Ranking by Verified Skills (NEW!)

**What it does:**
- When searching for a skill in Discover, verified users appear first
- Shows visual indicator (star badge) for verified matches
- Prioritizes trust and credibility in search results

**Ranking Algorithm:**

```
Search Query: "Python"
         ↓
Find all users with "Python" skill
         ↓
Split into 2 groups:
    ├─ Group A: Verified (score >= 70%)
    └─ Group B: Unverified
         ↓
Return: Group A first (verified), then Group B (unverified)
         ↓
Display:
  ✓ [Star Badge] Alice - Python (Verified)
  ✓ [Star Badge] Bob - Python (Verified)
    [No badge]  Carol - Python
    [No badge]  Dave - Python
```

**Visual Indicators:**
- ⭐ Gold star badge on verified cards
- Prominent card styling (light background)
- Verification date shown
- Match score displayed

**Matching Behavior:**
1. Find semantically similar skills (BERT matching)
2. Split by verification status (verified/unverified)
3. Sort within groups by match score
4. Return verified matches first
5. Show visual star indicator

**API Response:**
```json
{
  "results": [
    {
      "id": 1,
      "username": "alice",
      "skill": "Python",
      "match_score": 0.95,
      "has_verified_match": true,      // NEW!
      "verified_skills": ["Python"],   // NEW!
      "verified_matching_skills": ["Python"]  // NEW!
    },
    {
      "id": 2,
      "username": "bob",
      "skill": "python-dev",
      "match_score": 0.88,
      "has_verified_match": true,
      "verified_skills": ["Python"],
      "verified_matching_skills": ["Python"]
    },
    {
      "id": 3,
      "username": "carol",
      "skill": "Python",
      "match_score": 0.92,
      "has_verified_match": false,     // Unverified
      "verified_skills": [],
      "verified_matching_skills": []
    }
  ]
}
```

**What to say:**
> "When you search for 'Python' in Discover, the platform automatically ranks teachers who have verified Python skills at the top. You'll see a gold star badge next to verified teachers. This makes it easy to find trustworthy teachers—no guessing required."

---

### 14. Leaderboard & Progress Tracking

**What it does:**
- Ranks users by engagement and skill accumulation
- Shows learning metrics and achievements
- Motivates competition and participation

**Metrics Displayed:**
- Total skills learned
- Total skills taught
- Points balance
- Badges earned
- Current streak
- Average rating

**Ranking Factors:**
- Skills completed (main factor)
- Points earned
- Badges achievement
- Session completion rate

**What to say:**
> "The leaderboard shows who's most active on the platform. Users are ranked by skills they've learned and taught, creating friendly competition. It motivates consistent engagement."

---

## User Workflows

### Complete End-to-End Flow

**Scenario:** Alice wants to learn Python from verified teachers

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Alice registers on SkillXchange                    │
│ - Creates account                                          │
│ - Sets profile (bio, avatar)                              │
│ - Gets 1000 initial points                                │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Alice opens Discover page                          │
│ - Searches "Python"                                        │
│ - AI matching finds similar skills                         │
│ - Results ranked by verified status                        │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Alice sees verified teacher Bob                    │
│ - Bob has "✓ Verified in Python" badge                    │
│ - 4.8 star rating from 12 learners                         │
│ - Click "View Profile"                                    │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Alice clicks "Join Learning"                       │
│ - Selects session duration: 30 days                        │
│ - Creates learning request                                 │
│ - Alice gets notification: "Waiting for approval"          │
│ - Points NOT deducted yet                                 │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 5: Bob receives notification                          │
│ - "Alice wants to learn Python from you"                  │
│ - Reviews Alice's profile (ratings, badges)              │
│ - Clicks "Approve"                                        │
│ - Alice loses 100 points                                  │
│ - Session marked as "active"                              │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 6: Alice & Bob in active session                      │
│ - Chat in real-time messaging                             │
│ - Alice completes Python assignments                       │
│ - 30-day duration tracked with progress bar                │
│ - Either can mark session complete                         │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 7: Session marked complete                            │
│ - Bob: +150 points                                         │
│ - Alice: +50 points                                        │
│ - Net: Alice spent 50 points total                         │
│ - Both get notifications to rate each other               │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 8: Alice & Bob rate each other                        │
│ - Alice gives Bob 5 stars: "Great teacher!"               │
│ - Bob gives Alice 4 stars: "Enthusiastic learner"         │
│ - Ratings displayed on profiles                           │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 9: Alice takes verification quiz (NEW!)               │
│ - Sees "Take Python Quiz" button                           │
│ - Completes 10-question quiz                              │
│ - Scores 78% (✓ passes 70% threshold)                     │
│ - Python skill marked as "Learned"                        │
│ - Added to profile skills automatically                   │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 10: Alice now discoverable (NEW!)                     │
│ - Other users search "Python"                              │
│ - Alice appears with "✓ Verified Learner" status          │
│ - Profile shows verified "Python" skill                    │
│ - Alice can now teach Python to others                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Demonstration Flow

### What to Demo (5-10 minutes)

**Account Setup Phase (1 minute)**
1. Open browser → http://localhost:3000
2. Register Test Account 1 (Teacher)
3. Register Test Account 2 (Learner)

**Setup Skills Phase (2 minutes)**
1. Teacher Account: Add "Python" skill
2. Teacher Account: Take verification quiz
3. Show verification quiz passing (≥70%)
4. Show "✓ Verified" badge appears

**Discovery Phase (2 minutes)**
1. Switch to Learner Account
2. Open Discover page
3. Search "Python"
4. Show verified teacher at top with star badge ⭐
5. Click teacher profile

**Learning Request Phase (2 minutes)**
1. Click "Join Learning"
2. Select 30-day duration
3. Show points deduction
4. Switch to Teacher: Show request notification
5. Teacher approves request
6. Show session becomes "active"

**Session Completion Phase (2 minutes)**
1. Show session progress bar
2. Click "Complete Session"
3. Show points awarded
4. Show rating interface
5. Both rate each other
6. Show ratings on profile

**Verification Quiz Phase (1 minute)**
1. Switch to Learner
2. Show "Take Quiz" button
3. Take quick quiz (show a few questions)
4. Complete with score ≥ 70%
5. Show skill auto-added to profile
6. Refresh Discover → Show learner now appears as verified

**Final State (show)**
1. Leaderboard with both users ranked
2. Profile showing badges
3. Verified skills section
4. Points transaction history

---

## Database & System Design

### Database Schema

```sql
Key Tables:

User (Django built-in)
├─ id, username, email, password, date_joined

UserProfile
├─ user_id (FK), bio, avatar_url, created_at

Skill (NEW AUTO-SYNC!)
├─ id, user_id (FK), name, proficiency_level
├─ description: "Verified on SkillXchange via quiz"
├─ embedding (384-dim BERT vector)
└─ Note: Auto-populated from quiz passes

LearningSession
├─ id, learner_id (FK), teacher_id (FK)
├─ skill_name, status, start_date, end_date
├─ total_days, created_at

SkillRating
├─ id, session_id (FK), rater_id (FK)
├─ rating (1-5), feedback, created_at

UserPoints
├─ user_id (FK), balance, created_at, updated_at

PointTransaction
├─ id, user_id (FK), amount, type
├─ related_object (session/badge), timestamp

Badge
├─ id, user_id (FK), badge_type
├─ awarded_date, created_at

TeacherVerification (Teacher Quiz Results)
├─ id, teacher_id (FK), skill_name
├─ score, is_verified (True if score >= 70)
├─ verified_date, created_at

LearnerSkillVerification (Learner Quiz Results) (NEW!)
├─ id, learner_id (FK), skill_name
├─ score, is_verified (True if score >= 70)
├─ verified_date, created_at

Message
├─ id, sender_id (FK), receiver_id (FK)
├─ content, file, read, created_at

Notification
├─ id, user_id (FK), type, title
├─ message, sender_id (FK), link, read, created_at
```

### API Endpoints (Summary)

**Auth**: `/api/auth/register`, `/api/auth/login`  
**Skills**: `/api/skills/`, `/api/match-skills/` (NEW!)  
**Learning**: `/api/learning/join/`, `/api/learning/end/`, `/api/learning/sessions/`  
**Verification**: `/api/quiz/submit-learner-quiz/` (NEW!), `/api/quiz/submit-quiz/`  
**Points**: `/api/learning/points/`  
**Ratings**: `/api/learning/rate/`  
**Messages**: `/api/messages/`  
**Notifications**: `/api/notifications/`  

---

## Complete Technology Stack & Usage Matrix

### Backend Technologies

| Technology | Version | Purpose | Files/Features | Problem Solved |
|-----------|---------|---------|-----------------|-----------------|
| **Django** | 5.2.6 | Web framework | `backend/manage.py`, `backend/settings.py`, All views | Rapid API development, ORM, built-in admin |
| **Django REST Framework** | 3.16.1 | API serialization | All endpoints in `api/views.py` | Automatic JSON serialization, validation |
| **SQLite** | Built-in | Database (dev) | `db.sqlite3` | Development database, quick setup |
| **PostgreSQL** | Via psycopg2 | Database (production) | Production deployment | Scalable, robust database for production |
| **sentence-transformers** | 5.1.0 | BERT embeddings | `api/utils_safe.py` → `calculate_match_score()` | Semantic skill matching, synonym handling |
| **torch** | 2.3.1 | Deep learning | Required by transformers | BERT model inference, GPU acceleration |
| **transformers** | 4.56.1 | Hugging Face models | `api/utils_safe.py` | Pre-trained language models access |
| **scikit-learn** | 1.7.2 | ML algorithms | `api/utils_safe.py` → `cosine_similarity()` | Cosine similarity calculation for matching |
| **PyPDF2** | 3.0.1 | PDF parsing | `api/resume_views.py` → `ResumeUploadView` | Resume text extraction for skill detection |
| **Pillow** | 11.3.0 | Image processing | `api/views.py` → Profile picture upload | Profile picture handling, resizing |
| **Ably** | 2.1.1 | Real-time messaging | `api/message_views.py`, `api/ably_utils.py` | Instant message delivery, WebSocket |
| **nltk** | 3.9.1 | NLP utilities | `api/initialize_nltk.py` | Text processing, tokenization |
| **requests** | 2.32.5 | HTTP client | `api/quiz_generator.py` | Ollama API calls for quiz generation |
| **python-multipart** | 0.0.20 | Form parsing | File uploads | Multipart form data handling |
| **dj-database-url** | 2.3.0 | Database config | `settings.py` | Environment-based DB connection |
| **django-cors-headers** | 4.9.0 | CORS handling | `settings.py` | Frontend ↔ Backend communication |
| **gunicorn** | 23.0.0 | WSGI server | Production deployment | Production HTTP server |
| **whitenoise** | 6.9.0 | Static files | `settings.py` | Efficient static file serving |
| **huggingface-hub** | 0.35.0 | Model downloading | `api/utils_safe.py` | Download/cache BERT models |
| **numpy** | 2.3.3 | Numerical computing | Used by transformers/sklearn | Vector operations |
| **scipy** | 1.16.2 | Scientific computing | Used by sklearn | Mathematical operations |
| **PyYAML** | 6.0.2 | YAML parsing | Configuration files | Config file handling |
| **tzdata** | 2025.2 | Timezone data | Django ORM | Timezone-aware datetime handling |

### Frontend Technologies

| Technology | Version | Purpose | Files/Features | Problem Solved |
|-----------|---------|---------|-----------------|-----------------|
| **React** | 19.1.1 | UI framework | `frontend/src/` entire app | Component-based UI, reusable widgets |
| **React Router DOM** | 7.9.1 | Client routing | `frontend/src/App.js`, page components | Multi-page SPA without server routing |
| **Axios** | 1.12.2 | HTTP client | `frontend/src/services/api.js` | API calls, request/response handling |
| **Ably SDK** | 2.14.0 | Real-time client | `frontend/src/contexts/RealtimeContext.js` | Real-time messaging, pub/sub |
| **react-scripts** | 5.0.1 | Build tooling | `npm start`, `npm build` | Webpack bundling, dev server, optimization |
| **CSS3** | Native | Styling | `frontend/src/pages/*.css` | Responsive design, animations |
| **Testing Library** | 16.3.0+ | Testing | Optional unit tests | Component testing |
| **gh-pages** | 6.3.0 | GitHub Pages deploy | `npm run deploy` | Static hosting deployment |

### DevOps & Production

| Technology | Version | Purpose | Usage | Problem Solved |
|-----------|---------|---------|-------|-----------------|
| **Docker** | — | Containerization | Production container | Environment consistency |
| **Nginx** | — | Reverse proxy | Production reverse proxy | Load balancing, static serving |
| **Python** | 3.13.5 | Runtime | `python manage.py` commands | Code execution environment |
| **Node.js** | 14+ | Runtime | `npm` commands | Frontend build/run environment |
| **Git** | — | Version control | Repository tracking | Code history, collaboration |

### AI/ML Infrastructure

| Component | Technology | Model | Usage | Input/Output |
|-----------|-----------|-------|-------|--------------|
| **Skill Matching** | sentence-transformers | paraphrase-MiniLM-L6-v2 | `api/utils_safe.py` → `calculate_match_score()` | Input: skill strings; Output: 0-1 similarity |
| **Embeddings** | BERT/Transformers | MiniLM-L6-v2 | Stored in `Skill.embedding` (JSON, 384 dims) | 384-dimensional vectors |
| **Cosine Similarity** | scikit-learn | cosine_similarity() | `api/utils_safe.py` → matching algorithm | Input: 2 embeddings; Output: similarity score |
| **Quiz Generation** | Ollama (optional) | Mistral 7B | `api/quiz_generator.py` | Input: skill name; Output: 10 MCQ questions |

---

## Where Technologies Are Used - Quick Reference

### User Authentication Flow
```
User Input → React Form → Axios POST
           ↓
       Django auth_views.py → Token generation
           ↓
       DRF serializer → Validation
           ↓
       Token stored in React Context
```

### Skill Matching & Discovery
```
Search Input → React Explore page
           ↓
       Axios GET /api/match_skills/
           ↓
       Django SkillMatchView
           ↓
       utils_safe.py:
       - Load BERT model (sentence-transformers)
       - Encode search query
       - Load user skill embeddings
       - Calculate cosine_similarity (scikit-learn)
       - Rank by score
           ↓
       DRF Serializer → JSON response
           ↓
       React displays with verified badges
```

### Real-Time Messaging
```
User types message → React Messages page
           ↓
       Axios POST /api/messages/
       + Ably publish to channel
           ↓
       Django message_views.py → Save to DB
       DRF Serializer → Persist
           ↓
       Ably broadcasts to recipient
       (WebSocket via ably SDK)
           ↓
       Recipient React listens
       RealtimeContext.js handles incoming
           ↓
       Message displayed instantly
```

### Quiz & Verification System
```
Teacher/Learner initiates quiz
           ↓
   Django quiz_views.py:
   - Call Ollama API (requests library)
   - Ollama generates 10 MCQ questions
   - Cache result in SkillQuiz model
           ↓
   React displays quiz (frontend/src/components/LearnerQuiz/)
           ↓
   User submits answers
           ↓
   Django grades automatically
           ↓
   If score >= 70%:
   - Create Verification record
   - Call _sync_verified_skill_to_profile()
   - Add to Skill table
           ↓
   React shows "✓ Verified" badge
```

### Resume Processing
```
User uploads PDF
           ↓
   Django resume_views.py
   ↓
   PyPDF2 extracts text
   ↓
   NLTK tokenizes & processes
   ↓
   Match against skills database
   ↓
   Bulk create Skill records
   ↓
   React notifies user
```

---

## Presentation Speaking Points

### Opening (30 seconds)

> "SkillXchange is a peer-to-peer learning platform that asks a simple question: Why pay expensive tutors when your peers can teach you? We built a complete ecosystem where users can learn from others, teach what they know, and earn rewards. And crucially, we verify skills through AI quizzes so you know you're learning from qualified people."

### Problem Statement (30 seconds)

> "Learning is expensive. Courses cost money. Tutors charge fees. Even self-directed learning requires books and courses. Plus, there's no trust—you don't know if a teacher actually knows what they're teaching. Our solution: a free peer-exchange platform with AI verification."

### Core Innovation (60 seconds)

> "We use BERT embeddings for intelligent skill matching. When you search 'Python,' we don't just look for exact matches. We understand semantic similarity—'Python Programming' and 'Python Dev' are basically the same skill. We also verify skills through AI-generated quizzes. Teachers who score 70% or higher get a verified badge. Learners who complete sessions can take the same quiz and if they pass, the skill automatically appears on their profile and they become discoverable in search. This creates a trust-based system where credentials matter."

### Technical Excellence (30 seconds)

> "Our backend uses Django with a robust REST API. Frontend is React with real-time messaging via Ably. We use BERT transformers for semantic matching and SQLite for persistence. Everything is production-ready with proper authentication, authorization, and data validation."

### Gamification (30 seconds)

> "We gamified the entire experience. Users earn points for teaching (150 points) and spend points for learning (100 points). They unlock badges at milestones—3 skills, 5 skills, 10 skills. Daily login streaks encourage consistent engagement. Ratings and leaderboards create friendly competition."

### Key Metrics to Mention

- ✅ 15 complete features implemented
- ✅ AI-powered skill matching with 0.4 confidence threshold
- ✅ 70% verification threshold (teacher + learner quizzes)
- ✅ Configurable point economy
- ✅ 6 badge types (learner/teacher × bronze/silver/gold)
- ✅ Real-time messaging with Ably
- ✅ Verified skills auto-sync to profiles (NEW!)
- ✅ Discover ranking prioritizes verified matches (NEW!)

### Closing (30 seconds)

> "SkillXchange democratizes learning. It removes cost barriers, builds trust through verification, and gamifies the entire experience. Whether you're a student learning new skills or a professional sharing expertise, this platform values your time and knowledge. We're ready to scale this to thousands of users."

---

## Feature Checklist for Presentation

### Must-Show Features
- [ ] Registration and profile creation
- [ ] Skill search with verified badge (⭐)
- [ ] Learning request workflow
- [ ] Quiz taking and verification
- [ ] Verified skill auto-sync to profile (NEW!)
- [ ] Discover ranking by verified matches (NEW!)
- [ ] Points transaction
- [ ] Session completion and rating
- [ ] Badges earned

### Must-Mention Features (if time permits)
- Real-time messaging
- Resume upload & parsing
- Leaderboard
- Notification system
- Badge animations
- Points transaction history

---

## Quick Reference: New Features Summary

| Feature | Status | Impact | Demo-Friendly |
|---------|--------|--------|----------------|
| Learner Verification Quiz | ✅ Complete | Learners can prove learned skills | Yes |
| Verified Skills Auto-Sync | ✅ Complete | Profile always matches verification | Yes |
| Discover Ranking by Verified | ✅ Complete | Verified users appear first (⭐) | Yes |
| Backfilled Existing Verified | ✅ Complete | Existing users immediately benefited | No |

---

## Appendix: Technical Deep Dive

### BERT Embedding Details
- **Model**: paraphrase-MiniLM-L6-v2
- **Dimensions**: 384
- **Similarity Metric**: Cosine similarity
- **Threshold**: 0.4 (40% similarity minimum)
- **Performance**: ~100ms per search

### Quiz Generation
- **AI Framework**: Ollama (local, free)
- **Model**: Mistral 7B
- **Questions**: 10 per quiz
- **Caching**: Results cached after first generation
- **Grading**: Automated, configurable threshold (70%)

### Points Economy
- **Initial Balance**: 1000 points
- **Join Cost**: 100 points
- **Learner Reward**: 50 points
- **Teacher Reward**: 150 points
- **Configurable**: All values via admin panel

---

**End of Presentation README**

*Use this document to guide your presentation. Practice with a timer—aim for 15-20 minutes including demo.*
