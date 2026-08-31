const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`)
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status} ${res.statusText}`)
  }
  return res.json()
}

export interface SyncRun {
  ID: number
  Direction: string
  StartedAt: string
  FinishedAt: string | null
  RowsProcessed: number
  RowsFailed: number
  Status: string
  Detail: string | null
}

export interface PendingPayment {
  PaymentID: number
  AccountID: string
  CustName: string
  PaymentType: string
  Amount: number
  DateTime: string
  CheckNo: string | null
  SageExportError: string | null
}

export interface ARCustomer {
  'Customer ID': string
  Customer: string
  Balance: number
  'Last Pay Date': string | null
  'Last Pay Amt': number | null
  SyncRunAt: string
}

export interface Customer {
  CustomerID: number
  LeaseNumber: string
  CustFirstName: string
  CustLastName: string
  CustCurrentAddress1: string
  CustCurrentCity: string
  CustCurrentState: string
  CustCurrentZip: string
  VIN: string
  CustStatus: string
  CollStatus: string
}

export const api = {
  health: () => apiGet<{ api: string; database: string }>('/api/health'),
  syncStatus: () => apiGet<{ runs: SyncRun[] }>('/api/sage-sync/status'),
  pendingExports: () => apiGet<{ pending: PendingPayment[]; count: number }>('/api/sage-sync/pending-exports'),
  arSummary: () => apiGet<{ customers: ARCustomer[] }>('/api/sage-sync/ar-summary'),
  customers: (search: string) =>
    apiGet<{ customers: Customer[] }>(`/api/customers?search=${encodeURIComponent(search)}`),
}
