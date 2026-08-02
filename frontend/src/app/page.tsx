'use client'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to Career Assistant
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          AI-powered platform for resume optimization and job matching
        </p>
        <div className="space-x-4">
          <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            Get Started
          </button>
          <button className="px-6 py-3 bg-white text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50">
            Learn More
          </button>
        </div>
      </div>
    </main>
  )
}

