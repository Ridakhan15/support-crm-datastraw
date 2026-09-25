import { Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar.jsx'
import { ToastProvider } from './components/Toast.jsx'
import Dashboard from './pages/Dashboard.jsx'
import CreateTicket from './pages/CreateTicket.jsx'
import TicketDetails from './pages/TicketDetails.jsx'

export default function App() {
  return (
    <ToastProvider>
      <div className="min-h-screen bg-slate-50">
        <Navbar />
        <main>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/tickets/new" element={<CreateTicket />} />
            <Route path="/tickets/:ticketId" element={<TicketDetails />} />
          </Routes>
        </main>
      </div>
    </ToastProvider>
  )
}
