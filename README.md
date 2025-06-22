# Multi-Agent Text-to-SQL & Business QA at VDS

> **Goal** – Automate two frequent analytics scenarios at VDS:
>
> 1. **Business-level QA** – answer questions about indicator definitions & calculation logic.
> 2. **Text-to-SQL** – translate natural-language questions into SQL queries that fit the internal schema.

---

## 1 Architecture overview

![Multi-agent workflow](docs/multiagent_workflow.png)

The pipeline is orchestrated by **LangGraph** and powered by **Gemini Flash 2.0**.  Core agents:

| Step | Agent               | Purpose |
|------|---------------------|---------|
| ①    | **Context Parser**  | Enrich raw question with business context & temporal cues. |
| ②    | **Task Router**     | Route to *business* or *sql* branch. |
| ③    | **Schema Selector** | Filter schema to tables/columns relevant to the question. |
| ④    | **SQL Planner**     | Produce a step-by-step logical plan. |
| ⑤    | **SQL Generator**   | Generate final SQL from the plan. |
| ∥    | **Business QA Agent** | Answer qualitative questions via ReAct + retrieval. |

---

## 2 Key internal results

| Variant     | Business QA | Text-to-SQL |
|-------------|-------------|-------------|
| Single      | 100 %       | 78 %        |
| +Schema     | 100 %       | 90 %        |
| +Planner    | **100 %**   | **98.5 %**  |

Dataset: 60 business questions & 200 question–SQL pairs (single revenue table, 18 columns).

---
## 3 Open-source model evaluation (zero-shot)

| Model                 | Text-to-SQL<br>Accuracy | Business-QA<br>Accuracy |
|-----------------------|-------------------------|-------------------------|
| **Qwen3-14B**         | **88.5 %**              | **96.67 %**             |
| Qwen2.5-14B-Coder     | 70.5 %                 | **96.67 %**             |
| Qwen2.5-7B            | 74.0 %                 | 86.67 %                 |
| Qwen2.5-7B-Coder      | 70.0 %                 | 91.67 %                 |

Dataset: 60 business questions & 200 question–SQL pairs (single revenue table, 18 columns).
---

## 4 Roadmap

1. Fine-tune an on-premise open-source LLM on internal chat logs.
2. Add a critic agent for automatic validation & guardrails.
3. Enable live SQL execution with latency logging.
4. Expand schema coverage beyond a single revenue table.


© 2025 Viettel Digital Services – internal use only.