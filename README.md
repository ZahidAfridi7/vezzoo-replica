# Veezoo Replica

A production-ready, multi-tenant SaaS product inspired by Veezoo, enabling users to connect to their databases, visualize schema as a knowledge graph, and query data using a GPT-powered chat interface.

## Features

- **Multi-tenant Architecture**: Organization-based access control.
- **Database Connectivity**: Securely connect to PostgreSQL databases.
- **Schema Introspection**: Automatically scan and model database schemas as knowledge graphs.
- **Knowledge Graph UI**: Interactive visualization of database schemas using `react-force-graph`.
- **LLM-Powered Chat**: Natural language interface to query data, powered by OpenAI GPT-4.
- **Secure Authentication**: JWT-based auth with encrypted database credentials.

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy (Async), PostgreSQL, Celery/Redis (Background Jobs), OpenAI API.
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, Zustand, React Force Graph.
- **Infrastructure**: Docker Compose.

## Getting Started

### Prerequisites

- Docker & Docker Compose
- OpenAI API Key

### Setup

1. **Clone the repository**
2. **Environment Variables**:
   - Copy `.env.example` to `.env` in the root directory.
   - Fill in `OPENAI_API_KEY` and `ENCRYPTION_KEY` (generate a 32-byte url-safe base64 key).

3. **Run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

4. **Access the Application**:
   - Frontend: `http://localhost:3000`
   - Backend API Docs: `http://localhost:8000/docs`

## Usage Flow

1. **Sign Up**: Create an account and organization.
2. **Connect Database**: Add a PostgreSQL connection (Host, Port, User, Password, DB Name).
3. **Scan Schema**: Click "Test Connection" (which currently triggers a basic test) and then use the API or future UI to trigger a scan (currently auto-scan logic is in place via API).
4. **Explore Graph**: Navigate to the connection to view the Knowledge Graph.
5. **Chat**: Go to the Chat page, select a connection, and ask questions like "How many users are there?".

## Development

- **Backend**: `backend/`
- **Frontend**: `frontend/`

## License

MIT