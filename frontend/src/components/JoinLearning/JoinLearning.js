import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './JoinLearning.css';
import PointAnimation from '../PointAnimation/PointAnimation';

const JoinLearning = ({ teacherId, teacherUsername, skillName, onSuccess }) => {
  const [totalDays, setTotalDays] = useState(30);
  const [loading, setLoading] = useState(false);
  const [userPoints, setUserPoints] = useState(null);
  const [showAnimation, setShowAnimation] = useState(false);
  const [animationPoints, setAnimationPoints] = useState(0);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const fetchUserPoints = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_BASE_URL}/api/learning/points/`,
        {
          headers: { Authorization: `Token ${token}` }
        }
      );
      setUserPoints(response.data);
    } catch (error) {
      console.error('Error fetching user points:', error);
    }
  };

  useEffect(() => {
    fetchUserPoints();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleJoinLearning = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_BASE_URL}/api/learning/join/`,
        {
          teacher_id: teacherId,
          skill_name: skillName,
          total_days: totalDays
        },
        {
          headers: { Authorization: `Token ${token}` }
        }
      );

      // Check if it's a pending request (new flow) or accepted (old sessions)
      if (response.data.learning_session?.status === 'pending') {
        // Request sent successfully, show success message
        alert(`✓ ${response.data.message}\n\nPoints will be deducted when ${teacherUsername} accepts your request.`);
        
        // Notify parent component
        if (onSuccess) {
          onSuccess(response.data.learning_session);
        }
      } else {
        // Old flow - points deducted immediately (shouldn't happen anymore)
        setAnimationPoints(-response.data.points_deducted);
        setShowAnimation(true);

        // Update points display
        setUserPoints(prev => ({
          ...prev,
          balance: response.data.new_balance
        }));

        // Notify parent component
        if (onSuccess) {
          setTimeout(() => {
            onSuccess(response.data.learning_session);
          }, 2000);
        }
      }
    } catch (error) {
      console.error('Error joining learning session:', error);
      alert(error.response?.data?.error || 'Failed to send learning request');
    } finally {
      setLoading(false);
    }
  };

  const joinCost = 100; // Should be fetched from backend config

  return (
    <>
      <div className="join-learning-container">
        <div className="join-learning-header">
          <h3>Start Learning</h3>
          {userPoints && (
            <div className="user-points-display">
              <span className="points-icon">💰</span>
              <span className="points-value">{userPoints.balance}</span>
              <span className="points-label">points</span>
            </div>
          )}
        </div>

        <div className="join-learning-info">
          <div className="info-row">
            <span className="info-label">Teacher:</span>
            <span className="info-value">{teacherUsername}</span>
          </div>
          <div className="info-row">
            <span className="info-label">Skill:</span>
            <span className="info-value">{skillName}</span>
          </div>
          <div className="info-row">
            <span className="info-label">Cost:</span>
            <span className="info-value cost">{joinCost} points</span>
          </div>
        </div>

        <div className="learning-duration">
          <label htmlFor="total-days">Learning Duration (days):</label>
          <input
            id="total-days"
            type="number"
            min="1"
            max="365"
            value={totalDays}
            onChange={(e) => setTotalDays(parseInt(e.target.value) || 1)}
            className="duration-input"
          />
        </div>

        {userPoints && userPoints.balance < joinCost && (
          <div className="insufficient-points-warning">
            ⚠️ Insufficient points. You need {joinCost - userPoints.balance} more points.
          </div>
        )}

        <button
          className="btn-join-learning"
          onClick={handleJoinLearning}
          disabled={loading || (userPoints && userPoints.balance < joinCost)}
        >
          {loading ? 'Sending Request...' : 'Send Learning Request'}
        </button>

        <div className="join-learning-note">
          <small>
            💡 The teacher will receive your request. Points ({joinCost}) will be deducted when they accept.
          </small>
        </div>
      </div>

      {showAnimation && (
        <PointAnimation
          points={animationPoints}
          type="deduct"
          onComplete={() => setShowAnimation(false)}
        />
      )}
    </>
  );
};

export default JoinLearning;
