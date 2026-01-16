# Learning Request/Approval System - Implementation Summary

## Overview
Implemented a comprehensive request/approval workflow for the learning system. Now when a learner wants to start learning from a teacher, they must send a request and wait for the teacher's approval.

---

## Backend Changes

### 1. Database Schema Updates
**File:** `backend/api/models.py`
- Updated `LearningSession` model:
  - Added two new status choices: `'pending'` and `'rejected'`
  - Changed default status from `'in_progress'` to `'pending'`
  - Status choices now: `pending`, `in_progress`, `completed`, `cancelled`, `rejected`

**Migration:** `api/migrations/0009_alter_learningsession_status.py`

### 2. Updated API Endpoints
**File:** `backend/api/learning_views.py`

#### Modified: `join_learning()`
- **Old behavior:** Immediately deducted points and created an active session
- **New behavior:** 
  - Creates a session with `status='pending'`
  - Does NOT deduct points yet
  - Sets `points_deducted=0` (will be set when accepted)
  - Sends notification to teacher about the request
  - Validates learner has sufficient points before allowing request

#### New: `accept_learning_request(session_id)`
- **Endpoint:** `POST /api/learning/requests/<id>/accept/`
- **Purpose:** Teacher accepts a pending learning request
- **Actions:**
  1. Validates request exists and is pending
  2. Checks learner still has enough points
  3. Deducts points from learner's balance
  4. Creates point transaction record
  5. Updates session status to `'in_progress'`
  6. Sets `points_deducted` field
  7. Sends notification to learner about acceptance

#### New: `reject_learning_request(session_id)`
- **Endpoint:** `POST /api/learning/requests/<id>/reject/`
- **Purpose:** Teacher rejects a pending learning request
- **Actions:**
  1. Validates request exists and is pending
  2. Updates session status to `'rejected'`
  3. Sends notification to learner about rejection
  4. No points are deducted

#### New: `get_learning_requests()`
- **Endpoint:** `GET /api/learning/requests/`
- **Purpose:** Get all pending requests for current user (as teacher)
- **Returns:** List of pending learning sessions ordered by creation date

### 3. URL Configuration
**File:** `backend/api/urls.py`
Added three new routes:
```python
path('learning/requests/', get_learning_requests, name='get_learning_requests'),
path('learning/requests/<int:session_id>/accept/', accept_learning_request, name='accept_learning_request'),
path('learning/requests/<int:session_id>/reject/', reject_learning_request, name='reject_learning_request'),
```

---

## Frontend Changes

### 1. New Component: LearningRequests
**Files:**
- `frontend/src/components/LearningRequests/LearningRequests.js`
- `frontend/src/components/LearningRequests/LearningRequests.css`

**Features:**
- Displays all pending learning requests for the current user (as teacher)
- Shows learner information, skill name, duration, and points
- Accept/Reject buttons with loading states
- Click on learner name/avatar to view their profile
- Empty state when no requests
- Responsive grid layout

**UI Elements:**
- Request cards with learner avatar
- Skill badge
- Request date/time
- Duration and points information
- Accept button (green gradient)
- Reject button (red gradient)
- Loading spinners during actions

### 2. Updated Component: JoinLearning
**File:** `frontend/src/components/JoinLearning/JoinLearning.js`

**Changes:**
- Updated button text: "Send Learning Request" (was "Join Learning")
- Changed loading text: "Sending Request..." (was "Joining...")
- Updated info note to explain approval workflow
- Shows success alert when request is sent
- Handles pending status response

### 3. Updated Component: LearningSession
**File:** `frontend/src/components/LearningSession/LearningSession.js`
- Added support for `'pending'` and `'rejected'` status
- Status badge displays:
  - "Pending Approval" for pending sessions
  - "Rejected" for rejected sessions

**CSS File:** `frontend/src/components/LearningSession/LearningSession.css`
- Added `.status-badge.pending` style (blue)
- Added `.status-badge.rejected` style (red)

### 4. Navigation Updates
**File:** `frontend/src/components/Navigation/Navbar.js`

**New Features:**
- Added learning requests counter badge
- Shows number of pending requests next to 📚 icon
- Polls every 30 seconds for new requests
- Purple gradient badge (different from notification badge)
- Links to `/learning-requests` page

**CSS File:** `frontend/src/components/Navigation/Navbar.css`
- Added `.requests-badge` style for purple gradient

### 5. Routing
**File:** `frontend/src/App.js`
- Imported `LearningRequests` component
- Added route: `/learning-requests` → Protected route to LearningRequests component

