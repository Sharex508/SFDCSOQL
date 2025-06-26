# SOQL Query Generator - Model Explanation

## Overview

The SOQL Query Generator is a natural language processing (NLP) application that converts user questions in natural language into Salesforce Object Query Language (SOQL) queries. This document explains how the model works, its architecture, and the process it follows to generate SOQL queries.

## Architecture

The model is implemented in the `SOQLQueryGenerator` class in `nlp_model.py`. It uses a rule-based approach with pattern matching and keyword identification to convert natural language questions to SOQL queries. The model consists of several key components:

1. **Initialization and Configuration**
   - Loads Salesforce metadata (objects, fields, relationships)
   - Loads SOQL syntax documentation
   - Defines keywords for query operations (SELECT, WHERE, ORDER BY, LIMIT, etc.)

2. **Query Component Identification**
   - Identifies objects, fields, conditions, limits, and ordering from the question
   - Identifies relationships between objects (parent-to-child or child-to-parent)

3. **Query Generation**
   - Builds the SOQL query based on the identified components
   - Handles different types of queries (basic, relationship, etc.)

## How the Model Works

### 1. Processing a Question

When a user asks a question, the model follows these steps to generate a SOQL query:

1. **Identify Relationships**: The model first checks if the question involves a relationship between objects (e.g., "accounts with their contacts").
2. **Identify Object**: The model determines which Salesforce object to query (e.g., Account, Contact, Opportunity).
3. **Identify Fields**: The model determines which fields to include in the SELECT clause.
4. **Identify Conditions**: The model extracts conditions for the WHERE clause.
5. **Identify Limit and Order**: The model identifies any LIMIT or ORDER BY clauses.
6. **Generate Query**: The model builds the SOQL query based on the identified components.

### 2. Relationship Identification

The model can identify two types of relationships:

1. **Parent-to-Child Relationships**: These queries retrieve records from a parent object along with related records from a child object (e.g., "accounts with their contacts").
   - Example SOQL: `SELECT [Account fields], (SELECT [Contact fields] FROM Contacts) FROM Account`

2. **Child-to-Parent Relationships**: These queries retrieve records from a child object based on conditions on the parent object (e.g., "contacts of account name is 'acme'").
   - Example SOQL: `SELECT [Contact fields] FROM Contact WHERE Account.Name = 'acme'`

3. **Bidirectional Conversion**: The model can automatically convert between parent-to-child and child-to-parent queries when appropriate.

The relationship identification process uses regular expressions and pattern matching to identify common relationship patterns in the question. It then checks if the identified objects have a relationship in the metadata.

### 3. Object Identification

The model identifies the Salesforce object to query using these steps:

1. If the question involves a relationship, it returns the appropriate object based on the query direction.
2. Otherwise, it checks if any object name appears in the question (exact matches or plural forms).
3. If no object is identified, it defaults to "Account".

### 4. Field Identification

The model determines which fields to include in the SELECT clause:

1. It checks if the question is asking for all fields using patterns like "all fields", "all columns", etc.
2. It also checks if the question is a simple object request (e.g., "show me all accounts").
3. If either condition is true, it returns all fields for the object.
4. Otherwise, it returns default fields (Id and Name).

### 5. Condition Identification

The model extracts conditions for the WHERE clause:

1. For relationship queries, it looks for conditions on the parent object (e.g., "industry is technology").
2. It handles specific conditions like industry and name using pattern matching.
3. For child-to-parent queries, it uses dot notation for the relationship (e.g., "Account.Industry = 'technology'").
4. For non-relationship queries, it checks for "where" keywords and tries to extract conditions.

### 6. Query Generation

The model builds the SOQL query based on the identified components:

1. It starts with the SELECT clause, including the identified fields.
2. For parent-to-child relationships, it adds a subquery in the SELECT clause.
3. It adds the FROM clause with the object name.
4. It adds WHERE, ORDER BY, and LIMIT clauses if applicable.

## Example Queries

### Basic Query

**Question**: "Give me a list of all accounts"

**Process**:
1. No relationship identified
2. Object identified: Account
3. Fields identified: All fields of Account
4. No conditions, limit, or order identified
5. Generated SOQL: `SELECT [Account fields] FROM Account`

### Parent-to-Child Relationship Query

**Question**: "Show me accounts with their contacts"

**Process**:
1. Relationship identified: Parent-to-child (Account to Contact)
2. Object identified: Account
3. Fields identified: All fields of Account and Contact
4. No conditions, limit, or order identified
5. Generated SOQL: `SELECT [Account fields], (SELECT [Contact fields] FROM Contacts) FROM Account`

### Child-to-Parent Relationship Query

**Question**: "List opportunities from accounts in the technology industry"

**Process**:
1. Relationship identified: Child-to-parent (Opportunity to Account)
2. Object identified: Opportunity
3. Fields identified: All fields of Opportunity
4. Condition identified: Account.Industry = 'technology'
5. No limit or order identified
6. Generated SOQL: `SELECT [Opportunity fields] FROM Opportunity WHERE Account.Industry = 'technology'`

### Bidirectional Relationship Query

**Question**: "List opportunities from accounts in the technology industry"

**Process**:
1. Relationship identified: Child-to-parent (Opportunity to Account) with bidirectional flag
2. Converted to parent-to-child (Account to Opportunity)
3. Object identified: Account
4. Fields identified: All fields of Account and Opportunity
5. Condition identified: Industry = 'technology' (moved to subquery)
6. No limit or order identified
7. Generated SOQL: `SELECT [Account fields], (SELECT [Opportunity fields] FROM Opportunities WHERE Industry = 'technology') FROM Account`

## Conclusion

The SOQL Query Generator uses a rule-based approach with pattern matching and keyword identification to convert natural language questions to SOQL queries. It handles various types of queries, including basic queries and relationship queries (parent-to-child and child-to-parent). The model is designed to be flexible and can handle a wide range of natural language patterns.

While the current implementation is rule-based, it could be enhanced with more sophisticated NLP techniques such as named entity recognition, intent classification, and fine-tuned language models for better understanding of complex questions.