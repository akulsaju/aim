"""
AIM Studio v3 - Flask Backend API
REST API for AIM Model Ecosystem
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from aim_core import AIMModel, AIMManifest, create_manifest, get_engine, list_engines
from aim_hub import Registry, RegistryClient
from aim_core.plugins import get_plugin_manager

# Legacy imports for backward compatibility
from trainer import MarkovTrainer, train_model
from generator import MarkovGenerator, generate_text


# Initialize Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Configure paths
MODELS_DIR = Path(__file__).parent.parent / 'models'
MODELS_DIR.mkdir(exist_ok=True)

# Initialize AIM components
local_registry = Registry()
plugin_manager = get_plugin_manager()

# Store current model
current_model = None
current_aim_model = None


@app.route('/')
def index():
    """Serve the main frontend page."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/train', methods=['POST'])
def train():
    """
    Train a new Markov chain model from text data.
    
    Expected JSON payload:
        {
            "text": "training text data...",
            "order": 2  // optional, default is 2
        }
    
    Returns:
        JSON with training status and model statistics
    """
    global current_model
    
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided for training'}), 400
        
        text = data['text']
        order = data.get('order', 2)  # Default to bigram model
        
        # Validate order
        if not isinstance(order, int) or order < 1 or order > 5:
            return jsonify({'error': 'Order must be an integer between 1 and 5'}), 400
        
        # Train the model
        trainer = train_model(text, order=order)
        current_model = trainer
        
        # Get model statistics
        model_data = trainer.get_model_data()
        
        return jsonify({
            'success': True,
            'message': 'Model trained successfully',
            'stats': {
                'order': model_data['order'],
                'vocabulary_size': model_data['vocabulary_size'],
                'transitions_count': len(model_data['transitions'])
            }
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Training failed: {str(e)}'}), 500


@app.route('/api/generate', methods=['POST'])
def generate():
    """
    Generate text using the current model.
    
    Expected JSON payload:
        {
            "prompt": "optional starting text",
            "max_length": 100,  // optional, default 100
            "temperature": 1.0  // optional, default 1.0
        }
    
    Returns:
        JSON with generated text
    """
    global current_model
    
    try:
        # Check if model exists
        if current_model is None:
            return jsonify({'error': 'No model loaded. Please train or load a model first.'}), 400
        
        data = request.get_json() or {}
        
        prompt = data.get('prompt', None)
        max_length = data.get('max_length', 100)
        temperature = data.get('temperature', 1.0)
        
        # Validate parameters
        if not isinstance(max_length, int) or max_length < 1 or max_length > 500:
            return jsonify({'error': 'max_length must be between 1 and 500'}), 400
        
        # Generate text
        generated_text = generate_text(
            current_model,
            max_length=max_length,
            prompt=prompt,
            temperature=temperature
        )
        
        return jsonify({
            'success': True,
            'text': generated_text,
            'prompt': prompt,
            'length': len(generated_text.split())
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Generation failed: {str(e)}'}), 500


@app.route('/api/export', methods=['POST'])
def export_model():
    """
    Export the current model as a .aim file.
    
    Expected JSON payload:
        {
            "model_name": "My Model",
            "author": "Username",
            "version": "1.0"
        }
    
    Returns:
        JSON with .aim file data
    """
    global current_model
    
    try:
        # Check if model exists
        if current_model is None:
            return jsonify({'error': 'No model to export. Please train a model first.'}), 400
        
        data = request.get_json()
        
        # Validate required fields
        if not data or 'model_name' not in data:
            return jsonify({'error': 'model_name is required'}), 400
        
        model_name = data['model_name']
        author = data.get('author', 'Anonymous')
        version = data.get('version', '1.0')
        
        # Create .aim file structure
        aim_file = {
            'model_name': model_name,
            'author': author,
            'version': version,
            'algorithm': f'Markov Chain (order {current_model.order})',
            'created_at': datetime.now().isoformat(),
            'model_data': current_model.get_model_data()
        }
        
        # Save to models directory
        filename = f"{model_name.replace(' ', '_').lower()}.aim"
        filepath = os.path.join(MODELS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(aim_file, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Model exported successfully',
            'filename': filename,
            'path': filepath,
            'aim_data': aim_file
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'}), 500


@app.route('/api/load_model', methods=['POST'])
def load_model():
    """
    Load a .aim model file.
    
    Expected JSON payload:
        {
            "aim_data": { ... }  // Complete .aim file JSON data
        }
    
    OR upload a file directly
    
    Returns:
        JSON with load status
    """
    global current_model
    
    try:
        # Try to get JSON data
        if request.is_json:
            data = request.get_json()
            
            if 'aim_data' in data:
                aim_data = data['aim_data']
            else:
                # Assume the entire payload is the .aim data
                aim_data = data
        else:
            # Try to read from uploaded file
            if 'file' not in request.files:
                return jsonify({'error': 'No .aim data or file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Read and parse the file
            aim_data = json.load(file)
        
        # Validate .aim file structure
        required_fields = ['model_name', 'author', 'version', 'algorithm', 'model_data']
        for field in required_fields:
            if field not in aim_data:
                return jsonify({'error': f'Invalid .aim file: missing {field}'}), 400
        
        # Create a new trainer and load the model data
        trainer = MarkovTrainer()
        trainer.load_model_data(aim_data['model_data'])
        current_model = trainer
        
        return jsonify({
            'success': True,
            'message': 'Model loaded successfully',
            'model_info': {
                'name': aim_data['model_name'],
                'author': aim_data['author'],
                'version': aim_data['version'],
                'algorithm': aim_data['algorithm']
            }
        }), 200
        
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON format'}), 400
    except Exception as e:
        return jsonify({'error': f'Load failed: {str(e)}'}), 500


@app.route('/api/models', methods=['GET'])
def list_models():
    """
    List all available .aim model files in the models directory.
    
    Returns:
        JSON list of model files with metadata
    """
    try:
        models = []
        
        # Scan models directory
        for filename in os.listdir(MODELS_DIR):
            if filename.endswith('.aim'):
                filepath = os.path.join(MODELS_DIR, filename)
                
                # Read model metadata
                with open(filepath, 'r', encoding='utf-8') as f:
                    aim_data = json.load(f)
                
                models.append({
                    'filename': filename,
                    'model_name': aim_data.get('model_name', 'Unknown'),
                    'author': aim_data.get('author', 'Unknown'),
                    'version': aim_data.get('version', 'Unknown'),
                    'algorithm': aim_data.get('algorithm', 'Unknown'),
                    'created_at': aim_data.get('created_at', 'Unknown')
                })
        
        return jsonify({
            'success': True,
            'models': models
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to list models: {str(e)}'}), 500


@app.route('/api/model/<filename>', methods=['GET'])
def get_model_file(filename):
    """
    Download a specific .aim model file.
    
    Args:
        filename: Name of the .aim file
        
    Returns:
        The .aim file for download
    """
    try:
        return send_from_directory(MODELS_DIR, filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': f'File not found: {str(e)}'}), 404


@app.route('/api/status', methods=['GET'])
def status():
    """
    Get the current model status.
    
    Returns:
        JSON with information about the loaded model
    """
    global current_model
    
    if current_model is None:
        return jsonify({
            'model_loaded': False,
            'message': 'No model currently loaded'
        }), 200
    
    model_data = current_model.get_model_data()
    
    return jsonify({
        'model_loaded': True,
        'order': model_data['order'],
        'vocabulary_size': model_data['vocabulary_size'],
        'transitions_count': len(model_data['transitions'])
    }), 200


# ============================================================
# AIM v3 API Endpoints
# ============================================================

@app.route('/api/v3/engines', methods=['GET'])
def get_engines():
    """
    Get list of available AIM engines.
    
    Returns:
        JSON list of supported engines
    """
    return jsonify({
        'success': True,
        'engines': list_engines(),
        'descriptions': {
            'markov': 'Statistical text generation using Markov chains',
            'ngram': 'N-gram language model for text prediction',
            'embedding': 'Vector embedding-based similarity',
            'llm': 'Large Language Model interface'
        }
    }), 200


@app.route('/api/v3/train', methods=['POST'])
def train_v3():
    """
    Train a model using AIM v3 system.
    
    Expected JSON:
        {
            "name": "Model Name",
            "author": "Your Name",
            "type": "text",
            "engine": "markov",
            "text": "training data...",
            "engine_config": { ... }
        }
    """
    global current_aim_model
    
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'text field required'}), 400
        
        # Get parameters
        name = data.get('name', 'Untitled Model')
        author = data.get('author', 'Anonymous')
        engine = data.get('engine', 'markov')
        model_type = data.get('type', 'text')
        text_data = data['text']
        engine_config = data.get('engine_config', {})
        
        # Create and train model
        model = AIMModel.create(
            name=name,
            author=author,
            engine=engine,
            model_type=model_type,
            description=data.get('description', '')
        )
        
        # Train
        stats = model.train(text_data, **engine_config)
        current_aim_model = model
        
        return jsonify({
            'success': True,
            'message': 'Model trained successfully',
            'model': str(model),
            'stats': stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v3/generate', methods=['POST'])
def generate_v3():
    """
    Generate output using v3 model.
    
    Expected JSON:
        {
            "prompt": "optional prompt",
            "max_length": 100,
            "temperature": 1.0
        }
    """
    global current_aim_model
    
    if current_aim_model is None:
        return jsonify({'error': 'No model trained or loaded'}), 400
    
    try:
        data = request.get_json() or {}
        
        output = current_aim_model.generate(
            prompt=data.get('prompt'),
            max_length=data.get('max_length', 100),
            temperature=data.get('temperature', 1.0)
        )
        
        return jsonify({
            'success': True,
            'output': output
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v3/save', methods=['POST'])
def save_v3():
    """
    Save current model as .aim file.
    
    Expected JSON:
        {
            "filename": "mymodel.aim"  # optional
        }
    """
    global current_aim_model
    
    if current_aim_model is None:
        return jsonify({'error': 'No model to save'}), 400
    
    try:
        data = request.get_json() or {}
        filepath = data.get('filename')
        
        if filepath:
            filepath = os.path.join(MODELS_DIR, filepath)
        else:
            filepath = os.path.join(MODELS_DIR, None)
        
        saved_path = current_aim_model.save(filepath)
        
        # Register in local registry
        local_registry.register(
            current_aim_model.manifest['name'],
            saved_path,
            current_aim_model.manifest.to_dict()
        )
        
        return jsonify({
            'success': True,
            'path': saved_path,
            'size_kb': os.path.getsize(saved_path) / 1024
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v3/load', methods=['POST'])
def load_v3():
    """
    Load a .aim file.
    
    Expected:
        POST with 'file' parameter (multipart form-data)
        OR JSON with 'path' field (for pre-existing .aim files)
    """
    global current_aim_model
    
    try:
        filepath = None
        
        # Try to get file from form data
        if 'file' in request.files:
            file = request.files['file']
            if file.filename:
                filepath = os.path.join(MODELS_DIR, file.filename)
                file.save(filepath)
        else:
            # Try to get path from JSON
            data = request.get_json() or {}
            if 'path' in data:
                filepath = data['path']
        
        if not filepath:
            return jsonify({'error': 'No file or path provided'}), 400
        
        # Load with AIM system
        current_aim_model = AIMModel.load(filepath)
        
        return jsonify({
            'success': True,
            'model': str(current_aim_model),
            'info': current_aim_model.info()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v3/registry/list', methods=['GET'])
def registry_list():
    """List models in local registry."""
    models = local_registry.list()
    
    result = []
    for name in models:
        info = local_registry.get(name)
        result.append({
            'name': name,
            'path': info['path'],
            'registered': info['registered']
        })
    
    return jsonify({
        'success': True,
        'models': result
    }), 200


@app.route('/api/v3/registry/search', methods=['GET'])
def registry_search():
    """
    Search public registry (aimhub.org).
    
    Query parameters:
        ?q=query&tags=tag1,tag2&limit=10
    """
    try:
        query = request.args.get('q', '')
        tags = request.args.get('tags', '').split(',') if request.args.get('tags') else []
        limit = int(request.args.get('limit', 10))
        
        client = RegistryClient('https://aimhub.org')
        results = client.search(query, tags=tags, limit=limit)
        
        return jsonify({
            'success': True,
            'results': results
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v3/plugins', methods=['GET'])
def get_plugins():
    """List all available plugins."""
    plugins = plugin_manager.list_plugins()
    
    result = []
    for name in plugins:
        try:
            info = plugin_manager.get_plugin_info(name)
            result.append(info)
        except:
            pass
    
    return jsonify({
        'success': True,
        'plugins': result
    }), 200


@app.route('/api/v3/plugins/<name>/execute', methods=['POST'])
def execute_plugin(name):
    """
    Execute a plugin.
    
    Expected JSON:
        {
            "input": "plugin input data",
            "args": { ... }
        }
    """
    try:
        data = request.get_json()
        
        if 'input' not in data:
            return jsonify({'error': 'input field required'}), 400
        
        result = plugin_manager.execute_plugin(
            name,
            data['input'],
            **data.get('args', {})
        )
        
        return jsonify({
            'success': True,
            'result': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 50)
    print("AIM Studio Backend Server")
    print("=" * 50)
    print("Starting server on http://localhost:5000")
    print("Models directory:", MODELS_DIR)
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
