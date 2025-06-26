# SOQL Query Generator - User Guide

## Prerequisites

Before running the SOQL Query Generator, make sure you have the following:

1. Python 3.6 or higher installed
2. Required packages installed:
   ```
   pip install -r requirements.txt
   ```
   This will install:
   - argparse>=1.4.0
   - pandas>=1.3.0
   - openpyxl>=3.0.0

3. Salesforce metadata file:
   - The application uses `Salesforce_Complete_Metadata.xlsx` for metadata information
   - This file should be in the root directory of the project
   - If the file is not available, the application will use sample metadata

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

## Running the Example and Test Scripts

The project includes example and test scripts that demonstrate the functionality:

1. **Example script**:
   ```bash
   python example.py
   ```
   This script demonstrates how to use the SOQL Query Generator with three different types of questions:
   - A basic query for all fields of an object
   - A query for a different object
   - A query with a limit

2. **General test script**:
   ```bash
   python test_soql_generator.py
   ```
   This script tests various questions and prints the generated SOQL queries.

3. **Account-specific test script**:
   ```bash
   python test_account_query.py
   ```
   This script specifically tests generating a SOQL query for accounts with all fields.

## Notes

- The application uses a rule-based approach to convert natural language questions to SOQL queries.
- It supports basic query operations like SELECT, WHERE, ORDER BY, and LIMIT.
- The application loads metadata from the Excel file or uses sample data if the Excel file is not available.
- For best results, make sure your questions are clear and include the object name (e.g., "accounts", "contacts", "opportunities").
