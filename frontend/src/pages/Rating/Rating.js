import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import RatingFeedback from '../../components/RatingFeedback/RatingFeedback';
import './Rating.css';

const Rating = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();

  const handleSubmitSuccess = () => {
    // Navigate back to learning page after successful submission
    navigate('/learning');
  };

  return (
    <div className="rating-page">
      <div className="rating-container">
        <button className="back-button" onClick={() => navigate('/learning')}>
          ← Back to Learning
        </button>
        <RatingFeedback 
          sessionId={parseInt(sessionId)} 
          onSubmitSuccess={handleSubmitSuccess}
        />
      </div>
    </div>
  );
};

export default Rating;
