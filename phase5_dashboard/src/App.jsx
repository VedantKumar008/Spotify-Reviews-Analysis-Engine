import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import UserSegments from './pages/UserSegments'
import Insights from './pages/Insights'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/segments" element={<UserSegments />} />
          <Route path="/insights" element={<Insights />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
