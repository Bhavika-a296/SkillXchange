import React, { useRef, useState } from 'react';
import api from '../../services/api';
import './LearnerQuiz.css';

const LearnerQuiz = ({ sessionId, skillName, onQuizComplete }) => {
  const [step, setStep] = useState('quiz'); // quiz, loading, results
  const [quizData, setQuizData] = useState(null);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [noticeType, setNoticeType] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [showResultsPopup, setShowResultsPopup] = useState(true); // Show/hide results popup
  const isLoadingRef = useRef(false);

  React.useEffect(() => {
    loadQuiz();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [skillName]);

  const loadQuiz = async () => {
    if (isLoadingRef.current) return;
    isLoadingRef.current = true;
    setLoading(true);
    setError('');
    setNoticeType('');

    try {
      const res = await api.get('/quiz/get-quiz/', {
        params: { skill_name: skillName },
        timeout: 30000,
        validateStatus: (statusCode) => [200, 202, 404].includes(statusCode),
      });

      if (res.status === 200 && res?.data?.questions?.length >= 10) {
        setQuizData(res.data);
        setAnswers({});
      } else if (res.status === 202) {
        setNoticeType('processing');
        setError('Quiz is still being generated. Please try again in a moment.');
      } else {
        setNoticeType('error');
        setError('Quiz not found. Please try again.');
      }
    } catch (err) {
      setNoticeType('error');
      setError('Error loading quiz. Please try again.');
      console.error('Error loading quiz:', err);
    } finally {
      setLoading(false);
      isLoadingRef.current = false;
    }
  };

  const handleAnswerSelect = (questionId, optionIndex) => {
    setAnswers({
      ...answers,
      [questionId]: optionIndex,
    });
  };

  const handleSubmitQuiz = async (e) => {
    e.preventDefault();
    
    if (!quizData?.questions || quizData.questions.length === 0) {
      setError('No questions loaded');
      return;
    }

    const answeredCount = Object.keys(answers).length;
    if (answeredCount < quizData.questions.length) {
      setError(`Please answer all questions (${answeredCount}/${quizData.questions.length})`);
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      const response = await api.post('/quiz/submit-learner-quiz/', {
        skill_name: skillName,
        learning_session_id: sessionId,
        answers: answers,
      });

      setResults(response.data);
      setStep('results');

      if (onQuizComplete) {
        onQuizComplete(response.data);
      }
    } catch (err) {
      setError(
        err.response?.data?.error ||
        'Error submitting quiz. Please try again.'
      );
      console.error('Error submitting quiz:', err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="learner-quiz-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading quiz...</p>
        </div>
      </div>
    );
  }

  if (step === 'results' && results) {
    return (
      <div className="learner-quiz-container">
        {/* Results Popup Modal */}
        {showResultsPopup && (
          <div className="results-popup-overlay">
            <div className={`results-popup ${results.is_verified ? 'verified' : 'not-verified'}`}>
              {results.is_verified ? (
                <>
                  <div className="popup-icon verified-icon">🎉</div>
                  <h2 className="popup-title">Skill Verified!</h2>
                  <p className="popup-subtitle">Congratulations!</p>
                  <div className="score-box verified">
                    <div className="score-number">{results.score}%</div>
                    <div className="score-label">Score Achieved</div>
                  </div>
                  <p className="popup-message">
                    {results.skill_name} is now marked as a learned skill on your profile. 
                    <br />
                    You can showcase this verified skill to other users!
                  </p>
                </>
              ) : (
                <>
                  <div className="popup-icon not-verified-icon">📚</div>
                  <h2 className="popup-title">Not Yet Passed</h2>
                  <p className="popup-subtitle">Keep Learning!</p>
                  <div className="score-box not-verified">
                    <div className="score-number">{results.score}%</div>
                    <div className="score-label">Your Score</div>
                  </div>
                  <div className="progress-needed">
                    <p>You need <strong>70%</strong> to verify this skill</p>
                    <div className="threshold-bar">
                      <div className="threshold-fill" style={{ width: `${Math.min(results.score, 100)}%` }}></div>
                    </div>
                    <p className="points-needed">{Math.max(0, 70 - results.score)}% more needed</p>
                  </div>
                  <p className="popup-message">
                    Review the questions below and try again. You'll get it next time!
                  </p>
                </>
              )}
              <button 
                className={`popup-close-btn ${results.is_verified ? 'verified' : 'not-verified'}`}
                onClick={() => setShowResultsPopup(false)}
              >
                View Detailed Results
              </button>
            </div>
          </div>
        )}

        {/* Detailed Results */}
        <div className="quiz-results">
          <div className={`results-header ${results.is_verified ? 'passed' : 'failed'}`}>
            <h2>{results.is_verified ? '✅ Skill Learned!' : '❌ Review Your Answers'}</h2>
            <p className="score-display">Score: {results.score}%</p>
            <p className="answers-count">
              {results.correct_answers} out of {results.total_questions} correct
            </p>
          </div>

          <div className="results-details">
            <h3>Question Review</h3>
            {results.results && results.results.map((result, idx) => (
              <div key={result.question_id} className={`result-item ${result.is_correct ? 'correct' : 'incorrect'}`}>
                <div className="result-question">
                  <span className="result-number">Q{idx + 1}.</span>
                  <p>{result.question}</p>
                </div>
                <div className="result-answer">
                  <div className="user-answer">
                    <strong>Your answer:</strong> {result.user_answer_text || 'Not answered'}
                    <span className={`answer-badge ${result.is_correct ? 'correct' : 'incorrect'}`}>
                      {result.is_correct ? '✓' : '✗'}
                    </span>
                  </div>
                  {!result.is_correct && (
                    <div className="correct-answer">
                      <strong>Correct answer:</strong> {result.correct_answer_text}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="results-footer">
            {results.is_verified ? (
              <button onClick={() => window.location.reload()} className="btn-primary">
                Return to Dashboard
              </button>
            ) : (
              <button onClick={() => window.location.reload()} className="btn-retry">
                Retake Quiz
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (!quizData || !quizData.questions || quizData.questions.length === 0) {
    return (
      <div className="learner-quiz-container">
        <div className={`error-message quiz-notice ${noticeType}`}>
          {error || 'Unable to load quiz questions.'}
          {noticeType === 'error' && (
            <button onClick={loadQuiz} className="btn-try-again" style={{ marginTop: '20px' }}>
              Try Again
            </button>
          )}
        </div>
      </div>
    );
  }

  const answeredCount = Object.keys(answers).length;
  const progressPercentage = (answeredCount / quizData.questions.length) * 100;

  return (
    <div className="learner-quiz-container">
      <form onSubmit={handleSubmitQuiz} className="learner-quiz-form">
        <div className="quiz-header">
          <h2>Quiz: {skillName}</h2>
          <p className="quiz-subtitle">
            {quizData.questions.length} Questions • Score {Math.round(progressPercentage)}% Complete
          </p>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${progressPercentage}%` }}
            ></div>
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="quiz-questions">
          {quizData.questions.map((question, idx) => (
            <div key={question.id} className="question-card">
              <div className="question-header">
                <h3>Question {idx + 1} of {quizData.questions.length}</h3>
                {answers[question.id] !== undefined && (
                  <span className="answered-badge">✓ Answered</span>
                )}
              </div>
              <p className="question-text">{question.question}</p>
              <div className="options-grid">
                {question.options.map((option, optionIdx) => (
                  <label key={optionIdx} className="option-label">
                    <input
                      type="radio"
                      name={`question-${question.id}`}
                      value={optionIdx}
                      checked={answers[question.id] === optionIdx}
                      onChange={() => handleAnswerSelect(question.id, optionIdx)}
                      disabled={submitting}
                    />
                    <span className="option-text">{option}</span>
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="quiz-footer">
          <p className="progress-text">
            Answered: {answeredCount} / {quizData.questions.length}
          </p>
          <button
            type="submit"
            className="btn-primary btn-submit"
            disabled={answeredCount < quizData.questions.length || submitting}
          >
            {submitting ? 'Submitting...' : `Submit Quiz (${answeredCount}/${quizData.questions.length})`}
          </button>
        </div>
      </form>
    </div>
  );
};

export default LearnerQuiz;
