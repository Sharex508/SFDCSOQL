"""
Salesforce Metadata Loader
--------------------------
This module handles loading and managing Salesforce metadata (objects and fields)
which is used by the NLP model to generate accurate SOQL queries.
"""

import os
import json
import pandas as pd
from typing import Dict, List, Any, Optional

class SalesforceMetadataLoader:
    """
    A class for loading and managing Salesforce metadata (objects and fields)
    """

    def __init__(self, metadata_dir: str = "data/metadata"):
        """
        Initialize the metadata loader

        Args:
            metadata_dir: Directory where metadata files are stored
        """
        self.metadata_dir = metadata_dir
        self.objects = {}  # Dictionary of object name -> object metadata
        self.fields_by_object = {}  # Dictionary of object name -> list of fields
        self.relationships = {}  # Dictionary of object name -> list of relationships

        # Create metadata directory if it doesn't exist
        if not os.path.exists(metadata_dir):
            os.makedirs(metadata_dir, exist_ok=True)
            print(f"Created metadata directory at {metadata_dir}")

    def load_metadata(self):
        """
        Load all metadata from the metadata directory
        """
        if not os.path.exists(self.metadata_dir):
            print(f"Metadata directory {self.metadata_dir} does not exist")
            return

        # Load all JSON files in the metadata directory
        for filename in os.listdir(self.metadata_dir):
            if filename.endswith(".json"):
                object_name = filename[:-5]  # Remove .json extension
                self._load_object_metadata(object_name)

    def _load_object_metadata(self, object_name: str):
        """
        Load metadata for a specific object

        Args:
            object_name: Name of the Salesforce object
        """
        file_path = os.path.join(self.metadata_dir, f"{object_name}.json")
        if not os.path.exists(file_path):
            print(f"Metadata file for {object_name} does not exist")
            return

        try:
            with open(file_path, 'r') as f:
                metadata = json.load(f)

                # Store the object metadata
                self.objects[object_name] = metadata

                # Extract fields
                if 'fields' in metadata:
                    self.fields_by_object[object_name] = metadata['fields']
                else:
                    self.fields_by_object[object_name] = []

                # Extract relationships
                if 'relationships' in metadata:
                    self.relationships[object_name] = metadata['relationships']
                else:
                    self.relationships[object_name] = []

        except Exception as e:
            print(f"Error loading metadata for {object_name}: {str(e)}")

    def add_object(self, object_name: str, metadata: Dict[str, Any]):
        """
        Add or update a Salesforce object with its metadata

        Args:
            object_name: Name of the Salesforce object
            metadata: Object metadata including fields and relationships
        """
        # Store the object metadata
        self.objects[object_name] = metadata

        # Extract fields
        if 'fields' in metadata:
            self.fields_by_object[object_name] = metadata['fields']
        else:
            self.fields_by_object[object_name] = []

        # Extract relationships
        if 'relationships' in metadata:
            self.relationships[object_name] = metadata['relationships']
        else:
            self.relationships[object_name] = []

        # Save to file
        self._save_object_metadata(object_name)

    def _save_object_metadata(self, object_name: str):
        """
        Save metadata for a specific object to file

        Args:
            object_name: Name of the Salesforce object
        """
        if object_name not in self.objects:
            print(f"No metadata found for {object_name}")
            return

        file_path = os.path.join(self.metadata_dir, f"{object_name}.json")
        try:
            with open(file_path, 'w') as f:
                json.dump(self.objects[object_name], f, indent=2)
            print(f"Saved metadata for {object_name}")
        except Exception as e:
            print(f"Error saving metadata for {object_name}: {str(e)}")

    def get_object_names(self) -> List[str]:
        """
        Get a list of all object names

        Returns:
            List of object names
        """
        return list(self.objects.keys())

    def get_object_fields(self, object_name: str) -> List[Dict[str, Any]]:
        """
        Get fields for a specific object

        Args:
            object_name: Name of the Salesforce object

        Returns:
            List of field metadata dictionaries
        """
        return self.fields_by_object.get(object_name, [])

    def get_field_names(self, object_name: str) -> List[str]:
        """
        Get field names for a specific object

        Args:
            object_name: Name of the Salesforce object

        Returns:
            List of field names
        """
        fields = self.get_object_fields(object_name)
        return [field['name'] for field in fields if 'name' in field]

    def get_field_metadata(self, object_name: str, field_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific field

        Args:
            object_name: Name of the Salesforce object
            field_name: Name of the field

        Returns:
            Field metadata dictionary or None if not found
        """
        fields = self.get_object_fields(object_name)
        for field in fields:
            if field.get('name') == field_name:
                return field
        return None

    def get_object_relationships(self, object_name: str) -> List[Dict[str, Any]]:
        """
        Get relationships for a specific object

        Args:
            object_name: Name of the Salesforce object

        Returns:
            List of relationship metadata dictionaries
        """
        return self.relationships.get(object_name, [])

    def load_excel_metadata(self, excel_path: str = "Salesforce_Complete_Metadata.xlsx"):
        """
        Load metadata from Excel file

        Args:
            excel_path: Path to the Excel file containing Salesforce metadata
        """
        try:
            # Load the Excel file
            print(f"Loading metadata from {excel_path}...")
            df = pd.read_excel(excel_path)

            # Process the data
            # Group by CustomObject (table name)
            objects = df['CustomObject'].dropna().unique()

            for obj_name in objects:
                # Filter rows for this object
                obj_data = df[df['CustomObject'] == obj_name]

                # Create object metadata
                obj_metadata = {
                    "label": obj_name,
                    "fields": [],
                    "relationships": []
                }

                # Process fields
                for _, row in obj_data.iterrows():
                    # Skip rows without field information
                    if pd.isna(row.get('CustomField', '')):
                        continue

                    field_name = row['CustomField']
                    field_type = row.get('Field Type', 'string')

                    # Create field metadata
                    field_metadata = {
                        "name": field_name,
                        "type": field_type.lower() if not pd.isna(field_type) else "string",
                        "label": field_name
                    }

                    # Add lookup relationship if applicable
                    if 'Lookup Object' in row and not pd.isna(row.get('Lookup Object', '')):
                        lookup_obj = row['Lookup Object']
                        field_metadata["referenceTo"] = lookup_obj

                        # Add parent relationship
                        parent_relationship = {
                            "name": lookup_obj,
                            "type": "parent",
                            "parentObject": lookup_obj,
                            "field": field_name
                        }

                        if parent_relationship not in obj_metadata["relationships"]:
                            obj_metadata["relationships"].append(parent_relationship)

                        # Also create a corresponding child relationship on the parent object
                        # This will be added after all objects are processed

                    obj_metadata["fields"].append(field_metadata)

                # Add standard fields if not present
                standard_fields = [
                    {"name": "Id", "type": "id", "label": "ID"},
                    {"name": "Name", "type": "string", "label": "Name"}
                ]

                field_names = [f["name"] for f in obj_metadata["fields"]]
                for std_field in standard_fields:
                    if std_field["name"] not in field_names:
                        obj_metadata["fields"].append(std_field)

                # Add the object
                self.add_object(obj_name, obj_metadata)

            # Now create child relationships for all parent relationships
            print("Creating child relationships...")
            parent_relationships = {}

            # First, collect all parent relationships
            for obj_name, obj_data in self.objects.items():
                if obj_name in self.relationships:
                    for rel in self.relationships[obj_name]:
                        if rel['type'] == 'parent':
                            parent_obj = rel['parentObject']
                            if parent_obj not in parent_relationships:
                                parent_relationships[parent_obj] = []

                            # Create a child relationship
                            child_relationship = {
                                "name": f"{obj_name}s",  # Plural form of child object
                                "type": "child",
                                "childObject": obj_name,
                                "field": rel['field']
                            }

                            # Handle special plural forms
                            if obj_name.endswith('y'):
                                child_relationship["name"] = f"{obj_name[:-1]}ies"
                            elif obj_name.endswith('s'):
                                child_relationship["name"] = f"{obj_name}es"

                            parent_relationships[parent_obj].append(child_relationship)

            # Then, add the child relationships to the parent objects
            for parent_obj, child_rels in parent_relationships.items():
                if parent_obj in self.objects:
                    if parent_obj not in self.relationships:
                        self.relationships[parent_obj] = []

                    for child_rel in child_rels:
                        # Check if this relationship already exists
                        exists = False
                        for rel in self.relationships[parent_obj]:
                            if (rel['type'] == 'child' and 
                                rel['childObject'] == child_rel['childObject'] and
                                rel['field'] == child_rel['field']):
                                exists = True
                                break

                        if not exists:
                            self.relationships[parent_obj].append(child_rel)

                    # Update the object metadata
                    self.objects[parent_obj]['relationships'] = self.relationships[parent_obj]

                    # Save the updated metadata
                    self._save_object_metadata(parent_obj)

            print(f"Loaded metadata for {len(objects)} objects")
            return True
        except Exception as e:
            print(f"Error loading Excel metadata: {str(e)}")
            return False

    def add_sample_metadata(self, use_excel=True):
        """
        Add metadata from Excel file or use sample data if Excel file is not available

        Args:
            use_excel: Whether to try loading from Excel file first (default: True)
        """
        # Try to load from Excel file first if use_excel is True
        if use_excel:
            excel_path = "Salesforce_Complete_Metadata.xlsx"
            if os.path.exists(excel_path):
                success = self.load_excel_metadata(excel_path)
                if success:
                    return
            print("Excel file not found or loading failed. Using sample metadata...")
        else:
            print("Using sample metadata directly...")

        # Account object
        self.add_object("Account", {
            "label": "Account",
            "fields": [
                {"name": "Id", "type": "id", "label": "Account ID"},
                {"name": "Name", "type": "string", "label": "Account Name"},
                {"name": "Type", "type": "picklist", "label": "Account Type"},
                {"name": "Industry", "type": "picklist", "label": "Industry"},
                {"name": "AnnualRevenue", "type": "currency", "label": "Annual Revenue"},
                {"name": "Phone", "type": "phone", "label": "Phone"},
                {"name": "Website", "type": "url", "label": "Website"}
            ],
            "relationships": [
                {"name": "Contacts", "type": "child", "childObject": "Contact", "field": "AccountId"},
                {"name": "Opportunities", "type": "child", "childObject": "Opportunity", "field": "AccountId"}
            ]
        })

        # Contact object
        self.add_object("Contact", {
            "label": "Contact",
            "fields": [
                {"name": "Id", "type": "id", "label": "Contact ID"},
                {"name": "FirstName", "type": "string", "label": "First Name"},
                {"name": "LastName", "type": "string", "label": "Last Name"},
                {"name": "Email", "type": "email", "label": "Email"},
                {"name": "Phone", "type": "phone", "label": "Phone"},
                {"name": "Title", "type": "string", "label": "Title"},
                {"name": "AccountId", "type": "reference", "label": "Account ID"}
            ],
            "relationships": [
                {"name": "Account", "type": "parent", "parentObject": "Account", "field": "AccountId"}
            ]
        })

        # Opportunity object
        self.add_object("Opportunity", {
            "label": "Opportunity",
            "fields": [
                {"name": "Id", "type": "id", "label": "Opportunity ID"},
                {"name": "Name", "type": "string", "label": "Opportunity Name"},
                {"name": "StageName", "type": "picklist", "label": "Stage"},
                {"name": "CloseDate", "type": "date", "label": "Close Date"},
                {"name": "Amount", "type": "currency", "label": "Amount"},
                {"name": "AccountId", "type": "reference", "label": "Account ID"}
            ],
            "relationships": [
                {"name": "Account", "type": "parent", "parentObject": "Account", "field": "AccountId"},
                {"name": "Quotes", "type": "child", "childObject": "Quote", "field": "OpportunityId"}
            ]
        })

        # Quote object
        self.add_object("Quote", {
            "label": "Quote",
            "fields": [
                {"name": "Id", "type": "id", "label": "Quote ID"},
                {"name": "Name", "type": "string", "label": "Quote Name"},
                {"name": "Status", "type": "picklist", "label": "Status"},
                {"name": "ExpirationDate", "type": "date", "label": "Expiration Date"},
                {"name": "GrandTotal", "type": "currency", "label": "Grand Total"},
                {"name": "OpportunityId", "type": "reference", "label": "Opportunity ID"}
            ],
            "relationships": [
                {"name": "Opportunity", "type": "parent", "parentObject": "Opportunity", "field": "OpportunityId"},
                {"name": "QuoteLineItems", "type": "child", "childObject": "QuoteLineItem", "field": "QuoteId"},
                {"name": "Orders", "type": "child", "childObject": "Order", "field": "QuoteId"}
            ]
        })

        # QuoteLineItem object
        self.add_object("QuoteLineItem", {
            "label": "Quote Line Item",
            "fields": [
                {"name": "Id", "type": "id", "label": "Quote Line Item ID"},
                {"name": "Name", "type": "string", "label": "Quote Line Item Name"},
                {"name": "Quantity", "type": "number", "label": "Quantity"},
                {"name": "UnitPrice", "type": "currency", "label": "Unit Price"},
                {"name": "TotalPrice", "type": "currency", "label": "Total Price"},
                {"name": "QuoteId", "type": "reference", "label": "Quote ID"}
            ],
            "relationships": [
                {"name": "Quote", "type": "parent", "parentObject": "Quote", "field": "QuoteId"}
            ]
        })

        # Order object
        self.add_object("Order", {
            "label": "Order",
            "fields": [
                {"name": "Id", "type": "id", "label": "Order ID"},
                {"name": "Name", "type": "string", "label": "Order Name"},
                {"name": "Status", "type": "picklist", "label": "Status"},
                {"name": "EffectiveDate", "type": "date", "label": "Effective Date"},
                {"name": "TotalAmount", "type": "currency", "label": "Total Amount"},
                {"name": "QuoteId", "type": "reference", "label": "Quote ID"}
            ],
            "relationships": [
                {"name": "Quote", "type": "parent", "parentObject": "Quote", "field": "QuoteId"},
                {"name": "OrderLineItems", "type": "child", "childObject": "OrderLineItem", "field": "OrderId"}
            ]
        })

        # OrderLineItem object
        self.add_object("OrderLineItem", {
            "label": "Order Line Item",
            "fields": [
                {"name": "Id", "type": "id", "label": "Order Line Item ID"},
                {"name": "Name", "type": "string", "label": "Order Line Item Name"},
                {"name": "Quantity", "type": "number", "label": "Quantity"},
                {"name": "UnitPrice", "type": "currency", "label": "Unit Price"},
                {"name": "TotalPrice", "type": "currency", "label": "Total Price"},
                {"name": "OrderId", "type": "reference", "label": "Order ID"}
            ],
            "relationships": [
                {"name": "Order", "type": "parent", "parentObject": "Order", "field": "OrderId"}
            ]
        })
