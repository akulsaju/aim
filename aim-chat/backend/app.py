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
from scraper import WebScraper

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Initialize components
model_loader = ModelLoader()
chat_engine = ChatEngine()
web_scraper = WebScraper()


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


@app.route('/api/add_knowledge', methods=['POST'])
def add_knowledge():
    """
    Add new knowledge sentences to the current model
    
    Expected JSON:
    {
        "knowledge": ["New sentence 1", "New sentence 2"]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'knowledge' not in data:
            return jsonify({'error': 'Knowledge array is required'}), 400
        
        if not model_loader.is_loaded():
            return jsonify({'error': 'No model loaded. Create a new model first.'}), 400
        
        new_knowledge = data['knowledge']
        
        if not isinstance(new_knowledge, list):
            return jsonify({'error': 'Knowledge must be an array of sentences'}), 400
        
        # Filter empty sentences
        new_knowledge = [k.strip() for k in new_knowledge if k.strip()]
        
        if not new_knowledge:
            return jsonify({'error': 'No valid knowledge sentences provided'}), 400
        
        # Add to current model
        current_knowledge = model_loader.get_knowledge()
        current_knowledge.extend(new_knowledge)
        
        # Update chat engine
        chat_engine.set_knowledge(current_knowledge)
        
        return jsonify({
            'success': True,
            'message': f'Added {len(new_knowledge)} knowledge sentences',
            'total_knowledge': len(current_knowledge)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/create_model', methods=['POST'])
def create_model():
    """
    Create a new model from scratch
    
    Expected JSON:
    {
        "name": "ModelName",
        "version": "1.0",
        "description": "Description",
        "knowledge": ["Sentence 1", "Sentence 2"]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required = ['name', 'knowledge']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create model data
        model_data = {
            'name': data['name'],
            'version': data.get('version', '1.0'),
            'type': 'chat',
            'description': data.get('description', 'Custom knowledge model'),
            'knowledge': [k.strip() for k in data['knowledge'] if k.strip()]
        }
        
        if len(model_data['knowledge']) == 0:
            return jsonify({'error': 'At least one knowledge sentence required'}), 400
        
        # Load the model
        model_info = model_loader.load_from_json(model_data)
        
        # Update chat engine
        knowledge = model_loader.get_knowledge()
        chat_engine.set_knowledge(knowledge)
        chat_engine.clear_history()
        
        return jsonify({
            'success': True,
            'message': f"Model '{model_info['name']}' created successfully",
            'model_info': model_info
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/save_model', methods=['POST'])
def save_model():
    """
    Save the current model to a .aim file
    
    Expected JSON:
    {
        "filename": "mymodel.aim"  (optional, auto-generated if not provided)
    }
    """
    try:
        if not model_loader.is_loaded():
            return jsonify({'error': 'No model loaded'}), 400
        
        data = request.get_json() or {}
        model_info = model_loader.get_model_info()
        
        # Generate filename
        if 'filename' in data and data['filename']:
            filename = data['filename']
            if not filename.endswith('.aim'):
                filename += '.aim'
        else:
            # Auto-generate from model name
            import re
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', model_info['name'].lower())
            filename = f"{safe_name}.aim"
        
        # Prepare model data
        model_data = {
            'name': model_loader.current_model['name'],
            'version': model_loader.current_model['version'],
            'type': model_loader.current_model['type'],
            'description': model_loader.current_model.get('description', 'No description'),
            'knowledge': model_loader.get_knowledge()
        }
        
        # Save to models directory
        models_dir = os.path.join(os.path.dirname(__file__), '../models')
        os.makedirs(models_dir, exist_ok=True)
        
        filepath = os.path.join(models_dir, filename)
        
        import json
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(model_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': f'Model saved as {filename}',
            'filename': filename,
            'filepath': filepath
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/get_knowledge', methods=['GET'])
def get_knowledge():
    """
    Get all knowledge sentences from the current model
    """
    try:
        if not model_loader.is_loaded():
            return jsonify({'error': 'No model loaded'}), 400
        
        knowledge = model_loader.get_knowledge()
        
        return jsonify({
            'knowledge': knowledge,
            'count': len(knowledge)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/scrape', methods=['POST'])
def scrape_website():
    """
    Scrape a website and convert to AIM knowledge
    
    Expected JSON:
    {
        "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
        "model_name": "PythonAI",  // Optional
        "save": true  // Optional - save as file
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url'].strip()
        model_name = data.get('model_name', '').strip()
        should_save = data.get('save', False)
        
        if not url:
            return jsonify({'error': 'URL cannot be empty'}), 400
        
        # Scrape the website
        scraped_data = web_scraper.scrape_url(url)
        
        # If save is requested, save as .aim file
        if should_save:
            models_dir = os.path.join(os.path.dirname(__file__), '../models')
            os.makedirs(models_dir, exist_ok=True)
            
            # Generate filename
            safe_name = model_name or scraped_data['title']
            safe_name = safe_name.replace(' ', '_').replace('/', '_')[:50]
            filename = f"{safe_name}.aim"
            filepath = os.path.join(models_dir, filename)
            
            # Save the file
            save_info = web_scraper.save_as_aim(scraped_data, filepath, model_name)
            
            return jsonify({
                'success': True,
                'message': f'Scraped and saved {len(scraped_data["sentences"])} sentences',
                'data': scraped_data,
                'file': save_info
            })
        else:
            # Just return the data without saving
            return jsonify({
                'success': True,
                'message': f'Scraped {len(scraped_data["sentences"])} sentences',
                'data': scraped_data
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/scrape_and_load', methods=['POST'])
def scrape_and_load():
    """
    Scrape a website and immediately load it as the current model
    
    Expected JSON:
    {
        "url": "https://en.wikipedia.org/wiki/Artificial_intelligence"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url'].strip()
        
        if not url:
            return jsonify({'error': 'URL cannot be empty'}), 400
        
        # Scrape the website
        scraped_data = web_scraper.scrape_url(url)
        
        # Create model structure
        model_data = {
            "name": scraped_data['title'],
            "version": "1.0",
            "type": "chat",
            "description": scraped_data['description'],
            "knowledge": scraped_data['sentences']
        }
        
        # Load into model loader
        model_info = model_loader.load_from_json(model_data)
        
        # Update chat engine
        knowledge = model_loader.get_knowledge()
        chat_engine.set_knowledge(knowledge)
        chat_engine.clear_history()
        
        return jsonify({
            'success': True,
            'message': f'Scraped and loaded {len(scraped_data["sentences"])} sentences',
            'model_info': model_info,
            'source': scraped_data['source'],
            'url': url
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
