# SOQL Query Generator

A natural language processing (NLP) application that converts user questions into Salesforce Object Query Language (SOQL) queries.

## Overview

This application allows users to ask questions in natural language about their Salesforce data, and it will generate the appropriate SOQL query to retrieve that data. Instead of having to remember SOQL syntax and field names, users can simply ask questions like "Show me the top 5 accounts by revenue" or "Find contacts with email addresses that contain 'example.com'".

## Features

- Convert natural language questions to SOQL queries
- Support for all Salesforce objects and fields defined in the metadata
- Support for relationship queries:
  - Parent-to-child relationships (e.g., "Show me accounts with their contacts")
  - Child-to-parent relationships (e.g., "List contacts of account name is 'acme'")
  - Indirect relationships (e.g., "List quote line items of an account") that require traversing multiple levels of relationships
- Load metadata from Excel file (Salesforce_Complete_Metadata.xlsx)
- Interactive command-line interface
- Ability to process single questions via command-line arguments
- Extensible architecture for adding more objects and fields

## Requirements

- Python 3.7+
- pandas and openpyxl (for Excel file handling)
- Salesforce metadata (objects and fields)
   - The application uses `Salesforce_Complete_Metadata.xlsx` for metadata information
   - If the Excel file is not available, the application will use sample metadata
- SOQL documentation (optional, for reference)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/sfdcsoql.git
   cd sfdcsoql
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

For detailed instructions on how to set up and use the SOQL Query Generator, please refer to the [User Guide](guide.md).

### Interactive Mode

Run the application in interactive mode to enter multiple questions:

```
python main.py --interactive
```

or simply:

```
python main.py
```

### Single Question Mode

Process a single question:

```
python main.py --question "Show me the top 5 accounts by revenue"
```

### Example Script

Try the example script to see how the SOQL Query Generator works with different types of questions:

```
python example.py
```

## How It Works

The application consists of three main components:

1. **Metadata Loader**: Loads and manages Salesforce metadata (objects, fields, and relationships) from an Excel file or uses sample data if the Excel file is not available.
2. **NLP Model**: Processes natural language questions and identifies the components needed for a SOQL query.
3. **Query Generator**: Constructs valid SOQL queries based on the NLP model's output.

### NLP Approach

The current implementation uses a rule-based approach with keyword matching to identify:
- The Salesforce object to query
- Fields to include in the SELECT clause
- Conditions for the WHERE clause
- Ordering and limits
- Relationships between objects (parent-to-child and child-to-parent)

#### Relationship Queries

The application supports three types of relationship queries:

1. **Parent-to-Child Relationship Queries**: These queries retrieve records from a parent object along with related records from a child object. For example, "Show me accounts with their contacts" will generate a SOQL query with a subquery in the SELECT clause:
   ```sql
   SELECT [Account fields], (SELECT [Contact fields] FROM Contacts) FROM Account
   ```

2. **Child-to-Parent Relationship Queries**: These queries retrieve records from a child object based on conditions on the parent object. For example, "List contacts of account name is 'acme'" will generate a SOQL query with a condition using dot notation:
   ```sql
   SELECT [Contact fields] FROM Contact WHERE Account.Name = 'acme'
   ```

3. **Bidirectional Relationship Queries**: The application can automatically convert between parent-to-child and child-to-parent queries when appropriate. For example, a question like "List contacts of account name is 'acme'" can be expressed as either a child-to-parent query or a parent-to-child query:

   Child-to-Parent:
   ```sql
   SELECT [Contact fields] FROM Contact WHERE Account.Name = 'acme'
   ```

   Parent-to-Child (automatically converted):
   ```sql
   SELECT [Account fields], (SELECT [Contact fields] FROM Contacts WHERE Name = 'acme') FROM Account
   ```

   This bidirectional conversion ensures that the most appropriate query is generated based on the question, and allows for more flexibility in how users can phrase their questions.

4. **Indirect Relationship Queries**: The application can handle queries that involve indirect relationships, where objects are related through multiple levels of parent-child relationships. For example, "List quote line items of an account" requires traversing from Account to Opportunity to Quote to QuoteLineItem. The application generates nested subqueries to handle these indirect relationships:
   ```sql
   SELECT [Account fields], 
          (SELECT [Opportunity fields], 
                 (SELECT [Quote fields], 
                        (SELECT [QuoteLineItem fields] FROM QuoteLineItems) 
                 FROM Quotes) 
          FROM Opportunities) 
   FROM Account
   ```

   The application can also handle multiple indirect relationships in a single query. For example, "List quote line items and orders of an account" will generate a query that includes both QuoteLineItems and Orders:
   ```sql
   SELECT [Account fields], 
          (SELECT [Opportunity fields], 
                 (SELECT [Quote fields], 
                        (SELECT [QuoteLineItem fields] FROM QuoteLineItems),
                        (SELECT [Order fields] FROM Orders) 
                 FROM Quotes) 
          FROM Opportunities) 
   FROM Account
   ```

In a production environment, this could be enhanced with more sophisticated NLP techniques such as:
- Named entity recognition to identify objects and fields
- Intent classification to determine query type
- Fine-tuned language models for better understanding of complex questions

## Extending the Application

### Adding New Salesforce Objects

To add support for additional Salesforce objects, you can:
1. Modify the Excel file `Salesforce_Complete_Metadata.xlsx` to include the new objects and their fields
2. Modify the `add_sample_metadata` method in `metadata_loader.py` 
3. Provide your own metadata files in the `data/metadata` directory

### Improving NLP Capabilities

The NLP model in `nlp_model.py` can be enhanced with more sophisticated techniques:
- Integration with libraries like spaCy or Hugging Face Transformers
- Training on a dataset of question-query pairs
- Adding support for more complex query patterns

## Limitations

- The current implementation uses a simplified rule-based approach for NLP
- Limited support for complex queries (subqueries, aggregations, etc.)
- No integration with actual Salesforce API for validation or execution

## Future Enhancements

- Web interface for easier interaction
- Integration with Salesforce API to execute generated queries
- Support for more complex SOQL features (GROUP BY, HAVING, etc.)
- Machine learning-based NLP model for better question understanding
- Query validation and error handling

## License

This project is licensed under the MIT License - see the LICENSE file for details.
