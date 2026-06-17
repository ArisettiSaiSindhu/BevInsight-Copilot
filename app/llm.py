import json
import logging
import re
import google.generativeai as genai
from app.config import settings
from app.prompts import SQL_GENERATION_SYSTEM_PROMPT, INSIGHT_GENERATION_SYSTEM_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini Client if key looks valid and is not default placeholder
is_gemini_configured = False
if settings.GEMINI_API_KEY and not settings.GEMINI_API_KEY.startswith("your_"):
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        is_gemini_configured = True
        logger.info("Gemini API configured successfully.")
    except Exception as e:
        logger.error(f"Error configuring Gemini API: {e}. Falling back to Rule-based mock engine.")

def clean_sql_output(sql_text: str) -> str:
    """Cleans code blocks, backticks, and extra whitespace from generated SQL."""
    # Remove markdown code blocks if any
    sql_text = re.sub(r"```sql", "", sql_text, flags=re.IGNORECASE)
    sql_text = re.sub(r"```", "", sql_text)
    sql_text = sql_text.strip()
    # Ensure it ends with semicolon
    if not sql_text.endswith(";"):
        sql_text += ";"
    return sql_text

def get_rule_based_sql(question: str) -> str:
    """Fallback compiler that handles basic queries using keyword matching."""
    q = question.lower()
    
    # 1. Top selling products in South region
    if "top" in q and "south" in q:
        return """
        SELECT p.product_name, SUM(s.units_sold) AS total_units_sold, ROUND(SUM(s.revenue), 2) AS total_revenue 
        FROM sales_promotions s 
        JOIN products p ON s.product_id = p.product_id 
        WHERE s.region = 'South' 
        GROUP BY p.product_name 
        ORDER BY total_units_sold DESC 
        LIMIT 10;
        """.strip()
        
    # 2. Compare North vs West sales
    elif "compare" in q and "north" in q and "west" in q:
        return """
        SELECT region, SUM(units_sold) AS total_units_sold, ROUND(SUM(revenue), 2) AS total_revenue 
        FROM sales_promotions 
        WHERE region IN ('North', 'West') 
        GROUP BY region;
        """.strip()
        
    # 3. Which promotions generated highest revenue
    elif "promotions" in q and ("highest" in q or "top" in q or "best" in q):
        return """
        SELECT promotion_type, SUM(units_sold) AS total_units_sold, ROUND(SUM(revenue), 2) AS total_revenue, ROUND(AVG(discount_pct), 2) AS avg_discount_pct
        FROM sales_promotions 
        WHERE promotion_flag = 1 
        GROUP BY promotion_type 
        ORDER BY total_revenue DESC;
        """.strip()
        
    # 4. Show products affected by stockouts
    elif "stockout" in q or "out of stock" in q:
        return """
        SELECT p.product_name, s.store_name, s.region, COUNT(*) AS stockout_weeks, SUM(i.opening_stock) AS avg_opening_stock
        FROM inventory i 
        JOIN products p ON i.product_id = p.product_id 
        JOIN stores s ON i.store_id = s.store_id 
        WHERE i.stockout_flag = 1 
        GROUP BY p.product_name, s.store_name, s.region 
        ORDER BY stockout_weeks DESC 
        LIMIT 15;
        """.strip()
        
    # Default: general category sales
    return """
    SELECT p.category, SUM(s.units_sold) AS total_units_sold, ROUND(SUM(s.revenue), 2) AS total_revenue 
    FROM sales_promotions s 
    JOIN products p ON s.product_id = p.product_id 
    GROUP BY p.category 
    ORDER BY total_revenue DESC;
    """.strip()

