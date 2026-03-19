import React from 'react'

const SOURCE_ICON = { news: '📰', linkedin: '💼', crunchbase: '💰' }
const SOURCE_LABEL = { news: 'News', linkedin: 'LinkedIn', crunchbase: 'Crunchbase' }

const s = {
  feed: { display: 'flex', flexDirection: 'column', gap: 12 },
  item: { borderTop: '1px solid #f1f5f9', paddingTop: 12 },
  meta: { display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 },
  source: { fontSize: 11, fontWeight: 700, color: '#6b7280', textTransform: 'uppercase' },
  date: { fontSize: 11, color: '#9ca3af' },
  title: { fontSize: 14, fontWeight: 600, color: '#1e40af', marginBottom: 4 },
  summary: { fontSize: 13, color: '#4b5563', lineHeight: 1.5 },
  empty: { fontSize: 13, color: '#9ca3af', fontStyle: 'italic', padding: '12px 0' },
}

export default function SignalFeed({ signals }) {
  if (!signals || signals.length === 0) {
    return <div style={s.empty}>No signals found yet. Run enrichment to fetch data.</div>
  }

  return (
    <div style={s.feed}>
      {signals.map(sig => (
        <div key={sig.id} style={s.item}>
          <div style={s.meta}>
            <span>{SOURCE_ICON[sig.source] || '🔍'}</span>
            <span style={s.source}>{SOURCE_LABEL[sig.source] || sig.source}</span>
            {sig.published_at && (
              <span style={s.date}>
                {new Date(sig.published_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              </span>
            )}
          </div>
          {sig.url ? (
            <a href={sig.url} target="_blank" rel="noopener noreferrer" style={{ ...s.title, textDecoration: 'none' }}>
              {sig.title}
            </a>
          ) : (
            <div style={s.title}>{sig.title}</div>
          )}
          {sig.summary && <div style={s.summary}>{sig.summary.slice(0, 250)}{sig.summary.length > 250 ? '…' : ''}</div>}
        </div>
      ))}
    </div>
  )
}
