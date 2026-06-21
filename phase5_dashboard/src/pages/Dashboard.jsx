import React, { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, LineChart, Line, PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'
import { TrendingUp, TrendingDown, Users, MessageSquare, Activity, AlertCircle } from 'lucide-react'

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalReviews: 0,
    avgSentiment: 0,
    activeUsers: 0,
    recentActivity: 0
  })

  const [sentimentData, setSentimentData] = useState([])
  const [topicData, setTopicData] = useState([])

  useEffect(() => {
    // Fetch real data from API
    const fetchData = async () => {
      try {
        // Fetch stats
        const statsResponse = await fetch('http://127.0.0.1:5000/api/stats')
        const statsData = await statsResponse.json()
        setStats({
          totalReviews: statsData.total_reviews || 0,
          avgSentiment: statsData.avg_sentiment || 0,
          activeUsers: statsData.active_users || 0,
          recentActivity: statsData.recent_activity || 0
        })

        // Fetch sentiment data
        const sentimentResponse = await fetch('http://127.0.0.1:5000/api/sentiment')
        const sentimentData = await sentimentResponse.json()
        setSentimentData(sentimentData.sentiment_trend || [])

        // Fetch topic data
        const topicResponse = await fetch('http://127.0.0.1:5000/api/topics')
        const topicData = await topicResponse.json()
        const formattedTopicData = (topicData.topics || []).slice(0, 5).map(topic => ({
          name: topic.topic,
          value: topic.frequency,
          color: '#10b981'
        }))
        setTopicData(formattedTopicData)
      } catch (error) {
        console.error('Error fetching data:', error)
        // Fallback to default values if API fails
        setStats({
          totalReviews: 0,
          avgSentiment: 0,
          activeUsers: 0,
          recentActivity: 0
        })
      }
    }

    fetchData()
  }, [])

  const StatCard = ({ title, value, icon: Icon, trend, trendUp }) => (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm">{title}</p>
          <p className="text-2xl font-bold mt-1">{value.toLocaleString()}</p>
        </div>
        <div className={`p-3 rounded-lg ${trendUp ? 'bg-green-900' : 'bg-red-900'}`}>
          <Icon className={`w-6 h-6 ${trendUp ? 'text-green-400' : 'text-red-400'}`} />
        </div>
      </div>
      <div className={`flex items-center mt-4 text-sm ${trendUp ? 'text-green-400' : 'text-red-400'}`}>
        {trendUp ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
        {trend}
      </div>
    </div>
  )

  return (
    <div className="space-y-6 mt-0">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Reviews"
          value={stats.totalReviews}
          icon={MessageSquare}
          trend="+12%"
          trendUp={true}
        />
        <StatCard
          title="Avg Sentiment"
          value={stats.avgSentiment.toFixed(2)}
          icon={TrendingUp}
          trend="+5%"
          trendUp={true}
        />
        <StatCard
          title="Active Users"
          value={stats.activeUsers}
          icon={Users}
          trend="+8%"
          trendUp={true}
        />
        <StatCard
          title="Recent Activity"
          value={stats.recentActivity}
          icon={Activity}
          trend="-3%"
          trendUp={false}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sentiment Trend */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4">Sentiment Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={sentimentData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1f2937', border: '#374151' }}
                itemStyle={{ color: '#f3f4f6' }}
              />
              <Legend />
              <Bar dataKey="positive" fill="#10b981" name="Positive" />
              <Bar dataKey="negative" fill="#ef4444" name="Negative" />
              <Bar dataKey="neutral" fill="#6b7280" name="Neutral" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Topic Distribution */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4">Topic Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={topicData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {topicData.map((entry, index) => (
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
      </div>

      {/* Recent Alerts */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <AlertCircle className="w-5 h-5 mr-2 text-yellow-400" />
          Recent Alerts
        </h3>
        <div className="space-y-3">
          <div className="flex items-center p-3 bg-red-900/20 border border-red-800 rounded-lg">
            <div className="flex-1">
              <p className="text-sm font-medium text-red-400">Negative sentiment spike detected</p>
              <p className="text-xs text-gray-400">UI/UX issues - 2 hours ago</p>
            </div>
          </div>
          <div className="flex items-center p-3 bg-yellow-900/20 border border-yellow-800 rounded-lg">
            <div className="flex-1">
              <p className="text-sm font-medium text-yellow-400">Discovery feature engagement drop</p>
              <p className="text-xs text-gray-400">15% decrease - 5 hours ago</p>
            </div>
          </div>
          <div className="flex items-center p-3 bg-blue-900/20 border border-blue-800 rounded-lg">
            <div className="flex-1">
              <p className="text-sm font-medium text-blue-400">New user segment identified</p>
              <p className="text-xs text-gray-400">Genre Explorer segment - 1 day ago</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
