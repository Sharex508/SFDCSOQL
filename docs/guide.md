# SOQL Query Generator - User Guide

## Prerequisites

Before running the SOQL Query Generator, make sure you have the following:

1. Python 3.6 or higher installed
2. Required packages installed:
   ```
   pip install -r requirements.txt
   ```
   This will install:
   - pandas>=1.3.0
   - openpyxl>=3.0.0

   Note: argparse is part of the Python standard library since Python 3.2,
   so it's not included as a separate dependency for Python 3.8+ environments.

3. Salesforce metadata file:
   - The application uses `Salesforce_Complete_Metadata.xlsx` for metadata information
   - This file should be in the root directory of the project
   - If the file is not available, the application will use sample metadata
   - You can generate metadata files from your own Salesforce metadata Excel file using the provided script:
     ```
     python generate_metadata.py --excel-file your_metadata.xlsx --output-dir data/metadata
     ```

## Running the Application

The SOQL Query Generator can be run in two modes:

### 1. Interactive Mode

In interactive mode, you can enter multiple questions one by one and get SOQL queries in response.

```bash
python main.py --interactive
# or
python main.py -i
```

You can also run the application without any arguments to enter interactive mode:

```bash
python main.py
```

In interactive mode:
- Type `help` to see example questions
- Type `exit` or `quit` to end the session

### 2. Single Question Mode

You can also provide a single question as a command-line argument:

```bash
python main.py --question "Show me all accounts"
# or
python main.py -q "Show me all accounts"
```

## Example Questions and Generated SOQL Queries

Here are some example questions you can ask and the SOQL queries they generate:

1. **Basic query for all fields of an object**:
   ```
   Question: Give me a list of all accounts
   Generated SOQL Query: SELECT Id, Name, Type, Industry, AnnualRevenue, Phone, Website FROM Account
   ```

2. **Query for a different object**:
   ```
   Question: Show me all contacts
   Generated SOQL Query: SELECT Id, FirstName, LastName, Email, Phone, Title, AccountId FROM Contact
   ```

3. **Query with a condition**:
   ```
   Question: Get accounts with industry = technology
   Generated SOQL Query: SELECT Id, Name, Type, Industry, AnnualRevenue, Phone, Website FROM Account WHERE Industry = 'Technology'
   ```

4. **Query with a limit and ordering**:
   ```
   Question: Find the top 5 opportunities by amount
   Generated SOQL Query: SELECT Id, Name, StageName, CloseDate, Amount, AccountId FROM Opportunity ORDER BY Amount DESC LIMIT 5
   ```

5. **Query for specific fields**:
   ```
   Question: Show me account names and phone numbers
   Generated SOQL Query: SELECT Name, Phone FROM Account
   ```

## Running the Example Script

The project includes an example script that demonstrates the functionality:

1. **Example script**:
   ```bash
   python example.py
   ```
   This script demonstrates how to use the SOQL Query Generator with various types of questions:
   - Basic queries for all fields of an object
   - Parent-to-child relationship queries (e.g., "accounts with their contacts")
   - Child-to-parent relationship queries (e.g., "contacts of an account")
   - Queries with conditions and limits

## Notes

- The application uses a rule-based approach to convert natural language questions to SOQL queries.
- It supports basic query operations like SELECT, WHERE, ORDER BY, and LIMIT.
- The application loads metadata from the Excel file or uses sample data if the Excel file is not available.
- For best results, make sure your questions are clear and include the object name (e.g., "accounts", "contacts", "opportunities").
