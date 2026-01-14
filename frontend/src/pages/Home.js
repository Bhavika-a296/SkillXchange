import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';

const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="home">
      <div className="home-grid-bg"></div>

      <section className="hero">
        <div className="hero-content">
          <span className="hero-badge">Professional Skill Exchange Platform</span>
          <h1>Master New Skills, Share Your Expertise</h1>
          <p>Connect with professionals worldwide to exchange knowledge and accelerate your career growth</p>
          <div className="hero-actions">
            <button className="btn-primary" onClick={() => navigate('/login')}>
              <span>Get Started</span>
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M7.5 15L12.5 10L7.5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
            <button className="btn-secondary" onClick={() => navigate('/skills')}>
              Learn More
            </button>
          </div>
        </div>
      </section>

      <section className="features-section">
        <div className="section-header">
          <h2>Why Choose SkillXchange?</h2>
          <p>Everything you need to grow professionally</p>
        </div>
        
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon-wrapper">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z" fill="currentColor"/>
              </svg>
            </div>
            <h3>Real-Time Communication</h3>
            <p>Instant messaging and video calls to facilitate seamless knowledge exchange</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon-wrapper">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                <path d="M9 11H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2zm2-7h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V9h14v11z" fill="currentColor"/>
              </svg>
            </div>
            <h3>Flexible Scheduling</h3>
            <p>Book sessions at your convenience with integrated calendar and time management</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon-wrapper">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" fill="currentColor"/>
              </svg>
            </div>
            <h3>Verified Profiles</h3>
            <p>All users are verified to ensure quality interactions and trustworthy exchanges</p>
          </div>
        </div>
      </section>

      <section className="how-it-works">
        <div className="section-header">
          <h2>How It Works</h2>
          <p>Simple steps to start your learning journey</p>
        </div>

        <div className="steps-container">
          <div className="step">
            <div className="step-number">1</div>
            <h3>Create Your Profile</h3>
            <p>Sign up and showcase your skills and what you want to learn</p>
          </div>
          <div className="step-connector"></div>
          <div className="step">
            <div className="step-number">2</div>
            <h3>Get Matched</h3>
            <p>Our system finds the perfect learning partner for your goals</p>
          </div>
          <div className="step-connector"></div>
          <div className="step">
            <div className="step-number">3</div>
            <h3>Start Exchanging</h3>
            <p>Connect, schedule sessions, and grow together</p>
          </div>
        </div>
      </section>

      <section className="cta-section">
        <div className="cta-content">
          <h2>Ready to Transform Your Career?</h2>
          <p>Join thousands of professionals already growing their skills on SkillXchange</p>
          <button className="btn-primary large" onClick={() => navigate('/login')}>
            <span>Start Your Journey</span>
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M7.5 15L12.5 10L7.5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>
      </section>
    </div>
  );
};

export default Home;