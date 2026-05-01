# SkillXchange - New Features Theory (Report Draft)

## Purpose
This document explains only the newly implemented features in SkillXchange, focusing on theory, design intent, and system behavior for project-report use.

---

## 1) Teacher Skill Verification System

### Concept
The platform now includes a trust layer where teachers can prove competency in specific skills before learners choose them. Instead of relying only on self-declared skills, the system introduces objective verification through skill-specific quizzes.

### Why this matters
- Reduces information asymmetry between learners and teachers.
- Improves confidence in peer-learning quality.
- Creates measurable credibility signals in teacher profiles.

### Theoretical model
A teacher attempts a quiz for a selected skill. The system evaluates performance and stores a verification status.

Verification decision rule:

$$
\text{verified} =
\begin{cases}
1 & \text{if score} \ge 70\\
0 & \text{if score} < 70
\end{cases}
$$

### Data model introduced
- `SkillQuiz`: question bank per skill.
- `TeacherQuizAttempt`: stores each attempt for auditability and learning feedback.
- `TeacherVerification`: stores best/current verification state for a teacher-skill pair.

This separation supports both historical tracking (attempts) and current trust state (verification).

---

## 2) AI-Based Quiz Generation (Local LLM via Ollama)

### Concept
Quiz content is generated dynamically by a local LLM service (Ollama) rather than hardcoding all questions. This enables scalable assessment across many skills.

### Design rationale
- Expands coverage to long-tail skills.
- Avoids external API costs for quiz generation.
- Keeps generation under local/controlled runtime.

### Theoretical behavior
For a requested skill, the system:
1. Checks if quiz questions already exist.
2. If not, requests AI generation of MCQs.
3. Validates format consistency (question, options, answer index).
4. Persists validated questions for reuse.

This follows a generate-then-cache pattern, balancing flexibility and performance.

---

## 3) Public Verification Badges

### Concept
Verified skills are surfaced as profile badges so trust signals are visible during discovery and profile browsing.

### Why this matters
- Converts backend assessment into user-facing credibility indicators.
- Helps learners make better decisions quickly.
- Encourages teachers to maintain demonstrable competency.

### Theory in product terms
The badge acts as a lightweight reputation primitive: a binary credibility marker with score metadata. It supplements social proof with assessment-based proof.

---

## 4) Leaderboard and Engagement Scoring

### Concept
A new leaderboard ranks users using a blended metric of consistency (days active) and outcome (skills earned through completed learning sessions).

### Scoring formula
$$
\text{score} = (\text{days\_logged\_in} \times 2) + (\text{skills\_earned} \times 10)
$$

### Interpretation
- Activity contributes to steady progress.
- Skill completion receives stronger weight, emphasizing meaningful learning outcomes over passive app usage.

### Product effect
This introduces gamification with an educational bias: participation is rewarded, but mastery/progress is rewarded more.

---

## 5) Session-Aware Authentication Lifecycle

### Concept
Authentication now includes stronger session lifecycle handling through explicit logout behavior and activity-session tracking.

### New capabilities
- Logout endpoint with token invalidation.
- Account deletion endpoint for user control/privacy.
- Activity-session tracking (`login_time`, `logout_time`, `duration_seconds`) for behavioral analytics.

### Theoretical significance
The system moves from simple stateless token usage toward accountable session boundaries. This improves:
- Security hygiene (token invalidation on logout).
- Observability (time-spent and engagement analysis).
- Data governance (user-initiated account removal).

---

## 6) Improved Resume Skill Extraction Quality

### Concept
Skill extraction was strengthened to reduce false positives from resume noise and improve normalized skill mapping.

### New theory components
- Skill normalization before matching/storage (canonical forms).
- Validity filtering to reject non-skill artifacts (dates, links, generic words, noisy tokens).
- Dynamic vocabulary merging curated skills with database-known skills.
- Conservative fallback logic for robust extraction when embeddings are unavailable.

### Expected impact
- Better precision in extracted skills.
- Cleaner profile skill lists.
- Better downstream matching quality due to improved input integrity.

---

## 7) Production-Readiness and Deployment Architecture

### Concept
The project now includes deployment-grade configuration for cloud hosting and production serving.

### Additions
- `render.yaml` for service orchestration (backend, frontend, managed database).
- `build.sh` for reproducible backend build/migrate/static workflow.
- Production dependencies (`gunicorn`, `whitenoise`, `dj-database-url`, `psycopg2-binary`).

### Architectural meaning
The system transitions from development-only setup to platform-ready architecture with clearer separation of:
- runtime server responsibilities,
- static asset delivery,
- and managed database connectivity.

---

## 8) New UX Surfaces for the Added Features

### Newly exposed user interfaces
- Quiz page for teacher verification workflow.
- Leaderboard page for ranked engagement view.
- Verification badges component integrated into profile views.
- Debug surface for skill-match diagnostics during testing.

### Theory perspective
These interfaces operationalize backend capabilities into measurable user journeys: verify, compare, trust, and improve.

---

## Report-Ready Summary
The new implementation wave adds a trust-and-quality layer to SkillXchange through verified teaching credentials, introduces outcome-weighted gamification, strengthens extraction accuracy, and improves production readiness. Together, these updates shift the platform from a matching-and-chat prototype toward a more reliable learning marketplace model.
