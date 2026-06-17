# Future Improvements & Strategic Roadmap - BevInsight AI Copilot

This document outlines key technical enhancements, feature expansions, and architectural extensions planned for future releases of the **BevInsight AI Copilot** platform.

---

## 1. Multi-Turn Conversational Context
- **Objective:** Enable users to ask follow-up questions without re-stating the entire business context (e.g. User: *"Which products had stockouts?"* followed by *"Why did store S022 fail?"*).
- **Implementation Strategy:**
  - Introduce a session management layer in FastAPI to store chat history (NLP questions + returned SQL + generated insights).
  - Pass the recent 3-4 conversation rounds as context to the Gemini API, enabling the model to resolve pronouns and relative references (like *"that"*, *"them"*, *"previous"*).

---

## 2. Advanced Query Caching Layer
- **Objective:** Reduce Gemini API execution latency and token costs by avoiding recompilations for duplicate or highly similar queries.
- **Implementation Strategy:**
  - Implement a semantic caching layer using a lightweight vector database (e.g. ChromaDB, Faiss) or simple Redis cache.
  - Compute embeddings for incoming natural language questions. If a new question shares >95% similarity with a cached question, retrieve the pre-compiled SQL query directly, bypassing LLM call.

---

## 3. Write-Back Capabilities & ERP Integration
- **Objective:** Transition BevInsight from a passive analysis assistant to an active operational copilot.
- **Implementation Strategy:**
  - Create secure write-back endpoints enabling the AI to draft purchase orders, inventory transfers, or promotional modifications.
  - If a Critical Stockout Alert fires for Store S022, include a button in the UI: *"Approve Inventory Transfer"* which triggers an ERP API call to transfer stock from a nearby Hypermarket.

---

## 4. Fine-Tuned Domain Models
- **Objective:** Enhance Text-to-SQL translation accuracy for specialized corporate abbreviations, local product slangs, and supply chain metrics.
- **Implementation Strategy:**
  - Log user questions and verified SQL queries.
  - Build a curated dataset of 2,000+ FMCG question-SQL pairs.
  - Fine-tune a specialized model (e.g., Gemini 1.5 Flash customized version) to ensure high-accuracy responses for industry jargon.
