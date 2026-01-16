# Integration Guide - Adding Learning Flow to Existing Pages

## 🎯 Quick Integration Examples

### 1. Add "Join Learning" Button to User Profile Page

**File:** `frontend/src/pages/Profile/ProfilePage.js` (or similar)

```javascript
import React, { useState } from 'react';
import JoinLearning from '../../components/JoinLearning/JoinLearning';

const ProfilePage = ({ profileUser }) => {
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [selectedSkill, setSelectedSkill] = useState(null);
  const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
  const isOwnProfile = currentUser.id === profileUser.id;

  const handleJoinSkill = (skillName) => {
    setSelectedSkill(skillName);
    setShowJoinModal(true);
  };

  return (
    <div className="profile-page">
      {/* Existing profile content */}
      
      {/* Display user's skills */}
      <div className="skills-section">
        <h3>Skills</h3>
        {profileUser.skills.map(skill => (
          <div key={skill.id} className="skill-item">
            <span>{skill.name}</span>
            {!isOwnProfile && (
              <button onClick={() => handleJoinSkill(skill.name)}>
                Join Learning
              </button>
            )}
          </div>
        ))}
      </div>

      {/* Join Learning Modal/Component */}
      {showJoinModal && (
        <div className="modal">
          <JoinLearning
            teacherId={profileUser.id}
            teacherUsername={profileUser.username}
            skillName={selectedSkill}
            onSuccess={() => {
              setShowJoinModal(false);
              alert('Learning session started!');
            }}
          />
          <button onClick={() => setShowJoinModal(false)}>Close</button>
        </div>
      )}

      {/* Add Skills Learned/Taught Sections */}
      <SkillsLearnedTaught username={profileUser.username} />
    </div>
  );
};
```

---

### 2. Add Learning Link to Navigation

**File:** `frontend/src/components/Navigation/Navbar.js`

```javascript
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="navbar">
      <Link to="/">Home</Link>
      <Link to="/explore">Explore</Link>
      
      {/* ADD THIS */}
      <Link to="/learning">
        <span>📚</span> Learning
      </Link>
      
      <Link to="/messages">Messages</Link>
      <Link to="/profile">Profile</Link>
    </nav>
  );
};
```

---

### 3. Add Learning Route to App.js

**File:** `frontend/src/App.js`

```javascript
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Learning from './pages/Learning/Learning';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <Router>
      <Routes>
        {/* Existing routes */}
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        
        {/* ADD THESE */}
        <Route 
          path="/learning" 
          element={
            <ProtectedRoute>
              <Learning />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/rate-session/:sessionId" 
          element={
            <ProtectedRoute>
              <RateSession />
            </ProtectedRoute>
          } 
        />
        
        {/* Other routes */}
      </Routes>
    </Router>
  );
}
```

---

### 4. Create Rate Session Page

**File:** `frontend/src/pages/RateSession/RateSession.js` (NEW FILE)

```javascript
import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import RatingFeedback from '../../components/RatingFeedback/RatingFeedback';
import './RateSession.css';

const RateSession = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();

  return (
    <div className="rate-session-page">
      <div className="container">
        <RatingFeedback
          sessionId={parseInt(sessionId)}
          onSubmitSuccess={() => {
            navigate('/learning');
          }}
        />
      </div>
    </div>
  );
};

export default RateSession;
```

**File:** `frontend/src/pages/RateSession/RateSession.css` (NEW FILE)

```css
.rate-session-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
}

.rate-session-page .container {
  max-width: 800px;
  margin: 0 auto;
}
```

---

### 5. Add Points Display to Profile

**File:** `frontend/src/pages/Profile/ProfilePage.js`

```javascript
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ProfilePage = () => {
  const [userPoints, setUserPoints] = useState(null);
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchUserPoints();
  }, []);

  const fetchUserPoints = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_BASE_URL}/api/learning/points/`,
        {
          headers: { Authorization: `Token ${token}` }
        }
      );
      setUserPoints(response.data);
    } catch (error) {
      console.error('Error fetching points:', error);
    }
  };

  return (
    <div className="profile-page">
      {/* Points Badge in Header */}
      <div className="profile-header">
        <h1>{user.username}</h1>
        {userPoints && (
          <div className="points-badge">
            💰 {userPoints.balance} points
          </div>
        )}
      </div>

      {/* Rest of profile content */}
    </div>
  );
};
```

---

### 6. Add Skills Sections to Profile

**File:** `frontend/src/pages/Profile/ProfilePage.js`

```javascript
import SkillsLearnedTaught from '../../components/SkillsLearnedTaught/SkillsLearnedTaught';