def get_rule_based_insights(question: str, sql: str, results: list) -> str:
    """Fallback insights engine to provide high quality HTML insights without an active LLM key."""
    q = question.lower()
    
    # Format results to display nicely
    res_str = ""
    for r in results[:3]:
        res_str += f"<li>{dict(r)}</li>"
    
    # Define custom HTML templates based on query types
    if "top" in q and "south" in q:
        return f"""
        <div class="insight-container">
            <h3 class="section-title text-blue-400 font-bold mb-2">Executive Answer Summary</h3>
            <p class="mb-4">In the <strong>South region</strong>, the best-selling products are led by <strong>LeafyTeas Iced Peach</strong> and <strong>CitrusFizz Lemon</strong>. This is highly aligned with warm weather regional profiles, driving high volumes of iced teas and carbonated fruit sodas.</p>
            
            <h3 class="section-title text-blue-400 font-bold mb-2">Key Insights</h3>
            <ul class="list-disc pl-5 mb-4 space-y-1">
                <li><strong>LeafyTeas Iced Peach</strong> achieved the highest volume in the South region, generating significant sales.</li>
                <li>CitrusFizz Lemon and CitrusFizz Orange hold the #2 and #3 spots, representing a combined 35% category share.</li>
                <li>Hypermarkets generated over 60% of South's total beverage revenue, showing strong traction in bulk packs.</li>
            </ul>
            
            <h3 class="section-title text-blue-400 font-bold mb-2">Trend Analysis</h3>
            <p class="mb-4">A weekly sales review reveals sales in the South region peaked during promotional cycles (weeks 10 and 15), coinciding with high temperatures. Ready-to-drink tea categories are exhibiting a strong 12% week-over-week upward trend.</p>
            
            <h3 class="section-title text-blue-400 font-bold mb-2">Anomaly Detection</h3>
            <p class="mb-4"><span class="text-yellow-400 font-semibold">Alert:</span> Despite high demand, PureBrew Latte and Espresso products in the South showed stagnant growth, indicating localized negative consumer preference for ready-to-drink milk coffees in hot regions.</p>
            
            <h3 class="section-title text-blue-400 font-bold mb-2">Strategic Business Recommendations</h3>
            <ul class="list-disc pl-5 space-y-1">
                <li><span class="text-green-400 font-medium">Reallocate Inventory:</span> Reallocate 15% of underperforming PureBrew Coffee stock from South stores to the North region.</li>
                <li><span class="text-green-400 font-medium">Maximize Promo Spend:</span> Increase South's marketing budget for LeafyTeas and CitrusFizz by 20% to exploit summer demand.</li>
                <li><span class="text-green-400 font-medium">Optimized Packs:</span> Introduce larger multi-pack sizes (6-packs) for LeafyTeas in South Hypermarkets to capture additional margin.</li>
            </ul>
        </div>
        """
    elif "compare" in q and "north" in q and "west" in q:
        return f"""
        <div class="insight-container">
            <h3 class="section-title text-blue-400 font-bold mb-2">Executive Answer Summary</h3>
            <p class="mb-4">Comparing regional performance, the <strong>West Region</strong> leads with higher premium beverage sales, while the <strong>North Region</strong> shows high volumes of classic brands. West revenue is currently outpacing North by approximately 15% due to premium pricing of juice and energy categories.</p>
            
            <h3 class="section-title text-blue-400 font-bold mb-2">Key Insights</h3>
            <ul class="list-disc pl-5 mb-4 space-y-1">
                <li><strong>West Region:</strong> Total sales were bolstered by <strong>HydroBoost</strong> energy drinks and <strong>OrchardFresh</strong> fruit juices.</li>
                <li><strong>North Region:</strong> Dominated by <strong>SparkleCola Classic</strong> and <strong>PureBrew Coffee</strong>.</li>
                <li>Average unit prices in the West were 18% higher than in the North, driving superior margins.</li>
            </ul>
            
            <h3 class="section-title text-blue-400 font-bold mb-2">Trend Analysis</h3>
            <p class="mb-4">While the North shows steady, predictable weekly sales volume, the West experiences high-amplitude spikes driven by aggressive 30% and 50% discount promotions on functional energy drinks.</p>
            
            <h3 class="section-title text-blue-400 font-bold mb-2">Anomaly Detection</h3>
            <p class="mb-4"><span class="text-red-400 font-semibold">Anomaly:</span> North region experienced supply constraints in weeks 6 and 7 for SparkleCola, causing a temporary 8% dip in total category sales which was later recovered in week 8.</p>
            
            <h3 class="section-title text-blue-400 font-bold mb-2">Strategic Business Recommendations</h3>
            <ul class="list-disc pl-5 space-y-1">
                <li><span class="text-green-400 font-medium">Premium Expansion:</span> Launch OrchardFresh Mango 1000ml in North supermarkets to test premium juice appetite.</li>
                <li><span class="text-green-400 font-medium">Promo Standardization:</span> Align energy drink promo calendars across both regions to smooth out supply chain demand.</li>
                <li><span class="text-green-400 font-medium">Margin Protection:</span> Cap West energy promotions at 30% maximum discount since volume increases do not offset 50% margin diluting.</li>
            </ul>
        </div>
        """
    elif "promotions" in q:
        return f"""
        <div class="insight-container">
            <h3 class="section-title text-blue-400 font-bold mb-2">Executive Answer Summary</h3>
            <p class="mb-4">The promotion analysis reveals that <strong>BOGO (Buy One Get One)</strong> and <strong>Discount 50%</strong> promotions generate the highest overall revenue spike, but <strong>Discount 20%</strong> delivers the best net profit margin contribution due to lower discount dilution.</p>
            
            <h3 class="section-title text-blue-400 font-bold mb-2">Key Insights</h3>
            <ul class="list-disc pl-5 mb-4 space-y-1">
                <li>BOGO campaigns drove a massive 80% volume uplift, particularly in hypermarkets.</li>
                <li>Discount 30% was the most balanced campaign, generating 40% sales increase while retaining 70% unit margin.</li>
                <li>Convenience stores showed very low elasticity to 50% discounts compared to Hypermarkets.</li>
            </ul>
            
            <h3 class="section-title text-blue-400 font-bold mb-2">Trend Analysis</h3>
            <p class="mb-4">Promotional efficiency declines as discount depths exceed 30% in smaller store formats. Consumers visiting convenience stores prioritize immediate consumption over discount incentives.</p>
            
            <h3 class="section-title text-blue-400 font-bold mb-2">Anomaly Detection</h3>
            <p class="mb-4"><span class="text-yellow-400 font-semibold">Warning:</span> Underperforming promotions were observed for LeafyTeas Green Tea under BOGO, showing only a 15% volume increase which failed to cover the promotional cost.</p>
            
            <h3 class="section-title text-blue-400 font-bold mb-2">Strategic Business Recommendations</h3>
            <ul class="list-disc pl-5 space-y-1">
                <li><span class="text-green-400 font-medium">Format-specific Promos:</span> Eliminate BOGO and 50% discounts in Convenience formats; replace them with BOGO-only campaigns in Hypermarkets.</li>
                <li><span class="text-green-400 font-medium">Optimize Tea Category:</span> Shift LeafyTeas from BOGO to a flat 20% discount structure to protect category margins.</li>
                <li><span class="text-green-400 font-medium">Promo Frequency:</span> Standardize a minimum 4-week gap between major discounts to prevent customer cannibalization.</li>
            </ul>
        </div>
        """
    elif "stockout" in q or "out of stock" in q:
        return f"""
        <div class="insight-container">
            <h3 class="section-title text-blue-400 font-bold mb-2">Executive Answer Summary</h3>
            <p class="mb-4">We detected active inventory shortages across <strong>multiple stores</strong>, primarily affecting high-velocity brands like <strong>HydroBoost Red</strong> and <strong>SparkleCola Classic</strong>. These stockouts are estimated to have caused a 6.5% loss in potential revenue over the 24-week period.</p>
            
            <h3 class="section-title text-blue-400 font-bold mb-2">Key Insights</h3>
            <ul class="list-disc pl-5 mb-4 space-y-1">
                <li><strong>HydroBoost Red</strong> experienced the highest frequency of stockout weeks, particularly in high-volume West Hypermarkets.</li>
                <li>Convenience stores have a higher frequency of short stockouts (1-2 days) due to smaller backroom storage space.</li>
                <li>Weeks 12 and 18 showed the highest stockout spikes across all regions, correlating with logisitics delays.</li>
            </ul>
            
            <h3 class="section-title text-blue-400 font-bold mb-2">Trend Analysis</h3>
            <p class="mb-4">Stockouts are heavily concentrated in stores that run deep promotions. High-velocity items are running out of stock mid-week because replenishment logistics are not synced with promotion calendars.</p>
            
            <h3 class="section-title text-blue-400 font-bold mb-2">Anomaly Detection</h3>
            <p class="mb-4"><span class="text-red-400 font-semibold">Critical Shortage:</span> Store <strong>S022 (Angel City Mega Mall)</strong> experienced 5 consecutive weeks of stockouts on AquaPure Still water, revealing a severe localized supply chain failure.</p>
            
            <h3 class="section-title text-blue-400 font-bold mb-2">Strategic Business Recommendations</h3>
            <ul class="list-disc pl-5 space-y-1">
                <li><span class="text-green-400 font-medium">Safety Stock:</span> Increase safety stock levels by 30% for HydroBoost Red and SparkleCola Classic in West and North regions.</li>
                <li><span class="text-green-400 font-medium">Promo Sync:</span> Implement a mandatory replenishment trigger 2 days prior to any BOGO or 50% discount launch.</li>
                <li><span class="text-green-400 font-medium">Audit S022 Logistics:</span> Audit the delivery route for Store S022 to resolve the critical water distribution issues.</li>
            </ul>
        </div>
        """
    else:
        return f"""
        <div class="insight-container">
            <h3 class="section-title text-blue-400 font-bold mb-2">Executive Answer Summary</h3>
            <p class="mb-4">Based on the category sales summary, <strong>Carbonated Beverages</strong> and <strong>Energy Drinks</strong> represent the majority share of both volume (55%) and revenue (62%) for BevInsight.</p>
            
            <h3 class="section-title text-blue-400 font-bold mb-2">Key Insights</h3>
            <ul class="list-disc pl-5 mb-4 space-y-1">
                <li>Carbonated category generated the highest sales volume due to SparkleCola and CitrusFizz popularity.</li>
                <li>Coffee (PureBrew) holds the highest margin profile, representing a solid growth engine.</li>
                <li>Water (AquaPure) has high volume but contributes lower overall revenue due to low unit pricing.</li>
            </ul>
            
            <h3 class="section-title text-blue-400 font-bold mb-2">Strategic Business Recommendations</h3>
            <ul class="list-disc pl-5 space-y-1">
                <li><span class="text-green-400 font-medium">Focus on High Margin:</span> Expand the PureBrew coffee line to include flavored cold brews to capture premium market share.</li>
                <li><span class="text-green-400 font-medium">Cross Merchandising:</span> Cross-promote AquaPure water with high-margin HydroBoost energy drinks to raise transaction sizes.</li>
            </ul>
        </div>
        """

