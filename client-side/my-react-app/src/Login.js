// src/Login.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './App.css';
import logo from './logo.png';

export default function Login() {
  const [id, setId] = useState('');
  const [error, setError] = useState('');
  const [teachers, setTeachers] = useState([]);
  const [students, setStudents] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const loadData = async () => {
      try {
        const teacherRes = await fetch('/files/teachers.json');
        const teacherData = await teacherRes.json();
        setTeachers(teacherData);

        const studentRes = await fetch('/files/students.json');
        const studentData = await studentRes.json();
        setStudents(studentData);
      } catch (err) {
        console.error('Error loading data:', err);
      }
    };

    loadData();
  }, []);

  const handleStart = () => {
    const teacher = teachers.find(t => t.teacherID === id);
    const student = students.find(s => s.id === id);

    if (teacher) {
      navigate('/teacher', {
        state: {
          name: `${teacher.firstName} ${teacher.lastName}`,
          id: teacher.teacherID
        }
      });
    } else if (student) {
      navigate('/student', {
        state: {
          name: student.name,
          id: student.id
        }
      });
    } else {
      setError('Invalid ID. Please try again.');
    }
  };

  return (
    <div className="app-container">
      <img src={logo} alt="EyeLink Logo" className="logo" />
      <input
        type="text"
        placeholder="Enter your ID"
        value={id}
        onChange={(e) => setId(e.target.value)}
        className="password-input"
      />
      {error && <div className="error-message">{error}</div>}
      <button className="start-button" onClick={handleStart}>
        Let's Start
      </button>
    </div>
  );
}
