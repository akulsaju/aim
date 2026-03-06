# AIM File Format Specification

## Overview

The `.aim` file is the standard format for packaging AI models in the AIM ecosystem. It's a ZIP archive containing model data and metadata.

---

## File Structure

```
model.aim
├── aim.json              (Required) Manifest with metadata and configuration
├── model.json            (Required) Engine-specific model data
└── [additional files]    (Optional) Supporting files
```

---

## Manifest Format (aim.json)

The manifest is a JSON file containing model metadata and configuration.

### Required Fields

```json
{
  "name": "String",                    // Model name (unique identifier)
  "version": "String",                 // Semantic version (e.g., "1.0.0")
  "author": "String",                  // Author name
  "description": "String",             // Human-readable description
  "type": "String",                    // Model type: "text", "image", "audio", etc.
  "engine": "String",                  // Engine: "markov", "ngram", "embedding", "llm"
  "files": {                           // File mappings
    "model": "model.json",             // (Required) Model file path
    "metadata": "info.json"            // (Optional) Additional metadata
  }
}
```

### Optional Fields

```json
{
  "version": "1.0.0",
  "created": "2026-03-06T10:30:00Z",   // ISO 8601 timestamp
  "updated": "2026-03-06T15:45:00Z",
  "license": "MIT",                    // License type
  "tags": ["biology", "education"],    // Searchable tags
  "author": "John Doe",
  "source": "https://...",             // Original data source
  "homepage": "https://...",           // Project URL
  "repository": "https://...",         // Repository URL
  "dependencies": {                    // Required packages
    "transformers": ">=4.0.0"
  },
  "metadata": {                        // Custom metadata
    "training_samples": 10000,
    "vocabulary_size": 5432,
    "training_duration_minutes": 120,
    "accuracy": 0.95
  },
  "engine_config": {                   // Engine-specific configuration
    "order": 2,                        // For Markov engine
    "ngram_size": 3,                   // For n-gram engine
    "embedding_dim": 768               // For embedding engine
  }
}
```

---

## Complete Example

```json
{
  "name": "biology-tutor",
  "version": "2.1.0",
  "author": "Akul Desai",
  "description": "AI tutor trained on comprehensive biology textbooks and educational materials. Answers biology questions and provides explanations.",
  "type": "text",
  "engine": "markov",
  "created": "2026-03-06T10:30:00Z",
  "updated": "2026-03-06T15:45:00Z",
  "license": "CC-BY-4.0",
  "tags": ["biology", "education", "tutor", "q&a"],
  "source": "Khan Academy, Wikipedia, textbooks",
  "homepage": "https://example.com/biology-tutor",
  "repository": "https://github.com/user/biology-tutor",
  
  "files": {
    "model": "model.json",
    "metadata": "training.json",
    "readme": "README.md"
  },
  
  "dependencies": {
    "python": ">=3.8"
  },
  
  "metadata": {
    "training_samples": 50000,
    "vocabulary_size": 8932,
    "training_duration_minutes": 240,
    "avg_response_quality": 0.92,
    "data_sources": [
      "Khan Academy",
      "Wikipedia Biology Articles",
      "Textbooks"
    ]
  },
  
  "engine_config": {
    "order": 3,
    "temperature": 1.0
  }
}
```

---

## Engine-Specific Model Data

Each engine stores its trained model in `model.json`. Format varies by engine.

### Markov Engine Model Format

```json
{
  "engine": "markov",
  "order": 2,
  "vocabulary_size": 5432,
  "transitions": {
    "the quick": ["brown", "red", "happy"],
    "quick fox": ["jumps", "walks"],
    "fox jumps": ["over", "away"]
  },
  "start_words": [
    ["once", "upon"],
    ["the", "sky"],
    ["in", "the"]
  ]
}
```

### N-gram Engine Model Format

```json
{
  "engine": "ngram",
  "ngram_size": 3,
  "vocabulary_size": 5432,
  "ngrams": {
    "the quick brown": 125,
    "quick brown fox": 98,
    "brown fox jumps": 87
  }
}
```

### Embedding Engine Model Format

```json
{
  "engine": "embedding",
  "embedding_dim": 768,
  "encoder": "sentence-transformers/all-MiniLM-L6-v2",
  "vocabulary": ["word1", "word2", ...],
  "embeddings": [
    [0.1, 0.2, ..., 0.5],
    [0.2, 0.3, ..., 0.6],
    ...
  ]
}
```

---

## Loading and Creating .AIM Files

### Python

```python
from aim_core import AIMModel, create_manifest

# Create manifest
manifest = create_manifest(
    name="My Model",
    author="John Doe",
    engine="markov",
    description="My awesome model"
)

# Create model
model = AIMModel.create(
    name="My Model",
    author="John Doe",
    engine="markov"
)

# Train
model.train(training_data)

# Save as .aim
model.save("mymodel.aim")

# Load .aim file
model = AIMModel.load("mymodel.aim")
```

### CLI

```bash
# Create and train
aim train data.txt --name "My Model" --author "John Doe"

# Load and use
aim run mymodel.aim --prompt "text"

# Get info
aim info mymodel.aim
```

---

## Manifest Validation

When loading a `.aim` file, the system validates:

1. **Required fields present**: name, version, author, description, type, engine, files
2. **Valid type**: must be one of [text, image, audio, embedding, classification]
3. **Valid engine**: must be registered in ENGINE_REGISTRY
4. **Files exist**: all files listed in "files" must be present in ZIP
5. **Version format**: must be semantic versioning (x.y.z)

---

## File Size Guidelines

| Engine | Typical Size | Max Recommended |
|--------|--------------|-----------------|
| Markov | 100KB - 1MB | 10MB |
| N-gram | 500KB - 5MB | 50MB |
| Embedding | 10MB - 100MB | 500MB |
| LLM | 1GB - 175GB | N/A |

---

## Sharing and Distribution

### On AIM Hub

```bash
aim publish mymodel.aim --token YOUR_TOKEN
```

This uploads your .aim file to aimhub.org and makes it discoverable.

### Direct Sharing

Share the `.aim` file directly (email, GitHub, etc.). Recipients can:

```bash
aim install ./mymodel.aim
# or
aim run mymodel.aim
```

### In Code

```python
# Download and use
import requests
response = requests.get("https://example.com/mymodel.aim")
with open("mymodel.aim", "wb") as f:
    f.write(response.content)

model = AIMModel.load("mymodel.aim")
output = model.generate("prompt")
```

---

## Security Considerations

1. **Model Integrity**: For sensitive models, consider signing the ZIP file
2. **Data Privacy**: Models trained on private data should be kept local
3. **License**: Always respect model licenses when redistributing
4. **Dependencies**: Check if model requires external packages

---

## Extending the Format

The format is extensible. You can add:

1. **Custom metadata** in the `metadata` object
2. **Additional files** (docs, examples, test data)
3. **Engine-specific configurations** in `engine_config`
4. **Custom handlers** via plugins

---

## Version History

### v1.0 (Initial)
- Basic manifest format
- Markov engine support
- Local file storage

### v3.0 (Current)
- Multiple engines (markov, ngram, embedding, llm)
- Plugin system
- Registry/hub support
- Enhanced metadata
- Optional fields for flexibility

---

## Examples

See [AIM_V3_GUIDE.md](AIM_V3_GUIDE.md) for more examples and use cases.
