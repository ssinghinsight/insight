import React, { useState } from 'react'
import Dashboard from './pages/Dashboard.jsx'
import CompanyDetail from './pages/CompanyDetail.jsx'

export default function App() {
  const [selectedId, setSelectedId] = useState(null)

  return (
    <div>
      {selectedId ? (
        <CompanyDetail id={selectedId} onBack={() => setSelectedId(null)} />
      ) : (
        <Dashboard onSelect={setSelectedId} />
      )}
    </div>
  )
}
