# API Documentation - BevInsight AI Copilot

This document specifies the REST API endpoints provided by the **BevInsight AI Copilot** backend server.

---

## 1. Health Status Endpoint

### `GET /api/health`
Checks backend service availability and database connectivity.

#### Response:
- **Status Code:** `200 OK`
- **Content-Type:** `application/json`

```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

## 2. Executive Dashboard Endpoint

### `GET /api/dashboard`
Aggregates cumulative sales figures, top dimensions, and weekly/regional chart data.

#### Response:
- **Status Code:** `200 OK`
- **Content-Type:** `application/json`

```json
{
  "kpis": {
    "total_revenue": 1734435.06,
    "total_units_sold": 756228,
    "promo_revenue_pct": 10.9,
    "top_product": "OrchardFresh Mango",
    "top_region": "North",
    "inventory_risk_count": 5
  },
  "charts": {
    "weekly_trend": [
      {
        "week_start_date": "2026-01-04",
        "units": 28540,
        "revenue": 68450.25
      }
    ],
    "regional_distribution": [
      {
        "region": "North",
        "units": 215430,
        "revenue": 512400.12
      }
    ],
    "category_distribution": [
      {
        "category": "Carbonated",
        "units": 312000,
        "revenue": 620000.5
      }
    ]
  }
}
```

---

## 3. Smart Alerts Endpoint

### `GET /api/alerts`
Compiles critical stockouts, underperforming campaigns, and weekly financial metrics into a prioritized notification array.

#### Response:
- **Status Code:** `200 OK`
- **Content-Type:** `application/json`

```json
[
  {
    "id": "alert-1",
    "severity": "CRITICAL",
    "category": "INVENTORY",
    "title": "Stockout: PureBrew Latte",
    "description": "Product went out of stock in Boston Hub Hypermarket (North) in the recent week. Opening Stock: 90, Received: 42.",
    "timestamp": "2026-06-14"
  },
  {
    "id": "alert-6",
    "severity": "WARNING",
    "category": "PROMOTION",
    "title": "Underperforming Promotion: SparkleCola Zero",
    "description": "Promo 'Discount 50%' in Times Square Mart failed to generate expected volume. Sold only 18 units.",
    "timestamp": "2026-06-07"
  }
]
```

---

## 4. Conversational AI Query Endpoint

### `POST /api/query`
Receives a business user's natural language question, generates and executes SQL against SQLite, and passes results to Gemini to compile strategic text insights.

#### Request Schema (JSON):
```json
{
  "question": "Top selling products in South region"
}
```

#### Response Schema (JSON):
- **Status Code:** `200 OK`
- **Content-Type:** `application/json`

```json
{
  "question": "Top selling products in South region",
  "sql": "SELECT p.product_name, SUM(s.units_sold) AS total_units_sold, ROUND(SUM(s.revenue), 2) AS total_revenue FROM sales_promotions s JOIN products p ON s.product_id = p.product_id WHERE s.region = 'South' GROUP BY p.product_name ORDER BY total_units_sold DESC LIMIT 10;",
  "results": [
    {
      "product_name": "LeafyTeas Iced Peach",
      "total_units_sold": 12540,
      "total_revenue": 27588.0
    },
    {
      "product_name": "CitrusFizz Lemon",
      "total_units_sold": 9850,
      "total_revenue": 17730.0
    }
  ],
  "insights": "<div class=\"insight-container\">\n  <h3 class=\"section-title text-blue-400 font-bold mb-2\">Executive Answer Summary</h3>\n  <p class=\"mb-4\">In the <strong>South region</strong>, the best-selling products are led by <strong>LeafyTeas Iced Peach</strong>...</p>\n</div>",
  "success": true,
  "error": null
}
```
> [!NOTE]
> If the SQL syntax or query execution fails, `success` will return `false`, `results` will be empty `[]`, and details will be populated in the `error` field.
