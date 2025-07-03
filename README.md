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

- Python 3.8+
- pandas and openpyxl (for Excel file handling)
- Salesforce metadata (objects and fields)
   - The application uses `Salesforce_Complete_Metadata.xlsx` for metadata information
   - If the Excel file is not available, the application will use sample metadata
- SOQL documentation (optional, for reference)

## Project Structure

The project is organized into the following directories:

- `src/`: Source code
  - `models/`: Query generation models
    - `base_model.py`: Base class for all SOQL models
    - `where_clause_model.py`: Model for handling WHERE clauses
    - `advanced_features_model.py`: Model for advanced SOQL features
    - `aggregation_model.py`: Model for aggregation queries
    - `basic_query_model.py`: Model for basic queries
    - `date_filter_model.py`: Model for date filters
    - `relationship_model.py`: Model for relationship queries
    - `sorting_model.py`: Model for ORDER BY clauses
  - `services/`: Web services and utilities
    - `salesforce_metadata_service.py`: Command-line tool for retrieving Salesforce metadata
    - `salesforce_metadata_api.py`: API for retrieving Salesforce metadata
    - `salesforce_prompt_service.py`: API for processing natural language prompts
    - `generate_metadata.py`: Tool for generating metadata files
  - `utils/`: Utility modules
    - `metadata_loader.py`: Loads Salesforce metadata
    - `model_dispatcher.py`: Dispatches queries to appropriate models
    - `nlp_model.py`: Main NLP model for query generation
- `tests/`: Test files
  - Various test scripts for different components
- `docs/`: Documentation
  - `DEPLOYMENT_GUIDE.md`: Guide for deploying services
  - `SALESFORCE_METADATA_SERVICE_README.md`: Documentation for metadata service
  - `SALESFORCE_PROMPT_SERVICE_README.md`: Documentation for prompt service
  - `guide.md`: General usage guide
- `data/`: Data files
  - `metadata/`: Salesforce metadata files

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/sfdcsoql.git
   cd sfdcsoql
   ```

2. Set up the Python environment using the provided setup scripts:

   **For Unix/Linux/Mac:**
   ```
   chmod +x setup.sh
   ./setup.sh
   ```

   **For Windows:**
   ```
   setup.bat
   ```

   This will:
   - Check if Python 3.8+ is installed
   - Create a virtual environment
   - Install all required dependencies

3. Alternatively, you can manually set up the environment:
   ```
   # Create and activate a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

