"""
Debug script for the question being passed to _identify_relationship
"""

from metadata_loader import SalesforceMetadataLoader
from nlp_model import SOQLQueryGenerator

def main():
    print("Debugging the question being passed to _identify_relationship")
    print("----------------------------------------------------------")

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

    # Test case
    question = "List accounts with their quote line items and orders"
    print(f"Question: '{question}'")
    print(f"Question (lowercase): '{question.lower()}'")

    # Check if our pattern matches
    import re
    patterns = [
        r"(?:list|show|get|find|display|retrieve) (?:all )?(?:quote line items|quotelineitems)(?:,? (?:and )?(?:orders|order))?(?:,? (?:and )?(?:order line items|orderlineitems))? (?:of|from) (?:an |a |the )?accounts?",
        r"(?:list|show|get|find|display|retrieve) (?:all )?(?:orders|order)(?:,? (?:and )?(?:quote line items|quotelineitems))?(?:,? (?:and )?(?:order line items|orderlineitems))? (?:of|from) (?:an |a |the )?accounts?",
        r"(?:list|show|get|find|display|retrieve) (?:all )?(?:order line items|orderlineitems)(?:,? (?:and )?(?:quote line items|quotelineitems))?(?:,? (?:and )?(?:orders|order))? (?:of|from) (?:an |a |the )?accounts?"
    ]

    for i, pattern in enumerate(patterns):
        print(f"\nPattern {i+1}: {pattern}")
        match = re.search(pattern, question.lower())
        if match:
            print(f"Match found: {match.group()}")
        else:
            print("No match found")

    # Check if our simple patterns match
    simple_patterns = [
        "quote line items and orders",
        "orders and quote line items"
    ]

    for i, pattern in enumerate(simple_patterns):
        print(f"\nSimple pattern {i+1}: {pattern}")
        if pattern in question.lower():
            print(f"Match found: {pattern}")
        else:
            print("No match found")

    # Check if the question contains "accounts with their quote line items and orders"
    if "accounts with their quote line items and orders" in question.lower():
        print("\nMatch found for 'accounts with their quote line items and orders'")
    else:
        print("\nNo match found for 'accounts with their quote line items and orders'")

    # Call the _identify_relationship method
    relationships = query_generator._identify_relationship(question)
    if relationships:
        print(f"\nIdentified relationships: {len(relationships)}")
        for i, relationship in enumerate(relationships):
            print(f"  Relationship {i+1}:")
            print(f"  - Parent object: {relationship['parent_object']}")
            print(f"  - Child object: {relationship['child_object']}")
            print(f"  - Query direction: {relationship.get('query_direction', 'Not specified')}")
            print(f"  - Indirect: {relationship.get('indirect', False)}")
    else:
        print("\nNo relationships identified")

if __name__ == "__main__":
    main()