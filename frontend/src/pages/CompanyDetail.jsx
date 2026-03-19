import React, { useEffect, useState } from 'react'
import { getCompany, enrichOne } from '../api.js'
import SignalFeed from '../components/SignalFeed.jsx'
import CrackingBrief from '../components/CrackingBrief.jsx'

const PRIORITY_COLORS = {
  5: { bg: '#fee2e2', text: '#dc2626' },
  4: { bg: '#ffedd5', text: '#ea580c' },
  3: { bg: '#fef9c3', text: '#ca8a04' },
  2: { bg: '#dbeafe', text: '#1d4ed8' },
  1: { bg: '#f3f4f6', text: '#4b5563' },
}

const s = {
  page: { maxWidth: 780, margin: '0 auto', padding: '32px 24px' },
  back: { fontSize: 13, color: '#6b7280', cursor: 'pointer', marginBottom: 24, display: 'inline-flex', alignItems: 'center', gap: 4, background: 'none', border: 'none', padding: 0 },
  header: { marginBottom: 24 },
  nameRow: { display: 'flex', alignItems: 'center', gap: 12, marginBottom: 6 },
  name: { fontSize: 26, fontWeight: 800, color: '#0f172a' },
  badge: (p) => ({ fontSize: 12, fontWeight: 700, padding: '3px 10px', borderRadius: 999, background: PRIORITY_COLORS[p]?.bg, color: PRIORITY_COLORS[p]?.text }),
  meta: { fontSize: 13, color: '#6b7280', display: 'flex', gap: 16, flexWrap: 'wrap' },
  metaItem: { display: 'flex', alignItems: 'center', gap: 4 },
  summary: { fontSize: 15, color: '#374151', lineHeight: 1.6, background: '#f8fafc', borderRadius: 8, padding: '14px 16px', margin: '20px 0' },
  section: { marginTop: 28 },
  sectionTitle: { fontSize: 13, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#6b7280', marginBottom: 14 },
  actions: { display: 'flex', gap: 8, marginBottom: 20 },
  btn: { padding: '7px 14px', borderRadius: 7, fontSize: 13, fontWeight: 600, cursor: 'pointer', border: '1px solid #e2e8f0', background: 'white', color: '#374151' },
  loading: { color: '#9ca3af', fontSize: 14 },
  status: { fontSize: 13, color: '#6b7280' },
}

export default function CompanyDetail({ id, onBack }) {
  const [company, setCompany] = useState(null)
  const [loading, setLoading] = useState(true)
  const [enrichStatus, setEnrichStatus] = useState('')

  useEffect(() => {
    getCompany(id).then(data => {
      setCompany(data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [id])

  const handleEnrich = async () => {
    setEnrichStatus('Enriching…')
    try {
      await enrichOne(id)
      const updated = await getCompany(id)
      setCompany(updated)
      setEnrichStatus('Done!')
      setTimeout(() => setEnrichStatus(''), 2000)
    } catch {
      setEnrichStatus('Failed.')
    }
  }

  if (loading) return <div style={s.page}><div style={s.loading}>Loading…</div></div>
  if (!company) return <div style={s.page}><div style={s.loading}>Company not found.</div></div>

  const enrichedDate = company.enriched_at
    ? new Date(company.enriched_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
    : null

  return (
    <div style={s.page}>
      <button style={s.back} onClick={onBack}>← Back to Dashboard</button>

      <div style={s.header}>
        <div style={s.nameRow}>
          <h1 style={s.name}>{company.name}</h1>
          {company.priority && <span style={s.badge(company.priority)}>Priority {company.priority}</span>}
        </div>
        <div style={s.meta}>
          {company.industry && <span style={s.metaItem}>{company.industry}</span>}
          {company.website && <a href={company.website} target="_blank" rel="noopener noreferrer" style={{ color: '#1e40af', fontSize: 13 }}>{company.website}</a>}
          {company.last_sf_activity && <span style={s.metaItem}>Last SF activity: {company.last_sf_activity}</span>}
          {enrichedDate && <span style={s.metaItem}>Enriched: {enrichedDate}</span>}
        </div>
      </div>

      <div style={s.actions}>
        <button style={s.btn} onClick={handleEnrich}>⚡ Re-enrich</button>
        {enrichStatus && <span style={s.status}>{enrichStatus}</span>}
      </div>

      {company.ai_summary && (
        <div style={s.summary}>{company.ai_summary}</div>
      )}

      {company.priority === 5 && company.cracking_brief && (
        <CrackingBrief brief={company.cracking_brief} companyName={company.name} />
      )}

      <div style={s.section}>
        <div style={s.sectionTitle}>Signals ({company.signals?.length || 0})</div>
        <SignalFeed signals={company.signals || []} />
      </div>
    </div>
  )
}
