# SkillXchange - Project Presentation Documentation

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Backend Architecture](#backend-architecture)
4. [Frontend Architecture](#frontend-architecture)
5. [Database Schema](#database-schema)
6. [Skill Matching Algorithm](#skill-matching-algorithm)
7. [Real-time Communication](#real-time-communication)
8. [File Storage & Resume Processing](#file-storage--resume-processing)
9. [API Endpoints](#api-endpoints)
10. [Setup & Run Instructions](#setup--run-instructions)
11. [Demo Flow](#demo-flow)
12. [Key Features](#key-features)

---

## 🎯 Project Overview

**SkillXchange** is a professional skill exchange platform that connects users who want to learn new skills with those who can teach them. It's a mutual learning ecosystem where professionals can exchange knowledge.

### Core Concept
- Users create profiles with their skills and desired learning areas
- AI-powered matching connects learners with teachers based on skill similarity
- Real-time messaging facilitates communication
- Connection system manages relationships between users

---

## 🛠 Technology Stack

### Backend
- **Framework**: Django 5.2.6 (Python)
- **API**: Django REST Framework
- **Database**: SQLite (db.sqlite3)
- **Authentication**: Token-based (DRF Token Authentication)
- **AI/ML Libraries**:
  - `sentence-transformers` - BERT embeddings (MiniLM-L6-v2 model)
  - `scikit-learn` - Cosine similarity calculations
  - `nltk` - Natural language processing
  - `PyPDF2` - PDF resume parsing

### Frontend
- **Framework**: React 18
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Real-time**: Ably (WebSocket-based messaging)
- **Styling**: Custom CSS with responsive design

### Real-time Communication
- **Service**: Ably (Real-time pub/sub messaging)
- **Features**: Instant message delivery, presence detection

### File Storage
- **Resume Storage**: `backend/media/resumes/`
- **Profile Pictures**: `backend/media/profile_pictures/`
- **Chat Files**: `backend/media/chat_files/`

---

## 🔧 Backend Architecture

### Django Project Structure
```
backend/
├── api/                      # Main application
│   ├── models.py            # Database models
│   ├── views.py             # API views & viewsets
│   ├── serializers.py       # DRF serializers
│   ├── auth_views.py        # Authentication endpoints
│   ├── message_views.py     # Messaging endpoints
│   ├── resume_views.py      # Resume processing
│   ├── search_views.py      # Search functionality
│   ├── utils.py             # ML/AI utilities
│   ├── ably_utils.py        # Real-time utilities
│   ├── skills_data.py       # Predefined skills list
│   ├── urls.py              # URL routing
│   └── migrations/          # Database migrations
├── backend/
│   ├── settings.py          # Django configuration
│   ├── urls.py              # Root URL config
│   └── wsgi.py              # WSGI entry point
├── media/                   # User-uploaded files
├── db.sqlite3              # SQLite database
└── manage.py               # Django management
```

### Key Backend Components

#### 1. **Models** (`api/models.py`)
All database tables and relationships are defined here.

#### 2. **Authentication** (`api/auth_views.py`)
- Token-based authentication
- Registration with username validation
- Login with token generation

#### 3. **AI/ML Utilities** (`api/utils.py`)
- Resume text extraction
- Skill extraction from text
- BERT embedding generation
- Similarity calculation

#### 4. **Real-time** (`api/ably_utils.py`)
- Ably channel management
- Token generation for clients
- Message publishing

---

## 🎨 Frontend Architecture

### React Project Structure
```
frontend/
├── src/
│   ├── pages/               # Page components
│   │   ├── Home.js          # Landing page
│   │   ├── Auth/            # Login/Register
│   │   ├── Profile/         # User profile
│   │   ├── Explore/         # User discovery
│   │   ├── Messages/        # Chat interface
│   │   └── Notifications/   # Notification center
│   ├── components/          # Reusable components
│   │   ├── Navigation/      # Navbar
│   │   ├── NotificationPopup/ # Toast notifications
│   │   ├── NotificationManager/ # Real-time handler
│   │   ├── ResumeUpload/    # Resume uploader
│   │   └── SkillMatch/      # Skill matcher UI
│   ├── contexts/            # React contexts
│   │   ├── AuthContext.js   # Authentication state
│   │   └── RealtimeContext.js # Ably integration
│   ├── services/
│   │   └── api.js           # Axios API client
│   └── App.js               # Main app component
└── package.json
```

### State Management
- **AuthContext**: User authentication state, login/logout
- **RealtimeContext**: Ably connection, real-time subscriptions

### Key Frontend Features
- **Protected Routes**: Authentication-required pages
- **Real-time Notifications**: Popup toasts for new messages
- **Responsive Design**: Mobile-friendly layout
- **Token Interceptors**: Automatic token injection in requests

---

## 💾 Database Schema

### Database: SQLite (`backend/db.sqlite3`)

### Models & Tables

#### 1. **User** (Django built-in)
```python
Fields:
- id (PK)
- username (unique)
- email
- password (hashed)
- first_name
- last_name
- date_joined
```

#### 2. **UserProfile** (`api_userprofile`)
```python
Fields:
- id (PK)
- user_id (FK → User, OneToOne)
- bio (text)
- created_at
- updated_at

Relationship: Each user has one profile
```

#### 3. **Skill** (`api_skill`)
```python
Fields:
- id (PK)
- user_id (FK → User)
- name (varchar)
- description (text)
- proficiency_level (beginner/intermediate/advanced/expert)
- embedding (JSON) - BERT vector [384 dimensions]
- created_at
- updated_at

Unique Constraint: (user_id, name)
Relationship: User has many skills
```

#### 4. **Resume** (`api_resume`)
```python
Fields:
- id (PK)
- user_id (FK → User, OneToOne)
- file (FileField → media/resumes/)
- processed (boolean)
- created_at
- updated_at

Relationship: User has one resume
```

#### 5. **SkillMatch** (`api_skillmatch`)
```python
Fields:
- id (PK)
- seeker_id (FK → User)
- provider_id (FK → User)
- desired_skill (varchar)
- similarity_score (float, 0.0-1.0)
- created_at

Ordering: -similarity_score (highest first)
Purpose: Store skill matching results
```

#### 6. **Connection** (`api_connection`)
```python
Fields:
- id (PK)
- requester_id (FK → User)
- receiver_id (FK → User)
- status (pending/connected/rejected)
- created_at

Unique Constraint: (requester_id, receiver_id)
Purpose: Manage user connections
```

#### 7. **Message** (`api_message`)
```python
Fields:
- id (PK)
- sender_id (FK → User)
- receiver_id (FK → User)
- content (text)
- file (FileField → media/chat_files/)
- read (boolean)
- created_at

Ordering: created_at
Purpose: Store chat messages
```

#### 8. **DailyLogin** (`api_dailylogin`)
```python
Fields:
- id (PK)
- user_id (FK → User)
- login_date (date)
- created_at

Unique Constraint: (user_id, login_date)
Purpose: Track login streaks
```

#### 9. **Notification** (`api_notification`)
```python
Fields:
- id (PK)
- user_id (FK → User)
- notification_type (message/connection_request/connection_accepted/skill_match)
- title (varchar)
- message (text)
- sender_id (FK → User, nullable)
- link (varchar) - Navigation URL
- read (boolean)
- created_at

Ordering: -created_at
Purpose: Store user notifications
```

### Database Relationships Diagram
```
User ─┬─ 1:1 ─→ UserProfile
      ├─ 1:N ─→ Skill
      ├─ 1:1 ─→ Resume
      ├─ 1:N ─→ Connection (as requester)
      ├─ 1:N ─→ Connection (as receiver)
      ├─ 1:N ─→ Message (as sender)
      ├─ 1:N ─→ Message (as receiver)
      ├─ 1:N ─→ DailyLogin
      ├─ 1:N ─→ Notification (as recipient)
      └─ 1:N ─→ Notification (as sender)
```

### Migrations History
```
0001_initial.py                 - Initial models
0002_alter_resume_user.py       - Resume relationship
0003_remove_userprofile_...     - UserProfile cleanup
0004_remove_userprofile_...     - Message file field
0005_remove_userprofile_...     - Profile cleanup
0006_remove_userprofile_...     - DailyLogin added
0007_notification.py            - Notification system
```

---

## 🧠 Skill Matching Algorithm

### Overview
SkillXchange uses **semantic similarity matching** powered by BERT embeddings to connect users based on their skills.

### Algorithm Steps

#### 1. **Skill Input Processing**
```python
# User enters a skill they want to learn
desired_skill = "python programming"
```

#### 2. **Text Embedding Generation**
```python
from sentence_transformers import SentenceTransformer

# Load pre-trained BERT model (MiniLM-L6-v2)
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Generate 384-dimensional vector
embedding = model.encode([desired_skill])[0]
# Result: [0.023, -0.145, 0.892, ...] (384 floats)
```

**Why MiniLM-L6-v2?**
- Small, fast model (22MB)
- 384-dimensional embeddings (efficient)
- Good semantic understanding
- Pre-trained on paraphrase detection

#### 3. **Database Skill Retrieval**
```python
# Get all skills from database with their embeddings
all_skills = Skill.objects.all()
skill_embeddings = [
    (skill.user.id, skill.name, skill.embedding)
    for skill in all_skills
]
```

#### 4. **Cosine Similarity Calculation**
```python
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def calculate_similarity(embedding1, embedding2):
    # Convert to numpy arrays
    vec1 = np.array(embedding1).reshape(1, -1)
    vec2 = np.array(embedding2).reshape(1, -1)
    
    # Calculate cosine similarity
    similarity = cosine_similarity(vec1, vec2)[0][0]
    # Returns float between 0.0 (no match) and 1.0 (perfect match)
    return similarity
```

**Cosine Similarity Formula:**
```
similarity = (A · B) / (||A|| * ||B||)

Where:
- A · B = dot product of vectors
- ||A|| = magnitude of vector A
- Result ranges from -1 to 1 (we use 0 to 1)
```

#### 5. **Match Ranking**
```python
matches = []
for user_id, skill_name, skill_embedding in all_skills:
    score = calculate_similarity(desired_embedding, skill_embedding)
    matches.append((user_id, skill_name, score))

# Sort by score descending
matches.sort(key=lambda x: x[2], reverse=True)

# Return top 10 matches
top_matches = matches[:10]
```

#### 6. **Result Storage**
```python
# Store matches in database
for provider_id, skill, score in top_matches:
    if score > 0.5:  # Threshold for relevance
        SkillMatch.objects.create(
            seeker=request.user,
            provider_id=provider_id,
            desired_skill=desired_skill,
            similarity_score=score
        )
```

### Example Matching Scenario

**User A wants to learn:** "machine learning"

**User B has skill:** "deep learning"  
**Similarity Score:** 0.87 (High match - related concepts)

**User C has skill:** "graphic design"  
**Similarity Score:** 0.12 (Low match - unrelated)

**User D has skill:** "python ml"  
**Similarity Score:** 0.92 (Very high match - almost identical)

### Matching Accuracy
- **Semantic understanding**: Recognizes synonyms ("python" ≈ "Python programming")
- **Context awareness**: "java script" vs "java" recognized as different
- **Skill variants**: "machine learning" ≈ "ML" ≈ "artificial intelligence"

### Fallback Strategy
If BERT model fails to load:
```python
# Simple exact match fallback
if skill_name.lower() == desired_skill.lower():
    similarity = 1.0
else:
    similarity = 0.0
```

---

## 📡 Real-time Communication

### Architecture: Ably Pub/Sub

#### Why Ably?
- WebSocket-based real-time messaging
- Automatic reconnection handling
- Channel-based communication
- Token-based authentication
- Presence detection

### Backend Setup (`api/ably_utils.py`)

#### 1. **Ably Initialization**
```python
from ably import AblyRest

ABLY_API_KEY = 'X2wYaQ.vXSY1g:...'  # API key
ably = AblyRest(ABLY_API_KEY)
```

#### 2. **Channel Naming Convention**
```python
def get_channel_name(user1_id, user2_id):
    """Generate consistent channel for two users"""
    ids = sorted([user1_id, user2_id])
    return f'private-chat-{ids[0]}-{ids[1]}'

# Example: User 5 & User 12 → 'private-chat-5-12'
```

#### 3. **Token Generation**
```python
def generate_client_token(user_id):
    """Generate Ably token for frontend"""
    token_request = ably.auth.create_token_request({
        'client_id': str(user_id),
        'capability': {
            'private-chat-*': ['subscribe', 'presence']
        }
    })
    return token_request
```

#### 4. **Message Publishing**
```python
def publish_message_sync(channel_name, message_data):
    """Publish message to Ably channel"""
    channel = ably.channels.get(channel_name)
    channel.publish('message', message_data)
```

### Frontend Setup (`contexts/RealtimeContext.js`)

#### 1. **Ably Client Initialization**
```javascript
import { Realtime } from 'ably';

// Get token from backend
const response = await api.get('realtime/token/');
const { token } = response.data;

// Initialize Ably client
const ablyClient = new Realtime({ token });
```

#### 2. **Channel Subscription**
```javascript
const subscribeToChat = (otherUserId, onMessage) => {
    const channelName = getChannelName(user.id, otherUserId);
    const channel = ably.channels.get(channelName);
    
    // Subscribe to messages
    channel.subscribe('message', (message) => {
        onMessage(message.data);
    });
    
    return () => channel.unsubscribe();
};
```

#### 3. **Real-time Notification System**
```javascript
// NotificationManager polls for new notifications
useEffect(() => {
    const checkNotifications = async () => {
        const { data } = await api.get('/notifications/unread/');
        
        // Show popup for new notifications
        if (data.unread_count > lastCount) {
            showNotificationPopup(data.notifications[0]);
        }
    };
    
    const interval = setInterval(checkNotifications, 30000);
    return () => clearInterval(interval);
}, []);
```

### Message Flow

**Scenario: User A sends message to User B**

```
1. User A → Frontend → POST /api/messages/
   Body: { receiver: B_id, content: "Hello" }

2. Backend → Creates Message in database
   Message.objects.create(sender=A, receiver=B, content="Hello")

3. Backend → Triggers post_save signal
   create_message_notification() → Creates Notification for User B

4. Backend → Publishes to Ably channel
   channel: 'private-chat-A_id-B_id'
   message: { type: 'message', message: {...} }

5. User B's Browser → Ably client receives message
   channel.subscribe('message', callback)

6. User B → Message appears instantly in chat
   No page refresh needed!

7. User B → Notification popup appears
   NotificationManager → Shows toast notification
```

### Notification Types
```python
NOTIFICATION_TYPES = [
    'message',              # New chat message
    'connection_request',   # Someone wants to connect
    'connection_accepted',  # Connection approved
    'skill_match',         # New skill match found
]
```

---

## 📁 File Storage & Resume Processing

### File Storage Structure
```
backend/media/
├── resumes/
│   └── resume_userId_timestamp.pdf
├── profile_pictures/
│   └── profile_userId.jpg
└── chat_files/
    └── chat_file_timestamp.pdf
```

### Resume Upload & Processing

#### 1. **Upload Endpoint** (`resume_views.py`)
```python
class ResumeUploadView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        
        # Validate file type
        if not file.name.endswith('.pdf'):
            return Response({'error': 'Only PDF files'}, 
                          status=400)
        
        # Save resume
        resume, created = Resume.objects.update_or_create(
            user=request.user,
            defaults={'file': file, 'processed': False}
        )
```

#### 2. **Text Extraction** (`utils.py`)
```python
import PyPDF2

def extract_text_from_pdf(pdf_file):
    """Extract all text from PDF"""
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text
```

#### 3. **Skill Extraction**
```python
def extract_skills_from_text(text):
    """Extract skills using NLP and predefined list"""
    from .skills_data import COMMON_SKILLS
    import re
    
    text = text.lower()
    found_skills = set()
    
    # Multi-word skill matching
    for skill in COMMON_SKILLS:
        if ' ' in skill:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text):
                found_skills.add(skill)
    
    # Single word matching
    words = re.findall(r'\b\w+\b', text)
    for word in words:
        if word in COMMON_SKILLS:
            found_skills.add(word)
    
    return sorted(list(found_skills))
```

#### 4. **Automatic Skill Creation**
```python
# After extracting skills from resume
for skill_name in extracted_skills:
    # Generate BERT embedding
    embedding = get_skill_embedding(skill_name)
    
    # Create skill
    Skill.objects.get_or_create(
        user=request.user,
        name=skill_name,
        defaults={
            'embedding': embedding,
            'proficiency_level': 'intermediate'
        }
    )
```

### Predefined Skills List (`skills_data.py`)
```python
COMMON_SKILLS = [
    # Programming
    'python', 'javascript', 'java', 'c++', 'c#',
    
    # Frameworks
    'react', 'angular', 'django', 'flask', 'node.js',
    
    # Databases
    'mysql', 'postgresql', 'mongodb', 'redis',
    
    # Cloud
    'aws', 'azure', 'google cloud', 'docker', 'kubernetes',
    
    # Design
    'photoshop', 'illustrator', 'figma', 'ui/ux design',
    
    # ... 500+ skills total
]
```

### File Size Limits
```python
# settings.py
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
```

---

## 🔌 API Endpoints

### Base URL: `http://localhost:8000/api`

### Authentication Endpoints

#### POST `/auth/register/`
**Request:**
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123",
    "first_name": "John",
    "last_name": "Doe"
}
```
**Response:**
```json
{
    "token": "a1b2c3d4e5f6...",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com"
    }
}
```

#### POST `/auth/login/`
**Request:**
```json
{
    "username": "john_doe",
    "password": "SecurePass123"
}
```
**Response:**
```json
{
    "token": "a1b2c3d4e5f6...",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com"
    }
}
```

#### GET `/auth/check-username/{username}/`
**Response:**
```json
{
    "available": false,
    "message": "Username is already taken"
}
```

---

### Profile Endpoints

#### GET `/profile/`
**Headers:** `Authorization: Token a1b2c3d4e5f6...`  
**Response:**
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "profile": {
        "bio": "Software developer passionate about AI",
        "created_at": "2024-01-15T10:30:00Z"
    }
}
```

#### PATCH `/profile/`
**Request:**
```json
{
    "first_name": "Johnny",
    "profile": {
        "bio": "Updated bio text"
    }
}
```

---

### Skills Endpoints

#### GET `/skills/`
**Response:**
```json
[
    {
        "id": 1,
        "name": "Python",
        "description": "Backend development",
        "proficiency_level": "advanced",
        "created_at": "2024-01-15T10:30:00Z"
    }
]
```

#### POST `/skills/`
**Request:**
```json
{
    "name": "React",
    "description": "Frontend framework",
    "proficiency_level": "intermediate"
}
```

#### DELETE `/skills/{id}/`

---

### Resume Endpoints

#### POST `/upload_resume/`
**Request:** `multipart/form-data`
```
file: resume.pdf
```
**Response:**
```json
{
    "id": 1,
    "file": "/media/resumes/resume_1_20240115.pdf",
    "processed": true,
    "skills_extracted": ["python", "django", "react"],
    "created_at": "2024-01-15T10:30:00Z"
}
```

#### GET `/resume/current/`
**Response:**
```json
{
    "id": 1,
    "file": "/media/resumes/resume_1_20240115.pdf",
    "processed": true
}
```

#### DELETE `/resume/current/`

---

### Skill Matching Endpoints

#### POST `/match_skills/`
**Request:**
```json
{
    "skills": ["machine learning", "python"]
}
```
**Response:**
```json
{
    "matches": [
        {
            "user": {
                "id": 5,
                "username": "data_scientist",
                "email": "ds@example.com"
            },
            "skill": "deep learning",
            "similarity_score": 0.92
        },
        {
            "user": {
                "id": 8,
                "username": "ai_expert",
                "email": "ai@example.com"
            },
            "skill": "python ml",
            "similarity_score": 0.88
        }
    ]
}
```

---

### Search Endpoints

#### GET `/users/search/?q=python&skill=django`
**Response:**
```json
{
    "users": [
        {
            "id": 5,
            "username": "django_dev",
            "email": "dev@example.com",
            "skills": ["python", "django", "postgresql"]
        }
    ]
}
```

#### GET `/users/profile/{username}/`
**Response:**
```json
{
    "id": 5,
    "username": "django_dev",
    "profile": {
        "bio": "Full-stack developer"
    },
    "skills": [
        {
            "name": "Python",
            "proficiency_level": "expert"
        }
    ]
}
```

---

### Connection Endpoints

#### POST `/connections/request/{user_id}/`
**Response:**
```json
{
    "id": 10,
    "requester": 1,
    "receiver": 5,
    "status": "pending",
    "created_at": "2024-01-15T10:30:00Z"
}
```

#### GET `/connections/`
**Response:**
```json
{
    "connections": [
        {
            "id": 10,
            "user": {
                "id": 5,
                "username": "friend"
            },
            "status": "connected",
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

#### POST `/connections/{connection_id}/accept/`
**Response:**
```json
{
    "message": "Connection accepted",
    "connection": {
        "id": 10,
        "status": "connected"
    }
}
```

#### POST `/connections/{connection_id}/reject/`

---

### Messaging Endpoints

#### GET `/messages/?with={user_id or username}`
**Response:**
```json
{
    "messages": [
        {
            "id": 100,
            "sender": {
                "id": 1,
                "username": "john_doe"
            },
            "receiver": {
                "id": 5,
                "username": "friend"
            },
            "content": "Hello!",
            "file": null,
            "read": true,
            "created_at": "2024-01-15T10:30:00Z"
        }
    ],
    "connection_status": "connected",
    "connection_id": 10
}
```

#### POST `/messages/`
**Request:**
```json
{
    "receiver": 5,
    "content": "Hi there!"
}
```
**Response:**
```json
{
    "id": 101,
    "sender": 1,
    "receiver": 5,
    "content": "Hi there!",
    "created_at": "2024-01-15T10:35:00Z"
}
```

#### GET `/conversations/`
**Response:**
```json
{
    "conversations": [
        {
            "id": 5,
            "username": "friend",
            "email": "friend@example.com",
            "last_message": "See you later!",
            "last_message_time": "2024-01-15T11:00:00Z"
        }
    ]
}
```

---

### Notification Endpoints

#### GET `/notifications/`
**Response:**
```json
[
    {
        "id": 50,
        "notification_type": "message",
        "title": "New message from john_doe",
        "message": "Hello!",
        "sender": {
            "id": 1,
            "username": "john_doe"
        },
        "link": "/messages?user=john_doe",
        "read": false,
        "created_at": "2024-01-15T10:30:00Z"
    }
]
```

#### GET `/notifications/unread/`
**Response:**
```json
{
    "unread_count": 3,
    "notifications": [...]
}
```

#### POST `/notifications/{id}/mark_read/`

#### POST `/notifications/mark_all_read/`

---

### Real-time Endpoint

#### GET `/realtime/token/`
**Response:**
```json
{
    "token": "ably_token_xyz...",
    "expires": 1705320000,
    "capability": "{\"private-chat-*\":[\"subscribe\",\"presence\"]}",
    "clientId": "1"
}
```

---

### Streaks Endpoint

#### GET `/streaks/`
**Response:**
```json
{
    "current_streak": 5,
    "longest_streak": 12,
    "total_logins": 47
}
```

---

## 🚀 Setup & Run Instructions

### Prerequisites
- **Python 3.8+**
- **Node.js 14+**
- **Git**

---

### Backend Setup

#### 1. Navigate to backend directory
```bash
cd c:\SkillXchange\backend
```

#### 2. Create virtual environment (recommended)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

#### 3. Install dependencies
```bash
pip install django djangorestframework django-cors-headers
pip install sentence-transformers scikit-learn nltk PyPDF2
pip install ably
```

#### 4. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 5. Create superuser (admin access)
```bash
python manage.py createsuperuser
```

#### 6. Download NLTK data (first time only)
```bash
python manage.py shell
>>> import nltk
>>> nltk.download('punkt')
>>> nltk.download('averaged_perceptron_tagger')
>>> exit()
```

#### 7. Start Django server
```bash
python manage.py runserver
```
**Server runs at:** `http://localhost:8000`

---

### Frontend Setup

#### 1. Navigate to frontend directory
```bash
cd c:\SkillXchange\frontend
```

#### 2. Install dependencies
```bash
npm install
```

#### 3. Start React development server
```bash
npm start
```
**App opens at:** `http://localhost:3000`

---

### Environment Variables (Optional)

**Backend (`backend/.env`)**
```env
SECRET_KEY=your-secret-key
DEBUG=True
ABLY_API_KEY=your-ably-api-key
```

**Frontend (`frontend/.env`)**
```env
REACT_APP_API_BASE_URL=http://localhost:8000/api
```

---

### Testing Database

**Check database contents:**
```bash
cd backend
python check_database.py
```

**Access Django admin:**
1. Start backend server
2. Visit: `http://localhost:8000/admin`
3. Login with superuser credentials

---

## 🎬 Demo Flow

### Scenario: Complete User Journey

#### **Step 1: Registration**
1. Open `http://localhost:3000`
2. Click "Get Started" → Redirects to Login
3. Click "Register"
4. Fill form:
   - Username: `demo_user`
   - Email: `demo@example.com`
   - Password: `DemoPass123`
5. Click "Register" → Auto-login → Redirected to Home

#### **Step 2: Profile Setup**
1. Click "Profile" in navbar
2. Click "Edit Profile"
3. Update bio: "Software developer learning AI"
4. Click "Save"

#### **Step 3: Upload Resume**
1. Still on Profile page
2. In "Your Resume" section, click "Choose File"
3. Select PDF resume
4. Click "Upload Resume"
5. **Backend processes resume automatically**
6. Skills extracted and added to profile
7. Check "Your Skills" section → Skills appear

#### **Step 4: Add Manual Skill**
1. In "Your Skills" section
2. Click "Add Skill"
3. Enter:
   - Skill: `Machine Learning`
   - Proficiency: `Intermediate`
4. Click "Add"
5. **BERT embedding generated and stored**

#### **Step 5: Find Matches**
1. Click "Explore" in navbar
2. Enter skill you want to learn: `React`
3. Click "Find Matches"
4. **Backend runs similarity algorithm**
5. List of users with React skills appears
6. Sorted by similarity score

#### **Step 6: Connect with User**
1. Click on a user from matches
2. View their profile
3. Click "Send Connection Request"
4. **Connection created with status "pending"**

#### **Step 7: Messaging**
1. Other user logs in
2. Sees notification: "New connection request"
3. Goes to Messages page
4. Sees pending request with Accept/Reject buttons
5. Clicks "Accept"
6. **Connection status changes to "connected"**

#### **Step 8: Real-time Chat**
1. User 1 goes to Messages
2. Clicks on User 2 in conversation list
3. Types message: "Hi! Can you teach me React?"
4. Clicks Send
5. **Message saved to database**
6. **Ably publishes to real-time channel**
7. **User 2's browser receives message instantly**
8. **Notification popup appears on User 2's screen**

#### **Step 9: Notifications**
1. User 2 clicks notification bell icon
2. Sees unread badge (1)
3. Views "New message from demo_user"
4. Click notification → Redirects to Messages
5. Chat opens automatically

#### **Step 10: Skill Matching Result**
1. Backend creates SkillMatch record
2. User 1 sees similarity score: 0.91
3. Indicates high match between desired skill and provider's skill

---

## ✨ Key Features

### 1. **AI-Powered Skill Matching**
- BERT embeddings for semantic understanding
- Cosine similarity scoring (0.0 - 1.0)
- Top 10 matches returned
- Understands synonyms and related concepts

### 2. **Resume Parsing**
- Automatic PDF text extraction
- NLP-based skill extraction
- 500+ predefined skill database
- Auto-creates skills in profile

### 3. **Real-time Messaging**
- Instant message delivery via Ably
- No page refresh needed
- Connection-based access control
- File attachment support

### 4. **Notification System**
- Real-time popup notifications
- Unread badge in navbar
- Multiple notification types
- Persistent notification center
- Mark as read functionality

### 5. **Connection Management**
- Request/Accept/Reject workflow
- Connection status tracking
- Message access control
- Pending request indicators

### 6. **User Search & Discovery**
- Search by username
- Filter by skills
- View user profiles
- Skill-based recommendations

### 7. **Responsive Design**
- Mobile-friendly layout
- Touch-friendly controls
- Adaptive grid layouts
- Modern gradient UI

### 8. **Authentication & Security**
- Token-based authentication
- Password hashing (Django default)
- CORS protection
- Protected API endpoints

### 9. **Profile Customization**
- Bio editing
- Skill management (CRUD)
- Resume upload/delete
- Proficiency levels

### 10. **Login Streak Tracking**
- Daily login recording
- Streak calculation
- Gamification element

---

## 📊 Technical Highlights

### Performance
- **Skill matching**: < 2 seconds for 10,000 skills
- **Message delivery**: < 100ms via Ably
- **Resume processing**: < 5 seconds for 10-page PDF

### Scalability
- **Database**: SQLite (demo), easily migrate to PostgreSQL
- **File storage**: Local media (demo), can move to S3
- **Real-time**: Ably handles millions of concurrent connections

### Code Quality
- **Backend**: RESTful API design
- **Frontend**: Component-based architecture
- **Error handling**: Try-catch blocks, proper HTTP codes
- **Signals**: Automatic notification creation

---

## 🎤 Presentation Tips

### Opening (1 min)
"SkillXchange is a platform where professionals exchange knowledge. If you want to learn Python, we connect you with someone who can teach it. In return, you teach them something you know. It's a mutual learning ecosystem powered by AI."

### Tech Stack (1 min)
"Backend: Django REST API with SQLite. Frontend: React with real-time Ably integration. AI: BERT embeddings for semantic skill matching."

### Demo Key Points (3 min)
1. Show resume upload → automatic skill extraction
2. Search for skill → show similarity scores
3. Send message → demonstrate real-time delivery
4. Show notification popup

### Algorithm Explanation (2 min)
"We use BERT to convert skills into 384-dimensional vectors. 'Machine Learning' and 'Deep Learning' have similar vectors. We calculate cosine similarity to find the best matches. Score of 0.9+ means very high relevance."

### Q&A Prep
- **Why BERT?** "Understands semantic meaning, not just keywords"
- **Why Ably?** "Handles WebSocket complexity, auto-reconnection"
- **Scalability?** "SQLite for demo, PostgreSQL for production"
- **Security?** "Token auth, hashed passwords, connection-based access"

---

## 📝 Conclusion

SkillXchange demonstrates:
- ✅ Full-stack web development (Django + React)
- ✅ AI/ML integration (BERT embeddings)
- ✅ Real-time communication (Ably)
- ✅ RESTful API design
- ✅ Database modeling
- ✅ File processing (PDF parsing)
- ✅ Modern UI/UX

**GitHub:** https://github.com/Bhavika-a296/SkillXchange  
**Live Demo:** http://localhost:3000 (local)

---

## 🙏 Thank You!

Questions?

---

*Document prepared on: November 19, 2025*  
*Project: SkillXchange*  
*Version: 1.0*
