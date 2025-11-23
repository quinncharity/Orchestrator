## Policy-Aware LLM Workflow Orchestrator

### What this orchestrator does

This service exposes a single, policy-aware orchestration endpoint that:

- **Intake agent**: Classifies the user request into a simple task type.
- **Policy engine**: Enforces rules to allow, block, or modify the input (with redaction of basic PII).
- **Task agent**: When allowed, calls Anthropic Claude with structured JSON output.
- **Audit logger**: Appends a compact JSON record to `logs/audit.jsonl` for every request.

All internal agent outputs and final API responses are valid JSON objects.

---

### Project layout

```text
policy_orchestrator/
  app/
    api/
      routes.py          # FastAPI endpoints
    core/
      config.py          # Settings, Anthropic client init
      policy.py          # Policy evaluation logic
    agents/
      intake_agent.py    # Classify request into "task type"
      task_agent.py      # Executes requests using Claude
    services/
      orchestrator.py    # Main workflow logic: intake → policy → task
    utils/
      logger.py          # JSON audit log writer
    models/
      request_models.py  # Pydantic request schema
      response_models.py # Pydantic response schema
    main.py              # FastAPI entrypoint
  tests/
    test_orchestrator.py
  requirements.txt
  README.md
  .env.example           # (expected, see below)
```

---

### Running locally

- **Create and activate a virtualenv**:

```bash
git clone https://example.com/your-org/policy-orchestrator.git
cd policy-orchestrator

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

- **Install dependencies**:

```bash
pip install -r requirements.txt
```

- **Configure environment**:

Create a `.env` file in the project root (or use `.env.example` as a template) with:

```bash
echo "ANTHROPIC_API_KEY=your_anthropic_api_key_here" > .env
```

- **Run the API with uvicorn**:

```bash
uvicorn app.main:app --reload
```

By default, the API will be available at `http://127.0.0.1:8000`.

---

### API: `POST /orchestrate`

- **Endpoint**: `/orchestrate`
- **Method**: `POST`
- **Request body** (`OrchestrateRequest`):

```json
{
  "user_id": "123",
  "request_text": "Summarize the attached document for meeting notes."
}
```

- **Response body** (`OrchestrateResponse`):

```json
{
  "task_type": "document_summarization",
  "policy_decision": "allow",
  "agent_output": {
    "summary": "Short summary text...",
    "key_points": [
      "Point 1",
      "Point 2"
    ]
  },
  "audit_id": "a2bce9e2-3d6c-4d57-9e58-7c5c0a3a88a4",
  "timestamp": "2025-11-23T12:34:56.789012+00:00"
}
```

If the request is **blocked**, `agent_output` will be `null` and `policy_decision` will be `"block"`.

---

### Policy rules

- **Block** (`decision = "block"`):
  - If the text contains obvious disallowed content based on a simple keyword list, e.g. phrases like `"build a bomb"` or `"terrorist attack"`.

- **Modify** (`decision = "modify"`):
  - Emails and simple phone number patterns are redacted using regex and replaced with:
    - `[REDACTED_EMAIL]`
    - `[REDACTED_PHONE]`

- **Allow** (`decision = "allow"`):
  - Default when no disallowed content is found and no PII is redacted.

The policy engine returns:

```json
{
  "decision": "allow | block | modify",
  "reason": "string",
  "modified_text": "string or null"
}
```

---

### Task types and Claude prompts

- **Intake agent** (`intake_agent.py`):
  - Classifies `request_text` into one of:
    - `"document_summarization"`
    - `"data_extraction"`
    - `"general_query"`
    - `"unknown"`
  - Uses simple keyword and pattern heuristics.

- **Task agent** (`task_agent.py`):
  - Calls Claude via:

```python
client.messages.create(
    model="claude-3-5-sonnet-20241022",
    temperature=0,
    messages=[{"role": "user", "content": prompt}],
    response_format={"type": "json_object"},
)
```

- **Per-task instructions**:
  - **Summarization**:
    - Returns JSON like:
      - `{"summary": "...", "key_points": ["...", "..."]}`
  - **Data extraction**:
    - Returns JSON like:
      - `{"fields": {"names": [...], "dates": [...], "amounts": [...]}}`
  - **General query**:
    - Returns JSON like:
      - `{"answer": "...", "supporting_facts": ["...", "..."]}`
  - **Unknown**:
    - Returns JSON like:
      - `{"answer": "...", "notes": "..."}`.

All responses are parsed and validated as JSON objects.

---

### Audit logging

- Logs are written to `logs/audit.jsonl` as one JSON object per line.
- Schema (`AuditLogEntry`):

```json
{
  "audit_id": "uuid",
  "user_id": "string",
  "task_type": "string",
  "policy_decision": "string",
  "timestamp": "ISO 8601 string",
  "input": "original or modified input text",
  "output_summary": "short summary, not the full model output"
}
```

- The logger never stores the full Claude response:
  - It looks for standard keys like `"summary"` or `"answer"`.
  - Falls back to a truncated, 500-character JSON string if needed.

---

### Architecture diagram (conceptual)

```text
        +------------------+
        |  Client / UI     |
        +--------+---------+
                 |
                 v
        +--------+---------+
        |  FastAPI /       |
        |  /orchestrate    |
        +--------+---------+
                 |
                 v
        +--------+---------+
        |  Orchestrator    |
        |  (services)      |
        +---+----------+---+
            |          |
            |          |
   +--------v--+   +--v---------+
   | Intake    |   |  Policy    |
   | Agent     |   |  Engine    |
   +-----+-----+   +-----+------+
         |               |
         v               v
   +-----+---------------+------+
   |      Task Agent (LLM)     |
   +-------------+-------------+
                 |
                 v
        +--------+---------+
        |  Audit Logger    |
        +------------------+
```

---

### Future extensions

- **Richer policy engine**:
  - Integrate external policy configuration (e.g., OPA or a policy DSL).
  - Add user- or tenant-specific policy profiles.
- **Advanced intake**:
  - Use an LLM-based classifier instead of simple heuristics.
  - Support task routing to multiple specialized agents.
- **Observability**:
  - Structured logging to a centralized log system.
  - Metrics and tracing (e.g., Prometheus, OpenTelemetry).
- **Persistence**:
  - Replace JSONL audit logs with a database-backed audit store.
- **Security and governance**:
  - Stronger PII detection.
  - Role-based controls over specific task types.


