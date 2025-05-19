import React, { useState, useEffect } from 'react';
import './TeacherPage.css';
import { useNavigate, useLocation } from 'react-router-dom';

export default function TeacherPage() {
  const [message, setMessage] = useState('');
  const [teacherName, setTeacherName] = useState('');
  const [teacherId, setTeacherId] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const { name, id } = location.state || {};
    if (name && id) {
      setTeacherName(name);
      setTeacherId(id);
    } else {
      navigate('/');
    }
  }, [location, navigate]);

  const createTest = () => {
    setError('');
    navigate('/teacher/new_test', {
      state: {
        teacherId: teacherId,
        teacherName: teacherName
      }
    });
  };
  
  const viewTests2 = () => {
    setError('');
    navigate('/teacher/edit_test', {
      state: {
        teacherId: teacherId
      }
    });
  };

  return (
    <div className="teacher-container">
      <div className="welcome-section">
        <h2 className="welcome-message">
          שלום {teacherName} (ת"ז: {teacherId})
        </h2>
        <p className="intro-text">בחר את הפעולה שברצונך לבצע:</p>
      </div>
      <div className="actions-section">
        <button className="action-button" onClick={createTest}>צור מבחן</button>
        <button className="action-button" onClick={viewTests2}>צפה במבחנים</button>
      </div>
      <div id="result" className="result-message">{message}</div>
      {error && <div className="error-message">{error}</div>}
    </div>
  );
}
