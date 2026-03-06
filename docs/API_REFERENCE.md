# AIM REST API Reference

## Base URL

```
http://localhost:5000
```

---

## Authentication

Currently no authentication required. For production hub deployment, API tokens would be used:

```
Authorization: Bearer YOUR_API_TOKEN
```

---

## Legacy API (v0/v1)

### Training

**Endpoint:** `POST /api/train`

Train a Markov chain model.

**Request:**
```json
{
  "text": "Training text data...",
  "order": 2
}
```

**Response:**
```json
{
  "success": true,
  "message": "Model trained successfully",
  "stats": {
    "order": 2,
    "vocabulary_size": 5432,
    "transitions_count": 1280
  }
}
```

### Text Generation

**Endpoint:** `POST /api/generate`

Generate text using trained model.

**Request:**
```json
{
  "prompt": "Once upon a",
  "max_length": 100,
  "temperature": 1.0
}
```

**Response:**
```json
{
  "success": true,
  "text": "Once upon a time there was a kingdom...",
  "prompt": "Once upon a",
  "length": 95
}
```

### Export Model

**Endpoint:** `POST /api/export`

Export current model as .aim file.

**Request:**
```json
{
  "model_name": "My Story Generator",
  "author": "John Doe",
  "version": "1.0"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Model exported successfully",
  "filename": "my_story_generator.aim",
  "path": "/path/to/models/my_story_generator.aim"
}
```

### Load Model

**Endpoint:** `POST /api/load_model`

Load a .aim file.

**Request (JSON):**
```json
{
  "aim_data": {
    "model_name": "My Model",
    "author": "John",
    "version": "1.0",
    "algorithm": "Markov Chain (order 2)",
    "model_data": { ... }
  }
}
```

**Request (Form Data):**
File upload with multipart/form-data

**Response:**
```json
{
  "success": true,
  "message": "Model loaded successfully",
  "model_info": {
    "name": "My Model",
    "author": "John",
    "version": "1.0",
    "algorithm": "Markov Chain (order 2)"
  }
}
```

### List Models

**Endpoint:** `GET /api/models`

List all available .aim files.

**Response:**
```json
{
  "success": true,
  "models": [
    {
      "filename": "story_generator.aim",
      "model_name": "Story Generator",
      "author": "John",
      "version": "1.0",
      "algorithm": "Markov Chain (order 2)",
      "created_at": "2026-03-06T10:30:00"
    }
  ]
}
```

### Get Status

**Endpoint:** `GET /api/status`

Get current model status.

**Response:**
```json
{
  "model_loaded": true,
  "order": 2,
  "vocabulary_size": 5432,
  "transitions_count": 1280
}
```

### Download Model

**Endpoint:** `GET /api/model/<filename>`

Download a specific .aim file.

**Example:**
```
GET /api/model/story_generator.aim
```

---

## AIM v3 API

### Get Available Engines

**Endpoint:** `GET /api/v3/engines`

List all AI engines available.

**Response:**
```json
{
  "success": true,
  "engines": ["markov", "ngram", "embedding", "llm"],
  "descriptions": {
    "markov": "Statistical text generation using Markov chains",
    "ngram": "N-gram language model for text prediction",
    "embedding": "Vector embedding-based similarity",
    "llm": "Large Language Model interface"
  }
}
```

### Train Model (v3)

**Endpoint:** `POST /api/v3/train`

Train a model using AIM v3 system.

**Request:**
```json
{
  "name": "Biology Tutor",
  "author": "Akul",
  "type": "text",
  "engine": "markov",
  "description": "AI trained on biology textbooks",
  "text": "Training text data...",
  "engine_config": {
    "order": 2
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Model trained successfully",
  "model": "AIMModel(Biology Tutor v1.0.0 by Akul)",
  "stats": {
    "order": 2,
    "vocabulary_size": 8932,
    "transitions_count": 2150
  }
}
```

### Generate Text (v3)

**Endpoint:** `POST /api/v3/generate`

Generate output using trained model.

**Request:**
```json
{
  "prompt": "The human body is",
  "max_length": 150,
  "temperature": 0.8
}
```

**Response:**
```json
{
  "success": true,
  "output": "The human body is a complex system of interconnected organs, tissues, and cells..."
}
```

### Save Model (v3)

**Endpoint:** `POST /api/v3/save`

Save current model as .aim package.

**Request:**
```json
{
  "filename": "biology_tutor.aim"
}
```

