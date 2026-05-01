import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import './Badges.css';

const Badges = ({ username }) => {
  const [badges, setBadges] = useState([]);
  const [loading, setLoading] = useState(true);

  const renderBadgeIcon = (badgeName = '') => {
    const name = badgeName.toLowerCase();

    if (name.includes('mentor') || name.includes('teacher')) {
      return (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M12 3 5 6v6c0 5 3.4 8 7 9 3.6-1 7-4 7-9V6l-7-3Z" />
          <path d="m9 12 2 2 4-4" />
        </svg>
      );
    }

    if (name.includes('streak') || name.includes('consisten')) {
      return (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M12 2v5" />
          <path d="m15.5 4.5-2.2 2.2" />
          <path d="m8.5 4.5 2.2 2.2" />
          <path d="M6.5 10.5c0-3 2.5-5.5 5.5-5.5s5.5 2.5 5.5 5.5c0 4.5-5.5 5-5.5 11 0-6.1-5.5-6.5-5.5-11Z" />
        </svg>
      );
    }

    return (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <circle cx="12" cy="8" r="3" />
        <path d="M8 11H5v9l3-2 4 2 4-2 3 2v-9h-3" />
      </svg>
    );
  };

  useEffect(() => {
    fetchBadges();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [username]);

  const fetchBadges = async () => {
    try {
      setLoading(true);
      const endpoint = username 
        ? `/learning/badges/${username}/`
        : `/learning/badges/`;
      
      const response = await api.get(endpoint);
      console.log('Badges API response:', response.data); // Debug log
      setBadges(response.data.badges || []);
    } catch (error) {
      console.error('Error fetching badges:', error);
      console.error('Error details:', error.response?.data); // Debug log
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="badges-loading">Loading badges...</div>;
  }

  if (badges.length === 0) {
    return (
      <div className="badges-empty">
        <div className="empty-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="8" r="3" />
            <path d="M8 11H5v9l3-2 4 2 4-2 3 2v-9h-3" />
          </svg>
        </div>
        <p>No badges earned yet</p>
        <small>Complete learning sessions to earn badges!</small>
      </div>
    );
  }

  return (
    <div className="badges-container">
      <div className="badges-grid">
        {badges.map((badge) => (
          <div key={badge.id} className="badge-card">
            <div className="badge-icon">{renderBadgeIcon(badge.badge_name)}</div>
            <div className="badge-name">{badge.badge_name}</div>
            <div className="badge-date">
              {new Date(badge.earned_at).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Badges;
