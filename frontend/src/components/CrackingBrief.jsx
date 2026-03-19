import React, { useState } from 'react'

const s = {
  container: {
    background: 'linear-gradient(135deg, #fff7ed 0%, #fff1e6 100%)',
    border: '1px solid #fed7aa',
    borderRadius: 10,
    padding: '18px 20px',
    marginTop: 20,
  },
  header: { display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 },
  title: { fontSize: 13, fontWeight: 800, color: '#9a3412', textTransform: 'uppercase', letterSpacing: '0.06em' },
  strategy: {
    background: 'white',
    borderRadius: 8,
    padding: '14px 16px',
    marginBottom: 10,
    border: '1px solid #fed7aa',
  },
  hook: { fontSize: 13, fontWeight: 700, color: '#7c2d12', marginBottom: 6 },
  hookLabel: { fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#9a3412', marginBottom: 2 },
  target: { fontSize: 12, color: '#9a3412', marginBottom: 6 },
  targetLabel: { fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#9a3412', marginBottom: 2 },
  opening: { fontSize: 13, color: '#374151', fontStyle: 'italic', borderLeft: '3px solid #fb923c', paddingLeft: 10, margin: '6px 0 0' },
  copy: { fontSize: 11, cursor: 'pointer', color: '#6b7280', marginTop: 6, background: 'none', border: 'none', padding: 0 },
}

function StrategyCard({ strategy, index }) {
  const [copied, setCopied] = useState(false)

  const copyOpening = () => {
    navigator.clipboard.writeText(strategy.opening_line)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  return (
    <div style={s.strategy}>
      <div style={s.hookLabel}>Hook #{index + 1}</div>
      <div style={s.hook}>{strategy.hook}</div>
      <div style={s.targetLabel}>Target</div>
      <div style={s.target}>{strategy.target}</div>
      <div style={s.opening}>"{strategy.opening_line}"</div>
      <button style={s.copy} onClick={copyOpening}>
        {copied ? '✓ Copied' : '📋 Copy opening line'}
      </button>
    </div>
  )
}

export default function CrackingBrief({ brief, companyName }) {
  let strategies = []
  try {
    strategies = typeof brief === 'string' ? JSON.parse(brief) : brief
  } catch {
    return null
  }

  if (!strategies || strategies.length === 0) return null

  return (
    <div style={s.container}>
      <div style={s.header}>
        <span style={{ fontSize: 18 }}>🎯</span>
        <span style={s.title}>How to Crack {companyName}</span>
      </div>
      {strategies.map((strategy, i) => (
        <StrategyCard key={i} strategy={strategy} index={i} />
      ))}
    </div>
  )
}
