import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './UserRatings.css';

const UserRatings = ({ username }) => {
  const [learnerRatings, setLearnerRatings] = useState({ ratings: [], average_rating: 0, total_ratings: 0 });
  const [teacherRatings, setTeacherRatings] = useState({ ratings: [], average_rating: 0, total_ratings: 0 });
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('teacher');

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const fetchRatings = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Token ${token}` };

      const [learnerResponse, teacherResponse] = await Promise.all([
        axios.get(
          `${API_BASE_URL}/api/learning/ratings/user/${username}/?as_learner=true`,
          { headers }
        ),
        axios.get(
          `${API_BASE_URL}/api/learning/ratings/user/${username}/?as_teacher=true`,
          { headers }
        )
      ]);

      setLearnerRatings(learnerResponse.data);
      setTeacherRatings(teacherResponse.data);
    } catch (error) {
      console.error('Error fetching ratings:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (username) {
      fetchRatings();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [username]);

  const renderStars = (rating) => {
    return (
      <div className="stars-display">
        {[1, 2, 3, 4, 5].map((star) => (
          <span key={star} className={`star ${star <= rating ? 'filled' : ''}`}>
            ★
          </span>
        ))}
      </div>
    );
  };

  const renderRatingCard = (rating) => (
    <div key={rating.id} className="rating-card">
      <div className="rating-header">
        <div className="rater-info">
          <strong>{rating.rater.username}</strong>
          <span className="skill-name">• {rating.learning_session.skill_name}</span>
        </div>
        {renderStars(rating.rating)}
      </div>
      {rating.feedback && (
        <p className="rating-feedback">{rating.feedback}</p>
      )}
      <div className="rating-footer">
        <small>{new Date(rating.created_at).toLocaleDateString()}</small>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="user-ratings-container">
        <p>Loading ratings...</p>
      </div>
    );
  }

  const currentRatings = activeTab === 'teacher' ? teacherRatings : learnerRatings;
  const hasRatings = currentRatings.total_ratings > 0;

  return (
    <div className="user-ratings-container">
      <div className="ratings-tabs">
        <button
          className={`tab-btn ${activeTab === 'teacher' ? 'active' : ''}`}
          onClick={() => setActiveTab('teacher')}
        >
          As Teacher ({teacherRatings.total_ratings})
        </button>
        <button
          className={`tab-btn ${activeTab === 'learner' ? 'active' : ''}`}
          onClick={() => setActiveTab('learner')}
        >
          As Learner ({learnerRatings.total_ratings})
        </button>
      </div>

      {hasRatings && (
        <div className="average-rating-section">
          <div className="avg-rating-display">
            <span className="avg-number">{currentRatings.average_rating}</span>
            {renderStars(Math.round(currentRatings.average_rating))}
            <span className="rating-count">({currentRatings.total_ratings} {currentRatings.total_ratings === 1 ? 'rating' : 'ratings'})</span>
          </div>
        </div>
      )}

      <div className="ratings-list">
        {hasRatings ? (
          currentRatings.ratings.map(renderRatingCard)
        ) : (
          <div className="no-ratings">
            <p>No ratings yet as {activeTab === 'teacher' ? 'teacher' : 'learner'}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserRatings;
