import { useEffect, useState } from 'react'
import { api, ActiveAccount } from '../api'

export default function ActiveCollatVPanel() {
  const [accounts, setAccounts] = useState<ActiveAccount[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.activeCollatV()
      .then((data) => setAccounts(data.accounts))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const totalBalance = accounts.reduce((sum, a) => sum + Number(a.Balance || 0), 0)
  const totalCollatV = accounts.reduce((sum, a) => sum + Number(a.CollatV || 0), 0)

  return (
    <section className="rounded-lg border border-slate/20 bg-white p-6 lg:col-span-3">
      <div className="flex items-baseline justify-between">
        <div>
          <h2 className="font-display text-lg text-ink">Collat V by account (active)</h2>
          <p className="mt-1 text-sm text-slate">
            One row per active account, with balance and collateral value.
          </p>
        </div>
        {accounts.length > 0 && (
          <span className="text-xs text-slate">
            {accounts.length} accounts · ${totalBalance.toFixed(2)} balance · ${totalCollatV.toFixed(2)} Collat V
          </span>
        )}
      </div>

      {loading && <p className="mt-3 text-sm text-slate">Loading...</p>}
      {error && <p className="mt-3 text-sm text-red-600">Couldn't load report: {error}</p>}

      {!loading && !error && accounts.length > 0 && (
        <div className="mt-4 max-h-[32rem] overflow-y-auto">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-white">
              <tr className="text-left text-xs uppercase tracking-wide text-slate border-b border-slate/10">
                <th className="pb-2 font-medium">Account</th>
                <th className="pb-2 font-medium">Customer</th>
                <th className="pb-2 font-medium text-right">Balance</th>
                <th className="pb-2 font-medium text-right">Collat V</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate/10">
              {accounts.map((a) => (
                <tr key={a.LeaseID}>
                  <td className="py-2 font-mono text-xs">{a.LeaseNumber}</td>
                  <td className="py-2">{a.Customer}</td>
                  <td className="py-2 text-right font-mono">${Number(a.Balance).toFixed(2)}</td>
                  <td className="py-2 text-right font-mono">
                    {a.CollatV != null ? `$${Number(a.CollatV).toFixed(2)}` : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!loading && !error && accounts.length === 0 && (
        <p className="mt-3 text-sm text-slate">No active accounts found.</p>
      )}
    </section>
  )
}
