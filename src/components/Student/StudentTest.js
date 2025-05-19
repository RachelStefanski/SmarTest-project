import React, { useState, useEffect } from 'react';
import './StudentTest.css';

export default function StudentTest() {
  const [studentName, setStudentName] = useState('');
  const [studentId, setStudentId] = useState('');
  const [started, setStarted] = useState(false);
  const [timeLeft, setTimeLeft] = useState(0); // in seconds
  const [answers, setAnswers] = useState({});
  const [examData, setExamData] = useState(null);

  useEffect(() => {
    let timer;
    if (started && timeLeft > 0) {
      timer = setInterval(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
    } else if (timeLeft === 0 && started) {
      alert('הזמן נגמר! המבחן יישלח אוטומטית.');
      handleSubmit();
    }
    return () => clearInterval(timer);
  }, [started, timeLeft]);

  const handleStart = async () => {
    try {
      const response = await fetch(`http://localhost:5000/student/get_exam/${studentId}`);
      const data = await response.json();

      const currentTime = new Date();
      const examStartTime = new Date(data.startTime);

      if (currentTime < examStartTime) {
        alert('המבחן עדיין לא התחיל. אנא המתן.');
        return;
      }

      setExamData(data);
      setStarted(true);
      setTimeLeft(data.duration * 60); // Set timer from duration
    } catch (error) {
      console.error('שגיאה בטעינת המבחן:', error);
      alert('אירעה שגיאה בעת טעינת המבחן.');
    }
  };

  const handleAnswerChange = (workIndex, questionIndex, value) => {
    setAnswers((prev) => ({
      ...prev,
      [`${workIndex}-${questionIndex}`]: value,
    }));
  };

  const handleSubmit = () => {
    const submission = {
      studentName,
      studentId,
      submittedAt: new Date().toISOString(),
      answers,
    };
    console.log('Submission:', submission);
    alert('המבחן נשלח בהצלחה!');
    // כאן אפשר גם לשלוח לשרת: POST
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60).toString().padStart(2, '0');
    const secs = (seconds % 60).toString().padStart(2, '0');
    return `${mins}:${secs}`;
  };

  return (
    <div className="student-test-container">
      {!started ? (
        <div className="login-section">
          <h2>כניסת תלמיד</h2>
          <input
            type="text"
            placeholder="שם מלא"
            value={studentName}
            onChange={(e) => setStudentName(e.target.value)}
          />
          <input
            type="text"
            placeholder="תעודת זהות"
            value={studentId}
            onChange={(e) => setStudentId(e.target.value)}
          />
          <button onClick={handleStart}>התחל מבחן</button>
        </div>
      ) : examData ? (
        <div className="exam-section">
          <div className="exam-header">
            <h2>מבחן: {examData.title}</h2>
            <p>תלמיד: {studentName} | ת"ז: {studentId}</p>
            <p>זמן שנותר: {formatTime(timeLeft)}</p>
          </div>
          {examData.works.map((work, workIndex) => {
            const scorePerQuestion =
              work.questions.length > 0
                ? (parseFloat(work.weight) / work.questions.length).toFixed(2)
                : 0;
            return (
              <div key={workIndex} className="work-section">
                <h3>
                  עבודה: {work.name} (משקל: {work.weight} נקודות)
                </h3>
                {work.questions.map((question, questionIndex) => {
                  const answerKey = `${workIndex}-${questionIndex}`;
                  return (
                    <div key={questionIndex} className="question-section">
                      <p>
                        <strong>
                          שאלה {questionIndex + 1} ({scorePerQuestion} נקודות):
                        </strong>{' '}
                        {question.text}
                      </p>
                      {question.type === 'multiple' && (
                        <div className="options">
                          {question.options.map((option, optionIndex) => (
                            <label key={optionIndex}>
                              <input
                                type="radio"
                                name={answerKey}
                                value={option}
                                checked={answers[answerKey] === option}
                                onChange={(e) =>
                                  handleAnswerChange(workIndex, questionIndex, e.target.value)
                                }
                              />
                              {option}
                            </label>
                          ))}
                        </div>
                      )}
                      {question.type === 'truefalse' && (
                        <div className="options">
                          {['נכון', 'לא נכון'].map((option, optionIndex) => (
                            <label key={optionIndex}>
                              <input
                                type="radio"
                                name={answerKey}
                                value={option}
                                checked={answers[answerKey] === option}
                                onChange={(e) =>
                                  handleAnswerChange(workIndex, questionIndex, e.target.value)
                                }
                              />
                              {option}
                            </label>
                          ))}
                        </div>
                      )}
                      {question.type === 'open' && (
                        <textarea
                          rows="4"
                          placeholder="תשובתך כאן..."
                          value={answers[answerKey] || ''}
                          onChange={(e) =>
                            handleAnswerChange(workIndex, questionIndex, e.target.value)
                          }
                        />
                      )}
                    </div>
                  );
                })}
              </div>
            );
          })}
          <button onClick={handleSubmit}>שלח מבחן</button>
        </div>
      ) : (
        <p>טוען מבחן...</p>
      )}
    </div>
  );
}
