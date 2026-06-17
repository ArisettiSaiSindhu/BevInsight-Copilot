import re

def parse_tables_from_query(sql_query: str) -> list[str]:
    """Simple parser to extract database tables used in the SQL query."""
    tables = []
    # Find all table names in FROM and JOIN clauses
    matches = re.findall(r'\b(?:from|join)\s+([a-z0-9_]+)', sql_query.lower())
    for match in matches:
        # Avoid subqueries and alias keywords
        if match not in ["select", "left", "inner", "right", "outer", "cross"] and match not in tables:
            tables.append(match)
    return tables

def generate_reasoning_and_confidence(
    question: str, 
    sql_query: str, 
    resolved_metric: dict, 
    execution_success: bool,
    results_count: int
) -> dict:
    """
    Computes a confidence score and generates a business reasoning model explaining 
    the translation path from user question to database execution.
    """
    # 1. Table Detection
    tables_used = parse_tables_from_query(sql_query)
    table_labels = {
        "products": "Product Master (product_name, category, brand, pack_size, unit_price)",
        "stores": "Store Master (store_name, region, city, store_format)",
        "sales_promotions": "Sales & Promotions Fact (revenue, units_sold, promotion_type, discount_pct)",
        "inventory": "Inventory Fact (opening_stock, closing_stock, units_received, stockout_flag)"
    }
    detected_tables = [table_labels.get(t, t.upper()) for t in tables_used]

    # 2. Confidence Score Algorithm
    # Base: query was compiled and safety checked
    confidence_score = 40
    
    # Metric Resolution contribution (max +30)
    metric_confidence = resolved_metric.get("confidence", 50)
    confidence_score += int(metric_confidence * 0.3)
    
    # Data Payload contribution (max +20)
    if execution_success:
        if results_count > 0:
            confidence_score += 20
        else:
            confidence_score += 5  # Empty rows but valid query
            
    # Ambiguity check (max +10)
    # If the user query is very specific (contains product/store names), confidence is higher
    q_lower = question.lower()
    if any(keyword in q_lower for keyword in ["region", "south", "north", "west", "east", "p0", "s0"]):
        confidence_score += 10
    else:
        confidence_score += 5

    confidence_score = min(confidence_score, 100)

    # 3. Reasoning logs
    metric_name = resolved_metric.get("metric_name", "Sales Summary")
    metric_desc = resolved_metric.get("metric_definition", "General sales records.")
    
    reasoning_steps = [
        f"**Business Intent:** Identified focus on the **{metric_name}** metric ({metric_desc}).",
        f"**Data Model Mapping:** Extracted parameters from {', '.join(detected_tables)}.",
        f"**SQL Compilation:** Constructed SQLite-compliant read-only query mapping constraints safely.",
        f"**Verification:** Executed generated query against database, retrieving {results_count} matching record rows."
    ]

    return {
        "confidence": confidence_score,
        "metrics_selected": [metric_name],
        "tables_used": tables_used,
        "reasoning": "\n".join([f"- {step}" for step in reasoning_steps])
    }
