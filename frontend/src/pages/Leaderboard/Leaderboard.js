import React, { useEffect, useState } from 'react';
import api from '../../services/api';
import './Leaderboard.css';

const Leaderboard = () => {
  const [rows, setRows] = useState([]);
  const [myRank, setMyRank] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        setLoading(true);
        const { data } = await api.get('/learning/leaderboard/');
        setRows(data.leaderboard || []);
        setMyRank(data.my_rank || null);
      } catch (err) {
        setError('Failed to load leaderboard');
      } finally {
        setLoading(false);
      }
    };

    fetchLeaderboard();
  }, []);

  if (loading) {
    return <div className="leaderboard-container loading">Loading leaderboard...</div>;
  }

  if (error) {
    return <div className="leaderboard-container error-message">{error}</div>;
  }

  return (
    <div className="leaderboard-container">
      <h2 className="page-title">Leaderboard</h2>
      <p className="leaderboard-subtitle">
        Ranking is based on your platform minutes and skills-earned score.
      </p>

      {myRank && (
        <div className="my-rank-card">
          Your current rank: <strong>#{myRank}</strong>
        </div>
      )}

      {rows.length === 0 ? (
        <div className="empty-state">No leaderboard data yet.</div>
      ) : (
        <div className="leaderboard-table-wrapper">
          <table className="leaderboard-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>User</th>
                <th>Skills Earned</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.user_id}>
                  <td>#{row.rank}</td>
                  <td>{row.username}</td>
                  <td>{row.skills_earned}</td>
                  <td className="score-cell">{Number(row.score || 0).toFixed(0)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Leaderboard;
