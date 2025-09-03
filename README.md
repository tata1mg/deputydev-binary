# DeputyDev Binary

DeputyDev Binary is a high-performance Sanic-based web service that provides advanced code analysis, search, and management capabilities. It serves as an installable binary for running DeputyDev algorithms with support for codebase exploration, diff application, URL content processing, and Model Context Protocol (MCP) integration.

## Overview

This service offers a comprehensive suite of APIs for:
- **Code Search & Analysis**: Advanced fuzzy search, grep-based content search, and focused code snippet retrieval
- **Diff Management**: Apply and manage code diffs with validation
- **URL Processing**: Fetch, parse, and analyze web content including HTML scraping
- **Codebase Reading**: Navigate and read project files and structures
- **Chunk Processing**: Handle large codebases through intelligent chunking
- **Authentication**: Secure token-based authentication system
- **MCP Integration**: Model Context Protocol support for AI-assisted development

## Project Architecture

The project follows a clean, modular architecture with clear separation of concerns:

```
deputydev-binary/
├── app/
│   ├── clients/                    # External service integrations
│   │   ├── one_dev_client.py      # OneDev platform client
│   │   └── web_client.py          # Generic web client
│   ├── dataclasses/               # Data transfer objects
│   │   ├── diff_applicator/       # Diff application DTOs
│   │   └── codebase_search/       # Search-related DTOs
│   ├── models/                    # Data models and DTOs
│   │   ├── dtos/                  # Request/response models
│   │   │   ├── url_dtos/          # URL processing models
│   │   │   └── collection_dtos/   # Collection data models
│   ├── repository/                # Data access layer
│   │   └── urls_content_repository.py
│   ├── routes/                    # API endpoint definitions
│   │   ├── auth_token.py          # Authentication endpoints
│   │   ├── chunks.py              # Chunk processing APIs
│   │   ├── codebase_read.py       # File reading APIs
│   │   ├── diff_applicator.py     # Diff application APIs
│   │   ├── initialization.py      # Service initialization
│   │   ├── mcp.py                 # Model Context Protocol
│   │   ├── ping.py                # Health check
│   │   ├── search.py              # Search functionality
│   │   ├── shutdown.py            # Graceful shutdown
│   │   └── url.py                 # URL processing APIs
│   ├── services/                  # Business logic layer
│   │   ├── codebase_search/       # Search implementations
│   │   ├── url_service/           # URL processing services
│   │   ├── batch_chunk_search_service.py
│   │   ├── diff_applicator_service.py
│   │   ├── file_cache_service.py
│   │   ├── initialization_service.py
│   │   ├── mcp_service.py
│   │   ├── reranker_service.py
│   │   └── relevant_chunk_service.py
│   ├── utils/                     # Shared utilities
│   │   ├── constant/              # Application constants
│   │   ├── constants.py           # Core constants
│   │   ├── error_handler.py       # Error handling
│   │   ├── request_handlers.py    # Request processing
│   │   ├── response_headers_handler.py
│   │   └── util.py                # General utilities
│   ├── listeners.py               # Application lifecycle events
│   ├── logging_config.py          # Logging configuration
│   └── service.py                 # Main application entry point
├── service.bin                    # Compiled binary (Nuitka)
├── service.build/                 # Build artifacts
├── service.dist/                  # Distribution files
├── service.onefile-build/         # One-file build artifacts
├── .gitignore
├── pyproject.toml                 # Project configuration
├── README.md
└── uv.lock                        # Dependency lock file
```

## Key Features

### 🔍 **Advanced Search Capabilities**
- **Focus Search**: Targeted search for specific code elements (classes, functions, files)
- **File Path Search**: Fuzzy search through project file structures
- **Grep Search**: Pattern-based content search across codebases
- **Batch Processing**: Handle large-scale search operations efficiently

### 🔧 **Diff Management**
- **Unified Diff Application**: Apply code changes with validation
- **Multi-file Support**: Handle complex changesets across multiple files
- **Error Handling**: Robust error reporting for failed applications

### 🌐 **URL & Content Processing**
- **Web Scraping**: Extract and process HTML content
- **Content Serialization**: Convert web content to structured formats
- **URL Management**: Save, update, and search URL-based content

### 🚀 **Performance & Scalability**
- **Async Architecture**: Built on Sanic for high-performance async processing
- **Chunking System**: Intelligent code chunking for large repositories
- **Caching**: File-based caching for improved response times
- **Binary Compilation**: Nuitka-compiled binary for optimal performance

### 🔒 **Security & Authentication**
- **Token-based Auth**: Secure API access with configurable authentication
- **Request Validation**: Comprehensive input validation and sanitization
- **Error Isolation**: Secure error handling without information leakage

## Installation & Setup

### Prerequisites
- Python >= 3.11, < 3.12
- uv (recommended): https://docs.astral.sh/uv/
- Git

