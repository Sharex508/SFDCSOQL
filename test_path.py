"""
Test script for finding relationship paths
"""

from metadata_loader import SalesforceMetadataLoader
from nlp_model import SOQLQueryGenerator

def main():
    print("Testing relationship path finding")
    print("--------------------------------")

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

    # Test finding path from Account to QuoteLineItem
    start_obj = "Account"
    end_obj = "QuoteLineItem"
    print(f"\nFinding path from {start_obj} to {end_obj}...")
    path = query_generator._find_relationship_path(start_obj, end_obj)

    if path:
        print(f"Found path with {len(path)} steps:")
        for i, rel in enumerate(path):
            rel_type = rel.get('type', 'unknown')
            parent_obj = rel.get('parentObject', 'Unknown')
            child_obj = rel.get('childObject', 'Unknown')
            if rel_type == 'child':
                print(f"  {i+1}. {parent_obj} -> {child_obj}")
            elif rel_type == 'parent':
                print(f"  {i+1}. {child_obj} -> {parent_obj}")
    else:
        print(f"No path found from {start_obj} to {end_obj}")

    # Test finding path from Account to Order
    start_obj = "Account"
    end_obj = "Order"
    print(f"\nFinding path from {start_obj} to {end_obj}...")
    path = query_generator._find_relationship_path(start_obj, end_obj)

    if path:
        print(f"Found path with {len(path)} steps:")
        for i, rel in enumerate(path):
            rel_type = rel.get('type', 'unknown')
            parent_obj = rel.get('parentObject', 'Unknown')
            child_obj = rel.get('childObject', 'Unknown')
            if rel_type == 'child':
                print(f"  {i+1}. {parent_obj} -> {child_obj}")
            elif rel_type == 'parent':
                print(f"  {i+1}. {child_obj} -> {parent_obj}")
    else:
        print(f"No path found from {start_obj} to {end_obj}")

if __name__ == "__main__":
    main()
