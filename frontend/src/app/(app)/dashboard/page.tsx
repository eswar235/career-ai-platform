'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

import { useAuth } from '@/lib/hooks/useAuth'

export default function DashboardPage() {
  const router = useRouter()
  const { user, isLoading, isAuthenticated, logout } = useAuth()

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isLoading, isAuthenticated, router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Dashboard
              </h1>
              <p className="text-gray-600 mt-1">
                Welcome back, {user.fullName || user.email}!
              </p>
            </div>
            <button
              onClick={logout}
              className="px-4 py-2 text-gray-700 hover:text-gray-900 font-medium border border-gray-300 rounded-lg hover:bg-gray-50 transition"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-gray-500 text-sm font-medium mb-2">
              Resumes
            </div>
            <div className="text-3xl font-bold text-gray-900">0</div>
            <p className="text-gray-600 text-sm mt-2">Uploaded resumes</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-gray-500 text-sm font-medium mb-2">
              Jobs Saved
            </div>
            <div className="text-3xl font-bold text-gray-900">0</div>
            <p className="text-gray-600 text-sm mt-2">Bookmarked positions</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-gray-500 text-sm font-medium mb-2">
              Applications
            </div>
            <div className="text-3xl font-bold text-gray-900">0</div>
            <p className="text-gray-600 text-sm mt-2">Total submitted</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-gray-500 text-sm font-medium mb-2">
              Success Rate
            </div>
            <div className="text-3xl font-bold text-gray-900">0%</div>
            <p className="text-gray-600 text-sm mt-2">Interview callbacks</p>
          </div>
        </div>

        {/* Getting Started */}
        <div className="bg-white rounded-lg shadow p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Getting Started
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="border border-gray-200 rounded-lg p-6">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <span className="text-blue-600 text-xl font-bold">1</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Upload Resume
              </h3>
              <p className="text-gray-600">
                Start by uploading your resume. Our AI will extract your information automatically.
              </p>
              <button className="mt-4 text-blue-600 hover:text-blue-700 font-medium">
                Upload Now →
              </button>
            </div>

            <div className="border border-gray-200 rounded-lg p-6">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <span className="text-blue-600 text-xl font-bold">2</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Search Jobs
              </h3>
              <p className="text-gray-600">
                Find relevant job opportunities using our powerful search and filtering tools.
              </p>
              <button className="mt-4 text-blue-600 hover:text-blue-700 font-medium">
                Search Jobs →
              </button>
            </div>

            <div className="border border-gray-200 rounded-lg p-6">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <span className="text-blue-600 text-xl font-bold">3</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Apply Smarter
              </h3>
              <p className="text-gray-600">
                Get AI-optimized resumes and cover letters tailored to each position.
              </p>
              <button className="mt-4 text-blue-600 hover:text-blue-700 font-medium">
                Learn More →
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
