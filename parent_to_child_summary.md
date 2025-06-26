# Parent-to-Child Relationship Queries in SOQL Query Generator

## Overview

This document provides a summary of the implementation of parent-to-child relationship queries in the SOQL Query Generator application.

## What are Parent-to-Child Relationship Queries?

In Salesforce, a parent-to-child relationship query allows you to retrieve records from a parent object along with related records from a child object in a single query. For example, you can retrieve Account records along with their related Contact records.

## SOQL Syntax for Parent-to-Child Queries

The SOQL syntax for parent-to-child queries uses a subquery in the SELECT clause:

```sql
SELECT fields, (SELECT child_fields FROM ChildRelationship) FROM ParentObject
```

For example, to retrieve Account records along with their related Contact records:

```sql
SELECT Id, Name, (SELECT Id, FirstName, LastName FROM Contacts) FROM Account
```

## Implementation in SOQL Query Generator

The SOQL Query Generator now correctly identifies and generates parent-to-child relationship queries based on natural language questions. The implementation includes:

1. Enhanced relationship identification in the `_identify_relationship` method
2. Specific patterns for common parent-to-child relationships (Account-Contact, Account-Opportunity)
3. Proper construction of subqueries in the `generate_query` method

## Example Questions and Generated Queries

### Account-Contact Relationship

**Question**: "Show me accounts with their contacts"

**Generated SOQL Query**:
```sql
SELECT [Account fields], (SELECT [Contact fields] FROM Contacts) FROM Account
```

### Account-Opportunity Relationship

**Question**: "List accounts and their opportunities"

**Generated SOQL Query**:
```sql
SELECT [Account fields], (SELECT [Opportunity fields] FROM Opportunities) FROM Account
```

## How to Use Parent-to-Child Queries

To generate a parent-to-child relationship query, you can phrase your question in various ways:

1. "Show me [parent object] with their [child object]"
2. "List [parent object] and their [child object]"
3. "[parent object] with [child object]"
4. "[parent object] and their [child object]"

For example:
- "Show me accounts with their contacts"
- "List accounts and their opportunities"
- "Accounts with contacts"
- "Accounts and their opportunities"

## Notes

- The relationship name in the subquery (e.g., "Contacts", "Opportunities") is determined based on the child object name, typically using the plural form.
- For objects with special plural forms (e.g., "y" -> "ies"), the appropriate plural form is used.
- The application includes all fields from both the parent and child objects in the generated query.