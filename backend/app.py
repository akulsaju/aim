"""
AIM Studio - Flask Backend API
This is the main Flask application that provides REST API endpoints
for training models, generating text, and managing .aim model files.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime

from trainer import MarkovTrainer, train_model
from generator import MarkovGenerator, generate_text


# Initialize Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)  # Enable CORS for frontend communication

# Configure paths
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

# Store the current model in memory
current_model = None


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


if __name__ == '__main__':
    print("=" * 50)
    print("AIM Studio Backend Server")
    print("=" * 50)
    print("Starting server on http://localhost:5000")
    print("Models directory:", MODELS_DIR)
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
