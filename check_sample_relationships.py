"""
Script to check the relationships in the sample metadata
"""

def main():
    print("Checking sample relationships")
    print("--------------------------")

    # Define the sample metadata directly
    relationships = {
        "Account": [
            {"name": "Contacts", "type": "child", "childObject": "Contact", "field": "AccountId"},
            {"name": "Opportunities", "type": "child", "childObject": "Opportunity", "field": "AccountId"}
        ],
        "Contact": [
            {"name": "Account", "type": "parent", "parentObject": "Account", "field": "AccountId"}
        ],
        "Opportunity": [
            {"name": "Account", "type": "parent", "parentObject": "Account", "field": "AccountId"},
            {"name": "Quotes", "type": "child", "childObject": "Quote", "field": "OpportunityId"}
        ],
        "Quote": [
            {"name": "Opportunity", "type": "parent", "parentObject": "Opportunity", "field": "OpportunityId"},
            {"name": "QuoteLineItems", "type": "child", "childObject": "QuoteLineItem", "field": "QuoteId"},
            {"name": "Orders", "type": "child", "childObject": "Order", "field": "QuoteId"}
        ],
        "QuoteLineItem": [
            {"name": "Quote", "type": "parent", "parentObject": "Quote", "field": "QuoteId"}
        ],
        "Order": [
            {"name": "Quote", "type": "parent", "parentObject": "Quote", "field": "QuoteId"}
        ]
    }

    # Check relationships for each object
    for obj_name, rels in relationships.items():
        print(f"\nRelationships for {obj_name}:")
        for rel in rels:
            print(f"  - Type: {rel.get('type')}")
            if rel.get('type') == 'child':
                print(f"    Child Object: {rel.get('childObject')}")
                print(f"    Field: {rel.get('field')}")
            elif rel.get('type') == 'parent':
                print(f"    Parent Object: {rel.get('parentObject')}")
                print(f"    Field: {rel.get('field')}")

    # Find path from Account to QuoteLineItem
    print("\nFinding path from Account to QuoteLineItem:")
    path = find_path(relationships, "Account", "QuoteLineItem")
    if path:
        print(f"Found path with {len(path)} steps:")
        for i, rel in enumerate(path):
            rel_type = rel.get('type')
            if rel_type == 'child':
                parent_obj = rel.get('parentObject', rel.get('name', 'Unknown').replace('s', ''))
                child_obj = rel.get('childObject')
                print(f"  {i+1}. {parent_obj} -> {child_obj}")
            elif rel_type == 'parent':
                child_obj = rel.get('childObject', 'Unknown')
                parent_obj = rel.get('parentObject')
                print(f"  {i+1}. {child_obj} -> {parent_obj}")
    else:
        print("No path found")

    # Find path from Account to Order
    print("\nFinding path from Account to Order:")
    path = find_path(relationships, "Account", "Order")
    if path:
        print(f"Found path with {len(path)} steps:")
        for i, rel in enumerate(path):
            rel_type = rel.get('type')
            if rel_type == 'child':
                parent_obj = rel.get('parentObject', rel.get('name', 'Unknown').replace('s', ''))
                child_obj = rel.get('childObject')
                print(f"  {i+1}. {parent_obj} -> {child_obj}")
            elif rel_type == 'parent':
                child_obj = rel.get('childObject', 'Unknown')
                parent_obj = rel.get('parentObject')
                print(f"  {i+1}. {child_obj} -> {parent_obj}")
    else:
        print("No path found")

def find_path(relationships, start_obj, end_obj, max_depth=3):
    """
    Find a path between two objects using breadth-first search
    """
    if start_obj not in relationships or end_obj not in relationships:
        return None

    # If the objects are the same, return an empty path
    if start_obj == end_obj:
        return []

    # Check if there's a direct relationship
    for rel in relationships.get(start_obj, []):
        if (rel['type'] == 'child' and rel['childObject'] == end_obj) or \
           (rel['type'] == 'parent' and rel['parentObject'] == end_obj):
            return [rel]

    # Use breadth-first search to find the shortest path
    queue = [(start_obj, [])]  # (current_obj, path_so_far)
    visited = {start_obj}

    while queue:
        current_obj, path = queue.pop(0)

        # Don't go beyond max_depth
        if len(path) >= max_depth:
            continue

        # Get all relationships for the current object
        for rel in relationships.get(current_obj, []):
            next_obj = None
            if rel['type'] == 'parent':
                next_obj = rel['parentObject']
            elif rel['type'] == 'child':
                next_obj = rel['childObject']

            if next_obj and next_obj not in visited:
                # Create a new path with this relationship
                new_path = path + [rel]

                # Check if we've reached the end object
                if next_obj == end_obj:
                    return new_path

                # Add to queue for further exploration
                queue.append((next_obj, new_path))
                visited.add(next_obj)

    # No path found
    return None

if __name__ == "__main__":
    main()