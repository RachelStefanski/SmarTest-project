import { useEffect, useState } from 'react'

function TeacherDashboard({ defaultView }) {
  const [message, setMessage] = useState('')

  useEffect(() => {
    if (defaultView === 'new') {
      fetchNewTest()
    } else if (defaultView === 'view') {
      fetchViewTest()
    }
  }, [defaultView])

  function fetchNewTest() {
    fetch('http://localhost:5000/teacher/new_test')
      .then(res => res.json())
      .then(data => setMessage(data.message))
  }

  function fetchViewTest() {
    fetch('http://localhost:5000/teacher/view_test')
      .then(res => res.json())
      .then(data => setMessage(data.message))
  }

  return (
    <div>
      <h2>דף מורה</h2>
      <button onClick={fetchNewTest}>מבחן חדש</button>
      <button onClick={fetchViewTest}>צפה במבחנים</button>
      <div>{message}</div>
    </div>
  )
}

export default TeacherDashboard
