import React from 'react'

const s = {
  bar: { display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap', marginBottom: 24 },
  select: { padding: '6px 10px', borderRadius: 6, border: '1px solid #e2e8f0', fontSize: 13, background: 'white', cursor: 'pointer', color: '#374151' },
  label: { fontSize: 12, fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' },
  toggle: (active) => ({
    padding: '6px 12px', borderRadius: 6, fontSize: 13, fontWeight: 600, cursor: 'pointer',
    border: '1px solid', borderColor: active ? '#dc2626' : '#e2e8f0',
    background: active ? '#fee2e2' : 'white', color: active ? '#dc2626' : '#6b7280',
  }),
}

export default function FilterBar({ filters, onChange }) {
  return (
    <div style={s.bar}>
      <div>
        <span style={s.label}>Priority </span>
        <select
          style={s.select}
          value={filters.priority || ''}
          onChange={e => onChange({ ...filters, priority: e.target.value || null })}
        >
          <option value="">All</option>
          <option value="5">5 — Highest</option>
          <option value="4">4</option>
          <option value="3">3</option>
          <option value="2">2</option>
          <option value="1">1</option>
        </select>
      </div>

      <div>
        <span style={s.label}>Sort </span>
        <select
          style={s.select}
          value={filters.sort || 'priority'}
          onChange={e => onChange({ ...filters, sort: e.target.value })}
        >
          <option value="priority">Priority</option>
          <option value="last_activity">Last Activity</option>
          <option value="name">Name A–Z</option>
        </select>
      </div>

      <button
        style={s.toggle(filters.has_cracking_brief)}
        onClick={() => onChange({ ...filters, has_cracking_brief: filters.has_cracking_brief ? null : true })}
      >
        🎯 Has Cracking Strategy
      </button>
    </div>
  )
}
