'use client'

import { useEffect, useState } from 'react'
import { Zap, Image, Sparkles } from 'lucide-react'

interface UserStats {
  credits_available: number
  basic_processed: number
  qwen_processed: number
}

interface QuickStatsProps {
  userEmail: string
}

export default function QuickStats({ userEmail }: QuickStatsProps) {
  const [stats, setStats] = useState<UserStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    const fetchStats = async () => {
      if (!userEmail) {
        setLoading(false)
        return
      }

      try {
        const response = await fetch(`/api/v1/auth/stats?email=${encodeURIComponent(userEmail)}`)

        if (response.ok) {
          const data = await response.json()
          setStats({
            credits_available: data.credits_available,
            basic_processed: data.basic_processed,
            qwen_processed: data.qwen_processed
          })
          setError(false)
        } else {
          setError(true)
        }
      } catch (err) {
        console.error('Failed to fetch stats:', err)
        setError(true)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()

    // Refresh stats every 30 seconds
    const interval = setInterval(fetchStats, 30000)
    return () => clearInterval(interval)
  }, [userEmail])

  if (loading) {
    return (
      <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Stats</h3>
        <div className="space-y-4 animate-pulse">
          <div className="h-16 bg-gray-200 rounded-lg"></div>
          <div className="h-16 bg-gray-200 rounded-lg"></div>
          <div className="h-16 bg-gray-200 rounded-lg"></div>
        </div>
      </div>
    )
  }

  if (error || !stats) {
    return (
      <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Stats</h3>
        <p className="text-sm text-gray-500">Unable to load stats</p>
      </div>
    )
  }

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <Zap className="w-5 h-5 text-green-600" />
        Quick Stats
      </h3>

      <div className="space-y-4">
        {/* Credits Available */}
        <div className="flex items-center justify-between p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <Zap className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Credits Available</p>
              <p className="text-xs text-gray-500">Ready to use</p>
            </div>
          </div>
          <span className="text-3xl font-bold text-green-600">
            {stats.credits_available}
          </span>
        </div>

        {/* Basic Processing */}
        <div className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg border border-blue-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Image className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Basic Processing</p>
              <p className="text-xs text-gray-500">Images processed</p>
            </div>
          </div>
          <span className="text-3xl font-bold text-blue-600">
            {stats.basic_processed}
          </span>
        </div>

        {/* AI Processing (Qwen) */}
        <div className="flex items-center justify-between p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Sparkles className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">AI Processing</p>
              <p className="text-xs text-gray-500">Qwen images</p>
            </div>
          </div>
          <span className="text-3xl font-bold text-purple-600">
            {stats.qwen_processed}
          </span>
        </div>
      </div>

      {/* Total Processed */}
      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="flex items-center justify-between text-sm">
          <span className="font-medium text-gray-600">Total Processed</span>
          <span className="font-bold text-gray-900">
            {stats.basic_processed + stats.qwen_processed} images
          </span>
        </div>
      </div>
    </div>
  )
}
