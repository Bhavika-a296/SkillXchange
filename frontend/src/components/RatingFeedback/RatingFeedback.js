import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './RatingFeedback.css';

const RatingFeedback = ({ sessionId, onSubmitSuccess }) => {
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [feedback, setFeedback] = useState('');
  const [loading, setLoading] = useState(false);
  const [session, setSession] = useState(null);
  const [canRate, setCanRate] = useState(false);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchSessionDetails();
    checkCanRate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  const fetchSessionDetails = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_BASE_URL}/api/learning/sessions/${sessionId}/`,
        {
          headers: { Authorization: `Token ${token}` }
        }
      );
      setSession(response.data);
    } catch (error) {
      console.error('Error fetching session details:', error);
    }
  };

  const checkCanRate = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_BASE_URL}/api/learning/can-rate/${sessionId}/`,
        {
          headers: { Authorization: `Token ${token}` }
        }
      );
      setCanRate(response.data.can_rate);
    } catch (error) {
      console.error('Error checking rating status:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (rating === 0) {
      alert('Please select a rating');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_BASE_URL}/api/learning/rate/${sessionId}/`,
        {
          rating,
          feedback
        },
        {
          headers: { Authorization: `Token ${token}` }
        }
      );

      alert('Rating submitted successfully!');
      if (onSubmitSuccess) {
        onSubmitSuccess();
      }
    } catch (error) {
      console.error('Error submitting rating:', error);
      alert(error.response?.data?.error || 'Failed to submit rating');
    } finally {
      setLoading(false);
    }
  };

  if (!canRate) {
    return (
      <div className="rating-feedback-container">
        <div className="cannot-rate-message">
          <p>You cannot rate this session at this time.</p>
          <small>
            {session?.status !== 'completed' 
              ? 'Session must be completed first.' 
              : 'You have already rated this session.'}
          </small>
        </div>
      </div>
    );
  }

  const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
  const isLearner = session && session.learner.id === currentUser.id;
  const otherUser = session ? (isLearner ? session.teacher : session.learner) : null;

  return (
    <div className="rating-feedback-container">
      <div className="rating-feedback-header">
        <h3>Rate Your Experience</h3>
        {session && otherUser && (
          <p className="session-info">
            {isLearner ? 'Learning' : 'Teaching'} <strong>{session.skill_name}</strong> 
            {isLearner ? ' from ' : ' to '} 
            <strong>{otherUser.username}</strong>
          </p>
        )}
      </div>

      <form onSubmit={handleSubmit} className="rating-form">
        <div className="rating-stars-section">
          <label>Your Rating:</label>
          <div className="stars-container">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                className={`star ${star <= (hoveredRating || rating) ? 'filled' : ''}`}
                onClick={() => setRating(star)}
                onMouseEnter={() => setHoveredRating(star)}
                onMouseLeave={() => setHoveredRating(0)}
              >
                ★
              </button>
            ))}
          </div>
          {rating > 0 && (
            <p className="rating-text">
              {rating === 1 && 'Poor'}
              {rating === 2 && 'Fair'}
              {rating === 3 && 'Good'}
              {rating === 4 && 'Very Good'}
              {rating === 5 && 'Excellent'}
            </p>
          )}
        </div>

        <div className="feedback-section">
          <label htmlFor="feedback">Feedback (optional):</label>
          <textarea
            id="feedback"
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="Share your experience..."
            rows="5"
            className="feedback-textarea"
          />
        </div>

        <button
          type="submit"
          className="btn-submit-rating"
          disabled={loading || rating === 0}
        >
          {loading ? 'Submitting...' : 'Submit Rating'}
        </button>
      </form>
    </div>
  );
};

export default RatingFeedback;
