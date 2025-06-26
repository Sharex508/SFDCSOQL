"""
Debug script for the _identify_relationship method
"""

from metadata_loader import SalesforceMetadataLoader
from nlp_model import SOQLQueryGenerator
import re

def main():
    print("Debugging the _identify_relationship method")
    print("------------------------------------------")

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
        "Get accounts with all their order line items",
        "List accounts with their quote line items and orders"
    ]

    for test_case in test_cases:
        print(f"\n=== Testing: {test_case} ===")
        question = test_case
        question_lower = question.lower()
        print(f"Question: {question}")
        print(f"Question (lowercase): {question_lower}")

        # Set up the parent and child text
        query_generator._last_identified_parent = "Account"
        if "order line items" in question_lower:
            query_generator._last_identified_child_text = "order line items"
        elif "quote line items and orders" in question_lower:
            query_generator._last_identified_child_text = "quote line items and orders"

        print(f"Last identified parent: {query_generator._last_identified_parent}")
        print(f"Last identified child text: {query_generator._last_identified_child_text}")

        # Check if the child text contains "line items" or similar
        child_text = query_generator._last_identified_child_text.lower()
        is_line_items = "line items" in child_text or "lineitems" in child_text
        print(f"Is line items query: {is_line_items}")

        # Check if the child text contains "and"
        has_and = "and" in child_text
        print(f"Has 'and': {has_and}")

        if has_and:
            parts = child_text.split("and")
            print(f"Split parts: {parts}")
            for part in parts:
                part = part.strip()
                print(f"Processing part: '{part}'")
                # Check for "quote line items"
                if "quote" in part and "line items" in part:
                    print(f"  - Contains 'quote line items': True")
                    # Try to find a path from parent to QuoteLineItem
                    path = query_generator._find_relationship_path("Account", "QuoteLineItem")
                    print(f"  - Path from Account to QuoteLineItem: {path is not None}")
                # Check for "order line items"
                elif "order" in part and "line items" in part:
                    print(f"  - Contains 'order line items': True")
                    # Try to find a path from parent to OrderLineItem
                    path = query_generator._find_relationship_path("Account", "OrderLineItem")
                    print(f"  - Path from Account to OrderLineItem: {path is not None}")
                # Check for "orders"
                elif "orders" in part:
                    print(f"  - Contains 'orders': True")
                    # Try to find a path from parent to Order
                    path = query_generator._find_relationship_path("Account", "Order")
                    print(f"  - Path from Account to Order: {path is not None}")
                    if path:
                        print(f"  - Path details:")
                        for k, rel in enumerate(path):
                            rel_type = rel.get('type', 'unknown')
                            if rel_type == 'child':
                                print(f"    {k+1}. {rel.get('parentObject', 'Unknown')} -> {rel.get('childObject', 'Unknown')}")
                            elif rel_type == 'parent':
                                print(f"    {k+1}. {rel.get('childObject', 'Unknown')} -> {rel.get('parentObject', 'Unknown')}")

                    # Check if Order is already in added_objects
                    print(f"  - Is 'Order' in added_objects: {'Order' in added_objects if 'added_objects' in locals() else 'added_objects not defined'}")
                else:
                    print(f"  - No specific pattern matched")

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
            print("\nNo relationships identified")

        # Generate query
        query = query_generator.generate_query(question)
        print(f"\nGenerated SOQL Query: {query}")

        # Check if the query includes the expected objects (case-insensitive)
        query_lower = query.lower()

        if "order line items" in question_lower:
            has_order_line_items = "orderlineitems" in query_lower
            print(f"Query includes OrderLineItems: {has_order_line_items}")

        if "quote line items" in question_lower:
            has_quote_line_items = "quotelineitems" in query_lower
            print(f"Query includes QuoteLineItems: {has_quote_line_items}")

        if "orders" in question_lower:
            has_orders = "orders" in query_lower
            print(f"Query includes Orders: {has_orders}")

        # Reset the variables for the next test case
        query_generator._last_identified_parent = None
        query_generator._last_identified_child_text = None

if __name__ == "__main__":
    main()
