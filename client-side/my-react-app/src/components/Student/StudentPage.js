// src/StudentPage.jsx
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
      // If no data was received – redirect to login
      navigate('/');
    }
  }, [location, navigate]);

  const startTest = () => {
    navigate('/student/start_test', { state: { id: studentId } });
  };

  // If test editing becomes relevant – this function is ready but currently unused
  const handleEdit = (testId) => {
    navigate(`/teacher/edit_test/${testId}`);
  };

  const viewMarks = () => {
    navigate('/student/view_marks', { state: { name: studentName, id: studentId } });

    // Example logic if using server fetch:
    // if (!studentId) {
    //   setMessage('ID number is missing.');
    //   return;
    // }

    // fetch(`http://localhost:5000/student/view_marks?id=${encodeURIComponent(studentId)}`)
    //   .then(res => {
    //     if (!res.ok) {
    //       throw new Error('Server error');
    //     }
    //     return res.json();
    //   })
    //   .then(data => {
    //     if (data.message) {
    //       setMessage(data.message);
    //     } else if (data.marks) {
    //       setMessage('Grades loaded successfully.');
    //     } else {
    //       setMessage('No grades found.');
    //     }
    //   })
    //   .catch(err => {
    //     setMessage('An error occurred while loading grades.');
    //     console.error(err);
    //   });
  };

  return (
    <div className="student-container">
      <div className="welcome-section">
        <h2 className="welcome-message">Hello {studentName} (ID: {studentId})</h2>
        <p className="intro-text">Choose the action you want to perform:</p>
      </div>
      <div className="actions-section">
        <button className="action-button" onClick={startTest}>Start Test</button>
        <button className="action-button" onClick={viewMarks}>View Grades</button>
      </div>
      <div id="result" className="result-message">{message}</div>
    </div>
  );
}
