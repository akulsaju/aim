# Plugin Development Guide

## Overview

Plugins extend AIM with custom functionality. The plugin system allows you to add new data sources, engines, or processing capabilities.

---

## Creating a Plugin

### 1. Create Plugin Directory

```
plugins/
└── my_plugin/
    ├── __init__.py          # Plugin code
    └── plugin.json          # Manifest
```

### 2. Define Plugin Manifest (plugin.json)

```json
{
  "name": "my_plugin",
  "version": "1.0.0",
  "description": "What my plugin does",
  "author": "Your Name",
  "config": {
    "option1": "default_value"
  }
}
```

### 3. Implement Plugin Class

```python
# plugins/my_plugin/__init__.py

from aim_core.plugins import BasePlugin

class Plugin(BasePlugin):
    name = "my_plugin"
    version = "1.0.0"
    description = "Does something amazing"
    author = "Your Name"
    
    def __init__(self, config=None):
        super().__init__(config)
        # Initialize your plugin
    
    def execute(self, input_data, **kwargs):
        """
        Execute the plugin.
        
        Args:
            input_data: Input to process
            **kwargs: Additional arguments
        
        Returns:
            Processed output
        """
        # Your plugin logic here
        return process(input_data, **kwargs)
    
    def validate_config(self):
        """Validate configuration. Return True if valid."""
        return True
```

---

## Plugin Types

### 1. Data Source Plugin

Plugins that load training data:

```python
class Plugin(BasePlugin):
    name = "database_loader"
    description = "Load training data from database"
    
    def execute(self, connection_string, query, **kwargs):
        """Load data from database."""
        db = connect(connection_string)
        data = db.execute(query)
        return '\n'.join(data)
```

### 2. Data Processor Plugin

Plugins that transform data:

```python
class Plugin(BasePlugin):
    name = "text_cleaner"
    description = "Clean and normalize text"
    
    def execute(self, text, **kwargs):
        """Clean text."""
        # Remove special characters
        text = clean(text)
        # Normalize whitespace
        text = normalize(text)
        return text
```

### 3. Model Exporter Plugin

Plugins that export models to different formats:

```python
class Plugin(BasePlugin):
    name = "pytorch_exporter"
    description = "Export models to PyTorch format"
    
    def execute(self, model, output_path, **kwargs):
        """Export model."""
        pytorch_model = convert_to_pytorch(model)
        torch.save(pytorch_model, output_path)
        return output_path
```

### 4. Feature Plugin

Plugins that add processing features:

```python
class Plugin(BasePlugin):
    name = "pdf_summarizer"
    description = "Summarize PDF documents"
    
    def execute(self, pdf_path, **kwargs):
        """Summarize PDF."""
        text = extract_text(pdf_path)
        summary = summarize(text)
        return summary
```

---

## Using Plugins

### Via CLI

```bash
# Execute a plugin
aim plugin execute my_plugin --input "data.txt"
```

### Via Python API

```python
from aim_core.plugins import get_plugin_manager

manager = get_plugin_manager()

# Execute plugin
result = manager.execute_plugin('my_plugin', input_data)

# Get info
info = manager.get_plugin_info('my_plugin')
print(info)
```

### Via REST API

```bash
curl -X POST http://localhost:5000/api/v3/plugins/my_plugin/execute \
  -H "Content-Type: application/json" \
  -d '{"input": "my data"}'
```

---

## Built-in Plugins

### PDF Reader Plugin

```python
# plugins/pdf_reader/

class Plugin(BasePlugin):
    name = "pdf_reader"
    description = "Extract text from PDF files"
    
    def execute(self, pdf_path, **kwargs):
        """Extract text from PDF."""
        import PyPDF2
        
        text = []
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text.append(page.extract_text())
        
        return '\n'.join(text)
```

### Web Scraper Plugin

```python
# plugins/web_scraper/

class Plugin(BasePlugin):
    name = "web_scraper"
    description = "Scrape text from websites"
    
    def execute(self, url, **kwargs):
        """Scrape webpage."""
        from bs4 import BeautifulSoup
        import requests
        
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script/style
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return ' '.join(chunk for chunk in chunks if chunk)
```

### Image Generator Plugin

```python
# plugins/image_generator/

class Plugin(BasePlugin):
    name = "image_generator"
    description = "Generate images from text descriptions"
    
    def execute(self, prompt, model="stable-diffusion", **kwargs):
        """Generate image from text."""
        # Would integrate with Stable Diffusion, DALL-E, etc.
        # Placeholder for now
        return f"Would generate: {prompt}"
```

---

## Plugin Configuration

### Access Configuration

```python
class Plugin(BasePlugin):
    def __init__(self, config=None):
        super().__init__(config)
        
        # Access config values
        self.api_key = self.config.get('api_key')
        self.model = self.config.get('model', 'default')
        self.timeout = self.config.get('timeout', 30)
```

### Define Configuration Schema

```python
# plugin.json
{
  "name": "my_plugin",
  "version": "1.0.0",
  "config": {
    "api_key": "",          // Required
    "model": "default",     // Optional
    "timeout": 30,          // Optional with default
    "options": {
      "verbose": true,
      "cache": true
    }
  }
}
```

