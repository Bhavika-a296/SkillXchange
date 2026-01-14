import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ResumeUpload from '../../components/ResumeUpload/ResumeUpload';
import SkillMatch from '../../components/SkillMatch/SkillMatch';
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
        <section className="badges-section">
          <h3>Your Badges</h3>
          <div className="badges-grid">
            {/* Badge 1: 5 Day Streak */}
            <div className={`badge-item ${streakData.maxStreak >= 5 ? 'earned' : 'locked'}`}>
              <div className="badge-icon">
                <svg viewBox="0 0 100 100" className="badge-svg">
                  <circle cx="50" cy="50" r="45" className="badge-circle" />
                  <path d="M50 20 L60 40 L82 43 L66 58 L70 80 L50 69 L30 80 L34 58 L18 43 L40 40 Z" className="badge-star" />
                  <text x="50" y="95" textAnchor="middle" className="badge-number">5</text>
                </svg>
              </div>
              <div className="badge-info">
                <div className="badge-name">Starter</div>
                <div className="badge-desc">5 Day Streak</div>
              </div>
              {streakData.maxStreak >= 5 && <div className="badge-earned">✓</div>}
            </div>

            {/* Badge 2: 10 Day Streak */}
            <div className={`badge-item ${streakData.maxStreak >= 10 ? 'earned' : 'locked'}`}>
              <div className="badge-icon">
                <svg viewBox="0 0 100 100" className="badge-svg">
                  <circle cx="50" cy="50" r="45" className="badge-circle" />
                  <path d="M50 15 L55 35 L75 40 L60 55 L63 75 L50 67 L37 75 L40 55 L25 40 L45 35 Z" className="badge-star" />
                  <path d="M50 25 L53 38 L65 41 L56 50 L58 62 L50 57 L42 62 L44 50 L35 41 L47 38 Z" className="badge-star-small" />
                  <text x="50" y="95" textAnchor="middle" className="badge-number">10</text>
                </svg>
              </div>
              <div className="badge-info">
                <div className="badge-name">Committed</div>
                <div className="badge-desc">10 Day Streak</div>
              </div>
              {streakData.maxStreak >= 10 && <div className="badge-earned">✓</div>}
            </div>

            {/* Badge 3: 30 Day Streak */}
            <div className={`badge-item ${streakData.maxStreak >= 30 ? 'earned' : 'locked'}`}>
              <div className="badge-icon">
                <svg viewBox="0 0 100 100" className="badge-svg">
                  <circle cx="50" cy="50" r="45" className="badge-circle" />
                  <polygon points="50,10 61,35 88,35 67,52 76,77 50,60 24,77 33,52 12,35 39,35" className="badge-star" />
                  <circle cx="50" cy="50" r="15" className="badge-center" />
                  <text x="50" y="95" textAnchor="middle" className="badge-number">30</text>
                </svg>
              </div>
              <div className="badge-info">
                <div className="badge-name">Dedicated</div>
                <div className="badge-desc">30 Day Streak</div>
              </div>
              {streakData.maxStreak >= 30 && <div className="badge-earned">✓</div>}
            </div>

            {/* Badge 4: 60 Day Streak */}
            <div className={`badge-item ${streakData.maxStreak >= 60 ? 'earned' : 'locked'}`}>
              <div className="badge-icon">
                <svg viewBox="0 0 100 100" className="badge-svg">
                  <circle cx="50" cy="50" r="45" className="badge-circle" />
                  <path d="M50 10 L62 38 L92 38 L68 56 L78 84 L50 66 L22 84 L32 56 L8 38 L38 38 Z" className="badge-star" />
                  <path d="M50 20 L58 40 L78 40 L62 52 L68 72 L50 60 L32 72 L38 52 L22 40 L42 40 Z" className="badge-star-overlay" />
                  <text x="50" y="95" textAnchor="middle" className="badge-number">60</text>
                </svg>
              </div>
              <div className="badge-info">
                <div className="badge-name">Champion</div>
                <div className="badge-desc">60 Day Streak</div>
              </div>
              {streakData.maxStreak >= 60 && <div className="badge-earned">✓</div>}
            </div>

            {/* Badge 5: 100 Day Streak */}
            <div className={`badge-item ${streakData.maxStreak >= 100 ? 'earned' : 'locked'}`}>
              <div className="badge-icon">
                <svg viewBox="0 0 100 100" className="badge-svg">
                  <circle cx="50" cy="50" r="45" className="badge-circle" />
                  <path d="M50 8 L64 36 L94 36 L70 54 L82 82 L50 64 L18 82 L30 54 L6 36 L36 36 Z" className="badge-star" />
                  <circle cx="50" cy="50" r="20" className="badge-center" />
                  <circle cx="50" cy="50" r="12" className="badge-inner" />
                  <text x="50" y="95" textAnchor="middle" className="badge-number">100</text>
                </svg>
              </div>
              <div className="badge-info">
                <div className="badge-name">Legend</div>
                <div className="badge-desc">100 Day Streak</div>
              </div>
              {streakData.maxStreak >= 100 && <div className="badge-earned">✓</div>}
            </div>

            {/* Badge 6: 365 Day Streak */}
            <div className={`badge-item ${streakData.maxStreak >= 365 ? 'earned' : 'locked'}`}>
              <div className="badge-icon">
                <svg viewBox="0 0 100 100" className="badge-svg">
                  <circle cx="50" cy="50" r="45" className="badge-circle" />
                  <path d="M50 5 L66 34 L98 34 L72 52 L86 81 L50 63 L14 81 L28 52 L2 34 L34 34 Z" className="badge-star" />
                  <circle cx="50" cy="50" r="25" className="badge-center" />
                  <path d="M50 30 L54 44 L68 44 L57 52 L61 66 L50 58 L39 66 L43 52 L32 44 L46 44 Z" className="badge-star-inner" />
                  <text x="50" y="95" textAnchor="middle" className="badge-number">365</text>
                </svg>
              </div>
              <div className="badge-info">
                <div className="badge-name">Master</div>
                <div className="badge-desc">Year Streak</div>
              </div>
              {streakData.maxStreak >= 365 && <div className="badge-earned">✓</div>}
            </div>
          </div>
        </section>

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