---

## User Flow

### For Learners:
1. Browse users with skills they want to learn
2. Click "Send Learning Request" on a user's profile
3. System checks if they have enough points (but doesn't deduct yet)
4. Request is sent to the teacher
5. Learner sees "Pending Approval" status in their learning sessions
6. When teacher accepts:
   - Learner receives notification
   - Points are deducted
   - Session status changes to "In Progress"
7. When teacher rejects:
   - Learner receives notification
   - No points deducted
   - Session status changes to "Rejected"

### For Teachers:
1. Receive notification when learner sends request
2. See badge count on 📚 icon in navbar
3. Click 📚 to view all pending requests
4. See learner info, skill, duration, and points
5. Click "Accept" to:
   - Start the learning session
   - Deduct points from learner
   - Send acceptance notification
6. Click "Reject" to:
   - Decline the request
   - No points deducted
   - Send rejection notification

---

## Point System Changes

### Before:
- Points deducted immediately when "Join Learning" clicked
- Session created in "in_progress" status

### After:
- Points held (validated but not deducted) when request sent
- Session created in "pending" status
- Points only deducted when teacher accepts
- If rejected, learner keeps all points

---

## Notification System

### New Notifications:
1. **Request Sent:** Teacher receives notification when learner sends request
2. **Request Accepted:** Learner receives notification when teacher accepts
3. **Request Rejected:** Learner receives notification when teacher rejects

### Notification Links:
- Request notification → `/learning-requests`
- Acceptance/rejection → `/learning`

---

## API Endpoints Summary

### Existing (Modified):
- `POST /api/learning/join/` - Now creates pending requests

### New:
- `GET /api/learning/requests/` - Get pending requests for teacher
- `POST /api/learning/requests/<id>/accept/` - Accept a request
- `POST /api/learning/requests/<id>/reject/` - Reject a request

---

## Database Migration

### Migration File:
`backend/api/migrations/0009_alter_learningsession_status.py`

### Changes:
- Added 'pending' and 'rejected' to STATUS_CHOICES
- Changed default from 'in_progress' to 'pending'

**Applied:** ✅ Migration successfully applied to database

---

## Testing Checklist

### Backend:
- ✅ Migration created and applied
- ✅ Django server starts without errors
- ✅ All endpoints accessible

### Frontend:
- ✅ LearningRequests component created
- ✅ Route added to App.js
- ✅ Navbar shows requests badge
- ✅ JoinLearning updated with new messaging
- ✅ LearningSession handles pending/rejected statuses

### Integration:
- 🔄 Ready for user testing

---

## Files Created/Modified

### Created (2 files):
1. `frontend/src/components/LearningRequests/LearningRequests.js`
2. `frontend/src/components/LearningRequests/LearningRequests.css`

### Modified (9 files):
1. `backend/api/models.py` - Added pending/rejected statuses
2. `backend/api/learning_views.py` - Modified join_learning, added accept/reject/get_requests
3. `backend/api/urls.py` - Added 3 new routes
4. `frontend/src/App.js` - Added LearningRequests import and route
5. `frontend/src/components/Navigation/Navbar.js` - Added requests badge and counter
6. `frontend/src/components/Navigation/Navbar.css` - Added requests-badge style
7. `frontend/src/components/JoinLearning/JoinLearning.js` - Updated messaging
8. `frontend/src/components/LearningSession/LearningSession.js` - Added pending/rejected support
9. `frontend/src/components/LearningSession/LearningSession.css` - Added new status styles

---

## Next Steps (Optional Enhancements)

1. **Real-time Updates:** Use WebSocket to instantly update request count
2. **Request Expiration:** Auto-reject requests after X days
3. **Bulk Actions:** Allow teachers to accept/reject multiple requests at once
4. **Request Details:** Add custom message from learner to teacher
5. **Request History:** Show rejected requests with ability to re-request
6. **Email Notifications:** Send emails for important request events
7. **Request Analytics:** Track acceptance/rejection rates

---

## Configuration

### Point Costs:
- Join Learning Cost: 100 points (configurable via `PointConfiguration` model)
- Learner Completion Reward: 50 points
- Teacher Completion Reward: 150 points

### Polling Intervals:
- Navbar requests count: Every 30 seconds
- Navbar notifications count: Every 30 seconds

---

## Status

✅ **Implementation Complete**
- All backend changes implemented and tested
- All frontend components created
- Migration applied successfully
- Django server running without errors
- Ready for end-to-end testing
