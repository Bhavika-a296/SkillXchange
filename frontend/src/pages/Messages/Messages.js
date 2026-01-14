import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { messagesApi } from '../../services/api';
import api from '../../services/api';
import './Messages.css';

const Messages = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [conversations, setConversations] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState(null);
  const [connectionId, setConnectionId] = useState(null);
  const [isRequester, setIsRequester] = useState(false);
  const [meetingCreating, setMeetingCreating] = useState(false);
  const [isUserScrolling, setIsUserScrolling] = useState(false);
  const pollRef = useRef(null);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);

  // Get user from URL params if navigated from Explore
  useEffect(() => {
    const userId = searchParams.get('user');
    
    const loadConversations = async () => {
      try {
        setLoading(true);
        const resp = await messagesApi.getConversations();
        const convos = resp.data.conversations || [];
        setConversations(convos);
        
        if (userId) {
          // Find conversation with this user
          const user = convos.find(c => c.id === parseInt(userId));
          if (user) {
            handleSelectUser(user);
          } else {
            // If no existing conversation, start new chat
            setSelectedUser({ id: parseInt(userId) });
            fetchMessages(userId);
          }
        }
      } catch (err) {
        console.error('Error fetching conversations:', err);
      } finally {
        setLoading(false);
      }
    };
    
    loadConversations();
  }, [searchParams]);

  const fetchConversations = async () => {
    try {
      setLoading(true);
      const resp = await messagesApi.getConversations();
      setConversations(resp.data.conversations || []);
    } catch (err) {
      console.error('Error fetching conversations:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserAndStartChat = async (userId) => {
    try {
      // This would need a new API endpoint to get user info
      // For now, we'll just select them
      setSelectedUser({ id: parseInt(userId) });
      fetchMessages(userId);
    } catch (err) {
      console.error('Error fetching user:', err);
    }
  };

  const handleSelectUser = async (user) => {
    setSelectedUser(user);
    fetchMessages(user.id);
  };

  const fetchMessages = async (userId) => {
    try {
      const resp = await messagesApi.fetchConversation(userId);
      setMessages(resp.data.messages || []);
      setConnectionStatus(resp.data.connection_status);
      setConnectionId(resp.data.connection_id);
      setIsRequester(resp.data.is_requester);

      // Start polling for new messages
      if (pollRef.current) clearInterval(pollRef.current);
      pollRef.current = setInterval(async () => {
        const pollResp = await messagesApi.fetchConversation(userId);
        setMessages(pollResp.data.messages || []);
        setConnectionStatus(pollResp.data.connection_status);
      }, 2000);
    } catch (err) {
      console.error('Error fetching messages:', err);
    }
  };

  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  // Check if user is near bottom before auto-scrolling
  const isNearBottom = () => {
    if (!messagesContainerRef.current) return true;
    const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current;
    const threshold = 100; // pixels from bottom
    return scrollHeight - scrollTop - clientHeight < threshold;
  };

  useEffect(() => {
    // Only auto-scroll if user is near the bottom or if it's a new message being sent
    if (isNearBottom() || !isUserScrolling) {
      scrollToBottom();
    }
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Track user scrolling
  const handleScroll = () => {
    if (messagesContainerRef.current) {
      const isAtBottom = isNearBottom();
      setIsUserScrolling(!isAtBottom);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() && !selectedFile) return;
    if (!selectedUser) return;

    try {
      setSending(true);

      const formData = new FormData();
      formData.append('receiver', selectedUser.id);

      if (selectedFile) {
        formData.append('file', selectedFile);
      }

      if (newMessage.trim()) {
        formData.append('content', newMessage.trim());
      } else if (selectedFile) {
        formData.append('content', `Shared a file: ${selectedFile.name}`);
      }

      const resp = await messagesApi.sendMessageWithFile(formData);
      setMessages((m) => [...m, resp.data]);
      
      // Reset scroll flag so it auto-scrolls when sending a message
      setIsUserScrolling(false);

      // Update connection status after first message
      if (!connectionStatus) {
        const statusResp = await messagesApi.fetchConversation(selectedUser.id);
        setConnectionStatus(statusResp.data.connection_status);
        setConnectionId(statusResp.data.connection_id);
        setIsRequester(statusResp.data.is_requester);
      }

      setNewMessage('');
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err) {
      console.error('Error sending message:', err);
      alert(err.response?.data?.error || 'Failed to send message');
    } finally {
      setSending(false);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB');
        return;
      }
      setSelectedFile(file);
    }
  };

  const removeSelectedFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleCreateMeet = async () => {
    if (!selectedUser?.id) return;
    try {
      setMeetingCreating(true);
      const resp = await fetch('http://localhost:4000/api/create-meet', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ summary: `Chat with ${selectedUser.username}` })
      });

      if (resp.status === 401) {
        const data = await resp.json();
        if (data?.auth_url) {
          window.open(data.auth_url, '_blank');
        }
        return;
      }

      const data = await resp.json();
      if (data?.meetLink) {
        // Send the meet link as a message
        const formData = new FormData();
        formData.append('receiver', selectedUser.id);
        formData.append('content', `Google Meet: ${data.meetLink}`);
        
        const msgResp = await messagesApi.sendMessageWithFile(formData);
        setMessages((m) => [...m, msgResp.data]);
      }
    } catch (err) {
      console.error('Error creating Meet', err);
      alert('Failed to create Google Meet link');
    } finally {
      setMeetingCreating(false);
    }
  };

  const handleAcceptConnection = async () => {
    if (!connectionId) return;
    try {
      await api.post(`/connections/${connectionId}/accept/`);
      setConnectionStatus('connected');
      alert('Connection accepted!');
      // Refresh messages to update status
      await fetchMessages(selectedUser.id);
    } catch (err) {
      console.error('Error accepting connection:', err);
      alert('Failed to accept connection');
    }
  };

  const handleRejectConnection = async () => {
    if (!connectionId) return;
    try {
      await api.post(`/connections/${connectionId}/reject/`);
      setConnectionStatus('rejected');
      alert('Connection rejected');
      // Refresh messages to update status
      await fetchMessages(selectedUser.id);
    } catch (err) {
      console.error('Error rejecting connection:', err);
      alert('Failed to reject connection');
    }
  };

  const renderMessageContent = (text) => {
    if (!text) return null;
    const urlRegex = /((https?:\/\/|www\.)[^\s]+)/gi;
    const parts = text.split(urlRegex);
    return parts.map((part, idx) => {
      if (urlRegex.test(part)) {
        let href = part.startsWith('http') ? part : `https://${part}`;
        return (
          <a
            key={idx}
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="message-link"
          >
            {part}
          </a>
        );
      }
      return <span key={idx}>{part}</span>;
    });
  };

  return (
    <div className="messages-page">
      <div className="messages-container">
        {/* Sidebar with conversations list */}
        <div className="conversations-sidebar">
          <div className="sidebar-header">
            <h2>Messages</h2>
          </div>
          <div className="conversations-list">
            {loading ? (
              <p className="loading-text">Loading...</p>
            ) : conversations.length > 0 ? (
              conversations.map((user) => (
                <div
                  key={user.id}
                  className={`conversation-item ${selectedUser?.id === user.id ? 'active' : ''}`}
                  onClick={() => handleSelectUser(user)}
                >
                  <div className="conversation-avatar">
                    {user.username ? user.username[0].toUpperCase() : '?'}
                  </div>
                  <div className="conversation-info">
                    <div className="conversation-name">{user.username || 'Unknown'}</div>
                    {user.last_message && (
                      <div className="conversation-preview">
                        {user.last_message.substring(0, 30)}...
                      </div>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="empty-state">
                <p>No conversations yet</p>
                <button 
                  className="button-primary"
                  onClick={() => navigate('/explore')}
                >
                  Find Users
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Chat area */}
        <div className="chat-area">
          {selectedUser ? (
            <>
              <div className="chat-header">
                <div 
                  className="chat-header-user"
                  onClick={() => selectedUser.username && navigate(`/users/${selectedUser.username}`)}
                  style={{ cursor: 'pointer' }}
                >
                  <div className="chat-avatar">
                    {selectedUser.username ? selectedUser.username[0].toUpperCase() : '?'}
                  </div>
                  <div className="chat-user-info">
                    <h3>{selectedUser.username || 'User'}</h3>
                    <span className="status-indicator">
                      {connectionStatus === 'connected' ? 'Connected' : 
                       connectionStatus === 'pending' ? 'Pending' : 'Click to view profile'}
                    </span>
                  </div>
                </div>
                <div className="chat-header-actions">
                  {connectionStatus === 'pending' && !isRequester && (
                    <div className="connection-request-actions">
                      <button
                        className="accept-button"
                        onClick={handleAcceptConnection}
                        title="Accept connection request"
                      >
                        Accept
                      </button>
                      <button
                        className="reject-button"
                        onClick={handleRejectConnection}
                        title="Reject connection request"
                      >
                        Reject
                      </button>
                    </div>
                  )}
                  <button
                    className="meet-button"
                    onClick={handleCreateMeet}
                    disabled={meetingCreating || connectionStatus === 'rejected'}
                    title="Create Google Meet"
                  >
                    {meetingCreating ? '...' : "Let's meet"}
                  </button>
                </div>
              </div>

              {/* Connection Request Banner */}
              {connectionStatus === 'pending' && !isRequester && (
                <div className="connection-request-banner">
                  <div className="banner-content">
                    <span className="banner-icon">👥</span>
                    <div className="banner-text">
                      <strong>{selectedUser.username}</strong> sent you a connection request
                    </div>
                  </div>
                  <div className="banner-actions">
                    <button className="banner-accept-btn" onClick={handleAcceptConnection}>
                      Accept
                    </button>
                    <button className="banner-reject-btn" onClick={handleRejectConnection}>
                      Reject
                    </button>
                  </div>
                </div>
              )}

              <div className="messages-container-inner" ref={messagesContainerRef} onScroll={handleScroll}>
                {messages.length > 0 ? (
                  messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`message-bubble ${
                        msg.sender?.username === selectedUser.username ? 'received' : 'sent'
                      }`}
                    >
                      <div className="message-content">
                        {renderMessageContent(msg.content)}
                        {msg.file_url && (
                          <div className="message-file">
                            <a
                              href={msg.file_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="file-download"
                            >
                              📎 {msg.file_name || 'Download File'}
                            </a>
                          </div>
                        )}
                      </div>
                      <div className="message-time">
                        {new Date(msg.created_at).toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="empty-messages">
                    <p>No messages yet. Start the conversation!</p>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {connectionStatus !== 'rejected' && (
                <div className="message-input-container">
                  {selectedFile && (
                    <div className="selected-file-preview">
                      <span>📎 {selectedFile.name}</span>
                      <button onClick={removeSelectedFile} className="remove-file">
                        ✕
                      </button>
                    </div>
                  )}
                  <form onSubmit={handleSendMessage} className="message-form">
                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={handleFileSelect}
                      style={{ display: 'none' }}
                      accept=".pdf,.doc,.docx,.txt,.png,.jpg,.jpeg,.gif"
                    />
                    <button
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      className="attach-btn"
                    >
                      📎
                    </button>
                    <input
                      type="text"
                      placeholder="Type a message..."
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      className="message-input"
                    />
                    <button type="submit" className="send-btn" disabled={sending}>
                      {sending ? '...' : '➤'}
                    </button>
                  </form>
                </div>
              )}
            </>
          ) : (
            <div className="no-chat-selected">
              <h3>Select a conversation</h3>
              <p>Choose a conversation from the left to start messaging</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Messages;
