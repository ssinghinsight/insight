import React, { useEffect, useState, useCallback } from 'react'
import { getCompanies, syncSalesforce, enrichAll, sendDigest } from '../api.js'
import CompanyCard from '../components/CompanyCard.jsx'
import FilterBar from '../components/FilterBar.jsx'

const s = {
  page: { maxWidth: 1100, margin: '0 auto', padding: '32px 24px' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 32 },
  title: { fontSize: 26, fontWeight: 800, color: '#0f172a', margin: 0 },
  subtitle: { fontSize: 13, color: '#6b7280', marginTop: 4 },
  actions: { display: 'flex', gap: 8 },
  btn: (variant = 'default') => ({
    padding: '8px 14px', borderRadius: 7, fontSize: 13, fontWeight: 600, cursor: 'pointer',
    border: '1px solid',
    ...(variant === 'primary'
      ? { background: '#0f172a', color: 'white', borderColor: '#0f172a' }
      : variant === 'danger'
      ? { background: '#ef4444', color: 'white', borderColor: '#ef4444' }
      : { background: 'white', color: '#374151', borderColor: '#e2e8f0' }),
  }),
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: 16 },
  status: { fontSize: 13, color: '#6b7280', padding: '4px 10px', borderRadius: 6, background: '#f1f5f9' },
  empty: { textAlign: 'center', padding: '60px 0', color: '#9ca3af', fontSize: 15 },
  loading: { textAlign: 'center', padding: '60px 0', color: '#6b7280' },
}

export default function Dashboard({ onSelect }) {
  const [companies, setCompanies] = useState([])
  const [filters, setFilters] = useState({ sort: 'priority' })
  const [loading, setLoading] = useState(true)
  const [actionStatus, setActionStatus] = useState('')

  const loadCompanies = useCallback(async () => {
    setLoading(true)
    try {
      const params = {}
      if (filters.priority) params.priority = filters.priority
      if (filters.sort) params.sort = filters.sort
      if (filters.has_cracking_brief) params.has_cracking_brief = true
      const data = await getCompanies(params)
      setCompanies(data)
    } catch (err) {
      setActionStatus('Error loading companies.')
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => { loadCompanies() }, [loadCompanies])

  const handleSync = async () => {
    setActionStatus('Syncing Salesforce…')
    try {
      const res = await syncSalesforce()
      setActionStatus(res.message)
      await loadCompanies()
    } catch {
      setActionStatus('Sync failed.')
    }
  }

  const handleEnrich = async () => {
    setActionStatus('Enriching all companies (this may take a minute)…')
    try {
      const res = await enrichAll()
      setActionStatus(`Enriched ${res.enriched} companies.`)
      await loadCompanies()
    } catch {
      setActionStatus('Enrichment failed.')
    }
  }

  const handleDigest = async () => {
    setActionStatus('Sending digest…')
    try {
      const res = await sendDigest()
      setActionStatus(res.message)
    } catch {
      setActionStatus('Digest send failed.')
    }
  }

  return (
    <div style={s.page}>
      <div style={s.header}>
        <div>
          <h1 style={s.title}>Insight</h1>
          <div style={s.subtitle}>{companies.length} companies tracked</div>
        </div>
        <div style={s.actions}>
          {actionStatus && <span style={s.status}>{actionStatus}</span>}
          <button style={s.btn()} onClick={handleSync}>↓ Sync Salesforce</button>
          <button style={s.btn()} onClick={handleEnrich}>⚡ Enrich All</button>
          <button style={s.btn('danger')} onClick={handleDigest}>✉ Send Digest</button>
        </div>
      </div>

      <FilterBar filters={filters} onChange={setFilters} />

      {loading ? (
        <div style={s.loading}>Loading companies…</div>
      ) : companies.length === 0 ? (
        <div style={s.empty}>
          No companies found.<br />
          <small>Try syncing from Salesforce first.</small>
        </div>
      ) : (
        <div style={s.grid}>
          {companies.map(c => (
            <CompanyCard key={c.id} company={c} onClick={onSelect} />
          ))}
        </div>
      )}
    </div>
  )
}
