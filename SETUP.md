# Python Foundry Agents

Six separate Python projects implement the agents in [ReadMe.md](ReadMe.md).
They use Microsoft Foundry Agent Service (`azure-ai-projects` 2.x) and the
agent-bound OpenAI Responses API, authenticated with `DefaultAzureCredential`.
They are persistent prompt agents, not container-hosted agents. No unit tests
are included.

| Project | Package / CLI | Default Portal Name |
|---------|---------------|---------------------|
| agents/review-orchestrator | review-orchestrator-agent | ulta-review-orchestrator |
| agents/sentiment-analysis | sentiment-analysis-agent | ulta-sentiment-analysis |
| agents/review-summarization | review-summarization-agent | ulta-review-summarization |
| agents/personalized-response | personalized-response-agent | ulta-personalized-response |
| agents/brand-compliance | brand-compliance-agent | ulta-brand-compliance |
| agents/human-approval | human-approval-agent | ulta-human-approval |

Each project has its own build configuration, source package, and executable.
The shared `foundry-review-core` package provides SDK integration, typed contracts,
and approval gates. Agent projects do not import each other.

## Prerequisites

- Python 3.11+ and [uv](https://docs.astral.sh/uv/).
- An existing **new Microsoft Foundry project**, not a classic hub project.
- An Azure OpenAI deployment named `gpt-5.4-nano` in that project, or set the
  actual deployment name in the environment. Model availability and quota depend
  on your Azure region and subscription; this repository does not deploy models.
- Foundry User (formerly Azure AI User) permissions on that project.
- Azure CLI login for local use, or a managed identity with project access in Azure.

## Install And Configure

From the repository root:

```bash
uv sync --all-packages --locked
source .venv/bin/activate
az login
```

The local, gitignored `.env` already contains the confirmed deployment name:

```dotenv
FOUNDRY_PROJECT_ENDPOINT=https://YOUR-RESOURCE.services.ai.azure.com/api/projects/YOUR-PROJECT
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-5.4-nano
REVIEW_CONFIDENCE_THRESHOLD=0.80
FOUNDRY_AGENT_PREFIX=ulta
```

Fill in the endpoint from the Foundry project's overview. `.env.example` is the
committable template. Do not add API keys: authentication uses Entra ID. Existing
process environment values take precedence over dotenv values. Normal agent
commands load the nearest `.env` from the current working directory upward;
`--env /path/to/.env` selects one explicitly. The management command defaults
to the repository-root `.env`. You can use a separate `.env` for each project.

## Register And View In Foundry

```bash
python manage_agents.py register
python manage_agents.py verify
```

Registration creates a persistent version of each named agent in your project,
printing its ID, name, and version. It does not delete the agents afterward.
Open [Microsoft Foundry](https://ai.azure.com), select **the same project**, then
**Build > Agents**. Search for the six `ulta-` names above. Refresh the list if
necessary. This uses the new Foundry portal, not Agents (classic).

Every registration creates a new version. Normal invocations do not register
again and resolve the latest registered version. Coordinate version promotion
before production use; this starter does not pin immutable versions per workflow.
If a registration partially fails, completed registrations remain in Foundry.
Use `--agent sentiment-analysis` to register or verify just one role.
Changing a deployment name, prefix, or instructions requires re-registration.
`verify` checks that agent names exist; it does not verify model availability,
matching definitions, or successful model inference.

## Invoke Agents

Run one agent with a JSON file or pipe JSON through stdin:

```bash
sentiment-analysis-agent run --input examples/review.json
review-summarization-agent run --input examples/review.json
review-orchestrator-agent run --input examples/review.json
```

Each agent's CLI supports `register`, `run`, `--env`, and `--input`.
The orchestrator's `run` initializes context only. Use `process` for the complete
workflow:

```bash
review-orchestrator-agent process --input examples/review.json
```

This invokes all six persisted agents in sequence and returns structured JSON
with processing context, completed stages, findings, draft, compliance decision,
approval routing, and the README-compatible message payload. API requests incur
Azure model usage charges. No model call occurs during registration or verification.
Invalid input, refusal, incomplete output, and agent failures stop processing
without emitting an approved message.

The response agent takes `{ "review": ..., "sentiment": ..., "summary": ... }`.
Compliance additionally takes `"response"`. Human approval takes `review`,
`sentiment`, `response`, and `compliance`. Exact fields and validation rules are
defined in [models.py](packages/foundry-review-core/src/foundry_review_core/models.py).
`isVip` is the authoritative trusted input for VIP routing; an ingestion service
must populate it from customer records, not customer-authored text. Only send
the minimum customer metadata needed for processing.

## Approval And Integration Boundaries

Python gates require human review for negative sentiment, toxic content, legal
complaints, safety concerns, VIP customers, sentiment or response confidence below
the configured threshold, any compliance issue/failure, or an agent escalation.
Only qualifying positive/neutral reviews become `ReadyForPublishing` with an
`Approved` message. These gates protect detected flags; the quality of semantic
detection still depends on the model and requires operational evaluation.

`PendingHumanApproval` is a routing decision, never a simulated human approval.
The human-approval agent does not replace a manager. This repository does not
implement database ingestion, durable workflow storage, a manager approval UI,
Service Bus delivery, or publishing. Connect the returned `destination` and
`message` to those services, and publish sensitive responses only after an
authenticated manager action and revalidation of any edited response. In
production, persist workflow checkpoints and prevent duplicate publications.

All agents can be inspected individually in the portal, but chatting with the
orchestrator there does not execute the Python workflow. Use its `process` CLI
to coordinate agents. Portal-only chats also do not execute Python approval
gates, so they must not be used as an automated publishing endpoint.

## Separate Environments And Debugging

The workspace environment is convenient for local use, but each project can be
installed into an isolated environment. For example, from the repository root:

```bash
uv venv agents/sentiment-analysis/.venv
uv pip install --python agents/sentiment-analysis/.venv/bin/python \
  ./packages/foundry-review-core ./agents/sentiment-analysis
agents/sentiment-analysis/.venv/bin/sentiment-analysis-agent --help
```

Use the analogous paths for another agent. Include the shared package when
packaging or distributing an individual project. The root `uv.lock` records
the verified workspace dependency resolution.

In VS Code, select **Register Foundry Agents** or **Process Review Through Six
Foundry Agents** and press **F5** after configuration. These are CLI clients for
remote prompt agents, not local HTTP-hosted agents, so Agent Inspector server
configuration is not applicable. Registration changes remote versions; processing
incurs model usage. No Azure infrastructure is provisioned automatically.