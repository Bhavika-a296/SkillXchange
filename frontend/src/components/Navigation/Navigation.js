import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './Navigation.css';

const Navigation = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navigation">
      <div className="nav-brand">
        <Link to="/" className="brand">SkillXchange</Link>
      </div>
      <div className="nav-items">
        {isAuthenticated ? (
          <>
            <div className="user-profile">
              <span className="username">{user?.username}</span>
              <div className="dropdown-content">
                <Link to="/profile" className="dropdown-item">My Profile</Link>
                <Link to="/skills" className="dropdown-item">My Skills</Link>
                <Link to="/resume" className="dropdown-item">My Resume</Link>
                <button onClick={handleLogout} className="dropdown-item logout-btn">
                  Logout
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="auth-buttons">
            <Link to="/login" className="nav-button">Login</Link>
            <Link to="/register" className="nav-button register">Register</Link>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navigation;