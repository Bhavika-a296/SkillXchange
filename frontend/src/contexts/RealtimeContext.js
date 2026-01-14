import React, { createContext, useContext, useEffect, useState } from 'react';
import { Realtime } from 'ably';
import { useAuth } from './AuthContext';
import api from '../services/api';

const RealtimeContext = createContext();

export const RealtimeProvider = ({ children }) => {
  const [ably, setAbly] = useState(null);
  const { user } = useAuth();

  useEffect(() => {
    const setupAbly = async () => {
      if (user) {
        try {
          // Get token from backend
          const response = await api.get('realtime/token/');
          const { token } = response.data;

          // Initialize Ably with the token
          const ablyClient = new Realtime({ token });
          setAbly(ablyClient);

          // Handle connection state changes
          ablyClient.connection.on('connected', () => {
            console.log('Connected to Ably');
          });

          ablyClient.connection.on('failed', () => {
            console.error('Failed to connect to Ably');
          });

          // Cleanup on unmount
          return () => {
            if (ablyClient && ablyClient.connection.state === 'connected') {
              ablyClient.close();
            }
          };
        } catch (error) {
          console.error('Error setting up Ably:', error);
        }
      }
    };

    setupAbly();
  }, [user]);

  const getChannelName = (user1Id, user2Id) => {
    const ids = [user1Id, user2Id].sort();
    return `private-chat-${ids[0]}-${ids[1]}`;
  };

  const subscribeToChat = (otherUserId, onMessage) => {
    if (!ably || !user) return null;

    const channelName = getChannelName(user.id, otherUserId);
    const channel = ably.channels.get(channelName);

    channel.subscribe('message', (message) => {
      onMessage(message.data);
    });

    return () => {
      channel.unsubscribe();
    };
  };

  const value = {
    ably,
    subscribeToChat,
  };

  return (
    <RealtimeContext.Provider value={value}>
      {children}
    </RealtimeContext.Provider>
  );
};

export const useRealtime = () => {
  const context = useContext(RealtimeContext);
  if (!context) {
    throw new Error('useRealtime must be used within a RealtimeProvider');
  }
  return context;
};