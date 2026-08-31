import { useEffect, useState } from 'react'
import { api, ARCustomer } from '../api'

export default function AccountReportPanel() {
  const [customers, setCustomers] = useState<ARCustomer[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.accountReport()
      .then((data) => setCustomers(data.customers))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const totalBalance = customers.reduce((sum, c) => sum + Number(c.Balance || 0), 0)

  return (
    <section className="rounded-lg border border-slate/20 bg-white p-6 lg:col-span-3">
      <div className="flex items-baseline justify-between">
        <div>
          <h2 className="font-display text-lg text-ink">Account report (A-V)</h2>
          <p className="mt-1 text-sm text-slate">
            Every customer whose account starts with a letter A through V, collated one row per customer.
          </p>
        </div>
        {customers.length > 0 && (
          <span className="text-xs text-slate">
            {customers.length} customers · ${totalBalance.toFixed(2)} total balance
          </span>
        )}
      </div>

      {loading && <p className="mt-3 text-sm text-slate">Loading...</p>}
      {error && <p className="mt-3 text-sm text-red-600">Couldn't load report: {error}</p>}

      {!loading && !error && customers.length > 0 && (
        <div className="mt-4 max-h-[32rem] overflow-y-auto">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-white">
              <tr className="text-left text-xs uppercase tracking-wide text-slate border-b border-slate/10">
                <th className="pb-2 font-medium">Lease #(s)</th>
                <th className="pb-2 font-medium">Customer</th>
                <th className="pb-2 font-medium text-right">Balance</th>
                <th className="pb-2 font-medium text-right">Collat V</th>
                <th className="pb-2 font-medium text-right">Last payment</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate/10">
              {customers.map((c) => (
                <tr key={c['Customer ID']}>
                  <td className="py-2 font-mono text-xs">{c.LeaseNumber || '—'}</td>
                  <td className="py-2">{c.Customer}</td>
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
        </div>
      )}

      {!loading && !error && customers.length === 0 && (
        <p className="mt-3 text-sm text-slate">No accounts found.</p>
      )}
    </section>
  )
}
