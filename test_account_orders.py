"""
Test script for retrieving orders and order line items of an account
"""

from metadata_loader import SalesforceMetadataLoader
from nlp_model import SOQLQueryGenerator

def main():
    print("Testing retrieval of orders and order line items of an account")
    print("-----------------------------------------------------------")

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

    # Test the specific question from the issue description
    question = "retrieve orders and order line items of an account"
    print(f"\nQuestion: {question}")
    question_lower = question.lower()
    print(f"Question (lowercase): {question_lower}")

    # Debug: Check if the regex pattern matches
    import re
    pattern = r"(?:list|show|get|find|display|retrieve) (?:all )?(?:quote line items|quotelineitems|order line items|orderlineitems|orders)(?:,? (?:and )?(?:quote line items|quotelineitems|order line items|orderlineitems|orders))? (?:of|from) (?:an |a |the )?accounts?"
    print(f"Regex pattern: {pattern}")
    match = re.search(pattern, question_lower)
    print(f"Regex pattern match: {match is not None}")

    if match:
        print(f"Match groups: {match.groups()}")

    # Check if the specific keywords are in the question
    print(f"Contains 'orders': {'orders' in question_lower}")
    print(f"Contains 'order line items': {'order line items' in question_lower}")
    print(f"Contains 'quote line items': {'quote line items' in question_lower}")
    print(f"Contains 'quotelineitems': {'quotelineitems' in question_lower}")
    print(f"Contains 'account': {'account' in question_lower}")
    print(f"Contains 'retrieve': {'retrieve' in question_lower}")

    # Check if OrderLineItem exists in the metadata
    print(f"\nOrderLineItem exists in metadata: {'OrderLineItem' in query_generator.objects}")

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

    # Check if we can find a path from Account to OrderLineItem
    path = query_generator._find_relationship_path("Account", "OrderLineItem")
    print(f"\nPath from Account to OrderLineItem: {path is not None}")
    if path:
        print("Path details:")
        for i, rel in enumerate(path):
            rel_type = rel.get('type', 'unknown')
            if rel_type == 'child':
                print(f"  {i+1}. {rel.get('parentObject', 'Unknown')} -> {rel.get('childObject', 'Unknown')}")
            elif rel_type == 'parent':
                print(f"  {i+1}. {rel.get('childObject', 'Unknown')} -> {rel.get('parentObject', 'Unknown')}")

    # Check if we can find a path from Account to Order
    path = query_generator._find_relationship_path("Account", "Order")
    print(f"\nPath from Account to Order: {path is not None}")
    if path:
        print("Path details:")
        for i, rel in enumerate(path):
            rel_type = rel.get('type', 'unknown')
            if rel_type == 'child':
                print(f"  {i+1}. {rel.get('parentObject', 'Unknown')} -> {rel.get('childObject', 'Unknown')}")
            elif rel_type == 'parent':
                print(f"  {i+1}. {rel.get('childObject', 'Unknown')} -> {rel.get('parentObject', 'Unknown')}")

    # Identify relationships
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

    # Check if the query includes both Orders and OrderLineItems
    has_orders = "Orders" in query
    has_order_line_items = "OrderLineItems" in query

    print(f"\nQuery includes Orders: {has_orders}")
    print(f"Query includes OrderLineItems: {has_order_line_items}")

    if has_orders and has_order_line_items:
        print("\n✓ Success! The query includes both Orders and OrderLineItems as requested.")
    elif has_orders:
        print("\n✓ Success! The query includes Orders as requested.")
    else:
        print("\n✗ Failure! The query does not include Orders.")

if __name__ == "__main__":
    main()
