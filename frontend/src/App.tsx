
import React, { useState, useEffect } from 'react';
import { CopilotKit } from '@copilotkit/react-core';
import '@copilotkit/react-ui/styles.css';

import Dashboard from './components/Dashboard';
import ChatInterface from './components/ChatInterface';
import SearchInterface from './components/SearchInterface';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const COPILOT_API_KEY = import.meta.env.VITE_COPILOT_CLOUD_API_KEY || '';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [systemHealth, setSystemHealth] = useState<any>(null);

  useEffect(() => {
    checkSystemHealth();
    const interval = setInterval(checkSystemHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const checkSystemHealth = async () => {
    try {
      const response = await fetch(`${API_URL}/health`);
      const health = await response.json();
      setSystemHealth(health);
    } catch (error) {
      console.error('Health check failed:', error);
      setSystemHealth({ status: 'unhealthy', error: error.message });
    }
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard systemHealth={systemHealth} />;
      case 'chat':
        return <ChatInterface />;
      case 'search':
        return <SearchInterface />;
      case 'analytics':
        return <AnalyticsDashboard />;
      default:
        return <Dashboard systemHealth={systemHealth} />;
    }
  };

  return (
    <CopilotKit publicApiKey={COPILOT_API_KEY}>
      <div className="app">
        <header className="app-header">
          <h1>Customer Service AI Dashboard</h1>
          <div className="system-status">
            <span className={`status-indicator ${systemHealth?.status}`}>
              {systemHealth?.status || 'checking...'}
            </span>
          </div>
        </header>

        <nav className="app-nav">
          <button
            className={activeTab === 'dashboard' ? 'active' : ''}
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </button>
          <button
            className={activeTab === 'chat' ? 'active' : ''}
            onClick={() => setActiveTab('chat')}
          >
            Chat Interface
          </button>
          <button
            className={activeTab === 'search' ? 'active' : ''}
            onClick={() => setActiveTab('search')}
          >
            Semantic Search
          </button>
          <button
            className={activeTab === 'analytics' ? 'active' : ''}
            onClick={() => setActiveTab('analytics')}
          >
            Analytics
          </button>
        </nav>

        <main className="app-main">
          {renderContent()}
        </main>
      </div>
    </CopilotKit>
  );
}

export default App;
