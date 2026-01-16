import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import './Badges.css';

const Badges = ({ username }) => {
  const [badges, setBadges] = useState([]);
  const [loading, setLoading] = useState(true);

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
        <div className="empty-icon">🏅</div>
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
            <div className="badge-icon">{badge.icon}</div>
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
