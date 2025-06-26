"""
Test script for multiple relationships in SOQL Query Generator
"""

from metadata_loader import SalesforceMetadataLoader
from nlp_model import SOQLQueryGenerator

def main():
    print("Testing multiple relationships in SOQL Query Generator")
    print("----------------------------------------------------")

    # Set up metadata
    print("Setting up Salesforce metadata...")
    metadata_loader = SalesforceMetadataLoader()
    metadata_loader.add_sample_metadata()

    # Initialize query generator
    query_generator = SOQLQueryGenerator()

    # Load objects into the query generator
    query_generator.objects = {name: metadata_loader.objects[name] 
                              for name in metadata_loader.get_object_names()}
    query_generator.fields_by_object = metadata_loader.fields_by_object
    query_generator.relationships = metadata_loader.relationships

    # Test multiple relationships query
    question = "List all contacts, opportunities of account"
    print(f"\nQuestion: {question}")
    
    # Identify relationships
    relationships = query_generator._identify_relationship(question)
    if relationships:
        print(f"Identified relationships: {len(relationships)}")
        for i, relationship in enumerate(relationships):
            print(f"  Relationship {i+1}:")
            print(f"  - Parent object: {relationship['parent_object']}")
            print(f"  - Child object: {relationship['child_object']}")
            print(f"  - Relationship field: {relationship['relationship_field']}")
            print(f"  - Query direction: {relationship.get('query_direction', 'Not specified')}")
    
    # Generate query
    query = query_generator.generate_query(question)
    print(f"\nGenerated SOQL Query: {query}")
    
    # Check if the query includes both Contacts and Opportunities
    has_contacts = "Contacts" in query
    has_opportunities = "Opportunities" in query
    
    print(f"\nQuery includes Contacts: {has_contacts}")
    print(f"Query includes Opportunities: {has_opportunities}")
    
    if has_contacts and has_opportunities:
        print("\n✓ Success! The query includes both Contacts and Opportunities as child objects.")
    else:
        print("\n✗ Failure! The query does not include both Contacts and Opportunities as child objects.")

if __name__ == "__main__":
    main()