4. Activate the virtual environment (if not already activated):
   ```
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. Generate metadata files from your Salesforce metadata Excel file:
   ```
   python src/services/generate_metadata.py --excel-file your_metadata.xlsx --output-dir data/metadata
   ```
   This will create JSON files for each Salesforce object in your metadata Excel file.

## Usage

For detailed instructions on how to set up and use the SOQL Query Generator, please refer to the [User Guide](guide.md).

### Interactive Mode

Run the application in interactive mode to enter multiple questions:

```
python src/utils/nlp_model.py --interactive
```

or simply:

```
python src/utils/nlp_model.py
```

### Single Question Mode

Process a single question:

```
python src/utils/nlp_model.py --question "Show me the top 5 accounts by revenue"
```

### Example Script

Try the example script to see how the SOQL Query Generator works with different types of questions:

```
python tests/test_prompts.py
```

Note: The example script demonstrates various types of queries including basic queries, parent-to-child relationship queries, and child-to-parent relationship queries.

## How It Works

The application consists of three main components:

1. **Metadata Loader**: Loads and manages Salesforce metadata (objects, fields, and relationships) from an Excel file or uses sample data if the Excel file is not available.
2. **NLP Model**: Processes natural language questions and identifies the components needed for a SOQL query.
3. **Query Generator**: Constructs valid SOQL queries based on the NLP model's output.

### Modular Architecture

The application now uses a modular architecture where different types of queries are handled by specialized models:

1. **BaseSOQLModel**: The base class for all specialized models.
2. **BasicQueryModel**: Handles simple queries without complex conditions or features.
3. **WhereClauseModel**: Handles queries with WHERE clauses for filtering records.
4. **AggregationModel**: Handles queries with aggregate functions (COUNT, SUM, AVG, etc.) and GROUP BY clauses.
5. **DateFilterModel**: Handles queries with date literals and range filters.
6. **RelationshipModel**: Handles queries with parent-to-child and child-to-parent relationships.
7. **SortingModel**: Handles queries with ORDER BY, LIMIT, and OFFSET clauses.
8. **AdvancedFeaturesModel**: Handles queries with advanced features like ALL ROWS, FOR VIEW, FOR REFERENCE, and FOR UPDATE clauses.

The **ModelDispatcher** selects the appropriate model based on the user's prompt. If no specialized model can handle the prompt, it falls back to the basic query model.

This modular architecture makes it easier to:
- Add support for new query types
- Improve the accuracy of specific query types
- Maintain and test the codebase

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
2. Run the `generate_metadata.py` script to generate updated metadata files
3. Modify the `add_sample_metadata` method in `metadata_loader.py` 
4. Provide your own metadata files in the `data/metadata` directory

### Excel File Format

The `generate_metadata.py` script expects an Excel file with the following columns:
- `CustomObject`: The name of the Salesforce object (e.g., "Account", "Contact")
- `CustomField`: The API name of the field (e.g., "Name", "Email")
- `Field Type`: The data type of the field (e.g., "string", "picklist", "reference")
- `Lookup Object`: For reference fields, the object they reference (e.g., "Account" for a lookup to Account)

Example Excel file structure:

| CustomObject | CustomField | Field Type | Lookup Object |
|--------------|-------------|------------|---------------|
| Account      | Name        | string     |               |
| Account      | Industry    | picklist   |               |
| Contact      | FirstName   | string     |               |
| Contact      | LastName    | string     |               |
| Contact      | AccountId   | reference  | Account       |
| Opportunity  | Name        | string     |               |
| Opportunity  | Amount      | currency   |               |
| Opportunity  | AccountId   | reference  | Account       |

The script will automatically:
1. Create JSON files for each object
2. Add standard fields like "Id" if not present
3. Create parent-child relationships based on reference fields
4. Handle special plural forms for relationship names

### Improving NLP Capabilities

The NLP model in `nlp_model.py` can be enhanced with more sophisticated techniques:
- Integration with libraries like spaCy or Hugging Face Transformers
- Training on a dataset of question-query pairs
- Adding support for more complex query patterns

### Adding New Specialized Models

To add a new specialized model for a specific query type:

1. Create a new file for your model (e.g., `custom_model.py`)
2. Inherit from `BaseSOQLModel` and implement the required methods:
   ```python
   from base_model import BaseSOQLModel

   class CustomModel(BaseSOQLModel):
       def can_handle(self, question: str) -> bool:
           # Determine if this model can handle the question
           return "custom pattern" in question.lower()

       def generate_query(self, question: str) -> str:
           # Generate a SOQL query for the question
           # ...
           return query
   ```
3. Add your model to the `ModelDispatcher` in `model_dispatcher.py`:
   ```python
   from custom_model import CustomModel

   # In the ModelDispatcher.__init__ method:
   self.models = [
       # Add your model at the appropriate position in the list
       CustomModel(metadata_path, soql_docs_path),
       # Other models...
   ]
   ```

## Limitations

- The current implementation uses a rule-based approach for NLP, which may not handle all natural language variations
- No integration with actual Salesforce API for validation or execution
- May require fine-tuning for specific use cases or organizations
- Performance may degrade with very complex queries or large metadata sets

## Future Enhancements

- Web interface for easier interaction
- Integration with Salesforce API to execute generated queries
- Machine learning-based NLP model for better question understanding
- Query validation and error handling
- Support for more SOQL features and query patterns
- Integration with external NLP services for improved accuracy

## License

This project is licensed under the MIT License - see the LICENSE file for details.
