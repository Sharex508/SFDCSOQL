"""
Test script for parent-child relationship patterns in SOQL Query Generator
"""

from metadata_loader import SalesforceMetadataLoader
from nlp_model import SOQLQueryGenerator

def main():
    print("Testing parent-child relationship patterns in SOQL Query Generator")
    print("--------------------------------------------------------------")

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

    # Test cases for parent-child relationship patterns
    test_cases = [
        # Direct parent-child relationships
        "Show me accounts with their contacts",
        "List accounts with their opportunities",
        "Get accounts with all their contacts",
        
        # Indirect parent-child relationships
        "Show me accounts with their quote line items",
        "List accounts with their orders",
        "Get accounts with all their order line items",
        
        # Multiple relationships
        "Show me accounts with their contacts and opportunities",
        "List accounts with their quote line items and orders",
        
        # Different wording
        "Accounts with their contacts",
        "Accounts with their quote line items"
    ]

    for i, question in enumerate(test_cases):
        print(f"\nTest Case {i+1}: {question}")
        
        # Identify the main object
        main_object = query_generator._identify_object(question)
        print(f"Identified main object: {main_object}")
        
        # Check if the main object is correctly identified as Account
        if main_object == "Account":
            print("✓ Main object correctly identified as Account")
        else:
            print(f"✗ Main object incorrectly identified as {main_object}, should be Account")
        
        # Check if the last identified parent and child text are set correctly
        print(f"Last identified parent: {query_generator._last_identified_parent}")
        print(f"Last identified child text: {query_generator._last_identified_child_text}")
        
        # Identify relationships
        relationships = query_generator._identify_relationship(question)
        if relationships:
            print(f"Identified relationships: {len(relationships)}")
            for j, relationship in enumerate(relationships):
                print(f"  Relationship {j+1}:")
                print(f"  - Parent object: {relationship['parent_object']}")
                print(f"  - Child object: {relationship['child_object']}")
                print(f"  - Query direction: {relationship.get('query_direction', 'Not specified')}")
                print(f"  - Indirect: {relationship.get('indirect', False)}")
                
                # Print relationship path if it exists
                if 'relationship_path' in relationship:
                    print(f"  - Relationship path:")
                    for k, rel in enumerate(relationship['relationship_path']):
                        rel_type = rel.get('type', 'unknown')
                        if rel_type == 'child':
                            print(f"    {k+1}. {rel.get('parentObject', 'Unknown')} -> {rel.get('childObject', 'Unknown')}")
                        elif rel_type == 'parent':
                            print(f"    {k+1}. {rel.get('childObject', 'Unknown')} -> {rel.get('parentObject', 'Unknown')}")
        else:
            print("No relationships identified")
        
        # Generate query
        query = query_generator.generate_query(question)
        print(f"\nGenerated SOQL Query: {query}")
        
        # Check if the query includes the expected objects (case-insensitive)
        query_lower = query.lower()
        
        if "contacts" in question.lower():
            has_contacts = "contacts" in query_lower
            print(f"Query includes Contacts: {has_contacts}")
            
        if "opportunities" in question.lower():
            has_opportunities = "opportunities" in query_lower
            print(f"Query includes Opportunities: {has_opportunities}")
            
        if "quote line items" in question.lower() or "quotelineitems" in question.lower():
            has_quote_line_items = "quotelineitems" in query_lower
            print(f"Query includes QuoteLineItems: {has_quote_line_items}")
            
        if "orders" in question.lower():
            has_orders = "orders" in query_lower
            print(f"Query includes Orders: {has_orders}")
            
        if "order line items" in question.lower() or "orderlineitems" in question.lower():
            has_order_line_items = "orderlineitems" in query_lower
            print(f"Query includes OrderLineItems: {has_order_line_items}")

if __name__ == "__main__":
    main()