import { useEffect, useState } from 'react'
import { api, SyncRun } from '../api'

export default function SyncStatusPanel() {
  const [runs, setRuns] = useState<SyncRun[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.syncStatus()
      .then((data) => setRuns(data.runs))
      .catch((e) => setError(e.message))
  }, [])

  const latest = runs[0]

  return (
    <section className="rounded-lg border border-slate/20 bg-white p-6">
      <div className="flex items-baseline justify-between">
        <h2 className="font-display text-lg text-ink">Sage sync</h2>
        {latest && (
          <span
            className={`font-mono text-xs uppercase tracking-wide px-2 py-1 rounded ${
              latest.Status === 'success'
                ? 'bg-moss/10 text-moss'
                : latest.Status === 'partial'
                ? 'bg-rust/10 text-rust'
                : 'bg-red-100 text-red-700'
            }`}
          >
            {latest.Status}
          </span>
        )}
      </div>

      {error && <p className="mt-3 text-sm text-red-600">Couldn't load sync history: {error}</p>}

      {!error && runs.length === 0 && (
        <p className="mt-3 text-sm text-slate">No sync runs logged yet.</p>
      )}

      <ul className="mt-4 divide-y divide-slate/10">
        {runs.slice(0, 6).map((run) => (
          <li key={run.ID} className="flex items-center justify-between py-2 text-sm">
            <div>
              <span className="font-medium text-ink">
                {run.Direction === 'sage_to_mysql' ? 'Sage → MySQL' : 'MySQL → Sage'}
              </span>
              <span className="ml-2 text-slate">
                {new Date(run.StartedAt).toLocaleString()}
              </span>
            </div>
            <div className="font-mono text-xs text-slate">
              {run.RowsProcessed} ok{run.RowsFailed > 0 ? `, ${run.RowsFailed} failed` : ''}
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}
