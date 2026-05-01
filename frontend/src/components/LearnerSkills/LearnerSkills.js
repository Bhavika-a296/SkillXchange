import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './LearnerSkills.css';

const LearnerSkills = ({ username }) => {
  const [learnedSkills, setLearnedSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isOwnProfile, setIsOwnProfile] = useState(false);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const fetchLearnedSkills = async () => {
      try {
        setLoading(true);
        setError('');
        const token = localStorage.getItem('token');
        const currentUser = JSON.parse(localStorage.getItem('user') || '{}');

        // Determine if this is the user's own profile
        setIsOwnProfile(currentUser.username === username);

        let response;
        if (currentUser.username === username) {
          // Own profile - get all attempts
          response = await axios.get(
            `${API_BASE_URL}/api/quiz/learner-verifications/`,
            {
              headers: { Authorization: `Token ${token}` }
            }
          );
        } else {
          // Other user's profile - only get verified skills
          response = await axios.get(
            `${API_BASE_URL}/api/quiz/learner-verifications/${username}/`,
            {
              headers: { Authorization: `Token ${token}` }
            }
          );
        }

        const skills = response.data.learned_skills || [];
        setLearnedSkills(skills);
      } catch (err) {
        console.error('Error fetching learned skills:', err);
        // Don't show error if 404 - just means no skills learned yet
        if (err.response?.status !== 404) {
          setError('Error loading learned skills');
        }
      } finally {
        setLoading(false);
      }
    };

    if (username) {
      fetchLearnedSkills();
    }
  }, [username]);

  if (loading) {
    return (
      <div className="learner-skills-container">
        <div className="loading">Loading learned skills...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="learner-skills-container">
        <div className="error">{error}</div>
      </div>
    );
  }

  if (learnedSkills.length === 0) {
    return (
      <div className="learner-skills-container">
        <div className="empty-state">
          <p>{isOwnProfile ? 'No skills learned yet. Complete a learning session and pass the quiz!' : 'No skills learned yet.'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="learner-skills-container">
      <div className="skills-section">
        <h3 className="section-title">✓ Skills Learned</h3>
        <div className="skills-grid">
          {learnedSkills.map((skill) => (
            <div key={skill.skill_name} className="skill-badge-learned">
              <div className="skill-header">
                <h4>{skill.skill_name}</h4>
                <span className="verified-badge">✓</span>
              </div>
              <div className="skill-score">Score: {skill.score}%</div>
              {skill.verified_date && (
                <div className="skill-date">
                  Verified: {new Date(skill.verified_date).toLocaleDateString()}
                </div>
              )}
              {isOwnProfile && skill.status === 'failed' && (
                <div className="skill-status">Not yet verified</div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default LearnerSkills;
