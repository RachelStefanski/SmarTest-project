import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './CreateTest.css'; // עיצוב זהה לדפי יצירת מבחן

export default function ViewTest({ teacherID }) {
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const id = teacherID || localStorage.getItem('teacherID');
    if (!id) {
      setError('לא נמצא מזהה מורה. אנא התחבר שוב.');
      setLoading(false);
      return;
    }

    fetch(`http://localhost:5000/teacher/tests?teacherID=${id}`)
      .then((res) => {
        if (!res.ok) throw new Error('בעיה בשליפת המבחנים מהשרת');
        return res.json();
      })
      .then((data) => {
        setTests(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("שגיאה בטעינת מבחנים:", err);
        setError('אירעה שגיאה בטעינת המבחנים. נסה שוב מאוחר יותר.');
        setLoading(false);
      });
  }, [teacherID]);

  const handleEdit = (testId) => {
    navigate(`/teacher/edit_test/${testId}`);
  };

  const handleViewScores = (testId) => {
    navigate(`/teacher/view_scores/${testId}`);
  };

  if (loading) return <div>טוען מבחנים...</div>;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div className="create-exam-container">
      <h1>רשימת מבחנים של מורה</h1>
      {tests.length === 0 ? (
        <p>אין מבחנים להצגה.</p>
      ) : (
        <div className="tests-list">
          {tests.map((test, index) => (
            <div key={index} className="work-card">
              <h3>מבחן #{index + 1}</h3>
              <p><strong>תלמיד:</strong> {test.studentName}</p>
              <p><strong>ת"ז:</strong> {test.studentID}</p>
              <p><strong>זמן התחלה:</strong> {test.startTime}</p>
              <p><strong>משך:</strong> {test.duration} דקות</p>
              <button onClick={() => handleEdit(test.id)}>ערוך מבחן</button>
              <button onClick={() => handleViewScores(test.id)}>הצג ציונים</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
