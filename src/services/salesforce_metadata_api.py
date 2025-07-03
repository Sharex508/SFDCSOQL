#!/usr/bin/env python3
"""
Salesforce Metadata API Service
------------------------------
This script creates a Flask web service that exposes an API to retrieve Salesforce
metadata and generate Excel files that can be used by generate_metadata.py.

Usage:
    python salesforce_metadata_api.py --host <host> --port <port>

Example:
    python salesforce_metadata_api.py --host 0.0.0.0 --port 5000
"""

import argparse
import os
import sys
import json
import pandas as pd
import requests
import tempfile
from flask import Flask, request, jsonify, send_file
from simple_salesforce import Salesforce
from typing import Dict, List, Any, Optional
from werkzeug.utils import secure_filename

# Add the project root directory to the Python path
# This is necessary to make the absolute imports work when running the script directly
# Without this, Python would raise "ModuleNotFoundError: No module named 'src'"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import functions from salesforce_metadata_service.py
from src.services.salesforce_metadata_service import (
    salesforce_connection,
    get_all_objects,
    get_object_metadata,
    process_object_metadata,
    export_to_excel
)

# Create Flask app
app = Flask(__name__)

# Configure upload folder for temporary files
UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Salesforce Metadata API is running"})

@app.route('/api/metadata', methods=['POST'])
def get_metadata():
    """
    API endpoint to retrieve Salesforce metadata

    Expected JSON payload:
    {
        "username": "user@example.com",
        "password": "password",
        "security_token": "token",
        "client_id": "client_id",
        "client_secret": "client_secret",
        "objects": ["Account", "Contact"] // Optional, if not provided all objects will be retrieved
    }

    Returns:
        Excel file with Salesforce metadata
    """
    # Get JSON data from request
    data = request.json

    # Validate required fields
    required_fields = ['username', 'password', 'security_token', 'client_id', 'client_secret']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # Connect to Salesforce
    sf = salesforce_connection(
        username=data['username'],
        password=data['password'],
        security_token=data['security_token'],
        client_id=data['client_id'],
        client_secret=data['client_secret']
    )

    if not sf:
        return jsonify({"error": "Failed to authenticate with Salesforce"}), 401

    # Get list of objects to process
    if 'objects' in data and data['objects']:
        object_names = data['objects']
        app.logger.info(f"Processing {len(object_names)} specified objects")
    else:
        object_names = get_all_objects(sf)

    # Process each object
    all_metadata = []
    for i, object_name in enumerate(object_names):
        app.logger.info(f"[{i+1}/{len(object_names)}] Processing {object_name}...")
        metadata = get_object_metadata(sf, object_name)
        if metadata:
            formatted_metadata = process_object_metadata(object_name, metadata)
            all_metadata.extend(formatted_metadata)
            app.logger.info(f"Added {len(formatted_metadata)} fields for {object_name}")

    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    temp_file.close()

    # Export to Excel
    export_to_excel(all_metadata, temp_file.name)

    # Return the file
    return send_file(
        temp_file.name,
        as_attachment=True,
        download_name='Salesforce_Complete_Metadata.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/api/objects', methods=['POST'])
def get_objects():
    """
    API endpoint to retrieve list of Salesforce objects

    Expected JSON payload:
    {
        "username": "user@example.com",
        "password": "password",
        "security_token": "token",
        "client_id": "client_id",
        "client_secret": "client_secret"
    }

    Returns:
        JSON list of object names
    """
    # Get JSON data from request
    data = request.json

    # Validate required fields
    required_fields = ['username', 'password', 'security_token', 'client_id', 'client_secret']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # Connect to Salesforce
    sf = salesforce_connection(
        username=data['username'],
        password=data['password'],
        security_token=data['security_token'],
        client_id=data['client_id'],
        client_secret=data['client_secret']
    )

    if not sf:
        return jsonify({"error": "Failed to authenticate with Salesforce"}), 401

    # Get list of objects
    object_names = get_all_objects(sf)

    # Return the list
    return jsonify({"objects": object_names})

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Start Salesforce Metadata API service')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help='Host to bind the service to')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port to bind the service to')
    parser.add_argument('--debug', action='store_true',
                        help='Run in debug mode')
    return parser.parse_args()

def main():
    """Main function"""
    args = parse_arguments()

    print(f"Starting Salesforce Metadata API service on {args.host}:{args.port}")
    print("Available endpoints:")
    print("  GET  /health - Health check")
    print("  POST /api/metadata - Retrieve Salesforce metadata and return Excel file")
    print("  POST /api/objects - Retrieve list of Salesforce objects")

    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()
