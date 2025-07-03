"""
SOQL Query Generator 100 Prompts Tester
----------------------------------
This script tests the SOQL Query Generator against 100 prompts from the issue description
and compares the generated queries with the expected answers.

Debug features:
- Displays the identified object for each prompt
- Provides a summary of object identification results
- Shows which model handles each prompt
- Includes detailed information about specific query types
"""

import re
import os
from src.utils.metadata_loader import SalesforceMetadataLoader
from src.utils.nlp_model import SOQLQueryGenerator

def get_prompts_and_answers():
    """
    Get the prompts and expected answers from the issue description.

    Returns:
        A list of tuples (prompt, expected_answer)
    """
    # Define the prompts and expected answers
    prompts_answers = [
        # Basic Queries (1–10)
        ("Get all Account IDs and Names.", "SELECT Id, Name FROM Account"),
        ("Get all Contact IDs, First Names, and Last Names.", "SELECT Id, FirstName, LastName FROM Contact"),
        ("Get all open Opportunities with ID, Name, and Stage.", "SELECT Id, Name, StageName FROM Opportunity WHERE IsClosed = FALSE"),
        ("Get Leads where Status is 'Open – Not Contacted'.", "SELECT Id, Name FROM Lead WHERE Status = 'Open - Not Contacted'"),
        ("Get Cases where Priority is 'High'.", "SELECT Id, Subject FROM Case WHERE Priority = 'High'"),
        ("Get all Accounts where Industry is 'Technology'.", "SELECT Id, Name FROM Account WHERE Industry = 'Technology'"),
        ("Count Contacts where Mailing Country is 'USA'.", "SELECT COUNT(Id) FROM Contact WHERE MailingCountry = 'USA'"),
        ("Get User Names where IsActive is true.", "SELECT Id, Name FROM User WHERE IsActive = TRUE"),
        ("Get Leads created in the last 30 days with Email.", "SELECT Id, Email FROM Lead WHERE CreatedDate = LAST_N_DAYS:30"),
        ("Get Opportunities closing in the next 3 months.", "SELECT Id, Name FROM Opportunity WHERE CloseDate = NEXT_N_MONTHS:3"),

        # Parent-Child Queries (11–20)
        ("Get Accounts with their related Contacts.", "SELECT Id, Name, (SELECT Id, FirstName, LastName FROM Contacts) FROM Account"),
        ("Get Contacts with their related Account Names.", "SELECT Id, FirstName, LastName, Account.Name FROM Contact"),
        ("Get quotelines with related quote Name and Subject.", "SELECT Id, Subject, Account.Name FROM Case"),
        ("Get Opportunities related to Accounts in 'Finance' Industry.", "SELECT Id, Name FROM Opportunity WHERE Account.Industry = 'Finance'"),
        ("Get Account Names with their Owner Names.", "SELECT Id, Name, Owner.Name FROM Account"),
        ("Get Contacts with CreatedBy User Names.", "SELECT Id, FirstName, LastName, CreatedBy.Name FROM Contact"),
        ("Get Opportunities with their related Tasks.", "SELECT Id, Name, (SELECT Id, Subject FROM Tasks) FROM Opportunity"),
        ("Get Cases with their Case Comments.", "SELECT Id, Subject, (SELECT Id, CommentBody FROM CaseComments) FROM Case"),
        ("Get Quotes with their Quote Line Items.", "SELECT Id, Name, (SELECT Id, Product2.Name, Quantity FROM QuoteLineItems) FROM Quote"),
        ("Get Accounts with their Orders.", "SELECT Id, Name, (SELECT Id, Name FROM Orders) FROM Account"),

        # WHERE Clauses (21–30)
        ("Get Accounts where Name starts with 'Acme'.", "SELECT Id, Name FROM Account WHERE Name LIKE 'Acme%'"),
        ("Get Contacts where Mailing State is 'CA' or 'TX'.", "SELECT Id, FirstName, MailingState FROM Contact WHERE MailingState IN ('CA', 'TX')"),
        ("Get Leads with AnnualRevenue greater than 1 million.", "SELECT Id, Name FROM Lead WHERE AnnualRevenue > 1000000"),
        ("Get Opportunities where Amount is less than or equal to 50,000.", "SELECT Id, Name FROM Opportunity WHERE Amount <= 50000"),
        ("show me all Cases where Status equal to not 'Closed'.", "SELECT Id, Subject FROM Case WHERE Status != 'Closed'"),
        ("Get Accounts created after January 1, 2024.", "SELECT Id, Name FROM Account WHERE CreatedDate > 2024-01-01T00:00:00Z"),
        ("Get Contacts where Mailing City is 'Mumbai'.", "SELECT Id, FirstName FROM Contact WHERE MailingCity = 'Mumbai'"),
        ("Get Opportunities where StageName is 'Prospecting' or 'Qualification'.", "SELECT Id, Name FROM Opportunity WHERE StageName IN ('Prospecting', 'Qualification')"),
        ("Get Users where Profile Name is 'System Administrator'.", "SELECT Id, Name FROM User WHERE Profile.Name = 'System Administrator'"),
        ("Get Leads where IsConverted is false.", "SELECT Id, Name FROM Lead WHERE IsConverted = FALSE"),

        # Date Literals (31–40)
        ("Get Accounts created today.", "SELECT Id, Name FROM Account WHERE CreatedDate = TODAY"),
        ("Get Cases modified yesterday.", "SELECT Id, Subject FROM Case WHERE LastModifiedDate = YESTERDAY"),
        ("Get Contacts created this week.", "SELECT Id, FirstName FROM Contact WHERE CreatedDate = THIS_WEEK"),
        ("Get Opportunities closing this quarter.", "SELECT Id, Name FROM Opportunity WHERE CloseDate = THIS_QUARTER"),
        ("Get Leads created in the last 7 days.", "SELECT Id, Name FROM Lead WHERE CreatedDate = LAST_N_DAYS:7"),
        ("Get Opportunities closing in the next 14 days.", "SELECT Id, Name FROM Opportunity WHERE CloseDate = NEXT_N_DAYS:14"),
        ("Get Accounts created in the last 3 months.", "SELECT Id, Name FROM Account WHERE CreatedDate = LAST_N_MONTHS:3"),
        ("Get Cases created before last year.", "SELECT Id, Subject FROM Case WHERE CreatedDate < LAST_YEAR"),
        ("Get Opportunities created in the past year.", "SELECT Id, Name FROM Opportunity WHERE CreatedDate = LAST_365_DAYS"),
        ("Get Users who logged in one day ago.", "SELECT Id, Name FROM User WHERE LastLoginDate = YESTERDAY"),

        # GROUP BY & Aggregation (41–50)
        ("Count all Accounts.", "SELECT COUNT() FROM Account"),
        ("Count Accounts grouped by Industry.", "SELECT Industry, COUNT(Id) FROM Account GROUP BY Industry"),
        ("Get average AnnualRevenue grouped by Type.", "SELECT Type, AVG(AnnualRevenue) FROM Account GROUP BY Type"),
        ("Get total Opportunity Amounts grouped by Owner.", "SELECT OwnerId, SUM(Amount) FROM Opportunity GROUP BY OwnerId"),
        ("Get max and min Opportunity Amounts grouped by CloseDate.", "SELECT CloseDate, MAX(Amount), MIN(Amount) FROM Opportunity GROUP BY CloseDate"),
        ("Count Leads grouped by LeadSource.", "SELECT LeadSource, COUNT(Id) FROM Lead GROUP BY LeadSource"),
        ("Count Cases grouped by year.", "SELECT CALENDAR_YEAR(CreatedDate), COUNT(Id) FROM Case GROUP BY CALENDAR_YEAR(CreatedDate)"),
        ("Count Accounts grouped by Industry and Type using ROLLUP.", "SELECT Industry, Type, COUNT(Id) FROM Account GROUP BY ROLLUP(Industry, Type)"),
        ("Count Opportunities using CUBE on Stage and Type.", "SELECT StageName, Type, COUNT(Id) FROM Opportunity GROUP BY CUBE(StageName, Type)"),
        ("Count Opportunities grouped by AccountId.", "SELECT AccountId, COUNT(Id) FROM Opportunity GROUP BY AccountId"),

        # ORDER BY / LIMIT / OFFSET (51–60)
        ("Get top 10 most recently created Accounts.", "SELECT Id, Name, CreatedDate FROM Account ORDER BY CreatedDate DESC LIMIT 10"),
        ("Get top 5 Opportunities by Amount.", "SELECT Id, Name, Amount FROM Opportunity ORDER BY Amount DESC LIMIT 5"),
        ("Get Contacts ordered by LastName ascending.", "SELECT Id, FirstName, LastName FROM Contact ORDER BY LastName ASC"),
        ("Get 50 Contacts after skipping the first 50.", "SELECT Id, FirstName, LastName FROM Contact ORDER BY LastName ASC LIMIT 50 OFFSET 50"),
        ("Get Accounts ordered by AnnualRevenue with nulls last.", "SELECT Id, Name, AnnualRevenue FROM Account ORDER BY AnnualRevenue NULLS LAST"),
        ("Get closed-won Opportunities ordered by CreatedDate.", "SELECT Id, Name FROM Opportunity WHERE StageName = 'Closed Won' ORDER BY CreatedDate DESC"),
        ("Get top 20 High priority Cases by LastModifiedDate.", "SELECT Id, Subject FROM Case WHERE Priority = 'High' ORDER BY LastModifiedDate DESC LIMIT 20"),
        ("Get User who last logged in.", "SELECT Id, Name, LastLoginDate FROM User ORDER BY LastLoginDate DESC LIMIT 1"),
        ("Get open Tasks ordered by DueDate.", "SELECT Id, Subject, ActivityDate FROM Task WHERE Status != 'Completed' ORDER BY ActivityDate ASC"),
        ("Get Quotes ordered by ExpirationDate.", "SELECT Id, Name, ExpirationDate FROM Quote ORDER BY ExpirationDate DESC"),

        # Subqueries (61–70)
        ("Get Accounts with Opportunities where Amount > 100000.", "SELECT Id, Name, (SELECT Id, Name FROM Opportunities WHERE Amount > 100000) FROM Account"),
        ("Get Accounts without any closed Cases.", "SELECT Id, Name FROM Account WHERE Id NOT IN (SELECT AccountId FROM Case WHERE Status = 'Closed')"),
        ("Get Contacts with Cases where Priority = 'High'.", "SELECT Id, Name, (SELECT Id, Subject FROM Cases WHERE Priority = 'High') FROM Contact"),
        ("Get Opportunities for Accounts in the 'Finance' industry.", "SELECT Id, Name FROM Opportunity WHERE Account.Industry = 'Finance'"),
        ("Get Accounts where Name IN ('Acme', 'GlobalTech').", "SELECT Id, Name FROM Account WHERE Name IN ('Acme', 'GlobalTech')"),
        ("Get Opportunities where StageName IN ('Prospecting', 'Closed Won').", "SELECT Id, Name FROM Opportunity WHERE StageName IN ('Prospecting', 'Closed Won')"),
        ("Get Contacts where City NOT IN ('Paris', 'Berlin').", "SELECT Id, FirstName, MailingCity FROM Contact WHERE MailingCity NOT IN ('Paris', 'Berlin')"),
        ("Get Accounts created after variable date.", "SELECT Id, Name FROM Account WHERE CreatedDate > :someDateVariable"),
        ("Get Accounts in last 30 days without Closed-Won Opportunities.", "SELECT Id, Name FROM Account WHERE CreatedDate = LAST_N_DAYS:30 AND Id NOT IN (SELECT AccountId FROM Opportunity WHERE StageName = 'Closed Won')"),
        ("Get Leads where IsConverted = true.", "SELECT Id, Name FROM Lead WHERE IsConverted = TRUE"),

        # Sharing, Security, Deleted Rows (71–80)
        ("Get all Accounts with enforced sharing.", "SELECT Id, Name FROM Account WITH SHARING"),
        ("Get Opportunities with Owner.Name using sharing.", "SELECT Id, Name, Owner.Name FROM Opportunity WITH SHARING"),
        ("Get deleted Contacts using ALL ROWS.", "SELECT Id, FirstName, IsDeleted FROM Contact WHERE IsDeleted = TRUE ALL ROWS"),
        ("Get converted Leads using ALL ROWS.", "SELECT Id, Name FROM Lead WHERE IsConverted = TRUE ALL ROWS"),
        ("Get Account where Id = specific ID.", "SELECT Id, Name FROM Account WHERE Id = '001XXXXXXXXXXXX'"),
        ("Get Users where UserRole.Name is 'Sales Manager'.", "SELECT Id, Name FROM User WHERE UserRole.Name = 'Sales Manager'"),
        ("Get Accounts where Owner.Profile.Name is 'Partner Community User'.", "SELECT Id, Name FROM Account WHERE Owner.Profile.Name = 'Partner Community User'"),
        ("Get Opportunities where TeamMemberRole = 'Sales Rep'.", "SELECT OpportunityId FROM OpportunityTeamMember WHERE TeamMemberRole = 'Sales Rep'"),
        ("Get Contacts for Accounts owned by System Admin.", "SELECT Id, FirstName, LastName FROM Contact WHERE Account.Owner.Profile.Name = 'System Administrator'"),
        ("Count Cases for users in Partner profile.", "SELECT COUNT(Id) FROM Case WHERE CreatedBy.Profile.Name = 'Partner Community User'"),

        # Dynamic SOQL Patterns (81–90)
        ("Build dynamic SOQL to get Account Names.", "String query = 'SELECT Name FROM Account'"),
        ("Build SOQL using Apex variable for country.", "String query = 'SELECT Id, Name FROM Contact WHERE MailingCountry = :selectedCountry'"),
        ("Use a limit variable in SOQL query on Accounts.", "String query = 'SELECT Id, Name FROM Account LIMIT :limitSize'"),
        ("Use name prefix variable in Account name filter.", "String query = 'SELECT Id, Name FROM Account WHERE Name LIKE :prefix + '%''"),
        ("Use from/to date variables to filter Accounts.", "String query = 'SELECT Id, Name FROM Account WHERE CreatedDate >= :startDate AND CreatedDate <= :endDate'"),
        ("Filter Accounts with CreatedDate = TODAY.", "String query = 'SELECT Id, Name FROM Account WHERE CreatedDate = TODAY'"),
        ("Query User record using variable user name.", "String query = 'SELECT Id, Name FROM User WHERE Name = :userName'"),
        ("Get Opportunities with Amount > X and CloseDate < Y.", "String query = 'SELECT Id, Name FROM Opportunity WHERE Amount > :minAmount AND CloseDate < :closeDate'"),
        ("Search Cases where Subject includes dynamic keyword.", "String query = 'SELECT Id, Subject FROM Case WHERE Subject LIKE \'%' + keyword + '%\'"),
        ("Use dynamic object name in SOQL string.", "String query = 'SELECT Id FROM ' + objectName"),

        # FOR VIEW / UPDATE (91–100)
        ("Get Accounts using FOR VIEW.", "SELECT Id, Name FROM Account FOR VIEW"),
        ("Get Contacts using FOR REFERENCE.", "SELECT Id, Name FROM Contact FOR REFERENCE"),
        ("Get Account Names FOR VIEW.", "SELECT Name FROM Account FOR VIEW"),
        ("Get Contact Names FOR REFERENCE.", "SELECT FirstName, LastName FROM Contact FOR REFERENCE"),
        ("Get Opportunities ordered by Date FOR VIEW.", "SELECT Id, Name FROM Opportunity ORDER BY CloseDate DESC FOR VIEW"),
        ("Get Account by ID using FOR VIEW.", "SELECT Id, Name FROM Account WHERE Id = '001XXXXXXXXXXXX' FOR VIEW"),
        ("Lock Contact records using FOR UPDATE.", "SELECT Id, FirstName FROM Contact WHERE MailingCity = 'New York' FOR UPDATE"),
        ("Lock Prospects in Qualification using FOR UPDATE.", "SELECT Id, Name FROM Lead WHERE Status = 'Qualification' FOR UPDATE"),
        ("Lock Account records using FOR UPDATE.", "SELECT Id, Name FROM Account WHERE Industry = 'Technology' FOR UPDATE"),
        ("Lock new Case records using FOR UPDATE.", "SELECT Id, Subject FROM Case WHERE CreatedDate = TODAY FOR UPDATE")
    ]

    return prompts_answers

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
    print("SOQL Query Generator 100 Prompts Tester")
    print("----------------------------------")

    # Get prompts and expected answers
    prompt_answer_pairs = get_prompts_and_answers()
    print(f"Found {len(prompt_answer_pairs)} prompt-answer pairs.")

    # Initialize query generator
    query_generator = initialize_query_generator()

    # Check if modular architecture is available
    print(f"MODULAR_ARCHITECTURE_AVAILABLE: {query_generator.use_modular_architecture}")
    if query_generator.use_modular_architecture:
        print("Using modular architecture")
        print(f"Number of models: {len(query_generator.model_dispatcher.models)}")
        for i, model in enumerate(query_generator.model_dispatcher.models):
            print(f"Model {i+1}: {model.__class__.__name__}")
    else:
        print("Not using modular architecture")

    # Test each prompt
    results = []
    for i, (prompt, expected_answer) in enumerate(prompt_answer_pairs):
        print(f"\nTesting prompt {i+1}/100: \"{prompt}\"")
        print(f"Expected answer: {expected_answer}")

        # Check which model handles this prompt
        handling_model = None
        handling_model_instance = None
        if query_generator.use_modular_architecture:
            for model in query_generator.model_dispatcher.models:
                if model.can_handle(prompt):
                    handling_model = model.__class__.__name__
                    handling_model_instance = model
                    break
            if handling_model:
                print(f"Handling model: {handling_model}")

        # Debug: Identify the object for this prompt
        identified_object = None
        if handling_model_instance:
            identified_object = handling_model_instance._identify_object(prompt)
        else:
            # If no specific model handles it, use the base identification logic
            identified_object = query_generator._identify_object(prompt)

        print(f"Identified object: {identified_object}")

        try:
            # Generate query
            generated_query = query_generator.generate_query(prompt)
            print(f"Generated answer: {generated_query}")

            # Compare with expected answer
            is_match, similarity, differences = compare_queries(generated_query, expected_answer)

            print(f"Match: {'✅' if is_match else '❌'} (similarity: {similarity:.2f})")
            if not is_match and differences:
                if differences['missing']:
                    print(f"Missing terms: {', '.join(differences['missing'])}")
                if differences['extra']:
                    print(f"Extra terms: {', '.join(differences['extra'])}")

            results.append({
                'prompt': prompt,
                'expected': expected_answer,
                'generated': generated_query,
                'is_match': is_match,
                'similarity': similarity,
                'differences': differences,
                'handling_model': handling_model,
                'identified_object': identified_object
            })

        except Exception as e:
            results.append({
                'prompt': prompt,
                'expected': expected_answer,
                'generated': None,
                'is_match': False,
                'similarity': 0,
                'error': str(e),
                'handling_model': handling_model,
                'identified_object': identified_object
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

    # Group results by model
    model_results = {}
    for r in results:
        model = r.get('handling_model', 'Unknown')
        if model not in model_results:
            model_results[model] = {
                'total': 0,
                'matches': 0,
                'errors': 0
            }
        model_results[model]['total'] += 1
        if r.get('is_match', False):
            model_results[model]['matches'] += 1
        if 'error' in r:
            model_results[model]['errors'] += 1

    print("\nResults by model:")
    for model, stats in model_results.items():
        match_rate = stats['matches'] / stats['total'] * 100 if stats['total'] > 0 else 0
        print(f"  {model}: {stats['matches']}/{stats['total']} matches ({match_rate:.1f}%)")

    # Summarize object identification results
    print("\nObject identification results:")
    object_counts = {}
    for r in results:
        obj = r.get('identified_object', 'None')
        if obj not in object_counts:
            object_counts[obj] = {
                'total': 0,
                'matches': 0,
                'errors': 0
            }
        object_counts[obj]['total'] += 1
        if r.get('is_match', False):
            object_counts[obj]['matches'] += 1
        if 'error' in r:
            object_counts[obj]['errors'] += 1

    # Sort by total count (descending)
    sorted_objects = sorted(object_counts.items(), key=lambda x: x[1]['total'], reverse=True)

    for obj, stats in sorted_objects:
        match_rate = stats['matches'] / stats['total'] * 100 if stats['total'] > 0 else 0
        print(f"  {obj}: {stats['matches']}/{stats['total']} matches ({match_rate:.1f}%)")

    # Print details of a few specific prompts
    print("\nDetails of a few specific prompts:")

    # Basic query
    basic_query_prompt = "Get all Account IDs and Names."
    basic_query_result = next((r for r in results if r['prompt'] == basic_query_prompt), None)
    if basic_query_result:
        print(f"\nBasic Query: \"{basic_query_prompt}\"")
        print(f"Model: {basic_query_result.get('handling_model', 'Unknown')}")
        print(f"Identified object: {basic_query_result.get('identified_object', 'None')}")
        print(f"Expected: {basic_query_result['expected']}")
        print(f"Generated: {basic_query_result['generated']}")
        print(f"Match: {'✅' if basic_query_result['is_match'] else '❌'} (similarity: {basic_query_result['similarity']:.2f})")
        if not basic_query_result['is_match'] and basic_query_result['differences']:
            if basic_query_result['differences']['missing']:
                print(f"Missing terms: {', '.join(basic_query_result['differences']['missing'])}")
            if basic_query_result['differences']['extra']:
                print(f"Extra terms: {', '.join(basic_query_result['differences']['extra'])}")

    # Relationship query
    relationship_query_prompt = "Get Accounts with their related Contacts."
    relationship_query_result = next((r for r in results if r['prompt'] == relationship_query_prompt), None)
    if relationship_query_result:
        print(f"\nRelationship Query: \"{relationship_query_prompt}\"")
        print(f"Model: {relationship_query_result.get('handling_model', 'Unknown')}")
        print(f"Identified object: {relationship_query_result.get('identified_object', 'None')}")
        print(f"Expected: {relationship_query_result['expected']}")
        print(f"Generated: {relationship_query_result['generated']}")
        print(f"Match: {'✅' if relationship_query_result['is_match'] else '❌'} (similarity: {relationship_query_result['similarity']:.2f})")
        if not relationship_query_result['is_match'] and relationship_query_result['differences']:
            if relationship_query_result['differences']['missing']:
                print(f"Missing terms: {', '.join(relationship_query_result['differences']['missing'])}")
            if relationship_query_result['differences']['extra']:
                print(f"Extra terms: {', '.join(relationship_query_result['differences']['extra'])}")

    # Aggregation query
    aggregation_query_prompt = "Count all Accounts."
    aggregation_query_result = next((r for r in results if r['prompt'] == aggregation_query_prompt), None)
    if aggregation_query_result:
        print(f"\nAggregation Query: \"{aggregation_query_prompt}\"")
        print(f"Model: {aggregation_query_result.get('handling_model', 'Unknown')}")
        print(f"Identified object: {aggregation_query_result.get('identified_object', 'None')}")
        print(f"Expected: {aggregation_query_result['expected']}")
        print(f"Generated: {aggregation_query_result['generated']}")
        print(f"Match: {'✅' if aggregation_query_result['is_match'] else '❌'} (similarity: {aggregation_query_result['similarity']:.2f})")
        if not aggregation_query_result['is_match'] and aggregation_query_result['differences']:
            if aggregation_query_result['differences']['missing']:
                print(f"Missing terms: {', '.join(aggregation_query_result['differences']['missing'])}")
            if aggregation_query_result['differences']['extra']:
                print(f"Extra terms: {', '.join(aggregation_query_result['differences']['extra'])}")

    # Date filter query
    date_filter_query_prompt = "Get Accounts created today."
    date_filter_query_result = next((r for r in results if r['prompt'] == date_filter_query_prompt), None)
    if date_filter_query_result:
        print(f"\nDate Filter Query: \"{date_filter_query_prompt}\"")
        print(f"Model: {date_filter_query_result.get('handling_model', 'Unknown')}")
        print(f"Identified object: {date_filter_query_result.get('identified_object', 'None')}")
        print(f"Expected: {date_filter_query_result['expected']}")
        print(f"Generated: {date_filter_query_result['generated']}")
        print(f"Match: {'✅' if date_filter_query_result['is_match'] else '❌'} (similarity: {date_filter_query_result['similarity']:.2f})")
        if not date_filter_query_result['is_match'] and date_filter_query_result['differences']:
            if date_filter_query_result['differences']['missing']:
                print(f"Missing terms: {', '.join(date_filter_query_result['differences']['missing'])}")
            if date_filter_query_result['differences']['extra']:
                print(f"Extra terms: {', '.join(date_filter_query_result['differences']['extra'])}")

    # Where clause query
    where_clause_query_prompt = "Get Accounts where Industry is 'Technology'."
    where_clause_query_result = next((r for r in results if r['prompt'] == where_clause_query_prompt), None)
    if where_clause_query_result:
        print(f"\nWhere Clause Query: \"{where_clause_query_prompt}\"")
        print(f"Model: {where_clause_query_result.get('handling_model', 'Unknown')}")
        print(f"Identified object: {where_clause_query_result.get('identified_object', 'None')}")
        print(f"Expected: {where_clause_query_result['expected']}")
        print(f"Generated: {where_clause_query_result['generated']}")
        print(f"Match: {'✅' if where_clause_query_result['is_match'] else '❌'} (similarity: {where_clause_query_result['similarity']:.2f})")
        if not where_clause_query_result['is_match'] and where_clause_query_result['differences']:
            if where_clause_query_result['differences']['missing']:
                print(f"Missing terms: {', '.join(where_clause_query_result['differences']['missing'])}")
            if where_clause_query_result['differences']['extra']:
                print(f"Extra terms: {', '.join(where_clause_query_result['differences']['extra'])}")

    # Advanced features query
    advanced_features_query_prompt = "Get Accounts using FOR VIEW."
    advanced_features_query_result = next((r for r in results if r['prompt'] == advanced_features_query_prompt), None)
    if advanced_features_query_result:
        print(f"\nAdvanced Features Query: \"{advanced_features_query_prompt}\"")
        print(f"Model: {advanced_features_query_result.get('handling_model', 'Unknown')}")
        print(f"Identified object: {advanced_features_query_result.get('identified_object', 'None')}")
        print(f"Expected: {advanced_features_query_result['expected']}")
        print(f"Generated: {advanced_features_query_result['generated']}")
        print(f"Match: {'✅' if advanced_features_query_result['is_match'] else '❌'} (similarity: {advanced_features_query_result['similarity']:.2f})")
        if not advanced_features_query_result['is_match'] and advanced_features_query_result['differences']:
            if advanced_features_query_result['differences']['missing']:
                print(f"Missing terms: {', '.join(advanced_features_query_result['differences']['missing'])}")
            if advanced_features_query_result['differences']['extra']:
                print(f"Extra terms: {', '.join(advanced_features_query_result['differences']['extra'])}")

    # Sorting query
    sorting_query_prompt = "Get Contacts ordered by LastName ascending."
    sorting_query_result = next((r for r in results if r['prompt'] == sorting_query_prompt), None)
    if sorting_query_result:
        print(f"\nSorting Query: \"{sorting_query_prompt}\"")
        print(f"Model: {sorting_query_result.get('handling_model', 'Unknown')}")
        print(f"Identified object: {sorting_query_result.get('identified_object', 'None')}")
        print(f"Expected: {sorting_query_result['expected']}")
        print(f"Generated: {sorting_query_result['generated']}")
        print(f"Match: {'✅' if sorting_query_result['is_match'] else '❌'} (similarity: {sorting_query_result['similarity']:.2f})")
        if not sorting_query_result['is_match'] and sorting_query_result['differences']:
            if sorting_query_result['differences']['missing']:
                print(f"Missing terms: {', '.join(sorting_query_result['differences']['missing'])}")
            if sorting_query_result['differences']['extra']:
                print(f"Extra terms: {', '.join(sorting_query_result['differences']['extra'])}")

if __name__ == "__main__":
    main()
