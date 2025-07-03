import re
from src.utils.metadata_loader import SalesforceMetadataLoader
from src.utils.nlp_model import SOQLQueryGenerator

def normalize_query(query):
    """
    Normalize a SOQL query for comparison by removing extra whitespace and making case consistent.

    Args:
        query: The SOQL query to normalize

    Returns:
        A normalized version of the query
    """
    # Remove extra whitespace
    query = re.sub(r'\s+', ' ', query).strip()

    # Make keywords uppercase for consistent comparison
    keywords = ['SELECT', 'FROM', 'WHERE', 'ORDER BY', 'GROUP BY', 'HAVING', 'LIMIT', 'OFFSET', 'WITH', 'FOR']
    for keyword in keywords:
        query = re.sub(r'\b' + keyword + r'\b', keyword, query, flags=re.IGNORECASE)

    return query

def compare_queries(generated, expected):
    """
    Compare a generated query with the expected answer.

    Args:
        generated: The generated SOQL query
        expected: The expected SOQL query

    Returns:
        A tuple (is_match, similarity_score, differences)
    """
    # Normalize both queries
    generated_norm = normalize_query(generated)
    expected_norm = normalize_query(expected)

    # Check for exact match
    if generated_norm == expected_norm:
        return True, 1.0, None

    # Calculate similarity score (simple version)
    # In a more sophisticated version, you could use edit distance or other similarity metrics
    gen_words = set(generated_norm.split())
    exp_words = set(expected_norm.split())
    common_words = gen_words.intersection(exp_words)

    if len(gen_words) == 0 or len(exp_words) == 0:
        similarity = 0
    else:
        similarity = len(common_words) / max(len(gen_words), len(exp_words))

    # Identify differences
    differences = {
        'missing': list(exp_words - gen_words),
        'extra': list(gen_words - exp_words)
    }

    return False, similarity, differences

