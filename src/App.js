import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Login from './Login';
import TeacherPage from './components/Teacher/TeacherPage';
import StudentPage from './components/Student/StudentPage';
import CreateTest from './components/Teacher/CreateTest';
import ViewTest from './components/Teacher/ViewTest';
import ViewMarks from './components/Student/ViewMarks';
import StartTest from './components/Student/StudentTest';
import EditTest from './components/Teacher/EditTest';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/teacher" element={<TeacherPage />} />
      <Route path="/student" element={<StudentPage />} />
      <Route path="/teacher/new_test" element={<CreateTest />} />
      <Route path="/teacher/view_test" element={<ViewTest />} />
      <Route path="/student/view_marks" element={<ViewMarks />} />
      <Route path="/student/start_test" element={<StartTest />} />
      <Route path="/teacher/edit_test" element={<EditTest />} /> 
      {/* Add more routes as needed */}
    </Routes>

  );
}

export default App;
