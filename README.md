# YouTube Transcript API

A production-ready FastAPI backend providing YouTube transcript fetching with API key authentication, caching, and rate limiting.

## Features

- 🚀 FastAPI-based RESTful API
- 🔐 API key authentication with bcrypt hashing
- 🔑 Master key bypass for development/admin access
- ⚡ TTL cache with LRU eviction and disk persistence
- 🛡️ Rate limiting with sliding window algorithm
- 📊 Admin endpoints for API key management
- 🐳 Docker support for easy deployment
- ✅ Comprehensive testing suite
- 📝 Full type safety with Pydantic v2

## Architecture

```
FastAPI Backend (Port 8000)
├── API Key Authentication
├── Rate Limiting (per-tier)
├── TTL Cache with Disk Persistence
└── YouTube Transcript Service

Future: MCP Server (Port 8001)
└── HTTP Client → FastAPI Backend
```

## Quick Start

### 1. Clone and Install

```bash
git clone <repository-url>
cd myapi
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Create Admin API Key

```bash
python scripts/manage_keys.py create admin --tier admin --description "Master admin key"
```

Save the generated API key securely - it won't be shown again!

### 4. Run the Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Visit http://localhost:8000/docs for interactive API documentation.

## API Usage

### Get Transcript

```bash
curl -X POST "http://localhost:8000/api/v1/youtube/transcript" \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url_or_id": "dQw4w9WgXcQ",
    "languages": ["en"],
    "format_type": "plain"
  }'
```

### List Available Languages

```bash
curl "http://localhost:8000/api/v1/youtube/languages/dQw4w9WgXcQ" \
  -H "X-API-Key: your-api-key-here"
```

### Admin: Create API Key

```bash
curl -X POST "http://localhost:8000/api/v1/admin/keys" \
  -H "X-API-Key: your-admin-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "client-key",
    "tier": "free",
    "rate_limit": 100,
    "rate_window": 60
  }'
```

## API Key Tiers

| Tier    | Rate Limit          | Use Case                    |
|---------|---------------------|-----------------------------|
| free    | 100 req/min         | Development, testing        |
| premium | 1000 req/min        | Production applications     |
| admin   | 10000 req/min       | Admin operations, MCP server|

## Authentication Methods

### 1. Master API Key (Recommended for Development)

The master API key is a special bypass key configured via the `MASTER_API_KEY` environment variable:

**Features:**
- Bypasses database lookup for faster authentication
- Bypasses rate limiting completely
- Automatically has admin-tier permissions
- Perfect for development, testing, and administrative tasks

**Setup:**
```bash
# In .env file
MASTER_API_KEY=dev-master-key-12345
```

**Usage:**
```bash
curl -X POST "http://localhost:8000/api/v1/youtube/transcript" \
  -H "X-API-Key: dev-master-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"video_url_or_id": "dQw4w9WgXcQ"}'
```

**Security Notes:**
- Keep the master key secret in production environments
- Use a strong, random value for production
- Leave empty to disable the master key bypass feature
- Never commit the master key to version control

### 2. Database API Keys (Recommended for Production)

Create API keys stored in the database with fine-grained control:

```bash
# Via CLI
python scripts/manage_keys.py create myapp --tier premium

# Via API (requires admin key)
curl -X POST "http://localhost:8000/api/v1/admin/keys" \
  -H "X-API-Key: your-admin-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "client-key",
    "tier": "free",
    "rate_limit": 100,
    "rate_window": 60
  }'
```

**Benefits:**
- Granular rate limiting per key
- Can be enabled/disabled without server restart
- Trackable usage statistics
- Support for IP whitelisting
- Audit trail with last_used timestamps

## Docker Deployment

### Prerequisites

1. Copy and configure your `.env` file:
```bash
cp .env.example .env
# Edit .env with your production settings
```

### Build and Run

```bash
docker-compose up -d
```

The Docker container will automatically use the `.env` file for all configuration. No environment variables are hardcoded in `docker-compose.yml`.

### Create Admin Key (in container)

```bash
docker-compose exec api python scripts/manage_keys.py create admin --tier admin
```

Save the generated key to your `.env` file as `MASTER_API_KEY`.

## Project Structure

```
myapi/
├── app/
│   ├── api/           # API routes
│   │   ├── deps.py    # Dependency injection
│   │   └── v1/        # API v1 endpoints
│   ├── core/          # Core utilities (cache, rate limit, security)
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   ├── config.py      # Configuration
│   ├── database.py    # Database setup
│   └── main.py        # FastAPI app
├── tests/             # Test suite
├── scripts/           # CLI tools
├── Dockerfile         # Docker configuration
└── docker-compose.yml # Docker Compose
```

## Development

### Install Dev Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run Tests

```bash
pytest
pytest --cov=app --cov-report=html
```

### Code Quality

```bash
# Format code
black app/ tests/

