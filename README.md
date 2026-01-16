# SkillXchange

A platform for peer-to-peer skill exchange where users can learn and teach skills while earning rewards.

## Features

- 🎯 **Skill Matching**: AI-powered skill matching using BERT embeddings
- 💬 **Real-time Messaging**: Chat with other users using Ably
- 🏆 **Achievement Badges**: Earn badges for completing learning milestones
- 📊 **Learning Journey**: Track your learning and teaching progress
- 🔔 **Notifications**: Stay updated with real-time notifications
- 👤 **User Profiles**: Showcase your skills and achievements
- 📄 **Resume Upload**: Automatically extract skills from your resume

## Tech Stack

### Backend
- Django 5.2.6
- Django REST Framework
- SQLite Database
- SentenceTransformer (paraphrase-MiniLM-L6-v2) for skill matching
- Ably for real-time features

### Frontend
- React 18
- React Router
- Axios for API calls
- CSS3 for styling

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 14+
- pip
- npm

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

6. Start the Django server:
```bash
python manage.py runserver
```

The backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the React development server:
```bash
npm start
```

The frontend will run on `http://localhost:3000`

## Project Structure

```
SkillXchange/
├── backend/
│   ├── api/              # Django app
│   ├── backend/          # Django settings
│   ├── media/            # Uploaded files
│   └── manage.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/   # Reusable components
│   │   ├── contexts/     # React contexts
│   │   ├── pages/        # Page components
│   │   └── services/     # API services
│   └── package.json
└── README.md
```

## Key Features Explained

### Badge System
Users earn badges when they complete skill learning/teaching milestones:
- 🥉 3 skills (Learner/Teacher)
- 🥈 5 skills (Learner/Teacher)
- 🥇 10 skills (Learner/Teacher)

### Learning Journey
- Track all skills learned and taught
- View session details and duration
- Scrollable interface showing one card at a time

### Notification System
- Real-time notifications for messages, connections, and matches
- Notifications disappear once read
- Clean, uncluttered interface

## API Endpoints

- `/api/auth/` - Authentication (login, register, logout)
- `/api/profile/` - User profile management
- `/api/skills/` - Skill management
- `/api/learning/` - Learning sessions
- `/api/notifications/` - Notifications
- `/api/messages/` - Messaging

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For support, email support@skillxchange.com or open an issue in the repository.
