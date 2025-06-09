// src/StudentTest.jsx
import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import './StudentTest.css';

function QuestionBlock({ q, selected, work, answer, updateAnswer }) {
  const radioName = `q-${selected.test_id}-${work.work_id}-${q.question_id}`;
  const handleChange = val => updateAnswer(q.question_id, val);

  return (
    <div className="question-container">
      <p className="question-text">Q{q.question_id}: {q.question}</p>
      <p className="question-meta">Weight: <strong>{q.weight}</strong> | Type: {q.type}</p>

      {q.type === 'open' && (
        <textarea
          className="answer-textarea full-width"
          placeholder="Type your answer here…"
          value={answer || ''}
          onChange={e => handleChange(e.target.value)}
        />
      )}

      {(q.type === 'yes_no' || q.type === 'multiple_choice') && (
        <div className="options-group">
          {(q.type === 'yes_no' ? ['yes', 'no'] : q.options || []).map((opt, idx) => (
            <label key={`${work.work_id}_${q.question_id}_opt_${idx}`}>
              <input
                type="radio"
                name={radioName}
                value={opt}
                checked={answer === opt}
                onChange={() => handleChange(opt)}
              />
              {opt.toString().toUpperCase()}
            </label>
          ))}
        </div>
      )}
    </div>
  );
}

export default function StudentTest() {
  const { state } = useLocation();
  const studentId = state?.id || localStorage.getItem('studentId') || null;
  const studentCls = 'classB';

  const [tests, setTests] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [timeLeft, setTimeLeft] = useState(0);
  const [answers, setAnswers] = useState({});
  const [submissions, setSubmissions] = useState([]);

  const formatTime = sec => {
    const m = Math.floor(sec / 60).toString().padStart(2, '0');
    const s = (sec % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  // Load available tests for the class with detailed logs
  useEffect(() => {
    if (!studentId) {
      setError('Missing student ID');
      console.error('Missing student ID');
      return;
    }
    setLoading(true);
    console.log(`Fetching available tests for class: ${studentCls}`);

    fetch(`/api/tests/available?class=${studentCls}`)
      .then(res => {
        console.log('Response status:', res.status);
        if (res.ok) return res.json();
        else return Promise.reject('Fetch error');
      })
      .then(data => {
        console.log('Fetched tests:', data);
        const now = Date.now();
        const openTests = data
          .filter(t => {
            const start = new Date(t.start_time).getTime();
            const end = start + (t.duration_minutes || 0) * 60000;
            return now >= start && now <= end;
          })
          .map(t => ({
            ...t,
            test_id:
              t.test_id ||
              `${t.test_name.replace(/\s+/g, '_').toLowerCase()}_${new Date(t.start_time).getTime()}`,
          }));
        setTests(openTests);
        console.log('Open tests after filtering:', openTests);
      })
      .catch(err => {
        setError('Failed to load tests');
        console.error('Failed to load tests:', err);
      })
      .finally(() => setLoading(false));
  }, [studentId, studentCls]);

  // Timer to manage selected test duration
  useEffect(() => {
    if (!selected) return;

    setTimeLeft(selected.duration_minutes * 60);
    const timerId = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(timerId);
          alert('⏰ Time is up! Auto submission will happen soon.');
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timerId);
  }, [selected]);

  const updateAnswer = (qId, val) => setAnswers(prev => ({ ...prev, [qId]: val }));

  const handleSubmit = () => {
    if (!selected || !studentId) {
      alert('Missing details, please try again.');
      return;
    }

    const submission = {
      student_id: studentId,
      test_name: selected.test_name,
      answers: selected.works.flatMap(work =>
        work.questions.map(q => ({
          question_id: q.question_id,
          answer: answers[q.question_id] || '',
          weight: q.weight,
        }))
      ),
    };

    fetch('/api/submit-answers', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(submission),
    })
      .then(res => {
        if (!res.ok) throw new Error('Submission failed');
        return res.json();
      })
      .then(() => {
        alert('✅ Test submitted successfully');
        setSubmissions(prev => [...prev, submission]);
        setAnswers({});
        setSelected(null);
      })
      .catch(() => alert('❌ Submission failed'));
  };

  if (loading) return <p className="loading">Loading…</p>;
  if (error) return <p className="error-message">{error}</p>;
  if (!tests.length) return <p className="no-tests-message">No open tests for {studentCls}</p>;

  if (selected) {
    return (
      <div className="test-container">
        <h2 className="test-title">{selected.test_name}</h2>
        <p className="test-meta">
          Teacher ID: {selected.teacher_id} | Class: {selected.class_ids?.join(', ')}
        </p>
        <p className="test-meta">
          Duration: {selected.duration_minutes} min | Start: {new Date(selected.start_time).toLocaleString()}
        </p>
        <div className="timer">⏳ {formatTime(timeLeft)}</div>

        {selected.works.map(work => (
          <div key={`${selected.test_id}_${work.work_id}`} className="work-container">
            <h3 className="work-title">{work.work_title}</h3>
            {work.questions.map(q => (
              <QuestionBlock
                key={`${selected.test_id}_${work.work_id}_${q.question_id}`}
                q={q}
                selected={selected}
                work={work}
                answer={answers[q.question_id]}
                updateAnswer={updateAnswer}
              />
            ))}
          </div>
        ))}

        <button className="submit-btn" onClick={handleSubmit}>Submit Answers</button>

        {submissions.length > 0 && (
          <div className="submissions-container">
            <h3>📝 Student Submissions</h3>
            <pre className="submission-json">{JSON.stringify({ students: submissions }, null, 2)}</pre>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="available-tests-container">
      <h2 className="available-tests-title">Available Tests – {studentCls}</h2>
      {tests.map(t => (
        <div key={t.test_id} className="test-card">
          <h3>{t.test_name}</h3>
          <p>Start: {new Date(t.start_time).toLocaleString()}</p>
          <p>Duration: {t.duration_minutes} min</p>
          <button className="start-btn" onClick={() => setSelected(t)}>Start Test</button>
        </div>
      ))}
    </div>
  );
}
