import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import './VerificationBadges.css';

const VerificationBadges = ({ username, isOwnProfile = false }) => {
  const [verifications, setVerifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchVerifications = async () => {
      try {
        setLoading(true);
        const endpoint = isOwnProfile 
          ? '/quiz/teacher-verifications/'
          : `/quiz/teacher-verifications/${username}/`;
        
        const res = await api.get(endpoint);
        const verifiedSkills = (res.data.verified_skills || []).filter((skill) => skill.is_verified !== false);
        setVerifications(verifiedSkills);
      } catch (err) {
        // Silently fail if no verifications exist
        setVerifications([]);
      } finally {
        setLoading(false);
      }
    };

    fetchVerifications();
  }, [username, isOwnProfile]);

  if (loading) {
    return <div className="verifications-loading">Loading verifications...</div>;
  }

  if (!verifications || verifications.length === 0) {
    return (
      <div className="verifications-empty">
        {isOwnProfile ? (
          <>
            <p>No teacher verified skills yet</p>
            <a href="/quiz" className="verification-link">
              Take a quiz to get verified
            </a>
          </>
        ) : (
          <p>No teacher verified skills</p>
        )}
      </div>
    );
  }

  return (
    <div className="verifications-container">
      <h3 className="verifications-title">
        <span className="verification-title-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 3 5 6v6c0 5 3.4 8 7 9 3.6-1 7-4 7-9V6l-7-3Z" />
            <path d="m9 12 2 2 4-4" />
          </svg>
        </span>
        Teacher Verified Skills ({verifications.length})
      </h3>
      <div className="badges-list">
        {verifications.map((v) => (
          <div key={v.skill_name} className="verification-badge">
            <span className="badge-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 3 5 6v6c0 5 3.4 8 7 9 3.6-1 7-4 7-9V6l-7-3Z" />
                <path d="m9 12 2 2 4-4" />
              </svg>
            </span>
            <div className="badge-content">
              <span className="badge-skill">{v.skill_name}</span>
              <span className="badge-score">{v.score}%</span>
              {v.verified_date && (
                <span className="badge-date">{v.verified_date}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default VerificationBadges;
