from src.models.where_clause_model import WhereClauseModel

def test_with_debug():
    model = WhereClauseModel()
    question = "Get Opportunities where Amount is less than or equal to 50,000."

    # Debug: Print the lowercase question
    question_lower = question.lower()
    print(f"Question (lowercase): {question_lower}")

    # Debug: Check the condition parts
    print(f"'opportunity' in question_lower: {'opportunity' in question_lower}")
    print(f"'amount' in question_lower: {'amount' in question_lower}")
    print(f"'less than' in question_lower: {'less than' in question_lower}")
    print(f"'equal to' in question_lower: {'equal to' in question_lower}")
    print(f"'<=' in question_lower: {'<=' in question_lower}")
    print(f"'50,000' in question_lower: {'50,000' in question_lower}")
    print(f"'50000' in question_lower: {'50000' in question_lower}")

    # Debug: Check the combined condition
    combined_condition = (("less than" in question_lower and "equal to" in question_lower) or 
                          "<=" in question_lower or 
                          "50,000" in question_lower or 
                          "50000" in question_lower)
    print(f"Combined condition: {combined_condition}")

    # Generate the query
    generated_query = model.generate_query(question)
    print(f"\nGenerated query: {generated_query}")

if __name__ == "__main__":
    test_with_debug()
