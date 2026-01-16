# Learning Flow System - API Documentation

## Base URL
```
Development: http://localhost:8000/api
Production: https://your-domain.com/api
```

## Authentication
All endpoints require authentication using Token Authentication.

**Header:**
```
Authorization: Token <your-token-here>
```

---

## 📚 Learning Session Endpoints

### 1. Join Learning Session

**Endpoint:** `POST /learning/join/`

**Description:** Start a new learning session with another user

**Request Body:**
```json
{
  "teacher_id": 2,
  "skill_name": "Python Programming",
  "total_days": 30  // optional, defaults to configuration value
}
```

**Success Response (201):**
```json
{
  "message": "Successfully joined learning session",
  "learning_session": {
    "id": 1,
    "learner": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com"
    },
    "teacher": {
      "id": 2,
      "username": "jane_smith",
      "email": "jane@example.com"
    },
    "skill_name": "Python Programming",
    "status": "in_progress",
    "total_days": 30,
    "start_date": "2026-01-15T10:30:00Z",
    "end_date": null,
    "points_deducted": 100,
    "points_awarded_learner": null,
    "points_awarded_teacher": null,
    "progress_percentage": 0,
    "days_remaining": 30,
    "created_at": "2026-01-15T10:30:00Z",
    "updated_at": "2026-01-15T10:30:00Z"
  },
  "points_deducted": 100,
  "new_balance": 900
}
```

**Error Responses:**

400 Bad Request - Missing required fields:
```json
{
  "error": "teacher_id and skill_name are required"
}
```

400 Bad Request - Self-learning attempt:
```json
{
  "error": "You cannot start a learning session with yourself"
}
```

400 Bad Request - Insufficient points:
```json
{
  "error": "Insufficient points",
  "current_balance": 50,
  "required": 100
}
```

404 Not Found - Teacher not found:
```json
{
  "error": "Teacher not found"
}
```

---

### 2. End Learning Session

**Endpoint:** `POST /learning/end/{session_id}/`

**Description:** Complete a learning session and award points

**URL Parameters:**
- `session_id` (integer) - ID of the learning session

**Request Body:** None required

**Success Response (200):**
```json
{
  "message": "Learning session completed successfully",
  "learning_session": {
    "id": 1,
    "learner": {...},
    "teacher": {...},
    "skill_name": "Python Programming",
    "status": "completed",
    "total_days": 30,
    "start_date": "2026-01-15T10:30:00Z",
    "end_date": "2026-02-14T15:45:00Z",
    "points_deducted": 100,
    "points_awarded_learner": 50,
    "points_awarded_teacher": 150,
    "progress_percentage": 100,
    "days_remaining": 0,
    "created_at": "2026-01-15T10:30:00Z",
    "updated_at": "2026-02-14T15:45:00Z"
  },
  "learner_reward": 50,
  "teacher_reward": 150
}
```

**Error Responses:**

404 Not Found:
```json
{
  "error": "Learning session not found"
}
```

403 Forbidden:
```json
{
  "error": "You are not part of this learning session"
}
```

400 Bad Request:
```json
{
  "error": "Learning session already completed"
}
```

---

### 3. Get Learning Sessions

**Endpoint:** `GET /learning/sessions/`

**Description:** Retrieve all learning sessions for the authenticated user

**Query Parameters:**
- `role` (optional): `learner` | `teacher` | `all` (default: `all`)
- `status` (optional): `in_progress` | `completed` | `cancelled` | `all` (default: `all`)

**Example Request:**
```
GET /api/learning/sessions/?role=learner&status=in_progress
```

**Success Response (200):**
```json
[
  {
    "id": 1,
    "learner": {...},
    "teacher": {...},
    "skill_name": "Python Programming",
    "status": "in_progress",
    "total_days": 30,
    "start_date": "2026-01-15T10:30:00Z",
    "end_date": null,
    "points_deducted": 100,
    "points_awarded_learner": null,
    "points_awarded_teacher": null,
    "progress_percentage": 10,
    "days_remaining": 27,
    "created_at": "2026-01-15T10:30:00Z",
    "updated_at": "2026-01-15T10:30:00Z"
  },
  // ... more sessions
]
```

---

### 4. Get Learning Session Detail

**Endpoint:** `GET /learning/sessions/{session_id}/`

**Description:** Get detailed information about a specific learning session

**URL Parameters:**
- `session_id` (integer) - ID of the learning session

