import axios from 'axios'

const API_KEY = import.meta.env.VITE_API_KEY || ''

const api = axios.create({
  baseURL: '/api',
  headers: API_KEY ? { Authorization: `Bearer ${API_KEY}` } : {},
})

export const getCompanies = (params = {}) =>
  api.get('/companies', { params }).then(r => r.data)

export const getCompany = (id) =>
  api.get(`/companies/${id}`).then(r => r.data)

export const syncSalesforce = () =>
  api.post('/companies/sync').then(r => r.data)

export const enrichAll = () =>
  api.post('/enrich/all').then(r => r.data)

export const enrichOne = (id) =>
  api.post(`/companies/${id}/enrich`).then(r => r.data)

export const sendDigest = () =>
  api.post('/digest/send').then(r => r.data)

export const getSignals = (companyId, params = {}) =>
  api.get(`/signals/${companyId}`, { params }).then(r => r.data)

export const getSalesforceAuthStatus = () =>
  api.get('/auth/salesforce/status').then(r => r.data)

export const getSalesforceLoginUrl = () => '/api/auth/salesforce/login'
