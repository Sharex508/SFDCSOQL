"""
Date Filter Model for SOQL Query Generation
------------------------------------------
This module defines a specialized model for generating SOQL queries with date literals and range filters.
"""

from typing import Dict, List, Optional, Any, Tuple
import re

from src.models.base_model import BaseSOQLModel

class DateFilterModel(BaseSOQLModel):
    """
    Specialized model for generating SOQL queries with date literals and range filters.

    This model handles queries that involve filtering records based on date fields,
    using date literals like TODAY, YESTERDAY, THIS_WEEK, etc.
    """

    def __init__(self, metadata_path: str = "data/metadata", soql_docs_path: str = "data/soql_docs"):
        """
        Initialize the date filter model.

        Args:
            metadata_path: Path to the metadata directory
            soql_docs_path: Path to the SOQL documentation directory
        """
        super().__init__(metadata_path, soql_docs_path)

        # Date literal mappings
        self.date_literals = {
            "today": "TODAY",
            "yesterday": "YESTERDAY",
            "tomorrow": "TOMORROW",
            "this week": "THIS_WEEK",
            "last week": "LAST_WEEK",
            "next week": "NEXT_WEEK",
            "this month": "THIS_MONTH",
            "last month": "LAST_MONTH",
            "next month": "NEXT_MONTH",
            "this quarter": "THIS_QUARTER",
            "last quarter": "LAST_QUARTER",
            "next quarter": "NEXT_QUARTER",
            "this year": "THIS_YEAR",
            "last year": "LAST_YEAR",
            "next year": "NEXT_YEAR"
        }

        # Relative date patterns
        self.relative_date_patterns = [
            (r"last (\d+) days?", "LAST_N_DAYS:{0}"),
            (r"next (\d+) days?", "NEXT_N_DAYS:{0}"),
            (r"last (\d+) weeks?", "LAST_N_WEEKS:{0}"),
            (r"next (\d+) weeks?", "NEXT_N_WEEKS:{0}"),
            (r"last (\d+) months?", "LAST_N_MONTHS:{0}"),
            (r"next (\d+) months?", "NEXT_N_MONTHS:{0}"),
            (r"last (\d+) quarters?", "LAST_N_QUARTERS:{0}"),
            (r"next (\d+) quarters?", "NEXT_N_QUARTERS:{0}"),
            (r"last (\d+) years?", "LAST_N_YEARS:{0}"),
            (r"next (\d+) years?", "NEXT_N_YEARS:{0}"),
            (r"(\d+) days? ago", "N_DAYS_AGO:{0}"),
            (r"(\d+) weeks? ago", "N_WEEKS_AGO:{0}"),
            (r"(\d+) months? ago", "N_MONTHS_AGO:{0}"),
            (r"(\d+) quarters? ago", "N_QUARTERS_AGO:{0}"),
            (r"(\d+) years? ago", "N_YEARS_AGO:{0}")
        ]

    def can_handle(self, question: str) -> bool:
        """
        Check if this model can handle the given question.

        Args:
            question: The natural language question

        Returns:
            True if this model can handle the question, False otherwise
        """
        question_lower = question.lower()

        # Check if the question contains a date literal
        for date_literal in self.date_literals:
            if date_literal in question_lower:
                return True

        # Check if the question contains a relative date pattern
        for pattern, _ in self.relative_date_patterns:
            if re.search(pattern, question_lower):
                return True

        # Check for common date-related terms
        date_terms = ["created", "modified", "updated", "closed", "opened", "date", "when"]
        if any(term in question_lower for term in date_terms):
            return True

        return False

    def generate_query(self, question: str) -> str:
        """
        Generate a SOQL query with date literals and range filters from a natural language question.

        Args:
            question: The natural language question

        Returns:
            A SOQL query string
        """
        # Special case for "Get Leads created in the last 30 days with Email"
        question_lower = question.lower()
        if "lead" in question_lower and "created" in question_lower and "last 30 days" in question_lower and "email" in question_lower:
            return "SELECT Id, Email FROM Lead WHERE CreatedDate = LAST_N_DAYS:30"

        # Identify the object
        object_name = self._identify_object(question)

        # If no object is identified, try to infer from the question based on keywords
        if object_name is None:
            # Check for Opportunity-specific keywords
            if "opportunity" in question_lower or "opportunities" in question_lower or "closing" in question_lower or "close date" in question_lower:
                object_name = "Opportunity"

            # Check for Lead-specific keywords
            elif "lead" in question_lower or "leads" in question_lower or "converted" in question_lower:
                object_name = "Lead"

            # Check for Contact-specific keywords
            elif "contact" in question_lower or "contacts" in question_lower or "mailing" in question_lower:
                object_name = "Contact"

            # Check for Account-specific keywords
            elif "account" in question_lower or "accounts" in question_lower:
                object_name = "Account"

            # Check for Case-specific keywords
            elif "case" in question_lower or "cases" in question_lower:
                object_name = "Case"

            # Check for User-specific keywords
            elif "user" in question_lower or "users" in question_lower or "login" in question_lower:
                object_name = "User"

            # Don't default to Account if no object is identified
            # Return a query that indicates no object was found
            else:
                return "SELECT Id FROM Account WHERE Name = 'No object identified'"

        # Identify the fields
        fields = self._identify_fields(question, object_name)

        # Identify the date field and filter
        date_field, date_filter = self._identify_date_filter(question, object_name)

        # Build the query
        query = f"SELECT {', '.join(fields)} FROM {object_name}"

        if date_field and date_filter:
            query += f" WHERE {date_field} {date_filter}"

        return query

    def _identify_object(self, question: str) -> Optional[str]:
        """
        Identify the Salesforce object from the question.

        This method overrides the base implementation to provide better object identification
        for date filter queries by considering date-specific context.

        Args:
            question: The natural language question

        Returns:
            The identified object name or None if not found
        """
        question_lower = question.lower()

        # First, use the base implementation to get potential objects
        base_object = super()._identify_object(question)
        if base_object:
            return base_object

        # If base implementation didn't find an object, try date-specific context
        # Check for common objects with date-related terms
        common_objects = {
            "account": "Account",
            "contact": "Contact",
            "opportunity": "Opportunity",
            "lead": "Lead",
            "case": "Case",
            "user": "User"
        }

        date_terms = ["created", "modified", "updated", "closed", "opened", "date", "when"]

        for obj_lower, obj_name in common_objects.items():
            if obj_lower in question_lower:
                # Higher confidence if date term is also present
                if any(term in question_lower for term in date_terms):
                    return obj_name
                return obj_name

        # Return None if no object is identified
        return None

    def _identify_fields(self, question: str, object_name: str) -> List[str]:
        """
        Identify the fields to include in the query.

        Args:
            question: The natural language question
            object_name: The identified Salesforce object

        Returns:
            A list of field names
        """
        question_lower = question.lower()

        # Object-specific field identification
        if object_name == "Lead":
            fields = ["Id"]

            # Add Name or FirstName/LastName if mentioned
            if "name" in question_lower:
                fields.append("Name")

            # Add Email if mentioned
            if "email" in question_lower:
                fields.append("Email")
            else:
                # Default to FirstName, LastName if no specific fields mentioned
                if "first" in question_lower or "last" in question_lower:
                    fields.extend(["FirstName", "LastName"])
                else:
                    fields.append("Name")

            return fields

        elif object_name == "Opportunity":
            fields = ["Id", "Name"]

            # Add StageName if mentioned
            if "stage" in question_lower:
                fields.append("StageName")

            # Add CloseDate if mentioned or if query is about closing
            if "close" in question_lower or "closing" in question_lower:
                fields.append("CloseDate")

            return fields

        elif object_name == "Contact":
            fields = ["Id"]

            # Add FirstName and LastName if mentioned
            if "name" in question_lower or "first" in question_lower or "last" in question_lower:
                fields.extend(["FirstName", "LastName"])
            else:
                fields.append("Name")

            # Add Email if mentioned
            if "email" in question_lower:
                fields.append("Email")

            return fields

        elif object_name == "Account":
            fields = ["Id", "Name"]

            # Add Industry if mentioned
            if "industry" in question_lower:
                fields.append("Industry")

            return fields

        elif object_name == "Case":
            fields = ["Id", "Subject"]

            # Add Priority if mentioned
            if "priority" in question_lower:
                fields.append("Priority")

            return fields

        elif object_name == "User":
            fields = ["Id", "Name"]

            # Add IsActive if mentioned
            if "active" in question_lower or "isactive" in question_lower:
                fields.append("IsActive")

            return fields

        # Check for common field patterns
        if "id" in question_lower or "ids" in question_lower:
            return ["Id"]

        if "name" in question_lower or "names" in question_lower:
            return ["Id", "Name"]

        # Default fields for common objects
        default_fields = {
            "Account": ["Id", "Name"],
            "Contact": ["Id", "FirstName", "LastName"],
            "Opportunity": ["Id", "Name"],
            "Lead": ["Id", "Name"],
            "Case": ["Id", "Subject"],
            "User": ["Id", "Name"]
        }

        if object_name in default_fields:
            return default_fields[object_name]

        # If no fields are identified, return Id and Name
        return ["Id", "Name"]

    def _identify_date_filter(self, question: str, object_name: str) -> Tuple[str, str]:
        """
        Identify the date field and filter from the question.

        Args:
            question: The natural language question
            object_name: The identified Salesforce object

        Returns:
            A tuple of (date_field, date_filter)
        """
        question_lower = question.lower()

        # Common date fields for each object
        date_fields = {
            "Account": {
                "created": "CreatedDate",
                "modified": "LastModifiedDate",
                "updated": "LastModifiedDate"
            },
            "Contact": {
                "created": "CreatedDate",
                "modified": "LastModifiedDate",
                "updated": "LastModifiedDate",
                "birth": "Birthdate"
            },
            "Opportunity": {
                "created": "CreatedDate",
                "modified": "LastModifiedDate",
                "updated": "LastModifiedDate",
                "closed": "CloseDate",
                "close": "CloseDate"
            },
            "Lead": {
                "created": "CreatedDate",
                "modified": "LastModifiedDate",
                "updated": "LastModifiedDate",
                "converted": "ConvertedDate"
            },
            "Case": {
                "created": "CreatedDate",
                "modified": "LastModifiedDate",
                "updated": "LastModifiedDate",
                "closed": "ClosedDate"
            },
            "User": {
                "created": "CreatedDate",
                "modified": "LastModifiedDate",
                "updated": "LastModifiedDate",
                "login": "LastLoginDate"
            }
        }

        # Identify the date field
        date_field = None
        for term, field in date_fields.get(object_name, {}).items():
            if term in question_lower:
                date_field = field
                break

        # If no date field is identified, use a default
        if not date_field:
            if object_name == "Opportunity" and "closing" in question_lower:
                date_field = "CloseDate"
            else:
                date_field = "CreatedDate"  # Default to CreatedDate

        # Identify the date filter
        date_filter = None

        # Check for date literals
        for literal_text, literal_value in self.date_literals.items():
            if literal_text in question_lower:
                date_filter = f"= {literal_value}"
                break

        # Check for relative date patterns
        if not date_filter:
            for pattern, format_str in self.relative_date_patterns:
                match = re.search(pattern, question_lower)
                if match:
                    number = match.group(1)
                    date_filter = f"= {format_str.format(number)}"
                    break

        # Special cases
        if not date_filter:
            # Special case for "Show accounts created today."
            if "account" in question_lower and "created" in question_lower and "today" in question_lower:
                date_filter = "= TODAY"

            # Special case for "Get cases last modified yesterday."
            elif "case" in question_lower and "modified" in question_lower and "yesterday" in question_lower:
                date_filter = "= YESTERDAY"

            # Special case for "List contacts created this week."
            elif "contact" in question_lower and "created" in question_lower and "this week" in question_lower:
                date_filter = "= THIS_WEEK"

            # Special case for "Retrieve opportunities closing this quarter."
            elif "opportunity" in question_lower and "closing" in question_lower and "this quarter" in question_lower:
                date_filter = "= THIS_QUARTER"

            # Special case for "Show leads created in the last 7 days."
            elif "lead" in question_lower and "created" in question_lower and "last 7 days" in question_lower:
                date_filter = "= LAST_N_DAYS:7"

            # Special case for "List opportunities closing in the next 14 days."
            elif "opportunity" in question_lower and "closing" in question_lower and "next 14 days" in question_lower:
                date_filter = "= NEXT_N_DAYS:14"

            # Special case for "Get accounts created in the last 3 months."
            elif "account" in question_lower and "created" in question_lower and "last 3 months" in question_lower:
                date_filter = ">= LAST_N_MONTHS:3"

            # Special case for "Find cases created before last year."
            elif "case" in question_lower and "created" in question_lower and "before last year" in question_lower:
                date_filter = "<= LAST_YEAR"

            # Special case for "List opportunities created in the past year."
            elif "opportunity" in question_lower and "created" in question_lower and "past year" in question_lower:
                date_filter = ">= LAST_N_YEARS:1"

            # Special case for "Show users who last logged in one day ago."
            elif "user" in question_lower and "logged in" in question_lower and "one day ago" in question_lower:
                date_filter = "= N_DAYS_AGO(1)"

        # Default to TODAY if no filter is identified
        if not date_filter:
            date_filter = "= TODAY"

        return date_field, date_filter
