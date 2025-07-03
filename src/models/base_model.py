"""
Base Model for SOQL Query Generation
-----------------------------------
This module defines the base class for all specialized SOQL query generation models.
"""

from typing import Dict, List, Optional, Any, Tuple
import re
import os

class BaseSOQLModel:
    """
    Base class for all specialized SOQL query generation models.

    This class provides common functionality and defines the interface that all
    specialized models must implement. Specialized models should inherit from this
    class and override the can_handle and generate_query methods.
    """

    def __init__(self, metadata_path: str = "data/metadata", soql_docs_path: str = "data/soql_docs"):
        """
        Initialize the base SOQL model.

        Args:
            metadata_path: Path to the metadata directory
            soql_docs_path: Path to the SOQL documentation directory
        """
        self.metadata_path = metadata_path
        self.soql_docs_path = soql_docs_path
        self.objects = {}
        self.fields_by_object = {}
        self.relationships = {}
        self.soql_syntax = {}

        # Common keywords for query operations
        self.select_keywords = ["show", "get", "find", "display", "list", "retrieve", "give me"]
        self.where_keywords = ["where", "with", "that have", "that has", "whose", "which have", "which has", "having"]
        self.order_keywords = ["order by", "sort by", "sorted by", "arranged by", "in order of"]
        self.limit_keywords = ["limit", "only", "just", "top", "first", "last"]
        self.aggregate_keywords = {
            "count": ["count", "how many", "number of"],
            "sum": ["sum", "total", "add up"],
            "avg": ["average", "mean", "avg"],
            "min": ["minimum", "min", "smallest", "lowest"],
            "max": ["maximum", "max", "largest", "highest"]
        }

        # Advanced SOQL features
        self.all_rows_keywords = ["deleted", "including deleted", "all rows", "including all rows", "including removed", "removed", "recycled", "recycle bin", "trash", "including trash"]
        self.for_view_keywords = ["for view", "view"]
        self.for_reference_keywords = ["for reference", "reference", "refer to", "referring to"]
        self.for_update_keywords = ["for update", "update", "lock", "locking", "modify", "change", "edit"]

        # Load metadata and SOQL documentation
        self._load_metadata()
        self._load_soql_docs()

    def _load_metadata(self):
        """Load Salesforce metadata"""
        if not os.path.exists(self.metadata_path):
            os.makedirs(self.metadata_path, exist_ok=True)
            print(f"Created metadata directory at {self.metadata_path}")
            return

        # In a real implementation, this would load actual metadata files
        # For now, we'll just initialize with empty data
        self.objects = {}
        self.fields_by_object = {}
        self.relationships = {}

    def _load_soql_docs(self):
        """Load SOQL documentation"""
        if not os.path.exists(self.soql_docs_path):
            os.makedirs(self.soql_docs_path, exist_ok=True)
            print(f"Created SOQL docs directory at {self.soql_docs_path}")
            return

        # In a real implementation, this would load actual SOQL documentation
        # For now, we'll just initialize with basic SOQL syntax
        self.soql_syntax = {
            "select": "SELECT {fields} FROM {object}",
            "where": "WHERE {conditions}",
            "order_by": "ORDER BY {fields} {direction}",
            "limit": "LIMIT {limit}",
            "offset": "OFFSET {offset}",
            "group_by": "GROUP BY {fields}",
            "having": "HAVING {conditions}"
        }

    def can_handle(self, question: str) -> bool:
        """
        Determine if this model can handle the given question.

        This method should be overridden by specialized models to determine if they
        can handle the given question. The default implementation returns False.

        Args:
            question: The natural language question

        Returns:
            True if this model can handle the question, False otherwise
        """
        return False

    def generate_query(self, question: str) -> str:
        """
        Generate a SOQL query from a natural language question.

        This method should be overridden by specialized models to generate a SOQL query
        for the given question. The default implementation returns a simple query.

        Args:
            question: The natural language question

        Returns:
            A SOQL query string
        """
        return "SELECT Id FROM Account"

    def _identify_object(self, question: str) -> Optional[str]:
        """
        Identify the Salesforce object from the question.

        Args:
            question: The natural language question

        Returns:
            The identified object name or None if not found
        """
        # Convert question to lowercase for case-insensitive matching
        question_lower = question.lower()

        # Extract words from the question for more precise matching
        words = re.findall(r'\b\w+\b', question_lower)

        # Dictionary to store potential object matches and their confidence scores
        potential_objects = {}

        # First, try exact word matches (higher confidence)
        for obj_name in self.objects:
            obj_lower = obj_name.lower()
            # Check for exact word match
            if obj_lower in words:
                potential_objects[obj_name] = 0.9  # High confidence for exact word match
            # Check for exact match within the question
            elif obj_lower in question_lower:
                potential_objects[obj_name] = 0.7  # Medium-high confidence for substring match

        # Then try plural forms (medium confidence)
        for obj_name in self.objects:
            if obj_name in potential_objects:
                continue  # Skip if already found

            obj_lower = obj_name.lower()
            # Check for plural forms (simple 's' addition)
            plural_s = f"{obj_lower}s"
            if plural_s in words:
                potential_objects[obj_name] = 0.8  # Medium-high confidence for plural word match
            elif plural_s in question_lower:
                potential_objects[obj_name] = 0.6  # Medium confidence for plural substring match

            # Check for special plural forms (e.g., 'y' -> 'ies')
            if obj_lower.endswith('y'):
                plural_ies = f"{obj_lower[:-1]}ies"
                if plural_ies in words:
                    potential_objects[obj_name] = 0.8  # Medium-high confidence for plural word match
                elif plural_ies in question_lower:
                    potential_objects[obj_name] = 0.6  # Medium confidence for plural substring match

        # Check for common field names that might indicate the object
        for obj_name in self.fields_by_object:
            for field in self.fields_by_object[obj_name]:
                field_name = field["name"].lower()
                if field_name in question_lower:
                    # Increase confidence if field is mentioned
                    if obj_name in potential_objects:
                        potential_objects[obj_name] += 0.1
                    else:
                        potential_objects[obj_name] = 0.5  # Medium confidence for field match

        # If we have potential objects, determine the primary one
        if potential_objects:
            # If there's only one object, return it
            if len(potential_objects) == 1:
                return list(potential_objects.keys())[0]

            # If there are multiple objects, we need to determine which one is primary
            # First, check if any of the objects are in a parent-child relationship
            primary_object = self._determine_primary_object(potential_objects, question_lower)
            if primary_object:
                return primary_object

            # If we couldn't determine a primary object based on relationships,
            # return the one with highest confidence
            return max(potential_objects.items(), key=lambda x: x[1])[0]

        # Return None if no object is identified
        return None

    def _determine_primary_object(self, potential_objects: Dict[str, float], question_lower: str) -> Optional[str]:
        """
        Determine the primary object from a set of potential objects.

        This method uses relationship metadata to determine which object is primary
        when multiple objects are mentioned in a prompt.

        Args:
            potential_objects: Dictionary of potential objects and their confidence scores
            question_lower: The lowercase question

        Returns:
            The primary object name or None if it couldn't be determined
        """
        # If there are only two objects, check if they're in a parent-child relationship
        if len(potential_objects) == 2:
            objects = list(potential_objects.keys())
            obj1, obj2 = objects[0], objects[1]

            # Check if obj1 is a parent of obj2
            parent_child_relationship = self._check_parent_child_relationship(obj1, obj2)
            if parent_child_relationship:
                parent, child = parent_child_relationship

                # Check if the question is asking about the parent or the child
                # If the question contains phrases like "with their", "and their", etc.,
                # it's likely asking about the parent object
                parent_indicators = ["with their", "with its", "and their", "and its", "for each"]
                if any(indicator in question_lower for indicator in parent_indicators):
                    return parent

                # If the question contains phrases like "of", "for", "under", etc.,
                # it's likely asking about the child object
                child_indicators = [" of ", " for ", " under ", " belonging to ", " related to "]
                if any(indicator in question_lower for indicator in child_indicators):
                    return child

                # If we can't determine based on indicators, return the parent as default
                return parent

        # If there are more than two objects or we couldn't determine based on relationships,
        # check for specific patterns in the question

        # Pattern: "X with their Y" - X is primary
        for obj_name in potential_objects:
            obj_lower = obj_name.lower()
            pattern = rf"{obj_lower}s? with (?:their|its)"
            if re.search(pattern, question_lower):
                return obj_name

        # Pattern: "Y of X" - X is primary
        for obj_name in potential_objects:
            obj_lower = obj_name.lower()
            pattern = rf" of {obj_lower}s?"
            if re.search(pattern, question_lower):
                return obj_name

        # If we still can't determine, return None and let the caller decide
        return None

    def _check_parent_child_relationship(self, obj1: str, obj2: str) -> Optional[Tuple[str, str]]:
        """
        Check if two objects are in a parent-child relationship.

        Args:
            obj1: First object name
            obj2: Second object name

        Returns:
            A tuple (parent, child) if a relationship exists, None otherwise
        """
        # Check if obj1 is a parent of obj2
        if obj1 in self.relationships:
            for relationship in self.relationships[obj1]:
                if relationship.get('type') == 'child' and relationship.get('childObject') == obj2:
                    return (obj1, obj2)

        # Check if obj2 is a parent of obj1
        if obj2 in self.relationships:
            for relationship in self.relationships[obj2]:
                if relationship.get('type') == 'child' and relationship.get('childObject') == obj1:
                    return (obj2, obj1)

        # No parent-child relationship found
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
        # Default to Id and Name fields
        return ["Id", "Name"]

    def _identify_conditions(self, question: str, object_name: str) -> Optional[str]:
        """
        Identify the conditions for the WHERE clause.

        Args:
            question: The natural language question
            object_name: The identified Salesforce object

        Returns:
            A string with the WHERE clause conditions or None if no conditions
        """
        return None

    def _identify_limit(self, question: str) -> Optional[int]:
        """
        Identify the LIMIT clause from the question.

        Args:
            question: The natural language question

        Returns:
            The limit value or None if no limit
        """
        # Look for numbers in the question
        numbers = re.findall(r'\b\d+\b', question)
        question_lower = question.lower()

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

        return None

    def _identify_order(self, question: str, object_name: str) -> Optional[Tuple[List[str], str]]:
        """
        Identify the ORDER BY clause from the question.

        Args:
            question: The natural language question
            object_name: The identified Salesforce object

        Returns:
            A tuple of (fields, direction) or None if no ordering
        """
        # Check for order keywords
        for keyword in self.order_keywords:
            if keyword in question.lower():
                # Very simplistic approach
                if "asc" in question.lower() or "ascending" in question.lower():
                    return (["Name"], "ASC")
                elif "desc" in question.lower() or "descending" in question.lower():
                    return (["Name"], "DESC")
                else:
                    return (["Name"], "ASC")  # Default to ascending

        return None
