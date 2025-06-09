import React, { useEffect, useState } from 'react';

export default function ViewMarks() {
  const studentName = 'John Doe';
  const studentId = '123456789';
  const [marksData, setMarksData] = useState([]);

  useEffect(() => {
    fetch('/get_student_tests', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ student_id: studentId }),
    })
      .then(res => {
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      })
      .then(data => {
        console.log('Raw data from server:', data);

        const studentExams = data.student_tests.filter(s => s.final_score !== undefined);

        const formattedData = studentExams.map((exam, index) => ({
          testId: exam.test_name || `Test ${index + 1}`,
          totalGrade: exam.final_score,
          generalFeedback: exam.general_feedback || 'No general feedback received.',
          questions: Array.isArray(exam.answers)
            ? exam.answers.map(ans => {
                console.log('Processing answer:', ans);
                return {
                  questionId: ans.question_id,
                  question: ans.teacher_question || `Question ${ans.question_id}`,
                  teacherAnswer: ans.teacher_answer || 'No teacher answer provided.',
                  answer: ans.answer || '',
                  grade: ans.score ?? 'N/A',
                  maxGrade: ans.max_score ?? 100,
                  feedback: Array.isArray(ans.remark)
                    ? ans.remark.join('\n')
                    : 'No feedback received.',
                };
              })
            : [],
        }));

        console.log('Formatted data:', formattedData);

        setMarksData(formattedData);
      })
      .catch(err => {
        console.error('Error loading data:', err);
        setMarksData([]);
      });
  }, [studentId]);

  return (
    <div
      dir="ltr"
      style={{
        maxWidth: 1000,
        margin: '0 auto',
        padding: 30,
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        textAlign: 'left',
      }}
    >
      <h2 style={{ fontSize: 28, color: '#2c3e50', marginBottom: 30 }}>
        Hello {studentName} (ID: {studentId})
      </h2>

      {marksData.length === 0 ? (
        <p>No tests found for this student.</p>
      ) : (
        marksData.map((test, index) => (
          <div
            key={index}
            style={{
              backgroundColor: '#f9f9f9',
              border: '2px solid #dedede',
              borderRadius: 10,
              padding: 25,
              marginBottom: 30,
            }}
          >
            <h3 style={{ fontSize: 22, color: '#34495e', marginBottom: 10 }}>
              Test: {test.testId}
            </h3>
            <h4
              style={{
                fontSize: 20,
                fontWeight: 'bold',
                color: '#27ae60',
                marginBottom: 10,
              }}
            >
              Total Score: {test.totalGrade} / 100
            </h4>
            <p
              style={{
                fontSize: 16,
                fontStyle: 'italic',
                color: '#555',
                marginBottom: 20,
                whiteSpace: 'pre-line',
              }}
            >
              General Feedback: {test.generalFeedback}
            </p>

            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={thStyle}>Question (ID + Text)</th>
                  <th style={thStyle}>Teacher's Answer</th>
                  <th style={thStyle}>Your Answer</th>
                  <th style={{ ...thStyle, textAlign: 'center' }}>Score</th>
                  <th style={thStyle}>Feedback</th>
                </tr>
              </thead>
              <tbody>
                {test.questions.map((q, i) => (
                  <tr key={i} style={{ verticalAlign: 'top' }}>
                    <td style={tdStyle}>
                      <div style={{ fontWeight: 'bold', marginBottom: 4 }}>{q.questionId}</div>
                      <div>{q.question}</div>
                    </td>
                    <td style={tdStyle}>{q.teacherAnswer}</td>
                    <td style={tdStyle}>{q.answer}</td>
                    <td
                      style={{
                        ...tdStyle,
                        textAlign: 'center',
                        color:
                          typeof q.grade === 'number' && q.grade < q.maxGrade / 2
                            ? 'red'
                            : 'black',
                      }}
                    >
                      {q.grade} / {q.maxGrade}
                    </td>
                    <td style={{ ...tdStyle, whiteSpace: 'pre-line' }}>{q.feedback}</td>
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

const thStyle = {
  padding: 12,
  border: '1px solid #ccc',
  backgroundColor: '#eaeaea',
  fontSize: 16,
  textAlign: 'left',
};

const tdStyle = {
  padding: 12,
  border: '1px solid #ccc',
  fontSize: 16,
};
