import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './SkillsLearnedTaught.css';

const SkillsLearnedTaught = ({ username }) => {
  const [skillsTaught, setSkillsTaught] = useState([]);
  const [loading, setLoading] = useState(true);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const fetchSkills = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Token ${token}` };

      const taughtResponse = await axios.get(
        `${API_BASE_URL}/api/learning/skills-taught/${username ? username + '/' : ''}`,
        { headers }
      );

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
          <span className="skill-card-badge" aria-hidden="true">
            {type === 'learned' ? (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <rect x="6" y="4" width="12" height="16" rx="2" />
                <path d="M9 8h6M9 12h6" />
              </svg>
            ) : (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 6.5 12 3l9 3.5L12 10 3 6.5Z" />
                <path d="M6 8v4.5c0 1.7 2.7 3 6 3s6-1.3 6-3V8" />
              </svg>
            )}
          </span>
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
      <div className="skills-header">
        <h4>Skills Taught ({skillsTaught.length})</h4>
      </div>

      <div className="skills-content">
        <div className="skills-grid">
          {skillsTaught.length > 0 ? (
            skillsTaught.map((session) => renderSkillCard(session, 'taught'))
          ) : (
            <div className="empty-state">
              <p>No skills taught yet</p>
              <small>Help others learn to see them here</small>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SkillsLearnedTaught;
