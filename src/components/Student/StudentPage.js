import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './StudentPage.css';

export default function StudentPage() {
  const [message, setMessage] = useState('');
  const [studentName, setStudentName] = useState('');
  const [studentId, setStudentId] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const { name, id } = location.state || {};
    if (name && id) {
      setStudentName(name);
      setStudentId(id);
    } else {
      // אם לא הגיעו נתונים – חזרה לעמוד התחברות
      navigate('/');
    }
  }, [location, navigate]);

  const startTest = () => {
    navigate('/student/start_test');
  };
  const handleEdit = (testId) => {
    navigate(`/teacher/edit_test/${testId}`);
  };

  const viewMarks = () => {
    fetch('http://localhost:5000/student/view_marks')
      .then(res => res.json())
      .then(data => setMessage(data.message));
  };

  return (
    <div className="student-container">
      <div className="welcome-section">
        <h2 className="welcome-message">שלום {studentName} (ת"ז: {studentId})</h2>
        <p className="intro-text">בחר את הפעולה שברצונך לבצע:</p>
      </div>
      <div className="actions-section">
        <button className="action-button" onClick={startTest}>התחל מבחן</button>
        <button className="action-button" onClick={viewMarks}>צפה בציונים</button>
      </div>
      <div id="result" className="result-message">{message}</div>
    </div>
  );
}
