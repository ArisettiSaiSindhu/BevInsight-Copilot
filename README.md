# BevInsight AI Copilot (v2 Upgraded)

BevInsight AI Copilot is a next-generation, competition-grade AI Business Decision Support Copilot for FMCG beverage companies. Beyond a simple Natural Language to SQL chatbot, BevInsight includes intent resolution, price elasticity forecasting simulations, and explainable AI confidence scores, alongside proactive smart alerts.

---

## Key Advanced Features

1. **Business Metric Resolution Layer:** Translates vague retail terms (*"fastest growing"*, *"inventory risk"*, *"best promotion"*) into exact relational database metrics (WoW growth, stockout weeks, promotional uplift).
2. **Decision Simulator (Scenario Engine):** Allows users to shift sliders (Promotional Discounts, Safety Stock Levels, Campaign Durations) to model elasticities and predict simulated revenue changes and stockout risks.
3. **Explainability & Confidence Engine:** Explains *why* a query was compiled, *which* tables were selected, and computes a metric mapping confidence score.
4. **Smart Alerts Engine:** Automatically scans SQLite logs to flag critical stockouts, underperforming promotions, and excess inventory risks.
5. **SQL Safety Wrapper:** AST-style validation layer blocking SQL injection vectors, stacked queries, and modify commands (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `PRAGMA`), enforcing read-only constraints.
6. **Generate Weekly Board Report:** Compiles summaries, charts, risk scores, and recommendations into a formatted executive board report printable directly to PDF.

---

## Folder Structure

```
bevinsight-copilot/
├── app/                         # FastAPI Backend
│   ├── main.py                  # API Routes (Dashboard, Simulator, AI Query, Board)
│   ├── safety.py                # SQL Safety validation enforcements
│   ├── business_metrics.py      # Semantic metric resolution
│   ├── explainability_engine.py # Text explainability and confidence scoring
│   ├── scenario_engine.py       # Heuristic demand-pricing forecasting simulator
│   ├── database.py              # SQLite connection wrappers
│   ├── generator.py             # Seeding synthetic retail history data
│   ├── llm.py                   # Gemini integration wrappers
│   ├── prompts.py               # Prompt templates
│   └── config.py                # Environment configs
├── static/                      # Frontend SPA (React + Tailwind CDN Client)
│   ├── index.html
│   ├── style.css
│   └── app.js
├── frontend/                    # Standalone React Vite components
│   ├── src/
│   │   ├── components/          {DashboardKPIs, BusinessHealth, ChatInterface, DecisionSimulator}
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── requirements.txt
```

---

## Quick Start Guide

### 1. Installation
Ensure Python 3.10+ and Node.js are installed. In your terminal:
```powershell
# Setup virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r requirements.txt
```

### 2. Database Initialization
Seed the SQLite database with 24 weeks of FMCG beverage sales:
```powershell
python -m app.generator
```

### 3. Execution
Start the FastAPI server (it serves the React client directly on root):
```powershell
uvicorn app.main:app --reload
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

---

## Competition Differentiation (10 Core Pillars)
1. **Explainable AI:** Computes a transparent confidence percentage score and prints reasoning paths for audits.
2. **AST SQL Safety Guard:** Intercepts raw LLM outputs to block injection attempts and stack query executions.
3. **Resilient Local Fallback:** Employs rule-based regex parsers to guarantee dashboard operation during API offline cycles.
4. **Heuristic Simulation:** Forecasts elasticity trends dynamically using historical transaction ratios.
5. **Executive Summary Compilation:** Automates standard text business briefs directly from database indicators.
6. **FMCG Intent Resolution:** Corrects lexical differences (e.g., matching "water volume" to `AquaPure Still` units).
7. **Proactive Alarm Triggers:** Monitors warehouse supply stock buffers and flags overstock risks.
8. **PDF Report Compilation:** Connects responsive print sheets to compile presentation memos.
9. **Interactive Dashboard Cards:** Merges live conversation windows with dynamic KPI grids and Chart.js displays.
10. **Enterprise Monorepo Split:** Provides separate react files alongside monolithic FastAPI deployment bindings.
