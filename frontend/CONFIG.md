# Frontend Configuration

## Environment Variables

The frontend uses environment variables to configure the backend API connection.

### VITE_API_BASE_URL

Set the base URL for the backend API.

**Default:** `http://localhost:8000`

**Examples:**
- Development: `http://localhost:8000`
- Production: `https://your-api-domain.com`
- Docker: `http://backend:8000`
- Custom port: `http://localhost:3001`

### Setting Environment Variables

#### Option 1: Create a `.env` file
Create a `.env` file in the `frontend/` directory:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

#### Option 2: Set environment variable when running
```bash
VITE_API_BASE_URL=http://localhost:3001 npm run dev
```

#### Option 3: Export environment variable
```bash
export VITE_API_BASE_URL=http://localhost:3001
npm run dev
```

### Docker Configuration

When running with Docker Compose, the API URL should point to the backend service:

```bash
VITE_API_BASE_URL=http://backend:8000
```

### Production Configuration

For production deployments, set the API URL to your production backend:

```bash
VITE_API_BASE_URL=https://api.yourdomain.com
```

## Configuration File

The API configuration is centralized in `src/config/api.ts`. This file:

- Reads the `VITE_API_BASE_URL` environment variable
- Provides helper functions for making API requests
- Centralizes all API endpoint definitions

You can modify this file to add new endpoints or change the configuration logic. 