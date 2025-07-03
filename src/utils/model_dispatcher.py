"""
Model Dispatcher for SOQL Query Generation
------------------------------------------
This module contains the ModelDispatcher class that selects the appropriate
specialized model based on the user's prompt.
"""

from typing import Dict, List, Optional, Any
import re

# Import all specialized models
try:
    from src.models.basic_query_model import BasicQueryModel
    from src.models.where_clause_model import WhereClauseModel
    from src.models.date_filter_model import DateFilterModel
    from src.models.relationship_model import RelationshipModel
    from src.models.aggregation_model import AggregationModel
    from src.models.sorting_model import SortingModel
    from src.models.advanced_features_model import AdvancedFeaturesModel
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False

class ModelDispatcher:
    """
    A class that selects the appropriate specialized model based on the user's prompt.

    This class acts as a dispatcher that routes the query generation request to the
    most suitable specialized model. If no specialized model can handle the prompt,
    it falls back to the basic query model.
    """

    def __init__(self, metadata_path: str = "data/metadata", soql_docs_path: str = "data/soql_docs"):
        """
        Initialize the model dispatcher.

        Args:
            metadata_path: Path to the metadata directory
            soql_docs_path: Path to the SOQL documentation directory
        """
        self.metadata_path = metadata_path
        self.soql_docs_path = soql_docs_path
        self.objects = {}
        self.fields_by_object = {}
        self.relationships = {}

        # Initialize all specialized models if available
        self.models = []
        if MODELS_AVAILABLE:
            # Order matters: more specific models should come first
            self.models = [
                AdvancedFeaturesModel(metadata_path, soql_docs_path),
                RelationshipModel(metadata_path, soql_docs_path),  # Move RelationshipModel up for better handling of relationships
                WhereClauseModel(metadata_path, soql_docs_path),
                AggregationModel(metadata_path, soql_docs_path),
                DateFilterModel(metadata_path, soql_docs_path),
                SortingModel(metadata_path, soql_docs_path),
                BasicQueryModel(metadata_path, soql_docs_path)  # Fallback model
            ]

    def set_metadata(self, objects: Dict[str, Any], fields_by_object: Dict[str, List[Dict[str, Any]]], relationships: Dict[str, List[Dict[str, Any]]]):
        """
        Set the metadata for all models.

        Args:
            objects: Dictionary of Salesforce objects
            fields_by_object: Dictionary of fields by object
            relationships: Dictionary of relationships by object
        """
        self.objects = objects
        self.fields_by_object = fields_by_object
        self.relationships = relationships

        # Set metadata for all models
        for model in self.models:
            model.objects = objects
            model.fields_by_object = fields_by_object
            model.relationships = relationships

    def generate_query(self, question: str) -> str:
        """
        Generate a SOQL query from a natural language question.

        This method selects the appropriate specialized model based on the question
        and delegates the query generation to that model. It can also combine results
        from multiple models if needed.

        Args:
            question: The natural language question

        Returns:
            A SOQL query string
        """
        # If no models are available, return an error message
        if not self.models:
            return "Error: No specialized models available. Please check your installation."

        # Check for specific patterns that should be handled by specific models
        question_lower = question.lower()

        # Identify all models that can handle this question
        applicable_models = []
        for model in self.models:
            if model.can_handle(question):
                applicable_models.append(model)

        # If no models can handle the question, use the last model (BasicQueryModel)
        if not applicable_models:
            return self.models[-1].generate_query(question)

        # If only one model can handle the question, use that model
        if len(applicable_models) == 1:
            return applicable_models[0].generate_query(question)

        # If multiple models can handle the question, we need to determine which ones to use
        # and how to combine their results

        # First, check for specific combinations of models that we know how to handle

        # Combination: WhereClauseModel + AggregationModel
        where_model = next((m for m in applicable_models if isinstance(m, WhereClauseModel)), None)
        agg_model = next((m for m in applicable_models if isinstance(m, AggregationModel)), None)

        if where_model and agg_model and ("count" in question_lower or "sum" in question_lower or 
                                          "average" in question_lower or "avg" in question_lower or 
                                          "min" in question_lower or "max" in question_lower):
            # Get the object and conditions from the WhereClauseModel
            where_query = where_model.generate_query(question)

            # Extract the object and conditions
            object_match = re.search(r"FROM\s+(\w+)", where_query)
            conditions_match = re.search(r"WHERE\s+(.+?)(?:\s+ORDER BY|\s+LIMIT|$)", where_query)

            if object_match:
                object_name = object_match.group(1)

                # Get the aggregation fields from the AggregationModel
                agg_query = agg_model.generate_query(question)
                agg_fields_match = re.search(r"SELECT\s+(.+?)\s+FROM", agg_query)

                if agg_fields_match:
                    agg_fields = agg_fields_match.group(1)

                    # Build the combined query
                    query = f"SELECT {agg_fields} FROM {object_name}"

                    # Add WHERE clause if conditions were found
                    if conditions_match:
                        conditions = conditions_match.group(1)
                        query += f" WHERE {conditions}"

                    # Check for GROUP BY in the aggregation query
                    group_by_match = re.search(r"GROUP BY\s+(.+?)(?:\s+HAVING|\s+ORDER BY|\s+LIMIT|$)", agg_query)
                    if group_by_match:
                        group_by = group_by_match.group(1)
                        query += f" GROUP BY {group_by}"

                    # Check for HAVING in the aggregation query
                    having_match = re.search(r"HAVING\s+(.+?)(?:\s+ORDER BY|\s+LIMIT|$)", agg_query)
                    if having_match:
                        having = having_match.group(1)
                        query += f" HAVING {having}"

                    # Check for ORDER BY in either query
                    order_by_match = re.search(r"ORDER BY\s+(.+?)(?:\s+LIMIT|$)", where_query)
                    if not order_by_match:
                        order_by_match = re.search(r"ORDER BY\s+(.+?)(?:\s+LIMIT|$)", agg_query)

                    if order_by_match:
                        order_by = order_by_match.group(1)
                        query += f" ORDER BY {order_by}"

                    # Check for LIMIT in either query
                    limit_match = re.search(r"LIMIT\s+(\d+)", where_query)
                    if not limit_match:
                        limit_match = re.search(r"LIMIT\s+(\d+)", agg_query)

                    if limit_match:
                        limit = limit_match.group(1)
                        query += f" LIMIT {limit}"

                    return query

        # Combination: WhereClauseModel + DateFilterModel
        date_model = next((m for m in applicable_models if isinstance(m, DateFilterModel)), None)

        if where_model and date_model:
            # Get the object and fields from the WhereClauseModel
            where_query = where_model.generate_query(question)

            # Extract the object and fields
            object_match = re.search(r"SELECT\s+(.+?)\s+FROM\s+(\w+)", where_query)
            conditions_match = re.search(r"WHERE\s+(.+?)(?:\s+ORDER BY|\s+LIMIT|$)", where_query)

            if object_match:
                fields = object_match.group(1)
                object_name = object_match.group(2)

                # Get the date field and filter from the DateFilterModel
                date_field, date_filter = date_model._identify_date_filter(question, object_name)

                # Build the combined query
                query = f"SELECT {fields} FROM {object_name}"

                # Combine WHERE conditions if both models have them
                if conditions_match and date_field and date_filter:
                    conditions = conditions_match.group(1)
                    query += f" WHERE {conditions} AND {date_field} {date_filter}"
                elif date_field and date_filter:
                    query += f" WHERE {date_field} {date_filter}"
                elif conditions_match:
                    conditions = conditions_match.group(1)
                    query += f" WHERE {conditions}"

                # Check for ORDER BY in the where query
                order_by_match = re.search(r"ORDER BY\s+(.+?)(?:\s+LIMIT|$)", where_query)
                if order_by_match:
                    order_by = order_by_match.group(1)
                    query += f" ORDER BY {order_by}"

                # Check for LIMIT in the where query
                limit_match = re.search(r"LIMIT\s+(\d+)", where_query)
                if limit_match:
                    limit = limit_match.group(1)
                    query += f" LIMIT {limit}"

                return query

        # Combination: WhereClauseModel + RelationshipModel
        rel_model = next((m for m in applicable_models if isinstance(m, RelationshipModel)), None)

        if where_model and rel_model:
            # For relationship queries, the RelationshipModel is usually more appropriate
            # as it can handle the complex relationship structure
            rel_query = rel_model.generate_query(question)

            # Extract the object and conditions from the WhereClauseModel
            where_query = where_model.generate_query(question)
            conditions_match = re.search(r"WHERE\s+(.+?)(?:\s+ORDER BY|\s+LIMIT|$)", where_query)

            # If the relationship query doesn't have a WHERE clause but the where query does,
            # add the conditions to the relationship query
            if conditions_match and "WHERE" not in rel_query:
                conditions = conditions_match.group(1)
                # Insert the WHERE clause before any ORDER BY, LIMIT, etc.
                if "ORDER BY" in rel_query:
                    rel_query = rel_query.replace("ORDER BY", f"WHERE {conditions} ORDER BY")
                elif "LIMIT" in rel_query:
                    rel_query = rel_query.replace("LIMIT", f"WHERE {conditions} LIMIT")
                else:
                    rel_query += f" WHERE {conditions}"

            return rel_query

        # If we don't have a specific combination handler, use the model with the highest priority
        # The models are ordered by priority in the constructor, so the first applicable model
        # in the list has the highest priority
        return applicable_models[0].generate_query(question)
