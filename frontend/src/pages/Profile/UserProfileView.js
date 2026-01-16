import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { usersApi } from '../../services/api';
import JoinLearning from '../../components/JoinLearning/JoinLearning';
import SkillsLearnedTaught from '../../components/SkillsLearnedTaught/SkillsLearnedTaught';
import UserRatings from '../../components/UserRatings/UserRatings';
import Badges from '../../components/Badges/Badges';
import './Profile.css';

const UserProfileView = () => {
  const { username } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const searchedSkill = searchParams.get('skill'); // Get the searched skill from URL
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [connecting, setConnecting] = useState(false);
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [selectedSkill, setSelectedSkill] = useState(null);

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

  const handleJoinLearning = (skillName) => {
    setSelectedSkill(skillName);
    setShowJoinModal(true);
  };

  const handleJoinSuccess = () => {
    setShowJoinModal(false);
    setSelectedSkill(null);
    navigate('/learning');
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
          {searchedSkill && (
            <div className="searched-skill-banner">
              🔍 Showing match for: <strong>{searchedSkill}</strong>
            </div>
          )}
          <div className="skills-list">
            {profile.skills && profile.skills.length > 0 ? (
              <div className="skills-grid">
                {profile.skills
                  .filter((skill) => {
                    // If there's a searched skill, only show matching skills
                    if (searchedSkill) {
                      return skill.name.toLowerCase().includes(searchedSkill.toLowerCase());
                    }
                    // Otherwise, show all skills
                    return true;
                  })
                  .map((skill) => (
                    <div 
                      key={skill.id} 
                      className="skill-card highlighted-skill"
                    >
                      <div className="skill-header">
                        <h4>{skill.name}</h4>
                        <span className="skill-level">{skill.proficiency_level}</span>
                      </div>
                      {skill.description && (
                        <p className="skill-description">{skill.description}</p>
                      )}
                      <button 
                        className="btn-join-skill"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleJoinLearning(skill.name);
                        }}
                      >
                        📚 Start Learning
                      </button>
                    </div>
                  ))}
              </div>
            ) : (
              <p>No skills listed.</p>
            )}
          </div>
        </section>

        <section className="learning-history-section">
          <h3>Learning Journey</h3>
          <SkillsLearnedTaught username={username} />
        </section>

        <section className="badges-section">
          <h3>🏆 Achievements & Badges</h3>
          <Badges username={username} />
        </section>

        <section className="ratings-section">
          <h3>Ratings & Feedback</h3>
          <UserRatings username={username} />
        </section>

        <section className="connect-section">
          <button className="button-primary" onClick={handleConnect} disabled={connecting}>
            {connecting ? 'Connecting...' : 'Get Connected'}
          </button>
        </section>
      </div>

      {/* Join Learning Modal */}
      {showJoinModal && (
        <div className="modal-overlay" onClick={() => setShowJoinModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setShowJoinModal(false)}>×</button>
            <JoinLearning
              teacherId={profile.user.id}
              teacherUsername={profile.user.username}
              skillName={selectedSkill}
              onSuccess={handleJoinSuccess}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default UserProfileView;
