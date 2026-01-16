import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import './LearningSession.css';
import PointAnimation from '../PointAnimation/PointAnimation';

const LearningSession = ({ session, onUpdate }) => {
  const [showAnimation, setShowAnimation] = useState(false);
  const [animationPoints, setAnimationPoints] = useState(0);
  const [loading, setLoading] = useState(false);
  const [canRate, setCanRate] = useState(false);
  const { user: currentUser } = useAuth();

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const checkCanRate = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_BASE_URL}/api/learning/can-rate/${session.id}/`,
        {
          headers: { Authorization: `Token ${token}` }
        }
      );
      setCanRate(response.data.can_rate);
    } catch (error) {
      console.error('Error checking rating status:', error);
    }
  };

  useEffect(() => {
    if (session.status === 'completed') {
      checkCanRate();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session.status]);

  const handleEndLearning = async () => {
    if (!window.confirm('Are you sure you want to complete this learning session?')) {
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_BASE_URL}/api/learning/end/${session.id}/`,
        {},
        {
          headers: { Authorization: `Token ${token}` }
        }
      );

      // Show animation for points earned
      const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
      const isLearner = session.learner.id === currentUser.id;
      const pointsEarned = isLearner 
        ? response.data.learner_reward 
        : response.data.teacher_reward;

      setAnimationPoints(pointsEarned);
      setShowAnimation(true);

      // Update parent component
      if (onUpdate) {
        onUpdate();
      }
    } catch (error) {
      console.error('Error ending learning session:', error);
      alert(error.response?.data?.error || 'Failed to end learning session');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeClass = () => {
    switch (session.status) {
      case 'in_progress':
        return 'status-badge in-progress';
      case 'completed':
        return 'status-badge completed';
      case 'cancelled':
        return 'status-badge cancelled';
      case 'pending':
        return 'status-badge pending';
      case 'rejected':
        return 'status-badge rejected';
      default:
        return 'status-badge';
    }
  };

  const getStatusText = () => {
    switch (session.status) {
      case 'in_progress':
        return 'In Progress';
      case 'completed':
        return 'Completed';
      case 'cancelled':
        return 'Cancelled';
      case 'pending':
        return 'Pending Approval';
      case 'rejected':
        return 'Rejected';
      default:
        return session.status;
    }
  };

  if (!currentUser) {
    return null;
  }

  const isLearner = session.learner?.id === currentUser.user?.id || session.learner?.username === currentUser.user?.username;
  const otherUser = isLearner ? session.teacher : session.learner;
  
  // Determine role text based on status
  const getRoleText = () => {
    if (session.status === 'completed') {
      return isLearner ? 'Taught by' : 'Taught to';
    }
    return isLearner ? 'Learning from' : 'Teaching';
  };

  return (
    <>
      <div className="learning-session-card">
        <div className="session-header">
          <h3 className="skill-name">{session.skill_name}</h3>
          <span className={getStatusBadgeClass()}>{getStatusText()}</span>
        </div>

        <div className="session-info">
          <p className="session-role">
            {session.status === 'completed' ? (
              <>
                {getRoleText()} <strong>{otherUser.username}</strong>
              </>
            ) : (
              <>
                {getRoleText()}: <strong>{otherUser.username}</strong>
              </>
            )}
          </p>

          {session.status === 'in_progress' && (
            <>
              <div className="progress-section">
                <div className="progress-header">
                  <span>Progress: {session.progress_percentage}%</span>
                  <span className="days-remaining">
                    {session.days_remaining} days remaining
                  </span>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${session.progress_percentage}%` }}
                  />
                </div>
              </div>

              <div className="session-actions">
                <button
                  className="btn-end-learning"
                  onClick={handleEndLearning}
                  disabled={loading}
                >
                  {loading ? 'Completing...' : 'Complete Learning'}
                </button>
              </div>
            </>
          )}

          {session.status === 'completed' && (
            <div className="completion-info">
              <p className="completion-date">
                Completed on {new Date(session.end_date).toLocaleDateString()}
              </p>
              {session.points_awarded_learner && (
                <p className="points-earned">
                  Points earned: {isLearner ? session.points_awarded_learner : session.points_awarded_teacher}
                </p>
              )}
              {canRate && (
                <button 
                  className="btn-rate"
                  onClick={() => window.location.href = `/rate-session/${session.id}`}
                >
                  Rate & Give Feedback
                </button>
              )}
            </div>
          )}
        </div>

        <div className="session-footer">
          <small>Started: {new Date(session.start_date).toLocaleDateString()}</small>
          {session.status === 'in_progress' && (
            <small>Total duration: {session.total_days} days</small>
          )}
        </div>
      </div>

      {showAnimation && (
        <PointAnimation
          points={animationPoints}
          type="earn"
          onComplete={() => setShowAnimation(false)}
        />
      )}
    </>
  );
};

export default LearningSession;
