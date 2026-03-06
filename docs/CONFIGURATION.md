# AIM Configuration Guide

## Application Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5000
FLASK_HOST=0.0.0.0

# Model Storage
MODELS_DIR=./models
UPLOADS_DIR=./backend/uploads

# Registry Configuration
REGISTRY_DIR=~/.aim/registry
HUB_URL=https://aimhub.org

# Plugin Configuration
PLUGINS_DIR=./plugins
ENABLE_PLUGINS=True

# Database (future use)
DATABASE_URL=sqlite:///aim.db

# API Keys (for LLM engines, image generation, etc.)
OPENAI_API_KEY=
HUGGINGFACE_API_KEY=
```

### Flask App Configuration

In `backend/config.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', True)
    
    # Models
    MODELS_DIR = os.getenv('MODELS_DIR', './models')
    UPLOADS_DIR = os.getenv('UPLOADS_DIR', './backend/uploads')
    
    # Registry
    HUB_URL = os.getenv('HUB_URL', 'https://aimhub.org')
    
    # Plugins
    PLUGINS_DIR = os.getenv('PLUGINS_DIR', './plugins')
    ENABLE_PLUGINS = os.getenv('ENABLE_PLUGINS', 'True') == 'True'
    
    # API
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file upload


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    MODELS_DIR = './test_models'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    # Add production-specific settings
```

## Model Configuration

### Training Configuration

```json
{
  "engine": "markov",
  "engine_config": {
    "order": 2,
    "min_word_frequency": 1,
    "max_vocabulary_size": 10000
  },
  "preprocessing": {
    "lowercase": true,
    "remove_punctuation": false,
    "remove_stopwords": false,
    "lemmatize": false
  },
  "generation": {
    "temperature": 1.0,
    "top_k": 50,
    "top_p": 0.95
  }
}
```

### Generation Parameters

```json
{
  "prompt": "optional starting text",
  "max_length": 100,
  "temperature": 1.0,
  "top_k": null,
  "top_p": 1.0,
  "num_beams": 1,
  "repetition_penalty": 1.0,
  "length_penalty": 1.0
}
```

## Plugin Configuration

### Plugin Settings

Plugins can be configured in `aim.json`:

```json
{
  "plugins": {
    "pdf_reader": {
      "enabled": true,
      "config": {
        "extract_images": false,
        "preserve_formatting": true
      }
    },
    "web_scraper": {
      "enabled": true,
      "config": {
        "timeout": 30,
        "max_pages": 10,
        "follow_links": true
      }
    }
  }
}
```

## Server Configuration

### Development Server

```bash
cd backend
python app.py
```

### Production Server (Gunicorn)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 -t 120 app:app
```

### Nginx Configuration

```nginx
upstream aim {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
}

server {
    listen 80;
    server_name aimhub.org;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://aim;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /var/www/aim/frontend/;
    }
}
```

## Database Configuration (Future)

When database support is added:

```python
# PostgreSQL
DATABASE_URL=postgresql://user:pass@localhost:5432/aim

# MySQL
DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/aim

# SQLite
DATABASE_URL=sqlite:///aim.db
```

## Security Configuration

### API Key Management

```python
# For secret keys and API tokens
import secrets
from pathlib import Path

# Generate secret key for Flask
SECRET_KEY = secrets.token_hex(32)

# Store sensitive data
API_TOKENS = {
    'user_id': 'token_hash'
}
```

### CORS Configuration

```python
from flask_cors import CORS

# Allow specific origins
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://aimhub.org", "http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

## Logging Configuration

```python
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('aim.log', maxBytes=10485760, backupCount=10),
        logging.StreamHandler()
    ]
)
```

## Resource Limits

### Model Size Limits

- Markov models: Up to 50MB
- N-gram models: Up to 100MB
- Embedding models: Up to 500MB
- LLM models: No hard limit

### Request Limits

```python
MAX_REQUEST_SIZE = 100 * 1024 * 1024  # 100MB
MAX_TRAINING_TIME = 600  # 10 minutes
MAX_GENERATION_LENGTH = 10000  # tokens
```

## Testing Configuration

```python
import os
import tempfile

class TestConfig:
    TESTING = True
    MODELS_DIR = tempfile.mkdtemp()
    DATABASE_URL = "sqlite:///:memory:"
    SECRET_KEY = "test-key"
```

## Performance Tuning

### Caching

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/models')
@cache.cached(timeout=300)
def get_models():
    return models
```

### Async Processing

For long-running operations:

```python
from celery import Celery

celery = Celery(app.name)

@celery.task
def train_model_async(data):
    return model.train(data)

# Call async
task = train_model_async.delay(training_data)
result = task.get(timeout=600)
```

---

For more configuration options, see the source code and documentation.
