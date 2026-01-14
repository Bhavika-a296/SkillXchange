import React, { useState, useEffect } from 'react';
import { profileApi } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import './ResumeUpload.css';

const ResumeUpload = ({ onSkillsExtracted }) => {
  const { user } = useAuth();
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentResume, setCurrentResume] = useState(null);
  const [extractedSkills, setExtractedSkills] = useState([]);

  useEffect(() => {
    const fetchCurrentResume = async () => {
      try {
        const response = await profileApi.getCurrentResume();
        if (response.data) {
          setCurrentResume(response.data);
          setExtractedSkills(response.data.skills || []);
        }
      } catch (err) {
        console.error('Error fetching current resume:', err);
      }
    };

    if (user) {
      fetchCurrentResume();
    }
  }, [user]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError('');
    } else {
      setError('Please select a valid PDF file');
      setFile(null);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const { data } = await profileApi.uploadResume(formData);
      const skills = data.skills_extracted || [];
      setExtractedSkills(skills);
      setCurrentResume(data.resume || null);
      if (onSkillsExtracted) {
        onSkillsExtracted(skills);
      }
      setFile(null);
      // Reset file input
      const fileInput = document.querySelector('input[type="file"]');
      if (fileInput) fileInput.value = '';
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.response?.data?.error || 'An error occurred while uploading the resume');
    } finally {
      setLoading(false);
    }
  };

  const handleViewResume = () => {
    if (currentResume && currentResume.file_url) {
      // Construct the full URL
      const baseURL = 'http://127.0.0.1:8000';
      const resumeURL = currentResume.file_url.startsWith('http') 
        ? currentResume.file_url 
        : `${baseURL}${currentResume.file_url}`;
      window.open(resumeURL, '_blank');
    } else if (currentResume && currentResume.file) {
      const baseURL = 'http://127.0.0.1:8000';
      const resumeURL = currentResume.file.startsWith('http') 
        ? currentResume.file 
        : `${baseURL}${currentResume.file}`;
      window.open(resumeURL, '_blank');
    }
  };

  return (
    <div className="resume-upload">
      <h2>{currentResume ? 'Your Resume' : 'Upload Your Resume'}</h2>
      
      {currentResume ? (
        <div className="current-resume">
          <p className="resume-info">
            Resume uploaded on {new Date(currentResume.created_at).toLocaleDateString()}
            {currentResume.filename && ` - ${currentResume.filename}`}
          </p>
          <button 
            type="button"
            onClick={handleViewResume}
            className="view-resume-btn button-secondary"
          >
            View Current Resume
          </button>
        </div>
      ) : (
        <p className="upload-info">
          Upload your PDF resume to automatically extract your skills
        </p>
      )}

      {error && <div className="error-message">{error}</div>}

      <form onSubmit={handleUpload} className="upload-form">
        <div className="file-input-container">
          <input
            type="file"
            onChange={handleFileChange}
            accept=".pdf"
            id="resume-file"
            className="file-input"
          />
          <label htmlFor="resume-file" className="file-label">
            {file ? file.name : (currentResume ? 'Choose new PDF file' : 'Choose PDF file')}
          </label>
        </div>

        <button 
          type="submit" 
          className="upload-button"
          disabled={loading || !file}
        >
          {loading ? 'Processing...' : (currentResume ? 'Replace Resume' : 'Upload Resume')}
        </button>
      </form>

      {extractedSkills.length > 0 && (
        <div className="extracted-skills">
          <h3>Your Skills</h3>
          <div className="skills-list">
            {extractedSkills.map((skill) => (
              <span 
                key={skill.id} 
                className={`skill-tag ${skill.isNew ? 'new-skill' : ''}`}
                title={skill.isNew ? 'Newly added skill' : 'Existing skill'}
              >
                {skill.name}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ResumeUpload;