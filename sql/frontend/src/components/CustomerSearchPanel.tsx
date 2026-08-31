import { useState } from 'react'
import { api, Customer } from '../api'

export default function CustomerSearchPanel() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<Customer[]>([])
  const [error, setError] = useState<string | null>(null)
  const [searched, setSearched] = useState(false)

  async function runSearch(e: React.FormEvent) {
    e.preventDefault()
    if (!query.trim()) return
    try {
      const data = await api.customers(query.trim())
      setResults(data.customers)
      setSearched(true)
      setError(null)
    } catch (e: any) {
      setError(e.message)
    }
  }

  return (
    <section className="rounded-lg border border-slate/20 bg-white p-6 lg:col-span-3">
      <h2 className="font-display text-lg text-ink">Customer lookup</h2>
      <p className="mt-1 text-sm text-slate">
        Search by name, lease number, or VIN — the same lookup Access does today.
      </p>

      <form onSubmit={runSearch} className="mt-4 flex gap-2">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. Rodriguez, LN-1042, or a VIN"
          className="flex-1 rounded border border-slate/30 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-moss"
        />
        <button
          type="submit"
          className="rounded bg-moss px-4 py-2 text-sm font-medium text-white hover:bg-moss/90 focus:outline-none focus:ring-2 focus:ring-moss focus:ring-offset-2"
        >
          Search
        </button>
      </form>

      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}

      {searched && results.length === 0 && !error && (
        <p className="mt-3 text-sm text-slate">No customers matched "{query}".</p>
      )}

      {results.length > 0 && (
        <table className="mt-4 w-full text-sm">
          <thead>
            <tr className="text-left text-xs uppercase tracking-wide text-slate border-b border-slate/10">
              <th className="pb-2 font-medium">Name</th>
              <th className="pb-2 font-medium">Lease #</th>
              <th className="pb-2 font-medium">VIN</th>
              <th className="pb-2 font-medium">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate/10">
            {results.map((c) => (
              <tr key={c.CustomerID}>
                <td className="py-2">{c.CustFirstName} {c.CustLastName}</td>
                <td className="py-2 font-mono">{c.LeaseNumber}</td>
                <td className="py-2 font-mono text-xs">{c.VIN}</td>
                <td className="py-2">{c.CustStatus}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  )
}
