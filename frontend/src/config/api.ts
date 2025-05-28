// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const MCP_BASE_URL = import.meta.env.VITE_MCP_BASE_URL || 'http://localhost:8001';
const WORKER_BASE_URL = import.meta.env.VITE_WORKER_BASE_URL || 'http://localhost:8002';

export const apiConfig = {
  baseUrl: API_BASE_URL,
  mcpUrl: MCP_BASE_URL,
  workerUrl: WORKER_BASE_URL,
  endpoints: {
    // Backend endpoints
    health: '/health',
    chat: '/chat',
    search: '/search',
    analytics: {
      sentiment: '/analytics/sentiment',
    },
    stripe: {
      events: '/stripe/events',
    },
    // MCP endpoints
    mcp: {
      health: '/health',
      queue: '/_queue',
      webhook: '/webhook',
      notify: '/notify',
    },
    // Worker endpoints
    worker: {
      health: '/health',
      process: '/process',
    },
  },
};

// Helper function to build full API URLs
export const buildApiUrl = (endpoint: string, service: 'backend' | 'mcp' | 'worker' = 'backend'): string => {
  const baseUrl = service === 'mcp' ? apiConfig.mcpUrl : 
                  service === 'worker' ? apiConfig.workerUrl : 
                  apiConfig.baseUrl;
  return `${baseUrl}${endpoint}`;
};

// Helper function for making API requests
export const apiRequest = async (endpoint: string, options?: RequestInit, service: 'backend' | 'mcp' | 'worker' = 'backend') => {
  const url = buildApiUrl(endpoint, service);
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });
  
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }
  
  return response.json();
};

// MCP-specific helper functions
export const mcpRequest = async (endpoint: string, options?: RequestInit) => {
  return apiRequest(endpoint, options, 'mcp');
};

export const workerRequest = async (endpoint: string, options?: RequestInit) => {
  return apiRequest(endpoint, options, 'worker');
};

// Queue a task via MCP server
export const queueTask = async (taskType: string, payload: any, priority: number = 1) => {
  return mcpRequest(apiConfig.endpoints.mcp.queue, {
    method: 'POST',
    body: JSON.stringify({
      task_type: taskType,
      payload,
      priority,
    }),
  });
};

// Send webhook via MCP server
export const sendWebhook = async (source: string, eventType: string, data: any) => {
  return mcpRequest(apiConfig.endpoints.mcp.webhook, {
    method: 'POST',
    body: JSON.stringify({
      source,
      event_type: eventType,
      data,
    }),
  });
};

// Debug function to log current configuration
export const logApiConfig = () => {
  console.log('API Configuration:', {
    backend: apiConfig.baseUrl,
    mcp: apiConfig.mcpUrl,
    worker: apiConfig.workerUrl,
    environment: import.meta.env.MODE,
    isDev: import.meta.env.DEV,
  });
}; 