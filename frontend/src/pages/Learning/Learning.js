import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import api, { usersApi } from '../../services/api';
import LearningSession from '../../components/LearningSession/LearningSession';
import './Learning.css';

const Learning = () => {
  const [activeTab, setActiveTab] = useState('discover');
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [roleFilter, setRoleFilter] = useState('all');
  const [userPoints, setUserPoints] = useState(null);
  const [users, setUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const normalize = (value) => (value || '').trim().toLowerCase();

  const skillMatchesSearch = (skillName, query) => {
    const candidate = normalize(skillName);
    const desired = normalize(query);
    if (!candidate || !desired) return false;
    return candidate.includes(desired) || desired.includes(candidate);
  };

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const params = new URLSearchParams();
      if (roleFilter !== 'all') params.append('role', roleFilter);
      if (filter !== 'all') params.append('status', filter);

      const response = await axios.get(
        `${API_BASE_URL}/api/learning/sessions/?${params.toString()}`,
        {
          headers: { Authorization: `Token ${token}` }
        }
      );
      setSessions(response.data);
    } catch (error) {
      console.error('Error fetching learning sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserPoints = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_BASE_URL}/api/learning/points/`,
        {
          headers: { Authorization: `Token ${token}` }
        }
      );
      setUserPoints(response.data);
    } catch (error) {
      console.error('Error fetching user points:', error);
    }
  };

  const handleSessionUpdate = () => {
    fetchSessions();
    fetchUserPoints();
  };

  const fetchUsers = async () => {
    if (!searchTerm || searchTerm.trim() === '') {
      setUsers([]);
      return;
    }

    try {
      const matchResponse = await api.post('/match_skills/', {
        skills: [searchTerm.trim()]
      });
      
      const matches = matchResponse.data.matches || [];
      console.log('[Learning] === SKILL MATCH DEBUG ===');
      console.log('[Learning] Total matches:', matches.length);
      console.log('[Learning] Raw matches:', matches);
      
      // Log each match in detail
      matches.forEach((match, idx) => {
        console.log(`[Learning] Match ${idx + 1}:`, {
          username: match.username,
          match_score: match.match_score,
          match_percentage: match.match_percentage,
          matching_skills: match.matching_skills,
          'SCORE_TYPE': typeof match.match_score,
          'PERCENTAGE_TYPE': typeof match.match_percentage
        });
      });
      
      const profilePromises = matches.map((match, index) => 
        usersApi.getProfile(match.username)
          .then(profile => ({ profile, match, index }))
          .catch(err => {
            console.error(`Error fetching profile for ${match.username}:`, err);
            return null;
          })
      );
      
      const results = await Promise.all(profilePromises);
      
      const enrichedProfiles = results
        .filter(r => r !== null)
        .map(({ profile, match }) => {
          // Ensure match_percentage is properly calculated
          const matchPercentage = match.match_percentage !== undefined 
            ? match.match_percentage 
            : Math.round((match.match_score || 0) * 100);

          const verifiedSkills = match.verified_skills || [];
          const verifiedMatchingSkills = (match.verified_matching_skills && match.verified_matching_skills.length > 0)
            ? match.verified_matching_skills
            : verifiedSkills.filter((skill) => skillMatchesSearch(skill, searchTerm));
          
          console.log(`[Learning] Enriching ${match.username}:`, {
            original_percentage: match.match_percentage,
            calculated_percentage: matchPercentage,
            match_score: match.match_score,
            will_display: matchPercentage !== undefined && matchPercentage !== null
          });
          
          return {
            ...profile.data,
            match_score: match.match_score,
            match_percentage: matchPercentage,
            matching_skills: match.matching_skills,
            verified_skills: verifiedSkills,
            verified_matching_skills: verifiedMatchingSkills,
            has_verified_match: verifiedMatchingSkills.length > 0,
          };
        });
      
      console.log('[Learning] === ENRICHED PROFILES DEBUG ===');
      console.log('[Learning] Total enriched:', enrichedProfiles.length);
      enrichedProfiles.forEach((profile, idx) => {
        console.log(`[Learning] Profile ${idx + 1}:`, {
          username: profile.user?.username,
          match_percentage: profile.match_percentage,
          match_score: profile.match_score,
          'PERCENTAGE_TYPE': typeof profile.match_percentage,
          'WILL_SHOW': profile.match_percentage !== undefined && profile.match_percentage !== null
        });
      });
      setUsers(enrichedProfiles);
    } catch (err) {
      console.error('Error fetching users:', err);
      setUsers([]);
    }
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  useEffect(() => {
    if (activeTab === 'sessions') {
      fetchSessions();
    }
    fetchUserPoints();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filter, roleFilter, activeTab]);

  useEffect(() => {
    if (activeTab === 'discover') {
      fetchUsers();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchTerm, activeTab]);

  return (
    <div className="learning-page">
      <div className="learning-header">
        <h1>Learning Hub</h1>
        {userPoints && (
          <div className="points-display">
            <div className="points-card">
              <span className="points-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="8" />
                  <path d="M9.5 12h5" />
                  <path d="M12 9.5v5" />
                </svg>
              </span>
              <div className="points-info">
                <div className="points-balance">{userPoints.balance}</div>
                <div className="points-label">Current Points</div>
              </div>
            </div>
            <div className="points-stats">
              <div className="stat-item">
                <span className="stat-value">{userPoints.total_earned}</span>
                <span className="stat-label">Total Earned</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">{userPoints.total_spent}</span>
                <span className="stat-label">Total Spent</span>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="learning-tabs">
        <button
          className={`tab-button ${activeTab === 'discover' ? 'active' : ''}`}
          onClick={() => setActiveTab('discover')}
        >
          <span className="tab-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="6" />
              <path d="m20 20-4.2-4.2" />
            </svg>
          </span>
          Discover Skills
        </button>
        <button
          className={`tab-button ${activeTab === 'sessions' ? 'active' : ''}`}
          onClick={() => setActiveTab('sessions')}
        >
          <span className="tab-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M5 4.5A2.5 2.5 0 0 1 7.5 2H19v18H7.5A2.5 2.5 0 0 0 5 22V4.5Z" />
              <path d="M5 5h12" />
            </svg>
          </span>
          My Sessions
        </button>
      </div>

      {activeTab === 'discover' ? (
        <div className="discover-content">
          <div className="discover-header">
            <div className="search-filters">
              <input
                type="text"
                placeholder="Search by skill or username..."
                value={searchTerm}
                onChange={handleSearch}
                className="search-input"
              />
            </div>
          </div>

          <div className="users-grid">
            {users.map((profile) => (
              <div
                key={profile.user?.id || profile.user}
                className={`user-card ${profile.has_verified_match ? 'verified-match' : ''}`}
                onClick={() => navigate(`/users/${profile.user?.username}?skill=${encodeURIComponent(searchTerm.trim())}`)}
                style={{ cursor: 'pointer' }}
              >
                <div className="user-info">
                  <h3 className="user-name-row">
                    <span>{profile.user?.username}</span>
                    {profile.has_verified_match && (
                      <span
                        className="verified-star"
                        title={`Verified: ${profile.verified_matching_skills.join(', ')}`}
                        aria-label="Verified skill"
                      >
                        ★
                      </span>
                    )}
                  </h3>
                  {(profile.match_percentage !== undefined && profile.match_percentage !== null) && (
                    <div className="match-score">
                      <strong>Match: {profile.match_percentage}%</strong>
                    </div>
                  )}
                  <p className="user-bio">{(profile.bio || '').slice(0, 120)}{(profile.bio || '').length > 120 ? '…' : ''}</p>
                </div>

                {profile.skills && profile.skills.length > 0 && (
                  <div className="user-skills">
                    <h4>Skills</h4>
                    <div className="skill-tags">
                      {profile.skills.map((skill, index) => (
                        <span 
                          key={index} 
                          className={`skill-tag ${profile.matching_skills?.includes(skill.name || skill) ? 'matching' : ''}`}
                        >
                          {typeof skill === 'object' ? skill.name : skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {users.length === 0 && (
            <div className="no-results">
              {searchTerm.trim() === '' ? (
                <p>Start searching to find your match!</p>
              ) : (
                <p>No users found matching your search criteria.</p>
              )}
            </div>
          )}
        </div>
      ) : (
        <div className="sessions-content">
          <div className="learning-filters">
            <div className="filter-group">
              <label>Role:</label>
              <select value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}>
                <option value="all">All</option>
                <option value="learner">As Learner</option>
                <option value="teacher">As Teacher</option>
              </select>
            </div>

            <div className="filter-group">
              <label>Status:</label>
              <select value={filter} onChange={(e) => setFilter(e.target.value)}>
                <option value="all">All</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
              </select>
            </div>
          </div>

          <div className="learning-content">
            {loading ? (
              <div className="loading-state">
                <div className="spinner"></div>
                <p>Loading your learning sessions...</p>
              </div>
            ) : sessions.length > 0 ? (
              <div className="sessions-list">
                {sessions.map((session) => (
                  <LearningSession
                    key={session.id}
                    session={session}
                    onUpdate={handleSessionUpdate}
                  />
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M5 4.5A2.5 2.5 0 0 1 7.5 2H19v18H7.5A2.5 2.5 0 0 0 5 22V4.5Z" />
                    <path d="M5 5h12" />
                  </svg>
                </div>
                <h3>No Learning Sessions Yet</h3>
                <p>Start learning or teaching to see your sessions here</p>
                <button
                  className="btn-explore"
                  onClick={() => setActiveTab('discover')}
                >
                  Discover Skills
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Learning;