**Success Response (200):**
```json
{
  "id": 1,
  "learner": {...},
  "teacher": {...},
  "skill_name": "Python Programming",
  // ... full session details
}
```

**Error Response:**

404 Not Found:
```json
{
  "error": "Learning session not found"
}
```

---

## 💰 Points Endpoints

### 5. Get User Points

**Endpoint:** `GET /learning/points/`

**Description:** Get current user's point balance and recent transactions

**Success Response (200):**
```json
{
  "balance": 950,
  "total_earned": 200,
  "total_spent": 250,
  "recent_transactions": [
    {
      "id": 5,
      "user": 1,
      "username": "john_doe",
      "transaction_type": "join_learning",
      "amount": -100,
      "balance_after": 900,
      "description": "Joined learning session for Python Programming with jane_smith",
      "created_at": "2026-01-15T10:30:00Z"
    },
    {
      "id": 4,
      "user": 1,
      "username": "john_doe",
      "transaction_type": "complete_learning_learner",
      "amount": 50,
      "balance_after": 1000,
      "description": "Completed learning React Development with bob_jones",
      "created_at": "2026-01-14T14:20:00Z"
    }
    // ... up to 20 recent transactions
  ]
}
```

---

## 🎓 Skills Learned/Taught Endpoints

### 6. Get Skills Learned

**Endpoint:** `GET /learning/skills-learned/` or `GET /learning/skills-learned/{username}/`

**Description:** Get all completed skills learned by a user

**URL Parameters:**
- `username` (optional) - Username of the user. If omitted, returns data for authenticated user.

**Success Response (200):**
```json
[
  {
    "id": 1,
    "learner": {...},
    "teacher": {
      "id": 2,
      "username": "jane_smith",
      "email": "jane@example.com"
    },
    "skill_name": "Python Programming",
    "status": "completed",
    "total_days": 30,
    "start_date": "2026-01-15T10:30:00Z",
    "end_date": "2026-02-14T15:45:00Z",
    // ... full session details
  }
  // ... more completed learning sessions
]
```

---

### 7. Get Skills Taught

**Endpoint:** `GET /learning/skills-taught/` or `GET /learning/skills-taught/{username}/`

**Description:** Get all completed skills taught by a user

**URL Parameters:**
- `username` (optional) - Username of the user. If omitted, returns data for authenticated user.

**Success Response (200):**
```json
[
  {
    "id": 2,
    "learner": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com"
    },
    "teacher": {...},
    "skill_name": "React Development",
    "status": "completed",
    // ... full session details
  }
  // ... more teaching sessions
]
```

---

## ⭐ Rating Endpoints

### 8. Submit Rating

**Endpoint:** `POST /learning/rate/{session_id}/`

**Description:** Submit a rating and feedback for a completed learning session

**URL Parameters:**
- `session_id` (integer) - ID of the learning session

**Request Body:**
```json
{
  "rating": 5,  // integer 1-5
  "feedback": "Great teacher! Very patient and knowledgeable."  // optional
}
```

**Success Response (201):**
```json
{
  "message": "Rating submitted successfully",
  "rating": {
    "id": 1,
    "learning_session": {...},
    "rater": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com"
    },
    "rated_user": {
      "id": 2,
      "username": "jane_smith",
      "email": "jane@example.com"
    },
    "rating": 5,
    "feedback": "Great teacher! Very patient and knowledgeable.",
    "skill_name": "Python Programming",
    "created_at": "2026-02-14T16:00:00Z"
  }
}
```

**Error Responses:**

400 Bad Request - Invalid rating:
```json
{
  "error": "Rating must be between 1 and 5"
}
```

400 Bad Request - Session not completed:
```json
{
  "error": "Can only rate completed learning sessions"
}
```

400 Bad Request - Already rated:
```json
{
  "error": "You have already rated this learning session"
}
```

403 Forbidden:
```json
{
  "error": "You are not part of this learning session"
}
```

---

### 9. Get Session Ratings

**Endpoint:** `GET /learning/ratings/{session_id}/`

**Description:** Get all ratings for a specific learning session

**URL Parameters:**
- `session_id` (integer) - ID of the learning session

