import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import './Explore.css';
import api, { usersApi } from '../../services/api';

const Explore = () => {
  const [users, setUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  const normalize = (value) => (value || '').trim().toLowerCase();

  const skillMatchesSearch = (skillName, query) => {
    const candidate = normalize(skillName);
    const desired = normalize(query);
    if (!candidate || !desired) return false;
    return candidate.includes(desired) || desired.includes(candidate);
  };

  const fetchVerificationSkills = async (username) => {
    const [teacherResponse, learnerResponse] = await Promise.all([
      api.get(`/quiz/teacher-verifications/${username}/`).catch(() => ({ data: { verified_skills: [] } })),
      api.get(`/quiz/learner-verifications/${username}/`).catch(() => ({ data: { learned_skills: [] } })),
    ]);

    const teacherSkills = teacherResponse.data?.verified_skills || [];
    const learnerSkills = learnerResponse.data?.learned_skills || [];

    return [
      ...teacherSkills.map((item) => item.skill_name),
      ...learnerSkills.map((item) => item.skill_name),
    ].filter(Boolean);
  };

  const fetchUsers = useCallback(async () => {
    const query = searchTerm.trim();
    if (!query) {
      setUsers([]);
      return;
    }

    try {
      const matchResponse = await api.post('/match_skills/', { skills: [query] });
      const matches = matchResponse.data.matches || [];

      const profilePromises = matches.map((match) =>
        usersApi.getProfile(match.username)
          .then((profile) => ({ profile, match }))
          .catch(() => null)
      );

      const profiles = (await Promise.all(profilePromises)).filter(Boolean);

      const verificationResults = await Promise.all(
        profiles.map(async ({ match }) => {
          const verifiedSkills = await fetchVerificationSkills(match.username);
          const verifiedMatchingSkills = verifiedSkills.filter((skill) => skillMatchesSearch(skill, query));

          return {
            username: match.username,
            verifiedSkills,
            verifiedMatchingSkills,
            hasVerifiedMatch: verifiedMatchingSkills.length > 0,
          };
        })
      );

      const verificationMap = verificationResults.reduce((accumulator, item) => {
        accumulator[item.username] = item;
        return accumulator;
      }, {});

      const enrichedProfiles = profiles.map(({ profile, match }) => {
        const verification = verificationMap[match.username] || {
          verifiedSkills: [],
          verifiedMatchingSkills: [],
          hasVerifiedMatch: false,
        };

        return {
          ...profile.data,
          match_score: match.match_score,
          match_percentage: match.match_percentage ?? Math.round((match.match_score || 0) * 100),
          matching_skills: match.matching_skills || [],
          verified_skills: verification.verifiedSkills,
          verified_matching_skills: verification.verifiedMatchingSkills,
          has_verified_match: verification.hasVerifiedMatch,
        };
      });

      enrichedProfiles.sort((a, b) => {
        const verifiedDiff = Number(Boolean(b.has_verified_match)) - Number(Boolean(a.has_verified_match));
        if (verifiedDiff !== 0) return verifiedDiff;

        const scoreDiff = (b.match_score || 0) - (a.match_score || 0);
        if (scoreDiff !== 0) return scoreDiff;

        return (a.user?.username || '').localeCompare(b.user?.username || '');
      });

      setUsers(enrichedProfiles);
    } catch (err) {
      console.error('Error fetching users:', err);
      setUsers([]);
    }
  }, [searchTerm]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  return (
    <div className="explore-container">
      <div className="explore-header">
        <h2>Explore Skills</h2>
        <div className="search-filters">
          <input
            type="text"
            placeholder="Search by skill or username..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
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
              <div className="match-score">
                <strong>Match: {profile.match_percentage}%</strong>
              </div>
              <p className="user-bio">
                {(profile.bio || '').slice(0, 120)}{(profile.bio || '').length > 120 ? '…' : ''}
              </p>
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
  );
};

export default Explore;
