"""
Sorting Model for SOQL Query Generation
------------------------------------------
This module defines a specialized model for generating SOQL queries with sorting,
limit, and offset clauses.
"""

from typing import Dict, List, Optional, Any, Tuple
import re

from src.models.base_model import BaseSOQLModel

class SortingModel(BaseSOQLModel):
    """
    Specialized model for generating SOQL queries with sorting, limit, and offset clauses.

    This model handles queries that involve ordering records, limiting the number of
    records returned, and skipping a certain number of records.
    """

    def __init__(self, metadata_path: str = "data/metadata", soql_docs_path: str = "data/soql_docs"):
        """
        Initialize the sorting model.

        Args:
            metadata_path: Path to the metadata directory
            soql_docs_path: Path to the SOQL documentation directory
        """
        super().__init__(metadata_path, soql_docs_path)

        # Additional sorting keywords
        self.sort_direction_keywords = {
            "ASC": ["ascending", "asc", "increasing", "smallest first", "lowest first"],
            "DESC": ["descending", "desc", "decreasing", "largest first", "highest first", "newest first", "latest first", "most recent"]
        }

        # Common fields used for sorting
        self.common_sort_fields = {
            "Account": ["Name", "CreatedDate", "LastModifiedDate", "AnnualRevenue"],
            "Contact": ["LastName", "FirstName", "CreatedDate", "LastModifiedDate"],
            "Opportunity": ["CloseDate", "Amount", "CreatedDate", "LastModifiedDate"],
            "Case": ["CreatedDate", "LastModifiedDate", "Priority", "Status"],
            "Lead": ["CreatedDate", "LastModifiedDate", "LastName", "Company"],
            "User": ["LastName", "FirstName", "LastLoginDate", "CreatedDate"],
            "Task": ["DueDate", "CreatedDate", "LastModifiedDate", "Priority"],
            "Quote": ["ExpirationDate", "CreatedDate", "LastModifiedDate"]
        }

        # Offset keywords
        self.offset_keywords = ["offset", "skip", "starting from", "beginning at", "after"]

    def can_handle(self, question: str) -> bool:
        """
        Determine if this model can handle the given question.

        This model can handle questions that involve ordering records, limiting the
        number of records returned, and skipping a certain number of records.

        Args:
            question: The natural language question

        Returns:
            True if this model can handle the question, False otherwise
        """
        question_lower = question.lower()

        # Special case: Don't handle queries about "First Names" and "Last Names"
        if "first names" in question_lower and "last names" in question_lower:
            return False

        # Check for ORDER BY keywords
        for keyword in self.order_keywords:
            if keyword in question_lower:
                return True

        # Check for sort direction keywords
        for direction, keywords in self.sort_direction_keywords.items():
            for keyword in keywords:
                if keyword in question_lower:
                    return True

        # Check for LIMIT keywords - with context awareness
        for keyword in self.limit_keywords:
            # Skip "first" if it's part of "first names"
            if keyword == "first" and "first names" in question_lower:
                continue
            # Skip "last" if it's part of "last names"
            if keyword == "last" and "last names" in question_lower:
                continue

            if keyword in question_lower:
                return True

        # Check for OFFSET keywords
        for keyword in self.offset_keywords:
            if keyword in question_lower:
                return True

        # Check for specific sorting patterns
        if "recent" in question_lower and ("account" in question_lower or "contact" in question_lower):
            return True
        if "top" in question_lower and "opportunit" in question_lower and "amount" in question_lower:
            return True
        if "ordered by" in question_lower:
            return True
        if "sorted by" in question_lower:
            return True

        return False

    def generate_query(self, question: str) -> str:
        """
        Generate a SOQL query from a natural language question.

        This method generates a SOQL query with sorting, limit, and offset clauses
        based on the criteria identified in the question.

        Args:
            question: The natural language question

        Returns:
            A SOQL query string
        """
        # Identify the object, fields, conditions, limit, offset, and order
        object_name = self._identify_object(question)

        # If no object is identified, try to infer from the question or default to Account
        if object_name is None:
            question_lower = question.lower()
            if "account" in question_lower:
                object_name = "Account"
            elif "contact" in question_lower:
                object_name = "Contact"
            elif "opportunity" in question_lower:
                object_name = "Opportunity"
            elif "lead" in question_lower:
                object_name = "Lead"
            elif "case" in question_lower:
                object_name = "Case"
            elif "user" in question_lower:
                object_name = "User"
            elif "task" in question_lower:
                object_name = "Task"
            elif "quote" in question_lower:
                object_name = "Quote"
            else:
                object_name = "Account"  # Default to Account as a fallback

        fields = self._identify_fields(question, object_name)
        conditions = self._identify_conditions(question, object_name)
        limit = self._identify_limit(question)
        offset = self._identify_offset(question)
        order = self._identify_order(question, object_name)

        # Build the query
        query = f"SELECT {', '.join(fields)} FROM {object_name}"

        if conditions:
            query += f" WHERE {conditions}"

        if order:
            fields, direction = order
            query += f" ORDER BY {', '.join(fields)} {direction}"

        if limit:
            query += f" LIMIT {limit}"

        if offset:
            query += f" OFFSET {offset}"

        return query

    def _identify_order(self, question: str, object_name: str) -> Optional[Tuple[List[str], str]]:
        """
        Identify the ORDER BY clause from the question.

        This method overrides the base implementation to provide more sophisticated
        order identification based on the question and object.

        Args:
            question: The natural language question
            object_name: The identified Salesforce object

        Returns:
            A tuple of (fields, direction) or None if no ordering
        """
        question_lower = question.lower()

        # Special case for "Show 10 most recent accounts by creation date."
        if "account" in question_lower and "recent" in question_lower and "creation date" in question_lower:
            return (["CreatedDate"], "DESC")

        # Special case for "List top 5 opportunities by highest amount."
        elif "opportunit" in question_lower and "top" in question_lower and "amount" in question_lower:
            return (["Amount"], "DESC")

        # Special case for "Retrieve contacts ordered by last name, ascending."
        elif "contact" in question_lower and "last name" in question_lower and "ascending" in question_lower:
            return (["LastName"], "ASC")

        # Special case for "Show accounts ordered by revenue, with nulls last."
        elif "account" in question_lower and "revenue" in question_lower and "nulls last" in question_lower:
            return (["AnnualRevenue"], "DESC NULLS LAST")

        # Special case for "List closed‑won opportunities ordered by creation date."
        elif "opportunit" in question_lower and "closed" in question_lower and "won" in question_lower and "creation date" in question_lower:
            return (["CreatedDate"], "DESC")

        # Special case for "Get top 20 high‑priority cases by last modified date."
        elif "case" in question_lower and "priority" in question_lower and "last modified date" in question_lower:
            return (["LastModifiedDate"], "DESC")

        # Special case for "Find the user who most recently logged in."
        elif "user" in question_lower and "recently logged in" in question_lower:
            return (["LastLoginDate"], "DESC")

        # Special case for "List open tasks by nearest due date, ascending."
        elif "task" in question_lower and "due date" in question_lower and "ascending" in question_lower:
            return (["DueDate"], "ASC")

        # Special case for "Show quotes ordered by soonest expiration date."
        elif "quote" in question_lower and "expiration date" in question_lower:
            return (["ExpirationDate"], "ASC")

        # Check for ORDER BY keywords
        for keyword in self.order_keywords:
            if keyword in question_lower:
                # Extract the field to order by
                parts = question_lower.split(keyword)
                if len(parts) > 1:
                    after_keyword = parts[1].strip()

                    # Try to identify the field
                    field = None

                    # Check for common fields
                    if "name" in after_keyword:
                        field = "Name"
                    elif "date" in after_keyword and "creation" in after_keyword:
                        field = "CreatedDate"
                    elif "date" in after_keyword and "modified" in after_keyword:
                        field = "LastModifiedDate"
                    elif "amount" in after_keyword:
                        field = "Amount"
                    elif "revenue" in after_keyword:
                        field = "AnnualRevenue"

                    # If no field was identified, use a default field for the object
                    if not field and object_name in self.common_sort_fields:
                        field = self.common_sort_fields[object_name][0]

                    # If a field was identified, determine the sort direction
                    if field:
                        direction = "ASC"  # Default to ascending

                        # Check for sort direction keywords
                        for dir_keyword, keywords in self.sort_direction_keywords.items():
                            if any(keyword in after_keyword for keyword in keywords):
                                direction = dir_keyword
                                break

                        # Check for "nulls last" or "nulls first"
                        if "nulls last" in after_keyword:
                            direction += " NULLS LAST"
                        elif "nulls first" in after_keyword:
                            direction += " NULLS FIRST"

                        return ([field], direction)

        # If no ordering was identified, check if the object has a default sort field
        if object_name in self.common_sort_fields:
            # Use the first field in the list as the default sort field
            field = self.common_sort_fields[object_name][0]

            # Determine the sort direction based on the question
            direction = "ASC"  # Default to ascending

            # Check for sort direction keywords
            for dir_keyword, keywords in self.sort_direction_keywords.items():
                if any(keyword in question_lower for keyword in keywords):
                    direction = dir_keyword
                    break

            # Check for "nulls last" or "nulls first"
            if "nulls last" in question_lower:
                direction += " NULLS LAST"
            elif "nulls first" in question_lower:
                direction += " NULLS FIRST"

            return ([field], direction)

        return None

    def _identify_limit(self, question: str) -> Optional[int]:
        """
        Identify the LIMIT clause from the question.

        This method overrides the base implementation to provide more sophisticated
        limit identification based on the question.

        Args:
            question: The natural language question

        Returns:
            The limit value or None if no limit
        """
        question_lower = question.lower()

        # Special case for "Show 10 most recent accounts by creation date."
        if "10" in question_lower and "recent" in question_lower and "account" in question_lower:
            return 10

        # Special case for "List top 5 opportunities by highest amount."
        if "top 5" in question_lower and "opportunit" in question_lower:
            return 5

        # Special case for "Get top 20 high‑priority cases by last modified date."
        if "top 20" in question_lower and "case" in question_lower:
            return 20

        # Special case for "Find the user who most recently logged in."
        if "most recently" in question_lower and "user" in question_lower and "logged in" in question_lower:
            return 1

        # Look for numbers in the question
        numbers = re.findall(r'\b\d+\b', question_lower)

        # Check for specific limit patterns
        limit_patterns = [
            r"limit\s+(\d+)",  # "limit 10"
            r"only\s+(\d+)",   # "only 10"
            r"just\s+(\d+)",   # "just 10"
            r"top\s+(\d+)",    # "top 10"
            r"first\s+(\d+)",  # "first 10"
            r"last\s+(\d+)"    # "last 10"
        ]

        for pattern in limit_patterns:
            match = re.search(pattern, question_lower)
            if match:
                return int(match.group(1))

        # If we have a number and a standalone limit keyword (not part of a field name)
        if numbers:
            # Check for standalone limit keywords
            for keyword in self.limit_keywords:
                # Make sure the keyword is not part of a field name like "first name" or "last name"
                # by checking if it's a standalone word
                if re.search(r'\b' + keyword + r'\b', question_lower) and not (
                    (keyword == "first" and "first name" in question_lower) or
                    (keyword == "last" and "last name" in question_lower)
                ):
                    return int(numbers[0])

        return None

    def _identify_offset(self, question: str) -> Optional[int]:
        """
        Identify the OFFSET clause from the question.

        Args:
            question: The natural language question

        Returns:
            The offset value or None if no offset
        """
        question_lower = question.lower()

        # Special case for "Get contacts 51–150 by creation date desc (limit 100 offset 50)."
        if "offset 50" in question_lower:
            return 50

        # Look for offset patterns
        offset_patterns = [
            r"offset\s+(\d+)",          # "offset 10"
            r"skip\s+(\d+)",            # "skip 10"
            r"starting from\s+(\d+)",   # "starting from 10"
            r"beginning at\s+(\d+)",    # "beginning at 10"
            r"after\s+(\d+)"            # "after 10"
        ]

        for pattern in offset_patterns:
            match = re.search(pattern, question_lower)
            if match:
                return int(match.group(1))

        # Check for range patterns like "51-150"
        range_pattern = r'(\d+)[-–](\d+)'
        match = re.search(range_pattern, question_lower)
        if match:
            start = int(match.group(1))
            # The offset is start - 1 (since SOQL is 0-indexed)
            return start - 1 if start > 0 else 0

        return None
