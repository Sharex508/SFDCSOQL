#!/usr/bin/env python3
"""
Salesforce Metadata Service
--------------------------
This script connects to Salesforce using simple-salesforce, retrieves metadata
for all objects, and exports it to an Excel file that can be used by generate_metadata.py.

Usage:
    python salesforce_metadata_service.py --username <username> --password <password> --security-token <token> --client-id <client_id> --client-secret <client_secret> --output-file <output_file>

Example:
    python salesforce_metadata_service.py --username user@example.com --password mypassword --security-token mytoken --client-id myclientid --client-secret myclientsecret --output-file Salesforce_Complete_Metadata.xlsx
"""

import argparse
import os
import pandas as pd
import requests
from simple_salesforce import Salesforce
from typing import Dict, List, Any, Optional

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Retrieve Salesforce metadata and export to Excel')
    parser.add_argument('--username', '-u', type=str, required=True,
                        help='Salesforce username')
    parser.add_argument('--password', '-p', type=str, required=True,
                        help='Salesforce password')
    parser.add_argument('--security-token', '-t', type=str, required=True,
                        help='Salesforce security token')
    parser.add_argument('--client-id', '-i', type=str, required=True,
                        help='Salesforce connected app client ID')
    parser.add_argument('--client-secret', '-s', type=str, required=True,
                        help='Salesforce connected app client secret')
    parser.add_argument('--output-file', '-o', type=str, default="Salesforce_Complete_Metadata.xlsx",
                        help='Path to the output Excel file')
    parser.add_argument('--objects', type=str, nargs='+',
                        help='Specific Salesforce objects to retrieve (default: all)')
    return parser.parse_args()

def salesforce_connection(username: str, password: str, security_token: str, client_id: str, client_secret: str) -> Optional[Salesforce]:
    """
    Connect to Salesforce using OAuth 2.0
    
    Args:
        username: Salesforce username
        password: Salesforce password
        security_token: Salesforce security token
        client_id: Connected app client ID
        client_secret: Connected app client secret
        
    Returns:
        Salesforce connection object or None if authentication fails
    """
    # Authenticate with Salesforce
    auth_url = "https://login.salesforce.com/services/oauth2/token"
    data = {
        "grant_type": "password",
        "client_id": client_id,
        "client_secret": client_secret,
        "username": username,
        "password": password + security_token
    }

    print("Authenticating with Salesforce...")
    response = requests.post(auth_url, data=data)
    response_data = response.json()

    if "access_token" not in response_data:
        print("❌ Authentication failed:", response_data)
        return None

    access_token = response_data["access_token"]
    instance_url = response_data["instance_url"]
    print(f"✓ Authentication successful. Connected to {instance_url}")
    
    return Salesforce(instance_url=instance_url, session_id=access_token)

def get_all_objects(sf: Salesforce) -> List[str]:
    """
    Get a list of all available Salesforce objects
    
    Args:
        sf: Salesforce connection object
        
    Returns:
        List of object names
    """
    # Get global describe to list all objects
    print("Retrieving list of Salesforce objects...")
    global_describe = sf.describe()
    
    # Extract object names
    object_names = [obj['name'] for obj in global_describe['sobjects'] if obj['queryable']]
    print(f"Found {len(object_names)} queryable objects")
    
    return object_names

def get_object_metadata(sf: Salesforce, object_name: str) -> Dict[str, Any]:
    """
    Get metadata for a specific Salesforce object
    
    Args:
        sf: Salesforce connection object
        object_name: Name of the Salesforce object
        
    Returns:
        Object metadata dictionary
    """
    try:
        # Get the object by dynamically accessing it through the sf object
        obj = getattr(sf, object_name)
        metadata = obj.describe()
        return metadata
    except Exception as e:
        print(f"❌ Error retrieving metadata for {object_name}: {str(e)}")
        return {}

def process_object_metadata(object_name: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Process object metadata into a format suitable for the Excel file
    
    Args:
        object_name: Name of the Salesforce object
        metadata: Object metadata dictionary
        
    Returns:
        List of dictionaries with field information
    """
    formatted_fields = []
    
    for field in metadata.get('fields', []):
        formatted_fields.append({
            "CustomObject": object_name,
            "CustomField": field.get('name', ''),
            "Field Type": field.get('type', ''),
            "Lookup Object": ", ".join(field.get('referenceTo', [])) if field.get('type') == 'reference' else ""
        })
    
    return formatted_fields

def export_to_excel(metadata_list: List[Dict[str, Any]], output_file: str):
    """
    Export metadata to Excel file
    
    Args:
        metadata_list: List of dictionaries with field information
        output_file: Path to the output Excel file
    """
    # Convert to DataFrame
    df = pd.DataFrame(metadata_list)
    
    # Save to Excel
    print(f"Saving metadata to {output_file}...")
    df.to_excel(output_file, index=False)
    print(f"✓ Metadata saved to {output_file}")

def main():
    """Main function"""
    args = parse_arguments()
    
    # Connect to Salesforce
    sf = salesforce_connection(
        username=args.username,
        password=args.password,
        security_token=args.security_token,
        client_id=args.client_id,
        client_secret=args.client_secret
    )
    
    if not sf:
        return
    
    # Get list of objects to process
    if args.objects:
        object_names = args.objects
        print(f"Processing {len(object_names)} specified objects")
    else:
        object_names = get_all_objects(sf)
    
    # Process each object
    all_metadata = []
    for i, object_name in enumerate(object_names):
        print(f"[{i+1}/{len(object_names)}] Processing {object_name}...")
        metadata = get_object_metadata(sf, object_name)
        if metadata:
            formatted_metadata = process_object_metadata(object_name, metadata)
            all_metadata.extend(formatted_metadata)
            print(f"✓ Added {len(formatted_metadata)} fields for {object_name}")
    
    # Export to Excel
    export_to_excel(all_metadata, args.output_file)
    
    print(f"\nSummary:")
    print(f"- Processed {len(object_names)} objects")
    print(f"- Exported {len(all_metadata)} fields")
    print(f"- Output file: {args.output_file}")
    print("\nYou can now use this file with generate_metadata.py:")
    print(f"python generate_metadata.py --excel-file {args.output_file}")

if __name__ == "__main__":
    main()