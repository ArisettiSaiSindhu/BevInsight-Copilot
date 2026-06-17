# Upgraded Risk Analysis & Safeguards - BevInsight AI Copilot v2

This document details the critical operational risks and mitigation safeguards implemented in **BevInsight AI Copilot v2** to ensure secure, reliable retail decision support.

---

## 1. Enterprise SQL Injection & Stacked Queries
- **Risk:** Malicious users using natural language prompts to inject destructive SQL queries (e.g. `"; DROP TABLE stores;--"`).
- **Impact:** Permanent loss of corporate sales records and database schema destruction.
- **Safeguard (Implemented):**
  - **Start-Bound Rules:** Queries must start with `SELECT` or `WITH`.
  - **Semicolon Stacking Blocks:** Splits queries by `;` and blocks execution if more than one command block is populated.
  - **Token Checks:** Regex tokenizers analyze query strings and block execution if any modification terms (e.g., `DELETE`, `DROP`, `ALTER`, `TRUNCATE`) are matched.

---

## 2. Elasticity Forecast Model Deviations
- **Risk:** Heuristic models in the simulator simplify actual FMCG behavior. If price elasticity of demand shifts due to competitor entries, the simulator will drift.
- **Impact:** Misleading forecast predictions causing bad procurement actions.
- **Safeguard (Implemented):**
  - **Confidence Score Pacing:** Every simulator forecast returns a confidence score (base 90% and decremented by 5% for each parameters added) to warn the analyst of mathematical bounds.
  - **Explanatory Warn Memos:** UI explicitly highlights if deep discounts are modeled, noting potential margin dilutions.

---

## 3. Rate Limitations & Offline Outages
- **Risk:** API key rate limit errors (HTTP 429) or OAuth credential validation failures.
- **Impact:** The chatbot freezes, failing to compile answers.
- **Safeguard (Implemented):**
  - **Dual-Compilation Fallback:** If the Gemini client fails or is unconfigured, the backend automatically transitions to a keyword-matching rules compiler.
  - **Graceful Notification:** The UI badge updates dynamically to display "SQLite Active / Gemini Mock Mode" on credential limits, ensuring the corporate client is never locked out.
