import React, { useState, useEffect } from 'react';
import { Server, Play, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { mcpRequest, workerRequest, queueTask, apiConfig } from '../config/api';

interface Task {
  id: string;
  type: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  payload: any;
  timestamp: string;
}

const MCPInterface: React.FC = () => {
  const [mcpHealth, setMcpHealth] = useState<any>(null);
  const [workerHealth, setWorkerHealth] = useState<any>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    checkServicesHealth();
    const interval = setInterval(checkServicesHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const checkServicesHealth = async () => {
    try {
      const mcpHealthData = await mcpRequest(apiConfig.endpoints.mcp.health);
      setMcpHealth(mcpHealthData);
    } catch (error) {
      console.error('MCP health check failed:', error);
      setMcpHealth({ status: 'unhealthy', error: error.message });
    }

    try {
      const workerHealthData = await workerRequest(apiConfig.endpoints.worker.health);
      setWorkerHealth(workerHealthData);
    } catch (error) {
      console.error('Worker health check failed:', error);
      setWorkerHealth({ status: 'unhealthy', error: error.message });
    }
  };

  const handleQueueTask = async (taskType: string, payload: any) => {
    setIsLoading(true);
    try {
      const result = await queueTask(taskType, payload);
      
      const newTask: Task = {
        id: Date.now().toString(),
        type: taskType,
        status: 'queued',
        payload,
        timestamp: new Date().toISOString(),
      };
      
      setTasks(prev => [newTask, ...prev]);
      console.log('Task queued:', result);
    } catch (error) {
      console.error('Failed to queue task:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const taskExamples = [
    {
      name: 'Conversation Analysis',
      type: 'conversation_analysis',
      payload: {
        user_id: 'demo_user',
        conversation_data: {
          messages: ['I need help with my payment', 'Can you process my refund?']
        }
      }
    },
    {
      name: 'Payment Processing',
      type: 'payment_processing',
      payload: {
        user_id: 'demo_user',
        amount: 99.99,
        currency: 'usd'
      }
    },
    {
      name: 'Webhook Processing',
      type: 'webhook_processing',
      payload: {
        source: 'stripe',
        event_type: 'payment_intent.succeeded',
        data: { id: 'pi_demo123', amount: 2000 }
      }
    }
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'queued':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'processing':
        return <Play className="w-4 h-4 text-blue-500" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  return (
    <div className="mcp-interface">
      <div className="mcp-header">
        <h3>MCP Server Integration</h3>
        <p>Manage tasks and monitor MCP server and worker services</p>
      </div>

      {/* Service Health Status */}
      <div className="services-health">
        <h4>Service Health</h4>
        <div className="health-grid">
          <div className="health-card">
            <div className="health-header">
              <Server className="w-5 h-5" />
              <span>MCP Server</span>
            </div>
            <div className={`health-status ${mcpHealth?.status || 'unknown'}`}>
              {mcpHealth?.status || 'Checking...'}
            </div>
            {mcpHealth?.services && (
              <div className="health-details">
                {Object.entries(mcpHealth.services).map(([service, status]) => (
                  <div key={service} className="health-item">
                    <span>{service}:</span>
                    <span className={`status ${status}`}>{status as string}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="health-card">
            <div className="health-header">
              <Server className="w-5 h-5" />
              <span>Worker Service</span>
            </div>
            <div className={`health-status ${workerHealth?.status || 'unknown'}`}>
              {workerHealth?.status || 'Checking...'}
            </div>
            {workerHealth?.worker && (
              <div className="health-details">
                <div className="health-item">
                  <span>Worker:</span>
                  <span className={`status ${workerHealth.worker}`}>{workerHealth.worker}</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Task Queue Examples */}
      <div className="task-examples">
        <h4>Queue Tasks</h4>
        <div className="examples-grid">
          {taskExamples.map((example, index) => (
            <div key={index} className="example-card">
              <h5>{example.name}</h5>
              <p>Type: {example.type}</p>
              <button
                onClick={() => handleQueueTask(example.type, example.payload)}
                disabled={isLoading}
                className="queue-button"
              >
                {isLoading ? 'Queueing...' : 'Queue Task'}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Task History */}
      <div className="task-history">
        <h4>Task History</h4>
        {tasks.length === 0 ? (
          <p className="no-tasks">No tasks queued yet. Try queueing a task above.</p>
        ) : (
          <div className="tasks-list">
            {tasks.map((task) => (
              <div key={task.id} className="task-item">
                <div className="task-header">
                  {getStatusIcon(task.status)}
                  <span className="task-type">{task.type}</span>
                  <span className="task-status">{task.status}</span>
                </div>
                <div className="task-timestamp">
                  {new Date(task.timestamp).toLocaleString()}
                </div>
                <div className="task-payload">
                  <details>
                    <summary>Payload</summary>
                    <pre>{JSON.stringify(task.payload, null, 2)}</pre>
                  </details>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MCPInterface; 