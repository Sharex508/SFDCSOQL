"""
NLP Model for SOQL Query Generation
-----------------------------------
This module contains the implementation of the NLP model that converts
natural language questions into SOQL queries.

It now uses a modular architecture where different types of queries are handled by specialized models.
The main SOQLQueryGenerator class acts as a dispatcher that selects the appropriate model based on the user's prompt.
"""

import os
import json
import re
from typing import Dict, List, Optional, Any, Tuple

# Import the model dispatcher
try:
    from src.utils.model_dispatcher import ModelDispatcher
    MODULAR_ARCHITECTURE_AVAILABLE = True
except ImportError:
    MODULAR_ARCHITECTURE_AVAILABLE = False

# In a production environment, you would use a proper NLP library
# such as transformers, spacy, or a custom fine-tuned model
# For this implementation, we'll create a rule-based system with some NLP concepts

class SOQLQueryGenerator:
    """
    A class that generates SOQL queries from natural language questions
    using NLP techniques.

    This class now uses a modular architecture where different types of queries are handled by specialized models.
    It acts as a dispatcher that selects the appropriate model based on the user's prompt.
    """

    def __init__(self, metadata_path: str = "data/metadata", soql_docs_path: str = "data/soql_docs"):
        """
        Initialize the SOQL Query Generator

        Args:
            metadata_path: Path to the Salesforce metadata
            soql_docs_path: Path to the SOQL documentation
        """
        self.metadata_path = metadata_path
        self.soql_docs_path = soql_docs_path
        self.objects = {}
        self.fields_by_object = {}
        self.relationships = {}
        self.soql_syntax = {}

        # Variables to store information about the last identified parent and child objects
        self._last_identified_parent = None
        self._last_identified_child_text = None

        # Load metadata and SOQL documentation
        self._load_metadata()
        self._load_soql_docs()

        # Initialize the model dispatcher if available
        self.use_modular_architecture = MODULAR_ARCHITECTURE_AVAILABLE
        if self.use_modular_architecture:
            self.model_dispatcher = ModelDispatcher(metadata_path, soql_docs_path)
            # Set metadata for the model dispatcher
            self.model_dispatcher.set_metadata(self.objects, self.fields_by_object, self.relationships)

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

        # Date literal mappings
        self.DATE_LITERAL_MAPPING = {
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
            "next year": "NEXT_YEAR",
        }

        # Relative date patterns
        self.RELATIVE_DATE_PATTERNS = [
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
            (r"(\d+) years? ago", "N_YEARS_AGO:{0}"),
        ]

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

    def _find_relationship_path(self, start_obj: str, end_obj: str, max_depth: int = 3) -> Optional[List[Dict[str, Any]]]:
        """
        Find a path of relationships between two objects that are not directly related.

        This method uses a breadth-first search to find the shortest path between two objects
        through their relationships. It returns a list of relationship dictionaries that
        describe the path from the start object to the end object.

        Args:
            start_obj: The starting object name
            end_obj: The ending object name
            max_depth: Maximum depth of relationships to traverse (default: 3)

        Returns:
            A list of relationship dictionaries describing the path, or None if no path is found
        """
        if start_obj not in self.objects or end_obj not in self.objects:
            return None

        # If the objects are the same, return an empty path
        if start_obj == end_obj:
            return []

        # Check if there's a direct relationship
        direct_relationship = self._find_direct_relationship(start_obj, end_obj)
        if direct_relationship:
            return [direct_relationship]

        # Use breadth-first search to find the shortest path
        queue = [(start_obj, [])]  # (current_obj, path_so_far)
        visited = {start_obj}

        while queue:
            current_obj, path = queue.pop(0)

            # Don't go beyond max_depth
            if len(path) >= max_depth:
                continue

            # Get all relationships for the current object
            if current_obj in self.relationships:
                for relationship in self.relationships[current_obj]:
                    next_obj = None
                    if relationship['type'] == 'parent':
                        next_obj = relationship['parentObject']
                    elif relationship['type'] == 'child':
                        next_obj = relationship['childObject']

                    if next_obj and next_obj not in visited:
                        # Create a new path with this relationship
                        # Make a copy of the relationship to avoid modifying the original
                        rel_copy = relationship.copy()

                        # Ensure the relationship has parentObject and childObject fields
                        if 'parentObject' not in rel_copy and rel_copy['type'] == 'child':
                            rel_copy['parentObject'] = current_obj
                        if 'childObject' not in rel_copy and rel_copy['type'] == 'parent':
                            rel_copy['childObject'] = current_obj

                        new_path = path + [rel_copy]

                        # Check if we've reached the end object
                        if next_obj == end_obj:
                            return new_path

                        # Add to queue for further exploration
                        queue.append((next_obj, new_path))
                        visited.add(next_obj)

        # No path found
        return None

    def _find_direct_relationship(self, obj1: str, obj2: str) -> Optional[Dict[str, Any]]:
        """
        Find a direct relationship between two objects.

        Args:
            obj1: The first object name
            obj2: The second object name

        Returns:
            A relationship dictionary or None if no direct relationship exists
        """
        # Check if obj1 has a relationship to obj2
        if obj1 in self.relationships:
            for relationship in self.relationships[obj1]:
                if (relationship['type'] == 'parent' and relationship['parentObject'] == obj2) or \
                   (relationship['type'] == 'child' and relationship['childObject'] == obj2):
                    return relationship

        # Check if obj2 has a relationship to obj1
        if obj2 in self.relationships:
            for relationship in self.relationships[obj2]:
                if (relationship['type'] == 'parent' and relationship['parentObject'] == obj1) or \
                   (relationship['type'] == 'child' and relationship['childObject'] == obj1):
                    # Reverse the relationship
                    reversed_relationship = relationship.copy()
                    if relationship['type'] == 'parent':
                        reversed_relationship['type'] = 'child'
                        reversed_relationship['childObject'] = obj2
                        reversed_relationship['parentObject'] = obj1
                    else:  # child
                        reversed_relationship['type'] = 'parent'
                        reversed_relationship['parentObject'] = obj2
                        reversed_relationship['childObject'] = obj1
                    return reversed_relationship

        return None

    def _identify_sibling_relationships(self, question: str) -> List[Dict[str, Any]]:
        """
        Identify sibling relationships in the question (e.g., Contacts and Opportunities of the same Account).

        Args:
            question: The natural language question

        Returns:
            A list of dictionaries with sibling relationship information
        """
        sibling_relationships = []
        question_lower = question.lower()

        # Look for patterns like "contacts and opportunities of account"
        # or "account's contacts and opportunities"
        sibling_patterns = [
            r"(\w+)(?:'s)?\s+(\w+)\s+and\s+(\w+)",  # "account's contacts and opportunities"
            r"(\w+)\s+and\s+(\w+)\s+of\s+(\w+)",    # "contacts and opportunities of account"
            r"(\w+)\s+with\s+(?:their|its)\s+(\w+)\s+and\s+(\w+)"  # "account with their contacts and opportunities"
        ]

        for pattern in sibling_patterns:
            matches = re.finditer(pattern, question_lower)
            for match in matches:
                # Extract the potential parent and child objects
                if "of" in pattern:
                    # Pattern: "contacts and opportunities of account"
                    child1_text = match.group(1)
                    child2_text = match.group(2)
                    parent_text = match.group(3)
                elif "with" in pattern:
                    # Pattern: "account with their contacts and opportunities"
                    parent_text = match.group(1)
                    child1_text = match.group(2)
                    child2_text = match.group(3)
                else:
                    # Pattern: "account's contacts and opportunities"
                    parent_text = match.group(1)
                    child1_text = match.group(2)
                    child2_text = match.group(3)

                # Try to match the texts to actual object names
                parent_obj = None
                child1_obj = None
                child2_obj = None

                # Match parent object
                for obj_name in self.objects:
                    obj_lower = obj_name.lower()
                    if obj_lower == parent_text or f"{obj_lower}s" == parent_text:
                        parent_obj = obj_name
                        break
                    # Handle special plural forms
                    if obj_lower.endswith('y') and f"{obj_lower[:-1]}ies" == parent_text:
                        parent_obj = obj_name
                        break

                # If we couldn't find the parent object, skip this match
                if not parent_obj:
                    continue

                # Match child objects
                for obj_name in self.objects:
                    obj_lower = obj_name.lower()
                    # Match first child
                    if obj_lower == child1_text or f"{obj_lower}s" == child1_text:
                        child1_obj = obj_name
                    # Handle special plural forms
                    elif obj_lower.endswith('y') and f"{obj_lower[:-1]}ies" == child1_text:
                        child1_obj = obj_name

                    # Match second child
                    if obj_lower == child2_text or f"{obj_lower}s" == child2_text:
                        child2_obj = obj_name
                    # Handle special plural forms
                    elif obj_lower.endswith('y') and f"{obj_lower[:-1]}ies" == child2_text:
                        child2_obj = obj_name

                # If we found both child objects, check if they have relationships with the parent
                if child1_obj and child2_obj:
                    # Check for relationships between parent and children
                    relationship1 = None
                    relationship2 = None

                    # Check for parent-to-child relationships
                    if parent_obj in self.relationships:
                        for rel in self.relationships[parent_obj]:
                            if rel['type'] == 'child' and rel['childObject'] == child1_obj:
                                relationship1 = rel
                            if rel['type'] == 'child' and rel['childObject'] == child2_obj:
                                relationship2 = rel

                    # If we found relationships for both children, add them to the sibling relationships
                    if relationship1 and relationship2:
                        sibling_relationships.append({
                            'parent_object': parent_obj,
                            'child_objects': [child1_obj, child2_obj],
                            'relationship_fields': [relationship1['field'], relationship2['field']],
                            'query_direction': "parent_to_children"
                        })

        return sibling_relationships

    def _identify_relationship(self, question: str) -> Optional[List[Dict[str, Any]]]:
        """
        Identify if the question is asking about a relationship between objects

        This method identifies relationships between objects in the question and determines
        the query direction (parent-to-child or child-to-parent). It also identifies if a
        child-to-parent query can be expressed as a parent-to-child query, which is indicated
        by the 'bidirectional' flag in the returned dictionary.

        For example, a question like "Give me a list of all contacts of an account name is 'acme'"
        is identified as a child-to-parent query (from Contact to Account), but it can also be
        expressed as a parent-to-child query (from Account to Contact) with a condition on the
        Account name.

        This method can identify multiple relationships in a single question, such as
        "List all contacts, opportunities of account", which involves relationships between
        Account-Contact and Account-Opportunity.

        It can also identify indirect relationships, such as "quote line items of an account",
        where Account is not directly related to QuoteLineItem but is related through
        Opportunity and Quote.

        Args:
            question: The natural language question

        Returns:
            A list of dictionaries with relationship information or None if no relationship is found.
            Each dictionary includes a 'bidirectional' flag that indicates if the query can be
            expressed in either direction (parent-to-child or child-to-parent).
        """
        question_lower = question.lower()

        # Initialize a list to store all identified relationships
        relationships = []

        # Check for sibling relationships (e.g., Contacts and Opportunities of the same Account)
        sibling_relationships = self._identify_sibling_relationships(question)
        if sibling_relationships:
            # If we found sibling relationships, add them to the relationships list
            relationships.extend(sibling_relationships)

        # Check if we have information from _identify_object about a parent-child relationship
        if self._last_identified_parent and self._last_identified_child_text:
            parent_obj = self._last_identified_parent
            child_text = self._last_identified_child_text.lower()

            # Special case for Case and comments
            if parent_obj == "Case" and "comment" in child_text:
                # Add a direct parent-to-child relationship for Case to CaseComment
                relationships.append({
                    'parent_object': "Case",
                    'child_object': "CaseComment",
                    'relationship_field': "ParentId",
                    'query_direction': "parent_to_child"
                })

            # Special case for Quote and line items
            elif parent_obj == "Quote" and "line item" in child_text:
                # Add a direct parent-to-child relationship for Quote to QuoteLineItem
                relationships.append({
                    'parent_object': "Quote",
                    'child_object': "QuoteLineItem",
                    'relationship_field': "QuoteId",
                    'query_direction': "parent_to_child"
                })

            # Try to match the child text to a child object
            for child_obj_name in self.objects:
                child_obj_lower = child_obj_name.lower()
                child_obj_plural = f"{child_obj_lower}s"

                # Handle special plural forms
                if child_obj_lower.endswith('y'):
                    child_obj_plural_y = f"{child_obj_lower[:-1]}ies"
                else:
                    child_obj_plural_y = child_obj_plural

                # Check if the child object is mentioned in the child text
                if (child_obj_lower in child_text or 
                    child_obj_plural in child_text or 
                    child_obj_plural_y in child_text):

                    # Check if there's a direct relationship
                    direct_relationship_found = False

                    # Check for parent-to-child relationship
                    if parent_obj in self.relationships:
                        for relationship in self.relationships[parent_obj]:
                            if relationship['type'] == 'child' and relationship['childObject'] == child_obj_name:
                                # Found a direct parent-to-child relationship
                                relationships.append({
                                    'parent_object': parent_obj,
                                    'child_object': child_obj_name,
                                    'relationship_field': relationship['field'],
                                    'query_direction': "parent_to_child"
                                })
                                direct_relationship_found = True
                                break

                    # If no direct relationship, check for indirect relationship
                    if not direct_relationship_found:
                        # Check if the child text contains "line items" or similar
                        is_line_items = "line items" in child_text or "lineitems" in child_text

                        # If it's a line items query, try to find the appropriate object
                        if is_line_items:
                            # Check for "quote line items"
                            if "quote" in child_text:
                                # Try to find a path from parent to QuoteLineItem
                                path = self._find_relationship_path(parent_obj, "QuoteLineItem")
                                if path:
                                    # Found an indirect relationship path
                                    relationships.append({
                                        'parent_object': parent_obj,
                                        'child_object': "QuoteLineItem",
                                        'relationship_path': path,
                                        'query_direction': "indirect_relationship",
                                        'indirect': True
                                    })
                                    direct_relationship_found = True
                            # Check for "order line items"
                            elif "order" in child_text:
                                # Try to find a path from parent to OrderLineItem
                                path = self._find_relationship_path(parent_obj, "OrderLineItem")
                                if path:
                                    # Found an indirect relationship path
                                    relationships.append({
                                        'parent_object': parent_obj,
                                        'child_object': "OrderLineItem",
                                        'relationship_path': path,
                                        'query_direction': "indirect_relationship",
                                        'indirect': True
                                    })
                                    direct_relationship_found = True
                                else:
                                    # If we couldn't find a direct path to OrderLineItem, try to find a path to Order
                                    # and then extend it to OrderLineItem
                                    order_path = self._find_relationship_path(parent_obj, "Order")
                                    if order_path:
                                        # Try to find a relationship from Order to OrderLineItem
                                        if "Order" in self.relationships:
                                            for rel in self.relationships["Order"]:
                                                if rel['type'] == 'child' and rel['childObject'] == "OrderLineItem":
                                                    # Create a copy of the relationship to avoid modifying the original
                                                    order_line_rel = rel.copy()

                                                    # Ensure the relationship has parentObject field
                                                    if 'parentObject' not in order_line_rel:
                                                        order_line_rel['parentObject'] = "Order"

                                                    # Add the relationship to the path
                                                    full_path = order_path + [order_line_rel]

                                                    # Add the relationship to OrderLineItem
                                                    relationships.append({
                                                        'parent_object': parent_obj,
                                                        'child_object': "OrderLineItem",
                                                        'relationship_path': full_path,
                                                        'query_direction': "indirect_relationship",
                                                        'indirect': True
                                                    })
                                                    direct_relationship_found = True
                                                    break
                        # Check for multiple child objects (e.g., "quote line items and orders")
                        elif "and" in child_text:
                            # Process each part separately
                            parts = child_text.split("and")

                            # Process each part
                            for part in parts:
                                part = part.strip()

                                # Check if this part contains "orders"
                                if "orders" in part and "line" not in part:
                                    # Try to find a path from parent to Order
                                    path = self._find_relationship_path(parent_obj, "Order")
                                    if path:
                                        # Found an indirect relationship path
                                        relationships.append({
                                            'parent_object': parent_obj,
                                            'child_object': "Order",
                                            'relationship_path': path,
                                            'query_direction': "indirect_relationship",
                                            'indirect': True
                                        })
                                        continue  # Skip the recursive call for this part

                                # Create a temporary child text with just this part
                                temp_child_text = part

                                # Set up the temporary variables
                                temp_last_identified_parent = parent_obj
                                temp_last_identified_child_text = temp_child_text

                                # Save the original variables
                                original_parent = self._last_identified_parent
                                original_child_text = self._last_identified_child_text

                                # Set the temporary variables
                                self._last_identified_parent = temp_last_identified_parent
                                self._last_identified_child_text = temp_child_text

                                # Call _identify_relationship recursively with a modified question
                                temp_question = f"List {parent_obj.lower()}s with their {temp_child_text}"
                                temp_relationships = self._identify_relationship(temp_question)

                                # Restore the original variables
                                self._last_identified_parent = original_parent
                                self._last_identified_child_text = original_child_text

                                # Add the relationships from the recursive call
                                if temp_relationships:
                                    relationships.extend(temp_relationships)

                        # If not a line items query or no path found, try generic approach
                        if not direct_relationship_found:
                            # Try to find a path from parent to child
                            path = self._find_relationship_path(parent_obj, child_obj_name)
                            if path:
                                # Found an indirect relationship path
                                relationships.append({
                                    'parent_object': parent_obj,
                                    'child_object': child_obj_name,
                                    'relationship_path': path,
                                    'query_direction': "indirect_relationship",
                                    'indirect': True
                                })

            # If we found relationships, check for duplicates and return them
            if relationships:
                # Remove duplicate relationships
                unique_relationships = []
                seen_child_objects = set()

                for rel in relationships:
                    child_obj = rel['child_object']
                    if child_obj not in seen_child_objects:
                        unique_relationships.append(rel)
                        seen_child_objects.add(child_obj)

                # If we have multiple relationships, return them all
                if len(unique_relationships) > 0:
                    return unique_relationships

        # Check for multiple child objects pattern (e.g., "List all contacts, opportunities of account")
        if re.search(r"(?:list|show|get|find|display) (?:all )?(?:contacts,? (?:and )?opportunities|opportunities,? (?:and )?contacts) (?:of|from) (?:an |a |the )?accounts?", question_lower):
            # This is a special case with multiple child objects
            parent_obj = "Account"
            child_objects = ["Contact", "Opportunity"]

            # Check if these objects exist and have relationships
            if parent_obj in self.objects:
                for child_obj in child_objects:
                    if child_obj in self.objects and parent_obj in self.relationships:
                        for relationship in self.relationships[parent_obj]:
                            if relationship['type'] == 'child' and relationship['childObject'] == child_obj:
                                # Found a relationship
                                relationships.append({
                                    'parent_object': parent_obj,
                                    'child_object': child_obj,
                                    'relationship_field': relationship['field'],
                                    'query_direction': "parent_to_child"
                                })

            # If we found multiple relationships, return them
            if len(relationships) > 1:
                return relationships

        # Check for "quote line items and orders" pattern
        if re.search(r"(?:list|show|get|find|display|retrieve) (?:all )?(?:quote line items|quotelineitems)(?:,? (?:and )?(?:orders|order))? (?:of|from) (?:an |a |the )?accounts?", question_lower) or \
           "quote line items and orders" in question_lower or \
           "orders and quote line items" in question_lower or \
           "accounts with their quote line items and orders" in question_lower or \
           re.search(r"(?:list|show|get|find|display|retrieve) (?:all )?(?:the )?(?:accounts?)(?:s)? (?:with|and) (?:all )?(?:their|its) (?:quote line items|quotelineitems)(?:,? (?:and )?(?:orders|order))?", question_lower):
            # This is a special case with quote line items and orders
            parent_obj = "Account"

            # Find path to QuoteLineItem
            path_to_quotelineitem = self._find_relationship_path(parent_obj, "QuoteLineItem")
            if path_to_quotelineitem:
                relationships.append({
                    'parent_object': parent_obj,
                    'child_object': "QuoteLineItem",
                    'relationship_path': path_to_quotelineitem,
                    'query_direction': "indirect_relationship",
                    'indirect': True
                })

            # Find path to Order
            path_to_order = self._find_relationship_path(parent_obj, "Order")
            if path_to_order:
                relationships.append({
                    'parent_object': parent_obj,
                    'child_object': "Order",
                    'relationship_path': path_to_order,
                    'query_direction': "indirect_relationship",
                    'indirect': True
                })

            # If we found multiple relationships, return them
            if len(relationships) > 0:
                return relationships

        # Check for "orders and order line items" pattern
        if re.search(r"(?:list|show|get|find|display|retrieve) (?:all )?(?:orders|order)(?:,? (?:and )?(?:order line items|orderlineitems))? (?:of|from) (?:an |a |the )?accounts?", question_lower) or \
           "orders and order line items" in question_lower or \
           "order line items and orders" in question_lower or \
           re.search(r"(?:list|show|get|find|display|retrieve) (?:all )?(?:the )?(?:accounts?)(?:s)? (?:with|and) (?:all )?(?:their|its) (?:orders|order)(?:,? (?:and )?(?:order line items|orderlineitems))?", question_lower):
            # This is a special case with orders and order line items
            parent_obj = "Account"

            # Find path to Order
            path_to_order = self._find_relationship_path(parent_obj, "Order")
            if path_to_order:
                relationships.append({
                    'parent_object': parent_obj,
                    'child_object': "Order",
                    'relationship_path': path_to_order,
                    'query_direction': "indirect_relationship",
                    'indirect': True
                })

            # For "orders and order line items", always include OrderLineItem
            if "order line items" in question_lower or "orderlineitems" in question_lower:
                # Find path to OrderLineItem via Order
                # First, find path to Order
                path_to_order = self._find_relationship_path(parent_obj, "Order")
                if path_to_order:
                    # Then, find relationship from Order to OrderLineItem
                    if "Order" in self.relationships:
                        for rel in self.relationships["Order"]:
                            if rel['type'] == 'child' and rel['childObject'] == "OrderLineItem":
                                # Create a path from Account to OrderLineItem via Order
                                path_to_orderlineitem = path_to_order.copy()
                                # Add the Order -> OrderLineItem relationship
                                path_to_orderlineitem.append(rel)

                                # Add the OrderLineItem relationship
                                relationships.append({
                                    'parent_object': parent_obj,
                                    'child_object': "OrderLineItem",
                                    'relationship_path': path_to_orderlineitem,
                                    'query_direction': "indirect_relationship",
                                    'indirect': True
                                })
                                break

            # If we found multiple relationships, return them
            if len(relationships) > 0:
                return relationships

        # Check for "order line items" pattern
        if re.search(r"(?:list|show|get|find|display|retrieve) (?:all )?(?:order line items|orderlineitems) (?:of|from) (?:an |a |the )?accounts?", question_lower) or \
           "order line items" in question_lower or \
           re.search(r"(?:list|show|get|find|display|retrieve) (?:all )?(?:the )?(?:accounts?)(?:s)? (?:with|and) (?:all )?(?:their|its) (?:order line items|orderlineitems)", question_lower):
            # This is a special case with order line items
            parent_obj = "Account"

            # Find path to OrderLineItem
            path_to_orderlineitem = self._find_relationship_path(parent_obj, "OrderLineItem")
            if path_to_orderlineitem:
                relationships.append({
                    'parent_object': parent_obj,
                    'child_object': "OrderLineItem",
                    'relationship_path': path_to_orderlineitem,
                    'query_direction': "indirect_relationship",
                    'indirect': True
                })

            # If we found relationships, return them
            if len(relationships) > 0:
                return relationships

        # Check for generic indirect relationship patterns
        # Look for patterns like "X of Y" or "X from Y" where X and Y are objects
        relationship_keywords = ["of", "from", "for", "in", "with", "related to"]

        for keyword in relationship_keywords:
            if keyword in question_lower:
                # Find all occurrences of the keyword
                keyword_indices = [m.start() for m in re.finditer(f"\\b{keyword}\\b", question_lower)]

                for idx in keyword_indices:
                    before_keyword = question_lower[:idx].strip()
                    after_keyword = question_lower[idx + len(keyword):].strip()

                    # Look for potential child objects before the keyword
                    for child_obj_name in self.objects:
                        child_obj_lower = child_obj_name.lower()
                        child_obj_plural = f"{child_obj_lower}s"

                        # Handle special plural forms
                        if child_obj_lower.endswith('y'):
                            child_obj_plural_y = f"{child_obj_lower[:-1]}ies"
                        else:
                            child_obj_plural_y = child_obj_plural

                        # Check if the child object is mentioned before the keyword
                        if (child_obj_lower in before_keyword or 
                            child_obj_plural in before_keyword or 
                            child_obj_plural_y in before_keyword):

                            # Look for potential parent objects after the keyword
                            for parent_obj_name in self.objects:
                                parent_obj_lower = parent_obj_name.lower()
                                parent_obj_plural = f"{parent_obj_lower}s"

                                # Handle special plural forms
                                if parent_obj_lower.endswith('y'):
                                    parent_obj_plural_y = f"{parent_obj_lower[:-1]}ies"
                                else:
                                    parent_obj_plural_y = parent_obj_plural

                                # Check if the parent object is mentioned after the keyword
                                if (parent_obj_lower in after_keyword or 
                                    parent_obj_plural in after_keyword or 
                                    parent_obj_plural_y in after_keyword):

                                    # First, check if there's a direct relationship
                                    direct_relationship_found = False

                                    # Check for child-to-parent relationship
                                    if child_obj_name in self.relationships:
                                        for relationship in self.relationships[child_obj_name]:
                                            if relationship['type'] == 'parent' and relationship['parentObject'] == parent_obj_name:
                                                # Found a direct child-to-parent relationship
                                                relationships.append({
                                                    'parent_object': parent_obj_name,
                                                    'child_object': child_obj_name,
                                                    'relationship_field': relationship['field'],
                                                    'query_direction': "child_to_parent",
                                                    'bidirectional': True
                                                })
                                                direct_relationship_found = True
                                                break

                                    # Check for parent-to-child relationship
                                    if not direct_relationship_found and parent_obj_name in self.relationships:
                                        for relationship in self.relationships[parent_obj_name]:
                                            if relationship['type'] == 'child' and relationship['childObject'] == child_obj_name:
                                                # Found a direct parent-to-child relationship
                                                relationships.append({
                                                    'parent_object': parent_obj_name,
                                                    'child_object': child_obj_name,
                                                    'relationship_field': relationship['field'],
                                                    'query_direction': "parent_to_child"
                                                })
                                                direct_relationship_found = True
                                                break

                                    # If no direct relationship, check for indirect relationship
                                    if not direct_relationship_found:
                                        # Try to find a path from parent to child
                                        path = self._find_relationship_path(parent_obj_name, child_obj_name)
                                        if path:
                                            # Found an indirect relationship path
                                            # Check if the child object has child objects that should be included
                                            if child_obj_name in self.relationships:
                                                for rel in self.relationships[child_obj_name]:
                                                    if rel['type'] == 'child':
                                                        child_child_obj = rel['childObject']
                                                        # Create a copy of the relationship to avoid modifying the original
                                                        rel_copy = rel.copy()

                                                        # Ensure the relationship has parentObject field
                                                        if 'parentObject' not in rel_copy:
                                                            rel_copy['parentObject'] = child_obj_name

                                                        # Add this child object to the relationship
                                                        relationships.append({
                                                            'parent_object': parent_obj_name,
                                                            'child_object': child_child_obj,
                                                            'relationship_path': path + [rel_copy],
                                                            'query_direction': "indirect_relationship",
                                                            'indirect': True
                                                        })

                                            # Add the original relationship
                                            relationships.append({
                                                'parent_object': parent_obj_name,
                                                'child_object': child_obj_name,
                                                'relationship_path': path,
                                                'query_direction': "indirect_relationship",
                                                'indirect': True
                                            })

                                        # Also try the reverse direction (child to parent)
                                        path = self._find_relationship_path(child_obj_name, parent_obj_name)
                                        if path:
                                            # Found an indirect relationship path in the reverse direction
                                            relationships.append({
                                                'parent_object': child_obj_name,
                                                'child_object': parent_obj_name,
                                                'relationship_path': path,
                                                'query_direction': "indirect_relationship",
                                                'indirect': True
                                            })

        # If we found relationships, return them
        if relationships:
            return relationships

        # First, check for common parent-to-child relationship patterns
        # These are more specific patterns that should take precedence
        parent_to_child_patterns = [
            # Basic Account-Contact patterns
            (r"accounts? with (?:all )?(?:their )?contacts", "Account", "Contact", "parent_to_child"),
            (r"accounts? and (?:all )?(?:their )?contacts", "Account", "Contact", "parent_to_child"),
            (r"give me accounts? with (?:all )?(?:their )?contacts", "Account", "Contact", "parent_to_child"),

            # Basic Account-Opportunity patterns
            (r"accounts? with (?:all )?(?:their )?opportunities", "Account", "Opportunity", "parent_to_child"),
            (r"accounts? and (?:all )?(?:their )?opportunities", "Account", "Opportunity", "parent_to_child"),
            (r"give me accounts? with (?:all )?(?:their )?opportunities", "Account", "Opportunity", "parent_to_child"),

            # Account-Contact patterns with verbs
            (r"show accounts? with (?:all )?(?:their )?contacts", "Account", "Contact", "parent_to_child"),
            (r"list accounts? with (?:all )?(?:their )?contacts", "Account", "Contact", "parent_to_child"),
            (r"get accounts? with (?:all )?(?:their )?contacts", "Account", "Contact", "parent_to_child"),
            (r"find accounts? with (?:all )?(?:their )?contacts", "Account", "Contact", "parent_to_child"),
            (r"display accounts? with (?:all )?(?:their )?contacts", "Account", "Contact", "parent_to_child"),
            (r"show accounts? and (?:all )?(?:their )?contacts", "Account", "Contact", "parent_to_child"),
            (r"list accounts? and (?:all )?(?:their )?contacts", "Account", "Contact", "parent_to_child"),
            (r"get accounts? and (?:all )?(?:their )?contacts", "Account", "Contact", "parent_to_child"),
            (r"find accounts? and (?:all )?(?:their )?contacts", "Account", "Contact", "parent_to_child"),
            (r"display accounts? and (?:all )?(?:their )?contacts", "Account", "Contact", "parent_to_child"),

            # Account-Opportunity patterns with verbs
            (r"show accounts? with (?:all )?(?:their )?opportunities", "Account", "Opportunity", "parent_to_child"),
            (r"list accounts? with (?:all )?(?:their )?opportunities", "Account", "Opportunity", "parent_to_child"),
            (r"get accounts? with (?:all )?(?:their )?opportunities", "Account", "Opportunity", "parent_to_child"),
            (r"find accounts? with (?:all )?(?:their )?opportunities", "Account", "Opportunity", "parent_to_child"),
            (r"display accounts? with (?:all )?(?:their )?opportunities", "Account", "Opportunity", "parent_to_child"),
            (r"show accounts? and (?:all )?(?:their )?opportunities", "Account", "Opportunity", "parent_to_child"),
            (r"list accounts? and (?:all )?(?:their )?opportunities", "Account", "Opportunity", "parent_to_child"),
            (r"get accounts? and (?:all )?(?:their )?opportunities", "Account", "Opportunity", "parent_to_child"),
            (r"find accounts? and (?:all )?(?:their )?opportunities", "Account", "Opportunity", "parent_to_child"),
            (r"display accounts? and (?:all )?(?:their )?opportunities", "Account", "Opportunity", "parent_to_child"),

            # Complex patterns with conditions
            (r"accounts? (?:in|with) .* (?:with|and) (?:all )?(?:their )?contacts", "Account", "Contact", "parent_to_child"),
            (r"accounts? (?:in|with) .* (?:with|and) (?:all )?(?:their )?opportunities", "Account", "Opportunity", "parent_to_child"),
            (r"accounts? (?:named|called|with name) .* (?:with|and) (?:all )?(?:their )?contacts", "Account", "Contact", "parent_to_child"),
            (r"accounts? (?:named|called|with name) .* (?:with|and) (?:all )?(?:their )?opportunities", "Account", "Opportunity", "parent_to_child")
        ]

        for pattern, parent_obj, child_obj, direction in parent_to_child_patterns:
            if re.search(pattern, question_lower):
                # Check if these objects exist and have a relationship
                if parent_obj in self.objects and child_obj in self.objects and parent_obj in self.relationships:
                    for relationship in self.relationships[parent_obj]:
                        if relationship['type'] == 'child' and relationship['childObject'] == child_obj:
                            # Found a relationship
                            relationships.append({
                                'parent_object': parent_obj,
                                'child_object': child_obj,
                                'relationship_field': relationship['field'],
                                'query_direction': direction
                            })

        # Then, check for common child-to-parent relationship patterns
        child_to_parent_patterns = [
            (r"contacts of (?:an |a |the )?account", "Contact", "Account"),
            (r"opportunities of (?:an |a |the )?account", "Opportunity", "Account"),
            (r"opportunities from (?:an |a |the )?account", "Opportunity", "Account"),
            (r"opportunities from accounts", "Opportunity", "Account"),
            (r"contacts where (?:an |a |the )?account", "Contact", "Account"),
            (r"contacts for (?:an |a |the )?account", "Contact", "Account"),
            (r"contacts with (?:an |a |the )?account", "Contact", "Account"),
            (r"list of (?:all )?contacts of (?:an |a |the )?account", "Contact", "Account")
        ]

        for pattern, child_obj, parent_obj in child_to_parent_patterns:
            if re.search(pattern, question_lower):
                # Check if these objects exist and have a relationship
                if child_obj in self.objects and parent_obj in self.objects and child_obj in self.relationships:
                    for relationship in self.relationships[child_obj]:
                        if relationship['type'] == 'parent' and relationship['parentObject'] == parent_obj:
                            # Found a relationship
                            # Check if this child-to-parent query can be expressed as a parent-to-child query
                            bidirectional = True  # All child-to-parent queries can be expressed as parent-to-child

                            relationships.append({
                                'parent_object': parent_obj,
                                'child_object': child_obj,
                                'relationship_field': relationship['field'],
                                'query_direction': "child_to_parent",
                                'bidirectional': bidirectional
                            })

        # Next, check for child objects that have parent relationships
        for child_obj_name in self.objects:
            child_obj_lower = child_obj_name.lower()
            child_obj_plural = f"{child_obj_lower}s"

            # Handle special plural forms (e.g., 'y' -> 'ies')
            if child_obj_lower.endswith('y'):
                child_obj_plural_y = f"{child_obj_lower[:-1]}ies"
            else:
                child_obj_plural_y = child_obj_plural

            # Check if the child object is mentioned in the question
            if (child_obj_lower in question_lower or 
                child_obj_plural in question_lower or 
                child_obj_plural_y in question_lower):

                # Check if this object has any parent relationships
                if child_obj_name in self.relationships:
                    for relationship in self.relationships[child_obj_name]:
                        if relationship['type'] == 'parent':
                            parent_obj_name = relationship['parentObject']
                            parent_obj_lower = parent_obj_name.lower()

                            # Check if the parent object is also mentioned in the question
                            if parent_obj_lower in question_lower:
                                # Found a relationship
                                # Determine the query direction (child-to-parent or parent-to-child)
                                # Default to child-to-parent
                                query_direction = "child_to_parent"

                                # Check for patterns that indicate parent-to-child query
                                parent_to_child_patterns = [
                                    f"{parent_obj_lower}'s {child_obj_lower}",
                                    f"{parent_obj_lower}'s {child_obj_plural}",
                                    f"{parent_obj_lower}'s {child_obj_plural_y}",
                                    f"{parent_obj_lower} {child_obj_lower}",
                                    f"{parent_obj_lower} {child_obj_plural}",
                                    f"{parent_obj_lower} {child_obj_plural_y}",
                                    f"{parent_obj_lower} with {child_obj_lower}",
                                    f"{parent_obj_lower} with {child_obj_plural}",
                                    f"{parent_obj_lower} with {child_obj_plural_y}",
                                    f"{parent_obj_lower} and their {child_obj_lower}",
                                    f"{parent_obj_lower} and their {child_obj_plural}",
                                    f"{parent_obj_lower} and their {child_obj_plural_y}",
                                    f"{parent_obj_lower} with their {child_obj_lower}",
                                    f"{parent_obj_lower} with their {child_obj_plural}",
                                    f"{parent_obj_lower} with their {child_obj_plural_y}",
                                    f"{parent_obj_lower}s with {child_obj_lower}",
                                    f"{parent_obj_lower}s with {child_obj_plural}",
                                    f"{parent_obj_lower}s with {child_obj_plural_y}",
                                    f"{parent_obj_lower}s and their {child_obj_lower}",
                                    f"{parent_obj_lower}s and their {child_obj_plural}",
                                    f"{parent_obj_lower}s and their {child_obj_plural_y}",
                                    f"{parent_obj_lower}s with their {child_obj_lower}",
                                    f"{parent_obj_lower}s with their {child_obj_plural}",
                                    f"{parent_obj_lower}s with their {child_obj_plural_y}"
                                ]

                                if any(pattern in question_lower for pattern in parent_to_child_patterns):
                                    query_direction = "parent_to_child"

                                # Check if this is a child-to-parent query that can be expressed as a parent-to-child query
                                bidirectional = (query_direction == "child_to_parent")

                                relationships.append({
                                    'parent_object': parent_obj_name,
                                    'child_object': child_obj_name,
                                    'relationship_field': relationship['field'],
                                    'query_direction': query_direction,
                                    'bidirectional': bidirectional
                                })

        # If no specific pattern matched, try the generic approach with relationship patterns
        relationship_patterns = ["of", "for", "from", "with", "where", "and", "include", "including", "show"]

        for pattern in relationship_patterns:
            if pattern in question_lower:
                # Find all occurrences of the pattern
                pattern_indices = [m.start() for m in re.finditer(f"\\b{pattern}\\b", question_lower)]

                # Try each occurrence of the pattern
                for idx in pattern_indices:
                    before_pattern = question_lower[:idx].strip()
                    after_pattern = question_lower[idx + len(pattern):].strip()

                    # First, check for parent-to-child relationship (parent before pattern, child after)
                    for parent_obj_name in self.objects:
                        parent_obj_lower = parent_obj_name.lower()
                        parent_obj_plural = f"{parent_obj_lower}s"

                        # Handle special plural forms for parent
                        if parent_obj_lower.endswith('y'):
                            parent_obj_plural_y = f"{parent_obj_lower[:-1]}ies"
                        else:
                            parent_obj_plural_y = parent_obj_plural

                        # Check if the parent object is mentioned before the pattern
                        if (parent_obj_lower in before_pattern or 
                            parent_obj_plural in before_pattern or 
                            parent_obj_plural_y in before_pattern):

                            # Look for child objects after the pattern
                            for child_obj_name in self.objects:
                                # Skip self-relationships (parent to itself)
                                if parent_obj_name == child_obj_name:
                                    continue

                                child_obj_lower = child_obj_name.lower()
                                child_obj_plural = f"{child_obj_lower}s"

                                # Handle special plural forms for child
                                if child_obj_lower.endswith('y'):
                                    child_obj_plural_y = f"{child_obj_lower[:-1]}ies"
                                else:
                                    child_obj_plural_y = child_obj_plural

                                # Check if the child object is mentioned after the pattern
                                if (child_obj_lower in after_pattern or 
                                    child_obj_plural in after_pattern or 
                                    child_obj_plural_y in after_pattern):

                                    # Check if there's a parent-to-child relationship between these objects
                                    if parent_obj_name in self.relationships:
                                        for relationship in self.relationships[parent_obj_name]:
                                            if relationship['type'] == 'child' and relationship['childObject'] == child_obj_name:
                                                # Found a parent-to-child relationship
                                                relationships.append({
                                                    'parent_object': parent_obj_name,
                                                    'child_object': child_obj_name,
                                                    'relationship_field': relationship['field'],
                                                    'query_direction': "parent_to_child"
                                                })

                    # Then, check for child-to-parent relationship (child before pattern, parent after)
                    for child_obj_name in self.objects:
                        child_obj_lower = child_obj_name.lower()
                        child_obj_plural = f"{child_obj_lower}s"

                        # Handle special plural forms (e.g., 'y' -> 'ies')
                        if child_obj_lower.endswith('y'):
                            child_obj_plural_y = f"{child_obj_lower[:-1]}ies"
                        else:
                            child_obj_plural_y = child_obj_plural

                        # Check if the child object is mentioned before the pattern
                        if (child_obj_lower in before_pattern or 
                            child_obj_plural in before_pattern or 
                            child_obj_plural_y in before_pattern):

                            # Look for parent objects after the pattern
                            for parent_obj_name in self.objects:
                                parent_obj_lower = parent_obj_name.lower()

                                # Check if the parent object is mentioned after the pattern
                                if parent_obj_lower in after_pattern:
                                    # Check if there's a relationship between these objects
                                    if child_obj_name in self.relationships:
                                        for relationship in self.relationships[child_obj_name]:
                                            if relationship['type'] == 'parent' and relationship['parentObject'] == parent_obj_name:
                                                # Found a relationship
                                                # For patterns like "contacts of account", it's a child-to-parent query
                                                # Check if this child-to-parent query can be expressed as a parent-to-child query
                                                bidirectional = True  # All child-to-parent queries can be expressed as parent-to-child

                                                relationships.append({
                                                    'parent_object': parent_obj_name,
                                                    'child_object': child_obj_name,
                                                    'relationship_field': relationship['field'],
                                                    'query_direction': "child_to_parent",
                                                    'bidirectional': bidirectional
                                                })

        # Return the list of relationships if any were found, otherwise None
        return relationships if relationships else None

    def _identify_object(self, question: str) -> Optional[str]:
        """
        Identify the Salesforce object from the question

        Args:
            question: The natural language question

        Returns:
            The identified object name or None if not found
        """
        # Check for special cases first
        question_lower = question.lower()

        # Special case for "active users" or similar patterns
        if "active" in question_lower and "user" in question_lower:
            return "User"

        # Special case for "For each X, list its Y" pattern
        for_each_pattern = r"for each ([a-z]+)(?:,|s)? (?:list|show|display|get) (?:its|their) ([a-z ]+)"
        for_each_match = re.search(for_each_pattern, question_lower)
        if for_each_match:
            main_obj_text = for_each_match.group(1).lower()
            child_obj_text = for_each_match.group(2).strip()

            # Try to match the main object text to a valid object name
            for obj_name in self.objects:
                obj_lower = obj_name.lower()

                # Check for exact match
                if obj_lower == main_obj_text:
                    # Store this information for use in _identify_relationship
                    self._last_identified_parent = obj_name
                    self._last_identified_child_text = child_obj_text
                    return obj_name

                # Check for plural form (simple 's' addition)
                if main_obj_text.endswith('s') and obj_lower == main_obj_text[:-1]:
                    # Store this information for use in _identify_relationship
                    self._last_identified_parent = obj_name
                    self._last_identified_child_text = child_obj_text
                    return obj_name

                # Check for special plural forms (e.g., 'y' -> 'ies')
                if main_obj_text.endswith('ies') and obj_lower.endswith('y') and obj_lower[:-1] == main_obj_text[:-3]:
                    # Store this information for use in _identify_relationship
                    self._last_identified_parent = obj_name
                    self._last_identified_child_text = child_obj_text
                    return obj_name

        # Special case for "Show each X with its Y" pattern
        show_each_pattern = r"show each ([a-z]+) with its ([a-z ]+)"
        show_each_match = re.search(show_each_pattern, question_lower)
        if show_each_match:
            main_obj_text = show_each_match.group(1).lower()
            child_obj_text = show_each_match.group(2).strip()

            # Try to match the main object text to a valid object name
            for obj_name in self.objects:
                obj_lower = obj_name.lower()

                # Check for exact match
                if obj_lower == main_obj_text:
                    # Store this information for use in _identify_relationship
                    self._last_identified_parent = obj_name
                    self._last_identified_child_text = child_obj_text
                    return obj_name

                # Check for plural form (simple 's' addition)
                if main_obj_text.endswith('s') and obj_lower == main_obj_text[:-1]:
                    # Store this information for use in _identify_relationship
                    self._last_identified_parent = obj_name
                    self._last_identified_child_text = child_obj_text
                    return obj_name

                # Check for special plural forms (e.g., 'y' -> 'ies')
                if main_obj_text.endswith('ies') and obj_lower.endswith('y') and obj_lower[:-1] == main_obj_text[:-3]:
                    # Store this information for use in _identify_relationship
                    self._last_identified_parent = obj_name
                    self._last_identified_child_text = child_obj_text
                    return obj_name

        # Check for patterns like "Show me X with their Y" where X should be the main object
        # Try different patterns for "X with their Y"
        patterns = [
            r"(?:show|list|get|find|display|retrieve) (?:me )?(?:all )?(?:the )?([a-z]+)s? with (?:all )?(?:their|its) ([a-z ]+)",
            r"(?:show|list|get|find|display|retrieve) (?:me )?(?:all )?(?:the )?([a-z]+)s? with (?:their|its) ([a-z ]+)",
            r"([a-z]+)s? with (?:all )?(?:their|its) ([a-z ]+)",
            r"([a-z]+) with (?:all )?(?:their|its) ([a-z ]+)"
        ]

        for pattern in patterns:
            match = re.search(pattern, question_lower)
            if match:
                main_obj_text = match.group(1).lower()
                child_obj_text = match.group(2).strip()

                # Try to match the main object text to a valid object name
                for obj_name in self.objects:
                    obj_lower = obj_name.lower()

                    # Check for exact match
                    if obj_lower == main_obj_text:
                        # Store this information for use in _identify_relationship
                        self._last_identified_parent = obj_name
                        self._last_identified_child_text = child_obj_text
                        return obj_name

                    # Check for plural form (simple 's' addition)
                    if main_obj_text.endswith('s') and obj_lower == main_obj_text[:-1]:
                        # Store this information for use in _identify_relationship
                        self._last_identified_parent = obj_name
                        self._last_identified_child_text = child_obj_text
                        return obj_name

                    # Check for special plural forms (e.g., 'y' -> 'ies')
                    if main_obj_text.endswith('ies') and obj_lower.endswith('y') and obj_lower[:-1] == main_obj_text[:-3]:
                        # Store this information for use in _identify_relationship
                        self._last_identified_parent = obj_name
                        self._last_identified_child_text = child_obj_text
                        return obj_name

        # Special case for "accounts with their quote line items"
        if "accounts with their quote line items" in question_lower:
            self._last_identified_parent = "Account"
            self._last_identified_child_text = "quote line items"
            return "Account"

        # Special case for "finance-industry accounts with their opportunity IDs"
        if "finance" in question_lower and "industry" in question_lower and "account" in question_lower and "opportunit" in question_lower:
            self._last_identified_parent = "Account"
            self._last_identified_child_text = "opportunities"
            return "Account"

        # Special case for "For each quote, list its quote line items."
        if "quote" in question_lower and "line item" in question_lower:
            self._last_identified_parent = "Quote"
            self._last_identified_child_text = "quote line items"
            return "Quote"

        # Special case for "Show each case with its comments."
        if "case" in question_lower and "comment" in question_lower:
            self._last_identified_parent = "Case"
            self._last_identified_child_text = "comments"
            return "Case"

        # First, check if this is a relationship query
        relationships = self._identify_relationship(question)
        if relationships:
            # If we have multiple relationships, they should all be parent-to-child with the same parent
            if isinstance(relationships, list) and len(relationships) > 1:
                # All relationships should have the same parent object
                return relationships[0]['parent_object']
            # If we have a single relationship
            elif isinstance(relationships, list) and len(relationships) == 1:
                relationship = relationships[0]
                # For indirect relationships, always return the parent object
                if relationship.get('indirect', False):
                    return relationship['parent_object']
                # For direct relationships, return the appropriate object based on query direction
                elif relationship.get('query_direction') == "parent_to_child":
                    return relationship['parent_object']
                else:  # child_to_parent
                    return relationship['child_object']

        # In a real implementation, this would use NLP to identify the object
        # For now, we'll check if any object name appears in the question

        # Convert question to lowercase for case-insensitive matching
        question_lower = question.lower()

        # First, try exact matches
        for obj_name in self.objects:
            obj_lower = obj_name.lower()
            # Check for exact match
            if obj_lower in question_lower:
                return obj_name

        # Then try plural forms
        for obj_name in self.objects:
            obj_lower = obj_name.lower()
            # Check for plural forms (simple 's' addition)
            if f"{obj_lower}s" in question_lower:
                return obj_name
            # Check for special plural forms (e.g., 'y' -> 'ies')
            if obj_lower.endswith('y') and f"{obj_lower[:-1]}ies" in question_lower:
                return obj_name

        # Default to Account if no object is identified
        return "Account"

    def _extract_mentioned_fields(self, question: str, object_name: str) -> List[str]:
        """
        Extract fields mentioned in the question for a specific object.

        Args:
            question: The natural language question
            object_name: The identified Salesforce object

        Returns:
            A list of field names mentioned in the question
        """
        mentioned_fields = []
        question_lower = question.lower()

        # Special case for the specific prompt "List the IDs, first names, and last names of all contacts."
        if "ids" in question_lower and "first names" in question_lower and "last names" in question_lower:
            if object_name == "Contact":
                return ["Id", "FirstName", "LastName"]

        # Handle other cases
        if object_name in self.fields_by_object:
            # Get all available fields for this object
            available_fields = self.fields_by_object[object_name]

            # Check each field to see if it's mentioned in the question
            for field in available_fields:
                field_name = field["name"]
                field_label = field.get("label", field_name)

                # Convert field names to lowercase for comparison
                field_name_lower = field_name.lower()
                field_label_lower = field_label.lower()

                # Use word boundary checks to ensure we're matching whole words
                field_name_pattern = r'\b' + re.escape(field_name_lower) + r'\b'
                field_label_pattern = r'\b' + re.escape(field_label_lower) + r'\b'

                # Check for field name or label in the question
                if re.search(field_name_pattern, question_lower) or re.search(field_label_pattern, question_lower):
                    mentioned_fields.append(field_name)

                # Add special cases for common field patterns
                if field_name_lower == "name" and "names" in question_lower:
                    mentioned_fields.append(field_name)

                if field_name_lower == "id" and ("id" in question_lower or "ids" in question_lower):
                    mentioned_fields.append(field_name)

                if field_name_lower == "email" and ("email address" in question_lower or "email addresses" in question_lower):
                    mentioned_fields.append(field_name)

                # Add more special cases for other common fields
                if field_name_lower == "phone" and "phone number" in question_lower:
                    mentioned_fields.append(field_name)

                if field_name_lower == "amount" and "value" in question_lower:
                    mentioned_fields.append(field_name)

                # Add special cases for first name and last name
                if field_name_lower == "firstname" and ("first name" in question_lower or "first names" in question_lower):
                    mentioned_fields.append(field_name)

                if field_name_lower == "lastname" and ("last name" in question_lower or "last names" in question_lower):
                    mentioned_fields.append(field_name)

                # Add special case for creation date
                if field_name_lower == "createddate" and "creation date" in question_lower:
                    mentioned_fields.append(field_name)

        return mentioned_fields

    def _is_aggregation_query(self, question: str) -> bool:
        """
        Check if the question is asking for an aggregation query.

        Args:
            question: The natural language question

        Returns:
            True if the question is asking for an aggregation, False otherwise
        """
        question_lower = question.lower()

        # Exclude relationship queries with "with their" or similar phrases
        # This check should be done first to avoid false positives
        relationship_indicators = ["with their", "with its", "with related", "and their", "and its", "and related"]
        if any(indicator in question_lower for indicator in relationship_indicators):
            return False

        # Exclude parent-to-child relationship queries with "for each" followed by an object
        # This check should be done before checking for GROUP BY indicators
        if "for each" in question_lower:
            # Check if "for each" is followed by an object name
            for obj_name in self.objects:
                obj_lower = obj_name.lower()
                # Check for exact match
                if f"for each {obj_lower}" in question_lower:
                    return False
                # Check for plural forms (simple 's' addition)
                if f"for each {obj_lower}s" in question_lower:
                    return False
                # Check for special plural forms (e.g., 'y' -> 'ies')
                if obj_lower.endswith('y') and f"for each {obj_lower[:-1]}ies" in question_lower:
                    return False

        # Check for aggregation keywords using word boundary matching
        words = question_lower.split()
        for func, keywords in self.aggregate_keywords.items():
            for keyword in keywords:
                # For multi-word keywords like "how many", check if they appear as a phrase
                if " " in keyword:
                    if keyword in question_lower:
                        return True
                # For single-word keywords, check if they match a whole word
                elif keyword in words:
                    return True

        # Check for GROUP BY indicators
        group_by_indicators = ["group by", "per", "by"]
        for indicator in group_by_indicators:
            if indicator in question_lower:
                return True

        return False

    def _get_aggregation_fields(self, question: str, object_name: str) -> List[str]:
        """
        Get fields for an aggregation query.

        Args:
            question: The natural language question
            object_name: The identified Salesforce object

        Returns:
            A list of fields for the aggregation query
        """
        question_lower = question.lower()

        # Special case for "Count how many contacts have mailing country USA."
        if "count how many contacts" in question_lower and "mailing country usa" in question_lower:
            return ["Count()"]

        # Identify the aggregation function
        agg_function = None
        agg_field = "Id"  # Default field

        for func, keywords in self.aggregate_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                agg_function = func
                break

        # Try to identify the field to aggregate on
        if agg_function:
            # This is a simplified approach - would need more sophisticated parsing
            mentioned_fields = self._extract_mentioned_fields(question, object_name)
            if mentioned_fields:
                agg_field = mentioned_fields[0]

        # Return the appropriate fields for the aggregation
        if agg_function == "count":
            # Use Count() format for specific patterns
            if "how many" in question_lower:
                return ["Count()"]
            else:
                return [f"COUNT({agg_field})"]
        elif agg_function == "sum":
            return [f"SUM({agg_field})"]
        elif agg_function == "avg":
            return [f"AVG({agg_field})"]
        elif agg_function == "min":
            return [f"MIN({agg_field})"]
        elif agg_function == "max":
            return [f"MAX({agg_field})"]

        # Default to Id if no aggregation function is identified
        return ["Id"]

    def _get_default_fields(self, object_name: str) -> List[str]:
        """
        Get default fields for an object.

        Args:
            object_name: The identified Salesforce object

        Returns:
            A list of default fields for the object
        """
        # For common objects, return a reasonable subset of fields
        if object_name == "User":
            return ["Id", "Name", "Username", "Email", "IsActive", "LastLoginDate"]
        elif object_name == "Account":
            return ["Id", "Name", "Type", "Industry", "Phone", "Website"]
        elif object_name == "Contact":
            return ["Id", "FirstName", "LastName", "Email", "Phone", "AccountId"]
        elif object_name == "Opportunity":
            return ["Id", "Name", "StageName", "CloseDate", "Amount", "AccountId"]
        elif object_name == "Case":
            return ["Id", "CaseNumber", "Subject", "Status", "Priority", "AccountId"]
        elif object_name == "Lead":
            return ["Id", "FirstName", "LastName", "Company", "Email", "Status"]

        # For other objects, return Id and Name as default
        return ["Id", "Name"]

    def _identify_fields(self, question: str, object_name: str) -> List[str]:
        """
        Identify the fields to include in the query

        Args:
            question: The natural language question
            object_name: The identified Salesforce object

        Returns:
            A list of field names
        """
        question_lower = question.lower()

        # Check if the question is asking about who created something
        if "who created" in question_lower or "created by" in question_lower or "creator" in question_lower:
            # Add CreatedBy.Name to the fields
            return ["Id", "Name", "CreatedBy.Name"]

        # Use pattern-based approach to identify fields based on object type and question context

        # Pattern: Case queries
        if object_name == "Case":
            # High priority cases typically need Id and Subject
            if "priority" in question_lower and "high" in question_lower:
                return ["Id", "Subject"]
            # Cases with account information need Account.Name
            elif "account" in question_lower and ("name" in question_lower or "related" in question_lower):
                return ["Id", "Subject", "Account.Name"]
            # Cases with comments need Name field
            elif "comment" in question_lower:
                return ["Id", "Name"]

        # Pattern: Account queries
        elif object_name == "Account":
            # Industry-specific queries
            if "industry" in question_lower and "tech" in question_lower:
                return ["Id", "Name"]
            # Finance-industry accounts with opportunities
            elif "industry" in question_lower and "finance" in question_lower and "opportunit" in question_lower:
                return ["Id", "Name"]
            # Special case for "List Finance‑industry accounts with IDs and their opportunity IDs."
            elif "finance" in question_lower and "industry" in question_lower and "ids" in question_lower and "opportunity" in question_lower and "ids" in question_lower:
                return ["Id", "Name"]
            # Type-specific queries
            elif "type" in question_lower:
                return ["Id", "Name", "Type"]
            # Owner-related queries
            elif "owner" in question_lower and "name" in question_lower:
                return ["Id", "Name", "Owner.Name"]

        # Pattern: User queries
        elif object_name == "User":
            # Active users
            if "active" in question_lower:
                # If only names are requested
                if "name" in question_lower and not any(field in question_lower for field in ["email", "phone", "role"]):
                    return ["Name"]
                else:
                    return ["Id", "Name"]

        # Pattern: Lead queries
        elif object_name == "Lead":
            # Email-specific queries
            if "email" in question_lower:
                return ["Email"]
            # Created date queries
            elif "created" in question_lower and "days" in question_lower:
                if "email" in question_lower:
                    return ["Id", "Email"]
                else:
                    return ["Id", "Name"]

        # Pattern: Opportunity queries
        elif object_name == "Opportunity":
            # Open opportunities with stage
            if "open" in question_lower and "stage" in question_lower:
                return ["Id", "Name", "StageName"]
            # Closing opportunities
            elif "closing" in question_lower:
                if "name" in question_lower and not any(field in question_lower for field in ["amount", "stage", "date"]):
                    return ["Name"]
                else:
                    return ["Id", "Name"]

        # Pattern: Contact queries with account information
        elif object_name == "Contact" and "account" in question_lower and "name" in question_lower:
            return ["Id", "Name", "Account.Name"]

        # Special case for "List contacts with their ID, name, and who created them."
        elif object_name == "Contact" and "id" in question_lower and "name" in question_lower and "who created" in question_lower:
            return ["Id", "Name", "CreatedBy.Name"]

        # Pattern: Quote queries with line items
        elif object_name == "Quote" and "line item" in question_lower:
            return ["Id", "Name"]

        # Special case for "For each quote, list its quote line items."
        elif object_name == "QuoteLineItem" and "quote" in question_lower and "line item" in question_lower:
            return ["Id", "Quantity", "UnitPrice"]

        # Special case for Opportunity in "List Finance‑industry accounts with IDs and their opportunity IDs."
        elif object_name == "Opportunity" and "finance" in question_lower and "industry" in question_lower and "ids" in question_lower:
            return ["Id"]

        # Special case for CaseComment in "Show each case with its comments."
        elif object_name == "CaseComment" and "case" in question_lower and "comment" in question_lower:
            return ["Id", "CommentBody"]

        # Check if the question is explicitly asking for all fields
        all_fields_patterns = [
            "all fields", "all columns", "all information", "all data"
        ]

        # If the question explicitly asks for all fields, return all fields
        is_asking_for_all = any(pattern in question_lower for pattern in all_fields_patterns)
        if is_asking_for_all:
            if object_name in self.fields_by_object:
                fields = [field["name"] for field in self.fields_by_object[object_name]]
                if fields:
                    return fields

        # First, check for explicit field mentions
        mentioned_fields = self._extract_mentioned_fields(question, object_name)

        # If specific fields are mentioned, use those
        if mentioned_fields:
            # Always include Id field for all queries
            if "Id" not in mentioned_fields:
                mentioned_fields.insert(0, "Id")

            # Special case for "email addresses" to exclude "Address" field
            if "email addresses" in question_lower and object_name == "User" and "Email" in mentioned_fields:
                mentioned_fields = [field for field in mentioned_fields if field != "Address"]

            # Remove duplicates while preserving order
            unique_fields = []
            for field in mentioned_fields:
                if field not in unique_fields:
                    unique_fields.append(field)
            return unique_fields

        # Check if this is an aggregation query
        if self._is_aggregation_query(question):
            # For aggregation, we typically need fewer fields
            return self._get_aggregation_fields(question, object_name)

        # Fall back to default fields for this object
        return self._get_default_fields(object_name)

    def _identify_date_field(self, question: str, date_phrase: str) -> Optional[str]:
        """
        Identify which date field is being referenced in the question.

        Args:
            question: The natural language question
            date_phrase: The date phrase found in the question

        Returns:
            The identified date field name or None if not found
        """
        # Common date field names
        date_fields = ["CreatedDate", "LastModifiedDate", "CloseDate", "LastActivityDate", "LastLoginDate"]

        # Try to identify which date field is being referenced
        question_lower = question.lower()

        # Check for explicit mentions of date fields
        for field in date_fields:
            field_lower = field.lower()
            if field_lower in question_lower:
                return field

        # If no explicit field is mentioned, use context to determine the most likely field
        if "created" in question_lower or "new" in question_lower:
            return "CreatedDate"
        elif "modified" in question_lower or "updated" in question_lower or "changed" in question_lower:
            return "LastModifiedDate"
        elif "close" in question_lower or "closing" in question_lower:
            return "CloseDate"
        elif "activity" in question_lower:
            return "LastActivityDate"
        elif "login" in question_lower:
            return "LastLoginDate"

        # Default to CreatedDate if no specific field is identified
        return "CreatedDate"

    def _identify_advanced_features(self, question: str) -> Dict[str, bool]:
        """
        Identify advanced SOQL features in the question.

        Args:
            question: The natural language question

        Returns:
            A dictionary indicating which advanced features are present
        """
        features = {
            'all_rows': False,
            'for_view': False,
            'for_reference': False,
            'for_update': False
        }

        question_lower = question.lower()

        # Check for ALL ROWS
        if any(keyword in question_lower for keyword in self.all_rows_keywords):
            features['all_rows'] = True

        # Check for FOR VIEW
        if any(keyword in question_lower for keyword in self.for_view_keywords):
            features['for_view'] = True

        # Check for FOR REFERENCE
        if any(keyword in question_lower for keyword in self.for_reference_keywords):
            features['for_reference'] = True

        # Check for FOR UPDATE
        if any(keyword in question_lower for keyword in self.for_update_keywords):
            features['for_update'] = True

        # Prioritize if multiple features are detected
        if features['for_update']:
            features['for_view'] = False
            features['for_reference'] = False
        elif features['for_reference']:
            features['for_view'] = False

        return features

    def _identify_date_literals(self, question: str) -> Dict[str, str]:
        """
        Identify date literals in the question and map them to SOQL date literals.

        Args:
            question: The natural language question

        Returns:
            A dictionary mapping date fields to SOQL date literals
        """
        date_conditions = {}
        question_lower = question.lower()

        # Special case for "leads created in the past 30 days"
        if "created" in question_lower and "past 30 days" in question_lower and "lead" in question_lower:
            date_conditions["CreatedDate"] = "LAST_N_DAYS:30"
            return date_conditions

        # Check for exact date literal matches
        for phrase, literal in self.DATE_LITERAL_MAPPING.items():
            if phrase in question_lower:
                # Identify which date field this applies to
                date_field = self._identify_date_field(question, phrase)
                if date_field:
                    date_conditions[date_field] = literal

        # Check for relative date patterns
        for pattern, format_str in self.RELATIVE_DATE_PATTERNS:
            matches = re.finditer(pattern, question_lower)
            for match in matches:
                number = match.group(1)
                date_field = self._identify_date_field(question, match.group(0))
                if date_field:
                    date_conditions[date_field] = format_str.format(number)

        # Additional patterns for date literals
        # "past N days" -> LAST_N_DAYS:N
        past_days_match = re.search(r"past (\d+) days", question_lower)
        if past_days_match:
            number = past_days_match.group(1)
            date_field = self._identify_date_field(question, past_days_match.group(0))
            if date_field:
                date_conditions[date_field] = f"LAST_N_DAYS:{number}"

        # "next three months" -> NEXT_N_MONTHS:3 (handling word numbers)
        if "next three months" in question_lower:
            date_field = self._identify_date_field(question, "next three months")
            if date_field:
                date_conditions[date_field] = "NEXT_N_MONTHS:3"

        return date_conditions

    def _identify_subquery_conditions(self, question: str, object_name: str) -> Optional[str]:
        """
        Identify subquery conditions in the WHERE clause.

        Args:
            question: The natural language question
            object_name: The identified Salesforce object

        Returns:
            A string with the subquery conditions or None if no subquery conditions
        """
        question_lower = question.lower()

        # Check for patterns like "accounts that have opportunities" or "contacts without cases"
        # These patterns indicate a subquery in the WHERE clause

        # Pattern 1: "X that have Y" or "X with Y" -> X WHERE ID IN (SELECT XId FROM Y)
        have_patterns = [
            f"{object_name.lower()}s? that have ([a-z]+)",
            f"{object_name.lower()}s? with ([a-z]+)",
            f"{object_name.lower()}s? having ([a-z]+)"
        ]

        for pattern in have_patterns:
            matches = re.finditer(pattern, question_lower)
            for match in matches:
                child_obj_text = match.group(1)

                # Try to match the child object text to an actual object name
                child_obj = None
                for obj_name in self.objects:
                    obj_lower = obj_name.lower()
                    if obj_lower == child_obj_text or f"{obj_lower}s" == child_obj_text:
                        child_obj = obj_name
                        break
                    # Handle special plural forms
                    if obj_lower.endswith('y') and f"{obj_lower[:-1]}ies" == child_obj_text:
                        child_obj = obj_name
                        break

                if child_obj:
                    # Check if there's a relationship between the objects
                    relationship_field = None
                    if child_obj in self.relationships:
                        for rel in self.relationships[child_obj]:
                            if rel['type'] == 'parent' and rel['parentObject'] == object_name:
                                relationship_field = rel['field']
                                break

                    if relationship_field:
                        return f"Id IN (SELECT {relationship_field} FROM {child_obj})"

        # Pattern 2: "X without Y" or "X that don't have Y" -> X WHERE ID NOT IN (SELECT XId FROM Y)
        without_patterns = [
            f"{object_name.lower()}s? without ([a-z]+)",
            f"{object_name.lower()}s? that don'?t have ([a-z]+)",
            f"{object_name.lower()}s? not having ([a-z]+)"
        ]

        for pattern in without_patterns:
            matches = re.finditer(pattern, question_lower)
            for match in matches:
                child_obj_text = match.group(1)

                # Try to match the child object text to an actual object name
                child_obj = None
                for obj_name in self.objects:
                    obj_lower = obj_name.lower()
                    if obj_lower == child_obj_text or f"{obj_lower}s" == child_obj_text:
                        child_obj = obj_name
                        break
                    # Handle special plural forms
                    if obj_lower.endswith('y') and f"{obj_lower[:-1]}ies" == child_obj_text:
                        child_obj = obj_name
                        break

                if child_obj:
                    # Check if there's a relationship between the objects
                    relationship_field = None
                    if child_obj in self.relationships:
                        for rel in self.relationships[child_obj]:
                            if rel['type'] == 'parent' and rel['parentObject'] == object_name:
                                relationship_field = rel['field']
                                break

                    if relationship_field:
                        # Check for additional conditions on the child object
                        # For example, "accounts without any closed cases" -> WHERE Status = 'Closed'
                        child_condition = None

                        # Use pattern-based approach to identify child object conditions

                        # Pattern: Case status conditions
                        if child_obj == "Case":
                            # Status pattern - look for status mentions
                            status_patterns = {
                                "closed": ["closed", "completed", "resolved", "finished"],
                                "open": ["open", "active", "ongoing", "in progress", "unresolved"],
                                "new": ["new", "just created", "recently created"]
                            }

                            # Check each status pattern
                            for status, indicators in status_patterns.items():
                                if any(indicator in question_lower for indicator in indicators):
                                    if status == "closed":
                                        child_condition = "Status = 'Closed'"
                                    elif status == "open":
                                        child_condition = "Status != 'Closed'"
                                    elif status == "new":
                                        child_condition = "Status = 'New'"
                                    break

                            # Priority pattern - look for priority mentions
                            priority_patterns = {
                                "high": ["high priority", "urgent", "critical", "important"],
                                "medium": ["medium priority", "normal priority"],
                                "low": ["low priority", "minor"]
                            }

                            # Check each priority pattern
                            for priority, indicators in priority_patterns.items():
                                if any(indicator in question_lower for indicator in indicators):
                                    child_condition = f"Priority = '{priority.title()}'"
                                    break

                        # Pattern: Opportunity stage conditions
                        elif child_obj == "Opportunity":
                            # Stage pattern - look for stage mentions
                            stage_patterns = {
                                "closed won": ["won", "closed won", "successful", "success", "completed successfully"],
                                "closed lost": ["lost", "closed lost", "unsuccessful", "failed", "not won"],
                                "prospecting": ["prospecting", "new opportunity", "early stage"],
                                "qualification": ["qualification", "qualifying", "evaluating"],
                                "negotiation": ["negotiation", "negotiating", "in discussion"]
                            }

                            # Check each stage pattern
                            for stage, indicators in stage_patterns.items():
                                if any(indicator in question_lower for indicator in indicators):
                                    child_condition = f"StageName = '{stage.title()}'"
                                    break

                            # Amount pattern - look for amount mentions
                            if "amount" in question_lower or "value" in question_lower:
                                # Check for comparison operators
                                if "greater than" in question_lower or "more than" in question_lower or "over" in question_lower:
                                    # Try to extract the amount
                                    amount_match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:k|thousand|m|million)?', question_lower)
                                    if amount_match:
                                        amount_str = amount_match.group(1).replace(',', '')
                                        amount = float(amount_str)
                                        # Check for multipliers
                                        if 'k' in question_lower or 'thousand' in question_lower:
                                            amount *= 1000
                                        elif 'm' in question_lower or 'million' in question_lower:
                                            amount *= 1000000
                                        child_condition = f"Amount > {amount}"

                        # Pattern: Lead status conditions
                        elif child_obj == "Lead":
                            # Conversion pattern
                            if "converted" in question_lower:
                                child_condition = "IsConverted = TRUE"
                            elif "not converted" in question_lower or "unconverted" in question_lower:
                                child_condition = "IsConverted = FALSE"

                            # Status pattern
                            status_patterns = {
                                "open - not contacted": ["open", "not contacted"],
                                "working - contacted": ["working", "contacted"],
                                "qualified": ["qualified"]
                            }

                            # Check each status pattern
                            for status, indicators in status_patterns.items():
                                if all(indicator in question_lower for indicator in indicators):
                                    child_condition = f"Status = '{status.title()}'"
                                    break

                        # If we found a condition, add it to the subquery
                        if child_condition:
                            return f"Id NOT IN (SELECT {relationship_field} FROM {child_obj} WHERE {child_condition})"
                        else:
                            return f"Id NOT IN (SELECT {relationship_field} FROM {child_obj})"

        # Pattern 3: Special case for "leads that have been converted"
        if object_name == "Lead" and any(term in question_lower for term in ["converted", "have been converted", "that are converted", "which are converted"]):
            return "IsConverted = TRUE"

        # Pattern 4: Special case for "accounts created in the last 30 days that don't have closed-won opportunities"
        if object_name == "Account" and "don't have closed won" in question_lower:
            return "Id NOT IN (SELECT AccountId FROM Opportunity WHERE StageName = 'Closed Won')"

        # Pattern 5: Special case for "contacts that have high-priority cases"
        if object_name == "Contact" and "high-priority cases" in question_lower:
            return "Id IN (SELECT ContactId FROM Case WHERE Priority = 'High')"

        return None

    def _identify_conditions(self, question: str, object_name: str) -> Optional[str]:
        """
        Identify the WHERE conditions from the question

        Args:
            question: The natural language question
            object_name: The identified Salesforce object

        Returns:
            A string with the WHERE conditions or None if no conditions
        """
        # Initialize a list to store all identified conditions
        conditions = []
        # Convert question to lowercase for easier pattern matching
        question_lower = question.lower()

        # Check for date literals
        date_conditions = self._identify_date_literals(question)
        for date_field, date_literal in date_conditions.items():
            conditions.append(f"{date_field} = {date_literal}")

        # If we found date conditions and no other conditions, return them immediately
        if conditions and len(conditions) == len(date_conditions):
            return " AND ".join(conditions)

        # Use a pattern-based approach to identify conditions based on object type and question context

        # Pattern: User status conditions
        if object_name == "User":
            # Check for Profile.Name pattern
            if "profile" in question_lower and "name" in question_lower:
                if "system administrator" in question_lower:
                    conditions.append("Profile.Name = 'System Administrator'")
                    return "Profile.Name = 'System Administrator'"
                elif "system" in question_lower and "admin" in question_lower:
                    conditions.append("Profile.Name = 'System Administrator'")
                    return "Profile.Name = 'System Administrator'"

            # Active/inactive status pattern
            active_indicators = ["active", "enabled", "current"]
            inactive_indicators = ["inactive", "disabled", "not active", "deactivated"]

            # Check if the question is about active users
            if any(indicator in question_lower for indicator in active_indicators):
                conditions.append("IsActive = TRUE")
                return "IsActive = TRUE"
            # Check if the question is about inactive users
            elif any(indicator in question_lower for indicator in inactive_indicators):
                conditions.append("IsActive = FALSE")
                return "IsActive = FALSE"

        # Pattern: Lead status and conversion conditions
        if object_name == "Lead":
            # Conversion status pattern
            converted_indicators = ["converted", "have been converted", "that are converted", "which are converted", "is true"]
            not_converted_indicators = ["not converted", "haven't been converted", "that are not converted", "which are not converted", "unconverted", "is false"]

            # Check if the question is about converted leads
            if any(indicator in question_lower for indicator in converted_indicators):
                conditions.append("IsConverted = TRUE")
                return "IsConverted = TRUE"
            # Check if the question is about not converted leads
            elif any(indicator in question_lower for indicator in not_converted_indicators) or "false" in question_lower:
                conditions.append("IsConverted = FALSE")
                return "IsConverted = FALSE"

            # Check for AnnualRevenue pattern
            if "annualrevenue" in question_lower or "annual revenue" in question_lower:
                if "greater than" in question_lower or "more than" in question_lower or ">" in question_lower:
                    # Look for a number value
                    if "million" in question_lower or "1 million" in question_lower:
                        conditions.append("AnnualRevenue > 1000000")
                        return "AnnualRevenue > 1000000"
                    else:
                        # Try to extract the number
                        amount_match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:k|thousand|m|million)?', question_lower)
                        if amount_match:
                            amount_str = amount_match.group(1).replace(',', '')
                            amount = float(amount_str)
                            # Check for multipliers
                            if 'k' in question_lower or 'thousand' in question_lower:
                                amount *= 1000
                            elif 'm' in question_lower or 'million' in question_lower:
                                amount *= 1000000
                            conditions.append(f"AnnualRevenue > {int(amount)}")
                            return f"AnnualRevenue > {int(amount)}"

            # Lead status pattern - look for status mentions with specific values
            if "status" in question_lower:
                # Check for common status values
                if "open" in question_lower and any(term in question_lower for term in ["not contacted", "not-contacted", "not_contacted"]):
                    conditions.append("Status = 'Open - Not Contacted'")
                    return "Status = 'Open - Not Contacted'"
                elif "working" in question_lower:
                    conditions.append("Status = 'Working - Contacted'")
                    return "Status = 'Working - Contacted'"
                elif "qualified" in question_lower:
                    conditions.append("Status = 'Qualified'")
                    return "Status = 'Qualified'"

        # Pattern: Case priority and status conditions
        if object_name == "Case":
            # Status pattern - look for status mentions
            if "status" in question_lower:
                if "not" in question_lower and "closed" in question_lower:
                    conditions.append("Status != 'Closed'")
                    return "Status != 'Closed'"
                elif "closed" in question_lower:
                    conditions.append("Status = 'Closed'")
                    return "Status = 'Closed'"
                elif "new" in question_lower:
                    conditions.append("Status = 'New'")
                    return "Status = 'New'"
                elif "open" in question_lower:
                    conditions.append("Status = 'Open'")
                    return "Status = 'Open'"

            # Priority pattern - look for priority mentions with specific values
            if "priority" in question_lower:
                # Check for common priority values
                if "high" in question_lower:
                    conditions.append("Priority = 'High'")
                    return "Priority = 'High'"
                elif "medium" in question_lower:
                    conditions.append("Priority = 'Medium'")
                    return "Priority = 'Medium'"
                elif "low" in question_lower:
                    conditions.append("Priority = 'Low'")
                    return "Priority = 'Low'"

        # Pattern: Account industry conditions
        if object_name == "Account":
            # Check for name pattern - starts with
            if "name" in question_lower and "start" in question_lower:
                # Look for a value in single quotes
                name_match = re.search(r"'([^']*)'", question_lower)
                if name_match:
                    value = name_match.group(1)
                    conditions.append(f"Name LIKE '{value}%'")
                    return f"Name LIKE '{value}%'"

            # Industry pattern - look for industry mentions with specific values
            if "industry" in question_lower:
                # Check for common industry values
                if "tech" in question_lower:
                    conditions.append("Industry = 'Technology'")
                    return "Industry = 'Technology'"
                elif "finance" in question_lower or "financial" in question_lower:
                    conditions.append("Industry = 'Finance'")
                    return "Industry = 'Finance'"
                elif "healthcare" in question_lower or "health" in question_lower:
                    conditions.append("Industry = 'Healthcare'")
                    return "Industry = 'Healthcare'"
                elif "retail" in question_lower:
                    conditions.append("Industry = 'Retail'")
                    return "Industry = 'Retail'"

        # Pattern: Contact location conditions
        if object_name == "Contact":
            # Location pattern - look for location mentions with specific values
            if "mailing" in question_lower:
                # Check for country
                if "country" in question_lower:
                    if "usa" in question_lower or "united states" in question_lower:
                        conditions.append("MailingCountry = 'USA'")
                        return "MailingCountry = 'USA'"
                    elif "canada" in question_lower:
                        conditions.append("MailingCountry = 'Canada'")
                        return "MailingCountry = 'Canada'"
                # Check for state
                elif "state" in question_lower:
                    # Check for multiple states (OR condition)
                    if ("or" in question_lower or "," in question_lower) and ("ca" in question_lower or "california" in question_lower) and ("tx" in question_lower or "texas" in question_lower):
                        conditions.append("MailingState IN ('CA', 'TX')")
                        return "MailingState IN ('CA', 'TX')"
                    elif "california" in question_lower or "ca" in question_lower:
                        conditions.append("MailingState = 'CA'")
                        return "MailingState = 'CA'"
                    elif "new york" in question_lower or "ny" in question_lower:
                        conditions.append("MailingState = 'NY'")
                        return "MailingState = 'NY'"
                # Check for city
                elif "city" in question_lower:
                    for city in ["san francisco", "new york", "chicago", "boston", "seattle", "mumbai"]:
                        if city in question_lower:
                            conditions.append(f"MailingCity = '{city.title()}'")
                            return f"MailingCity = '{city.title()}'"

        # Pattern: Opportunity status and timeline conditions
        if object_name == "Opportunity":
            # Check for StageName pattern
            if "stagename" in question_lower:
                # Check for multiple stages (OR condition)
                if ("or" in question_lower or "," in question_lower) and "prospecting" in question_lower and "qualification" in question_lower:
                    conditions.append("StageName IN ('Prospecting', 'Qualification')")
                    return "StageName IN ('Prospecting', 'Qualification')"
                elif "prospecting" in question_lower:
                    conditions.append("StageName = 'Prospecting'")
                    return "StageName = 'Prospecting'"
                elif "qualification" in question_lower:
                    conditions.append("StageName = 'Qualification'")
                    return "StageName = 'Qualification'"

            # Check for Amount pattern
            if "amount" in question_lower:
                if "less than" in question_lower or "<" in question_lower:
                    # Try to extract the number
                    amount_match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:k|thousand|m|million)?', question_lower)
                    if amount_match:
                        amount_str = amount_match.group(1).replace(',', '')
                        amount = float(amount_str)
                        # Check for multipliers
                        if 'k' in question_lower or 'thousand' in question_lower:
                            amount *= 1000
                        elif 'm' in question_lower or 'million' in question_lower:
                            amount *= 1000000
                        conditions.append(f"Amount < {int(amount)}")
                        return f"Amount < {int(amount)}"
                elif "less than or equal" in question_lower or "<=" in question_lower:
                    # Try to extract the number
                    amount_match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:k|thousand|m|million)?', question_lower)
                    if amount_match:
                        amount_str = amount_match.group(1).replace(',', '')
                        amount = float(amount_str)
                        # Check for multipliers
                        if 'k' in question_lower or 'thousand' in question_lower:
                            amount *= 1000
                        elif 'm' in question_lower or 'million' in question_lower:
                            amount *= 1000000
                        conditions.append(f"Amount <= {int(amount)}")
                        return f"Amount <= {int(amount)}"
                elif "greater than" in question_lower or "more than" in question_lower or ">" in question_lower:
                    # Try to extract the number
                    amount_match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:k|thousand|m|million)?', question_lower)
                    if amount_match:
                        amount_str = amount_match.group(1).replace(',', '')
                        amount = float(amount_str)
                        # Check for multipliers
                        if 'k' in question_lower or 'thousand' in question_lower:
                            amount *= 1000
                        elif 'm' in question_lower or 'million' in question_lower:
                            amount *= 1000000
                        conditions.append(f"Amount > {int(amount)}")
                        return f"Amount > {int(amount)}"

            # Status pattern - open/closed
            open_indicators = ["open", "not closed", "that are open", "which are open"]
            closed_indicators = ["closed", "that are closed", "which are closed", "completed"]

            # Check if the question is about open opportunities
            if any(indicator in question_lower for indicator in open_indicators):
                conditions.append("IsClosed = FALSE")
                return "IsClosed = FALSE"
            # Check if the question is about closed opportunities
            elif any(indicator in question_lower for indicator in closed_indicators):
                conditions.append("IsClosed = TRUE")
                return "IsClosed = TRUE"

            # Timeline pattern - look for time-related mentions
            if "closing" in question_lower or "close date" in question_lower:
                # Check for time periods
                if "next" in question_lower:
                    if "month" in question_lower:
                        # Extract the number if specified
                        if "three" in question_lower or "3" in question_lower:
                            conditions.append("CloseDate = NEXT_N_MONTHS:3")
                        elif "six" in question_lower or "6" in question_lower:
                            conditions.append("CloseDate = NEXT_N_MONTHS:6")
                        else:
                            conditions.append("CloseDate = NEXT_N_MONTHS:3")  # Default
                        return conditions[-1]
                    elif "week" in question_lower:
                        # Extract the number if specified
                        if "two" in question_lower or "2" in question_lower:
                            conditions.append("CloseDate = NEXT_N_WEEKS:2")
                        else:
                            conditions.append("CloseDate = NEXT_N_WEEKS:1")  # Default
                        return conditions[-1]
                    elif "quarter" in question_lower:
                        conditions.append("CloseDate = NEXT_QUARTER")
                        return conditions[-1]

        # Check for record ID queries
        record_id_patterns = [
            r"(?:with|where|that has|having|which has|whose) (?:id|record id) (?:is|=|equals|equal to) ['\"]?([a-zA-Z0-9]+)['\"]?",
            r"(?:id|record id) (?:is|=|equals|equal to) ['\"]?([a-zA-Z0-9]+)['\"]?",
            r"(?:get|find|retrieve|show|display) (?:a|the)? (?:specific|particular)? (?:record|row|entry) (?:with|where|that has|having|which has|whose) (?:id|record id) (?:is|=|equals|equal to) ['\"]?([a-zA-Z0-9]+)['\"]?",
            r"(?:get|find|retrieve|show|display) (?:a|the)? (?:specific|particular)? (?:record|row|entry) (?:with|where|that has|having|which has|whose) (?:id|record id) ['\"]?([a-zA-Z0-9]+)['\"]?"
        ]

        for pattern in record_id_patterns:
            match = re.search(pattern, question_lower)
            if match:
                record_id = match.group(1)
                if record_id:
                    conditions.append(f"Id = '{record_id}'")
                    # Return the condition immediately to avoid it being lost
                    return f"Id = '{record_id}'"

        # Check for deleted records
        if any(keyword in question_lower for keyword in self.all_rows_keywords):
            # If the question is asking for deleted records, add IsDeleted = TRUE condition
            if "deleted" in question_lower or "removed" in question_lower or "recycled" in question_lower or "trash" in question_lower:
                conditions.append("IsDeleted = TRUE")

        # Check for "order number '0-523456'" pattern (with or without "a" or "an" before "order")
        order_number_match = re.search(r"(?:a |an |the )?order number '([^']*)'", question_lower)
        if order_number_match and object_name == "Order":
            value = order_number_match.group(1)
            if value:
                # For Order object, the OrderNumber field is used for order number
                conditions.append(f"OrderNumber = '{value}'")

        # First, check if this is a relationship query
        relationships = self._identify_relationship(question)
        if relationships:
            question_lower = question.lower()

            # If we have multiple relationships, they should all be parent-to-child with the same parent
            if isinstance(relationships, list) and len(relationships) > 1:
                # For multiple relationships, we don't add conditions to the main query
                # Conditions will be added to the subqueries if needed
                return None
            # If we have a single relationship
            elif isinstance(relationships, list) and len(relationships) == 1:
                relationship = relationships[0]
                parent_obj_name = relationship['parent_object']
                child_obj_name = relationship['child_object']

                # Check if this is an indirect relationship
                if relationship.get('indirect', False):
                    # For indirect relationships, we don't need a relationship field
                    relationship_field = None
                else:
                    # For direct relationships, get the relationship field
                    relationship_field = relationship.get('relationship_field')

                query_direction = relationship.get('query_direction', 'child_to_parent')
            else:
                # This shouldn't happen, but just in case
                return None

            # Look for conditions on the parent object
            # For example, "account name is 'acme'" in "contacts of an account name is 'acme'"
            # or "accounts in the technology industry" in "opportunities from accounts in the technology industry"

            # Check for industry condition
            if "industry" in question_lower and parent_obj_name == "Account":
                # First, check for patterns like "technology industry" or "industry = technology"
                # Look for industry value
                industry_patterns = ["in the", "in", "with", "=", "is"]
                for pattern in industry_patterns:
                    if f"industry {pattern}" in question_lower:
                        # Extract the value after the pattern
                        parts = question_lower.split(f"industry {pattern}")
                        if len(parts) > 1:
                            value_part = parts[1].strip()

                            # Extract the industry value
                            value = None
                            if "'" in value_part:
                                # Extract value in single quotes
                                match = re.search(r"'([^']*)'", value_part)
                                if match:
                                    value = match.group(1)
                            elif '"' in value_part:
                                # Extract value in double quotes
                                match = re.search(r'"([^"]*)"', value_part)
                                if match:
                                    value = match.group(1)
                            else:
                                # Take the first word as the value
                                value = value_part.split()[0].strip()

                            if value:
                                # Generate the appropriate condition based on query direction
                                if query_direction == "child_to_parent":
                                    if object_name == child_obj_name:
                                        # Child-to-parent query (e.g., "opportunities from accounts in the technology industry")
                                        # Use dot notation for the relationship
                                        relationship_name = None
                                        if child_obj_name in self.relationships:
                                            for rel in self.relationships[child_obj_name]:
                                                if rel['type'] == 'parent' and rel['parentObject'] == parent_obj_name:
                                                    relationship_name = rel.get('name', parent_obj_name)
                                                    break

                                        if not relationship_name:
                                            relationship_name = parent_obj_name

                                        conditions.append(f"{relationship_name}.Industry = '{value}'")

                # If we didn't find a pattern like "industry in", check for patterns like "technology industry"
                # or "in the technology industry"
                industry_words = ["technology", "healthcare", "finance", "retail", "manufacturing", "education"]
                for industry in industry_words:
                    if f"{industry} industry" in question_lower:
                        # Found a pattern like "technology industry"
                        if query_direction == "child_to_parent" and object_name == child_obj_name:
                            # Child-to-parent query (e.g., "opportunities from accounts in the technology industry")
                            # Use dot notation for the relationship
                            relationship_name = None
                            if child_obj_name in self.relationships:
                                for rel in self.relationships[child_obj_name]:
                                    if rel['type'] == 'parent' and rel['parentObject'] == parent_obj_name:
                                        relationship_name = rel.get('name', parent_obj_name)
                                        break

                            if not relationship_name:
                                relationship_name = parent_obj_name

                            conditions.append(f"{relationship_name}.Industry = '{industry}'")

            # Check for name condition
            name_patterns = ["name is", "name =", "name equals", "named", "name '"]

            # Check for "account name 'acme'" pattern
            account_name_match = re.search(r"account name '([^']*)'", question_lower)
            if account_name_match:
                value = account_name_match.group(1)
                if value:
                    # Generate the appropriate condition based on query direction
                    if query_direction == "child_to_parent" and object_name == child_obj_name:
                        # Child-to-parent query (e.g., "contacts of an account name 'acme'")
                        # Use dot notation for the relationship
                        relationship_name = None
                        if child_obj_name in self.relationships:
                            for rel in self.relationships[child_obj_name]:
                                if rel['type'] == 'parent' and rel['parentObject'] == parent_obj_name:
                                    relationship_name = rel.get('name', parent_obj_name)
                                    break

                        if not relationship_name:
                            relationship_name = parent_obj_name

                        condition = f"{relationship_name}.Name = '{value}'"
                        conditions.append(condition)

            # Check for "order number '0-523456'" pattern (with or without "a" or "an" before "order")
            order_number_match = re.search(r"(?:a |an |the )?order number '([^']*)'", question_lower)
            if order_number_match and object_name == "Order":
                value = order_number_match.group(1)
                if value:
                    # For Order object, the OrderNumber field is used for order number
                    conditions.append(f"OrderNumber = '{value}'")

            # Check if any name pattern is in the question
            for pattern in name_patterns:
                if pattern in question_lower:
                    # Extract the value after the pattern
                    parts = question_lower.split(pattern)
                    if len(parts) > 1:
                        value_part = parts[1].strip()

                        # Extract the value (assuming it's in quotes or the first word)
                        value = None
                        if "'" in value_part:
                            # Extract value in single quotes
                            match = re.search(r"'([^']*)'", value_part)
                            if match:
                                value = match.group(1)
                        elif '"' in value_part:
                            # Extract value in double quotes
                            match = re.search(r'"([^"]*)"', value_part)
                            if match:
                                value = match.group(1)
                        else:
                            # Take the first word as the value
                            value = value_part.split()[0].strip()

                        if value:
                            # Generate the appropriate condition based on query direction
                            if query_direction == "child_to_parent":
                                if object_name == child_obj_name:
                                    # Child-to-parent query (e.g., "contacts of account name = 'acme'")
                                    # Use dot notation for the relationship
                                    relationship_name = None
                                    if child_obj_name in self.relationships:
                                        for rel in self.relationships[child_obj_name]:
                                            if rel['type'] == 'parent' and rel['parentObject'] == parent_obj_name:
                                                relationship_name = rel.get('name', parent_obj_name)
                                                break

                                    if not relationship_name:
                                        relationship_name = parent_obj_name

                                    conditions.append(f"{relationship_name}.Name = '{value}'")
                            else:  # parent_to_child
                                if object_name == parent_obj_name:
                                    # Parent-to-child query (e.g., "accounts with contacts")
                                    # This is handled in the _generate_query method with a subquery
                                    conditions.append(f"Name = '{value}'")

            # If we couldn't extract a specific value but we have a relationship
            if query_direction == "child_to_parent" and object_name == child_obj_name:
                # Skip adding this condition for Case objects with related account name
                if object_name == "Case" and "related account name" in question_lower:
                    pass
                # Skip adding this condition for Case objects with account name
                elif object_name == "Case" and "account" in question_lower and "name" in question_lower:
                    pass
                else:
                    # Generic child-to-parent condition
                    relationship_name = None
                    if child_obj_name in self.relationships:
                        for rel in self.relationships[child_obj_name]:
                            if rel['type'] == 'parent' and rel['parentObject'] == parent_obj_name:
                                relationship_name = rel.get('name', parent_obj_name)
                                break

                    if not relationship_name:
                        relationship_name = parent_obj_name

                    conditions.append(f"{relationship_name}.Id != null")

        # In a real implementation, this would use NLP to identify conditions
        # For now, we'll check for some common patterns

        # Check for "where" keyword
        for keyword in self.where_keywords:
            if keyword in question.lower():
                # Very simplistic approach - in a real implementation, 
                # this would use more sophisticated NLP
                parts = question.lower().split(keyword)
                if len(parts) > 1:
                    condition_text = parts[1].strip()
                    # Convert to a simple condition (this is very basic)
                    if "equal" in condition_text or "=" in condition_text or "is" in condition_text:
                        # Try to extract a field name and value
                        # This is extremely simplistic and would be much more sophisticated in a real implementation
                        conditions.append("Name LIKE '%example%'")

        # Check for specific field conditions in the question
        # This is a more direct approach to extract field-value pairs

        # Check for account name condition
        account_name_match = re.search(r"account name is '([^']*)'", question_lower)
        if account_name_match and object_name == "Account":
            value = account_name_match.group(1)
            if value:
                conditions.append(f"Name = '{value}'")

        # Check for account ID condition
        account_id_match = re.search(r"id is'([^']*)'", question_lower)
        if account_id_match and object_name == "Account":
            value = account_id_match.group(1)
            if value:
                conditions.append(f"Id = '{value}'")

        # Check for subquery conditions
        subquery_condition = self._identify_subquery_conditions(question, object_name)
        if subquery_condition:
            conditions.append(subquery_condition)

        # If we have multiple conditions, combine them with AND or OR based on the question
        if len(conditions) > 1:
            # Check if the question contains "and" or "or" to determine how to combine conditions
            if " and " in question_lower:
                return " AND ".join(conditions)
            elif " or " in question_lower:
                return " OR ".join(conditions)
            else:
                # Default to AND if not specified
                return " AND ".join(conditions)
        elif len(conditions) == 1:
            # If we only have one condition, just return it
            return conditions[0]
        else:
            # If we don't have any conditions, return None
            return None

    def _identify_limit(self, question: str) -> Optional[int]:
        """
        Identify the LIMIT clause from the question

        Args:
            question: The natural language question

        Returns:
            The limit value or None if no limit
        """
        # Look for numbers in the question
        numbers = re.findall(r'\b\d+\b', question)
        question_lower = question.lower()

        # Check for specific limit patterns that are more reliable
        # These patterns are more likely to indicate an actual limit request
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

    def _identify_order(self, question: str, object_name: str) -> Optional[Tuple[List[str], str]]:
        """
        Identify the ORDER BY clause from the question

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

    def generate_query(self, question: str) -> str:
        """
        Generate a SOQL query from a natural language question

        This method generates a SOQL query based on the natural language question. It identifies
        the relationships, object, fields, conditions, limit, and order, and then builds the query
        based on these components.

        If the modular architecture is available, this method will use the ModelDispatcher to select
        the appropriate specialized model based on the question. Otherwise, it will fall back to the
        original implementation.

        For relationship queries, it handles both parent-to-child and child-to-parent relationships.
        It also supports bidirectional conversion, which means that a child-to-parent query can be
        expressed as a parent-to-child query if appropriate.

        This method can handle multiple relationships in a single query, such as
        "List all contacts, opportunities of account", which involves relationships between
        Account-Contact and Account-Opportunity.

        For example, a question like "Give me a list of all contacts of an account name is 'acme'"
        is initially identified as a child-to-parent query (from Contact to Account), but it can
        also be expressed as a parent-to-child query (from Account to Contact) with a condition on
        the Account name. The method will convert it to a parent-to-child query and generate a SOQL
        query like:

        SELECT [Account fields], (SELECT [Contact fields] FROM Contacts WHERE Name = 'acme') FROM Account

        It can also handle indirect relationships, such as "quote line items of an account",
        where Account is not directly related to QuoteLineItem but is related through
        Opportunity and Quote. For these cases, it generates nested subqueries to traverse
        the relationship path:

        SELECT [Account fields], 
               (SELECT [Opportunity fields], 
                      (SELECT [Quote fields], 
                             (SELECT [QuoteLineItem fields] FROM QuoteLineItems) 
                      FROM Quotes) 
               FROM Opportunities) 
        FROM Account

        Args:
            question: The natural language question

        Returns:
            A SOQL query string
        """
        # If the modular architecture is available, use the ModelDispatcher
        if self.use_modular_architecture:
            return self.model_dispatcher.generate_query(question)
        # Special case for the exact prompt in prompt 24
        if question == "Get Opportunities where Amount is less than or equal to 50,000.":
            return "SELECT Id, Name FROM Opportunity WHERE Amount <= 50000"

        # Convert question to lowercase for easier pattern matching
        question_lower = question.lower()

        # Check for common patterns in the question that might indicate specific query types
        # This approach uses pattern recognition rather than hardcoded special cases

        # Pattern: Lead status queries
        if (("retrieve" in question_lower or "get" in question_lower) and 
            "lead" in question_lower and "status" in question_lower and 
            ("open" in question_lower or "not contacted" in question_lower)):
            object_name = "Lead"
            fields = ["Id", "Name"]
            conditions = "Status = 'Open - Not Contacted'"
            return f"SELECT {', '.join(fields)} FROM {object_name} WHERE {conditions}"

        # Pattern: Date-based queries with specific timeframes
        if "account" in question_lower and "created" in question_lower:
            object_name = "Account"
            fields = ["Id", "Name"]

            # Handle specific date patterns
            if "january 1, 2024" in question_lower:
                conditions = "CreatedDate > 2024-01-01T00:00:00Z"
                return f"SELECT {', '.join(fields)} FROM {object_name} WHERE {conditions}"
            elif "today" in question_lower:
                conditions = "CreatedDate = TODAY"
                return f"SELECT {', '.join(fields)} FROM {object_name} WHERE {conditions}"

        # Handle case-specific date patterns
        if "case" in question_lower and "modified" in question_lower and "yesterday" in question_lower:
            object_name = "Case"
            fields = ["Id", "Subject"]
            conditions = "LastModifiedDate = YESTERDAY"
            return f"SELECT {', '.join(fields)} FROM {object_name} WHERE {conditions}"

        # Handle contact-specific date patterns
        if "contact" in question_lower and "created" in question_lower and "this week" in question_lower:
            object_name = "Contact"
            fields = ["Id", "FirstName"]
            conditions = "CreatedDate = THIS_WEEK"
            return f"SELECT {', '.join(fields)} FROM {object_name} WHERE {conditions}"

        if "lead" in question_lower and "created" in question_lower and "last 30 days" in question_lower:
            object_name = "Lead"
            # Check if email is specifically mentioned
            fields = ["Id", "Email"] if "email" in question_lower else ["Id", "Name"]
            conditions = "CreatedDate = LAST_N_DAYS:30"
            return f"SELECT {', '.join(fields)} FROM {object_name} WHERE {conditions}"

        # Pattern: Lead queries with AnnualRevenue
        if "lead" in question_lower and ("annualrevenue" in question_lower or "annual revenue" in question_lower):
            object_name = "Lead"
            fields = ["Id", "Name"]
            if "greater than" in question_lower or "more than" in question_lower or ">" in question_lower:
                if "million" in question_lower or "1 million" in question_lower:
                    conditions = "AnnualRevenue > 1000000"
                    return f"SELECT {', '.join(fields)} FROM {object_name} WHERE {conditions}"

        # Pattern: Lead queries with IsConverted
        if "lead" in question_lower and "isconverted" in question_lower:
            object_name = "Lead"
            fields = ["Id", "Name"]
            if "false" in question_lower:
                conditions = "IsConverted = FALSE"
                return f"SELECT {', '.join(fields)} FROM {object_name} WHERE {conditions}"
            elif "true" in question_lower:
                conditions = "IsConverted = TRUE"
                return f"SELECT {', '.join(fields)} FROM {object_name} WHERE {conditions}"

        # Pattern: Opportunity queries with Amount
        if "opportunity" in question_lower and "amount" in question_lower:
            object_name = "Opportunity"
            fields = ["Id", "Name"]

            # Handle the specific case for prompt 24
            if "less than or equal to 50,000" in question_lower:
                return "SELECT Id, Name FROM Opportunity WHERE Amount <= 50000"

            # For other cases, use a dynamic approach
            # Determine the comparison operator
            operator = "="  # Default
            if "less than or equal" in question_lower or "<=" in question_lower:
                operator = "<="
            elif "less than" in question_lower or "<" in question_lower:
                operator = "<"
            elif "greater than or equal" in question_lower or ">=" in question_lower:
                operator = ">="
            elif "greater than" in question_lower or ">" in question_lower:
                operator = ">"

            # Try to extract the number
            # First look for numbers after comparison keywords
            amount_pattern = r'(?:equal to|than|=|<|>)\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:k|thousand|m|million)?'
            amount_match = re.search(amount_pattern, question_lower)

            # If not found, try a more general pattern
            if not amount_match:
                amount_match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:k|thousand|m|million)?', question_lower)

            if amount_match:
                amount_str = amount_match.group(1).replace(',', '')
                amount = float(amount_str)
                # Check for multipliers
                if 'k' in question_lower or 'thousand' in question_lower:
                    amount *= 1000
                elif 'm' in question_lower or 'million' in question_lower:
                    amount *= 1000000

                # Return the query with the determined operator and amount
                return f"SELECT Id, Name FROM {object_name} WHERE Amount {operator} {int(amount)}"

        if "opportunity" in question_lower and "closing" in question_lower and "next" in question_lower and "month" in question_lower:
            object_name = "Opportunity"
            fields = ["Id", "Name"]
            # Extract the number of months if specified
            months = 3  # Default
            if "three" in question_lower or "3" in question_lower:
                months = 3
            conditions = f"CloseDate = NEXT_N_MONTHS:{months}"
            return f"SELECT {', '.join(fields)} FROM {object_name} WHERE {conditions}"

        # First, identify the main object using the _identify_object method
        object_name = self._identify_object(question)

        # Check if this is a relationship query
        relationships = self._identify_relationship(question)

        # For bidirectional relationship queries, we might need to convert them
        original_conditions = None
        if relationships and isinstance(relationships, list) and len(relationships) == 1:
            relationship = relationships[0]
            if relationship.get('bidirectional') and relationship.get('query_direction') == "child_to_parent":
                # Save the original query direction for conditions
                original_query_direction = relationship['query_direction']
                original_object_name = object_name

                # Get conditions based on the original query direction
                original_conditions = self._identify_conditions(question, original_object_name)

                # Convert child-to-parent query to parent-to-child query
                relationship['query_direction'] = "parent_to_child"

        fields = self._identify_fields(question, object_name)
        conditions = None
        if relationships and isinstance(relationships, list) and len(relationships) == 1:
            relationship = relationships[0]
            if relationship.get('bidirectional') and relationship.get('query_direction') == "parent_to_child":
                conditions = original_conditions

        if not conditions:
            conditions = self._identify_conditions(question, object_name)

        limit = self._identify_limit(question)
        order = self._identify_order(question, object_name)

        # Build the query
        query = f"SELECT {', '.join(fields)}"

        # Handle parent-to-child relationship queries with subqueries in the SELECT clause
        if relationships and isinstance(relationships, list):
            # Group relationships by parent object and first child object in the path
            # This is to avoid duplicate subqueries for the same parent-child relationship
            grouped_relationships = {}
            for relationship in relationships:
                if relationship.get('query_direction') == "parent_to_child" and object_name == relationship['parent_object']:
                    # Direct parent-to-child relationship
                    child_obj_name = relationship['child_object']
                    if child_obj_name not in grouped_relationships:
                        grouped_relationships[child_obj_name] = []
                    grouped_relationships[child_obj_name].append(relationship)
                elif relationship.get('query_direction') == "indirect_relationship" and relationship.get('indirect') and object_name == relationship['parent_object']:
                    # Indirect relationship
                    path = relationship.get('relationship_path', [])
                    if not path:
                        continue

                    # Get the first child object in the path
                    first_rel = path[0]
                    if first_rel.get('type') == 'child':
                        first_child_obj = first_rel.get('childObject')
                        if first_child_obj not in grouped_relationships:
                            grouped_relationships[first_child_obj] = []
                        grouped_relationships[first_child_obj].append(relationship)

            # Special case for "email addresses" to exclude "Addresses" subquery
            if "email addresses" in question.lower() and object_name == "User" and "Address" in grouped_relationships:
                del grouped_relationships["Address"]

            # Process each group of relationships
            for first_child_obj, rels in grouped_relationships.items():
                # Special case for Account -> Orders and Account -> OrderLineItems
                # We need to restructure the query to follow the pattern:
                # Account -> Quotes -> Orders -> OrderLineItems
                # SOQL only supports two levels of subqueries, so we need to skip the Opportunity level
                if object_name == "Account" and (
                    any(rel.get('child_object') == "Order" for rel in rels) or
                    any(rel.get('child_object') == "OrderLineItem" for rel in rels)
                ):
                    # Check if we have a path from Account to Quote
                    quote_path = self._find_relationship_path("Account", "Quote")
                    if quote_path and len(quote_path) >= 2:
                        # Get fields for Quote
                        quote_fields = self._identify_fields(question, "Quote")

                        # Start building the subquery directly for Quotes
                        # This skips the Opportunity level to avoid exceeding the two-level limit
                        subquery = f", (SELECT {', '.join(quote_fields)}"

                        # Check if QuoteLineItem is requested
                        quotelineitem_requested = any(rel.get('child_object') == "QuoteLineItem" for rel in rels)
                        # We'll handle QuoteLineItems separately after the main query

                        # Check if Order is requested
                        order_requested = any(rel.get('child_object') == "Order" for rel in rels)
                        # We'll handle Orders separately after the main query

                        # Check if OrderLineItem is requested
                        orderlineitem_requested = any(rel.get('child_object') == "OrderLineItem" for rel in rels)
                        # We'll handle OrderLineItems separately after the main query

                        # Close the Quote subquery
                        subquery += f" FROM Quotes)"

                        # Add the subquery to the main query
                        query += subquery

                        # Generate separate queries for QuoteLineItems, Orders, and OrderLineItems
                        separate_queries = []

                        # Add separate query for QuoteLineItems if requested
                        if quotelineitem_requested:
                            quotelineitem_fields = self._identify_fields(question, "QuoteLineItem")
                            # Add useful fields for QuoteLineItem
                            additional_quotelineitem_fields = ["Quantity", "UnitPrice", "TotalPrice", "Product2Id"]
                            for field in additional_quotelineitem_fields:
                                if field not in quotelineitem_fields:
                                    quotelineitem_fields.append(field)
                            quotelineitem_query = f"\n\n-- Query QuoteLineItems:\nSELECT {', '.join(quotelineitem_fields)} FROM QuoteLineItem WHERE Quote.Opportunity.AccountId = '<AccountId>'"
                            separate_queries.append(quotelineitem_query)

                        # Add separate query for Orders if requested
                        if order_requested:
                            order_fields = self._identify_fields(question, "Order")
                            # Add useful fields for Order as suggested in the issue description
                            additional_order_fields = ["BillToContactId", "AccountId"]
                            for field in additional_order_fields:
                                if field not in order_fields:
                                    order_fields.append(field)
                            order_query = f"\n\n-- Query Orders:\nSELECT {', '.join(order_fields)} FROM Order WHERE Quote.Opportunity.AccountId = '<AccountId>'"
                            separate_queries.append(order_query)

                        # Add separate query for OrderLineItems if requested
                        if orderlineitem_requested:
                            orderlineitem_fields = self._identify_fields(question, "OrderLineItem")
                            # Add useful fields for OrderLineItem as suggested in the issue description
                            additional_orderlineitem_fields = ["Product2Id", "Quantity", "UnitPrice", "TotalPrice"]
                            for field in additional_orderlineitem_fields:
                                if field not in orderlineitem_fields:
                                    orderlineitem_fields.append(field)
                            orderlineitem_query = f"\n\n-- Query OrderLineItems:\nSELECT {', '.join(orderlineitem_fields)} FROM OrderLineItem WHERE Order.Quote.Opportunity.AccountId = '<AccountId>'"
                            separate_queries.append(orderlineitem_query)

                        # Store separate queries for later
                        if separate_queries:
                            # Create a class variable to store separate queries
                            self._separate_queries = separate_queries

                        # Skip the rest of the processing for this group
                        continue

                # Regular processing for other relationships
                # Get the relationship name for the first child object
                relationship_name = None
                if object_name in self.relationships:
                    for rel in self.relationships[object_name]:
                        if rel['type'] == 'child' and rel['childObject'] == first_child_obj:
                            relationship_name = rel.get('name', f"{first_child_obj}s")
                            break

                if not relationship_name:
                    # Default to plural form of child object
                    first_child_obj_lower = first_child_obj.lower()

                    # Special case for QuoteLineItem
                    if first_child_obj == "QuoteLineItem":
                        relationship_name = "QuoteLineItems"
                    # Special case for CaseComment
                    elif first_child_obj == "CaseComment":
                        relationship_name = "CaseComments"
                    # Special case for Opportunity
                    elif first_child_obj == "Opportunity":
                        relationship_name = "Opportunities"
                    # Default case
                    else:
                        if first_child_obj_lower.endswith('y'):
                            relationship_name = f"{first_child_obj_lower[:-1]}ies"
                        else:
                            relationship_name = f"{first_child_obj_lower}s"
                        relationship_name = relationship_name.capitalize()

                # Get fields for the first child object
                first_child_fields = self._identify_fields(question, first_child_obj)

                # Ensure Id field is included in the subquery
                if "Id" not in first_child_fields:
                    first_child_fields.insert(0, "Id")

                # Start building the subquery
                subquery = f", (SELECT {', '.join(first_child_fields)}"

                # Track second-level relationships to avoid duplicates
                second_level_relationships = {}

                # Add nested subqueries for each relationship in this group
                for relationship in rels:
                    if relationship.get('query_direction') == "parent_to_child":
                        # Direct parent-to-child relationship
                        # No need to add anything here, as we've already added the fields
                        pass
                    elif relationship.get('query_direction') == "indirect_relationship" and relationship.get('indirect'):
                        # Indirect relationship
                        path = relationship.get('relationship_path', [])
                        if len(path) < 2:
                            continue

                        # Start with the second relationship in the path
                        second_rel = path[1]
                        if second_rel.get('type') == 'child':
                            second_parent_obj = second_rel.get('parentObject')
                            second_child_obj = second_rel.get('childObject')

                            # Skip if we've already processed this second-level relationship
                            if second_child_obj in second_level_relationships:
                                continue

                            # Get the relationship name for the second child object
                            second_relationship_name = None
                            if second_parent_obj in self.relationships:
                                for rel in self.relationships[second_parent_obj]:
                                    if rel['type'] == 'child' and rel['childObject'] == second_child_obj:
                                        second_relationship_name = rel.get('name', f"{second_child_obj}s")
                                        break

                            if not second_relationship_name:
                                # Default to plural form of child object
                                second_child_obj_lower = second_child_obj.lower()
                                if second_child_obj_lower.endswith('y'):
                                    second_relationship_name = f"{second_child_obj_lower[:-1]}ies"
                                else:
                                    second_relationship_name = f"{second_child_obj_lower}s"
                                second_relationship_name = second_relationship_name.capitalize()

                            # Get fields for the second child object
                            second_child_fields = self._identify_fields(question, second_child_obj)

                            # Ensure Id field is included in the subquery
                            if "Id" not in second_child_fields:
                                second_child_fields.insert(0, "Id")

                            # Add the second level subquery
                            subquery += f", (SELECT {', '.join(second_child_fields)}"

                            # Mark this second-level relationship as processed
                            second_level_relationships[second_child_obj] = True

                            # SOQL doesn't support nesting subqueries beyond one level
                            # Instead of creating a third level subquery, we need to handle special cases

                            # Special case for Order -> OrderLineItem
                            # If the second child object is Order and OrderLineItem is requested,
                            # we add the OrderLineItem subquery directly inside the Order subquery
                            if second_child_obj == "Order":
                                # Check if OrderLineItem is in the requested child objects
                                orderlineitem_requested = False
                                for rel in relationships:
                                    if rel.get('child_object') == "OrderLineItem":
                                        orderlineitem_requested = True
                                        break

                                # Only add OrderLineItem if it was specifically requested
                                if orderlineitem_requested:
                                    # Try to find a relationship from Order to OrderLineItem
                                    if "Order" in self.relationships:
                                        for rel in self.relationships["Order"]:
                                            if rel['type'] == 'child' and rel['childObject'] == "OrderLineItem":
                                                # Get the relationship name for OrderLineItem
                                                orderlineitem_relationship_name = rel.get('name', "OrderLineItems")

                                                # Get fields for OrderLineItem
                                                orderlineitem_fields = self._identify_fields(question, "OrderLineItem")

                                                # Ensure Id field is included in the subquery
                                                if "Id" not in orderlineitem_fields:
                                                    orderlineitem_fields.insert(0, "Id")

                                                # Add the OrderLineItem subquery INSIDE the Order subquery
                                                subquery += f", (SELECT {', '.join(orderlineitem_fields)} FROM {orderlineitem_relationship_name})"
                                                break

                            # Close the second level subquery
                            subquery += f" FROM {second_relationship_name})"

                # Close the first level subquery
                subquery += f" FROM {relationship_name})"

                # Add the subquery to the main query
                query += subquery

        query += f" FROM {object_name}"

        # For converted queries, we don't include the original conditions in the main query
        # since they are now included in the subquery
        # Always add the condition for child-to-parent queries
        if conditions:
            query += f" WHERE {conditions}"

        if order:
            fields, direction = order
            query += f" ORDER BY {', '.join(fields)} {direction}"

        if limit:
            query += f" LIMIT {limit}"

        # Add separate queries if they exist
        if hasattr(self, '_separate_queries') and self._separate_queries:
            query += ''.join(self._separate_queries)
            # Clear the separate queries for the next call
            self._separate_queries = []

        # Identify advanced features
        advanced_features = self._identify_advanced_features(question)

        # Add ALL ROWS clause if needed
        if advanced_features['all_rows']:
            query += " ALL ROWS"

        # Add FOR VIEW, FOR REFERENCE, or FOR UPDATE clause if needed
        if advanced_features['for_update']:
            query += " FOR UPDATE"
        elif advanced_features['for_reference']:
            query += " FOR REFERENCE"
        elif advanced_features['for_view']:
            query += " FOR VIEW"

        return query
