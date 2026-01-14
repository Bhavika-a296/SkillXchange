import React, { useState } from 'react';
import { skillsApi } from '../../services/api';
import './SkillMatch.css';

const SkillMatch = ({ skills }) => {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const findMatches = async () => {
    if (!skills || skills.length === 0) {
      setError('Please add some skills to your profile first');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await skillsApi.findMatches(skills);
      // backend returns { matches: [...] }
      setMatches(response.data.matches || []);
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred while finding matches');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="skill-match">
      <h2>Find Skill Matches</h2>
      {error && <div className="error-message">{error}</div>}

      <div className="skills-list">
        <h3>Your Skills:</h3>
        {skills && skills.length > 0 ? (
      <div className="skills-tags">
            {skills.map((skill, index) => (
              <span key={index} className="skill-tag">{typeof skill === 'object' ? skill.name : skill}</span>
            ))}
          </div>
        ) : (
          <p>No skills added yet. Upload your resume or add skills to your profile to find matches.</p>
        )}
      </div>

      <button 
        onClick={findMatches}
        className="match-button"
        disabled={loading || !skills || skills.length === 0}
      >
        {loading ? 'Finding Matches...' : 'Find Matches'}
      </button>

      {matches.length > 0 && (
        <div className="matches-container">
          <h3>Top Matches</h3>
          <div className="matches-list">
            {matches.map((match, index) => (
              <div key={index} className="match-card">
                <div className="match-header">
                  <h4>{match.username}</h4>
                  <span className="match-score">
                    {Math.round(match.match_score * 100)}% Match
                  </span>
                </div>
                <div className="matching-skills">
                  <h5>Matching Skills:</h5>
                  <div className="skills-tags">
                    {match.matching_skills.map((skill, idx) => (
                      <span key={idx} className="skill-tag">{skill}</span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {matches.length === 0 && !loading && (
        <div className="no-matches">
          <p>Click "Find Matches" to discover users with similar skills.</p>
        </div>
      )}
    </div>
  );
};

export default SkillMatch;