**Success Response (200):**
```json
{
  "ratings": [
    {
      "id": 1,
      "learning_session": {...},
      "rater": {...},
      "rated_user": {...},
      "rating": 5,
      "feedback": "Great teacher!",
      "skill_name": "Python Programming",
      "created_at": "2026-02-14T16:00:00Z"
    },
    {
      "id": 2,
      "learning_session": {...},
      "rater": {...},
      "rated_user": {...},
      "rating": 4,
      "feedback": "Very helpful learner!",
      "skill_name": "Python Programming",
      "created_at": "2026-02-14T16:15:00Z"
    }
  ],
  "can_rate": false,
  "session_status": "completed"
}
```

---

### 10. Get User Ratings

**Endpoint:** `GET /learning/ratings/user/` or `GET /learning/ratings/user/{username}/`

**Description:** Get all ratings received by a user

**Query Parameters:**
- `as_learner` (optional): `true` | `false` - Filter ratings received as learner
- `as_teacher` (optional): `true` | `false` - Filter ratings received as teacher

**Example Request:**
```
GET /api/learning/ratings/user/jane_smith/?as_teacher=true
```

**Success Response (200):**
```json
{
  "ratings": [
    {
      "id": 1,
      "learning_session": {...},
      "rater": {...},
      "rated_user": {...},
      "rating": 5,
      "feedback": "Excellent teacher!",
      "skill_name": "Python Programming",
      "created_at": "2026-02-14T16:00:00Z"
    }
    // ... more ratings
  ],
  "average_rating": 4.75,
  "total_ratings": 8
}
```

---

### 11. Check Can Rate

**Endpoint:** `GET /learning/can-rate/{session_id}/`

**Description:** Check if the authenticated user can rate a learning session

**URL Parameters:**
- `session_id` (integer) - ID of the learning session

**Success Response (200):**
```json
{
  "can_rate": true,
  "session_status": "completed",
  "has_rated": false,
  "reason": "Can rate"
}
```

or

```json
{
  "can_rate": false,
  "session_status": "in_progress",
  "has_rated": false,
  "reason": "Session not completed"
}
```

---

## 📊 Data Models

### LearningSession Object
```typescript
{
  id: number,
  learner: User,
  teacher: User,
  skill_name: string,
  status: 'in_progress' | 'completed' | 'cancelled',
  total_days: number,
  start_date: string (ISO 8601),
  end_date: string (ISO 8601) | null,
  points_deducted: number,
  points_awarded_learner: number | null,
  points_awarded_teacher: number | null,
  progress_percentage: number (0-100),
  days_remaining: number,
  created_at: string (ISO 8601),
  updated_at: string (ISO 8601)
}
```

### User Object
```typescript
{
  id: number,
  username: string,
  email: string
}
```

### PointTransaction Object
```typescript
{
  id: number,
  user: number,
  username: string,
  transaction_type: string,
  amount: number,
  balance_after: number,
  description: string,
  created_at: string (ISO 8601)
}
```

### SkillRating Object
```typescript
{
  id: number,
  learning_session: LearningSession,
  rater: User,
  rated_user: User,
  rating: number (1-5),
  feedback: string,
  skill_name: string,
  created_at: string (ISO 8601)
}
```

---

## 🔧 Configuration

Point values and defaults are configurable via the PointConfiguration model:

- `join_learning_cost`: 100 (default)
- `learning_completion_reward_learner`: 50 (default)
- `learning_completion_reward_teacher`: 150 (default)
- `default_learning_period_days`: 30 (default)

These can be modified via Django Admin panel or directly in the database.

---

## 🚨 Error Codes

- `200` - Success (GET, POST for updates)
- `201` - Created (POST for new resources)
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (missing or invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `500` - Server Error (unexpected error)

---

## 📝 Notes

1. All timestamps are in UTC and ISO 8601 format
2. Progress percentage is calculated server-side based on elapsed time
3. Points are transactional - either all operations succeed or none
4. Ratings are limited to one per user per session
5. Both learner and teacher can complete a session
6. Sessions can only be rated after completion

---

## 🧪 Testing with curl

### Join Learning
```bash
curl -X POST http://localhost:8000/api/learning/join/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "teacher_id": 2,
    "skill_name": "Python Programming",
    "total_days": 30
  }'
```

### Get Points
```bash
curl -X GET http://localhost:8000/api/learning/points/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Submit Rating
```bash
curl -X POST http://localhost:8000/api/learning/rate/1/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 5,
    "feedback": "Excellent teacher!"
  }'
```

---

**Last Updated:** January 2026  
**API Version:** 1.0
