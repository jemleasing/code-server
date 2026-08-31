import { useEffect, useState } from 'react'
import { api, PendingPayment } from '../api'

export default function PendingExportsPanel() {
  const [pending, setPending] = useState<PendingPayment[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.pendingExports()
      .then((data) => setPending(data.pending))
      .catch((e) => setError(e.message))
  }, [])

  const failing = pending.filter((p) => p.SageExportError)

  return (
    <section className="rounded-lg border border-slate/20 bg-white p-6">
      <div className="flex items-baseline justify-between">
        <h2 className="font-display text-lg text-ink">Pending Sage exports</h2>
        <span className="font-mono text-xs text-slate">{pending.length} queued</span>
      </div>

      {error && <p className="mt-3 text-sm text-red-600">Couldn't load queue: {error}</p>}

      {failing.length > 0 && (
        <p className="mt-3 text-sm text-rust">
          {failing.length} receipt{failing.length > 1 ? 's' : ''} need attention before export.
        </p>
      )}

      <ul className="mt-4 divide-y divide-slate/10">
        {pending.slice(0, 8).map((p) => (
          <li key={p.PaymentID} className="py-2 text-sm">
            <div className="flex items-center justify-between">
              <span className="font-medium text-ink">{p.CustName || p.AccountID}</span>
              <span className="font-mono">${Number(p.Amount).toFixed(2)}</span>
            </div>
            <div className="mt-1 flex items-center justify-between text-xs text-slate">
              <span>{p.PaymentType} · {new Date(p.DateTime).toLocaleDateString()}</span>
              {p.SageExportError && <span className="text-rust">{p.SageExportError}</span>}
            </div>
          </li>
        ))}
      </ul>

      {pending.length === 0 && !error && (
        <p className="mt-3 text-sm text-slate">Nothing waiting — everything's been sent to Sage.</p>
      )}
    </section>
  )
}
