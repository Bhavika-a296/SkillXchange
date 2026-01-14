import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { usersApi } from '../../services/api';
import './Profile.css';

const UserProfileView = () => {
  const { username } = useParams();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [connecting, setConnecting] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        const { data } = await usersApi.getProfile(username);
        setProfile(data);
        setError('');
      } catch (err) {
        console.error('Error fetching user profile:', err);
        setError('Could not load user profile');
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, [username]);

  const handleConnect = async () => {
    if (!profile?.user?.id) return;
    try {
      setConnecting(true);
      // Redirect to Messages page with this user selected
      navigate(`/messages?user=${profile.user.id}`);
    } catch (err) {
      console.error('Error connecting:', err);
    } finally {
      setConnecting(false);
    }
  };

  if (loading) return <div className="profile-container loading">Loading...</div>;
  if (error) return <div className="profile-container error-message">{error}</div>;
  if (!profile) return <div className="profile-container empty-state">No profile found</div>;

  return (
    <div className="profile-container">
      <div className="profile-header">
        <h2>{profile.user?.username}'s Profile</h2>
        <button className="button-secondary" onClick={() => navigate(-1)}>Back</button>
      </div>

      <div className="profile-content">
        <section className="profile-info">
          <h3>About</h3>
          <p className="bio-text">{profile.bio || 'No bio available.'}</p>
        </section>

        <section className="skills-section">
          <h3>Skills</h3>
          <div className="skills-list">
            {profile.skills && profile.skills.length > 0 ? (
              <div className="skills-tags">
                {profile.skills.map((skill, idx) => (
                  <span key={idx} className="skill-tag">
                    {skill.name}
                  </span>
                ))}
              </div>
            ) : (
              <p>No skills listed.</p>
            )}
          </div>
        </section>

        <section className="connect-section">
          <button className="button-primary" onClick={handleConnect} disabled={connecting}>
            {connecting ? 'Connecting...' : 'Get Connected'}
          </button>
        </section>
      </div>
    </div>
  );
};

export default UserProfileView;
