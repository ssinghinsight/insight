import React from 'react'

const PRIORITY_COLORS = {
  5: { border: '#ef4444', bg: '#fee2e2', text: '#dc2626' },
  4: { border: '#f97316', bg: '#ffedd5', text: '#ea580c' },
  3: { border: '#eab308', bg: '#fef9c3', text: '#ca8a04' },
  2: { border: '#3b82f6', bg: '#dbeafe', text: '#1d4ed8' },
  1: { border: '#9ca3af', bg: '#f3f4f6', text: '#4b5563' },
}

const s = {
  card: (priority) => ({
    background: 'white',
    borderRadius: 10,
    padding: '18px 20px',
    borderLeft: `4px solid ${PRIORITY_COLORS[priority]?.border || '#e5e7eb'}`,
    cursor: 'pointer',
    transition: 'box-shadow 0.15s',
    boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
  }),
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 6 },
  name: { fontSize: 16, fontWeight: 700, color: '#0f172a' },
  badge: (priority) => ({
    fontSize: 11, fontWeight: 700, padding: '2px 8px', borderRadius: 999,
    background: PRIORITY_COLORS[priority]?.bg || '#f3f4f6',
    color: PRIORITY_COLORS[priority]?.text || '#6b7280',
    whiteSpace: 'nowrap',
  }),
  meta: { fontSize: 12, color: '#6b7280', marginBottom: 8 },
  summary: { fontSize: 13, color: '#374151', lineHeight: 1.5, marginBottom: 10 },
  footer: { display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' },
  pill: { fontSize: 11, color: '#6b7280', background: '#f1f5f9', padding: '2px 8px', borderRadius: 999 },
  crackCta: { fontSize: 11, fontWeight: 700, color: '#dc2626', background: '#fee2e2', padding: '2px 8px', borderRadius: 999 },
}

export default function CompanyCard({ company, onClick }) {
  const priority = company.priority

  return (
    <div
      style={s.card(priority)}
      onClick={() => onClick(company.id)}
      onMouseEnter={e => e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)'}
      onMouseLeave={e => e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.06)'}
    >
      <div style={s.header}>
        <div style={s.name}>{company.name}</div>
        {priority && (
          <span style={s.badge(priority)}>Priority {priority}</span>
        )}
      </div>

      <div style={s.meta}>
        {company.industry && <span>{company.industry}</span>}
        {company.last_sf_activity && (
          <span> · Last activity: {new Date(company.last_sf_activity).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
        )}
      </div>

      {company.ai_summary && (
        <div style={s.summary}>
          {company.ai_summary.slice(0, 160)}{company.ai_summary.length > 160 ? '…' : ''}
        </div>
      )}

      <div style={s.footer}>
        {company.signal_count > 0 && (
          <span style={s.pill}>{company.signal_count} signal{company.signal_count !== 1 ? 's' : ''}</span>
        )}
        {!company.enriched_at && (
          <span style={s.pill}>Not enriched</span>
        )}
        {company.has_cracking_brief && (
          <span style={s.crackCta}>🎯 Cracking strategy ready</span>
        )}
      </div>
    </div>
  )
}
