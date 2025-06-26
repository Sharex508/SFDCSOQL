"""
Script to check the relationships that are being loaded
"""

import os
from metadata_loader import SalesforceMetadataLoader

def main():
    print("Checking relationships")
    print("---------------------")

    # Set up metadata
    print("Setting up Salesforce metadata...")
    metadata_loader = SalesforceMetadataLoader()

    # Use sample metadata directly instead of loading from Excel
    print("Using sample metadata directly...")
    excel_path = "Salesforce_Complete_Metadata.xlsx"
    if os.path.exists(excel_path):
        print(f"Excel file {excel_path} exists, but we're not loading it")

    # Add sample metadata directly
    metadata_loader.add_sample_metadata()

    # Check relationships for Account
    print("\nRelationships for Account:")
    if "Account" in metadata_loader.relationships:
        for rel in metadata_loader.relationships["Account"]:
            print(f"  - Type: {rel.get('type')}")
            if rel.get('type') == 'child':
                print(f"    Child Object: {rel.get('childObject')}")
                print(f"    Field: {rel.get('field')}")
            elif rel.get('type') == 'parent':
                print(f"    Parent Object: {rel.get('parentObject')}")
                print(f"    Field: {rel.get('field')}")
    else:
        print("  No relationships found")

    # Check relationships for Opportunity
    print("\nRelationships for Opportunity:")
    if "Opportunity" in metadata_loader.relationships:
        for rel in metadata_loader.relationships["Opportunity"]:
            print(f"  - Type: {rel.get('type')}")
            if rel.get('type') == 'child':
                print(f"    Child Object: {rel.get('childObject')}")
                print(f"    Field: {rel.get('field')}")
            elif rel.get('type') == 'parent':
                print(f"    Parent Object: {rel.get('parentObject')}")
                print(f"    Field: {rel.get('field')}")
    else:
        print("  No relationships found")

    # Check relationships for Quote
    print("\nRelationships for Quote:")
    if "Quote" in metadata_loader.relationships:
        for rel in metadata_loader.relationships["Quote"]:
            print(f"  - Type: {rel.get('type')}")
            if rel.get('type') == 'child':
                print(f"    Child Object: {rel.get('childObject')}")
                print(f"    Field: {rel.get('field')}")
            elif rel.get('type') == 'parent':
                print(f"    Parent Object: {rel.get('parentObject')}")
                print(f"    Field: {rel.get('field')}")
    else:
        print("  No relationships found")

    # Check relationships for QuoteLineItem
    print("\nRelationships for QuoteLineItem:")
    if "QuoteLineItem" in metadata_loader.relationships:
        for rel in metadata_loader.relationships["QuoteLineItem"]:
            print(f"  - Type: {rel.get('type')}")
            if rel.get('type') == 'child':
                print(f"    Child Object: {rel.get('childObject')}")
                print(f"    Field: {rel.get('field')}")
            elif rel.get('type') == 'parent':
                print(f"    Parent Object: {rel.get('parentObject')}")
                print(f"    Field: {rel.get('field')}")
    else:
        print("  No relationships found")

    # Check relationships for Order
    print("\nRelationships for Order:")
    if "Order" in metadata_loader.relationships:
        for rel in metadata_loader.relationships["Order"]:
            print(f"  - Type: {rel.get('type')}")
            if rel.get('type') == 'child':
                print(f"    Child Object: {rel.get('childObject')}")
                print(f"    Field: {rel.get('field')}")
            elif rel.get('type') == 'parent':
                print(f"    Parent Object: {rel.get('parentObject')}")
                print(f"    Field: {rel.get('field')}")
    else:
        print("  No relationships found")

if __name__ == "__main__":
    main()
