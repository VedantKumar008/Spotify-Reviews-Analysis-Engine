import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Users,
  Lightbulb,
  Menu,
  X,
  Play
} from 'lucide-react'

// API URL configuration with fallback for local development
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api'

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [isIngesting, setIsIngesting] = useState(false)
  const [ingestionMessage, setIngestionMessage] = useState('')
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'User Segments', href: '/segments', icon: Users },
    { name: 'Insights', href: '/insights', icon: Lightbulb },
  ]

  const handleIngestion = async () => {
    if (isIngesting) return

    setIsIngesting(true)
    setIngestionMessage('Starting ingestion...')

    try {
      const response = await fetch(`${API_URL}/ingest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      const data = await response.json()

      if (response.ok) {
        setIngestionMessage(`Success! ${data.message}`)
        setTimeout(() => setIngestionMessage(''), 5000)
      } else {
        setIngestionMessage(`Error: ${data.error}`)
        setTimeout(() => setIngestionMessage(''), 5000)
      }
    } catch (error) {
      setIngestionMessage(`Error: ${error.message}`)
      setTimeout(() => setIngestionMessage(''), 5000)
    } finally {
      setIsIngesting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white flex">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-gray-800 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 flex-shrink-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-700">
          <h1 className="text-xl font-bold text-green-400">Spotify Insights</h1>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden text-gray-400 hover:text-white"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <nav className="mt-6 px-4">
          <ul className="space-y-2">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <li key={item.name}>
                  <Link
                    to={item.href}
                    className={`flex items-center px-4 py-3 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-green-600 text-white'
                        : 'text-gray-300 hover:bg-gray-700'
                    }`}
                  >
                    <item.icon className="w-5 h-5 mr-3" />
                    {item.name}
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col">
        {/* Top bar */}
        <header className="bg-gray-800 border-b border-gray-700 h-16 flex items-center justify-between px-6 flex-shrink-0">
          <div className="flex items-center">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden mr-4 text-gray-400 hover:text-white"
            >
              <Menu className="w-6 h-6" />
            </button>
            <h2 className="text-lg font-semibold">
              {navigation.find((item) => item.href === location.pathname)?.name || 'Dashboard'}
            </h2>
          </div>

          <div className="flex items-center gap-4">
            {ingestionMessage && (
              <span className={`text-sm ${ingestionMessage.includes('Error') ? 'text-red-400' : 'text-green-400'}`}>
                {ingestionMessage}
              </span>
            )}
            <button
              onClick={handleIngestion}
              disabled={isIngesting}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                isIngesting
                  ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                  : 'bg-green-600 hover:bg-green-700 text-white'
              }`}
            >
              <Play className="w-4 h-4" />
              <span>{isIngesting ? 'Ingesting...' : 'Ingest Reviews'}</span>
            </button>
          </div>
        </header>

        {/* Page content */}
        <main className="pt-2 px-6 pb-6 flex-1 overflow-auto">{children}</main>
      </div>
    </div>
  )
}

export default Layout
