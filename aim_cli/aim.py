#!/usr/bin/env python
"""
AIM CLI - Package Manager
Command-line interface for training, exporting, and managing AI models
"""

import click
import json
import os
import sys
from pathlib import Path
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from aim_core import AIMModel, AIMManifest, create_manifest, get_engine, list_engines
from aim_hub import Registry, RegistryClient
from .trainer import create_trainer


@click.group()
@click.version_option()
def cli():
    """
    🎯 AIM - AI Model Ecosystem
    
    Train, export, and manage AI models like packages.
    """
    pass


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--name', prompt='Model name', help='Name of the model')
@click.option('--author', prompt='Author name', help='Your name')
@click.option('--engine', type=click.Choice(list_engines()), default='markov', help='Engine to use')
@click.option('--order', type=int, default=2, help='Markov order (for markov engine)')
@click.option('--output', '-o', help='Output .aim file path')
@click.option('--description', prompt='Model description', default='', help='Model description')
def train(input_file: str, name: str, author: str, engine: str, order: int, output: str, description: str):
    """
    Train a new AI model from text data.
    
    INPUT_FILE: Path to training text file (.txt, .md, .csv, etc.)
    
    Example:
        aim train data.txt --name "My AI" --author "John" --engine markov
    """
    click.echo(f"📚 Training model: {name}")
    
    try:
        # Read training data
        with open(input_file, 'r', encoding='utf-8') as f:
            text_data = f.read()
        
        # Create model
        model = AIMModel.create(
            name=name,
            author=author,
            engine=engine,
            description=description,
            model_type="text"
        )
        
        # Train
        click.echo(f"🔧 Training with {engine} engine...")
        stats = model.train(text_data, order=order if engine == "markov" else None)
        
        click.echo(f"✅ Training complete!")
        click.echo(f"   Vocabulary: {stats.get('vocabulary_size', 'N/A')} words")
        click.echo(f"   States: {stats.get('transitions_count', 'N/A')}")
        
        # Save model
        if output is None:
            output = f"{name.lower().replace(' ', '_')}.aim"
        
        output_path = model.save(output)
        click.echo(f"💾 Model saved: {output_path}")
        click.echo(f"   Size: {os.path.getsize(output_path) / 1024:.1f} KB")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('model_file', type=click.Path(exists=True))
@click.option('--prompt', '-p', default='', help='Input prompt')
@click.option('--length', '-l', type=int, default=100, help='Max output length')
def run(model_file: str, prompt: str, length: int):
    """
    Run an AIM model and generate output.
    
    MODEL_FILE: Path to .aim model file
    
    Example:
        aim run mymodel.aim --prompt "Once upon a time" --length 100
    """
    click.echo(f"🚀 Loading model: {model_file}")
    
    try:
        # Load model
        model = AIMModel.load(model_file)
        click.echo(f"✅ Loaded: {model}")
        
        if prompt:
            click.echo(f"💬 Prompt: {prompt}")
        
        # Generate
        click.echo(f"🤖 Generating...\n")
        output = model.generate(prompt if prompt else None, max_length=length)
        click.echo(output)
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('model_file', type=click.Path(exists=True))
def info(model_file: str):
    """
    Display model information.
    
    MODEL_FILE: Path to .aim model file
    
    Example:
        aim info mymodel.aim
    """
    try:
        model = AIMModel.load(model_file)
        info = model.info()
        
        manifest = info['manifest']
        click.echo(f"\n📦 Model: {manifest['name']}")
        click.echo(f"   Version: {manifest['version']}")
        click.echo(f"   Author: {manifest['author']}")
        click.echo(f"   Description: {manifest['description']}")
        click.echo(f"   Engine: {manifest['engine']}")
        click.echo(f"   Type: {manifest['type']}")
        click.echo(f"   License: {manifest.get('license', 'Unknown')}")
        
        if manifest.get('tags'):
            click.echo(f"   Tags: {', '.join(manifest['tags'])}")
        
        click.echo()
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('model_name')
@click.option('--registry', default='http://localhost:8000', help='Registry URL (local server)')
def install(model_name: str, registry: str):
    """
    Install a model from AIM Hub registry.
    
    MODEL_NAME: Name of the model to install
    
    Example:
        aim install wikipedia-ai
        aim install biology-tutor
    """
    click.echo(f"📥 Installing: {model_name}")
    click.echo(f"   From: {registry}")
    
    try:
        client = RegistryClient(registry)
        model_info = client.search(model_name)
        
        if not model_info:
            click.echo(f"❌ Model not found: {model_name}", err=True)
            sys.exit(1)
        
        click.echo(f"✅ Found: {model_info['name']}")
        click.echo(f"   Author: {model_info['author']}")
        click.echo(f"   Description: {model_info['description']}")
        
        # Download
        click.echo(f"⬇️  Downloading...")
        filepath = client.download(model_name)
        
        click.echo(f"✅ Installed: {filepath}")
        click.echo(f"   Use: aim run {filepath}")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('model_file', type=click.Path(exists=True))
@click.option('--registry', default='http://localhost:8000', help='Registry URL (local server)')
@click.option('--token', prompt=True, hide_input=True, help='API token for publishing')
def publish(model_file: str, registry: str, token: str):
    """
    Publish a model to AIM Hub registry.
    
    MODEL_FILE: Path to .aim model file
    
    Example:
        aim publish mymodel.aim --token YOUR_TOKEN
    """
    click.echo(f"📤 Publishing: {model_file}")
    
    try:
        model = AIMModel.load(model_file)
        client = RegistryClient(registry, token=token)
        
        click.echo(f"📝 Model: {model.manifest['name']}")
        
        # Upload
        url = client.upload(model_file)
        
        click.echo(f"✅ Published!")
        click.echo(f"   URL: {url}")
        click.echo(f"   Install with: aim install {model.manifest['name']}")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def list_engines_cmd():
    """List all available AI engines."""
    click.echo("\n🔧 Available Engines:\n")
    
    engines = list_engines()
    for engine in engines:
        engine_info = ENGINE_DESCRIPTIONS.get(engine, "Custom engine")
        click.echo(f"  • {engine:12} - {engine_info}")
    
    click.echo()


@cli.command()
@click.option('--query', '-q', help='Search query')
@click.option('--tag', '-t', multiple=True, help='Filter by tag')
@click.option('--limit', type=int, default=10, help='Number of results')
@click.option('--registry', default='http://localhost:8000', help='Registry URL (local server)')
def search(query: str, tag: list, limit: int, registry: str):
    """
    Search for models in AIM Hub.
    
    Example:
        aim search --query "biology"
        aim search --tag "education" --tag "tutorial"
    """
    click.echo(f"🔍 Searching AIM Hub...")
    
    try:
        client = RegistryClient(registry)
        results = client.search(query or "", tags=tag, limit=limit)
        
        if not results:
            click.echo("No models found.")
            return
        
        click.echo(f"\n📦 Found {len(results)} models:\n")
        
        for model in results:
            click.echo(f"  • {model['name']}")
            click.echo(f"    Author: {model['author']}")
            click.echo(f"    {model['description'][:60]}...")
            click.echo(f"    Tags: {', '.join(model.get('tags', []))}")
            click.echo()
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


ENGINE_DESCRIPTIONS = {
    "markov": "Statistical text generation using Markov chains",
    "ngram": "N-gram language model for text prediction",
    "embedding": "Vector embedding-based similarity and generation",
    "llm": "Large Language Model interface (OpenAI, Hugging Face, etc.)"
}


if __name__ == '__main__':
    cli()
