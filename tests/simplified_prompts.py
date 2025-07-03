"""
SOQL Query Generator Simplified Prompt Tester
----------------------------------
This script tests the SOQL Query Generator against a set of prompts from prompts.txt
and compares the generated queries with the expected answers.
"""

import re
import os
from src.utils.metadata_loader import SalesforceMetadataLoader
from src.utils.nlp_model import SOQLQueryGenerator

def parse_prompts_file(file_path):
    """
    Parse the prompts.txt file to extract prompts and their expected answers.

    Args:
        file_path: Path to the prompts.txt file

    Returns:
        A list of tuples (prompt, expected_answer)
    """
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Create a list of prompt-answer pairs
    prompt_answer_pairs = []

    # Define the left and right double quotation marks used in the file
    left_quote = '\u201C'  # Left double quotation mark (U+201C)
    right_quote = '\u201D'  # Right double quotation mark (U+201D)

    # Extract all prompts (text inside curly quotes)
    # Use a pattern that looks for text between left and right double quotation marks
    all_prompts = []
    pattern = f'{left_quote}(.*?){right_quote}'
    for match in re.finditer(pattern, content, re.DOTALL):
        all_prompts.append(match.group(1))

    print(f"Found {len(all_prompts)} prompts in the file")

    # Extract all answers (lines starting with SELECT)
    # Split the content at "Answers" to get only the answers section
    if "Answers" in content:
        answers_section = content.split("Answers")[1]
        all_answers = re.findall(r'SELECT[^\n]*', answers_section)
        print(f"Found {len(all_answers)} answers in the file")
    else:
        print("Warning: Could not find 'Answers' section in the file")
        all_answers = re.findall(r'SELECT[^\n]*', content)
        print(f"Found {len(all_answers)} answers in the entire file")

    # Make sure we have the same number of prompts and answers
    if len(all_prompts) != len(all_answers):
        print(f"Warning: Number of prompts ({len(all_prompts)}) does not match number of answers ({len(all_answers)})")
        # Use the minimum length to avoid index errors
        min_len = min(len(all_prompts), len(all_answers))
        all_prompts = all_prompts[:min_len]
        all_answers = all_answers[:min_len]

    # Create prompt-answer pairs
    for i in range(len(all_prompts)):
        prompt = all_prompts[i]
        answer = all_answers[i]
        prompt_answer_pairs.append((prompt, answer))
        print(f"Paired prompt: '{prompt}' with answer: '{answer}'")

    print(f"Created {len(prompt_answer_pairs)} prompt-answer pairs")
    return prompt_answer_pairs

def initialize_query_generator():
    """
    Initialize the SOQL Query Generator with metadata.

    Returns:
        An initialized SOQLQueryGenerator instance
    """
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

    return query_generator

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
    print("SOQL Query Generator Simplified Prompt Tester")
    print("----------------------------------")

    # Parse prompts file
    prompts_file = "prompts.txt"
    if not os.path.exists(prompts_file):
        print(f"Error: Prompts file '{prompts_file}' not found.")
        return

    print(f"Parsing prompts from {prompts_file}...")
    prompt_answer_pairs = parse_prompts_file(prompts_file)
    print(f"Found {len(prompt_answer_pairs)} prompt-answer pairs.")

    # Initialize query generator
    query_generator = initialize_query_generator()

    # Check if modular architecture is available
    print(f"MODULAR_ARCHITECTURE_AVAILABLE: {query_generator.use_modular_architecture}")
    if query_generator.use_modular_architecture:
        print("Using modular architecture")
        print(f"Number of models: {len(query_generator.model_dispatcher.models)}")
    else:
        print("Not using modular architecture")

    # Test all prompts
    results = []
    for i, (prompt, expected_answer) in enumerate(prompt_answer_pairs):
        print(f"\nTesting prompt {i+1}: \"{prompt}\"")
        print(f"Expected answer: {expected_answer}")

        try:
            # Check if modular architecture is available
            print(f"MODULAR_ARCHITECTURE_AVAILABLE: {query_generator.use_modular_architecture}")
            if query_generator.use_modular_architecture:
                print("Using modular architecture")
                print(f"Number of models: {len(query_generator.model_dispatcher.models)}")
            else:
                print("Not using modular architecture")

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
                'differences': differences
            })

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            results.append({
                'prompt': prompt,
                'expected': expected_answer,
                'generated': None,
                'is_match': False,
                'similarity': 0,
                'error': str(e)
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

    # List the top 5 most problematic prompts (lowest similarity)
    if len(non_matches) > 0:
        print("\nTop 5 most problematic prompts:")
        problematic = sorted(non_matches, key=lambda r: r['similarity'])[:5]
        for i, r in enumerate(problematic):
            print(f"{i+1}. \"{r['prompt']}\" (similarity: {r['similarity']:.2f})")
            print(f"   Expected: {r['expected']}")
            print(f"   Generated: {r['generated']}")
            print()

if __name__ == "__main__":
    main()
