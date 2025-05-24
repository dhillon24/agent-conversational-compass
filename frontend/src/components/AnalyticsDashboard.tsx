
import React, { useState, useEffect } from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const AnalyticsDashboard: React.FC = () => {
  const [timeRange, setTimeRange] = useState('7d');
  const [analyticsData, setAnalyticsData] = useState<any>({});
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchAnalytics();
  }, [timeRange]);

  const fetchAnalytics = async () => {
    setIsLoading(true);
    try {
      // Mock analytics data for demonstration
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const mockData = {
        sentimentTrend: generateSentimentTrend(),
        conversationVolume: generateConversationVolume(),
        responseTime: generateResponseTime(),
        topIssues: generateTopIssues(),
        customerSatisfaction: generateSatisfactionData(),
        paymentMetrics: generatePaymentMetrics(),
      };
      
      setAnalyticsData(mockData);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const generateSentimentTrend = () => {
    const days = timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : 90;
    const data = [];
    for (let i = days; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      data.push({
        date: date.toLocaleDateString(),
        positive: 0.6 + Math.random() * 0.3,
        neutral: 0.2 + Math.random() * 0.2,
        negative: 0.1 + Math.random() * 0.1,
      });
    }
    return data;
  };

  const generateConversationVolume = () => {
    const data = [];
    const hours = 24;
    for (let i = 0; i < hours; i++) {
      data.push({
        hour: `${i}:00`,
        conversations: Math.floor(Math.random() * 50) + 10,
        resolved: Math.floor(Math.random() * 40) + 5,
      });
    }
    return data;
  };

  const generateResponseTime = () => {
    const data = [];
    const days = 7;
    for (let i = days; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      data.push({
        date: date.toLocaleDateString(),
        avgResponseTime: Math.random() * 300 + 30, // 30-330 seconds
        firstResponseTime: Math.random() * 120 + 10, // 10-130 seconds
      });
    }
    return data;
  };

  const generateTopIssues = () => [
    { issue: 'Payment Problems', count: 45, percentage: 30 },
    { issue: 'Account Access', count: 38, percentage: 25 },
    { issue: 'Billing Questions', count: 32, percentage: 21 },
    { issue: 'Technical Support', count: 23, percentage: 15 },
    { issue: 'Refund Requests', count: 12, percentage: 9 },
  ];

  const generateSatisfactionData = () => [
    { name: 'Very Satisfied', value: 35, color: '#22c55e' },
    { name: 'Satisfied', value: 40, color: '#84cc16' },
    { name: 'Neutral', value: 15, color: '#eab308' },
    { name: 'Dissatisfied', value: 8, color: '#f97316' },
    { name: 'Very Dissatisfied', value: 2, color: '#ef4444' },
  ];

  const generatePaymentMetrics = () => ({
    totalRevenue: 125420,
    successRate: 97.5,
    averageTransaction: 89.50,
    refundRate: 2.1,
  });

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  return (
    <div className="analytics-dashboard">
      <div className="analytics-header">
        <h2>Analytics Dashboard</h2>
        <div className="time-range-selector">
          <button
            className={timeRange === '7d' ? 'active' : ''}
            onClick={() => setTimeRange('7d')}
          >
            7 Days
          </button>
          <button
            className={timeRange === '30d' ? 'active' : ''}
            onClick={() => setTimeRange('30d')}
          >
            30 Days
          </button>
          <button
            className={timeRange === '90d' ? 'active' : ''}
            onClick={() => setTimeRange('90d')}
          >
            90 Days
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="loading-spinner">Loading analytics...</div>
      ) : (
        <div className="analytics-grid">
          {/* Key Metrics */}
          <div className="analytics-card metrics-card">
            <h3>Key Metrics</h3>
            <div className="metrics-grid">
              <div className="metric">
                <span className="metric-value">1,247</span>
                <span className="metric-label">Total Conversations</span>
              </div>
              <div className="metric">
                <span className="metric-value">94.2%</span>
                <span className="metric-label">Resolution Rate</span>
              </div>
              <div className="metric">
                <span className="metric-value">2.3m</span>
                <span className="metric-label">Avg Response Time</span>
              </div>
              <div className="metric">
                <span className="metric-value">4.6/5</span>
                <span className="metric-label">Customer Rating</span>
              </div>
            </div>
          </div>

          {/* Sentiment Trend */}
          <div className="analytics-card chart-card">
            <h3>Sentiment Trend</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analyticsData.sentimentTrend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="positive" stroke="#22c55e" strokeWidth={2} />
                <Line type="monotone" dataKey="neutral" stroke="#eab308" strokeWidth={2} />
                <Line type="monotone" dataKey="negative" stroke="#ef4444" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Conversation Volume */}
          <div className="analytics-card chart-card">
            <h3>Conversation Volume (24h)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analyticsData.conversationVolume}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="conversations" fill="#3b82f6" />
                <Bar dataKey="resolved" fill="#22c55e" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Customer Satisfaction */}
          <div className="analytics-card chart-card">
            <h3>Customer Satisfaction</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={analyticsData.customerSatisfaction}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percentage }) => `${name}: ${percentage}%`}
                >
                  {analyticsData.customerSatisfaction?.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Top Issues */}
          <div className="analytics-card">
            <h3>Top Issues</h3>
            <div className="issues-list">
              {analyticsData.topIssues?.map((issue: any, index: number) => (
                <div key={index} className="issue-item">
                  <div className="issue-info">
                    <span className="issue-name">{issue.issue}</span>
                    <span className="issue-count">{issue.count} cases</span>
                  </div>
                  <div className="issue-bar">
                    <div
                      className="issue-progress"
                      style={{ width: `${issue.percentage}%` }}
                    />
                  </div>
                  <span className="issue-percentage">{issue.percentage}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Payment Metrics */}
          <div className="analytics-card">
            <h3>Payment Metrics</h3>
            <div className="payment-metrics">
              <div className="payment-metric">
                <span className="payment-value">${analyticsData.paymentMetrics?.totalRevenue?.toLocaleString()}</span>
                <span className="payment-label">Total Revenue</span>
              </div>
              <div className="payment-metric">
                <span className="payment-value">{analyticsData.paymentMetrics?.successRate}%</span>
                <span className="payment-label">Success Rate</span>
              </div>
              <div className="payment-metric">
                <span className="payment-value">${analyticsData.paymentMetrics?.averageTransaction}</span>
                <span className="payment-label">Avg Transaction</span>
              </div>
              <div className="payment-metric">
                <span className="payment-value">{analyticsData.paymentMetrics?.refundRate}%</span>
                <span className="payment-label">Refund Rate</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyticsDashboard;