### Local setup (uv)

1) Create and activate a virtual environment
   - uv venv
   - source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
2) Install dependencies (including dev tools)
   - uv sync --group dev
3) Install git hooks
   - pre-commit install
4) Run formatters/linters locally
   - ruff format .
   - ruff check .

Alternative (pip) setup:
- python -m venv .venv && source .venv/bin/activate
- pip install -e .
- pip install "pre-commit>=4.2.0" "ruff==0.12.0"
- pre-commit install

### Production Deployment

#### Using Pre-compiled Binary
```bash
# Run the compiled binary directly
./service.bin [port]
# Default port: 8001
```

#### Using Python Runtime
```bash
# Run via Python module
python -m app.service [port]
```

#### Using UV
```bash
# Run with UV in production mode
uv run python -m app.service [port]
```

## API Endpoints

### Core Services

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ping` | GET | Health check endpoint |
| `/v1/initialization` | POST | Initialize service components |
| `/v1/shutdown` | POST | Graceful service shutdown |

### Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/auth-token` | POST | Token validation and management |

### Code Search & Analysis
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/get-focus-search-results` | POST | Search for specific code elements |
| `/v1/file-path-search` | POST | Search through file paths |
| `/v1/grep-search` | POST | Pattern-based content search |
| `/v1/chunks` | POST | Process and search code chunks |

### Code Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/codebase-read` | POST | Read and navigate codebase files |
| `/v1/diff-applicator/apply-diff` | POST | Apply unified diffs to files |

### Content Processing
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/url-reader` | POST | Fetch and process URL content |
| `/v1/urls` | GET/POST/PUT | Manage URL collections |

### Integration
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/mcp` | WebSocket | Model Context Protocol interface |

## Configuration

### Environment Variables
```bash
# SSL Certificate location (automatically configured)
SSL_CERT_FILE=/path/to/certificates

# Optional: Custom port (default: 8001)
PORT=8001
```

### Configuration File
Create `binary_config.json` in the project root:
```json
{
  "weaviate": {
    "url": "your-weaviate-instance",
    "api_key": "your-api-key"
  },
  "authentication": {
    "enabled": true,
    "token_validation_url": "your-auth-endpoint"
  },
  "logging": {
    "level": "INFO",
    "format": "json"
  }
}
```

## Build & Distribution

### Development Build
```bash
# Install build dependencies
uv sync --group dev

# Format code
uv run ruff format .

# Lint code
uv run ruff check .
```

### Binary Compilation
```bash
# Install Nuitka (optional dependency)
uv sync --extra binarization

# Compile to binary
nuitka --onefile --output-filename=service.bin app/service.py
```

The binary compilation creates:
- `service.bin` - Standalone executable
- `service.build/` - Build artifacts
- `service.dist/` - Distribution files
- `service.onefile-build/` - One-file build cache

## Dependencies

### Core Dependencies
- **Sanic 22.12.0** - Async web framework
- **WebSockets 14.0** - WebSocket support for MCP
- **FuzzyWuzzy 0.18.0** - Fuzzy string matching
- **Beautiful Soup 4** - HTML parsing
- **html2text** - HTML to text conversion
- **deputydev-core** - Core DeputyDev algorithms

### Development Dependencies
- **Ruff** - Fast Python linter and formatter
- **Nuitka** - Python compiler for binary generation

## Performance Considerations

### Server Configuration
- **Request Timeout**: 3000 seconds (configurable for long-running operations)
- **Response Timeout**: 3000 seconds
- **Keep-Alive Timeout**: 3000 seconds
- **WebSocket Max Size**: 10MB
- **Default Port**: 8001

### Optimization Features
- Async request handling for concurrent operations
- File caching for frequently accessed content
- Chunked processing for large codebases
- Connection pooling for external services
- Graceful shutdown with resource cleanup

## Monitoring & Logging

The service includes comprehensive logging and monitoring:
- Structured JSON logging
- Request/response tracking
- Error reporting with stack traces
- Performance metrics collection
- Health check endpoints

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Use a different port
   python -m app.service 8002
   ```

2. **SSL Certificate errors**
   ```bash
   # Certificates are auto-configured via certifi
   # Check SSL_CERT_FILE environment variable
   ```

3. **Binary execution issues**
   ```bash
   # Ensure binary has execute permissions
   chmod +x service.bin
   ```

4. **Memory issues with large codebases**
   - Increase system memory allocation
   - Use chunked processing endpoints
   - Configure appropriate timeout values

## Contributing

1. Follow the existing code structure and patterns
2. Use Ruff for code formatting: `uv run ruff format .`
3. Run linting: `uv run ruff check .`
4. Test API endpoints thoroughly
5. Update documentation for new features

## Version Information

- **Python Requirement**: >=3.11,<3.12
