"""
Debug script for the _identify_object method
"""

from metadata_loader import SalesforceMetadataLoader
from nlp_model import SOQLQueryGenerator
import re

def main():
    print("Debugging the _identify_object method")
    print("------------------------------------")

    # Set up metadata
    print("Setting up Salesforce metadata...")
    metadata_loader = SalesforceMetadataLoader()
    metadata_loader.add_sample_metadata(use_excel=False)

    # Initialize query generator
    query_generator = SOQLQueryGenerator()

    # Load objects into the query generator
    query_generator.objects = {name: metadata_loader.objects[name] 
                              for name in metadata_loader.get_object_names()}
    query_generator.fields_by_object = metadata_loader.fields_by_object
    query_generator.relationships = metadata_loader.relationships

    # Test cases
    test_cases = [
        "Show me accounts with their contacts",
        "List accounts with their opportunities",
        "Show me accounts with their quote line items",
        "List accounts with their orders",
        "Accounts with their quote line items"
    ]

    for test_case in test_cases:
        print(f"\n=== Testing: {test_case} ===")
        question = test_case
        question_lower = question.lower()
        print(f"Question: {question}")
        print(f"Question (lowercase): {question_lower}")

        # Try different patterns for "X with their Y"
        patterns = [
            r"(?:show|list|get|find|display|retrieve) (?:me )?(?:all )?(?:the )?([a-z]+)s? with (?:all )?(?:their|its) ([a-z ]+)",
            r"(?:show|list|get|find|display|retrieve) (?:me )?(?:all )?(?:the )?([a-z]+)s? with (?:their|its) ([a-z ]+)",
            r"([a-z]+)s? with (?:all )?(?:their|its) ([a-z ]+)",
            r"([a-z]+) with (?:all )?(?:their|its) ([a-z ]+)"
        ]

        for i, pattern in enumerate(patterns):
            print(f"\nPattern {i+1}: {pattern}")
            match = re.search(pattern, question_lower)
            if match:
                print(f"Match found: {match.groups()}")
                main_obj_text = match.group(1).lower()
                child_obj_text = match.group(2).strip()
                print(f"Main object text: {main_obj_text}")
                print(f"Child object text: {child_obj_text}")

                # Try to match the main object text to a valid object name
                for obj_name in query_generator.objects:
                    obj_lower = obj_name.lower()

                    # Check for exact match
                    if obj_lower == main_obj_text:
                        print(f"✓ Exact match: {obj_name}")
                        break

                    # Check for plural form (simple 's' addition)
                    if main_obj_text.endswith('s') and obj_lower == main_obj_text[:-1]:
                        print(f"✓ Plural match: {obj_name}")
                        break

                    # Check for special plural forms (e.g., 'y' -> 'ies')
                    if main_obj_text.endswith('ies') and obj_lower.endswith('y') and obj_lower[:-1] == main_obj_text[:-3]:
                        print(f"✓ Special plural match: {obj_name}")
                        break
                else:
                    print(f"✗ No matching object found for {main_obj_text}")
            else:
                print("No match found")

        # Special case for "accounts with their quote line items"
        if "accounts with their quote line items" in question_lower:
            print("\nSpecial case for 'accounts with their quote line items' matched")
        else:
            print("\nSpecial case for 'accounts with their quote line items' not matched")

        # Call the _identify_object method
        main_object = query_generator._identify_object(question)
        print(f"\nIdentified main object: {main_object}")
        print(f"Last identified parent: {query_generator._last_identified_parent}")
        print(f"Last identified child text: {query_generator._last_identified_child_text}")

        # Reset the variables for the next test case
        query_generator._last_identified_parent = None
        query_generator._last_identified_child_text = None

if __name__ == "__main__":
    main()
