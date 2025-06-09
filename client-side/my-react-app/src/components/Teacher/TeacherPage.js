import React, { useState, useEffect } from 'react';
import './TeacherPage.css';
import { useNavigate, useLocation } from 'react-router-dom';

export default function TeacherPage() {
  const [message, setMessage] = useState('');
  const [teacherName, setTeacherName] = useState('');
  const [teacherID, setTeacherID] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const { name, id } = location.state || {};
    if (name && id) {
      setTeacherName(name);
      setTeacherID(id);
    } else {
      navigate('/');
    }
  }, [location, navigate]);

  const createTest = () => {
    setError('');
    navigate('/teacher/new_test', {
      state: {
        teacherID: teacherID,
        teacherName: teacherName
      }
    });
  };

  const viewTests = () => {
    setError('');
    navigate('/teacher/view_test', {
      state: {
        teacherID: teacherID
      }
    });
  };

  return (
    <div className="teacher-container">
      <div className="welcome-section">
        <h2 className="welcome-message">
          Hello {teacherName} (ID: {teacherID})
        </h2>
        <p className="intro-text">Please choose an action:</p>
      </div>
      <div className="actions-section">
        <button className="action-button" onClick={createTest}>Create New Test</button>
        <button className="action-button" onClick={viewTests}>View Existing Tests</button>
      </div>
      <div id="result" className="result-message">{message}</div>
      {error && <div className="error-message">{error}</div>}
    </div>
  );
}
