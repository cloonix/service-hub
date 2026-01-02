# Service Hub

A collection of API services and MCP servers for LLM integration.

## Features

- 🚀 FastAPI backend with YouTube transcript service
- 🔐 API key authentication with master key bypass
- 🤖 MCP server for LLM integration (Claude, etc.)
- ⚡ TTL cache with disk persistence
- 🛡️ Rate limiting per API key tier
- 🐳 Docker Compose deployment

## Quick Start

### Production (Pull from GitHub Container Registry)

```bash
# 1. Clone and configure
git clone git@github.com:cloonix/service-hub.git
cd service-hub
cp .env.example .env
# Edit .env with your configuration

# 2. Start services (pulls latest images)
docker compose up -d

# 3. Test
curl http://localhost:8000/health
```

### Development (Build locally)

```bash
# 1. Clone and configure
git clone git@github.com:cloonix/service-hub.git
cd service-hub
cp .env.example .env
# Edit .env with your configuration

# 2. Build and start services
docker compose -f docker-compose.dev.yml up -d

# 3. Test
curl http://localhost:8000/health
```

**Services:**
- API: http://localhost:8000
- MCP: http://localhost:8001/mcp
- Docs: http://localhost:8000/docs

## API Usage

### Authentication

Two methods:

**1. Master Key** (Development - bypasses database):
```bash
# In .env
MASTER_API_KEY=your-secret-key-here
```

**2. Database Keys** (Production):
```bash
# Create API key
docker compose exec api python scripts/manage_keys.py create myapp --tier premium

# Use the generated key
curl -H "X-API-Key: myapi_live_..." http://localhost:8000/api/v1/youtube/transcript
```

### YouTube Transcripts

```bash
# Get transcript
curl -X POST "http://localhost:8000/api/v1/youtube/transcript" \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url_or_id": "dQw4w9WgXcQ",
    "languages": ["en"],
    "format_type": "plain"
  }'

# List languages
curl "http://localhost:8000/api/v1/youtube/languages/dQw4w9WgXcQ" \
  -H "X-API-Key: your-key"
```

**Formats:** `plain`, `structured`, `srt`, `vtt`

## MCP Server

The MCP server exposes YouTube transcripts to LLMs via Model Context Protocol.

### Tools
- `get_youtube_transcript(video_url_or_id, languages, format_type)`
- `list_youtube_languages(video_id)`

### Claude Desktop Integration

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

### Architecture

```
┌─────────────┐
│ MCP Client  │ (Claude, etc.)
└──────┬──────┘
       │ HTTP/SSE :8001
┌──────▼──────┐
│ MCP Server  │
└──────┬──────┘
       │ HTTP :8000 (master key)
┌──────▼──────┐
│ FastAPI     │
└─────────────┘
```

## API Key Tiers

| Tier    | Rate Limit  | Use Case        |
|---------|-------------|-----------------|
| free    | 100/min     | Testing         |
| premium | 1000/min    | Production      |
| admin   | 10000/min   | Internal tools  |

## Configuration

All settings via `.env`:

```bash
# API
ENVIRONMENT=production
DEBUG=false
MASTER_API_KEY=your-secret-key

# Database
DATABASE_URL=sqlite:///./data/myapi.db

# Cache
CACHE_ENABLED=true
CACHE_TTL=3600

# MCP
MCP_TRANSPORT=streamable-http
FASTAPI_URL=http://api:8000
```

See `.env.example` for all options.

## Docker Images

Pre-built images are automatically published to GitHub Container Registry on every push to main:

- **API:** `ghcr.io/cloonix/service-hub-api:latest`
- **MCP:** `ghcr.io/cloonix/service-hub-mcp:latest`

**Available tags:**
- `latest` - Latest build from main branch
- `main` - Same as latest
- `v*` - Semantic version tags (e.g., `v1.0.0`, `v1.0`, `v1`)
- `main-<sha>` - Specific commit SHA

**Pull images:**
```bash
docker pull ghcr.io/cloonix/service-hub-api:latest
docker pull ghcr.io/cloonix/service-hub-mcp:latest
```

**Multi-platform support:** `linux/amd64`, `linux/arm64`

## Development

```bash
# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload

# Run MCP server
uvicorn mcp_server.server:app --port 8001
```

## Project Structure

```
service-hub/
├── app/                  # FastAPI application
│   ├── api/             # API endpoints
│   ├── core/            # Cache, rate limiting, security
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   └── services/        # Business logic
├── mcp_server/          # MCP server
│   ├── server.py        # Main MCP server
│   ├── tools/           # MCP tool implementations
│   ├── clients/         # API clients
│   ├── prompts/         # MCP prompts
│   └── resources/       # MCP resources
├── scripts/             # Management scripts
├── tests/               # Test suite
├── docker-compose.yml   # Docker services
└── .env.example         # Configuration template
```

## License

MIT
