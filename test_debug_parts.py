"""
Debug script for the parts after splitting by "and"
"""

from metadata_loader import SalesforceMetadataLoader
from nlp_model import SOQLQueryGenerator

def main():
    print("Debugging the parts after splitting by 'and'")
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

    # Test case
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

            # Check our condition
            if "orders" in part and "line" not in part:
                print(f"  - Our condition is triggered: True")
            else:
                print(f"  - Our condition is triggered: False")

if __name__ == "__main__":
    main()