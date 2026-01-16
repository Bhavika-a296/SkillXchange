import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';
import './Navbar.css';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [unreadCount, setUnreadCount] = useState(0);
  const [requestsCount, setRequestsCount] = useState(0);

  useEffect(() => {
    if (user) {
      fetchUnreadCount();
      fetchRequestsCount();
      // Poll for new notifications and requests every 30 seconds
      const interval = setInterval(() => {
        fetchUnreadCount();
        fetchRequestsCount();
      }, 30000);
      return () => clearInterval(interval);
    }
  }, [user]);

  const fetchUnreadCount = async () => {
    try {
      const { data } = await api.get('/notifications/unread/');
      setUnreadCount(data.unread_count);
    } catch (error) {
      console.error('Error fetching unread count:', error);
    }
  };

  const fetchRequestsCount = async () => {
    try {
      const { data } = await api.get('/learning/requests/');
      setRequestsCount(data.requests?.length || 0);
    } catch (error) {
      console.error('Error fetching requests count:', error);
    }
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/" className="navbar-logo">
          SkillXchange
        </Link>
      </div>
      <div className="navbar-menu">
        {user && <Link to="/learning" className="nav-link">🎓 Learning Hub</Link>}
        {user && (
          <Link to="/learning-requests" className="nav-link notification-link">
            <span className="notification-icon">📚</span>
            {requestsCount > 0 && (
              <span className="notification-badge requests-badge">{requestsCount > 99 ? '99+' : requestsCount}</span>
            )}
          </Link>
        )}
        {user && <Link to="/messages" className="nav-link">Messages</Link>}
        {user && (
          <Link to="/notifications" className="nav-link notification-link">
            <span className="notification-icon">🔔</span>
            {unreadCount > 0 && (
              <span className="notification-badge">{unreadCount > 99 ? '99+' : unreadCount}</span>
            )}
          </Link>
        )}
        {user ? (
          <>
            <div className="navbar-end">
              <Link to="/profile" className="nav-button">Profile</Link>
              <button 
                className="nav-button" 
                onClick={() => {
                  logout();
                  navigate('/');
                }}
              >
                Logout
              </button>
            </div>
          </>
        ) : (
          <div className="navbar-end">
            <Link to="/login" className="nav-link">Login</Link>
            <Link to="/register" className="nav-button">Register</Link>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;