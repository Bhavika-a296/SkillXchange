import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import './LearningRequests.css';

const LearningRequests = () => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    fetchRequests();
  }, []);

  const fetchRequests = async () => {
    try {
      setLoading(true);
      const response = await api.get('/learning/requests/');
      setRequests(response.data.requests);
      setError(null);
    } catch (err) {
      console.error('Error fetching learning requests:', err);
      setError('Failed to load learning requests');
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async (requestId) => {
    try {
      setActionLoading(prev => ({ ...prev, [requestId]: 'accepting' }));
      const response = await api.post(`/learning/requests/${requestId}/accept/`);
      
      // Show success message
      alert(response.data.message);
      
      // Remove the request from the list
      setRequests(prev => prev.filter(req => req.id !== requestId));
      
      // Refresh requests
      fetchRequests();
    } catch (err) {
      console.error('Error accepting request:', err);
      alert(err.response?.data?.error || 'Failed to accept request');
    } finally {
      setActionLoading(prev => ({ ...prev, [requestId]: null }));
    }
  };

  const handleReject = async (requestId) => {
    try {
      setActionLoading(prev => ({ ...prev, [requestId]: 'rejecting' }));
      const response = await api.post(`/learning/requests/${requestId}/reject/`);
      
      // Show success message
      alert(response.data.message);
      
      // Remove the request from the list
      setRequests(prev => prev.filter(req => req.id !== requestId));
      
      // Refresh requests
      fetchRequests();
    } catch (err) {
      console.error('Error rejecting request:', err);
      alert(err.response?.data?.error || 'Failed to reject request');
    } finally {
      setActionLoading(prev => ({ ...prev, [requestId]: null }));
    }
  };

  const handleViewProfile = (username) => {
    navigate(`/profile/${username}`);
  };

  if (loading) {
    return (
      <div className="learning-requests-container">
        <div className="loading-spinner">Loading requests...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="learning-requests-container">
        <div className="error-message">{error}</div>
        <button onClick={fetchRequests} className="btn btn-primary">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="learning-requests-container">
      <h1 className="page-title">Learning Requests</h1>
      <p className="page-subtitle">
        Students who want to learn from you
      </p>

      {requests.length === 0 ? (
        <div className="no-requests">
          <div className="no-requests-icon">📫</div>
          <h3>No pending requests</h3>
          <p>You don't have any learning requests at the moment.</p>
        </div>
      ) : (
        <div className="requests-grid">
          {requests.map((request) => (
            <div key={request.id} className="request-card">
              <div className="request-header">
                <div className="learner-info">
                  <div
                    className="learner-avatar"
                    onClick={() => handleViewProfile(request.learner?.username)}
                  >
                    {request.learner?.username?.charAt(0).toUpperCase() || '?'}
                  </div>
                  <div className="learner-details">
                    <h3
                      className="learner-name"
                      onClick={() => handleViewProfile(request.learner?.username)}
                    >
                      {request.learner?.username || 'Unknown'}
                    </h3>
                    <p className="request-date">
                      {new Date(request.created_at).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                </div>
              </div>

              <div className="request-body">
                <div className="skill-badge">{request.skill_name}</div>
                <div className="request-info">
                  <div className="info-item">
                    <span className="info-label">Duration:</span>
                    <span className="info-value">{request.total_days} days</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Points (from learner):</span>
                    <span className="info-value points-highlight">
                      -{request.points_deducted || 100}
                    </span>
                  </div>
                </div>
              </div>

              <div className="request-actions">
                <button
                  className="btn btn-accept"
                  onClick={() => handleAccept(request.id)}
                  disabled={actionLoading[request.id]}
                >
                  {actionLoading[request.id] === 'accepting' ? (
                    <>
                      <span className="spinner-small"></span>
                      Accepting...
                    </>
                  ) : (
                    <>
                      <span className="icon">✓</span>
                      Accept
                    </>
                  )}
                </button>
                <button
                  className="btn btn-reject"
                  onClick={() => handleReject(request.id)}
                  disabled={actionLoading[request.id]}
                >
                  {actionLoading[request.id] === 'rejecting' ? (
                    <>
                      <span className="spinner-small"></span>
                      Rejecting...
                    </>
                  ) : (
                    <>
                      <span className="icon">✕</span>
                      Reject
                    </>
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default LearningRequests;