# Lint
ruff check app/ tests/

# Type checking
mypy app/
```

## Configuration

All configuration is managed through the `.env` file. Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your settings
```

**Important**: All environment variables should be in `.env` only. The `docker-compose.yml` file reads from `.env` automatically - do not add environment variables directly in the compose file.

Key environment variables:

```env
# API Settings
ENVIRONMENT=production  # or development
DEBUG=False
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./data/myapi.db

# Cache
CACHE_ENABLED=true
CACHE_TTL=3600
CACHE_MAX_SIZE=100
CACHE_DIR=/app/cache

# Rate Limiting
RATE_LIMIT_ENABLED=true
DEFAULT_RATE_LIMIT=100
DEFAULT_RATE_WINDOW=60

# Security
MASTER_API_KEY=<your-master-key-here>
SECRET_KEY=<random-secret-for-production>

# CORS (restrict in production)
ALLOWED_ORIGINS=*

# YouTube (Optional)
# YOUTUBE_COOKIES=/path/to/cookies.txt
# YOUTUBE_PROXY_HTTP=http://proxy:port
```

See `.env.example` for all available configuration options.

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Health & Metrics

```bash
# Health check
curl http://localhost:8000/health

# Metrics (cache stats)
curl http://localhost:8000/metrics
```

## MCP Server Integration

The project includes an MCP (Model Context Protocol) server that exposes YouTube transcript functionality via HTTP, allowing LLMs and other clients to access transcripts programmatically.

### What is MCP?

MCP is a protocol that allows AI assistants to connect to external tools and services. The YouTube MCP server exposes:

**Tools:**
- `get_youtube_transcript`: Fetch transcripts in various formats (plain, structured, srt, vtt)
- `list_youtube_languages`: List available transcript languages for a video

**Resources:**
- `info://youtube-service`: Service information and usage guide

**Prompts:**
- `summarize_video`: Generate video summary prompts with customizable focus

### Deployment

The MCP server is included in the Docker Compose setup and runs on port **8001** by default.

```bash
# Start both API and MCP servers
docker compose up -d

# MCP server available at:
http://localhost:8001/mcp
```

### Configuration

Configure via environment variables in `.env`:

```env
# MCP Server Settings
MCP_TRANSPORT=streamable-http        # Use HTTP transport
FASTAPI_URL=http://api:8000          # FastAPI backend URL
MASTER_API_KEY=your-master-key-here  # API authentication
```

### Testing the MCP Server

The MCP server uses Server-Sent Events (SSE) for communication. Test with an MCP-compatible client or use the FastAPI backend directly.

**Direct API access (simpler):**
```bash
curl -X POST "http://localhost:8000/api/v1/youtube/transcript" \
  -H "X-API-Key: your-master-key" \
  -H "Content-Type: application/json" \
  -d '{"video_url_or_id": "dQw4w9WgXcQ"}'
```

**MCP endpoint:**
```bash
# MCP server running at http://localhost:8001/mcp
# Requires MCP-compatible client (Claude Desktop, etc.)
```

### MCP Client Integration

#### Option 1: Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "youtube-transcript": {
      "url": "http://localhost:8001/mcp"
    }
  }
}
```

#### Option 2: Custom MCP Client

Use any MCP-compatible HTTP client to connect to `http://localhost:8001/mcp`.

### Standalone Deployment

Run the MCP server separately:

```bash
# Install dependencies
pip install -r requirements.txt

# Run with uvicorn
uvicorn youtube_mcp.server:app --host 0.0.0.0 --port 8001
```

### Architecture

```
┌─────────────────┐
│  MCP Client     │
│ (Claude, etc.)  │
└────────┬────────┘
         │ HTTP/SSE
         │ port 8001
┌────────▼────────┐
│  MCP Server     │
│ youtube_mcp     │
└────────┬────────┘
         │ HTTP
         │ port 8000
┌────────▼────────┐
│  FastAPI        │
│  Backend        │
└─────────────────┘
```

The MCP server acts as a proxy, translating MCP protocol requests into FastAPI calls using the master API key for authentication.

## Security Best Practices

1. ✅ Never commit `.env` files
2. ✅ Use strong API keys (auto-generated)
3. ✅ Rotate API keys regularly (use admin endpoints)
4. ✅ Run with HTTPS in production
5. ✅ Restrict CORS origins in production
6. ✅ Use environment-specific configurations

## Troubleshooting

### Database Issues

```bash
# Reset database
rm data/myapi.db
python -c "from app.database import init_db; init_db()"
```

### Cache Issues

```bash
# Clear cache
rm -rf cache/*
# Or via API (requires admin key)
curl -X POST "http://localhost:8000/api/v1/admin/cache/clear" \
  -H "X-API-Key: your-admin-key"
```

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Support

For issues and questions, please open an issue on GitHub.
