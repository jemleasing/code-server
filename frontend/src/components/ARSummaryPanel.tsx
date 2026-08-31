import { useEffect, useState } from 'react'
import { api, ARCustomer } from '../api'

export default function ARSummaryPanel() {
  const [customers, setCustomers] = useState<ARCustomer[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.arSummary()
      .then((data) => setCustomers(data.customers))
      .catch((e) => setError(e.message))
  }, [])

  return (
    <section className="rounded-lg border border-slate/20 bg-white p-6 lg:col-span-2">
      <div className="flex items-baseline justify-between">
        <h2 className="font-display text-lg text-ink">Highest AR balances</h2>
        <span className="text-xs text-slate">
          {customers[0]?.SyncRunAt ? `as of ${new Date(customers[0].SyncRunAt).toLocaleString()}` : ''}
        </span>
      </div>

      {error && <p className="mt-3 text-sm text-red-600">Couldn't load balances: {error}</p>}

      <table className="mt-4 w-full text-sm">
  <thead>
    <tr className="text-left text-xs uppercase tracking-wide text-slate border-b border-slate/10">
      <th className="pb-2 font-medium">Lease #(s)</th> {/* Collated per customer */}
      <th className="pb-2 font-medium">Customer</th>
      <th className="pb-2 font-medium">Vehicle</th>
      <th className="pb-2 font-medium text-right">Balance</th>
      <th className="pb-2 font-medium text-right">Collat V</th>
      <th className="pb-2 font-medium text-right">Last payment</th>
    </tr>
  </thead>
  <tbody className="divide-y divide-slate/10">
    {customers.slice(0, 10).map((c) => (
      <tr key={c['Customer ID']}>
        <td className="py-2 font-mono text-xs">{c.LeaseNumber || '—'}</td> {/* Comma-separated list of this customer's leases */}
        <td className="py-2">{c.Customer}</td>
        <td className="py-2 text-xs text-slate">{c.Vehicle || '—'}</td>
        <td className="py-2 text-right font-mono">${Number(c.Balance).toFixed(2)}</td>
        <td className="py-2 text-right font-mono">
          {c.CollatV != null ? `$${Number(c.CollatV).toFixed(2)}` : '—'}
        </td>
        <td className="py-2 text-right text-slate">
          {c['Last Pay Date'] ? new Date(c['Last Pay Date']).toLocaleDateString() : '—'}
        </td>
      </tr>
    ))}
  </tbody>
</table>

      {customers.length === 0 && !error && (
        <p className="mt-3 text-sm text-slate">No AR data available. Please check connection settings.</p>
      )}
    </section>
  )
}
