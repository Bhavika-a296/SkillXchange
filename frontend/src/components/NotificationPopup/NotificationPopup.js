import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './NotificationPopup.css';

const NotificationPopup = ({ notification, onClose, onMarkAsRead }) => {
  const navigate = useNavigate();
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    // Trigger animation
    setTimeout(() => setVisible(true), 10);

    // Auto-close after 5 seconds
    const timer = setTimeout(() => {
      handleClose();
    }, 5000);

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
        return '💬';
      case 'connection_request':
        return '👥';
      case 'connection_accepted':
        return '✅';
      case 'skill_match':
        return '🎯';
      default:
        return '🔔';
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
      <button className="popup-close" onClick={(e) => { e.stopPropagation(); handleClose(); }}>
        ✕
      </button>
    </div>
  );
};

export default NotificationPopup;
