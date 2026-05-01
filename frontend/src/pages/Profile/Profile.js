import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import ResumeUpload from '../../components/ResumeUpload/ResumeUpload';
import SkillsLearnedTaught from '../../components/SkillsLearnedTaught/SkillsLearnedTaught';
import LearnerSkills from '../../components/LearnerSkills/LearnerSkills';
import Badges from '../../components/Badges/Badges';
import VerificationBadges from '../../components/VerificationBadges/VerificationBadges';
import { profileApi, authApi } from '../../services/api';
import api from '../../services/api';
import './Profile.css';

const Profile = () => {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [profile, setProfile] = useState(null);
  const [connections, setConnections] = useState([]);
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [isDeletingAccount, setIsDeletingAccount] = useState(false);
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

  const handleDeleteAccount = async () => {
    const confirmed = window.confirm(
      'Delete your account permanently? This action cannot be undone.'
    );
    if (!confirmed) {
      return;
    }

    try {
      setIsDeletingAccount(true);
      await authApi.deleteAccount();
      await logout();
      navigate('/login');
    } catch (err) {
      console.error('Error deleting account:', err);
      setError(err.response?.data?.message || 'Failed to delete account. Please try again.');
    } finally {
      setIsDeletingAccount(false);
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
        <div className="profile-header-actions">
          <button 
            className="button-primary"
            onClick={() => setIsEditing(!isEditing)}
          >
            {isEditing ? 'Cancel' : 'Edit Profile'}
          </button>
          <button
            className="button-danger"
            onClick={handleDeleteAccount}
            disabled={isDeletingAccount}
          >
            {isDeletingAccount ? 'Deleting...' : 'Delete Account'}
          </button>
        </div>
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
              {(() => {
                const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                const today = new Date();
                const months = [];
                
                // Generate month labels for the past 365 days
                for (let i = 12; i >= 0; i--) {
                  const date = new Date(today);
                  date.setMonth(date.getMonth() - i);
                  months.push(monthNames[date.getMonth()]);
                }
                
                return months.map((month, idx) => (
                  <span key={idx} className="month-label">{month}</span>
                ));
              })()}
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
          <h3>Completed Learning Sessions</h3>
          <SkillsLearnedTaught />
        </section>

        <section className="learned-skills-section">
          <h3>Skills Verified as Learner</h3>
          <LearnerSkills username={profile.user?.username} />
        </section>

        <section className="badges-section">
          <h3>
            <span className="section-title-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d="M7 4h10v3a5 5 0 0 1-10 0V4Z" />
                <path d="M7 7H5a2 2 0 0 0 2 2M17 7h2a2 2 0 0 1-2 2" />
                <path d="M12 12v5M9 20h6" />
              </svg>
            </span>
            Achievements & Badges
          </h3>
          <Badges />
        </section>

        <section className="verification-section">
          <h3>
            <span className="section-title-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 3 5 6v6c0 5 3.4 8 7 9 3.6-1 7-4 7-9V6l-7-3Z" />
                <path d="m9 12 2 2 4-4" />
              </svg>
            </span>
            Skills Verified as Teacher
          </h3>
          <VerificationBadges 
            username={profile.user?.username} 
            isOwnProfile={true} 
          />
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