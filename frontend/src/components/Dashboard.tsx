import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { apiRequest, apiConfig } from '../config/api';

interface DashboardProps {
  systemHealth: any;
}

const Dashboard: React.FC<DashboardProps> = ({ systemHealth }) => {
  const [conversations, setConversations] = useState([]);
  const [sentimentData, setSentimentData] = useState([]);
  const [stripeEvents, setStripeEvents] = useState([]);
  const [debugInfo, setDebugInfo] = useState<any>(null);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch sentiment analytics
      try {
        const sentimentData = await apiRequest(apiConfig.endpoints.analytics.sentiment);
        setSentimentData(generateSentimentChart(sentimentData));
      } catch (error) {
        console.error('Error fetching sentiment data:', error);
      }

      // Fetch recent Stripe events
      try {
        const eventsData = await apiRequest(`${apiConfig.endpoints.stripe.events}?limit=10`);
        setStripeEvents(eventsData.events || []);
      } catch (error) {
        console.error('Error fetching Stripe events:', error);
      }

      // Mock conversation data for now
      setConversations([
        { id: '1', user: 'customer123', message: 'Need help with payment', status: 'resolved', timestamp: new Date().toISOString() },
        { id: '2', user: 'customer456', message: 'Invoice question', status: 'pending', timestamp: new Date().toISOString() },
      ]);

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  const generateSentimentChart = (data: any) => {
    // Generate mock sentiment data over time
    const days = 7;
    const chartData = [];
    for (let i = days; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      chartData.push({
        date: date.toLocaleDateString(),
        positive: 0.6 + Math.random() * 0.3,
        neutral: 0.2 + Math.random() * 0.2,
        negative: 0.1 + Math.random() * 0.1,
      });
    }
    return chartData;
  };

  const performDashboardAnalysis = async (analysisType: string) => {
    // Simulate AI analysis
    return {
      type: analysisType,
      insights: `Analysis for ${analysisType} shows positive trends`,
      recommendations: ['Continue current approach', 'Monitor edge cases'],
      timestamp: new Date().toISOString(),
    };
  };

  const refreshData = () => {
    fetchDashboardData();
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Customer Service Dashboard</h2>
        <button onClick={refreshData} className="refresh-button">
          Refresh Data
        </button>
      </div>

      <div className="dashboard-grid">
        {/* System Health */}
        <div className="dashboard-card">
          <h3>System Health</h3>
          <div className="health-grid">
            {systemHealth && (
              <>
                <div className="health-item">
                  <span>Overall:</span>
                  <span className={`status ${systemHealth.status}`}>{systemHealth.status}</span>
                </div>
                {systemHealth.services && Object.entries(systemHealth.services).map(([service, status]) => (
                  <div key={service} className="health-item">
                    <span>{service}:</span>
                    <span className={`status ${status}`}>{status as string}</span>
                  </div>
                ))}
              </>
            )}
          </div>
        </div>

        {/* Sentiment Analytics */}
        <div className="dashboard-card chart-card">
          <h3>Sentiment Trend (7 days)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={sentimentData}>
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

        {/* Recent Conversations */}
        <div className="dashboard-card">
          <h3>Recent Conversations</h3>
          <div className="conversation-list">
            {conversations.map((conv: any) => (
              <div key={conv.id} className="conversation-item">
                <div className="conversation-header">
                  <span className="user-id">{conv.user}</span>
                  <span className={`status ${conv.status}`}>{conv.status}</span>
                </div>
                <div className="conversation-message">{conv.message}</div>
                <div className="conversation-time">{new Date(conv.timestamp).toLocaleString()}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Stripe Events */}
        <div className="dashboard-card">
          <h3>Recent Payments</h3>
          <div className="stripe-events">
            {stripeEvents.map((event: any) => (
              <div key={event.id} className="stripe-event">
                <div className="event-type">{event.type}</div>
                <div className="event-time">{new Date(event.created * 1000).toLocaleString()}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Debug Panel */}
        {debugInfo && (
          <div className="dashboard-card debug-card">
            <h3>AI Analysis</h3>
            <div className="debug-content">
              <pre>{JSON.stringify(debugInfo, null, 2)}</pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
