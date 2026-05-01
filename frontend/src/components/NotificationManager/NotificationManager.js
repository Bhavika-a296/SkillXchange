import React, { useEffect, useRef, useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useRealtime } from '../../contexts/RealtimeContext';
import api from '../../services/api';
import NotificationPopup from '../NotificationPopup/NotificationPopup';

const NotificationManager = () => {
  const { user } = useAuth();
  const { ably } = useRealtime();
  const [popupNotifications, setPopupNotifications] = useState([]);
  const seenNotificationKeysRef = useRef(new Set());

  const getNotificationKey = (notification) => {
    if (!notification) return null;
    return notification.id
      ? `id:${notification.id}`
      : `${notification.notification_type || 'unknown'}:${notification.title || ''}:${notification.message || ''}:${notification.created_at || ''}`;
  };

  useEffect(() => {
    if (!ably || !user) return;

    // Subscribe to user's notification channel
    const channel = ably.channels.get(`notifications-${user.id}`);
    
    channel.subscribe('new-notification', (message) => {
      const notification = message.data;
      showPopupNotification(notification);
    });

    return () => {
      channel.unsubscribe();
    };
  }, [ably, user]);

  // Also poll for new notifications every 30 seconds as fallback
  useEffect(() => {
    if (!user) return;

    let lastCheckTime = new Date();

    const checkForNewNotifications = async () => {
      try {
        const { data } = await api.get('/notifications/', {
          params: {
            created_at__gt: lastCheckTime.toISOString()
          }
        });
        
        if (data.length > 0) {
          data.forEach(notification => {
            if (!notification.read) {
              showPopupNotification(notification);
            }
          });
          lastCheckTime = new Date();
        }
      } catch (error) {
        console.error('Error checking for notifications:', error);
      }
    };

    const interval = setInterval(checkForNewNotifications, 30000);
    return () => clearInterval(interval);
  }, [user]);

  const showPopupNotification = (notification) => {
    const normalizedNotification = {
      ...notification,
      id: notification.id || Date.now(),
    };
    const notificationKey = getNotificationKey(normalizedNotification);

    if (notificationKey && seenNotificationKeysRef.current.has(notificationKey)) {
      return;
    }

    if (notificationKey) {
      seenNotificationKeysRef.current.add(notificationKey);
    }

    setPopupNotifications((prev) => {
      if (prev.some((item) => getNotificationKey(item) === notificationKey)) {
        return prev;
      }

      return [...prev, normalizedNotification];
    });
  };

  const removePopupNotification = (id) => {
    setPopupNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  const markNotificationAsRead = async (notificationId) => {
    try {
      await api.post(`/notifications/${notificationId}/mark_read/`);
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  return (
    <div className="notification-manager">
      {popupNotifications.length > 0 && (
        <NotificationPopup
          key={popupNotifications[0].id}
          notification={popupNotifications[0]}
          onClose={() => removePopupNotification(popupNotifications[0].id)}
          onMarkAsRead={markNotificationAsRead}
        />
      )}
    </div>
  );
};

export default NotificationManager;
