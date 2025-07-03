"""
SOQL Query Generator
-------------------
This application uses natural language processing to convert user questions
into Salesforce Object Query Language (SOQL) queries.
"""

import os
import json
import argparse
from typing import Dict, List, Optional, Any

from src.utils.metadata_loader import SalesforceMetadataLoader
from src.utils.nlp_model import SOQLQueryGenerator

def setup_sample_data():
    """Set up sample metadata for demonstration purposes"""
    print("Setting up sample Salesforce metadata...")
    metadata_loader = SalesforceMetadataLoader()
    metadata_loader.add_sample_metadata()
    print("Sample metadata setup complete.")
    return metadata_loader

def interactive_mode(query_generator: SOQLQueryGenerator):
    """Run the application in interactive mode"""
    print("\n=== SOQL Query Generator ===")
    print("Type 'exit' or 'quit' to end the session")
    print("Type 'help' for assistance")

    while True:
        try:
            question = input("\nEnter your question: ")

            if question.lower() in ['exit', 'quit']:
                print("Exiting...")
                break

            if question.lower() == 'help':
                print("\nExample questions:")
                print("- Show me all accounts")
                print("- Find contacts with email addresses")
                print("- Get the top 5 opportunities by amount")
                print("- List accounts in the technology industry")
                continue

            if not question.strip():
                print("Please enter a question.")
                continue

            # Generate SOQL query
            query = query_generator.generate_query(question)

            print("\nGenerated SOQL Query:")
            print(query)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

def process_single_question(query_generator: SOQLQueryGenerator, question: str):
    """Process a single question and return the SOQL query"""
    query = query_generator.generate_query(question)
    print(f"Question: {question}")
    print(f"Generated SOQL Query: {query}")
    return query

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='SOQL Query Generator')
    parser.add_argument('--question', '-q', type=str, help='Question to convert to SOQL')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
    args = parser.parse_args()

    # Set up metadata
    metadata_loader = setup_sample_data()

    # Initialize query generator
    query_generator = SOQLQueryGenerator(
        metadata_path=metadata_loader.metadata_dir,
        soql_docs_path="data/soql_docs"
    )

    # Load objects into the query generator
    query_generator.objects = {name: metadata_loader.objects[name] 
                              for name in metadata_loader.get_object_names()}
    query_generator.fields_by_object = metadata_loader.fields_by_object
    query_generator.relationships = metadata_loader.relationships

    # Process based on arguments
    if args.interactive or not args.question:
        interactive_mode(query_generator)
    else:
        process_single_question(query_generator, args.question)

if __name__ == "__main__":
    main()
