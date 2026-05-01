import React, { useRef, useState } from 'react';
import api from '../../services/api';
import './TeacherQuiz.css';

const TeacherQuiz = () => {
  const [step, setStep] = useState('select'); // select, loading, quiz, results
  const [skillName, setSkillName] = useState('');
  const [quizData, setQuizData] = useState(null);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [generationProgress, setGenerationProgress] = useState({
    readyCount: 0,
    requiredCount: 10,
    message: '',
  });
  const isGeneratingRef = useRef(false);

  const waitForQuizPool = async (requestedSkill, maxWaitMs = 300000, intervalMs = 5000) => {
    const startTime = Date.now();
    let lastProgressMessage = '';

    while (Date.now() - startTime < maxWaitMs) {
      try {
        const res = await api.get('/quiz/get-quiz/', {
          params: { skill_name: requestedSkill },
          timeout: 15000,
          validateStatus: (statusCode) => [200, 202, 404].includes(statusCode),
        });

        if (res.status === 202 && res?.data?.in_progress) {
          lastProgressMessage = res.data.message || lastProgressMessage;
          setGenerationProgress({
            readyCount: res.data.ready_count || 0,
            requiredCount: res.data.required_count || 10,
            message: res.data.message || 'Generating quiz...',
          });
        }

        if (res?.data?.questions?.length >= 10) {
          return res.data;
        }
      } catch (pollErr) {
        throw pollErr;
      }

      await new Promise((resolve) => setTimeout(resolve, intervalMs));
    }

    if (lastProgressMessage) {
      setError(lastProgressMessage);
      setGenerationProgress((prev) => ({
        ...prev,
        message: lastProgressMessage,
      }));
    }

    return null;
  };

  // Step 1: Generate quiz for a skill
  const handleGenerateQuiz = async (e) => {
    e.preventDefault();
    if (isGeneratingRef.current) {
      return;
    }

    const requestedSkill = skillName.trim();

    if (!requestedSkill) {
      setError('Please enter a skill name');
      return;
    }

    isGeneratingRef.current = true;
    setLoading(true);
    setError('');
    setGenerationProgress({
      readyCount: 0,
      requiredCount: 10,
      message: 'Starting AI quiz generation...',
    });

    try {
      const genRes = await api.post('/quiz/generate-quiz/', {
        skill_name: requestedSkill,
        num_questions: 10,
      }, {
        timeout: 30000,
      });

      if (genRes.data.success) {
        setSkillName(genRes.data.skill_name || requestedSkill);
        setQuizData({
          skill_name: genRes.data.skill_name || requestedSkill,
          total_questions: genRes.data.total_questions || 0,
          questions: genRes.data.questions || [],
        });
        setAnswers({});
        setStep('quiz');
      } else if (genRes.data.in_progress) {
        setError(genRes.data.message || 'Generating quiz. Please wait...');
        setGenerationProgress((prev) => ({
          ...prev,
          message: genRes.data.message || 'Generating quiz. Please wait...',
        }));

        const pooledQuiz = await waitForQuizPool(requestedSkill);
        if (pooledQuiz?.questions?.length) {
          setSkillName(pooledQuiz.skill_name || requestedSkill);
          setQuizData(pooledQuiz);
          setAnswers({});
          setStep('quiz');
          setError('');
          setGenerationProgress({
            readyCount: 10,
            requiredCount: 10,
            message: '',
          });
        } else {
          setError('Quiz is still generating. Please click Start Quiz again in a few seconds.');
        }
      } else {
        setError(genRes.data.message || 'Failed to generate quiz. Please try again.');
      }
    } catch (err) {
      // If generation finished but response was interrupted, recover by fetching the latest saved quiz.
      try {
        const fallbackRes = await api.get('/quiz/get-quiz/', {
          params: { skill_name: requestedSkill },
          timeout: 30000,
        });

        if (fallbackRes?.data?.questions?.length >= 10) {
          setSkillName(fallbackRes.data.skill_name || requestedSkill);
          setQuizData(fallbackRes.data);
          setAnswers({});
          setStep('quiz');
          setError('Generation completed after a connection delay. Loaded the latest quiz.');
          return;
        }
      } catch (fallbackErr) {
        // Continue to show original generation error.
      }

      setError(err.response?.data?.error || 'Failed to generate quiz. Make sure Ollama is running.');
    } finally {
      isGeneratingRef.current = false;
      setLoading(false);
    }
  };

  // Step 2: Handle answer selection
  const handleAnswerChange = (questionId, optionIndex) => {
    setAnswers({
      ...answers,
      [questionId]: optionIndex,
    });
  };

  // Step 3: Submit quiz
  const handleSubmitQuiz = async (e) => {
    e.preventDefault();
    
    if (Object.keys(answers).length !== quizData.questions.length) {
      setError('Please answer all questions');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const res = await api.post('/quiz/submit-quiz/', {
        skill_name: skillName,
        answers: answers,
      });

      setResults(res.data);
      setStep('results');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to submit quiz');
    } finally {
      setLoading(false);
    }
  };

  // Reset and start over
  const handleReset = () => {
    setStep('select');
    setSkillName('');
    setQuizData(null);
    setAnswers({});
    setResults(null);
    setError('');
  };

  return (
    <div className="quiz-container">
      <h1 className="page-title">Skill Verification Quiz</h1>
      <p className="quiz-subtitle">
        Get verified in your skills and build trust with learners
      </p>

      {/* Step 1: Select Skill */}
      {step === 'select' && (
        <div className="quiz-card">
          <h2>Choose a Skill to Verify</h2>
          <form onSubmit={handleGenerateQuiz}>
            <div className="form-group">
              <label>Skill Name</label>
              <input
                type="text"
                placeholder="e.g., Python, JavaScript, UI Design"
                value={skillName}
                onChange={(e) => setSkillName(e.target.value)}
                className="input-field"
              />
              <small>Enter the skill you want to get verified in</small>
            </div>

            {error && <div className="error-message">{error}</div>}

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
            >
              {loading ? 'Generating Quiz...' : 'Start Quiz'}
            </button>

            {loading && (
              <div className="generation-progress" role="status" aria-live="polite">
                <div className="generation-progress-header">
                  <span>Building your 10-question quiz</span>
                  <span>{generationProgress.readyCount}/{generationProgress.requiredCount}</span>
                </div>
                <div className="generation-progress-track">
                  <div
                    className="generation-progress-fill"
                    style={{
                      width: `${Math.max(5, Math.min(100, Math.round((generationProgress.readyCount / (generationProgress.requiredCount || 10)) * 100)))}%`,
                    }}
                  />
                </div>
                <p className="generation-progress-message">
                  {generationProgress.message || 'Generating with AI. This can take a few minutes for new skills.'}
                </p>
              </div>
            )}
          </form>
        </div>
      )}

      {/* Step 2: Take Quiz */}
      {step === 'quiz' && quizData && (
        <div className="quiz-card">
          <div className="quiz-header">
            <h2>{quizData.skill_name} Quiz</h2>
            <p>{quizData.total_questions} Questions</p>
          </div>

          <form onSubmit={handleSubmitQuiz}>
            {quizData.questions.map((question, index) => (
              <div key={question.id} className="question-block">
                <h3>
                  Question {index + 1}: {question.question}
                </h3>
                <div className="options">
                  {question.options.map((option, optionIndex) => (
                    <label key={optionIndex} className="option-label">
                      <input
                        type="radio"
                        name={`question-${question.id}`}
                        value={optionIndex}
                        checked={answers[question.id] === optionIndex}
                        onChange={() => handleAnswerChange(question.id, optionIndex)}
                      />
                      <span className="option-text">{option}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}

            {error && <div className="error-message">{error}</div>}

            <div className="button-group">
              <button
                type="button"
                onClick={handleReset}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="btn btn-primary"
              >
                {loading ? 'Submitting...' : 'Submit Quiz'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Step 3: Results */}
      {step === 'results' && results && (
        <div className="quiz-card">
          <div className={`results-banner ${results.is_verified ? 'success' : 'failed'}`}>
            <h2>Quiz Complete!</h2>
            <div className="score-display">
              <span className="score">{results.score}%</span>
              <span className="message">{results.message}</span>
            </div>
          </div>

          <div className="results-details">
            <div className="result-stat">
              <span className="stat-label">Correct Answers</span>
              <span className="stat-value">
                {results.correct_answers} / {results.total_questions}
              </span>
            </div>
            <div className="result-stat">
              <span className="stat-label">Status</span>
              <span className={`stat-value ${results.is_verified ? 'verified' : 'not-verified'}`}>
                {results.is_verified ? (
                  <>
                    <span className="status-icon" aria-hidden="true">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 3 5 6v6c0 5 3.4 8 7 9 3.6-1 7-4 7-9V6l-7-3Z" />
                        <path d="m9 12 2 2 4-4" />
                      </svg>
                    </span>
                    Verified
                  </>
                ) : (
                  <>
                    <span className="status-icon" aria-hidden="true">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 3 5 6v6c0 5 3.4 8 7 9 3.6-1 7-4 7-9V6l-7-3Z" />
                        <path d="M9.5 9.5 14.5 14.5M14.5 9.5l-5 5" />
                      </svg>
                    </span>
                    Not Verified
                  </>
                )}
              </span>
            </div>
          </div>

          {!results.is_verified && (
            <div className="warning-box">
              <strong>Need 70% to verify</strong>
              <p>Practice more and take the quiz again!</p>
            </div>
          )}

          <div className="button-group">
            <button onClick={handleReset} className="btn btn-primary">
              Take Another Quiz
            </button>
          </div>

          {/* Show detailed results */}
          {results.results && results.results.length > 0 && (
            <div className="detailed-results">
              <h3>Review Your Answers</h3>
              {results.results.map((result, index) => (
                <div key={index} className={`result-item ${result.is_correct ? 'correct' : 'incorrect'}`}>
                  <div className="result-icon">
                    {result.is_correct ? (
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                        <path d="M20 6 9 17l-5-5" />
                      </svg>
                    ) : (
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                        <path d="M18 6 6 18M6 6l12 12" />
                      </svg>
                    )}
                  </div>
                  <div className="result-content">
                    <p className="result-question">Q{index + 1}: {result.question}</p>
                    <p className="result-answer">
                      Your answer: <strong>{result.user_answer_text ||'Not answered'}</strong>
                    </p>
                    {!result.is_correct && (
                      <p className="result-correct">
                        Correct answer: <strong>{result.correct_answer_text || 'Option ' + String.fromCharCode(65 + result.correct_answer_index)}</strong>
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TeacherQuiz;
