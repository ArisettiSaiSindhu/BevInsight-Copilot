import re
import logging

logger = logging.getLogger(__name__)

# Dictionary of standard retail FMCG metrics
METRIC_DICTIONARY = {
    "revenue": {
        "name": "Revenue",
        "description": "Total sales revenue generated after promotional discount deductions.",
        "sql_expression": "SUM(revenue)",
        "unit": "USD",
        "synonyms": ["sales", "income", "turnover", "earnings", "revenue", "perform", "value"]
    },
    "volume": {
        "name": "Volume (Units Sold)",
        "description": "Total count of beverage units sold.",
        "sql_expression": "SUM(units_sold)",
        "unit": "Units",
        "synonyms": ["units", "volume", "sold", "quantity", "count", "bottles", "cans"]
    },
    "promo_uplift": {
        "name": "Promotion Revenue Uplift",
        "description": "Incremental revenue generated during active promotional weeks compared to baseline non-promo weeks.",
        "sql_expression": "SUM(revenue) FILTER (WHERE promotion_flag = 1)",
        "unit": "Percent",
        "synonyms": ["promotion", "discount", "promo", "uplift", "campaign", "bogo", "successful"]
    },
    "growth_rate": {
        "name": "Week-over-Week Growth Rate",
        "description": "Percentage change in sales revenue or volume compared to the previous week.",
        "sql_expression": "WoW Growth Calculation",
        "unit": "Percent",
        "synonyms": ["growth", "increase", "growing", "decline", "trend", "change"]
    },
    "inventory_risk": {
        "name": "Stockout Risk",
        "description": "Probability that a product will run out of stock, flagged by week-end closing stock reaching 0.",
        "sql_expression": "SUM(stockout_flag)",
        "unit": "Incidents",
        "synonyms": ["stockout", "out of stock", "shortage", "risk", "empty", "depletion"]
    },
    "excess_inventory": {
        "name": "Excess Inventory Ratio",
        "description": "Remaining shelf inventory exceeding average weekly sales requirements (closing stock > 3x average weekly sales).",
        "sql_expression": "closing_stock / average_weekly_sales",
        "unit": "Ratio",
        "synonyms": ["excess", "overstock", "surplus", "wasted", "slow moving", "dusty"]
    }
}

def resolve_business_metric(question: str) -> dict:
    """
    Parses a user question to resolve which retail metrics are being queried.
    Returns details on resolved metric and mapping confidence.
    """
    q = question.lower()
    best_metric = None
    max_matches = 0
    confidence = 50  # Base confidence
    
    # Check for direct synonyms in dictionary
    for key, metric in METRIC_DICTIONARY.items():
        matches = 0
        for synonym in metric["synonyms"]:
            # Use regex for word boundaries to avoid partial matching (e.g., 'in' matching 'income')
            if re.search(r'\b' + re.escape(synonym) + r'\b', q):
                matches += 1
                
        if matches > max_matches:
            max_matches = matches
            best_metric = key

    # Intent-based rule upgrades
    if not best_metric:
        # Defaults based on general keywords
        if "money" in q or "rich" in q or "dollars" in q:
            best_metric = "revenue"
        elif "much" in q or "many" in q:
            best_metric = "volume"
        elif "risk" in q or "danger" in q or "ran out" in q or "depleted" in q:
            best_metric = "inventory_risk"
        elif "campaign" in q or "deals" in q:
            best_metric = "promo_uplift"
        else:
            best_metric = "revenue"  # General fallback metric

    # Calculate Confidence Score based on number of synonym hits
    metric_info = METRIC_DICTIONARY[best_metric]
    confidence += min(max_matches * 15, 45) # Max +45% confidence for synonym matches
    
    # Context-specific confidence boosts
    if "best performing" in q and best_metric == "revenue":
        confidence += 5
        reasoning = "Resolved 'best performing' to 'Revenue' based on standard FMCG practice."
    elif "most successful" in q and "promotion" in q:
        best_metric = "promo_uplift"
        confidence = 95
        reasoning = "Mapped 'most successful promotion' to 'Promotion Revenue Uplift' metric."
    elif "fastest growing" in q or "growth" in q:
        best_metric = "growth_rate"
        confidence = 90
        reasoning = "Mapped 'fastest growing' to 'Week-over-Week Growth Rate' metric."
    elif "risk" in q or "stockout" in q:
        best_metric = "inventory_risk"
        confidence = 95
        reasoning = "Mapped 'inventory risk' to 'Stockout Risk' metric."
    else:
        reasoning = f"Mapped keyword query terms to the '{metric_info['name']}' metric."

    return {
        "resolved": True,
        "metric_key": best_metric,
        "metric_name": metric_info["name"],
        "metric_definition": metric_info["description"],
        "sql_expression": metric_info["sql_expression"],
        "confidence": min(confidence, 100),
        "reasoning": reasoning
    }

if __name__ == "__main__":
    # Test resolution
    test_queries = [
        "What is the best performing region?",
        "Show products with inventory risk",
        "Which was the most successful promotion?",
        "Find the fastest growing product"
    ]
    for query in test_queries:
        print(f"Query: '{query}'")
        print(resolve_business_metric(query))
        print("-" * 40)
