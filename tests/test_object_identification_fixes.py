"""
Test Object Identification Fixes
-------------------------------
This script tests the object identification fixes for the problematic prompts
mentioned in the issue description.
"""

import os
from src.utils.metadata_loader import SalesforceMetadataLoader
from src.utils.nlp_model import SOQLQueryGenerator

def initialize_query_generator():
    """
    Initialize the SOQL Query Generator with metadata.

    Returns:
        An initialized SOQLQueryGenerator instance
    """
    # Set up metadata
    print("Setting up Salesforce metadata...")
    metadata_loader = SalesforceMetadataLoader()
    metadata_loader.add_sample_metadata()

    # Initialize query generator
    query_generator = SOQLQueryGenerator()

    # Load objects into the query generator
    query_generator.objects = {name: metadata_loader.objects[name] 
                              for name in metadata_loader.get_object_names()}
    query_generator.fields_by_object = metadata_loader.fields_by_object
    query_generator.relationships = metadata_loader.relationships

    return query_generator

def test_object_identification(query_generator, prompt, expected_object):
    """
    Test if the model correctly identifies the object for a given prompt.

    Args:
        query_generator: The initialized SOQLQueryGenerator instance
        prompt: The prompt to test
        expected_object: The expected object to be identified

    Returns:
        True if the identified object matches the expected object, False otherwise
    """
    print(f"\nTesting prompt: \"{prompt}\"")
    print(f"Expected object: {expected_object}")

    # Check which model handles this prompt
    handling_model = None
    handling_model_instance = None
    if query_generator.use_modular_architecture:
        for model in query_generator.model_dispatcher.models:
            if model.can_handle(prompt):
                handling_model = model.__class__.__name__
                handling_model_instance = model
                break
        if handling_model:
            print(f"Handling model: {handling_model}")

    # Identify the object
    identified_object = None
    if handling_model_instance:
        identified_object = handling_model_instance._identify_object(prompt)
    else:
        # If no specific model handles it, use the base identification logic
        identified_object = query_generator._identify_object(prompt)

    print(f"Identified object: {identified_object}")

    # Check if the identified object matches the expected object
    is_match = identified_object == expected_object
    print(f"Match: {'✅' if is_match else '❌'}")

    return is_match

def main():
    print("Test Object Identification Fixes")
    print("-------------------------------")

    # Initialize query generator
    query_generator = initialize_query_generator()

    # Define the problematic prompts and their expected objects
    problematic_prompts = [
        # Cases where Identified Object was "None"
        ("Get all Account IDs and Names.", "Account"),
        ("Get Accounts with their related Contacts.", "Account"),
        ("Get Contacts with their related Account Names.", "Contact"),
        ("Get Account Names with their Owner Names.", "Account"),
        ("Get Opportunities with their related Tasks.", "Opportunity"),
        ("Get Accounts with their Orders.", "Account"),
        ("Count all Accounts.", "Account"),
        ("Get average AnnualRevenue grouped by Type.", "Account"),
        ("Count Leads grouped by LeadSource.", "Lead"),
        ("Count Cases grouped by year.", "Case"),
        ("Count Opportunities grouped by AccountId.", "Opportunity"),

        # Cases where Identified Object was Incorrect
        ("Get quotelines with related quote Name and Subject.", "Case")
    ]

    # Test each prompt
    results = []
    for prompt, expected_object in problematic_prompts:
        is_match = test_object_identification(query_generator, prompt, expected_object)
        results.append((prompt, expected_object, is_match))

    # Summarize results
    print("\n=== SUMMARY ===")
    print(f"Total prompts tested: {len(results)}")
    matches = sum(1 for _, _, is_match in results if is_match)
    print(f"Correct identifications: {matches}/{len(results)} ({matches/len(results)*100:.1f}%)")

    # List failed prompts
    if matches < len(results):
        print("\nFailed prompts:")
        for prompt, expected_object, is_match in results:
            if not is_match:
                print(f"- \"{prompt}\" (Expected: {expected_object})")

if __name__ == "__main__":
    main()