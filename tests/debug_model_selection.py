"""
Debug Model Selection
--------------------
This script debugs the model selection process for a specific prompt.
"""

from src.utils.metadata_loader import SalesforceMetadataLoader
from src.utils.nlp_model import SOQLQueryGenerator

def main():
    print("Debug Model Selection")
    print("--------------------")

    # Initialize query generator
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

    # Check if modular architecture is available
    print(f"MODULAR_ARCHITECTURE_AVAILABLE: {query_generator.use_modular_architecture}")
    if query_generator.use_modular_architecture:
        print("Using modular architecture")
        print(f"Number of models: {len(query_generator.model_dispatcher.models)}")
        for i, model in enumerate(query_generator.model_dispatcher.models):
            print(f"Model {i+1}: {model.__class__.__name__}")
    else:
        print("Not using modular architecture")

    # Test the problematic prompt
    prompt = "Get all Contact IDs, First Names, and Last Names."
    print(f"\nTesting prompt: \"{prompt}\"")

    # Check which model handles this prompt
    if query_generator.use_modular_architecture:
        for model in query_generator.model_dispatcher.models:
            can_handle = model.can_handle(prompt)
            print(f"Model {model.__class__.__name__} can handle: {can_handle}")

            # If the model can handle the prompt, print the object it identifies
            if can_handle:
                object_name = model._identify_object(prompt)
                print(f"  Identified object: {object_name}")

                # If it's the SortingModel, print more details
                if model.__class__.__name__ == "SortingModel":
                    question_lower = prompt.lower()
                    print(f"  Question lower: {question_lower}")
                    print(f"  'recent' in question: {'recent' in question_lower}")
                    print(f"  'contact' in question: {'contact' in question_lower}")
                    print(f"  'account' in question: {'account' in question_lower}")
                    print(f"  'ordered by' in question: {'ordered by' in question_lower}")
                    print(f"  'sorted by' in question: {'sorted by' in question_lower}")

                    # Check for ORDER BY keywords
                    for keyword in model.order_keywords:
                        if keyword in question_lower:
                            print(f"  ORDER BY keyword found: {keyword}")

                    # Check for sort direction keywords
                    for direction, keywords in model.sort_direction_keywords.items():
                        for keyword in keywords:
                            if keyword in question_lower:
                                print(f"  Sort direction keyword found: {keyword} ({direction})")

                    # Check for LIMIT keywords
                    for keyword in model.limit_keywords:
                        if keyword in question_lower:
                            print(f"  LIMIT keyword found: {keyword}")

                    # Check for OFFSET keywords
                    for keyword in model.offset_keywords:
                        if keyword in question_lower:
                            print(f"  OFFSET keyword found: {keyword}")

    # Generate query
    generated_query = query_generator.generate_query(prompt)
    print(f"\nGenerated query: {generated_query}")

if __name__ == "__main__":
    main()
