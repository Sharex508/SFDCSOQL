"""
Test script for dynamic relationship handling in SOQL Query Generator
"""

from metadata_loader import SalesforceMetadataLoader
from nlp_model import SOQLQueryGenerator

def main():
    print("Testing dynamic relationship handling in SOQL Query Generator")
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

    # Test various indirect relationship queries
    test_cases = [
        # Standard indirect relationship
        "List quote line items of an account",

        # Multiple indirect relationships with common path
        "Show me orders and quote line items of an account",

        # Different wording for the same relationship
        "Get all quote line items related to an account",

        # Different objects with indirect relationship
        "Find order line items from an opportunity",

        # More complex query with conditions
        "Show me quote line items of accounts in the technology industry",

        # Different relationship direction
        "Show me accounts with their quote line items",

        # Generic relationship query
        "Show me all objects related to account ABC123"
    ]

    for i, question in enumerate(test_cases):
        print(f"\nTest Case {i+1}: {question}")

        # Identify the main object
        main_object = query_generator._identify_object(question)
        print(f"Identified main object: {main_object}")

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
        if "quote line items" in question.lower() or "quotelineitems" in question.lower():
            has_quote_line_items = "quotelineitems" in query.lower()
            print(f"Query includes QuoteLineItems: {has_quote_line_items}")

            # For Test Case 6, print more information
            if "accounts with their quote line items" in question.lower():
                print("\nDebug information for Test Case 6:")
                print(f"Query: {query}")
                print(f"Query contains 'QuoteLineItems': {'quotelineitems' in query.lower()}")
                print(f"Query contains 'Quotes': {'quotes' in query.lower()}")

                # Check if there's a relationship from Account to QuoteLineItem
                account_to_quotelineitem = False
                for rel in relationships:
                    if rel['parent_object'] == "Account" and rel['child_object'] == "QuoteLineItem":
                        account_to_quotelineitem = True
                        print(f"Found relationship from Account to QuoteLineItem: {rel}")
                        break
                print(f"Found relationship from Account to QuoteLineItem: {account_to_quotelineitem}")

        if "orders" in question.lower():
            has_orders = "orders" in query.lower()
            print(f"Query includes Orders: {has_orders}")

        if "order line items" in question.lower() or "orderlineitems" in question.lower():
            has_order_line_items = "orderlineitems" in query.lower()
            print(f"Query includes OrderLineItems: {has_order_line_items}")

if __name__ == "__main__":
    main()
