import React, { useState, useEffect } from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts'
import { Filter, Download, RefreshCw, Users, TrendingUp, Activity } from 'lucide-react'

// API URL configuration with fallback for local development
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api'

const UserSegments = () => {
  const [selectedSegment, setSelectedSegment] = useState(null)
  const [loading, setLoading] = useState(false)

  const [segmentData, setSegmentData] = useState([])
  const [segmentBehavior, setSegmentBehavior] = useState([])

  useEffect(() => {
    // Fetch real data from API
    const fetchData = async () => {
      try {
        const response = await fetch(`${API_URL}/segments`)
        const data = await response.json()
        
        setSegmentData(data.segments || [])
        setSegmentBehavior(data.behavior || [])
      } catch (error) {
        console.error('Error fetching segment data:', error)
        // Set empty arrays if API fails
        setSegmentData([])
        setSegmentBehavior([])
      }
    }

    fetchData()
  }, [])

  const segmentProfiles = {
    'Discovery Focused': {
      description: 'Users who actively seek new music and artists',
      keyBehaviors: ['Frequent discovery', 'Explore new genres', 'Browse recommendations'],
      challenges: ['Limited variety', 'Repetitive recommendations'],
      motivations: ['Find fresh music', 'Discover emerging artists']
    },
    'Habitual Listener': {
      description: 'Users who listen to familiar content and established playlists',
      keyBehaviors: ['Repeat listening', 'Playlist dependence', 'Artist loyalty'],
      challenges: ['Resistance to change', 'Comfort zone'],
      motivations: ['Comfort', 'Familiarity', 'Consistency']
    },
    'Mood-Based': {
      description: 'Users who select music based on current mood or emotional state',
      keyBehaviors: ['Mood matching', 'Emotional listening', 'Situation-based'],
      challenges: ['Context mismatch', 'Limited mood detection'],
      motivations: ['Emotional regulation', 'Mood enhancement']
    },
    'Activity-Based': {
      description: 'Users who listen to music for specific activities',
      keyBehaviors: ['Activity matching', 'Routine listening', 'Purpose-driven'],
      challenges: ['Activity-specific needs', 'Context limitations'],
      motivations: ['Performance enhancement', 'Focus', 'Relaxation']
    },
    'Genre Explorer': {
      description: 'Users who actively explore and discover within specific genres',
      keyBehaviors: ['Genre deep-dives', 'Artist exploration', 'Niche interests'],
      challenges: ['Limited cross-genre discovery', 'Genre silos'],
      motivations: ['Genre expertise', 'Curated experiences']
    },
    'Casual Listener': {
      description: 'Users with low engagement and passive consumption habits',
      keyBehaviors: ['Background listening', 'Low interaction', 'Passive consumption'],
      challenges: ['Low motivation', 'Lack of engagement'],
      motivations: ['Background noise', 'Convenience']
    }
  }

  const handleRefresh = () => {
    setLoading(true)
    setTimeout(() => setLoading(false), 1000)
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-gray-400" />
          <span className="text-sm text-gray-400">Filters:</span>
        </div>
        <select className="bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500">
          <option value="all">All Segments</option>
          <option value="discovery">Discovery Focused</option>
          <option value="habitual">Habitual Listener</option>
          <option value="mood">Mood-Based</option>
          <option value="activity">Activity-Based</option>
          <option value="genre">Genre Explorer</option>
          <option value="casual">Casual Listener</option>
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

      {/* Segment Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Segment Distribution */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4">Segment Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={segmentData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="size"
              >
                {segmentData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: '#1f2937', border: '#374151' }}
                itemStyle={{ color: '#f3f4f6' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Segment Growth */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4">Segment Growth</h3>
          <div className="space-y-3">
            {segmentData.map((segment) => (
              <div key={segment.name} className="flex items-center">
                <div className="w-32 text-sm text-gray-400">{segment.name}</div>
                <div className="flex-1 mx-4">
                  <div className="h-4 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${(segment.size / 3200) * 100}%`,
                        backgroundColor: segment.color
                      }}
                    />
                  </div>
                </div>
                <div className="w-20 text-sm text-right">
                  <span className={`font-medium ${segment.growth.startsWith('+') ? 'text-green-400' : 'text-red-400'}`}>
                    {segment.growth}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Segment Behavior Analysis */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">Segment Behavior Analysis</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={segmentBehavior}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="segment" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip
              contentStyle={{ backgroundColor: '#1f2937', border: '#374151' }}
              itemStyle={{ color: '#f3f4f6' }}
            />
            <Legend />
            <Bar dataKey="New Music" fill="#10b981" name="New Music %" />
            <Bar dataKey="Favorites" fill="#3b82f6" name="Favorites %" />
            <Bar dataKey="Playlists" fill="#f59e0b" name="Playlists %" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Segment Profiles */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">Segment Profiles</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {segmentData.map((segment) => (
            <div
              key={segment.name}
              className="p-4 bg-gray-700/50 rounded-lg border border-gray-600 hover:border-gray-500 transition-colors cursor-pointer"
              onClick={() => setSelectedSegment(segment.name)}
            >
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium">{segment.name}</h4>
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: segment.color }} />
              </div>
              <p className="text-sm text-gray-400 mb-3">
                {segmentProfiles[segment.name]?.description}
              </p>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">{segment.size.toLocaleString()} users</span>
                <span className={segment.growth.startsWith('+') ? 'text-green-400' : 'text-red-400'}>
                  {segment.growth}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Segment Detail Modal */}
      {selectedSegment && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 border border-gray-700">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-xl font-semibold">{selectedSegment}</h3>
              <button
                onClick={() => setSelectedSegment(null)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>
            {segmentProfiles[selectedSegment] && (
              <div className="space-y-4">
                <div>
                  <p className="text-gray-400 text-sm">Description</p>
                  <p className="text-base">{segmentProfiles[selectedSegment].description}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-sm">Key Behaviors</p>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {segmentProfiles[selectedSegment].keyBehaviors.map((behavior) => (
                      <span key={behavior} className="px-3 py-1 bg-gray-700 rounded-full text-sm">
                        {behavior}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-gray-400 text-sm">Challenges</p>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {segmentProfiles[selectedSegment].challenges.map((challenge) => (
                      <span key={challenge} className="px-3 py-1 bg-red-900/30 border border-red-800 rounded-full text-sm text-red-400">
                        {challenge}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-gray-400 text-sm">Motivations</p>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {segmentProfiles[selectedSegment].motivations.map((motivation) => (
                      <span key={motivation} className="px-3 py-1 bg-green-900/30 border border-green-800 rounded-full text-sm text-green-400">
                        {motivation}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default UserSegments
