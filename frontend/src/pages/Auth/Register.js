import React, { useState, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { authApi } from '../../services/api';
import ResumeUpload from '../../components/ResumeUpload/ResumeUpload';
import './Auth.css';

const Register = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');
  const [step, setStep] = useState(1); // 1 for registration form, 2 for resume upload
  const [usernameStatus, setUsernameStatus] = useState({ checking: false, available: true, suggestion: null });

  // Debounce function to delay username availability check
  const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  };

  const checkUsername = async (username) => {
    if (!username) return;
    const validUsername = username.toLowerCase().replace(/\s+/g, '_');
    try {
      setUsernameStatus(prev => ({ ...prev, checking: true }));
      const { data } = await authApi.checkUsername(validUsername);
      setUsernameStatus({
        checking: false,
        available: data.available,
        suggestion: data.suggestion
      });
    } catch (err) {
      setUsernameStatus({ checking: false, available: true, suggestion: null });
    }
  };

  // Memoize the debounced function with its dependencies
  const debouncedCheckUsername = useCallback(
    debounce(checkUsername, 500),
    [checkUsername]
  );

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));

    if (name === 'username') {
      debouncedCheckUsername(value);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Form validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // Convert name to valid username (lowercase, replace spaces with underscores)
    const validUsername = formData.username.trim().toLowerCase().replace(/\s+/g, '_');
    
    try {
      const requestData = {
        username: validUsername,
        email: formData.email.trim(),
        password: formData.password,
        password2: formData.confirmPassword, // Add password confirmation
      };

      await register(requestData);
      setStep(2); // Move to resume upload step
    } catch (err) {
      if (err.response?.data?.username) {
        // Handle username already exists error
        const suggestedUsername = `${validUsername}_${Math.floor(Math.random() * 1000)}`;
        setError(`Username already taken. Try something like: ${suggestedUsername}`);
      } else {
        setError(err.response?.data?.error || 'Registration failed. Please try again.');
      }
    }
  };

  const handleSkillsExtracted = (skills) => {
    navigate('/'); // Redirect to home after skills are extracted
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        {step === 1 ? (
          <>
            <h2>Create an Account</h2>
            {error && <div className="error-message">{error}</div>}
            
            <form onSubmit={handleSubmit} className="auth-form">
              <div className="form-group">
                <label htmlFor="username">Username</label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  pattern="[a-zA-Z0-9@.+\-_]+"
                  title="Username can only contain letters, numbers, and @/./+/-/_ characters"
                  required
                  className={!usernameStatus.available ? 'invalid' : ''}
                />
                <small className="form-help">
                  Username will be converted to lowercase and spaces will be replaced with underscores
                </small>
                {usernameStatus.checking && (
                  <small className="form-help checking">Checking username availability...</small>
                )}
                {!usernameStatus.available && (
                  <small className="form-help error">
                    Username already taken. Try: {usernameStatus.suggestion}
                  </small>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="password">Password</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="confirmPassword">Confirm Password</label>
                <input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                />
              </div>

              <button type="submit" className="button-primary">
                Register
              </button>
            </form>

            <p className="auth-link">
              Already have an account? <Link to="/login">Login here</Link>
            </p>
          </>
        ) : (
          <>
            <h2>Upload Your Resume</h2>
            <p>Let's extract your skills to help you find better matches!</p>
            <ResumeUpload onSkillsExtracted={handleSkillsExtracted} />
          </>
        )}
      </div>
    </div>
  );
};

export default Register;