def main():
    print("Checking if modular architecture is being used...")

    # Initialize query generator
    metadata_loader = SalesforceMetadataLoader()
    metadata_loader.add_sample_metadata()

    query_generator = SOQLQueryGenerator()
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

        # Try to import the models directly to see if there's an issue
        try:
            from basic_query_model import BasicQueryModel
            print("Successfully imported BasicQueryModel")
        except ImportError as e:
            print(f"Failed to import BasicQueryModel: {e}")

        try:
            from where_clause_model import WhereClauseModel
            print("Successfully imported WhereClauseModel")
        except ImportError as e:
            print(f"Failed to import WhereClauseModel: {e}")

        try:
            from date_filter_model import DateFilterModel
            print("Successfully imported DateFilterModel")
        except ImportError as e:
            print(f"Failed to import DateFilterModel: {e}")

        try:
            from relationship_model import RelationshipModel
            print("Successfully imported RelationshipModel")
        except ImportError as e:
            print(f"Failed to import RelationshipModel: {e}")

        try:
            from aggregation_model import AggregationModel
            print("Successfully imported AggregationModel")
        except ImportError as e:
            print(f"Failed to import AggregationModel: {e}")

        try:
            from sorting_model import SortingModel
            print("Successfully imported SortingModel")
        except ImportError as e:
            print(f"Failed to import SortingModel: {e}")

        try:
            from advanced_features_model import AdvancedFeaturesModel
            print("Successfully imported AdvancedFeaturesModel")
        except ImportError as e:
            print(f"Failed to import AdvancedFeaturesModel: {e}")

    # Test multiple prompts with their expected answers
    prompt_answer_pairs = [
        ("Show me the ID and name of all accounts.", "SELECT Id, Name FROM Account"),
        ("List closed‑won opportunities ordered by creation date.", "SELECT Name FROM Opportunity WHERE StageName = 'Closed Won' ORDER BY CreatedDate"),
        ("Retrieve IDs of leads with status 'Open – Not Contacted'.", "SELECT Id FROM Lead WHERE Status = 'Open - Not Contacted'"),
        ("For each quote, list its quote line items.", "SELECT Id, Name, (SELECT Id, Quantity, UnitPrice FROM QuoteLineItems) FROM Quote"),
        ("Show each case with its comments.", "SELECT Id, Name, (SELECT Id, CommentBody FROM CaseComments) FROM Case")
    ]

    results = []
    for prompt, expected_answer in prompt_answer_pairs:
        print(f"\nTesting prompt: \"{prompt}\"")
        print(f"Expected answer: {expected_answer}")

        # Check which model handles this prompt
        handling_model = None
        if query_generator.use_modular_architecture:
            for model in query_generator.model_dispatcher.models:
                if model.can_handle(prompt):
                    handling_model = model.__class__.__name__
                    print(f"Model that can handle this prompt: {handling_model}")
                    break

        try:
            # Generate query
            generated_query = query_generator.generate_query(prompt)
            print(f"Generated query: {generated_query}")

            # Compare with expected answer
            is_match, similarity, differences = compare_queries(generated_query, expected_answer)

            if is_match:
                print("✅ MATCH!")
            else:
                print(f"❌ NO MATCH (similarity: {similarity:.2f})")
                if differences:
                    if differences['missing']:
                        print(f"  Missing terms: {', '.join(differences['missing'])}")
                    if differences['extra']:
                        print(f"  Extra terms: {', '.join(differences['extra'])}")

            results.append({
                'prompt': prompt,
                'expected': expected_answer,
                'generated': generated_query,
                'is_match': is_match,
                'similarity': similarity,
                'differences': differences,
                'handling_model': handling_model
            })

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            results.append({
                'prompt': prompt,
                'expected': expected_answer,
                'generated': None,
                'is_match': False,
                'similarity': 0,
                'error': str(e),
                'handling_model': handling_model
            })

    # Summarize results
    matches = sum(1 for r in results if r['is_match'])
    errors = sum(1 for r in results if 'error' in r)

    print("\n=== SUMMARY ===")
    print(f"Total prompts tested: {len(results)}")
    print(f"Exact matches: {matches} ({matches/len(results)*100:.1f}%)")
    print(f"Errors: {errors} ({errors/len(results)*100:.1f}%)")

    # Calculate average similarity for non-matching queries
    non_matches = [r for r in results if not r['is_match'] and 'error' not in r]
    if non_matches:
        avg_similarity = sum(r['similarity'] for r in non_matches) / len(non_matches)
        print(f"Average similarity for non-matching queries: {avg_similarity:.2f}")

    # Group results by similarity ranges
    similarity_ranges = {
        '0.9-1.0': 0,
        '0.8-0.9': 0,
        '0.7-0.8': 0,
        '0.6-0.7': 0,
        '0.5-0.6': 0,
        '0.0-0.5': 0
    }

    for r in results:
        if 'error' in r:
            continue

        sim = r['similarity']
        if sim >= 0.9:
            similarity_ranges['0.9-1.0'] += 1
        elif sim >= 0.8:
            similarity_ranges['0.8-0.9'] += 1
        elif sim >= 0.7:
            similarity_ranges['0.7-0.8'] += 1
        elif sim >= 0.6:
            similarity_ranges['0.6-0.7'] += 1
        elif sim >= 0.5:
            similarity_ranges['0.5-0.6'] += 1
        else:
            similarity_ranges['0.0-0.5'] += 1

    print("\nSimilarity distribution:")
    for range_name, count in similarity_ranges.items():
        print(f"  {range_name}: {count} ({count/len(results)*100:.1f}%)")

    # List all prompts with their results
    print("\nDetailed results:")
    for i, r in enumerate(results):
        print(f"{i+1}. \"{r['prompt']}\"")
        print(f"   Model: {r['handling_model']}")
        if 'error' in r:
            print(f"   ERROR: {r['error']}")
        else:
            print(f"   Match: {'✅' if r['is_match'] else '❌'} (similarity: {r['similarity']:.2f})")
            print(f"   Expected: {r['expected']}")
            print(f"   Generated: {r['generated']}")
            if not r['is_match'] and r['differences']:
                if r['differences']['missing']:
                    print(f"   Missing terms: {', '.join(r['differences']['missing'])}")
                if r['differences']['extra']:
                    print(f"   Extra terms: {', '.join(r['differences']['extra'])}")
        print()

if __name__ == "__main__":
    main()
