#!/usr/bin/env python3
"""
Metadata Generator Script
------------------------
This script generates Salesforce metadata files from an Excel file containing
object and field definitions. It creates JSON files for each Salesforce object
with field and relationship information.

Usage:
    python generate_metadata.py --excel-file <path_to_excel_file> --output-dir <output_directory>

Example:
    python generate_metadata.py --excel-file Salesforce_Complete_Metadata.xlsx --output-dir data/metadata
"""

import os
import sys
import argparse

# Add the project root directory to the Python path
# This is necessary to make the absolute imports work when running the script directly
# Without this, Python would raise "ModuleNotFoundError: No module named 'src'"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.metadata_loader import SalesforceMetadataLoader

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Generate Salesforce metadata files from Excel')
    parser.add_argument('--excel-file', '-e', type=str, default="Salesforce_Complete_Metadata.xlsx",
                        help='Path to the Excel file containing Salesforce metadata')
    parser.add_argument('--output-dir', '-o', type=str, default="data/metadata",
                        help='Directory where metadata files will be saved')
    return parser.parse_args()

def generate_metadata(excel_file, output_dir):
    """
    Generate metadata files from Excel file

    Args:
        excel_file: Path to the Excel file containing Salesforce metadata
        output_dir: Directory where metadata files will be saved
    """
    print(f"Generating metadata files from {excel_file} to {output_dir}")

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created output directory at {output_dir}")

    # Initialize metadata loader with the specified output directory
    metadata_loader = SalesforceMetadataLoader(metadata_dir=output_dir)

    # Load metadata from Excel file
    success = metadata_loader.load_excel_metadata(excel_path=excel_file)

    if success:
        print(f"Successfully generated metadata files for {len(metadata_loader.get_object_names())} objects")
        print(f"Metadata files are saved in {output_dir}")
        print("\nGenerated objects:")
        for obj_name in metadata_loader.get_object_names():
            print(f"- {obj_name} ({len(metadata_loader.get_object_fields(obj_name))} fields, "
                  f"{len(metadata_loader.get_object_relationships(obj_name))} relationships)")
    else:
        print("Failed to generate metadata files")

def main():
    """Main function"""
    args = parse_arguments()
    generate_metadata(args.excel_file, args.output_dir)

if __name__ == "__main__":
    main()
