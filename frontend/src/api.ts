/// <reference types="vite/client" />

const API_BASE = import.meta.env.VITE_API_URL || 'https://code.dev.n3d.fit';

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
  'Customer ID': string;
  Customer: string;
  LeaseNumber?: string;
  Balance: number;
  'Last Pay Date': string | null;
  'Last Pay Amt': number | null;
  CollatV: number | null;
  Vehicle?: string;
  SyncRunAt: string;
}

export interface Customer {
  LeaseID: string;
  LeaseNumber: string;
  CustomerID: number;
  Customer: string;
  VIN: string;
  AmountDue: number;
  LastPayDate: string | null;
  Active?: number | boolean;
  CustCell: string | null;
  TagNum: string | null;
  TLC_DiamondNum: string | null;
}

export const api = {
  health: () => apiGet<{ api: string; database: string }>('/api/health'),
  customers: (search: string) =>
    apiGet<{ customers: Customer[] }>(`/api/customers?search=${encodeURIComponent(search)}`),
  arSummary: () => apiGet<{ customers: ARCustomer[] }>('/api/leases/ar-summary'),
  accountReport: () => apiGet<{ customers: ARCustomer[] }>('/api/leases/account-report'),
}