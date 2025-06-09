import React, { useState, useEffect, useRef } from 'react';
import './CreateTest.css';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const QUESTION_TYPES = [
  { value: 'open', label: 'Open' },
  { value: 'multiple', label: 'Multiple Choice' },
  { value: 'yesno', label: 'Yes/No' }
];


export default function CreateTest({ teacherId }) {
  const navigate = useNavigate();
  const [testName, setTestName] = useState('');
  const [startTime, setStartTime] = useState('');
  const [duration, setDuration] = useState('');
  const [works, setWorks] = useState([]);
  const [classIds, setClassIds] = useState([]);
  const [allClasses, setAllClasses] = useState([]);
  const [error, setError] = useState('');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  /* ------------------------------------------------------------------ */
  /*                    LOAD CLASSES + CLOSE DROPDOWN                   */
  /* ------------------------------------------------------------------ */

  useEffect(() => {
    setAllClasses([
      { id: 'classA', name: 'class A' },
      { id: 'classB', name: 'class B' },
      { id: 'classC', name: 'class C' },
      { id: 'classD', name: 'class D' },
      { id: 'classE', name: 'class E' },
      { id: 'classF', name: 'class F' },
    ]);
  }, []);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  /* ------------------------------------------------------------------ */
  /*                              HELPERS                               */
  /* ------------------------------------------------------------------ */

  const handleClassToggle = (id) => {
    setClassIds(prev =>
      prev.includes(id) ? prev.filter(c => c !== id) : [...prev, id]
    );
  };

  /* ---------- WORKS & QUESTIONS ---------- */

  const addWork = () => {
    setWorks(prev => [...prev, { title: '', weight: '', questions: [] }]);
  };

  const updateWork = (index, field, value) => {
    setWorks(prev => {
      const updated = [...prev];
      updated[index][field] = value;
      return updated;
    });
  };

  const addQuestion = (wIndex) => {
    const work = works[wIndex];
    if (work.questions.length > 0) {
      const lastQ = work.questions[work.questions.length - 1];
      const lastIncomplete =
        !lastQ.text ||
        (lastQ.type === 'open' && !lastQ.answer) ||
        ((lastQ.type === 'multiple' || lastQ.type === 'yesno') &&
          (!lastQ.options || lastQ.options.length === 0));
      if (lastIncomplete) {
        setError('Please complete the last question before adding a new one');
        return;
      }
    }
    setWorks(prev => {
      const updated = [...prev];
      updated[wIndex].questions.push({ text: '', answer: '', type: 'open', options: [] });
      return updated;
    });
    setError('');
  };

  const updateQuestion = (wIndex, qIndex, field, value) => {
    setWorks(prev => {
      const updated = [...prev];
      const question = { ...updated[wIndex].questions[qIndex], [field]: value };

      if (field === 'type' && value === 'yesno') {
        question.options = ['yes', 'no'];
        question.answer = ''; // אפשר גם לשים 'yes' אם רוצים תשובה ברירת מחדל
      }

      updated[wIndex].questions[qIndex] = question;
      return updated;
    });
    setError('');
  };

  /* ---------- OPTIONS ---------- */

  const updateOption = (wIndex, qIndex, optionIndex, value) => {
    setWorks(prev => {
      const updated = [...prev];
      const opts = updated[wIndex].questions[qIndex].options || [];
      opts[optionIndex] = value;
      updated[wIndex].questions[qIndex].options = opts;
      return updated;
    });
  };

  const addOption = (wIndex, qIndex) => {
    setWorks(prev => {
      const updated = [...prev];
      const opts = updated[wIndex].questions[qIndex].options || [];
      opts.push('');
      updated[wIndex].questions[qIndex].options = opts;
      return updated;
    });
  };

  const deleteOption = (wIndex, qIndex, optionIndex) => {
    setWorks(prev => {
      const updated = [...prev];
      updated[wIndex].questions[qIndex].options.splice(optionIndex, 1);
      return updated;
    });
  };

  const deleteQuestion = (wIndex, qIndex) => {
    setWorks(prev => {
      const updated = [...prev];
      updated[wIndex].questions.splice(qIndex, 1);
      return updated;
    });
  };

  /* ------------------------------------------------------------------ */
  /*                             VALIDATION                             */
  /* ------------------------------------------------------------------ */

  const validate = () => {
    if (!testName || !startTime || !duration || classIds.length === 0) {
      setError('All fields and at least one class must be selected');
      return false;
    }
    const total = works.reduce((sum, w) => sum + Number(w.weight || 0), 0);
    if (total !== 100) {
      setError('Total weight of all works must be 100');
      return false;
    }
    for (const w of works) {
      if (!w.title || !w.weight) {
        setError('All work fields must be filled');
        return false;
      }
      for (const q of w.questions) {
        if (!q.text) {
          setError('All questions must be filled');
          return false;
        }
        if (q.type === 'open' && !q.answer) {
          setError('Open questions must have an answer');
          return false;
        }
        if ((q.type === 'multiple' || q.type === 'yesno')) {
          if (!q.options || q.options.length === 0) {
            setError('Choice questions must have options');
            return false;
          }
          if (!q.answer || !q.options.includes(q.answer)) {
            setError('Choice questions must have a selected answer');
            return false;
          }
        }
      }
    }
    setError('');
    return true;
  };

  /* ------------------------------------------------------------------ */
  /*                               SAVE                                 */
  /* ------------------------------------------------------------------ */

  const saveTest = async () => {
    if (!validate()) return;

    const newTest = {
      teacher_id: 123,  // מזהה מורה, ניתן לשנות לפי הצורך
      test_name: testName,
      start_time: startTime,
      duration_minutes: Number(duration),
      class_ids: classIds,
      works: works.map((w, wi) => ({
        work_id: wi + 1,
        work_title: w.title,
        score: Number(w.weight),
        questions: w.questions.map((q, qi) => ({
          question_id: `${wi + 1}_${qi + 1}`,
          type: q.type === 'yesno' ? 'yes_no' : q.type === 'multiple' ? 'multiple_choice' : 'open',
          question: q.text,
          model_answer: q.type === 'open' ? q.answer.split('\n') : [q.answer],
          weight: w.weight / w.questions.length,
          options: q.type === 'multiple' ? q.options : undefined
        })),
        // ✅ הוספת תשובות מורה
        answer_models: w.questions
          .filter(q => q.type === 'open')  // רק לשאלות פתוחות
          .map((q, qi) => ({
            question_id: `${wi + 1}_${qi + 1}`,
            answer: q.answer,  // אותה תשובה שכבר יש בשדה model_answer
          }))
      }))
    };

    try {
      console.log('newTest:', newTest);

      const response = await axios.post('/api/tests', newTest);
      alert(`Test "${newTest.test_name}" saved successfully!`);
      navigate(-1);
    } catch (err) {
      if (err.response && err.response.status === 409) {
        alert('A test with this name already exists');
        // setError('A test with this name already exists');
      } else if (err.response && err.response.data && err.response.data.error) {
        console.error('Server error:', err.response.data.error);
        setError(err.response.data.error);
      } else {
        console.error('Error saving test:', err);
        setError('An unexpected error occurred while saving the test');
      }
    }
  };

  /* ------------------------------------------------------------------ */
  /*                              RENDER                                */
  /* ------------------------------------------------------------------ */

  return (
    <div className="create-test-container">
      <h2>Create Test</h2>

      {/* --- BASIC INFO --- */}
      <input
        placeholder="Test Name"
        value={testName}
        onChange={e => setTestName(e.target.value)}
      />
      <input
        type="datetime-local"
        value={startTime}
        onChange={e => setStartTime(e.target.value)}
      />
      <input
        type="number"
        placeholder="Duration (minutes)"
        value={duration}
        onChange={e => setDuration(e.target.value)}
      />

      {/* --- CLASS SELECT --- */}
      <div
        className="class-select-container"
        ref={dropdownRef}
        style={{ position: 'relative', display: 'inline-block', marginTop: 10 }}
      >
        <button
          type="button"
          onClick={() => setIsDropdownOpen(prev => !prev)}
          className="dropdown-button"
        >
          Choose Classes ▼
        </button>

        {isDropdownOpen && (
          <div
            className="dropdown-list"
            style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              width: 200,
              maxHeight: 150,
              overflowY: 'auto',
              border: '1px solid #ccc',
              backgroundColor: 'white',
              zIndex: 10,
              padding: 5,
              boxShadow: '0 2px 6px rgba(0,0,0,0.2)',
              fontSize: 12,
            }}
          >
            {allClasses.map(c => (
              <label
                key={c.id}
                style={{ display: 'inline-flex', marginBottom: 5, cursor: 'pointer' }}
              >
                <input
                  type="checkbox"
                  checked={classIds.includes(c.id)}
                  onChange={() => handleClassToggle(c.id)}
                />
                &nbsp;{c.name}
              </label>
            ))}
          </div>
        )}
      </div>

      {/* --- SELECTED CLASSES --- */}
      <div style={{ marginTop: 10 }}>
        {classIds.length > 0 ? (
          <div>
            <strong>Selected Classes:&nbsp;</strong>
            {classIds.map((id, idx) => {
              const cls = allClasses.find(c => c.id === id);
              const name = cls?.name || id;
              const last = idx === classIds.length - 1;
              return (
                <span key={id} style={{ marginRight: 8 }}>
                  {name}
                  {!last && ','}
                </span>
              );
            })}
          </div>
        ) : (
          <div>No classes selected</div>
        )}
      </div>

      {/* --- WORKS --- */}
      <button type="button" onClick={addWork} style={{ marginTop: 15 }}>
        Add Work
      </button>

      {works.map((work, wi) => (
        <div
          key={wi}
          className="work-container"
          style={{ marginTop: 20, border: '1px solid #ddd', padding: 10 }}
        >
          <input
            placeholder="Work Title"
            value={work.title}
            onChange={e => updateWork(wi, 'title', e.target.value)}
          />
          <input
            type="number"
            placeholder="Weight (%)"
            value={work.weight}
            onChange={e => updateWork(wi, 'weight', e.target.value)}
            style={{ marginLeft: 10, width: 150 }}
          />
          <button
            type="button"
            onClick={() => addQuestion(wi)}
            style={{ marginLeft: 15, width: 150 }}
          >
            Add Question
          </button>

          {/* --- QUESTIONS --- */}
          {work.questions.map((q, qi) => (
            <div
              key={qi}
              className="question-container"
              style={{ marginTop: 10, paddingLeft: 10 }}
            >
              <input
                placeholder="Question Text"
                value={q.text}
                onChange={e => updateQuestion(wi, qi, 'text', e.target.value)}
                style={{ width: '100%' }}
              />
              <select
                value={q.type}
                onChange={e => updateQuestion(wi, qi, 'type', e.target.value)}
                style={{ marginLeft: 10 }}
              >
                {QUESTION_TYPES.map(opt => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>

              {/* --- OPEN QUESTION --- */}
              {q.type === 'open' && (
                <textarea
                  placeholder="Model answer"
                  value={q.answer}
                  onChange={e => updateQuestion(wi, qi, 'answer', e.target.value)}
                  style={{ display: 'block', width: '100%', marginTop: 5 }}
                />
              )}

              {/* --- CHOICE QUESTION --- */}
              {(q.type === 'multiple' || q.type === 'yesno') && (
                <div style={{ marginTop: 10 }}>
                  {q.options &&
                    q.options.map((opt, oi) => (
                      <div
                        key={oi}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          marginBottom: 8,
                          border: '1px solid #ddd',
                          padding: '8px 10px',
                          borderRadius: 8,
                          backgroundColor: '#f9f9f9',
                        }}
                      >
                        <input
                          type="radio"
                          name={`answer-${wi}-${qi}`}
                          value={opt}
                          checked={q.answer === opt}
                          onChange={() => updateQuestion(wi, qi, 'answer', opt)}
                          style={{
                            marginRight: 12,
                            width: 18,
                            height: 18,
                            flexShrink: 0,
                          }}
                          required
                        />
                        <input
                          type="text"
                          value={opt}
                          onChange={e => updateOption(wi, qi, oi, e.target.value)}
                          placeholder={`Option ${oi + 1}`}
                          style={{
                            flex: 1,
                            padding: 8,
                            fontSize: 15,
                            border: '1px solid #ccc',
                            borderRadius: 6,
                          }}
                          required
                          disabled={q.type === 'yesno'} // מנע עריכה באופציות yesno
                        />
                        {q.type === 'multiple' && (
                          <button
                            type="button"
                            onClick={() => deleteOption(wi, qi, oi)}
                            title="Delete option"
                            style={{
                              marginLeft: 10,
                              background: 'none',
                              border: 'none',
                              color: '#cc0000',
                              fontSize: 18,
                              cursor: 'pointer',
                            }}
                          >
                            🗑️
                          </button>
                        )}
                      </div>
                    ))}

                  {/* ADD OPTION BUTTON */}
                  {q.type === 'multiple' && (
                    <button
                      type="button"
                      onClick={() => {
                        const allFilled = q.options && q.options.every(o => o.trim() !== '');
                        if (allFilled) {
                          addOption(wi, qi);
                        } else {
                          alert('Please fill all options before adding a new one.');
                        }
                      }}
                      style={{
                        marginTop: 12,
                        padding: '8px 16px',
                        backgroundColor: '#007bff',
                        color: 'white',
                        border: 'none',
                        borderRadius: 6,
                        fontSize: 14,
                        cursor: 'pointer',
                      }}
                    >
                      ➕ Add Option
                    </button>
                  )}
                </div>
              )}

              <button
                type="button"
                onClick={() => deleteQuestion(wi, qi)}
                style={{ marginTop: 5, color: 'red' }}
              >
                Delete Question
              </button>
            </div>
          ))}
        </div>
      ))}

      {/* --- ERROR MESSAGE --- */}
      {error && (
        <div style={{ color: 'red', marginTop: 15 }}>{error}</div>
      )}

      {/* --- SAVE --- */}
      <button
        type="button"
        onClick={saveTest}
        style={{
          marginTop: 20,
          backgroundColor: '#4caf50',
          color: 'white',
          padding: '10px 20px',
          border: 'none',
          borderRadius: 4,
        }}
      >
        Save Test
      </button>
    </div>
  );
}
