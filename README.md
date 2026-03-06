# 🎯 AIM Studio

**A lightweight desktop application for training simple AI text models using Markov chains**

AIM Studio lets anyone create, train, and share text generation models without complex AI infrastructure. Train models on your own text data and export them as `.aim` files that others can use!

---

## 📋 Table of Contents

- [Features](#features)
- [What is AIM Studio?](#what-is-aim-studio)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Using AIM Studio](#using-aim-studio)
- [.AIM File Format](#aim-file-format)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

- **🎓 Easy Training**: Upload text files or paste text directly to train models
- **🤖 Text Generation**: Generate new text based on learned patterns
- **💾 Model Export**: Save trained models as portable `.aim` files
- **📂 Model Loading**: Load and run `.aim` files created by you or others
- **🎨 Clean UI**: Simple, intuitive interface for all skill levels
- **🔧 Customizable**: Adjust model complexity and generation parameters
- **🌐 Open Source**: Free and open for everyone to use and modify

---

## 🤔 What is AIM Studio?

AIM Studio is a beginner-friendly platform for creating text generation AI models using **Markov chains** - a simple but powerful statistical method for learning text patterns.

### What are Markov Chains?

A Markov chain model learns which words typically follow other words in your training text. For example, if you train it on fantasy stories, it learns that "once upon" is often followed by "a time", or that "magic" might be followed by "spell", "wand", or "power".

### Use Cases

- Create chatbots with specific personality styles
- Generate creative writing prompts
- Build text completion tools
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
