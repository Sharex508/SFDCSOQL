#!/usr/bin/env python3
"""
Salesforce Prompt Service
------------------------
This script creates a Flask web service that exposes an API to receive natural language
prompts from Salesforce and generate SOQL queries using the SOQLQueryGenerator.

Usage:
    python salesforce_prompt_service.py --host <host> --port <port> --metadata-dir <metadata_dir>

Example:
    python salesforce_prompt_service.py --host 0.0.0.0 --port 5000 --metadata-dir data/metadata
"""

import argparse
import os
import sys
import json
import logging
from flask import Flask, request, jsonify
from typing import Dict, Any, Optional

# Add the project root directory to the Python path
# This is necessary to make the absolute imports work when running the script directly
# Without this, Python would raise "ModuleNotFoundError: No module named 'src'"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the SOQLQueryGenerator
from src.utils.nlp_model import SOQLQueryGenerator

# Create Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variable to store the query generator
query_generator = None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "message": "Salesforce Prompt Service is running",
        "metadata_loaded": query_generator is not None
    })

@app.route('/api/generate-query', methods=['POST'])
def generate_query():
    """
    API endpoint to generate a SOQL query from a natural language prompt

    Expected JSON payload:
    {
        "prompt": "Get all Accounts with Name and Industry"
    }

    Returns:
        JSON with the generated SOQL query
    """
    # Get JSON data from request
    data = request.json

    # Validate required fields
    if 'prompt' not in data:
        return jsonify({"error": "Missing required field: prompt"}), 400

    prompt = data['prompt']
    logger.info(f"Received prompt: {prompt}")

    # Check if query generator is initialized
    if query_generator is None:
        return jsonify({"error": "Query generator not initialized. Metadata may not be loaded."}), 500

    try:
        # Generate the query
        query = query_generator.generate_query(prompt)
        logger.info(f"Generated query: {query}")

        return jsonify({
            "prompt": prompt,
            "query": query
        })
    except Exception as e:
        logger.error(f"Error generating query: {str(e)}")
        return jsonify({"error": f"Failed to generate query: {str(e)}"}), 500

@app.route('/api/batch-generate', methods=['POST'])
def batch_generate():
    """
    API endpoint to generate multiple SOQL queries from a list of prompts

    Expected JSON payload:
    {
        "prompts": [
            "Get all Accounts with Name and Industry",
            "Find Contacts in California"
        ]
    }

    Returns:
        JSON with the generated SOQL queries
    """
    # Get JSON data from request
    data = request.json

    # Validate required fields
    if 'prompts' not in data or not isinstance(data['prompts'], list):
        return jsonify({"error": "Missing or invalid required field: prompts (must be a list)"}), 400

    prompts = data['prompts']
    logger.info(f"Received batch of {len(prompts)} prompts")

    # Check if query generator is initialized
    if query_generator is None:
        return jsonify({"error": "Query generator not initialized. Metadata may not be loaded."}), 500

    results = []
    errors = []

    # Process each prompt
    for i, prompt in enumerate(prompts):
        try:
            # Generate the query
            query = query_generator.generate_query(prompt)
            results.append({
                "prompt": prompt,
                "query": query
            })
        except Exception as e:
            logger.error(f"Error generating query for prompt {i}: {str(e)}")
            errors.append({
                "prompt": prompt,
                "error": str(e)
            })

    return jsonify({
        "results": results,
        "errors": errors,
        "total": len(prompts),
        "successful": len(results),
        "failed": len(errors)
    })

def initialize_query_generator(metadata_dir: str):
    """
    Initialize the SOQLQueryGenerator with the specified metadata directory

    Args:
        metadata_dir: Path to the directory containing metadata files

    Returns:
        True if initialization was successful, False otherwise
    """
    global query_generator

    try:
        logger.info(f"Initializing query generator with metadata from {metadata_dir}")
        query_generator = SOQLQueryGenerator(metadata_path=metadata_dir)
        logger.info("Query generator initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize query generator: {str(e)}")
        return False

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Start Salesforce Prompt Service')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help='Host to bind the service to')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port to bind the service to')
    parser.add_argument('--metadata-dir', type=str, default='data/metadata',
                        help='Directory containing metadata files')
    parser.add_argument('--debug', action='store_true',
                        help='Run in debug mode')
    return parser.parse_args()

def main():
    """Main function"""
    args = parse_arguments()

    # Initialize the query generator
    if not initialize_query_generator(args.metadata_dir):
        logger.error("Failed to initialize query generator. Exiting.")
        return

    print(f"Starting Salesforce Prompt Service on {args.host}:{args.port}")
    print(f"Using metadata from {args.metadata_dir}")
    print("Available endpoints:")
    print("  GET  /health - Health check")
    print("  POST /api/generate-query - Generate a SOQL query from a prompt")
    print("  POST /api/batch-generate - Generate multiple SOQL queries from a list of prompts")

    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()
