import React, { useState } from 'react';
import api from '../../services/api';

const DebugMatch = () => {
  const [skill, setSkill] = useState('php');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const testMatch = async () => {
    setLoading(true);
    try {
      const response = await api.post('/match_skills/', {
        skills: [skill]
      });
      
      const data = {
        matches: response.data.matches,
        count: response.data.matches?.length || 0,
        raw: JSON.stringify(response.data, null, 2)
      };
      
      setResult(data);
      console.log('Match response:', response.data);
    } catch (err) {
      setResult({ error: err.message, details: err.response?.data });
      console.error('Error:', err);
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h1>Debug Skill Match</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <input 
          type="text" 
          value={skill}
          onChange={(e) => setSkill(e.target.value)}
          placeholder="Enter skill to search"
          style={{ padding: '10px', width: '300px', fontSize: '16px' }}
        />
        <button 
          onClick={testMatch}
          disabled={loading}
          style={{ padding: '10px 20px', marginLeft: '10px', fontSize: '16px' }}
        >
          {loading ? 'Testing...' : 'Test Match'}
        </button>
      </div>

      {result && (
        <div>
          {result.error ? (
            <div style={{ color: 'red' }}>
              <h3>Error:</h3>
              <pre>{result.error}</pre>
              <pre>{JSON.stringify(result.details, null, 2)}</pre>
            </div>
          ) : (
            <div>
              <h3>Results: {result.count} matches found</h3>
              
              <h4>Match Details:</h4>
              {result.matches?.map((match, idx) => (
                <div key={idx} style={{ 
                  border: '1px solid #ccc', 
                  padding: '10px', 
                  marginBottom: '10px',
                  backgroundColor: match.match_percentage > 50 ? '#e8f5e9' : '#fff3e0'
                }}>
                  <div><strong>Username:</strong> {match.username}</div>
                  <div><strong>Match Score:</strong> {match.match_score}</div>
                  <div><strong>Match Percentage:</strong> {match.match_percentage}%</div>
                  <div><strong>Matching Skills:</strong> {match.matching_skills?.join(', ') || 'None'}</div>
                </div>
              ))}

              <h4>Raw Response:</h4>
              <pre style={{ 
                backgroundColor: '#f5f5f5', 
                padding: '15px', 
                overflow: 'auto',
                maxHeight: '400px'
              }}>
                {result.raw}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DebugMatch;
