import ARSummaryPanel from './components/ARSummaryPanel'
import CustomerSearchPanel from './components/CustomerSearchPanel'
import AccountReportPanel from './components/AccountReportPanel'
import ActiveCollatVPanel from './components/ActiveCollatVPanel'
import ActiveFullReportPanel from './components/ActiveFullReportPanel'

export default function App() {
  return (
    <div className="min-h-screen">
      <header className="border-b border-slate/20 bg-white">
        <div className="mx-auto max-w-6xl px-6 py-5">
          <p className="font-mono text-xs uppercase tracking-widest text-rust">JEM Leasing</p>
          <h1 className="font-display text-2xl text-ink">Operations console</h1>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-8">
        <div className="grid gap-6 lg:grid-cols-2">
          <ARSummaryPanel />
          <CustomerSearchPanel />
          <AccountReportPanel />
          <ActiveCollatVPanel />
          <ActiveFullReportPanel />
        </div>
      </main>
    </div>
  )
}