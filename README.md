# ASK Config GenAI

Project: ASK Config GenAI

A concise GenAI-driven assistant for querying and summarizing network configuration stored in a local database. Users interact with the system via natural-language prompts; an agent parses the prompt, runs one or more tools/skills that query the config data, and returns a human-friendly answer.

This README documents the code layout, key components, data contracts, run/development instructions, and guidance for extending the system.

---

## High-level overview

- Purpose: let network engineers (or automation systems) ask natural-language questions about network device configuration and receive concise, actionable answers.
- Interaction model: user types a prompt -> `Agent` (in `src/ask_network/agent.py`) interprets prompt -> uses prompt templates and parsing logic (in `src/ask_network/prompt.py`) -> invokes tools (in `src/ask_network/tools.py`) and modular `skills/` to query `data/` -> synthesizes and returns a natural-language response.

Assumptions
- This repository contains the core agent logic and connectors but not a specific external LLM provider. The prompts are prepared for a GenAI model and the app expects an LLM call to be wired either inside the agent or via a skill.
- No concrete runner script was present; examples below show how to wire a small runner. Adjust according to your project's actual APIs and secrets management.

---

## Repository layout

- `requirements.txt` — Python dependencies (install with pip).
- `src/` — package sources.
  - `src/__init__.py`
  - `src/ask_network/`
    - `__init__.py`
    - `agent.py`        — orchestration layer: receives prompts, chooses skills/tools, manages LLM calls and response formatting.
    - `prompt.py`       — centralized place for prompt templates, prompt-building helpers, and parsing utilities.
    - `tools.py`        — I/O tools for querying the network config database, caching, filtering, and returning structured results.
    - `skills/`         — folder for domain-specific skills (e.g., `vlan_skill.py`, `routing_skill.py`). Keep each skill small and testable.
- `data/` — local data used by tools (e.g., sqlite files, CSVs, or mock JSON). Keep sensitive data out of the repo.
- `README.md` — this file.

---

## Key components (what to expect in each file)

- `src/ask_network/agent.py`
  - Entrypoint for handling user prompts.
  - Typical responsibilities:
    - Validate the raw prompt.
    - Choose which skill(s) to run based on intent.
    - Invoke tools to fetch structured data.
    - Optionally call a GenAI model to summarize or transform results.
    - Format and return the final response.

- `src/ask_network/prompt.py`
  - Houses prompt templates and helpers for building LLM-ready text.
  - Should export functions like `build_query_prompt(intent, context)` and small helpers for sanitizing user input.

- `src/ask_network/tools.py`
  - Database access, query builders, and result transformers.
  - Keep I/O here so skills and the agent stay testable and deterministic.
  - Examples: `get_device_config(device_id)`, `search_acl(device, term)`, `list_vlans(device)`.

- `src/ask_network/skills/`
  - Each skill focuses on a single user intent or vertical (VLANs, routing, interfaces, inventory).
  - Skills should accept structured inputs and return structured outputs. The `agent` converts user prompt -> structured input for a skill.

---

## Data shapes / API contract

Design simple, well-documented data structures for exchange between agent, skills and tools. Example shapes:

- Device config record (returned by a tool):

{
  "device_id": "router01",
  "hostname": "router01",
  "vendor": "ios-xe",
  "config_snippet": "interface GigabitEthernet0/1\n description uplink ...",
  "metadata": {
    "last_updated": "2026-05-20T12:34:56Z"
  }
}

- Skill result (skill -> agent):

{
  "skill": "vlan_summary",
  "device_id": "switch01",
  "summary": "Switch has 24 VLANs; 3 inactive; VLAN 10 is the management VLAN",
  "details": [ { "vlan": 10, "name": "mgmt", "status": "active" }, ... ]
}

Agent should validate and normalize these shapes before passing them to the LLM or returning to the user.

---

## Example user interaction

User: "Show me the VLANs on switch sw01 and highlight untagged ports."

Flow:
1. `Agent` receives the prompt.
2. `prompt.py` builds an intent (e.g., `vlan_query`) and a sanitized query prompt.
3. `Agent` invokes `skills/vlan_skill` with structured parameters: `{ device_id: "sw01", details: { include_ports: true }}`.
4. `vlan_skill` calls `tools.get_vlan_info(device_id)` which queries `data/`.
5. Skill returns structured results; `agent` either formats directly or asks an LLM to create a natural-language report and recommendations.
6. The final response is returned to the user in chat.

---

## Getting started (local)

1. Create and activate a virtual environment (Windows PowerShell example):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run a small interactive runner (example). There is no canonical CLI yet — create a small runner file like `scripts/run_agent.py` to exercise the agent. Minimal example:

```text
# example runner — create `scripts/run_agent.py`
# Implement or adapt the Agent class in `src/ask_network/agent.py` and then run:
# from src.ask_network.agent import Agent
# agent = Agent()
# print(agent.handle_prompt("Show me interfaces on router01 with description"))
```

Adjust to your actual `Agent` constructor signature. If the repo already exposes a CLI or web server, prefer that.

Secrets / LLM keys: keep keys out of the repo. Use environment variables (e.g. `OPENAI_API_KEY`) or a secrets manager.

---

## Development guidance and best practices

- Keep prompt logic in `prompt.py` and keep the templates small and testable.
- Keep I/O in `tools.py` to make unit tests deterministic.
- Each skill should be unit tested with mocked tool responses.
- Add type hints and small schema validations (pydantic or marshmallow recommended) for the data shapes.
- Avoid sending unfiltered production configs to a public LLM. Redact secrets (passwords, keys, SNMP community strings) in `tools.py` before passing text to any external model.

Edge cases to handle
- Empty or ambiguous prompts: agent should request clarification rather than guessing.
- Large configs: summarize or paginate instead of sending full blobs.
- Missing device or data: return a clear user-facing error and a diagnostic (e.g., "device not found in DB").

---

## Testing

- Add unit tests for tool functions and skills. Mock DB calls and file I/O.
- Add integration tests for the agent that mock or stub the LLM responses.

---

## Security & privacy

- Do not commit real credentials or private configs.
- Redact secrets before sending to LLMs.
- Consider a data retention policy for logs and conversation transcripts.

---

## Extending the project

- Add new skill modules under `src/ask_network/skills/` for new use cases.
- Add a service layer (FastAPI/Flask) for a web chat front-end.
- Add caching for repeated queries.
- Add role-based access control if multiple users with different permissions will use the system.

---

## Next steps (suggested)

- Create a small `scripts/run_agent.py` runner and add example prompts in `examples/`.
- Add unit tests for at least one tool and one skill.
- Add a sample `data/` dataset (anonymized) for local dev.

---

If you'd like, I can also:
- Add the example `scripts/run_agent.py` runner to the repo.
- Scaffold a skill (e.g., `vlan_skill.py`) and a small unit test.
- Add a simple FastAPI server to expose the agent as an HTTP API.

Tell me which of those you'd like next and I'll implement it.
