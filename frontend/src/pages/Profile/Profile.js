import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ResumeUpload from '../../components/ResumeUpload/ResumeUpload';
import SkillsLearnedTaught from '../../components/SkillsLearnedTaught/SkillsLearnedTaught';
import Badges from '../../components/Badges/Badges';
import { profileApi } from '../../services/api';
import api from '../../services/api';
import './Profile.css';

const Profile = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [connections, setConnections] = useState([]);
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [streakData, setStreakData] = useState({
    currentStreak: 0,
    maxStreak: 0,
    totalSessions: 0,
    contributions: []
  });
  const [formData, setFormData] = useState({
    bio: '',
    skills: [],
    interests: '',
    user: { username: 'User' }
  });

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        const { data } = await profileApi.get();
        
        // Initialize profile data with defaults
        const profileData = {
          user: data.user || { username: 'User' },
          bio: data.bio || '',
          skills: data.skills || [],
          interests: data.interests || '',
          created_at: data.created_at,
          updated_at: data.updated_at
        };
        
        setProfile(profileData);
        setFormData({
          bio: profileData.bio,
          skills: Array.isArray(profileData.skills) ? profileData.skills : [],
          interests: profileData.interests,
          user: profileData.user
        });
        setError('');
      } catch (err) {
        console.error('Error fetching profile:', err);
        setError('An error occurred while fetching profile');
      } finally {
        setLoading(false);
      }
    };

    const fetchConnections = async () => {
      try {
        const { data } = await api.get('/connections/');
        setConnections(data.connections || []);
      } catch (err) {
        console.error('Error fetching connections:', err);
      }
    };

    const fetchStreakData = async () => {
      try {
        const { data } = await api.get('/streaks/');
        setStreakData({
          currentStreak: data.current_streak || 0,
          maxStreak: data.max_streak || 0,
          totalSessions: data.total_days || 0,
          contributions: data.contributions || []
        });
      } catch (err) {
        console.error('Error fetching streak data:', err);
        // Keep default empty state
      }
    };

    fetchProfile();
    fetchConnections();
    fetchStreakData();
  }, [navigate]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const { data: updatedProfile } = await profileApi.update(formData);
      setProfile(updatedProfile);
      setIsEditing(false);
      setError('');
    } catch (err) {
      console.error('Error updating profile:', err);
      setError('An error occurred while updating profile');
    }
  };

  if (loading) {
    return <div className="profile-container loading">Loading...</div>;
  }

  if (error) {
    return <div className="profile-container error-message">{error}</div>;
  }

  if (!profile) {
    return <div className="profile-container empty-state">No profile data available</div>;
  }

  return (
    <div className="profile-container">
      {/* SVG Gradients Definition */}
      <svg width="0" height="0" style={{ position: 'absolute' }}>
        <defs>
          <linearGradient id="goldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#fbbf24" />
            <stop offset="50%" stopColor="#f59e0b" />
            <stop offset="100%" stopColor="#d97706" />
          </linearGradient>
          <linearGradient id="blueGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#3b82f6" />
            <stop offset="100%" stopColor="#06b6d4" />
          </linearGradient>
        </defs>
      </svg>

      <div className="profile-header">
        <h2>{profile.user?.username || 'My'} Profile</h2>
        <button 
          className="button-primary"
          onClick={() => setIsEditing(!isEditing)}
        >
          {isEditing ? 'Cancel' : 'Edit Profile'}
        </button>
      </div>

      {/* About Me - Horizontal Card */}
      <section className="profile-info-horizontal">
        <h3>About Me</h3>
        {isEditing ? (
          <textarea
            name="bio"
            value={formData.bio || ''}
            onChange={handleChange}
            placeholder="Tell us about yourself..."
            className="bio-input"
            rows="2"
          />
        ) : (
          <p className="bio-text">{profile.bio || 'No bio added yet.'}</p>
        )}
      </section>

      {/* Resume - Horizontal Card */}
      <section className="resume-section-horizontal">
        <h3>Resume</h3>
        <ResumeUpload onSkillsExtracted={(skills) => {
          setFormData(prev => ({
            ...prev,
            skills: [...prev.skills, ...skills]
          }));
        }} />
      </section>

      <div className="profile-content">
        <section className="streaks-section">
          <h3>Login Streaks</h3>
          <div className="streak-stats">
            <div className="stat-item">
              <div className="stat-value">{streakData.totalSessions}</div>
              <div className="stat-label">Total Days</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{streakData.maxStreak}</div>
              <div className="stat-label">Max Streak</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{streakData.currentStreak}</div>
              <div className="stat-label">Current Streak</div>
            </div>
          </div>
          <div className="contribution-graph">
            <div className="months-labels">
              {['Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'].map((month, idx) => (
                <span key={idx} className="month-label">{month}</span>
              ))}
            </div>
            <div className="contributions-grid">
              {streakData.contributions.map((day, idx) => {
                const level = day.count === 0 ? 0 : day.count === 1 ? 1 : day.count === 2 ? 2 : day.count === 3 ? 3 : 4;
                return (
                  <div
                    key={idx}
                    className={`contribution-day level-${level}`}
                    title={`${day.date}: ${day.count} sessions`}
                  />
                );
              })}
            </div>
          </div>
        </section>

        <section className="learning-journey-section">
          <h3>Learning Journey on SkillXchange</h3>
          <SkillsLearnedTaught />
        </section>

        <section className="badges-section">
          <h3>🏆 Achievements & Badges</h3>
          <Badges />
        </section>

        <section className="connections-section">
          <h3>My Connections</h3>
          {connections.length > 0 ? (
            <div className="connections-grid">
              {connections.map((connection) => (
                <div
                  key={connection.id}
                  className="connection-card"
                  onClick={() => navigate(`/users/${connection.username}`)}
                >
                  <div className="connection-info">
                    <h4>{connection.username}</h4>
                    {connection.profile?.bio && (
                      <p className="connection-bio">
                        {connection.profile.bio.slice(0, 80)}
                        {connection.profile.bio.length > 80 ? '...' : ''}
                      </p>
                    )}
                  </div>
                  <button
                    className="message-button"
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/users/${connection.username}`);
                    }}
                  >
                    View Profile
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <p className="no-connections">No connections yet. Start exploring to connect with others!</p>
          )}
        </section>
      </div>

      {isEditing && ( 
        <form onSubmit={handleSubmit} className="profile-form">
          <div className="form-group">
            <label htmlFor="bio">Bio</label>
            <textarea
              id="bio"
              name="bio"
              value={formData.bio || ''}
              onChange={handleChange}
              rows="4"
            />
          </div>

          <div className="form-actions">
            <button type="submit" className="button-primary">Save Changes</button>
          </div>
        </form>
      )}
    </div>
  );
};

export default Profile;