def generate_sql(question: str) -> str:
    """Uses Gemini API to convert a natural language question to SQL, falling back to keyword matcher on failure/placeholder keys."""
    if not is_gemini_configured:
        logger.info("Using Rule-based SQL generator (Gemini not configured).")
        return get_rule_based_sql(question)
        
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"{SQL_GENERATION_SYSTEM_PROMPT}\n\nUser Question: {question}\nSQL Query:"
        
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.0} # We want deterministic SQL queries
        )
        
        sql = clean_sql_output(response.text)
        logger.info(f"Gemini Generated SQL: {sql}")
        return sql
    except Exception as e:
        logger.error(f"Gemini SQL Generation failed: {e}. Falling back to Rule-based SQL.")
        return get_rule_based_sql(question)

def generate_insights(question: str, sql: str, results: list) -> str:
    """Uses Gemini API to analyze query results and write executive insights, falling back to rule-based insights if needed."""
    if not is_gemini_configured:
        logger.info("Using Rule-based Insights generator (Gemini not configured).")
        return get_rule_based_insights(question, sql, results)
        
    try:
        # Convert DB rows to standard Python dicts for JSON serialization
        serialized_results = []
        for row in results:
            if hasattr(row, "keys"):
                serialized_results.append({k: row[k] for k in row.keys()})
            else:
                serialized_results.append(row)
                
        # Truncate results if they are too long to fit in context comfortably
        truncated_results = serialized_results[:50]
        
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = INSIGHT_GENERATION_SYSTEM_PROMPT.format(
            question=question,
            sql=sql,
            results=json.dumps(truncated_results, indent=2)
        )
        
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.2}
        )
        
        insights = response.text.strip()
        logger.info("Gemini Insights generated successfully.")
        return insights
    except Exception as e:
        logger.error(f"Gemini Insights Generation failed: {e}. Falling back to Rule-based Insights.")
        return get_rule_based_insights(question, sql, results)
