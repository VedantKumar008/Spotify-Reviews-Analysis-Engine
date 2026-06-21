import React, { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Filter, Download, RefreshCw, Lightbulb, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react'

// API URL configuration with fallback for local development
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api'

const Insights = () => {
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [loading, setLoading] = useState(false)

  const [opportunities, setOpportunities] = useState([])
  const [hypotheses, setHypotheses] = useState([])
  const [painPoints, setPainPoints] = useState([])

  useEffect(() => {
    // Fetch real data from API
    const fetchData = async () => {
      try {
        const response = await fetch(`${API_URL}/insights`)
        const data = await response.json()
        
        setOpportunities(data.opportunities || [])
        setHypotheses(data.hypotheses || [])
        setPainPoints(data.pain_points || [])
      } catch (error) {
        console.error('Error fetching insights data:', error)
        // Set empty arrays if API fails
        setOpportunities([])
        setHypotheses([])
        setPainPoints([])
      }
    }

    fetchData()
  }, [])

  const handleRefresh = () => {
    setLoading(true)
    setTimeout(() => setLoading(false), 1000)
  }

  const getPriorityColor = (score) => {
    if (score >= 0.8) return 'bg-red-900/30 border-red-800 text-red-400'
    if (score >= 0.6) return 'bg-yellow-900/30 border-yellow-800 text-yellow-400'
    return 'bg-green-900/30 border-green-800 text-green-400'
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-gray-400" />
          <span className="text-sm text-gray-400">Filters:</span>
        </div>
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
        >
          <option value="all">All Categories</option>
          <option value="discovery">Discovery</option>
          <option value="personalization">Personalization</option>
          <option value="ui">UI/UX</option>
          <option value="content">Content</option>
        </select>
        <button
          onClick={handleRefresh}
          disabled={loading}
          className="ml-auto flex items-center gap-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 px-4 py-2 rounded-lg text-sm transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-red-900/30 rounded-lg">
              <AlertTriangle className="w-5 h-5 text-red-400" />
            </div>
            <h3 className="text-lg font-semibold">Pain Points</h3>
          </div>
          <p className="text-3xl font-bold text-red-400">5</p>
          <p className="text-sm text-gray-400 mt-1">Critical issues identified</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-green-900/30 rounded-lg">
              <Lightbulb className="w-5 h-5 text-green-400" />
            </div>
            <h3 className="text-lg font-semibold">Opportunities</h3>
          </div>
          <p className="text-3xl font-bold text-green-400">5</p>
          <p className="text-sm text-gray-400 mt-1">High-priority opportunities</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-blue-900/30 rounded-lg">
              <TrendingUp className="w-5 h-5 text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold">Hypotheses</h3>
          </div>
          <p className="text-3xl font-bold text-blue-400">4</p>
          <p className="text-sm text-gray-400 mt-1">Testable hypotheses generated</p>
        </div>
      </div>

      {/* Pain Points */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">Pain Points Analysis</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={painPoints}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="name" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip
              contentStyle={{ backgroundColor: '#1f2937', border: '#374151' }}
              itemStyle={{ color: '#f3f4f6' }}
            />
            <Legend />
            <Bar dataKey="severity" fill="#ef4444" name="Severity" />
            <Bar dataKey="frequency" fill="#3b82f6" name="Frequency" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Opportunities */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">Product Opportunities</h3>
        <div className="space-y-4">
          {opportunities.map((opp) => (
            <div key={opp.id} className="p-4 bg-gray-700/50 rounded-lg border border-gray-600">
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(opp.priority)}`}>
                      Priority: {(opp.priority * 100).toFixed(0)}%
                    </span>
                    <span className="text-sm text-gray-400">{opp.category}</span>
                  </div>
                  <p className="text-base">{opp.description}</p>
                </div>
              </div>
              <div className="flex items-center gap-6 mt-3 text-sm">
                <div>
                  <span className="text-gray-400">Impact:</span>
                  <span className="ml-2 font-medium">{(opp.impact * 100).toFixed(0)}%</span>
                </div>
                <div>
                  <span className="text-gray-400">Feasibility:</span>
                  <span className="ml-2 font-medium">{(opp.feasibility * 100).toFixed(0)}%</span>
                </div>
                <div>
                  <span className="text-gray-400">Evidence:</span>
                  <span className="ml-2 font-medium">{opp.evidence} mentions</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Hypotheses */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">Research Hypotheses</h3>
        <div className="space-y-4">
          {hypotheses.map((hyp) => (
            <div key={hyp.id} className="p-4 bg-gray-700/50 rounded-lg border border-gray-600">
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(hyp.overallScore)}`}>
                      Score: {(hyp.overallScore * 100).toFixed(0)}%
                    </span>
                    <span className="text-sm text-gray-400">Target: {hyp.targetSegment}</span>
                  </div>
                  <p className="text-base">{hyp.statement}</p>
                </div>
              </div>
              <div className="flex items-center gap-6 mt-3 text-sm">
                <div>
                  <span className="text-gray-400">Data Support:</span>
                  <span className="ml-2 font-medium">{(hyp.dataSupport * 100).toFixed(0)}%</span>
                </div>
                <div>
                  <span className="text-gray-400">Strategic Alignment:</span>
                  <span className="ml-2 font-medium">{(hyp.strategicAlignment * 100).toFixed(0)}%</span>
                </div>
                <div>
                  <span className="text-gray-400">Testability:</span>
                  <span className="ml-2 font-medium">{(hyp.testability * 100).toFixed(0)}%</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Action Items */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <CheckCircle className="w-5 h-5 mr-2 text-green-400" />
          Recommended Actions
        </h3>
        <div className="space-y-3">
          <div className="flex items-start p-3 bg-green-900/20 border border-green-800 rounded-lg">
            <div className="flex-1">
              <p className="font-medium text-green-400">Priority 1: Improve Discovery Features</p>
              <p className="text-sm text-gray-300 mt-1">Focus on enhancing music discovery algorithms and UI to address the most critical pain point</p>
            </div>
          </div>
          <div className="flex items-start p-3 bg-blue-900/20 border border-blue-800 rounded-lg">
            <div className="flex-1">
              <p className="font-medium text-blue-400">Priority 2: Test Personalization Hypothesis</p>
              <p className="text-sm text-gray-300 mt-1">Run A/B test to validate hypothesis about personalization impact on Habitual Listeners</p>
            </div>
          </div>
          <div className="flex items-start p-3 bg-yellow-900/20 border border-yellow-800 rounded-lg">
            <div className="flex-1">
              <p className="font-medium text-yellow-400">Priority 3: Address UI/UX Issues</p>
              <p className="text-sm text-gray-300 mt-1">Implement quick fixes for common UI/UX complaints identified in reviews</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Insights
