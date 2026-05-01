import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './NotificationPopup.css';

const NotificationPopup = ({ notification, onClose, onMarkAsRead }) => {
  const navigate = useNavigate();
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    // Trigger animation
    setTimeout(() => setVisible(true), 10);

    // Auto-close after a short display period
    const timer = setTimeout(() => {
      handleClose();
    }, 3500);

    return () => clearTimeout(timer);
  }, []);

  const handleClose = () => {
    setVisible(false);
    setTimeout(() => onClose(), 300); // Wait for animation
  };

  const handleClick = () => {
    // Mark notification as read when clicked
    if (onMarkAsRead && !notification.read) {
      onMarkAsRead(notification.id);
    }
    if (notification.link) {
      navigate(notification.link);
    }
    handleClose();
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'message':
        return (
          <svg className="popup-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M7 9.5h10M7 13h7" />
            <path d="M5 5h14a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H9l-4 3v-3H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2Z" />
          </svg>
        );
      case 'connection_request':
        return (
          <svg className="popup-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <rect x="6" y="4" width="12" height="16" rx="2" />
            <path d="M9 8h6M9 12h6" />
          </svg>
        );
      case 'connection_accepted':
        return (
          <svg className="popup-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M12 3 5 6v6c0 5 3.4 8 7 9 3.6-1 7-4 7-9V6l-7-3Z" />
            <path d="m9 12 2 2 4-4" />
          </svg>
        );
      case 'skill_match':
        return (
          <svg className="popup-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="7" />
            <circle cx="12" cy="12" r="3" />
          </svg>
        );
      default:
        return (
          <svg className="popup-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M15 17H5.5a2.5 2.5 0 0 1 2-2.4V11a4.5 4.5 0 0 1 9 0v3.6a2.5 2.5 0 0 1 2 2.4H15Z" />
            <path d="M10.5 20a1.5 1.5 0 0 0 3 0" />
          </svg>
        );
    }
  };

  return (
    <div className={`notification-popup ${visible ? 'visible' : ''}`} onClick={handleClick}>
      <div className="popup-icon">
        {getNotificationIcon(notification.notification_type)}
      </div>
      <div className="popup-content">
        <div className="popup-title">{notification.title}</div>
        <div className="popup-message">{notification.message}</div>
      </div>
      <button className="popup-close" aria-label="Close notification" onClick={(e) => { e.stopPropagation(); handleClose(); }}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M18 6 6 18M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
};

export default NotificationPopup;
