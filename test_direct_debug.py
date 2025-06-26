"""
Debug script for directly calling the _identify_relationship method
"""

from metadata_loader import SalesforceMetadataLoader
from nlp_model import SOQLQueryGenerator

def main():
    print("Debugging direct call to _identify_relationship")
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
    print("\nTesting direct call with 'quote line items and orders'")
    
    # Set up the parent and child text
    query_generator._last_identified_parent = "Account"
    query_generator._last_identified_child_text = "quote line items and orders"
    
    # Print the parent and child text
    print(f"Last identified parent: {query_generator._last_identified_parent}")
    print(f"Last identified child text: {query_generator._last_identified_child_text}")
    
    # Create the question
    question = "List accounts with their quote line items and orders"
    print(f"Question: '{question}'")
    
    # Check if our special case pattern matches
    import re
    if "quote line items and orders" in question.lower():
        print("Simple pattern 'quote line items and orders' matched")
    else:
        print("Simple pattern 'quote line items and orders' not matched")
        
    if "accounts with their quote line items and orders" in question.lower():
        print("Pattern 'accounts with their quote line items and orders' matched")
    else:
        print("Pattern 'accounts with their quote line items and orders' not matched")
    
    # Call the _identify_relationship method
    relationships = query_generator._identify_relationship(question)
    
    # Print the relationships
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
    
    # Generate query
    query = query_generator.generate_query(question)
    print(f"\nGenerated SOQL Query: {query}")
    
    # Check if the query includes the expected objects (case-insensitive)
    query_lower = query.lower()
    
    has_quote_line_items = "quotelineitems" in query_lower
    print(f"Query includes QuoteLineItems: {has_quote_line_items}")
    
    has_orders = "orders" in query_lower
    print(f"Query includes Orders: {has_orders}")

if __name__ == "__main__":
    main()