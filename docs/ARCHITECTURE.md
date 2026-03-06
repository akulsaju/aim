# AIM v3 Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    AIM v3 Architecture                       │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐     ┌──────────────────┐   ┌────────────┐
│   Web Browser    │     │    CLI Tools     │   │  External  │
│   (Frontend)     │     │  (aim command)   │   │    Apps    │
└────────┬─────────┘     └────────┬─────────┘   └──────┬─────┘
         │                        │                    │
         └────────────┬───────────┴────────────────────┘
                      │
              ┌───────▼────────┐
              │   REST API     │
              │  (Flask/v3)    │
              └───────┬────────┘
                      │
         ┌────────────┼────────────┐
         │            │            │
    ┌────▼────┐  ┌───▼───┐  ┌────▼──────┐
    │ Training │  │ Model  │  │ Generation│
    │ Endpoint │  │ Manager│  │ Endpoint  │
    └────┬────┘  └───┬───┘  └────┬──────┘
         │           │           │
    ┌────▼─────────────┴────────────┴──────┐
    │                                      │
    │      AIM Core System                 │
    │  (aim_core package)                  │
    │                                      │
    │  ┌──────────────────────────────┐   │
    │  │   Model Management            │   │
    │  │  - Manifest                   │   │
    │  │  - AIMModel                   │   │
    │  └──────────────────────────────┘   │
    │                                      │
    │  ┌──────────────────────────────┐   │
    │  │   Engine System               │   │
    │  │  - Markov                     │   │
    │  │  - N-gram                     │   │
    │  │  - Embedding (planned)        │   │
    │  │  - LLM (planned)              │   │
    │  └──────────────────────────────┘   │
    │                                      │
    │  ┌──────────────────────────────┐   │
    │  │   Plugin System               │   │
    │  │  - Plugin Manager             │   │
    │  │  - Plugin Registry            │   │
    │  └──────────────────────────────┘   │
    │                                      │
    └──────────────────────────────────────┘
         │
         └──────────────┬──────────────┐
                        │              │
              ┌─────────▼──┐   ┌──────▼────┐
              │ File System│   │  Registry  │
              │  .aim files│   │  (Hub API) │
              └────────────┘   └───────────┘
```

## Component Architecture

### 1. Frontend Layer
- **Web UI** (HTML/CSS/JavaScript)
- **CLI Tool** (Click-based Python CLI)
- **Client Libraries** (Python, JavaScript, etc.)

### 2. API Layer
- **REST API** (Flask)
- **v0/v1 Endpoints** (Legacy compatibility)
- **v3 Endpoints** (New AIM v3 features)
- **Model Operations** (Train, Generate, Save, Load)
- **Registry Operations** (Search, Install, Publish)
- **Plugin Operations** (List, Execute)

### 3. Core Layer (aim_core)
- **Manifest System**
  - Model metadata format
  - Validation
  - Serialization

- **Model System**
  - AIMModel class
  - Model loading/saving
  - Unified interface

- **Engine System**
  - BaseEngine abstract class
  - Markov implementation
  - N-gram implementation
  - Extensible for future engines

- **Plugin System**
  - BasePlugin abstract class
  - Plugin discovery
  - Plugin execution
  - Hook system

### 4. Hub Layer (aim_hub)
- **Local Registry**
  - Index file (JSON)
  - Model metadata
  - Installation tracking

- **Remote Registry** (aimhub.org)
  - Model search
  - Model download
  - Model upload
  - User authentication

### 5. Storage Layer
- **File System**
  - .aim files (ZIP packages)
  - Manifest files
  - Model weights

- **Plugin Directory**
  - Plugin code
  - Plugin configuration
  - Plugin dependencies

## Data Flow

### Training Workflow
```
User Input (text) → Validation → Engine Training → Model State → Manifest → .aim File
```

### Generation Workflow
```
.aim File → Load → Engine Setup → Prompt Input → Generation → Output
```

### Plugin Workflow
```
Plugin Request → Load Plugin → Validate Config → Execute → Return Result
```

## Key Design Principles

1. **Modularity** - Each component has a single responsibility
2. **Extensibility** - Easy to add engines and plugins
3. **Portability** - Models are self-contained .aim packages
4. **Simplicity** - Hide complexity behind clear APIs
5. **Compatibility** - Support legacy v0/v1 code
6. **Standard Format** - Universal .aim specification

## Engine System

### Base Interface

```python
class BaseEngine(ABC):
    def train(data, **kwargs) -> stats
    def generate(prompt, **kwargs) -> output
    def save(filepath)
    def load(filepath)
```

### Markov Engine

- **Input**: Raw text
- **Processing**: Word tokenization, state building
- **Output**: Probability distributions (transition tables)
- **Storage**: JSON with states and transitions

### N-gram Engine

- **Input**: Raw text
- **Processing**: N-gram extraction, frequency counting
- **Output**: N-gram frequency tables
- **Storage**: JSON with n-grams and counts

### Future Engines

- **Embedding Engine**: Vector-based semantic similarity
- **LLM Engine**: Interface to OpenAI, Hugging Face, local LLMs

## Plugin System

### Discovery & Loading

1. Scan `plugins/` directory
2. Find `plugin.json` manifests
3. Load Python modules
4. Validate configuration
5. Register in manager

### Execution

1. Get plugin by name
2. Validate input
3. Execute plugin.execute()
4. Handle errors
5. Return output

### Hooks System

```python
manager.register_hook('model_trained', callback)
manager.call_hook('model_trained', model)
```

## Security Considerations

1. **Model Validation** - Verify .aim file structure and manifest
2. **Plugin Sandbox** - Isolate plugin execution
3. **File Size Limits** - Prevent DoS via large uploads
4. **API Authentication** - Token-based for hub operations
5. **Input Validation** - Sanitize all user inputs

## Performance Optimization

1. **Lazy Loading** - Load models only when needed
2. **Caching** - Cache model metadata and plugin info
3. **Async Operations** - Long training/generation in background
4. **Streaming** - Stream large file uploads/downloads
5. **Compression** - ZIP compression for .aim files

## Testing Strategy

### Unit Tests
- Component isolation
- Edge cases
- Error handling

### Integration Tests
- Full workflows
- Component interaction
- API endpoints

### Performance Tests
- Large model training
- Generation speed
- Memory usage

## Deployment Architecture

### Development
```
Python virtual env → Flask dev server → Local file system
```

### Production
```
Gunicorn (4+ workers) → Nginx proxy → S3/Cloud storage
```

### Hub Deployment (aimhub.org)
```
Load balancer → API servers (Gunicorn) → Database → CDN
                             ↓
                    Message queue (Celery)
                             ↓
                    Model processing workers
```

## Database Schema (Future)

### Users Table
```sql
users:
  - id (PK)
  - username
  - email
  - api_token
  - created_at
```

### Models Table
```sql
models:
  - id (PK)
  - name
  - author_id (FK)
  - version
  - description
  - engine
  - downloads
  - rating
  - created_at
  - updated_at
```

### Ratings Table
```sql
ratings:
  - id (PK)
  - model_id (FK)
  - user_id (FK)
  - rating
  - review
  - created_at
```

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, JavaScript, Fetch API |
| CLI | Python Click |
| Backend | Flask, Gunicorn |
| Core | Python 3.8+ |
| Database | PostgreSQL (future) |
| Storage | S3 or local filesystem |
| Cache | Redis (future) |
| Queue | Celery (future) |
| Deploy | Docker, Kubernetes (future) |

---

**Last Updated:** March 2026
