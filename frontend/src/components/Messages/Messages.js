import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useRealtime } from '../../contexts/RealtimeContext';
import api from '../../services/api';
import './Messages.css';

const Messages = ({ selectedUser }) => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const { user } = useAuth();
  const { subscribeToChat } = useRealtime();
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (selectedUser) {
      let mounted = true;

      // Load existing messages
      const loadMessages = async () => {
        try {
          const response = await api.get(`/messages/?with=${selectedUser.id}`);
          if (mounted) {
            // Backend returns array directly now
            setMessages(response.data);
            scrollToBottom();
          }
        } catch (error) {
          console.error('Error loading messages:', error);
        }
      };

      loadMessages();

      // Subscribe to real-time updates
      const unsubscribe = subscribeToChat(selectedUser.id, (data) => {
        console.log('Received real-time message:', data);
        if (data.type === 'message' && mounted) {
          setMessages(prev => [...prev, data.message]);
          scrollToBottom();
        }
      });

      return () => {
        mounted = false;
        if (unsubscribe) unsubscribe();
      };
    }
  }, [selectedUser, subscribeToChat]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedUser) return;

    try {
      await api.post('/messages/', {
        receiver: selectedUser.id,
        content: newMessage.trim()
      });
      
      setNewMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  if (!selectedUser) {
    return <div className="messages-container">Select a user to start chatting</div>;
  }

  return (
    <div className="messages-container">
      <div className="messages-header">
        <h3>Chat with {selectedUser.username}</h3>
      </div>
      
      <div className="messages-list">
        {messages.map((message) => (
          <div 
            key={message.id} 
            className={`message ${message.sender?.id === user.id || message.sender === user.id ? 'sent' : 'received'}`}
          >
            <div className="message-content">{message.content}</div>
            <div className="message-time">
              {new Date(message.created_at).toLocaleTimeString()}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      <form onSubmit={handleSendMessage} className="message-input-form">
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Type a message..."
          className="message-input"
        />
        <button type="submit" className="send-button">Send</button>
      </form>
    </div>
  );
};

export default Messages;