import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import './ViewMarks.css';

export default function ViewMarks() {
  const [marksData, setMarksData] = useState([]);
  const [studentName, setStudentName] = useState('');
  const [studentId, setStudentId] = useState('');
  const location = useLocation();

  useEffect(() => {
    const { name, id } = location.state || {};
    if (name && id) {
      setStudentName(name);
      setStudentId(id);

      fetch('http://localhost:5000/student/view_marks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ studentId: id })
      })
        .then(res => res.json())
        .then(data => {
          setMarksData(data.tests || []);
        })
        .catch(err => {
          console.error('שגיאה בקבלת ציונים:', err);
        });
    }
  }, [location]);

  return (
    <div className="marks-container">
      <h2 className="marks-title">שלום {studentName} (ת"ז: {studentId})</h2>
      {marksData.length === 0 ? (
        <p>לא נמצאו מבחנים עבור תלמיד זה.</p>
      ) : (
        marksData.map((test, index) => (
          <div key={index} className="test-card">
            <h3 className="test-title">מבחן מספר {test.testId}</h3>
            <h4 className="total-grade">ציון כולל: {test.totalGrade} / 100</h4>
            <table className="questions-table">
              <thead>
                <tr>
                  <th>שאלה</th>
                  <th>תשובתך</th>
                  <th>ציון</th>
                  <th>הסבר</th>
                </tr>
              </thead>
              <tbody>
                {test.questions.map((q, i) => (
                  <tr key={i}>
                    <td>{q.question}</td>
                    <td>{q.answer}</td>
                    <td>{q.grade}</td>
                    <td>{q.feedback}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))
      )}
    </div>
  );
}
