import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import './Explore.css';
import api, { usersApi } from '../../services/api';

const Explore = () => {
  const [users, setUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  const fetchUsers = useCallback(async () => {
    // Only search when there's a non-empty query (username or skill).
    if (!searchTerm || searchTerm.trim() === '') {
      setUsers([]);
      return;
    }

    try {
      // Use AI-powered skill matching endpoint
      const matchResponse = await api.post('/match_skills/', {
        skills: [searchTerm.trim()]
      });
      
      const matches = matchResponse.data.matches || [];
      console.log('Skill matches:', matches);
      
      // Fetch full profiles for matched users
      const profilePromises = matches.map((match, index) => 
        usersApi.getProfile(match.username)
          .then(profile => ({ profile, match, index }))
          .catch(err => {
            console.error(`Error fetching profile for ${match.username}:`, err);
            return null;
          })
      );
      
      const results = await Promise.all(profilePromises);
      
      // Combine match data with profile data, preserving match information
      const enrichedProfiles = results
        .filter(r => r !== null)
        .map(({ profile, match }) => ({
          ...profile.data,
          match_score: match.match_score,
          match_percentage: match.match_percentage,
          matching_skills: match.matching_skills
        }));
      
      setUsers(enrichedProfiles);
    } catch (err) {
      console.error('Error fetching users:', err);
      setUsers([]);
    }
  }, [searchTerm]); // Add dependencies for useCallback

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]); // fetchUsers is now memoized, so this is safe

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleConnect = async (userId) => {
    try {
      await api.post(`/connections/request/${userId}/`);
      // Refresh the users list
      fetchUsers();
    } catch (err) {
      console.error('Error sending connection request:', err);
    }
  };

  return (
    <div className="explore-container">
      <div className="explore-header">
        <h2>Explore Skills</h2>
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
            className="user-card"
            onClick={() => navigate(`/users/${profile.user?.username}`)}
            style={{ cursor: 'pointer' }}
          >
            <div className="user-info">
              <h3>{profile.user?.username}</h3>
              {/* Display match percentage if available */}
              {profile.match_percentage !== undefined && (
                <div className="match-score">
                  <strong>Match: {profile.match_percentage}%</strong>
                </div>
              )}
              {/* Short bio preview only */}
              <p className="user-bio">{(profile.bio || '').slice(0, 120)}{(profile.bio || '').length > 120 ? '…' : ''}</p>
            </div>

            {/* Display skills without proficiency levels */}
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
  );
};

export default Explore;