const ProfilePage = ({ username }) => {
  return (
    <div className="profile-page">
      {/* Existing profile info */}
      
      {/* User's own skills */}
      <section className="my-skills">
        <h2>My Skills</h2>
        {/* Existing skills display */}
      </section>

      {/* ADD THIS SECTION */}
      <section className="learning-history">
        <h2>Learning Journey</h2>
        <SkillsLearnedTaught username={username} />
      </section>
    </div>
  );
};
```

---

### 7. Notification Integration

**File:** `frontend/src/components/NotificationPopup/NotificationPopup.js`

```javascript
const NotificationPopup = ({ notification }) => {
  const handleClick = () => {
    if (notification.link) {
      window.location.href = notification.link;
    }
  };

  // Handle learning-related notifications
  const getNotificationIcon = () => {
    if (notification.notification_type === 'skill_match') {
      return '🎓';
    }
    // ... other notification types
  };

  return (
    <div className="notification" onClick={handleClick}>
      <span className="icon">{getNotificationIcon()}</span>
      <div className="content">
        <h4>{notification.title}</h4>
        <p>{notification.message}</p>
      </div>
    </div>
  );
};
```

---

## 🎨 Styling Integration

### Add to Global CSS

**File:** `frontend/src/index.css` or `frontend/src/App.css`

```css
/* Learning Flow Global Styles */
:root {
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  --danger-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.points-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--primary-gradient);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 16px;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 12px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}
```

---

## 📱 Responsive Considerations

### Mobile Navigation

```javascript
// Add to mobile menu
<div className="mobile-menu">
  <Link to="/learning">
    <div className="menu-item">
      <span className="icon">📚</span>
      <span>Learning</span>
    </div>
  </Link>
</div>
```

---

## 🔔 Real-time Updates (Optional Enhancement)

If you want real-time updates when points change:

```javascript
import { useEffect } from 'react';
import { useRealtimeContext } from '../../contexts/RealtimeContext';

const PointsDisplay = () => {
  const { subscribe } = useRealtimeContext();
  const [points, setPoints] = useState(null);

  useEffect(() => {
    // Subscribe to point updates
    const unsubscribe = subscribe('points-update', (data) => {
      setPoints(data.new_balance);
      // Optionally show animation
    });

    return () => unsubscribe();
  }, []);

  // ...
};
```

---

## 🚀 Quick Start Integration Steps

1. **Add Route** → Update App.js with /learning route
2. **Add Navigation** → Add Learning link to navbar
3. **Update Profile** → Add SkillsLearnedTaught component
4. **Add Join Button** → Add JoinLearning to skill displays
5. **Create Rate Page** → Add rate-session route and page
6. **Test Flow** → Join → Complete → Rate

---

## ✅ Integration Checklist

Backend:
- [ ] Run migrations
- [ ] Initialize point config
- [ ] Verify all endpoints working

Frontend:
- [ ] Import all new components
- [ ] Add /learning route to App.js
- [ ] Add /rate-session/:id route to App.js
- [ ] Add Learning link to navigation
- [ ] Add JoinLearning button to profiles
- [ ] Add SkillsLearnedTaught to profiles
- [ ] Add points display to user dashboard
- [ ] Test on desktop
- [ ] Test on mobile
- [ ] Test animations

---

## 🎯 Minimal Integration (5 Minutes)

If you want the quickest possible integration:

1. **Add to App.js:**
```javascript
import Learning from './pages/Learning/Learning';

// In routes:
<Route path="/learning" element={<Learning />} />
```

2. **Add to Navbar:**
```javascript
<Link to="/learning">Learning</Link>
```

3. **Done!** Users can now access /learning to see their sessions.

For join functionality, add JoinLearning component to existing profile pages where skills are displayed.

---

## 📞 Need Help?

Common integration issues:

1. **Import errors:** Ensure paths are correct relative to your file structure
2. **Styling conflicts:** Use more specific CSS selectors
3. **Route not found:** Check BrowserRouter is wrapping all routes
4. **API errors:** Verify REACT_APP_API_URL is set correctly

---

**Happy Integrating! 🎉**
