# AIM v3 - Open AI Model Ecosystem

## 🎯 Vision

**AIM** (AI Model Ecosystem) makes it easy to:
- **Create** AI models from simple data
- **Export** them as portable `.aim` packages
- **Share** them with others
- **Install** them like apps
- **Run** them locally or online

AIM combines ideas from npm, Docker, and PyTorch into a simplified package for AI models.

---

## 📦 What's New in v3

### Universal Model Format
Every model is a `.aim` file - a standard package containing:
- Model metadata (name, version, author)
- AI engine configuration
- Trained weights/data
- Supporting files

Example packages:
- `biology_teacher.aim` - biology question answering
- `wikipedia_chat.aim` - conversational Wikipedia search
- `coding_assistant.aim` - code generation and completion

### 🔧 Multiple AI Engines

Choose the right engine for your task:

| Engine | Use Case | Status |
|--------|----------|--------|
| **markov** | Statistical text generation | ✅ Ready |
| **ngram** | Language models | ✅ Ready |
| **embedding** | Semantic similarity | 📋 Planned |
| **llm** | Large language models | 📋 Planned |

### 📥 Package Manager (CLI)

Install and manage models like npm packages:

```bash
# Train a new model
aim train data.txt --name "my-model" --engine markov

# Run a model
aim run mymodel.aim --prompt "Once upon a time"

# Install from hub
aim install wikipedia-ai

# Publish to registry
aim publish mymodel.aim
```

### 🌐 AIM Hub

Central registry for discovering and sharing models (aimhub.org):
- ⭐ Browse thousands of models
- 👥 See authors and training data
- 📊 View usage statistics
- 🔗 One-click installation

### 🔌 Plugin System

Extend AIM with custom functionality:

```python
from aim_core.plugins import BasePlugin

class CustomPlugin(BasePlugin):
    def execute(self, input_data, **kwargs):
        return process(input_data)
```

Built-in plugins:
- **pdf_reader** - Extract text from PDFs
- **web_scraper** - Scrape web pages
- **image_generator** - Generate images from text

### 💾 Dataset Support

Train from multiple file formats:
- `.txt` - Plain text
- `.md` - Markdown files
- `.csv` - Structured data
- `.json` - JSON objects
- `.pdf` - PDF documents (with plugin)

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/user/aim
cd aim

# Install dependencies
pip install -r requirements.txt

# Install CLI tool
pip install -e aim_cli/
```

### Train Your First Model

```bash
# 1. Create training data
echo "Your training text..." > data.txt

# 2. Train a model
aim train data.txt --name my-model --author "Your Name"

# 3. Run the model
aim run my-model.aim --prompt "Start text"
```

### Use via Python API

```python
from aim_core import AIMModel

# Create and train
model = AIMModel.create(name="MyModel", author="You", engine="markov")
model.train(text_data)

# Generate
output = model.generate(prompt="Once ", max_length=100)
print(output)

# Save
model.save("mymodel.aim")

# Load
model = AIMModel.load("mymodel.aim")
```

### Web Interface

```bash
# Start the Flask server
cd backend
python app.py

# Visit http://localhost:5000
```

---

## 🏗️ Project Structure

```
aim/
├── aim_core/                 # Core AIM system
│   ├── manifest.py          # Model metadata format
│   ├── model.py             # AIM model class
│   ├── engines.py           # AI engines (markov, ngram, etc.)
│   └── plugins.py           # Plugin system
│
├── aim_cli/                  # Command-line interface
│   ├── aim.py               # CLI commands
│   └── trainer.py           # Dataset loading
│
├── aim_hub/                  # Registry and package management
│   └── registry.py          # Local & remote registries
│
├── plugins/                  # Extensible plugins
│   ├── pdf_reader/
│   ├── web_scraper/
│   └── image_generator/
│
├── backend/                  # Flask REST API
│   ├── app.py               # Flask application
│   ├── trainer.py           # Legacy trainer (backward compat)
│   └── generator.py         # Legacy generator
│
├── frontend/                 # Web UI
│   ├── index.html
│   ├── app.js
│   └── style.css
│
├── models/                   # Saved .aim files
│   └── fantasy_story_generator.aim
│
└── docs/                     # Documentation
    ├── AIM_FORMAT.md
    ├── API_REFERENCE.md
    └── PLUGIN_DEVELOPMENT.md
```

---

## 📚 Key Concepts

### .AIM File Format

A `.aim` file is a ZIP package containing:

```
mymodel.aim
├── aim.json               # Manifest (metadata & config)
└── model.json             # Engine-specific model data
```

**Example manifest (aim.json):**

```json
{
  "name": "Biology Tutor",
  "version": "2.0",
  "author": "Akul",
  "description": "AI trained on biology textbooks",
  "type": "text",
  "engine": "markov",
  "created": "2026-03-06T10:30:00",
  "license": "MIT",
  "tags": ["biology", "education", "tutor"],
  "files": {
    "model": "model.json",
    "metadata": "info.json"
  },
  "metadata": {
    "training_samples": 10000,
    "vocabulary_size": 5432
  }
}
```

### Engines

Each engine implements the same interface:

```python
class Engine:
    def train(data, **kwargs) -> stats
    def generate(prompt, **kwargs) -> output
    def save(filepath)
    def load(filepath)
