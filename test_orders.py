"""
Test script for the Order and OrderLineItem relationships
"""

from metadata_loader import SalesforceMetadataLoader
from nlp_model import SOQLQueryGenerator

def main():
    print("Testing Order and OrderLineItem relationships")
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

    # Print relationships for Order
    print("\nRelationships for Order:")
    if "Order" in query_generator.relationships:
        for rel in query_generator.relationships["Order"]:
            print(f"  - Type: {rel.get('type')}")
            if rel.get('type') == 'child':
                print(f"    Child Object: {rel.get('childObject')}")
                print(f"    Field: {rel.get('field')}")
            elif rel.get('type') == 'parent':
                print(f"    Parent Object: {rel.get('parentObject')}")
                print(f"    Field: {rel.get('field')}")
    else:
        print("  No relationships found")

    # Print relationships for OrderLineItem
    print("\nRelationships for OrderLineItem:")
    if "OrderLineItem" in query_generator.relationships:
        for rel in query_generator.relationships["OrderLineItem"]:
            print(f"  - Type: {rel.get('type')}")
            if rel.get('type') == 'child':
                print(f"    Child Object: {rel.get('childObject')}")
                print(f"    Field: {rel.get('field')}")
            elif rel.get('type') == 'parent':
                print(f"    Parent Object: {rel.get('parentObject')}")
                print(f"    Field: {rel.get('field')}")
    else:
        print("  No relationships found")

    # Find path from Account to Order
    print("\nFinding path from Account to Order:")
    path = query_generator._find_relationship_path("Account", "Order")
    if path:
        print(f"Found path with {len(path)} steps:")
        for i, rel in enumerate(path):
            rel_type = rel.get('type', 'unknown')
            if rel_type == 'child':
                print(f"  {i+1}. {rel.get('parentObject', 'Unknown')} -> {rel.get('childObject', 'Unknown')}")
            elif rel_type == 'parent':
                print(f"  {i+1}. {rel.get('childObject', 'Unknown')} -> {rel.get('parentObject', 'Unknown')}")
    else:
        print("No path found")

    # Find path from Account to OrderLineItem
    print("\nFinding path from Account to OrderLineItem:")
    path = query_generator._find_relationship_path("Account", "OrderLineItem")
    if path:
        print(f"Found path with {len(path)} steps:")
        for i, rel in enumerate(path):
            rel_type = rel.get('type', 'unknown')
            if rel_type == 'child':
                print(f"  {i+1}. {rel.get('parentObject', 'Unknown')} -> {rel.get('childObject', 'Unknown')}")
            elif rel_type == 'parent':
                print(f"  {i+1}. {rel.get('childObject', 'Unknown')} -> {rel.get('parentObject', 'Unknown')}")
    else:
        print("No path found")

    # Test case
    question = "List accounts with their quote line items and orders"
    print(f"\nTesting: {question}")

    # Set up the parent and child text
    query_generator._last_identified_parent = "Account"
    query_generator._last_identified_child_text = "quote line items and orders"

    # Debug the child text parsing
    child_text = "quote line items and orders"
    print(f"Child text: '{child_text}'")

    # Check if the child text contains "and"
    has_and = "and" in child_text
    print(f"Has 'and': {has_and}")

    if has_and:
        parts = child_text.split("and")
        print(f"Split parts: {parts}")
        for part in parts:
            part = part.strip()
            print(f"Processing part: '{part}'")

            # Check conditions
            print(f"  - Contains 'quote': {'quote' in part}")
            print(f"  - Contains 'line': {'line' in part}")
            print(f"  - Contains 'items': {'items' in part}")
            print(f"  - Contains 'order': {'order' in part}")
            print(f"  - Contains 'orders': {'orders' in part}")
            print(f"  - Contains 'line items': {'line items' in part}")

            # Check specific conditions
            is_quote_line_items = "quote" in part and "line items" in part
            is_order_line_items = "order" in part and "line items" in part
            is_orders = "orders" in part
            is_order_without_line = "order" in part and "line" not in part

            print(f"  - Is quote line items: {is_quote_line_items}")
            print(f"  - Is order line items: {is_order_line_items}")
            print(f"  - Is orders: {is_orders}")
            print(f"  - Is order without line: {is_order_without_line}")

    # Call the _identify_relationship method
    relationships = query_generator._identify_relationship(question)
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
