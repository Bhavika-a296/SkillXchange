import React, { createContext, useContext, useEffect, useState } from 'react';
import { Realtime } from 'ably';
import { useAuth } from './AuthContext';
import api from '../services/api';

const RealtimeContext = createContext();

export const RealtimeProvider = ({ children }) => {
  const [ably, setAbly] = useState(null);
  const { user } = useAuth();

  useEffect(() => {
    let isCancelled = false;
    let localClient = null;

    const setupAbly = async () => {
      if (!user) {
        if (ably) {
          ably.close();
          setAbly(null);
        }
        return;
      }

      try {
        // Get token from backend
        const response = await api.get('realtime/token/');
        if (isCancelled) {
          return;
        }
        const { token } = response.data;

        // Close any existing client before replacing it
        setAbly((previousClient) => {
          if (previousClient) {
            previousClient.close();
          }
          return previousClient;
        });

        // Initialize Ably with the token
        localClient = new Realtime({ token });
        setAbly(localClient);

        // Handle connection state changes
        localClient.connection.on('connected', () => {
          console.log('Connected to Ably');
        });

        localClient.connection.on('failed', () => {
          console.error('Failed to connect to Ably');
        });
      } catch (error) {
        if (!isCancelled) {
          console.error('Error setting up Ably:', error);
        }
      }
    };

    setupAbly();

    return () => {
      isCancelled = true;
      if (localClient) {
        localClient.close();
      }
    };
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