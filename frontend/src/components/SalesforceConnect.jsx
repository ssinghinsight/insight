import React from 'react'
import { getSalesforceLoginUrl } from '../api.js'

const s = {
  banner: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    background: '#fff7ed',
    border: '1px solid #fed7aa',
    borderRadius: 10,
    padding: '14px 20px',
    marginBottom: 24,
  },
  left: { display: 'flex', alignItems: 'center', gap: 12 },
  icon: { fontSize: 22 },
  text: { fontSize: 14, color: '#92400e', fontWeight: 500 },
  sub: { fontSize: 12, color: '#b45309', marginTop: 2 },
  btn: {
    padding: '8px 16px',
    background: '#0f172a',
    color: 'white',
    border: 'none',
    borderRadius: 7,
    fontSize: 13,
    fontWeight: 600,
    cursor: 'pointer',
    textDecoration: 'none',
    display: 'inline-block',
  },
}

export default function SalesforceConnect() {
  return (
    <div style={s.banner}>
      <div style={s.left}>
        <span style={s.icon}>🔌</span>
        <div>
          <div style={s.text}>Salesforce not connected</div>
          <div style={s.sub}>Connect your account to sync companies and activity notes.</div>
        </div>
      </div>
      <a href={getSalesforceLoginUrl()} style={s.btn}>
        Connect Salesforce
      </a>
    </div>
  )
}
