"""
Test script for directly calling the _identify_relationship method
"""

from metadata_loader import SalesforceMetadataLoader
from nlp_model import SOQLQueryGenerator

def main():
    print("Testing direct call to _identify_relationship")
    print("-------------------------------------------")

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
    print("\nTesting direct call with 'orders'")
    
    # Set up the parent and child text
    query_generator._last_identified_parent = "Account"
    query_generator._last_identified_child_text = "orders"
    
    # Call the _identify_relationship method
    relationships = query_generator._identify_relationship("List accounts with their orders")
    if relationships:
        print(f"Identified relationships: {len(relationships)}")
        for i, relationship in enumerate(relationships):
            print(f"  Relationship {i+1}:")
            print(f"  - Parent object: {relationship['parent_object']}")
            print(f"  - Child object: {relationship['child_object']}")
            print(f"  - Query direction: {relationship.get('query_direction', 'Not specified')}")
            print(f"  - Indirect: {relationship.get('indirect', False)}")
            
            # Print relationship path if it exists
            if 'relationship_path' in relationship:
                print(f"  - Relationship path:")
                for j, rel in enumerate(relationship['relationship_path']):
                    rel_type = rel.get('type', 'unknown')
                    if rel_type == 'child':
                        print(f"    {j+1}. {rel.get('parentObject', 'Unknown')} -> {rel.get('childObject', 'Unknown')}")
                    elif rel_type == 'parent':
                        print(f"    {j+1}. {rel.get('childObject', 'Unknown')} -> {rel.get('parentObject', 'Unknown')}")
    else:
        print("No relationships identified")
    
    # Reset the variables
    query_generator._last_identified_parent = None
    query_generator._last_identified_child_text = None

    # Test case
    print("\nTesting direct call with 'quote line items and orders'")
    
    # Set up the parent and child text
    query_generator._last_identified_parent = "Account"
    query_generator._last_identified_child_text = "quote line items and orders"
    
    # Call the _identify_relationship method
    relationships = query_generator._identify_relationship("List accounts with their quote line items and orders")
    if relationships:
        print(f"Identified relationships: {len(relationships)}")
        for i, relationship in enumerate(relationships):
            print(f"  Relationship {i+1}:")
            print(f"  - Parent object: {relationship['parent_object']}")
            print(f"  - Child object: {relationship['child_object']}")
            print(f"  - Query direction: {relationship.get('query_direction', 'Not specified')}")
            print(f"  - Indirect: {relationship.get('indirect', False)}")
            
            # Print relationship path if it exists
            if 'relationship_path' in relationship:
                print(f"  - Relationship path:")
                for j, rel in enumerate(relationship['relationship_path']):
                    rel_type = rel.get('type', 'unknown')
                    if rel_type == 'child':
                        print(f"    {j+1}. {rel.get('parentObject', 'Unknown')} -> {rel.get('childObject', 'Unknown')}")
                    elif rel_type == 'parent':
                        print(f"    {j+1}. {rel.get('childObject', 'Unknown')} -> {rel.get('parentObject', 'Unknown')}")
    else:
        print("No relationships identified")

if __name__ == "__main__":
    main()