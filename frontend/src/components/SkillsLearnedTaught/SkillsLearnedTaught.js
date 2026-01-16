import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './SkillsLearnedTaught.css';

const SkillsLearnedTaught = ({ username }) => {
  const [skillsLearned, setSkillsLearned] = useState([]);
  const [skillsTaught, setSkillsTaught] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('learned');

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const fetchSkills = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Token ${token}` };

      const [learnedResponse, taughtResponse] = await Promise.all([
        axios.get(
          `${API_BASE_URL}/api/learning/skills-learned/${username ? username + '/' : ''}`,
          { headers }
        ),
        axios.get(
          `${API_BASE_URL}/api/learning/skills-taught/${username ? username + '/' : ''}`,
          { headers }
        )
      ]);

      setSkillsLearned(learnedResponse.data);
      setSkillsTaught(taughtResponse.data);
    } catch (error) {
      console.error('Error fetching skills:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSkills();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [username]);

  const renderSkillCard = (session, type) => {
    const otherUser = type === 'learned' ? session.teacher : session.learner;
    const endDate = new Date(session.end_date).toLocaleDateString();

    return (
      <div key={session.id} className="skill-card">
        <div className="skill-card-header">
          <h4 className="skill-card-title">{session.skill_name}</h4>
          <span className="skill-card-badge">{type === 'learned' ? '📚' : '🎓'}</span>
        </div>
        <div className="skill-card-body">
          <p className="skill-card-user">
            {type === 'learned' ? 'Learned from' : 'Taught to'}: 
            <a href={`/profile/${otherUser.username}`} className="user-link">
              {otherUser.username}
            </a>
          </p>
          <p className="skill-card-date">Completed: {endDate}</p>
          <p className="skill-card-duration">Duration: {session.total_days} days</p>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="skills-section">
        <div className="loading-spinner">Loading...</div>
      </div>
    );
  }

  return (
    <div className="skills-section">
      <div className="skills-tabs">
        <button
          className={`tab-button ${activeTab === 'learned' ? 'active' : ''}`}
          onClick={() => setActiveTab('learned')}
        >
          Skills Learned ({skillsLearned.length})
        </button>
        <button
          className={`tab-button ${activeTab === 'taught' ? 'active' : ''}`}
          onClick={() => setActiveTab('taught')}
        >
          Skills Taught ({skillsTaught.length})
        </button>
      </div>

      <div className="skills-content">
        {activeTab === 'learned' && (
          <div className="skills-grid">
            {skillsLearned.length > 0 ? (
              skillsLearned.map(session => renderSkillCard(session, 'learned'))
            ) : (
              <div className="empty-state">
                <p>No skills learned yet</p>
                <small>Complete learning sessions to see them here</small>
              </div>
            )}
          </div>
        )}

        {activeTab === 'taught' && (
          <div className="skills-grid">
            {skillsTaught.length > 0 ? (
              skillsTaught.map(session => renderSkillCard(session, 'taught'))
            ) : (
              <div className="empty-state">
                <p>No skills taught yet</p>
                <small>Help others learn to see them here</small>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default SkillsLearnedTaught;
