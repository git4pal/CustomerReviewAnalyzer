# Repository Guidance

Implement the six agents specified in ReadMe.md as separate Python projects under
agents/. Each has its own pyproject.toml, import package, and CLI. Shared SDK and
contract code belongs in packages/foundry-review-core; this is not a seventh agent.

Use Microsoft Foundry's current versioned prompt-agent API via azure-ai-projects
2.x and its agent-bound OpenAI Responses client. Do not replace persistent agents
with local-only prompts. Read endpoint and deployment settings from the environment;
never hardcode a deployment in Python or commit .env files or credentials.

Do not create unit tests. Validate packaging, imports, Python syntax, CLI commands,
and SDK signatures. Never report portal visibility without remote registration
and verification. Never bypass deterministic approval gates or claim a human
approved a response. External ingestion, queues, manager identity, and publishing
are separate integrations, not simulated actions.

Use `uv sync --all-packages --locked` to install the workspace. The workspace
environment is .venv. Use `python manage_agents.py register` only against the
explicitly selected project; each call creates a new persistent agent version.

If you are in VS Code, read the vscode-microsoft-foundry skill first.