```

**Markov Engine Example:**
```python
engine = get_engine("markov", config={"order": 2})
stats = engine.train(text_data)
output = engine.generate(prompt="Once ", max_length=100)
engine.save("model.json")
```

### Plugin Architecture

Plugins extend AIM functionality:

```python
from aim_core.plugins import BasePlugin

class MyPlugin(BasePlugin):
    name = "my_plugin"
    version = "1.0.0"
    
    def execute(self, input_data, **kwargs):
        return process(input_data)
```

---

## 🔌 API Reference

### CLI Commands

```bash
aim train <file>                 # Train a model
aim run <model.aim>              # Run a model
aim info <model.aim>             # Show model info
aim install <model-name>         # Install from hub
aim publish <model.aim>          # Publish to hub
aim search --query "text"        # Search hub
aim list-engines                 # List available engines
```

### Python API

```python
from aim_core import AIMModel, create_manifest

# Create model
model = AIMModel.create(
    name="MyModel",
    author="Author",
    engine="markov",
    description="My awesome model",
    model_type="text"
)

# Train
stats = model.train(training_data, order=2)

# Generate
output = model.generate(prompt="text", max_length=100)

# Save & Load
model.save("mymodel.aim")
model = AIMModel.load("mymodel.aim")

# Get info
print(model.info())
```

### REST API (Flask)

```
GET    /api/v3/engines                 # List engines
POST   /api/v3/train                   # Train model
POST   /api/v3/generate                # Generate output
POST   /api/v3/save                    # Save model
POST   /api/v3/load                    # Load model
GET    /api/v3/registry/list           # List local models
GET    /api/v3/registry/search         # Search hub
GET    /api/v3/plugins                 # List plugins
POST   /api/v3/plugins/<name>/execute  # Run plugin
```

---

## 🛠️ Development

### Install for Development

```bash
git clone https://github.com/user/aim
cd aim
pip install -r requirements.txt
pip install -e .
```

### Run Tests

```bash
pytest tests/
```

### Build Documentation

```bash
cd docs
make html
```

---

## 🤝 Contributing

We welcome contributions! Areas to contribute:

1. **New Engines** - Implement embedding, LLM, or custom engines
2. **Plugins** - Create pdf_reader, web_scraper, or voice AI plugins
3. **Documentation** - Improve guides and examples
4. **Testing** - Add test coverage
5. **UI/UX** - Improve web interface

### Adding a New Engine

```python
# aim_core/engines.py

class MyEngine(BaseEngine):
    def train(self, data, **kwargs):
        # training logic
        return stats
    
    def generate(self, prompt, **kwargs):
        # generation logic
        return output
    
    def save(self, filepath):
        # save to file
        pass
    
    def load(self, filepath):
        # load from file
        pass

# Register engine
register_engine("myengine", MyEngine)
```

### Creating a Plugin

```python
# plugins/myplugin/__init__.py

from aim_core.plugins import BasePlugin

class Plugin(BasePlugin):
    name = "myplugin"
    version = "1.0.0"
    description = "My awesome plugin"
    
    def execute(self, input_data, **kwargs):
        return process(input_data)
```

---

## 📊 Roadmap

### v1 (Current) ✅
- [x] Train text → export .aim
- [x] Basic UI
- [x] Markov engine
- [x] Model loading

### v2 ✅
- [x] GUI improvements
- [x] Multiple engines
- [x] Plugin system
- [x] Web interface

### v3 🚀
- [x] Universal .aim format
- [x] Package manager (CLI)
- [x] Registry system
- [x] Plugin ecosystem
- [ ] AIM Hub (aimhub.org)
- [ ] Collaborative training
- [ ] Advanced engines (embedding, LLM)
- [ ] Mobile app

---

## 📄 License

MIT License - See LICENSE file

---

## 🤔 FAQ

**Q: How is AIM different from Hugging Face?**
A: AIM focuses on simplicity and local execution. Hugging Face is a comprehensive ML platform. AIM: lightweight, local-first. HF: feature-rich, cloud-enabled.

**Q: Can I use LLMs with AIM?**
A: Currently we support Markov and n-gram engines. LLM support is planned for v3.1+ (integrations with OpenAI, Hugging Face).

**Q: How large can .aim files be?**
A: .aim files are just ZIP packages. Size depends on engine and training data. Typical: 100KB - 10MB.

**Q: Can I train on proprietary data?**
A: Yes! .aim files stay on your machine. You control sharing.

**Q: How does the Hub work?**
A: Optional. You can use AIM entirely locally without ever connecting to aimhub.org.

---

## 📞 Support

- 📖 Documentation: [docs/](docs/)
- 💬 Discussions: [GitHub Discussions](https://github.com/)
- 🐛 Issues: [GitHub Issues](https://github.com/)
- 📧 Email: support@aimhub.org

---

**Made with ❤️ by the AIM Team**
