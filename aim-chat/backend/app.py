"""
AIM Chat - Flask Backend Server
Simple chatbot API for loading knowledge models and answering questions
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from model_loader import ModelLoader
from chat_engine import ChatEngine

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Initialize components
model_loader = ModelLoader()
chat_engine = ChatEngine()


@app.route('/')
def index():
    """Serve the main frontend page"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get the current system status"""
    model_info = model_loader.get_model_info()
    stats = chat_engine.get_stats()
    
    return jsonify({
        'status': 'online',
        'model_loaded': model_loader.is_loaded(),
        'model_info': model_info,
        'stats': stats
    })


@app.route('/api/load_model', methods=['POST'])
def load_model():
    """
    Load a .aim model file
    
    Expected JSON:
    {
        "filepath": "path/to/model.aim"
    }
    OR
    {
        "model_data": { ... }  // Direct JSON model data
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Check if filepath or model_data is provided
        if 'filepath' in data:
            filepath = data['filepath']
            model_info = model_loader.load_model(filepath)
        elif 'model_data' in data:
            model_info = model_loader.load_from_json(data['model_data'])
        else:
            return jsonify({'error': 'Either filepath or model_data required'}), 400
        
        # Update chat engine with new knowledge
        knowledge = model_loader.get_knowledge()
        chat_engine.set_knowledge(knowledge)
        chat_engine.clear_history()
        
        return jsonify({
            'success': True,
            'message': f"Model '{model_info['name']}' loaded successfully",
            'model_info': model_info
        })
    
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to load model: {str(e)}'}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Process a chat message
    
    Expected JSON:
    {
        "message": "User's question"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        if not model_loader.is_loaded():
            return jsonify({'error': 'No model loaded. Please load a model first.'}), 400
        
        # Get response from chat engine
        result = chat_engine.chat(user_message)
        
        return jsonify({
            'success': True,
            'response': result['response'],
            'confidence': result['confidence']
        })
    
    except Exception as e:
        return jsonify({'error': f'Chat failed: {str(e)}'}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get the conversation history"""
    history = chat_engine.get_conversation_history()
    return jsonify({
        'history': history,
        'count': len(history)
    })


@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Clear the conversation history"""
    chat_engine.clear_history()
    return jsonify({
        'success': True,
        'message': 'Conversation history cleared'
    })


@app.route('/api/models', methods=['GET'])
def list_models():
    """List available .aim model files in the models directory"""
    try:
        models_dir = os.path.join(os.path.dirname(__file__), '../models')
        
        if not os.path.exists(models_dir):
            return jsonify({'models': []})
        
        models = []
        for filename in os.listdir(models_dir):
            if filename.endswith('.aim'):
                filepath = os.path.join(models_dir, filename)
                try:
                    import json
                    with open(filepath, 'r', encoding='utf-8') as f:
                        model_data = json.load(f)
                    models.append({
                        'filename': filename,
                        'name': model_data.get('name', 'Unknown'),
                        'version': model_data.get('version', '1.0'),
                        'type': model_data.get('type', 'chat'),
                        'description': model_data.get('description', 'No description'),
                        'knowledge_count': len(model_data.get('knowledge', []))
                    })
                except:
                    # Skip invalid files
                    continue
        
        return jsonify({'models': models})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/load_model_by_name', methods=['POST'])
def load_model_by_name():
    """
    Load a model by filename from the models directory
    
    Expected JSON:
    {
        "filename": "model.aim"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'filename' not in data:
            return jsonify({'error': 'Filename is required'}), 400
        
        filename = data['filename']
        models_dir = os.path.join(os.path.dirname(__file__), '../models')
        filepath = os.path.join(models_dir, filename)
        
        model_info = model_loader.load_model(filepath)
        
        # Update chat engine
        knowledge = model_loader.get_knowledge()
        chat_engine.set_knowledge(knowledge)
        chat_engine.clear_history()
        
        return jsonify({
            'success': True,
            'message': f"Model '{model_info['name']}' loaded successfully",
            'model_info': model_info
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 50)
    print("🚀 AIM Chat Server Starting...")
    print("=" * 50)
    print("📍 http://localhost:5000")
    print("💬 Open your browser to start chatting!")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
