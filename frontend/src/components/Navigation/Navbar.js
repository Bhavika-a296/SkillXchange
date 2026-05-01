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

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/" className="navbar-logo">
          SkillXchange
        </Link>
      </div>
      <div className="navbar-menu">
        {user && (
          <Link to="/learning" className="nav-link">
            <span className="nav-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5v-15Z" />
                <path d="M8 7h8M8 11h8" />
              </svg>
            </span>
            Learning Hub
          </Link>
        )}
        {user && (
          <Link to="/leaderboard" className="nav-link">
            <span className="nav-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 20h16" />
                <rect x="6" y="10" width="3" height="8" rx="1" />
                <rect x="11" y="7" width="3" height="11" rx="1" />
                <rect x="16" y="4" width="3" height="14" rx="1" />
              </svg>
            </span>
            Leaderboard
          </Link>
        )}
        {user && (
          <Link to="/quiz" className="nav-link">
            <span className="nav-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 3 5 6v6c0 5 3.4 8 7 9 3.6-1 7-4 7-9V6l-7-3Z" />
                <path d="m9 12 2 2 4-4" />
              </svg>
            </span>
            Verify Skills
          </Link>
        )}
        {user && (
          <Link to="/learning-requests" className="nav-link notification-link">
            <span className="notification-icon" aria-hidden="true">
              <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <rect x="6" y="4" width="12" height="16" rx="2" />
                <path d="M9 8h6M9 12h6" />
              </svg>
            </span>
            {requestsCount > 0 && (
              <span className="notification-badge requests-badge">{requestsCount > 99 ? '99+' : requestsCount}</span>
            )}
          </Link>
        )}
        {user && <Link to="/messages" className="nav-link">Messages</Link>}
        {user && (
          <Link to="/notifications" className="nav-link notification-link">
            <span className="notification-icon" aria-hidden="true">
              <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d="M15 17H5.5a2.5 2.5 0 0 1 2-2.4V11a4.5 4.5 0 0 1 9 0v3.6a2.5 2.5 0 0 1 2 2.4H15Z" />
                <path d="M10.5 20a1.5 1.5 0 0 0 3 0" />
              </svg>
            </span>
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
                onClick={handleLogout}
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