**Response:**
```json
{
  "success": true,
  "path": "/path/to/models/biology_tutor.aim",
  "size_kb": 245.5
}
```

### Load Model (v3)

**Endpoint:** `POST /api/v3/load`

Load a .aim package file.

**Request (Multipart/Form-Data):**
```
file=<binary .aim file>
```

**Request (JSON):**
```json
{
  "path": "/path/to/model.aim"
}
```

**Response:**
```json
{
  "success": true,
  "model": "AIMModel(Biology Tutor v2.1.0 by Akul)",
  "info": {
    "manifest": {
      "name": "Biology Tutor",
      "version": "2.1.0",
      "author": "Akul",
      ...
    },
    "engine": "MarkovEngine"
  }
}
```

### List Local Registry

**Endpoint:** `GET /api/v3/registry/list`

List models in local registry.

**Response:**
```json
{
  "success": true,
  "models": [
    {
      "name": "biology-tutor",
      "path": "/path/to/biology_tutor.aim",
      "registered": "2026-03-06T10:30:00"
    }
  ]
}
```

### Search Registry

**Endpoint:** `GET /api/v3/registry/search`

Search AIM Hub registry.

**Query Parameters:**
- `q=<query>` - Search query
- `tags=<tag1,tag2>` - Filter by tags
- `limit=<number>` - Max results (default: 10)

**Example:**
```
GET /api/v3/registry/search?q=biology&tags=education,tutorial&limit=20
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "name": "biology-tutor",
      "author": "Akul",
      "description": "AI tutor trained on biology textbooks",
      "download_url": "...",
      "downloads": 1250,
      "rating": 4.8,
      "tags": ["biology", "education", "tutor"]
    }
  ]
}
```

### List Plugins

**Endpoint:** `GET /api/v3/plugins`

List all available plugins.

**Response:**
```json
{
  "success": true,
  "plugins": [
    {
      "name": "pdf_reader",
      "version": "1.0.0",
      "description": "Extract text from PDF files",
      "author": "AIM Team"
    },
    {
      "name": "web_scraper",
      "version": "1.0.0",
      "description": "Scrape text from web pages",
      "author": "AIM Team"
    }
  ]
}
```

### Execute Plugin

**Endpoint:** `POST /api/v3/plugins/<name>/execute`

Execute a plugin with input data.

**Request:**
```json
{
  "input": "/path/to/file.pdf",
  "args": {
    "option1": "value1"
  }
}
```

**Response:**
```json
{
  "success": true,
  "result": "Extracted text from PDF..."
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (missing/invalid parameters) |
| 404 | Not found (model/file not found) |
| 500 | Server error (unexpected error) |

### Common Errors

**No model trained/loaded:**
```json
{
  "error": "No model loaded. Please train or load a model first."
}
```

**Invalid JSON:**
```json
{
  "error": "Invalid JSON format"
}
```

**File not found:**
```json
{
  "error": "File not found: model.aim"
}
```

---

## Rate Limiting

Currently unlimited. Future versions may implement rate limiting for hub deployment.

---

## CORS

CORS is enabled for all endpoints. You can make requests from any domain.

---

## Examples

### Train and Generate (Legacy)

```bash
# Train
curl -X POST http://localhost:5000/api/train \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Once upon a time...",
    "order": 2
  }'

# Generate
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Once upon",
    "max_length": 50
  }'
```

### Train and Save (v3)

```bash
# Train
curl -X POST http://localhost:5000/api/v3/train \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Model",
    "author": "John",
    "engine": "markov",
    "text": "Training data...",
    "engine_config": {"order": 3}
  }'

# Save
curl -X POST http://localhost:5000/api/v3/save \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "mymodel.aim"
  }'
```

### Load and Generate (v3)

```bash
# Load
curl -X POST http://localhost:5000/api/v3/load \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/path/to/model.aim"
  }'

# Generate
curl -X POST http://localhost:5000/api/v3/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "text",
    "max_length": 100
  }'
```

### Search and Execute Plugin

```bash
# Search registry
curl "http://localhost:5000/api/v3/registry/search?q=biology"

# Execute plugin
curl -X POST http://localhost:5000/api/v3/plugins/pdf_reader/execute \
  -H "Content-Type: application/json" \
  -d '{
    "input": "/path/to/document.pdf"
  }'
```

---

## Support

For issues or questions:
- GitHub: https://github.com/aimhub/aim
- Email: support@aimhub.org
