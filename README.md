# 🎯 AIM v3 - Open AI Model Ecosystem

**Git for AI models + App Store for AI**

AIM makes it easy to **create**, **export**, **share**, and **run** AI models like software packages.

---

## ✨ What's New in v3

### 🎁 Universal Model Format
Every model is a `.aim` file - a portable package containing metadata, configuration, and trained weights.

### 🔧 Multiple Engines
- **Markov** - Statistical text generation ✅
- **N-gram** - Language models ✅
- **Embedding** - Semantic similarity 📋
- **LLM** - Large Language Models 📋

### 📦 Package Manager
Install and manage models like npm packages:
```bash
aim train data.txt --name "my-model"
aim run mymodel.aim --prompt "text"
aim install wikipedia-ai
aim publish mymodel.aim
```

### 🌐 Model Registry (Local)

**Created by:** [@akulsaju](https://github.com/akulsaju)
Central registry for discovering and sharing models - coming soon!

### 🔌 Plugin System
Extend AIM with custom functionality:
- `pdf_reader` - Extract text from PDFs
- `web_scraper` - Scrape web pages  
- `image_generator` - Generate images from text
- Create custom plugins easily

### 💾 Multi-Format Data Loading
Train from `.txt`, `.md`, `.csv`, `.json`, `.pdf` files

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/user/aim
cd aim

# Install dependencies
pip install -r requirements.txt

# Install AIM CLI
pip install -e aim_cli/
```

### 2. Train Your First Model

```bash
# Create training data
echo "Your training text here..." > data.txt

# Train a model
aim train data.txt --name "my-model" --author "Your Name"

# Run the model
aim run my-model.aim --prompt "Start text" --length 100
```

### 3. Use in Python

```python
from aim_core import AIMModel

# Create and train
model = AIMModel.create(name="My Model", author="You", engine="markov")
model.train(text_data)

# Generate
output = model.generate(prompt="Once ", max_length=100)

# Save
model.save("mymodel.aim")

# Load
model = AIMModel.load("mymodel.aim")
```

### 4. Web Interface

```bash
cd backend
python app.py
# Visit http://localhost:5000
```

---

## 📚 Project Structure

```
aim/
├── aim_core/              # Core AIM system
│   ├── manifest.py       # Model format & metadata
│   ├── model.py          # AIM Model class
│   ├── engines.py        # AI engines
│   └── plugins.py        # Plugin system
│
├── aim_cli/              # Command-line interface
│   ├── aim.py            # CLI commands
│   └── trainer.py        # Dataset loading
│
├── aim_hub/              # Registry & package management
│   └── registry.py       # Local & remote registries
│
├── plugins/              # Extensible plugins
│   ├── pdf_reader/
│   ├── web_scraper/
│   └── image_generator/
│
├── backend/              # Flask REST API
│   ├── app.py            # Flask application
│   ├── trainer.py        # Legacy trainer
│   └── generator.py      # Legacy generator
│
├── frontend/             # Web UI
│   ├── index.html
│   ├── app.js
│   └── style.css
│
├── models/               # Saved .aim files
│   └── fantasy_story_generator.aim
│
├── docs/                 # Documentation
│   ├── AIM_FORMAT.md
│   ├── API_REFERENCE.md
│   └── PLUGIN_GUIDE.md
│
├── AIM_V3_GUIDE.md       # Complete v3 guide
└── requirements.txt      # Dependencies
```

---

## 🎓 Learning Path

**Absolute Beginner:**
1. Read [AIM_V3_GUIDE.md](AIM_V3_GUIDE.md) (10 min)
2. Run Quick Start above (15 min)
3. Explore examples: `python examples/quick_examples.py`

**Intermediate:**
1. Read [docs/AIM_FORMAT.md](docs/AIM_FORMAT.md) - understand .aim files
2. Try different engines
3. Create your own models
4. Use plugins

**Advanced:**
1. Read [docs/PLUGIN_GUIDE.md](docs/PLUGIN_GUIDE.md)
2. Create custom plugins
3. Contribute engines
4. Deploy private hub

---

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| [AIM_V3_GUIDE.md](AIM_V3_GUIDE.md) | Complete guide to AIM v3 |
| [docs/AIM_FORMAT.md](docs/AIM_FORMAT.md) | .aim file format specification |
| [docs/API_REFERENCE.md](docs/API_REFERENCE.md) | REST API reference |
| [docs/PLUGIN_GUIDE.md](docs/PLUGIN_GUIDE.md) | Creating plugins |

---

## 🔌 Available Plugins

### pdf_reader
Extract text from PDF files for training.

```python
from aim_core.plugins import get_plugin_manager

manager = get_plugin_manager()
text = manager.execute_plugin('pdf_reader', '/path/to/file.pdf')
```

### web_scraper
Scrape text from web pages.

```python
text = manager.execute_plugin('web_scraper', 'https://example.com')
```

### image_generator
Generate images from text descriptions (requires API).

```python
result = manager.execute_plugin('image_generator', 'A cat on a beach')
```

---

## 💻 CLI Commands

```bash
# Training
aim train <file>                    # Train model from file
aim train <file> --engine ngram     # Use specific engine
aim train <file> --order 3          # Markov order

# Running Models
aim run <model.aim>                 # Interactive mode
aim run <model.aim> --prompt "text" # With prompt
aim run <model.aim> --length 200    # Custom length

# Model Management
aim info <model.aim>                # Show model info
aim list-engines                    # List available engines
aim search --query "biology"        # Search hub
aim install <model-name>            # Install from hub
aim publish <model.aim>             # Publish to hub

# Help
aim --help
aim train --help
```

---

## 🌐 REST API

The Flask server provides REST endpoints:

```bash
# Get available engines
GET /api/v3/engines

# Train model
POST /api/v3/train
Body: {"name": "...", "text": "...", "engine": "markov"}

# Generate text
POST /api/v3/generate
Body: {"prompt": "...", "max_length": 100}

# Save model
POST /api/v3/save
Body: {"filename": "model.aim"}

# Load model
POST /api/v3/load
File upload or {"path": "/path/to/model.aim"}

# List plugins
GET /api/v3/plugins

# Execute plugin
POST /api/v3/plugins/<name>/execute
Body: {"input": "data"}
```

See [docs/API_REFERENCE.md](docs/API_REFERENCE.md) for complete API reference.

---

## 🧪 Examples

### Train from Text File

```bash
aim train examples/sample_text.txt --name "story-generator"
aim run story-generator.aim --prompt "Once upon"
```

### Use Different Engines

```bash
# Markov chain (simple, fast)
aim train data.txt --name model1 --engine markov --order 2

# N-gram (more sophisticated)
aim train data.txt --name model2 --engine ngram

# Compare generations
aim run model1.aim --prompt "The"
aim run model2.aim --prompt "The"
```

### Publish and Share

```bash
# Save locally
aim train data.txt --name "my-awesome-model"

# Publish to hub
aim publish my-awesome-model.aim --token YOUR_TOKEN

# Others can install it
aim install my-awesome-model
```

### Use in Your Project

```python
from aim_core import AIMModel

# Load pre-trained model
model = AIMModel.load("biology_tutor.aim")

# Generate responses
for question in questions:
    answer = model.generate(prompt=question, max_length=200)
    print(f"Q: {question}")
    print(f"A: {answer}\n")
```

---

## 🛠️ Development

### Install for Development

```bash
git clone https://github.com/user/aim
cd aim
pip install -r requirements.txt
pip install -e aim_cli/
```

### Run Tests

```bash
pytest tests/
```

### Project Roadmap

- [x] Universal .aim format
- [x] Markov & N-gram engines
- [x] CLI tool (aim command)
- [x] Plugin system
- [x] REST API
- [ ] AIM Hub (aimhub.org) - Deploy and host
- [ ] Embedding engine
- [ ] LLM engine support
- [ ] Web-based trainer
- [ ] Collaborative model training
- [ ] Mobile app
- [ ] GUI desktop application

---

## 🤝 Contributing

Contributions welcome! Areas to contribute:

1. **New Engines** - Implement embedding, LLM engines
2. **Plugins** - Create pdf_reader, web_scraper, voice_ai, etc.
3. **Documentation** - Improve guides and examples
4. **Testing** - Add test coverage
5. **UI/UX** - Improve web interface
6. **Hub** - Deploy aimhub.org registry

See [docs/CONTRIBUTION_GUIDE.md](docs/CONTRIBUTION_GUIDE.md) for details.

---

## 📊 Features Comparison

| Feature | AIM | Hugging Face | PyTorch | n/a |
|---------|-----|--------------|---------|-----|
| Lightweight | ✅ | ❌ | ❌ | - |
| Local-first | ✅ | ❌ | ✅ | - |
| Simple API | ✅ | ⚠️ | ❌ | - |
| Model Sharing | ✅ | ✅ | ⚠️ | - |
| Package Manager | ✅ | ❌ | ❌ | - |
| Multiple Engines | ✅ | ✅ | ❌ | - |
| Plugin System | ✅ | ❌ | ❌ | - |

---

## ❓ FAQ

**Q: Is AIM for beginners?**
A: Yes! AIM is designed to be beginner-friendly while remaining powerful for advanced users.

**Q: Can I use LLMs?**
A: LLM support is coming in v3.1. Currently supports Markov and N-gram engines.

**Q: How large can models be?**
A: Typically 100KB - 10MB. Depends on engine and training data.

**Q: Is it free?**
A: Yes! MIT License - free for personal and commercial use.

**Q: Can I deploy models?**
A: Yes! Models can run locally, behind a web API, or on cloud platforms.

**Q: How does aimhub.org work?**
A: Central registry for discovering and installing models (like npm or pip). Optional - use AIM entirely offline.

---

## 📜 License

MIT License - See [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

Inspired by:
- **npm** - Package management simplicity
- **Docker** - Containerization and distribution
- **PyTorch** - ML framework accessibility
- **Hugging Face** - Model sharing community

---

## 📞 Support & Community

- 📖 **Docs**: [AIM_V3_GUIDE.md](AIM_V3_GUIDE.md)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/)
- 🐛 **Issues**: [GitHub Issues](https://github.com/)
- 📧 **Email**: support@aimhub.org
- 🐦 **Twitter**: [@aimhub_org](https://twitter.com/)

---

**Made with ❤️ to democratize AI**

*Latest: AIM v3.0 - March 2026*
- Learn about natural language processing
- Experiment with AI text generation
- Share custom models with friends or the community

---

## 🔧 How It Works

### Training Process

1. **Input Text**: You provide sample text (stories, articles, conversations, etc.)
2. **Tokenization**: The text is split into words and punctuation
3. **Pattern Learning**: The system learns which words follow which sequences
4. **Model Creation**: A transition dictionary is built mapping word sequences to possible next words

### Generation Process

1. **Starting Point**: Begin with a random sequence or user-provided prompt
2. **Word Selection**: Look up possible next words based on current sequence
3. **Continuation**: Add the selected word and shift the sequence window
4. **Iteration**: Repeat until desired length is reached

---

## 📦 Installation

### Prerequisites

- **Python 3.7+** installed on your system
- **pip** package manager
- A modern web browser (Chrome, Firefox, Safari, or Edge)

### Step 1: Clone or Download

```bash
git clone https://github.com/yourusername/aim-studio.git
cd aim-studio
```

Or download and extract the ZIP file.

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- Flask (web framework)
- Flask-CORS (cross-origin resource sharing)

### Step 3: Run the Application

```bash
cd backend
python app.py
```

The server will start at `http://localhost:5000`

### Step 4: Open the Interface

Open your web browser and navigate to:
```
http://localhost:5000
```

---

## 🚀 Quick Start

### Training Your First Model

1. **Prepare Training Text**
   - Get a text file (.txt) with at least 100-200 words
   - Or use the example file in `examples/sample_text.txt`

2. **Train the Model**
   - Open AIM Studio in your browser
   - Paste your text into the "Train Model" section
   - Choose model order (2 is recommended for beginners)
   - Click "Train Model"

3. **Generate Text**
   - Go to "Generate Text" section
   - Optionally add a prompt (starting words)
   - Set maximum word count
   - Click "Generate Text"

4. **Export Your Model**
   - Go to "Export Model" section
   - Enter a model name and your name
   - Click "Export as .aim File"
   - Save the downloaded file

### Loading an Existing Model

1. **Find a .aim File**
   - Use the example: `models/fantasy_story_generator.aim`
   - Or download one from the community

2. **Load the Model**
   - Go to "Load Model" section
   - Click "Choose .aim File" and select your file
   - Or click on a model in the "Available Models" list
   - Click "Load Model"

3. **Use the Model**
   - Once loaded, go to "Generate Text"
   - Generate text with or without prompts

---

## 📖 Using AIM Studio

### Training Parameters

#### Model Order
- **Order 1**: Simplest, looks at one word at a time
  - Needs less training data
  - Produces less coherent text
  
- **Order 2** ⭐ (Recommended)
  - Balances coherence and flexibility
  - Good for most use cases
  
- **Order 3**: Most complex, looks at three words
  - Produces more coherent text
  - Requires significantly more training data

#### Training Text Quality
- **Minimum**: 50 words (works but limited)
- **Recommended**: 500+ words for decent results
- **Best**: 2000+ words for high-quality models

### Generation Parameters

#### Prompt
- Optional starting words for generation
- Leave empty for random starting point
- Works best with sequences that exist in training data

#### Maximum Length
- Number of words to generate
- Range: 10-500 words
- Recommend 50-150 for most cases

---

## 📄 .AIM File Format

AIM files use JSON format and contain all information needed to recreate a trained model.

### Structure

```json
{
  "model_name": "Name of the model",
  "author": "Creator's name",
  "version": "1.0",
  "algorithm": "Markov Chain (order 2)",
  "created_at": "2026-03-05T10:00:00",
  "model_data": {
    "order": 2,
    "transitions": {
      "word1 word2": ["word3", "word4", "word5"],
      "word2 word3": ["word6", "word7"]
    },
    "start_words": [
      "word1 word2",
      "word2 word3"
    ],
    "vocabulary_size": 1000
  }
}
```

### Fields Explained

- **model_name**: Display name for the model
- **author**: Creator's name or handle
- **version**: Version number (useful for updates)
- **algorithm**: Type of algorithm used (always Markov Chain for now)
- **created_at**: ISO timestamp of creation
- **model_data.order**: N-gram order (1, 2, or 3)
- **model_data.transitions**: Word sequence → possible next words mapping
- **model_data.start_words**: Valid starting sequences for generation
- **model_data.vocabulary_size**: Total unique words in the model

### Sharing .AIM Files

- ✅ Files are portable - share via email, cloud storage, etc.
- ✅ Platform independent - works on any system
- ✅ No executables - safe to share (just JSON data)
- ⚠️ File size can grow with very large training texts

---

## 📁 Project Structure

```
aim-studio/
│
├── backend/
│   ├── trainer.py          # Markov chain training logic
│   ├── generator.py        # Text generation logic
│   └── app.py              # Flask API server
│
├── frontend/
│   ├── index.html          # Main UI interface
│   ├── style.css           # Styling and layout
│   └── app.js              # Frontend JavaScript logic
│
├── models/
│   └── *.aim               # Saved model files
│
├── examples/
│   ├── sample_text.txt     # Example training text
│   └── *.aim               # Example pre-trained models
│
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── LICENSE                # License information
```

---

## 🔌 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### 1. Train Model
```http
POST /api/train
Content-Type: application/json

{
  "text": "Your training text here...",
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
    "vocabulary_size": 1234,
    "transitions_count": 5678
  }
}
```

#### 2. Generate Text
```http
POST /api/generate
Content-Type: application/json

{
  "prompt": "Once upon",
  "max_length": 100,
  "temperature": 1.0
}
```

**Response:**
```json
{
  "success": true,
  "text": "Once upon a time there was...",
  "prompt": "Once upon",
  "length": 98
}
```

#### 3. Export Model
```http
POST /api/export
Content-Type: application/json

{
  "model_name": "My Cool Model",
  "author": "Your Name",
  "version": "1.0"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Model exported successfully",
  "filename": "my_cool_model.aim",
  "aim_data": { ... }
}
```

#### 4. Load Model
```http
POST /api/load_model
Content-Type: application/json

{
  "aim_data": { ... }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Model loaded successfully",
  "model_info": {
    "name": "My Cool Model",
    "author": "Your Name",
    "version": "1.0",
    "algorithm": "Markov Chain (order 2)"
  }
}
```

#### 5. List Models
```http
GET /api/models
```

**Response:**
```json
{
  "success": true,
  "models": [
    {
      "filename": "model1.aim",
      "model_name": "Model 1",
      "author": "Author Name",
      "version": "1.0",
      "algorithm": "Markov Chain (order 2)",
      "created_at": "2026-03-05T10:00:00"
    }
  ]
}
```

#### 6. Get Model Status
```http
GET /api/status
```

**Response:**
```json
{
  "model_loaded": true,
  "order": 2,
  "vocabulary_size": 1234,
  "transitions_count": 5678
}
```

---

## 💡 Examples

### Example 1: Story Generator

**Training Text:** Fantasy stories, fairy tales
**Order:** 2
**Prompt:** "Once upon"
**Result:** Generates fantasy-style story beginnings

### Example 2: Technical Writer

**Training Text:** Technical documentation, tutorials
**Order:** 2-3
**Prompt:** "To implement"
**Result:** Generates technical instruction-style text

### Example 3: Poetry Generator

**Training Text:** Poems, lyrics
**Order:** 1-2
**Prompt:** Leave empty
**Result:** Generates poetic phrases

### Example Training Texts

Try training on different types of content:
- 📚 Books (from Project Gutenberg)
- 📰 News articles
- 💬 Chat logs
- 🎭 Movie scripts
- 🎵 Song lyrics
- 📝 Your own writing

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Bug Reports
- Open an issue on GitHub
- Describe the problem clearly
- Include steps to reproduce

### Feature Requests
- Open an issue with the "enhancement" label
- Explain the feature and its benefits
- Discuss implementation ideas

### Code Contributions
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Beginner-Friendly Tasks
- Improve documentation
- Add example models
- Create tutorials
- Fix typos and formatting

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### What this means:
- ✅ Free to use for any purpose
- ✅ Free to modify and distribute
- ✅ Can be used commercially
- ✅ No warranty provided

---

## 🙏 Acknowledgments

- Markov chains concept introduced by Andrey Markov
- Built with Flask, a Python micro web framework
- Inspired by the need for accessible AI tools
- Thanks to all contributors and users!

---

## 📞 Support

### Getting Help
- 📖 Read this README thoroughly
- 🐛 Check existing GitHub issues
- 💬 Open a new issue for bugs or questions
- 📧 Contact: your-email@example.com

### Troubleshooting

**Server won't start?**
- Check Python version (3.7+)
- Install requirements: `pip install -r requirements.txt`
- Check if port 5000 is available

**Can't connect to server?**
- Make sure backend is running
- Check firewall settings
- Try `http://localhost:5000` instead of `127.0.0.1:5000`

**Generated text is nonsense?**
- Increase training text amount
- Try different order values
- Ensure training text is coherent

**Model file won't load?**
- Verify JSON format is valid
- Check all required fields are present
- Try re-exporting the model

---

## 🚀 Future Plans

- [ ] Support for more model types (LSTM, GPT-style)
- [ ] Model merging and fine-tuning
- [ ] Web-based model sharing platform
- [ ] Preprocessing options (lowercase, punctuation handling)
- [ ] Real-time training progress display
- [ ] Batch generation mode
- [ ] API authentication for multi-user setups

---

## 🌟 Star History

If you find AIM Studio useful, consider giving it a star on GitHub! ⭐

---

**Happy modeling! 🎯**

*Create something amazing and share it with the world!*
