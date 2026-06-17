import re

# Set of forbidden SQL commands in lowercase
FORBIDDEN_KEYWORDS = {
    "drop", "delete", "update", "insert", "alter", 
    "truncate", "attach", "pragma", "create", "replace",
    "grant", "revoke", "exec", "execute"
}

def validate_sql_query(sql_query: str) -> tuple[bool, str]:
    """
    Validates a SQL query for safety against injection and destructive operations.
    Returns: (is_safe: bool, error_message: str)
    """
    # 1. Clean query
    query_clean = sql_query.strip().lower()
    if not query_clean:
        return False, "SQL Query is empty."

    # 2. Check: Must start with SELECT (or WITH for common table expressions)
    if not (query_clean.startswith("select") or query_clean.startswith("with")):
        return False, "Query violation: Only read-only SELECT queries are allowed."

    # 3. Prevent stacked query execution (multiple semicolons ending in a command)
    # Semicolon followed by characters that represent a new command is disallowed
    semicolon_split = query_clean.split(";")
    active_statements = [s.strip() for s in semicolon_split if s.strip()]
    if len(active_statements) > 1:
        # Check if the subsequent statements contain any commands
        return False, "Query violation: Stacked queries (multiple statements) are blocked."

    # 4. Tokenize and check for blocked keywords
    # Match words, ignoring within string literals if possible (but keeping it simple/safe)
    # We find all alphanumeric strings
    tokens = set(re.findall(r'[a-z]+', query_clean))
    
    intersect = tokens.intersection(FORBIDDEN_KEYWORDS)
    if intersect:
        return False, f"Query violation: Destructive operation '{list(intersect)[0].upper()}' is blocked."

    return True, ""

def sanitize_and_validate(sql_query: str) -> tuple[bool, str, str]:
    """
    Cleans the SQL query, validates it, and returns (is_safe, sanitized_query, error_message).
    """
    # Remove markdown formatting block if present
    sql = re.sub(r"```sql", "", sql_query, flags=re.IGNORECASE)
    sql = re.sub(r"```", "", sql)
    sql = sql.strip()
    
    # Ensure ends with semicolon
    if sql and not sql.endswith(";"):
        sql += ";"
        
    is_safe, err = validate_sql_query(sql)
    return is_safe, sql, err
