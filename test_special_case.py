"""
Test script for the special case for "quote line items and orders"
"""

from metadata_loader import SalesforceMetadataLoader
from nlp_model import SOQLQueryGenerator

def main():
    print("Testing special case for 'quote line items and orders'")
    print("--------------------------------------------------")

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
    
    # Check if the regex pattern matches
    pattern = r"(?:list|show|get|find|display|retrieve) (?:all )?(?:quote line items|quotelineitems)(?:,? (?:and )?(?:orders|order))?(?:,? (?:and )?(?:order line items|orderlineitems))? (?:of|from) (?:an |a |the )?accounts?"
    match = re.search(pattern, question.lower())
    if match:
        print(f"Regex pattern 1 matched: {match.group()}")
    else:
        print("Regex pattern 1 not matched")
        
    pattern = r"(?:list|show|get|find|display|retrieve) (?:all )?(?:orders|order)(?:,? (?:and )?(?:quote line items|quotelineitems))?(?:,? (?:and )?(?:order line items|orderlineitems))? (?:of|from) (?:an |a |the )?accounts?"
    match = re.search(pattern, question.lower())
    if match:
        print(f"Regex pattern 2 matched: {match.group()}")
    else:
        print("Regex pattern 2 not matched")
        
    pattern = r"(?:list|show|get|find|display|retrieve) (?:all )?(?:order line items|orderlineitems)(?:,? (?:and )?(?:quote line items|quotelineitems))?(?:,? (?:and )?(?:orders|order))? (?:of|from) (?:an |a |the )?accounts?"
    match = re.search(pattern, question.lower())
    if match:
        print(f"Regex pattern 3 matched: {match.group()}")
    else:
        print("Regex pattern 3 not matched")
        
    # Test a different pattern
    pattern = r"(?:list|show|get|find|display|retrieve) (?:all )?(?:the )?(?:accounts?)(?:s)? (?:with|and) (?:all )?(?:their|its) (?:quote line items|quotelineitems)(?:,? (?:and )?(?:orders|order))?"
    match = re.search(pattern, question.lower())
    if match:
        print(f"New regex pattern matched: {match.group()}")
    else:
        print("New regex pattern not matched")
    
    # Directly test the special case code
    print("\nDirectly testing the special case code:")
    
    # Create a new question that should match the special case
    special_case_question = "List quote line items and orders of an account"
    print(f"Special case question: '{special_case_question}'")
    
    # Check if the special case pattern matches
    if "quote line items and orders" in special_case_question.lower():
        print("Simple pattern 'quote line items and orders' matched")
    else:
        print("Simple pattern 'quote line items and orders' not matched")
        
    # Check if the regex pattern matches
    pattern = r"(?:list|show|get|find|display|retrieve) (?:all )?(?:quote line items|quotelineitems)(?:,? (?:and )?(?:orders|order))?(?:,? (?:and )?(?:order line items|orderlineitems))? (?:of|from) (?:an |a |the )?accounts?"
    match = re.search(pattern, special_case_question.lower())
    if match:
        print(f"Regex pattern 1 matched: {match.group()}")
    else:
        print("Regex pattern 1 not matched")
    
    # Call the _identify_relationship method
    relationships = query_generator._identify_relationship(special_case_question)
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
    query = query_generator.generate_query(special_case_question)
    print(f"\nGenerated SOQL Query: {query}")
    
    # Check if the query includes the expected objects (case-insensitive)
    query_lower = query.lower()
    
    has_quote_line_items = "quotelineitems" in query_lower
    print(f"Query includes QuoteLineItems: {has_quote_line_items}")
    
    has_orders = "orders" in query_lower
    print(f"Query includes Orders: {has_orders}")

if __name__ == "__main__":
    main()