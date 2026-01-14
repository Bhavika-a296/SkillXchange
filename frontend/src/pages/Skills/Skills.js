import React, { useState, useEffect } from 'react';
import './Skills.css';

const Skills = () => {
  const [skills, setSkills] = useState([]);
  const [newSkill, setNewSkill] = useState({
    title: '',
    description: '',
    proficiencyLevel: 'beginner',
  });
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSkills();
  }, []);

  const fetchSkills = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/skills/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSkills(data);
      }
    } catch (err) {
      console.error('Error fetching skills:', err);
    }
  };

  const handleChange = (e) => {
    setNewSkill({
      ...newSkill,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/skills/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(newSkill),
      });

      if (response.ok) {
        setNewSkill({
          title: '',
          description: '',
          proficiencyLevel: 'beginner',
        });
        fetchSkills();
      } else {
        setError('Failed to add skill');
      }
    } catch (err) {
      setError('An error occurred. Please try again later.');
    }
  };

  return (
    <div className="skills-container">
      <div className="skills-header">
        <h2>My Skills</h2>
      </div>

      <div className="skills-content">
        <div className="add-skill-section">
          <h3>Add New Skill</h3>
          {error && <div className="error-message">{error}</div>}
          
          <form onSubmit={handleSubmit} className="add-skill-form">
            <div className="form-group">
              <label htmlFor="title">Skill Title</label>
              <input
                type="text"
                id="title"
                name="title"
                value={newSkill.title}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="description">Description</label>
              <textarea
                id="description"
                name="description"
                value={newSkill.description}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="proficiencyLevel">Proficiency Level</label>
              <select
                id="proficiencyLevel"
                name="proficiencyLevel"
                value={newSkill.proficiencyLevel}
                onChange={handleChange}
                required
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
                <option value="expert">Expert</option>
              </select>
            </div>

            <button type="submit" className="button-primary">
              Add Skill
            </button>
          </form>
        </div>

        <div className="skills-list">
          <h3>My Skills List</h3>
          {skills.length === 0 ? (
            <p>No skills added yet.</p>
          ) : (
            <div className="skills-grid">
              {skills.map((skill) => (
                <div key={skill.id} className="skill-card">
                  <h4>{skill.title}</h4>
                  <p>{skill.description}</p>
                  <span className={`proficiency-badge ${skill.proficiencyLevel}`}>
                    {skill.proficiencyLevel}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Skills;