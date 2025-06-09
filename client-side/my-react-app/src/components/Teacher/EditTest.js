import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';

export default function EditTest() {
  const [tests, setTests] = useState([]);
  const [editedTests, setEditedTests] = useState({});
  const location = useLocation();
  const teacherId = location.state?.id;

  useEffect(() => {
    const fetchTests = async () => {
      try {
        const res = await fetch('/files/tests.json');
        const data = await res.json();
        setTests(data);
      } catch (err) {
        console.error('שגיאה בטעינת מבחנים:', err);
      }
    };
    fetchTests();
  }, []);

  const handleChange = (testId, field, value) => {
    setEditedTests(prev => ({
      ...prev,
      [testId]: {
        ...prev[testId],
        [field]: value
      }
    }));
  };

  const handleQuestionChange = (testId, index, field, value) => {
    const test = editedTests[testId] || tests.find(t => t.id === testId);
    const questions = [...(test.questions || [])];
    questions[index] = {
      ...questions[index],
      [field]: value
    };
    handleChange(testId, 'questions', questions);
  };

  const addQuestion = (testId) => {
    const test = editedTests[testId] || tests.find(t => t.id === testId);
    const questions = [...(test.questions || [])];
    questions.push({ text: '', teacherAnswer: '' });
    handleChange(testId, 'questions', questions);
  };

  const removeQuestion = (testId, index) => {
    const test = editedTests[testId] || tests.find(t => t.id === testId);
    const questions = [...(test.questions || [])];
    questions.splice(index, 1);
    handleChange(testId, 'questions', questions);
  };

  const handleSave = async (testId) => {
    const updatedTest = {
      ...tests.find(t => t.id === testId),
      ...editedTests[testId]
    };

    const updatedTests = tests.map(t =>
      t.id === testId ? updatedTest : t
    );

    try {
      await fetch('/save_tests', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedTests)
      });
      alert('המבחן נשמר בהצלחה');
      setTests(updatedTests);
      setEditedTests(prev => {
        const newEdits = { ...prev };
        delete newEdits[testId];
        return newEdits;
      });
    } catch (err) {
      console.error('שגיאה בשמירה:', err);
    }
  };

  const teacherTests = tests.filter(test => test.teacherId === teacherId);

  return (
    <div style={{ padding: '2rem' }}>
      <h2>עריכת מבחנים</h2>
      {teacherTests.length === 0 ? (
        <p>לא נמצאו מבחנים</p>
      ) : (
        teacherTests.map(test => {
          const edited = editedTests[test.id] || test;
          return (
            <div key={test.id} style={{ border: '1px solid #ccc', padding: '1rem', marginBottom: '2rem' }}>
              <label>שם המבחן: </label>
              <input
                value={edited.title}
                onChange={e => handleChange(test.id, 'title', e.target.value)}
              /><br />
              <label>תיאור: </label>
              <input
                value={edited.description || ''}
                onChange={e => handleChange(test.id, 'description', e.target.value)}
              /><br />

              <h4>שאלות:</h4>
              {(edited.questions || []).map((q, i) => (
                <div key={i} style={{ marginBottom: '1rem' }}>
                  <label>שאלה {i + 1}:</label>
                  <input
                    value={q.text}
                    onChange={e => handleQuestionChange(test.id, i, 'text', e.target.value)}
                    placeholder="טקסט השאלה"
                    style={{ width: '80%' }}
                  /><br />
                  <label>תשובת מורה:</label>
                  <input
                    value={q.teacherAnswer}
                    onChange={e => handleQuestionChange(test.id, i, 'teacherAnswer', e.target.value)}
                    placeholder="תשובת מורה"
                    style={{ width: '80%' }}
                  /><br />
                  <button onClick={() => removeQuestion(test.id, i)}>מחק שאלה</button>
                </div>
              ))}
              <button onClick={() => addQuestion(test.id)}>הוסף שאלה</button><br /><br />
              <button onClick={() => handleSave(test.id)}>שמור</button>
            </div>
          );
        })
      )}
    </div>
  );
}
