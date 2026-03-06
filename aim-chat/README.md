# 💬 AIM Chat

A simple, lightweight ChatGPT-like chatbot application that runs 100% locally. Load `.aim` knowledge models and chat with your own AI assistant!

**Created by:** [@akulsaju](https://github.com/akulsaju)

## 🌟 Features

- **Simple Chat Interface** - Clean, ChatGPT-style UI
- **Knowledge-Based Responses** - AI retrieves relevant information from loaded models
- **100% Local** - No cloud services, complete privacy
- **Lightweight** - No heavy AI frameworks like TensorFlow or PyTorch
- **Easy to Extend** - Create your own `.aim` knowledge models

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Server

```bash
cd backend
python app.py
```

### 3. Open in Browser

Navigate to: **http://localhost:5000**

That's it! 🎉

## 📁 Project Structure

```
aim-chat/
├── backend/
│   ├── app.py              # Flask server
│   ├── chat_engine.py      # Keyword-based retrieval logic
│   └── model_loader.py     # Loads .aim files
├── frontend/
│   ├── index.html          # Chat UI
│   ├── style.css           # Styling
│   └── app.js              # Frontend logic
├── models/
│   ├── solar.aim           # Solar system knowledge
│   └── general.aim         # General tech knowledge
├── README.md
└── requirements.txt
```

## 🤖 How It Works

### The AIM Model Format

`.aim` files are simple JSON files containing knowledge sentences:

```json
{
  "name": "MyAI",
  "version": "1.0",
  "type": "chat",
  "description": "My custom AI assistant",
  "knowledge": [
    "The sky is blue due to Rayleigh scattering.",
    "Water boils at 100°C at sea level.",
    "Python is a programming language."
  ]
}
```

### How Responses Work

1. **User asks a question**: "What is Python?"
2. **Extract keywords**: ["python"]
3. **Search knowledge base**: Find sentences containing "python"
4. **Return best match**: "Python is a programming language."

It's that simple! No neural networks, no complex ML models - just smart keyword matching.

## 📝 Creating Your Own Models

Create a new file `mymodel.aim` in the `models/` folder:

```json
{
  "name": "HistoryAI",
  "version": "1.0",
  "type": "chat",
  "description": "Historical facts",
  "knowledge": [
    "The Roman Empire fell in 476 AD.",
    "World War II ended in 1945.",
    "The Great Wall of China was built over centuries."
  ]
}
```

Save it and reload the page - your model will appear in the sidebar!

## 🎯 Use Cases

- **Educational Bots** - Create subject-specific tutors
- **Documentation Helpers** - Load project documentation as knowledge
- **FAQ Bots** - Answer common questions
- **Study Aids** - Quiz yourself with flashcard-style knowledge
- **Personal Assistants** - Store personal notes and retrieve them conversationally

## 🛠️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | Check server and model status |
| `/api/models` | GET | List available models |
| `/api/load_model_by_name` | POST | Load a model by filename |
| `/api/chat` | POST | Send a message and get response |
| `/api/history` | GET | Get conversation history |
| `/api/clear` | POST | Clear conversation history |

## 🧠 How the Retrieval Engine Works

### Keyword Extraction

```python
User: "Tell me about the Sun"
Keywords: ["sun"]  # Stopwords removed
```

### Relevance Scoring

Each knowledge sentence is scored based on:
- Number of keyword matches
- Exact word boundary matches (bonus points)

### Best Match Selection

The sentence with the highest relevance score is returned.

## 🎨 Customization

### Change the UI Theme

Edit `frontend/style.css` and modify the CSS variables:

```css
:root {
    --primary-color: #10a37f;  /* Change this */
    --background: #f7f7f8;
    /* ... */
}
```

### Improve the Retrieval Logic

Edit `backend/chat_engine.py` to:
- Add synonym matching
- Implement fuzzy search
- Add multi-sentence responses
- Include context awareness

## 📊 Example Conversations

**With SolarAI:**

```
User: What is the Sun?
AI: The Sun is the star at the center of the Solar System.

User: Tell me about Mars
AI: Mars is known as the Red Planet due to iron oxide on its surface.
```

**With GeneralAI:**

```
User: What is Python?
AI: Python is a high-level programming language known for its simplicity.

User: Explain machine learning
AI: Machine learning is a subset of artificial intelligence.
```

## 🚧 Limitations

- **No learning**: The bot doesn't learn from conversations
- **Keyword-based**: Simple matching, not true natural language understanding
- **Single-sentence responses**: Returns one knowledge item at a time
- **No context**: Each query is independent

## 🔮 Future Enhancements

Want to improve AIM Chat? Here are ideas:

- [ ] Add sentence embeddings for better matching
- [ ] Support multi-sentence responses
- [ ] Implement conversation context
- [ ] Add voice input/output
- [ ] Create a model editor UI
- [ ] Support document uploads (PDF, TXT)
- [ ] Add authentication and user profiles

## 📄 License

MIT License - Feel free to use this project however you like!

## 🙏 Contributing

This is a beginner-friendly project! Contributions welcome:

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 💡 Tips

- **More knowledge = better responses**: Add lots of relevant sentences
- **Be specific**: Detailed sentences work better than vague ones
- **Test your models**: Try various questions to ensure good coverage
- **Keep it simple**: The beauty of AIM Chat is its simplicity

## 📞 Need Help?

- Check the code comments - everything is well documented
- Experiment with the example models
- Create an issue if you find bugs

---

**Built with ❤️ by [@akulsaju](https://github.com/akulsaju)**

Start chatting with your AI assistant today! 🚀
