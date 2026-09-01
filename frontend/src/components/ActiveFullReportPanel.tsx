import { useEffect, useState } from 'react'
import { api, ActiveFullReportRow } from '../api'

function downloadCsv(rows: ActiveFullReportRow[]) {
  const headers = [
    'Customer ID', 'Customer', 'Account', 'Balance',
    'CollatV (tblcollatv)', 'CollatV (scorecard)', 'CollatV (product search)',
    'Year', 'Make', 'Model', 'Cost', 'Current Value',
  ]
  const escape = (val: unknown) => {
    const s = val == null ? '' : String(val)
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
  }
  const data = rows.map((r) => [
    r['Customer ID'], r.Customer, r.LeaseNumber, Number(r.Balance).toFixed(2),
    r.CollatV_TblCollatv != null ? Number(r.CollatV_TblCollatv).toFixed(2) : '',
    r.CollatV_Scorecard != null ? Number(r.CollatV_Scorecard).toFixed(2) : '',
    r.CollatV_ProductSearch != null ? Number(r.CollatV_ProductSearch).toFixed(2) : '',
    r.Year ?? '', r.Make ?? '', r.Model ?? '',
    r.Cost != null ? Number(r.Cost).toFixed(2) : '',
    r.CurrentValue != null ? Number(r.CurrentValue).toFixed(2) : '',
  ])
  const csv = [headers, ...data].map((row) => row.map(escape).join(',')).join('\n')

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `active-accounts-full-report-${new Date().toISOString().slice(0, 10)}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

const money = (v: number | null | undefined) => (v != null ? `$${Number(v).toFixed(2)}` : '—')

export default function ActiveFullReportPanel() {
  const [rows, setRows] = useState<ActiveFullReportRow[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.activeFullReport()
      .then((data) => setRows(data.accounts))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <section className="rounded-lg border border-slate/20 bg-white p-6 lg:col-span-3">
      <div className="flex items-baseline justify-between">
        <div>
          <h2 className="font-display text-lg text-ink">Active accounts - full report</h2>
          <p className="mt-1 text-sm text-slate">
            Balance, CollatV from every source table, and vehicle detail - one row per active account.
          </p>
        </div>
        <div className="flex items-center gap-3">
          {rows.length > 0 && <span className="text-xs text-slate">{rows.length} active accounts</span>}
          {rows.length > 0 && (
            <button
              onClick={() => downloadCsv(rows)}
              className="rounded bg-moss px-3 py-1.5 text-xs font-medium text-white hover:bg-moss/90 focus:outline-none focus:ring-2 focus:ring-moss focus:ring-offset-2"
            >
              Export CSV
            </button>
          )}
        </div>
      </div>

      {loading && <p className="mt-3 text-sm text-slate">Loading...</p>}
      {error && <p className="mt-3 text-sm text-red-600">Couldn't load report: {error}</p>}

      {!loading && !error && rows.length > 0 && (
        <div className="mt-4 max-h-[32rem] overflow-auto">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-white">
              <tr className="text-left text-xs uppercase tracking-wide text-slate border-b border-slate/10">
                <th className="pb-2 pr-3 font-medium">Account</th>
                <th className="pb-2 pr-3 font-medium">Customer</th>
                <th className="pb-2 pr-3 font-medium text-right">Balance</th>
                <th className="pb-2 pr-3 font-medium text-right">CollatV (tblcollatv)</th>
                <th className="pb-2 pr-3 font-medium text-right">CollatV (scorecard)</th>
                <th className="pb-2 pr-3 font-medium text-right">CollatV (product search)</th>
                <th className="pb-2 pr-3 font-medium">Year</th>
                <th className="pb-2 pr-3 font-medium">Make</th>
                <th className="pb-2 pr-3 font-medium">Model</th>
                <th className="pb-2 pr-3 font-medium text-right">Cost</th>
                <th className="pb-2 font-medium text-right">Current value</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate/10">
              {rows.map((r) => (
                <tr key={r.LeaseID}>
                  <td className="py-2 pr-3 font-mono text-xs">{r.LeaseNumber}</td>
                  <td className="py-2 pr-3">{r.Customer}</td>
                  <td className="py-2 pr-3 text-right font-mono">{money(r.Balance)}</td>
                  <td className="py-2 pr-3 text-right font-mono">{money(r.CollatV_TblCollatv)}</td>
                  <td className="py-2 pr-3 text-right font-mono">{money(r.CollatV_Scorecard)}</td>
                  <td className="py-2 pr-3 text-right font-mono">{money(r.CollatV_ProductSearch)}</td>
                  <td className="py-2 pr-3 text-xs text-slate">{r.Year ?? '—'}</td>
                  <td className="py-2 pr-3 text-xs text-slate">{r.Make ?? '—'}</td>
                  <td className="py-2 pr-3 text-xs text-slate">{r.Model ?? '—'}</td>
                  <td className="py-2 pr-3 text-right font-mono">{money(r.Cost)}</td>
                  <td className="py-2 text-right font-mono">{money(r.CurrentValue)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!loading && !error && rows.length === 0 && (
        <p className="mt-3 text-sm text-slate">No active accounts found.</p>
      )}
    </section>
  )
}
