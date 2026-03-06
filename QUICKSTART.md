# 🚀 Quick Start Guide - AIM Studio

## Installation & Running (3 Simple Steps)

### Step 1: Install Dependencies
Open your terminal/command prompt in the aim-studio folder and run:

```bash
pip install -r requirements.txt
```

### Step 2: Start the Backend Server
Navigate to the backend folder and run the Flask app:

```bash
cd backend
python app.py
```

You should see:
```
==================================================
AIM Studio Backend Server
==================================================
Starting server on http://localhost:5000
Models directory: ...
==================================================
```

### Step 3: Open the Application
Open your web browser and go to:
```
http://localhost:5000
```

That's it! You're ready to train your first model! 🎉

---

## First-Time Usage Tutorial

### 1. Train Your First Model

1. Copy the example text from `examples/sample_text.txt`
2. Paste it into the "Train Model" section
3. Keep the order at 2 (default)
4. Click "Train Model"
5. Wait for the success message

### 2. Generate Text

1. Go to the "Generate Text" section
2. Try entering a prompt like "once upon" or "the wizard"
3. Click "Generate Text"
4. See your AI-generated story!

### 3. Export Your Model

1. Go to "Export Model" section
2. Enter a cool name like "My Fantasy Writer"
3. Add your name as author
4. Click "Export as .aim File"
5. The file will download automatically

### 4. Load an Existing Model

1. Go to "Load Model" section
2. Click on "Fantasy Story Generator" in the available models list
3. Or upload the .aim file you just exported
4. Generate new text with the loaded model

---

## Troubleshooting

**Problem:** `ModuleNotFoundError: No module named 'flask'`  
**Solution:** Run `pip install -r requirements.txt`

**Problem:** Server won't start or "Address already in use"  
**Solution:** Another app is using port 5000. Kill that process or change the port in [app.py](backend/app.py#L365)

**Problem:** "Server not connected" error in browser  
**Solution:** Make sure the backend is running in your terminal

**Problem:** Generated text is gibberish  
**Solution:** You need more training text (at least 200+ words)

---

## Tips for Better Models

✅ Use **500+ words** of training text for best results  
✅ Keep text **consistent in style** (all stories, or all technical docs, etc.)  
✅ Use **order 2** for balanced results  
✅ Use **order 3** only if you have 2000+ words of training data  
✅ **Experiment!** Try different text sources and parameters  

---

## Next Steps

- Try training on different types of text (poems, technical docs, chat logs)
- Experiment with different order values (1, 2, 3)
- Share your .aim files with friends
- Read the full [README.md](README.md) for advanced usage

---

**Need Help?**  
Check the full documentation in [README.md](README.md) or open an issue on GitHub!

**Have Fun Creating! 🎯**
