"""
SQL Sorcerer Plugin for Willow v6

This plugin converts natural language queries to optimized SQL queries.
"""

import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def extract_entities(query: str) -> Dict[str, str]:
    """
    Extract entities from natural language query.
    
    Args:
        query: Natural language query
        
    Returns:
        Dictionary of extracted entities
    """
    entities = {
        'action': 'SELECT',
        'table': 'table',
        'columns': '*',
        'conditions': [],
        'order_by': None,
        'limit': None
    }
    
    query_lower = query.lower()
    
    # Extract action
    if 'select' in query_lower:
        entities['action'] = 'SELECT'
    elif 'insert' in query_lower:
        entities['action'] = 'INSERT'
    elif 'update' in query_lower:
        entities['action'] = 'UPDATE'
    elif 'delete' in query_lower:
        entities['action'] = 'DELETE'
    
    # Extract table name
    table_patterns = [
        r'from\s+(\w+)',
        r'table\s+(\w+)',
        r'into\s+(\w+)',
        r'update\s+(\w+)'
    ]
    
    for pattern in table_patterns:
        match = re.search(pattern, query_lower)
        if match:
            entities['table'] = match.group(1)
            break
    
    # Extract conditions
    if 'where' in query_lower:
        where_match = re.search(r'where\s+(.+)', query_lower)
        if where_match:
            conditions = where_match.group(1)
            # Simple condition parsing
            entities['conditions'] = [conditions.strip()]
    
    # Extract ordering
    if 'order by' in query_lower:
        order_match = re.search(r'order by\s+(\w+)', query_lower)
        if order_match:
            entities['order_by'] = order_match.group(1)
    
    # Extract limit
    if 'limit' in query_lower:
        limit_match = re.search(r'limit\s+(\d+)', query_lower)
        if limit_match:
            entities['limit'] = limit_match.group(1)
    
    return entities


def build_sql_query(entities: Dict[str, str]) -> str:
    """
    Build SQL query from extracted entities.
    
    Args:
        entities: Dictionary of query entities
        
    Returns:
        Generated SQL query
    """
    action = entities['action']
    table = entities['table']
    columns = entities['columns']
    conditions = entities['conditions']
    order_by = entities['order_by']
    limit = entities['limit']
    
    query_parts = []
    
    if action == 'SELECT':
        query_parts.append(f"SELECT {columns}")
        query_parts.append(f"FROM {table}")
        
        if conditions:
            query_parts.append(f"WHERE {' AND '.join(conditions)}")
        
        if order_by:
            query_parts.append(f"ORDER BY {order_by}")
        
        if limit:
            query_parts.append(f"LIMIT {limit}")
    
    elif action == 'INSERT':
        query_parts.append(f"INSERT INTO {table}")
        query_parts.append("(column1, column2) VALUES (value1, value2)")
    
    elif action == 'UPDATE':
        query_parts.append(f"UPDATE {table}")
        query_parts.append("SET column1 = value1")
        
        if conditions:
            query_parts.append(f"WHERE {' AND '.join(conditions)}")
    
    elif action == 'DELETE':
        query_parts.append(f"DELETE FROM {table}")
        
        if conditions:
            query_parts.append(f"WHERE {' AND '.join(conditions)}")
    
    return " ".join(query_parts) + ";"


def optimize_query(sql_query: str) -> str:
    """
    Apply basic SQL optimization suggestions.
    
    Args:
        sql_query: SQL query to optimize
        
    Returns:
        Optimized SQL query with suggestions
    """
    optimizations = []
    
    # Check for SELECT *
    if 'SELECT *' in sql_query.upper():
        optimizations.append("Consider specifying columns instead of using SELECT *")
    
    # Check for missing indexes hint
    if 'WHERE' in sql_query.upper():
        optimizations.append("Ensure proper indexes exist on WHERE clause columns")
    
    # Check for ORDER BY without LIMIT
    if 'ORDER BY' in sql_query.upper() and 'LIMIT' not in sql_query.upper():
        optimizations.append("Consider adding LIMIT for large result sets")
    
    return sql_query, optimizations


def run_sql_sorcerer(natural_language_query: str) -> str:
    """
    Convert natural language queries to optimized SQL queries.
    
    Args:
        natural_language_query: Natural language query
        
    Returns:
        Generated SQL query with optimization suggestions
    """
    logger.info("Running SQL Sorcerer on query.")
    
    if not natural_language_query.strip():
        return "No query provided for conversion."
    
    # Extract entities from natural language
    entities = extract_entities(natural_language_query)
    
    # Build SQL query
    sql_query = build_sql_query(entities)
    
    # Optimize query
    optimized_query, optimizations = optimize_query(sql_query)
    
    # Generate response
    response = "🔮 SQL Sorcerer Result:\n\n"
    response += f"Original Query: {natural_language_query}\n\n"
    response += f"Generated SQL:\n```sql\n{optimized_query}\n```\n"
    
    if optimizations:
        response += "\n💡 Optimization Suggestions:\n"
        for opt in optimizations:
            response += f"• {opt}\n"
    
    return response


# Entry point for plugin loader
def run(input_text: str) -> str:
    """
    Main entry point for the SQL Sorcerer plugin.
    
    Args:
        input_text: Natural language query to convert
        
    Returns:
        Generated SQL query
    """
    return run_sql_sorcerer(input_text) 