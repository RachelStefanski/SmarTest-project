// CreateTest.js
import React, { useState } from 'react';
import './CreateTest.css';
import axios from 'axios';

export default function CreateTest({ teacherId }) {
  const [testName, setTestName] = useState('');
  const [startTime, setStartTime] = useState('');
  const [duration, setDuration] = useState('');
  const [works, setWorks] = useState([]);
  const [error, setError] = useState('');

  const addWork = () => {
    setWorks([...works, { title: '', weight: '', questions: [] }]);
  };

  const updateWork = (index, field, value) => {
    const updated = [...works];
    updated[index][field] = value;
    setWorks(updated);
  };

  const addQuestion = (wIndex) => {
    const work = works[wIndex];
    if (work.questions.length > 0) {
      const lastQ = work.questions[work.questions.length - 1];
      if (!lastQ.text || !lastQ.answer) {
        setError('נא להשלים את השאלה הקודמת לפני הוספת חדשה');
        return;
      }
    }
    const updated = [...works];
    updated[wIndex].questions.push({ text: '', answer: '' });
    setWorks(updated);
  };

  const updateQuestion = (wIndex, qIndex, field, value) => {
    const updated = [...works];
    updated[wIndex].questions[qIndex][field] = value;
    setWorks(updated);
  };

  const deleteQuestion = (wIndex, qIndex) => {
    const updated = [...works];
    updated[wIndex].questions.splice(qIndex, 1);
    setWorks(updated);
  };

  const validate = () => {
    if (!testName || !startTime || !duration) {
      setError('יש למלא את כל השדות');
      return false;
    }
    const total = works.reduce((sum, w) => sum + Number(w.weight || 0), 0);
    if (total !== 100) {
      setError('סך כל המשקלים של העבודות חייב להיות בדיוק 100');
      return false;
    }
    for (const w of works) {
      if (!w.title || !w.weight) {
        setError('יש למלא את כל שדות העבודות');
        return false;
      }
      for (const q of w.questions) {
        if (!q.text || !q.answer) {
          setError('יש למלא את כל השאלות והתשובות');
          return false;
        }
      }
    }
    return true;
  };

  const saveTest = async () => {
    if (!validate()) return;

    const newTest = {
      teacher_id: teacherId,
      test_name: testName,
      start_time: startTime,
      duration,
      works
    };
        try {
      await axios.post('/api/tests', newTest); // נדרש endpoint בצד שרת
      setError('המבחן נשמר בהצלחה!');
    } catch (e) {
      setError('שגיאה בשמירת המבחן');
    }
  };

  return (
    <div className="create-test-container">
      <h2>יצירת מבחן</h2>
      <input placeholder="שם מבחן" value={testName} onChange={e => setTestName(e.target.value)} required />
      <input type="datetime-local" value={startTime} onChange={e => setStartTime(e.target.value)} required />
      <input type="number" placeholder="משך (בדקות)" value={duration} onChange={e => setDuration(e.target.value)} required />
      <button onClick={addWork}>הוסף עבודה</button>

      {works.map((work, i) => (
        <div className="work-block" key={i}>
          <input placeholder="כותרת עבודה" value={work.title} onChange={e => updateWork(i, 'title', e.target.value)} required />
          <input type="number" placeholder="משקל (%)" value={work.weight} onChange={e => updateWork(i, 'weight', e.target.value)} required />
          <button onClick={() => addQuestion(i)}>הוסף שאלה</button>

          {work.questions.map((q, j) => (
            <div className="question-block" key={j}>
              <textarea placeholder="שאלה" value={q.text} onChange={e => updateQuestion(i, j, 'text', e.target.value)} required />
              <textarea placeholder="תשובת מורה" value={q.answer} onChange={e => updateQuestion(i, j, 'answer', e.target.value)} required />
              <button onClick={() => deleteQuestion(i, j)}>🗑️ מחק שאלה</button>
            </div>
          ))}
        </div>
      ))}

      <button onClick={saveTest}>שמור מבחן</button>
      {error && <p className="error">{error}</p>}
    </div>
  );
}
