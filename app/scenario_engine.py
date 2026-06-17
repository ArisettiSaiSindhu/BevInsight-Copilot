from app.database import get_db_connection

def simulate_business_scenario(
    discount_change: float = 0.0,    # e.g., +10.0 (meaning 15% -> 25% discount)
    inventory_change: float = 0.0,   # e.g., +20.0 (meaning +20% opening stock)
    promo_weeks_change: int = 0,     # e.g., +2 (prolonging promo periods)
    sales_drop_change: float = 0.0   # e.g., -10.0 (general sales decrease)
) -> dict:
    """
    Simulates retail FMCG outcomes based on elasticities, inventory safety margins,
    and promotional adjustments.
    """
    # 1. Retrieve baseline aggregates
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            SUM(revenue) AS base_rev, 
            SUM(units_sold) AS base_units,
            AVG(discount_pct) AS avg_discount
        FROM sales_promotions;
    """)
    base_row = cursor.fetchone()
    base_rev = base_row["base_rev"] or 1000000.0
    base_units = base_row["base_units"] or 500000
    base_avg_discount = base_row["avg_discount"] or 5.0
    
    cursor.execute("SELECT COUNT(*) AS stockouts FROM inventory WHERE stockout_flag = 1;")
    stockout_row = cursor.fetchone()
    base_stockouts = stockout_row["stockouts"] or 200
    
    conn.close()

    # 2. Run simulation algorithms
    sim_units = base_units
    sim_rev = base_rev
    sim_stockouts = base_stockouts
    confidence = 90
    
    # Heuristics:
    # A. PROMOTIONAL DISCOUNT INCREASE EFFECTS
    # Price Elasticity of Demand: Every +1.0% increase in discount depth yields +2.5% unit sales
    # But dilutes baseline prices: revenue multiplier = (1 - new_discount/100) / (1 - old_discount/100)
    if discount_change != 0:
        pct_change = discount_change / 100.0
        # Unit sales expansion
        unit_uplift = 2.5 * discount_change
        sim_units = int(sim_units * (1 + unit_uplift / 100.0))
        
        # Price dilution
        old_price_factor = 1.0 - (base_avg_discount / 100.0)
        new_price_factor = 1.0 - ((base_avg_discount + discount_change) / 100.0)
        price_dilution = new_price_factor / old_price_factor
        
        sim_rev = sim_rev * (sim_units / base_units) * price_dilution
        
        # Deep promotion also increases stockout pressure (if inventory isn't changed)
        if discount_change > 0 and inventory_change <= 0:
            sim_stockouts = int(sim_stockouts * (1 + (discount_change * 1.5) / 100.0))
        confidence -= 5

    # B. INVENTORY INCREASE EFFECTS
    # Adding inventory reduces stockouts: every +1% inventory yields -1.4% stockouts
    # Recovered sales: every 10% stockout reduction recovers 1.5% lost volume/revenue
    if inventory_change != 0:
        inv_pct = inventory_change / 100.0
        stockout_reduction = 1.4 * inventory_change
        sim_stockouts = max(0, int(sim_stockouts * (1 - stockout_reduction / 100.0)))
        
        if inventory_change > 0:
            # Recover lost revenue
            recovered_pct = (stockout_reduction / 10.0) * 0.015
            sim_rev = sim_rev * (1 + recovered_pct)
            sim_units = int(sim_units * (1 + recovered_pct))
        confidence -= 5

    # C. PROMO DURATION CHANGE EFFECTS
    # Extending promotions by weeks increases total promo revenue but dampens average prices
    if promo_weeks_change != 0:
        # Assumes weekly promo extension increases units by 1.8% WoW but lowers price index
        sim_units = int(sim_units * (1 + (promo_weeks_change * 1.8) / 100.0))
        sim_rev = sim_rev * (1 + (promo_weeks_change * 1.2) / 100.0)
        confidence -= 5

    # D. GENERAL SALES/DEMAND SHIFTS
    if sales_drop_change != 0:
        drop_pct = sales_drop_change / 100.0
        sim_units = int(sim_units * (1 + drop_pct))
        sim_rev = sim_rev * (1 + drop_pct)
        # Drops in demand reduce inventory stockouts
        if sales_drop_change < 0:
            sim_stockouts = int(sim_stockouts * (1 + (sales_drop_change * 1.2) / 100.0))
        confidence -= 5

    # 3. Calculate Risk Score (1 to 10 scale)
    # Risk factor components:
    # - Stockout ratio (stockouts relative to transaction volume)
    # - Margin dilution (average discount depth)
    # - Revenue drops
    stockout_ratio = (sim_stockouts / sim_units) * 1000 if sim_units > 0 else 0
    margin_risk = (base_avg_discount + discount_change) / 10.0
    
    risk_score = 4.0  # Base standard risk
    risk_score += (stockout_ratio * 0.8)
    risk_score += (margin_risk * 0.5)
    
    if sales_drop_change < 0:
        risk_score += abs(sales_drop_change) * 0.25
        
    risk_score = round(max(1.0, min(10.0, risk_score)), 1)
    
    # Determine Risk Category
    if risk_score >= 7.5:
        risk_level = "High"
    elif risk_score >= 4.5:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    # Calculate absolute differences
    rev_diff = round(sim_rev - base_rev, 2)
    units_diff = sim_units - base_units
    
    rev_diff_sign = "+" if rev_diff >= 0 else ""
    units_diff_sign = "+" if units_diff >= 0 else ""
    
    rev_pct_diff = round((rev_diff / base_rev) * 100, 1) if base_rev > 0 else 0.0
    units_pct_diff = round((units_diff / base_units) * 100, 1) if base_units > 0 else 0.0

    return {
        "scenario": {
            "discount_change": f"{discount_change:+.1f}%",
            "inventory_change": f"{inventory_change:+.1f}%",
            "promo_weeks_change": f"{promo_weeks_change:+d} weeks",
            "sales_drop_change": f"{sales_drop_change:+.1f}%"
        },
        "base_metrics": {
            "revenue": round(base_rev, 2),
            "units_sold": base_units,
            "stockouts": base_stockouts
        },
        "simulated_metrics": {
            "revenue": round(sim_rev, 2),
            "units_sold": sim_units,
            "stockouts": sim_stockouts
        },
        "sales_uplift": f"{units_diff_sign}{units_pct_diff}%",
        "revenue_change": f"{rev_diff_sign}${abs(rev_diff):,.2f} ({rev_diff_sign}{rev_pct_diff}%)",
        "inventory_risk": risk_level,
        "risk_score": risk_score,
        "confidence": max(confidence, 60)
    }

if __name__ == "__main__":
    # Test simulation
    print(simulate_business_scenario(discount_change=10.0))
    print("-" * 40)
    print(simulate_business_scenario(inventory_change=20.0))
