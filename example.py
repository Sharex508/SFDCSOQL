"""
Example script for SOQL Query Generator
--------------------------------------
This script demonstrates how to use the SOQL Query Generator with various types of questions,
including basic queries, relationship queries (parent-to-child and child-to-parent), and queries with conditions.
"""

from metadata_loader import SalesforceMetadataLoader
from nlp_model import SOQLQueryGenerator

def main():
    print("SOQL Query Generator Example")
    print("---------------------------")

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

    print("\n1. Basic Queries")
    print("---------------")

    # Example question for a basic query
    question = "Give me a list of all contacts of an account"
    print(f"\nQuestion: {question}")
    query = query_generator.generate_query(question)
    print(f"Generated SOQL Query: {query}")

    # Try another question for Contact object
    question = "List all contacts, opportunities of account"
    print(f"\nQuestion: {question}")
    query = query_generator.generate_query(question)
    print(f"Generated SOQL Query: {query}")

    # Try a question with a limit
    question = "Find the top 3 opportunities by amount"
    print(f"\nQuestion: {question}")
    query = query_generator.generate_query(question)
    print(f"Generated SOQL Query: {query}")

    print("\n2. Parent-to-Child Relationship Queries")
    print("-------------------------------------")

    # Example of a parent-to-child relationship query (Account to Contact)
    question = "Give me accounts with all their contacts"
    print(f"\nQuestion: {question}")

    # Identify relationship
    relationships = query_generator._identify_relationship(question)
    if relationships:
        print(f"Identified relationship: {relationships}")
        if isinstance(relationships, list):
            for i, relationship in enumerate(relationships):
                print(f"  Relationship {i+1}:")
                print(f"  - Parent object: {relationship['parent_object']}")
                print(f"  - Child object: {relationship['child_object']}")
                print(f"  - Relationship field: {relationship['relationship_field']}")
                print(f"  - Query direction: {relationship.get('query_direction', 'Not specified')}")
        else:
            # This shouldn't happen with the updated code, but just in case
            print(f"  - Parent object: {relationships['parent_object']}")
            print(f"  - Child object: {relationships['child_object']}")
            print(f"  - Relationship field: {relationships['relationship_field']}")
            print(f"  - Query direction: {relationships.get('query_direction', 'Not specified')}")

    query = query_generator.generate_query(question)
    print(f"Generated SOQL Query: {query}")

    # Example of another parent-to-child relationship query (Account to Opportunity)
    question = "Show me accounts with their opportunities"
    print(f"\nQuestion: {question}")
    query = query_generator.generate_query(question)
    print(f"Generated SOQL Query: {query}")

    print("\n3. Child-to-Parent Relationship Queries")
    print("-------------------------------------")

    # Example of a child-to-parent relationship query (Contact to Account)
    question = "Give me a list of all contacts of an account name is 'acme'"
    print(f"\nQuestion: {question}")

    # Identify relationship
    relationships = query_generator._identify_relationship(question)
    if relationships:
        print(f"Identified relationship: {relationships}")
        if isinstance(relationships, list):
            for i, relationship in enumerate(relationships):
                print(f"  Relationship {i+1}:")
                print(f"  - Parent object: {relationship['parent_object']}")
                print(f"  - Child object: {relationship['child_object']}")
                print(f"  - Relationship field: {relationship['relationship_field']}")
                print(f"  - Query direction: {relationship.get('query_direction', 'Not specified')}")
        else:
            # This shouldn't happen with the updated code, but just in case
            print(f"  - Parent object: {relationships['parent_object']}")
            print(f"  - Child object: {relationships['child_object']}")
            print(f"  - Relationship field: {relationships['relationship_field']}")
            print(f"  - Query direction: {relationships.get('query_direction', 'Not specified')}")

    query = query_generator.generate_query(question)
    print(f"Generated SOQL Query: {query}")

    # Example of another child-to-parent relationship query (Opportunity to Account)
    question = "List opportunities from accounts in the technology industry"
    print(f"\nQuestion: {question}")
    query = query_generator.generate_query(question)
    print(f"Generated SOQL Query: {query}")

    print("\n4. Bidirectional Relationship Queries")
    print("----------------------------------")
    print("(Child-to-Parent queries automatically converted to Parent-to-Child)")

    # Example of a bidirectional relationship query (Contact to Account, converted to Account to Contact)
    question = "Give me a list of all contacts of an account name is 'acme'"
    print(f"\nQuestion: {question}")

    # Identify relationship
    relationships = query_generator._identify_relationship(question)
    if relationships:
        print(f"Identified relationship: {relationships}")
        if isinstance(relationships, list):
            for i, relationship in enumerate(relationships):
                print(f"  Relationship {i+1}:")
                print(f"  - Parent object: {relationship['parent_object']}")
                print(f"  - Child object: {relationship['child_object']}")
                print(f"  - Relationship field: {relationship['relationship_field']}")
                print(f"  - Query direction: {relationship.get('query_direction', 'Not specified')}")
                print(f"  - Bidirectional: {relationship.get('bidirectional', False)}")
        else:
            # This shouldn't happen with the updated code, but just in case
            print(f"  - Parent object: {relationships['parent_object']}")
            print(f"  - Child object: {relationships['child_object']}")
            print(f"  - Relationship field: {relationships['relationship_field']}")
            print(f"  - Query direction: {relationships.get('query_direction', 'Not specified')}")
            print(f"  - Bidirectional: {relationships.get('bidirectional', False)}")

    query = query_generator.generate_query(question)
    print(f"Generated SOQL Query: {query}")
    print(f"✓ Query is now a parent-to-child query with a subquery in the SELECT clause")

    # Example of another bidirectional relationship query (Opportunity to Account, converted to Account to Opportunity)
    question = "List opportunities from accounts in the technology industry"
    print(f"\nQuestion: {question}")

    # Identify relationship
    relationships = query_generator._identify_relationship(question)
    if relationships:
        print(f"Identified relationship: {relationships}")
        if isinstance(relationships, list):
            for i, relationship in enumerate(relationships):
                print(f"  Relationship {i+1}:")
                print(f"  - Parent object: {relationship['parent_object']}")
                print(f"  - Child object: {relationship['child_object']}")
                print(f"  - Relationship field: {relationship['relationship_field']}")
                print(f"  - Query direction: {relationship.get('query_direction', 'Not specified')}")
                print(f"  - Bidirectional: {relationship.get('bidirectional', False)}")
        else:
            # This shouldn't happen with the updated code, but just in case
            print(f"  - Parent object: {relationships['parent_object']}")
            print(f"  - Child object: {relationships['child_object']}")
            print(f"  - Relationship field: {relationships['relationship_field']}")
            print(f"  - Query direction: {relationships.get('query_direction', 'Not specified')}")
            print(f"  - Bidirectional: {relationships.get('bidirectional', False)}")

    query = query_generator.generate_query(question)
    print(f"Generated SOQL Query: {query}")
    print(f"✓ Query is now a parent-to-child query with a subquery in the SELECT clause")

if __name__ == "__main__":
    main()
