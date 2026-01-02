# Service Hub

A collection of API services and MCP servers for LLM integration.

## Features

- 🚀 FastAPI backend with YouTube transcript service
- 🔐 API key authentication with master key bypass
- 🤖 MCP server for LLM integration (Claude, etc.)
- 💻 Command-line interface for interactive use
- ⚡ TTL cache with disk persistence
- 🛡️ Rate limiting per API key tier
- 🐳 Docker Compose deployment
- 📦 Reusable library architecture

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

## CLI Usage

The CLI provides a command-line interface for fetching YouTube transcripts without running the API server.

### Installation

```bash
# Core API only (minimal dependencies)
pip install -r requirements.txt

# For CLI support
pip install -r requirements.txt -r requirements-cli.txt

# For MCP server
pip install -r requirements.txt -r requirements-mcp.txt

# For development
pip install -r requirements.txt -r requirements-dev.txt
```

### Commands

**Get transcript:**
```bash
# Plain text (default)
python scripts/youtube-transcript get-transcript dQw4w9WgXcQ

# JSON format with timestamps
python scripts/youtube-transcript get-transcript dQw4w9WgXcQ -f json

# Save as SRT subtitle file
python scripts/youtube-transcript get-transcript dQw4w9WgXcQ -f srt -o subtitles.srt

# Get Spanish transcript
python scripts/youtube-transcript get-transcript dQw4w9WgXcQ -l es

# Multiple languages (fallback)
python scripts/youtube-transcript get-transcript dQw4w9WgXcQ -l en -l es
```

**List available languages:**
```bash
# Show as table
python scripts/youtube-transcript list-languages dQw4w9WgXcQ

# Output as JSON
python scripts/youtube-transcript list-languages dQw4w9WgXcQ --json
```

**Show version:**
```bash
python scripts/youtube-transcript version
```

**Supported formats:**
- `plain` - Plain text (default)
- `json` - JSON with timestamps and metadata
- `srt` - SubRip subtitle format
- `vtt` - WebVTT subtitle format

**Exit codes:**
- `0` - Success
- `1` - General error
- `2` - Invalid video ID
- `3` - No transcript available
- `4` - Transcript unavailable
- `5` - Transcripts disabled

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

The project uses a library-first architecture where core functionality is shared across all interfaces:

```
┌──────────────────────────────────────────────┐
│             lib/youtube/                     │
│  (Core Library - Shared Business Logic)     │
│  - TranscriptService                         │
│  - Formatters (plain, json, srt, vtt)       │
│  - Models & Exceptions                       │
└────────┬──────────────┬──────────────┬───────┘
         │              │              │
    ┌────▼─────┐   ┌───▼────┐   ┌────▼─────┐
    │ FastAPI  │   │  MCP   │   │   CLI    │
    │ (REST)   │   │ Server │   │  (Typer) │
    └──────────┘   └────────┘   └──────────┘

Benefits:
- No code duplication across interfaces
- Single source of truth for business logic
- Easy to add new interfaces (GraphQL, gRPC, etc.)
- Consistent behavior across all entry points
```

**MCP Server Architecture:**
```
┌─────────────┐
│ MCP Client  │ (Claude, etc.)
└──────┬──────┘
       │ HTTP/SSE :8001
┌──────▼──────┐
│ MCP Server  │ ──► lib/youtube (direct use)
└─────────────┘
```

**Previous architecture:** MCP → HTTP → FastAPI → Service  
**New architecture:** MCP → lib/youtube (no HTTP overhead)

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
# Install dependencies (including dev tools)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# Run locally
uvicorn app.main:app --reload

# Run MCP server (requires MCP dependencies)
pip install -r requirements-mcp.txt
uvicorn mcp_server.server:app --port 8001

# Run tests
pytest

# Code quality
black .
ruff check .
mypy .
```

### Dependency Structure

The project uses a modular dependency structure to keep installations minimal:

```
requirements.txt           # Core API dependencies (8 packages)
├── fastapi, uvicorn      # Web framework
├── pydantic              # Data validation
├── sqlalchemy            # Database ORM
├── bcrypt                # Security
└── youtube-transcript-api # Core feature

requirements-cli.txt       # CLI additions (2 packages)
├── typer                 # CLI framework
└── rich                  # Pretty terminal output

requirements-mcp.txt       # MCP server additions (2 packages)
├── mcp                   # MCP protocol
└── httpx                 # HTTP client

requirements-dev.txt       # Development tools (6 packages)
├── pytest, pytest-asyncio, pytest-cov  # Testing
└── black, ruff, mypy                   # Code quality
```

**Benefits:**
- Core API installs only 8 dependencies
- Optional features add minimal overhead
- Docker images stay lean
- Faster CI/CD builds

## Project Structure

```
service-hub/
├── lib/                  # Reusable libraries (NEW)
│   └── youtube/         # YouTube transcript library
│       ├── service.py   # TranscriptService class
│       ├── formatters.py # Format converters
│       ├── models.py    # Pydantic models
│       ├── cache.py     # Cache protocol
│       └── exceptions.py # Custom exceptions
├── app/                  # FastAPI application
│   ├── api/             # API endpoints
│   ├── core/            # Cache, rate limiting, security
│   ├── models/          # Database models
│   └── schemas/         # Pydantic schemas (re-exports)
├── mcp/                 # MCP server
│   ├── server.py        # Main MCP server
│   ├── tools/           # MCP tool implementations
│   ├── prompts/         # MCP prompts
│   └── resources/       # MCP resources
├── cli/                 # Command-line interface (NEW)
│   └── youtube.py       # YouTube CLI commands
├── scripts/             # Management scripts & entry points
│   ├── manage_keys.py   # API key management
│   └── youtube-transcript # CLI entry point
├── tests/               # Test suite
├── docker-compose.yml   # Docker services
└── .env.example         # Configuration template
```

## License

MIT
