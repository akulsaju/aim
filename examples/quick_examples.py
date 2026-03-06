#!/usr/bin/env python
"""
AIM v3 Quick Examples
Simple examples of using AIM to create, train, and use AI models
"""

# Example 1: Train a model using the Python API
print("=" * 60)
print("Example 1: Train a Model with Python API")
print("=" * 60)

from aim_core import AIMModel

# Create a model
model = AIMModel.create(
    name="Story Generator",
    author="John Doe",
    engine="markov",
    description="Generates fantasy stories",
    model_type="text"
)

# Training data (mini example)
training_data = """
Once upon a time, there was a kingdom far away.
The kingdom had three towers and a great forest.
Many knights lived in the kingdom and protected the land.
One day, a mysterious wizard appeared in the forest.
The wizard had powerful magic and ancient knowledge.
The knights set out to meet the wizard.
After many adventures, they found him in the deepest woods.
""" * 5

# Train the model
print("\n🔧 Training model...")
stats = model.train(training_data, order=2)

print(f"✅ Training complete!")
print(f"   Vocabulary size: {stats.get('vocabulary_size')}")
print(f"   Transitions: {stats.get('transitions_count')}")

# Generate some text
print("\n🤖 Generating text...")
output = model.generate(prompt="Once upon", max_length=50)
print(f"Output: {output}")

# Save the model
print("\n💾 Saving model...")
filepath = model.save("story_generator.aim")
print(f"✅ Model saved to: {filepath}")

# ---

# Example 2: Load and use a saved model
print("\n" + "=" * 60)
print("Example 2: Load and Use a Saved Model")
print("=" * 60)

# Load the model
print("\n📂 Loading model...")
loaded_model = AIMModel.load("story_generator.aim")
print(f"✅ Loaded: {loaded_model}")

# Generate more text
prompts = [
    "The kingdom",
    "The wizard",
    "Many knights"
]

print("\n🤖 Generating variations:")
for prompt in prompts:
    output = loaded_model.generate(prompt=prompt, max_length=40)
    print(f"  Prompt: {prompt}")
    print(f"  Output: {output}\n")

# ---

# Example 3: Using the CLI
print("=" * 60)
print("Example 3: Using the CLI")
print("=" * 60)

print("""
# Train a model from command line:
aim train data.txt --name "my-model" --author "John" --engine markov

# Run the model:
aim run my-model.aim --prompt "Once upon a time" --length 100

# Get model information:
aim info my-model.aim

# List available engines:
aim list-engines

# Search the hub:
aim search --query "biology"

# Install a model from hub:
aim install wikipedia-ai
""")

# ---

# Example 4: Using different engines
print("\n" + "=" * 60)
print("Example 4: Using Different Engines")
print("=" * 60)

from aim_core import get_engine, list_engines

print(f"\nAvailable engines: {list_engines()}")

# Create models with different engines
for engine_name in ["markov", "ngram"]:
    print(f"\n📌 Creating {engine_name} model...")
    try:
        model = AIMModel.create(
            name=f"Test {engine_name}",
            author="Example",
            engine=engine_name
        )
        print(f"✅ {engine_name} model created")
    except Exception as e:
        print(f"⚠️  {engine_name}: {e}")

# ---

# Example 5: Using the Web API
print("\n" + "=" * 60)
print("Example 5: Using the Web API")
print("=" * 60)

print("""
# Start the Flask server first:
cd backend
python app.py

# Then in another terminal, use the API:

# Train via API
curl -X POST http://localhost:5000/api/v3/train \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "API Model",
    "author": "User",
    "engine": "markov",
    "text": "Training text..."
  }'

# Generate via API
curl -X POST http://localhost:5000/api/v3/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "prompt": "Once",
    "max_length": 100
  }'

# Save via API
curl -X POST http://localhost:5000/api/v3/save \\
  -H "Content-Type: application/json" \\
  -d '{
    "filename": "model.aim"
  }'
""")

# ---

# Example 6: Using Plugins
print("\n" + "=" * 60)
print("Example 6: Using Plugins")
print("=" * 60)

from aim_core.plugins import get_plugin_manager

manager = get_plugin_manager()
print(f"\nAvailable plugins: {manager.list_plugins()}")

print("""
# Using pdf_reader plugin in Python:
from aim_core.plugins import get_plugin_manager

manager = get_plugin_manager()
plugin = manager.get_plugin('pdf_reader')

if plugin:
    text = plugin.execute('/path/to/document.pdf')
    print(text)

# Using web_scraper plugin:
from aim_core.plugins import get_plugin_manager

manager = get_plugin_manager()
scraped_text = manager.execute_plugin(
    'web_scraper',
    'https://example.com/page'
)
print(scraped_text)
""")

# ---

# Example 7: Creating a Custom Plugin
print("\n" + "=" * 60)
print("Example 7: Creating a Custom Plugin")
print("=" * 60)

print("""
# Create a custom plugin at plugins/my_plugin/__init__.py:

from aim_core.plugins import BasePlugin

class Plugin(BasePlugin):
    name = "my_plugin"
    version = "1.0.0"
    description = "My awesome plugin"
    author = "Your Name"
    
    def execute(self, input_data, **kwargs):
        # Your plugin logic here
        result = process(input_data)
        return result

# Use your plugin:
from aim_core.plugins import get_plugin_manager

manager = get_plugin_manager()
result = manager.execute_plugin('my_plugin', input_data)
""")

print("\n" + "=" * 60)
print("🎉 Examples complete!")
print("=" * 60)
print("""
For more information:
- Documentation: AIM_V3_GUIDE.md
- API Reference: docs/API_REFERENCE.md
- Plugin Guide: docs/PLUGIN_GUIDE.md
""")