### Validate Configuration

```python
class Plugin(BasePlugin):
    required_keys = ['api_key']
    
    def __init__(self, config=None):
        super().__init__(config)
    
    def validate_config(self):
        """Check required configuration."""
        for key in self.required_keys:
            if key not in self.config:
                return False
        return True
```

---

## Advanced Features

### Plugin Hooks

Register callbacks to run at specific events:

```python
from aim_core.plugins import get_plugin_manager

manager = get_plugin_manager()

# Register hook
def on_model_trained(model):
    print(f"Model trained: {model.name}")

manager.register_hook('model_trained', on_model_trained)

# Call hooks
manager.call_hook('model_trained', model)
```

### Plugin Dependencies

Declare dependencies in plugin.json:

```json
{
  "name": "my_plugin",
  "dependencies": {
    "requests": ">=2.25.0",
    "beautifulsoup4": ">=4.9.0"
  }
}
```

### Error Handling

```python
class Plugin(BasePlugin):
    def execute(self, input_data, **kwargs):
        try:
            result = process(input_data)
            return result
        except ValueError as e:
            raise ValueError(f"Invalid input: {e}")
        except Exception as e:
            raise RuntimeError(f"Plugin error: {e}")
```

---

## Plugin Distribution

### Share on GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/user/my_plugin
git push
```

### Register in Plugin Directory

Submit your plugin to be listed:

1. Fork [aimhub/plugins](https://github.com/aimhub/plugins)
2. Create plugin manifest
3. Submit pull request

### Package as PyPI Module

```bash
# setup.py
from setuptools import setup

setup(
    name='aim-plugin-my_plugin',
    version='1.0.0',
    author='Your Name',
    packages=['aim_plugins.my_plugin'],
)

# Install
pip install aim-plugin-my_plugin
```

---

## Testing Plugins

```python
# test_my_plugin.py

import pytest
from plugins.my_plugin import Plugin

def test_plugin_init():
    plugin = Plugin({"option": "value"})
    assert plugin.name == "my_plugin"

def test_plugin_execute():
    plugin = Plugin()
    result = plugin.execute("input_data")
    assert result is not None

def test_plugin_validation():
    plugin = Plugin({})
    assert plugin.validate_config()
```

Run tests:

```bash
pytest test_my_plugin.py
```

---

## Examples

### Email Notifier Plugin

```python
class Plugin(BasePlugin):
    name = "email_notifier"
    description = "Send email notifications"
    
    def execute(self, message, recipient, **kwargs):
        import smtplib
        
        server = smtplib.SMTP_SSL(
            self.config['smtp_host'],
            self.config['smtp_port']
        )
        server.login(
            self.config['email'],
            self.config['password']
        )
        server.sendmail(
            self.config['email'],
            recipient,
            message
        )
        server.quit()
        return f"Email sent to {recipient}"
```

### Database Logger Plugin

```python
class Plugin(BasePlugin):
    name = "db_logger"
    description = "Log training results to database"
    
    def execute(self, model_name, metrics, **kwargs):
        import sqlite3
        
        conn = sqlite3.connect(self.config['db_path'])
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO training_logs (model, metrics) VALUES (?, ?)",
            (model_name, str(metrics))
        )
        conn.commit()
        conn.close()
        return "Logged to database"
```

---

## Troubleshooting

### Plugin Not Found

```bash
# Ensure plugin directory exists and has __init__.py
ls plugins/my_plugin/__init__.py
```

### Plugin Won't Load

```bash
# Check plugin.json syntax
python -c "import json; json.load(open('plugins/my_plugin/plugin.json'))"

# Check for import errors
python -c "from plugins.my_plugin import Plugin"
```

### Configuration Issues

```bash
# Validate configuration
python -c "from plugins.my_plugin import Plugin; p = Plugin({}); print(p.validate_config())"
```

---

## API Reference

### BasePlugin Methods

```python
class BasePlugin(ABC):
    def __init__(self, config):
        """Initialize with configuration."""
    
    @abstractmethod
    def execute(self, input_data, **kwargs):
        """Execute plugin logic."""
    
    def get_info(self):
        """Get plugin metadata."""
    
    def validate_config(self):
        """Validate configuration."""
```

### PluginManager Methods

```python
manager.discover_plugins()
manager.register_plugin(name, plugin)
manager.get_plugin(name)
manager.execute_plugin(name, data)
manager.list_plugins()
manager.get_plugin_info(name)
manager.register_hook(hook_name, callback)
manager.call_hook(hook_name, *args, **kwargs)
```

---

## Best Practices

1. **Keep plugins focused** - One responsibility per plugin
2. **Document configuration** - Clear config schema with examples
3. **Handle errors gracefully** - Useful error messages
4. **Validate input** - Check input data before processing
5. **Use logging** - Log important events
6. **Version properly** - Use semantic versioning
7. **Test thoroughly** - Unit and integration tests
8. **Document usage** - Clear examples in README

---

For more examples and the plugin ecosystem, visit [https://github.com/aimhub/plugins](https://github.com/aimhub/plugins)
