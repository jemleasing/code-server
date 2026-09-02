import { useEffect, useState } from 'react'
import { api, EzpassViolationRow } from '../api'

const money = (v: number | null | undefined) => (v != null ? `$${Number(v).toFixed(2)}` : '—')

export default function EzpassViolationsPanel() {
  const [rows, setRows] = useState<EzpassViolationRow[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.ezpassViolations()
      .then((data) => setRows(data.customers))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <section className="rounded-lg border border-slate/20 bg-white p-6 lg:col-span-3">
      <div className="flex items-baseline justify-between">
        <div>
          <h2 className="font-display text-lg text-ink">EZPass violations (last 180 days)</h2>
          <p className="mt-1 text-sm text-slate">
            Customers with a toll violation in the last 180 days: ticket count, balance, CollatV, and current car value.
          </p>
        </div>
        {rows.length > 0 && <span className="text-xs text-slate">{rows.length} customers</span>}
      </div>

      {loading && <p className="mt-3 text-sm text-slate">Loading...</p>}
      {error && <p className="mt-3 text-sm text-red-600">Couldn't load report: {error}</p>}

      {!loading && !error && rows.length > 0 && (
        <div className="mt-4 max-h-[32rem] overflow-y-auto">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-white">
              <tr className="text-left text-xs uppercase tracking-wide text-slate border-b border-slate/10">
                <th className="pb-2 pr-3 font-medium">Customer</th>
                <th className="pb-2 pr-3 font-medium">Lease #(s)</th>
                <th className="pb-2 pr-3 font-medium text-right">Tickets</th>
                <th className="pb-2 pr-3 font-medium text-right">Balance</th>
                <th className="pb-2 pr-3 font-medium text-right">Collat V</th>
                <th className="pb-2 font-medium text-right">Current value</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate/10">
              {rows.map((r) => (
                <tr key={r['Customer ID']}>
                  <td className="py-2 pr-3">{r.Customer}</td>
                  <td className="py-2 pr-3 font-mono text-xs">{r.LeaseNumber || '—'}</td>
                  <td className="py-2 pr-3 text-right font-mono">{r.TicketCount}</td>
                  <td className="py-2 pr-3 text-right font-mono">{money(r.Balance)}</td>
                  <td className="py-2 pr-3 text-right font-mono">{money(r.CollatV)}</td>
                  <td className="py-2 text-right font-mono">{money(r.CurrentValue)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!loading && !error && rows.length === 0 && (
        <p className="mt-3 text-sm text-slate">No EZPass violations found in the last 180 days.</p>
      )}
    </section>
  )
}
