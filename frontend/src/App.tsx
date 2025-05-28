import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from './components/Dashboard';
import ChatInterface from './components/ChatInterface';
import SearchInterface from './components/SearchInterface';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import MCPInterface from './components/MCPInterface';
import { apiRequest, apiConfig } from './config/api';
import './App.css';

const queryClient = new QueryClient();

function CustomerServiceApp() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [systemHealth, setSystemHealth] = useState<any>(null);

  useEffect(() => {
    checkSystemHealth();
    const interval = setInterval(checkSystemHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const checkSystemHealth = async () => {
    try {
      const health = await apiRequest(apiConfig.endpoints.health);
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
      case 'mcp':
        return <MCPInterface />;
      default:
        return <Dashboard systemHealth={systemHealth} />;
    }
  };

  return (
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
        <button
          className={activeTab === 'mcp' ? 'active' : ''}
          onClick={() => setActiveTab('mcp')}
        >
          MCP Server
        </button>
      </nav>

      <main className="app-main">
        {renderContent()}
      </main>
    </div>
  );
}

const App = () => (
  <QueryClientProvider client={queryClient}>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<CustomerServiceApp />} />
        <Route path="*" element={<div>Page not found</div>} />
      </Routes>
    </BrowserRouter>
  </QueryClientProvider>
);

export default App;
