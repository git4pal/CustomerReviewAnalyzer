# Deploy The Review Agents To Microsoft Foundry

## What This Guide Deploys

Follow this guide to register the repository's six agents in a Microsoft Foundry
project and inspect them in the Foundry portal. Use the **new Foundry** experience,
not Foundry (classic) or a classic hub-based project.

Deployment has two parts: use the portal to prepare the project and model, then
run the repository's Python registration command to create the six persistent
prompt agents. There is no Python source-folder upload step in this deployment
path. The registration command sends each agent's instructions and model reference
to Foundry; the Python workflow remains a client that runs where you execute it.

| Included After Registration | Not Deployed By These Steps |
|-----------------------------|-----------------------------|
| Six persistent prompt agents visible under Build > Agents. | A container-hosted Python agent or workflow service. |
| Agent instructions, output-schema guidance, and model deployment references. | Database ingestion, Azure Functions, or Service Bus integration. |
| Independently invocable specialist agents. | A manager approval UI, durable workflow store, or publishing service. |
| New agent versions when definitions are registered again. | Automatic execution of Python approval rules inside portal chats. |

For component responsibilities and dependencies, see
[Architecture.md](Architecture.md). For a shorter command reference, see
[SETUP.md](SETUP.md).

**Cost notice:** Creating Azure resources, deploying models, and invoking agents
can incur charges. Choose an approved subscription, region, deployment type, and
quota. The registration and verification commands do not perform model inference.

## Step 1: Prepare Accounts And Tools

Before starting, obtain the following:

| Requirement | How To Obtain Or Verify It |
|-------------|----------------------------|
| Azure subscription | Use an active subscription approved for this workload. |
| Microsoft Entra account | Use the account and tenant that have access to the target subscription and project. |
| Resource-creation permission | Ask your administrator for an appropriate Foundry resource-creation role if you need a new project. Existing-project users can skip resource creation. |
| Agent access | Ask an administrator for Foundry User access on the project. This was previously called Azure AI User. |
| Model-deployment permission | Ask a project/resource administrator to deploy the model if your role cannot manage deployments. |
| Python 3.11 or newer | Install from [Python downloads](https://www.python.org/downloads/). |
| uv | Follow the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/). |
| Azure CLI | Follow the [Azure CLI installation guide](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli). |
| Repository files | Obtain this repository and open its root folder in a terminal or VS Code. |
| Network access | Your machine must reach the Foundry project endpoint and Microsoft Entra sign-in services. Private projects require the organization's approved network access. |

Check the tools in your terminal:

```bash
python --version
uv --version
az version
```

On macOS/Linux, use `python3 --version` if `python` is not available before
activating a virtual environment. Do not continue until Python is at least 3.11.

**Expected result:** Tools are installed, and you know which Azure account,
subscription, and tenant to use. Installing tools does not grant Azure permissions.

## Step 2: Create Or Select A Foundry Project

If your administrator already supplied a new Foundry project, select that project
and continue to Step 3. Do not create a duplicate project.

To create a project through the portal:

1. Open [Microsoft Foundry](https://ai.azure.com) and sign in.
2. If a **New Foundry** toggle is shown, enable it.
3. Open the project selector in the upper-left corner and select **Create new project**.
4. Enter a project name, for example `customer-review-analyzer`.
5. Open **Advanced options** and select the intended subscription, resource group,
   Foundry resource options, and region as available in the form.
6. Choose a region that supports the required model and satisfies your organization's
   data-handling requirements. Do not assume every region supports the same models.
7. Review the selections, select **Create project**, and wait for creation to finish.
8. Confirm the new project is the active project in the selector.

Portal labels can change. If the screens differ, use Microsoft's
[resource setup quickstart](https://learn.microsoft.com/en-us/azure/foundry/tutorials/quickstart-create-foundry-resources)
for the current portal flow.

**Expected result:** A new Foundry project is available in the intended
subscription and resource group.

## Step 3: Grant Deployment Users Access

An administrator should complete this step for each user or team security group
that will register and invoke agents. Creating a project for yourself may already
grant the necessary access; verify rather than adding duplicate assignments.

1. In the selected Foundry project, open **Manage**.
2. Select **Project details**, then the **Users** tab.
3. Select **Add user** and add the intended team member or supported security group.
4. Confirm the identity has **Foundry User** permissions at project scope.
5. If project membership controls do not provide the required role, ask an Azure
   administrator to inspect the project's **Access control (IAM)** in the Azure
   portal and assign the appropriate role.
6. Ask the deployment user to sign in and select the project to confirm access.

Assigning roles requires separate authorization, such as Owner or Role Based
Access Control Administrator at the appropriate scope. Being able to view an
Azure resource does not necessarily grant agent data-plane access. Role changes
can take time to propagate. Sign in again if access remains stale.

See [Foundry role-based access control](https://learn.microsoft.com/en-us/azure/foundry/concepts/rbac-foundry)
for role names, scopes, and administrative permissions.

**Expected result:** The deployment user can access the project and has permission
to create, list, and invoke agents. An administrator can manage the model deployment.

## Step 4: Deploy Or Confirm The Azure OpenAI Model

The repository is configured to use the Azure deployment name `gpt-5.4-nano`.
Availability is not guaranteed in every subscription or region. Confirm support
for Foundry prompt agents, the Responses API, and structured outputs before use.

1. Select **Build** in the Foundry portal, then **Models** in the left navigation.
2. Check whether the intended deployment already exists. If it does, open it and
   record its exact deployment name; do not deploy a duplicate.
3. Otherwise select **Deploy > Deploy a base model**.
4. Search for the OpenAI model `gpt-5.4-nano`.
5. If the model is available to you, select it and open the deployment flow.
6. Review the model version, deployment type, region, quota/capacity, and applicable
   cost and data-residency settings. If the UI offers custom settings, use them to
   set the deployment name to `gpt-5.4-nano` when appropriate.
7. Complete deployment and wait until it is ready or shows a successful state.
8. Record the actual deployment name displayed by the portal.

**If the model is missing or deployment is blocked:** Stop and ask the Azure
administrator to check model availability, access, supported regions, and quota.
Do not assume that changing a deployment's name changes its underlying model.
Use another model only after the workload owner approves it, then update the
environment configuration to its actual deployment name.

The value used by the code is the **deployment name**, which may differ from the
model catalog name. Do not enter an OpenAI public API model identifier unless it
is also the actual Azure deployment name. This repository does not deploy models.

**Expected result:** A usable Azure OpenAI deployment exists for the selected
project, and its exact name is known.

## Step 5: Copy The Project Endpoint

1. Return to the selected project's welcome or overview screen.
2. Find the **project endpoint** and use its copy button.
3. Confirm that the endpoint has this form:

```text
https://YOUR-RESOURCE.services.ai.azure.com/api/projects/YOUR-PROJECT
```

Use the endpoint displayed for this project. Do not substitute the portal's
browser address, a resource ARM ID, a connection string, or an Azure OpenAI
endpoint ending in `/openai` or `.openai.azure.com`.

**Expected result:** You have the project endpoint and model deployment name
for the same target environment.

## Step 6: Install The Six Python Projects

Open a terminal in the repository root, the directory containing
[manage_agents.py](manage_agents.py), [pyproject.toml](pyproject.toml), and
[uv.lock](uv.lock).

On macOS/Linux, replace the example path with your checkout location:

```bash
cd /path/to/CustomerReviewAnalyzer
uv sync --all-packages --locked
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
Set-Location "C:\path\to\CustomerReviewAnalyzer"
uv sync --all-packages --locked
.\.venv\Scripts\Activate.ps1
```

If organizational PowerShell policy blocks activation, do not weaken that policy.
Instead, prefix the subsequent Python commands with `.\.venv\Scripts\python.exe`
and invoke agent executables from `.\.venv\Scripts\`.

The install command builds all six separately packaged agents and the shared core
package into one local workspace environment. It does not merge the projects or
deploy anything to Azure. No unit tests are created or required.

Verify the local commands load:

```bash
python manage_agents.py --help
sentiment-analysis-agent --help
review-orchestrator-agent --help
```

**Expected result:** Installation succeeds and the commands display help without
import errors. Keep the virtual environment activated for subsequent commands.

## Step 7: Configure The Environment File

Open the repository-root `.env`. If it does not exist in a fresh checkout, create
it using [the environment template](.env.example) without overwriting any existing
environment configuration.

Set the values as follows, replacing the endpoint and deployment name with the
values recorded in Steps 4 and 5:

```dotenv
FOUNDRY_PROJECT_ENDPOINT=https://YOUR-RESOURCE.services.ai.azure.com/api/projects/YOUR-PROJECT
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-5.4-nano
REVIEW_CONFIDENCE_THRESHOLD=0.80
FOUNDRY_AGENT_PREFIX=ulta
```

| Setting | Meaning |
|---------|---------|
| `FOUNDRY_PROJECT_ENDPOINT` | Project in which agents will be registered. |
| `AZURE_AI_MODEL_DEPLOYMENT_NAME` | Existing Azure model deployment referenced by the agents. |
| `REVIEW_CONFIDENCE_THRESHOLD` | Confidence below this value requires human review. Valid range: 0 to 1. |
| `FOUNDRY_AGENT_PREFIX` | Agent namespace. Use 1-30 lowercase letters, digits, or hyphens, beginning with a letter. |

Keep `.env` out of source control. API keys are not needed: this implementation
uses Microsoft Entra authentication through `DefaultAzureCredential`.

Existing process environment variables override the values in `.env`. If a
command targets an unexpected project or deployment, check inherited environment
variables and VS Code terminal settings before changing code. Use a dedicated
prefix or project for each environment to avoid updating another team's agents.

**Expected result:** Configuration points to the intended project and an existing
deployment; no placeholder values remain in the endpoint.

## Step 8: Authenticate The Deployment User

From the activated terminal:

```bash
az login
az account set --subscription "YOUR-SUBSCRIPTION-ID"
az account show --query "{subscription:name, subscriptionId:id, tenantId:tenantId}" --output json
```

Complete browser authentication using the same identity that has project access.
If your organization requires an explicit tenant, use:

```bash
az login --tenant "YOUR-TENANT-ID"
```

After tenant-specific sign-in, select the intended subscription again. Do not
put passwords, access tokens, or CLI credentials in `.env` or the repository.
If other credentials are configured on the machine, `DefaultAzureCredential`
may select them before Azure CLI credentials; investigate identity mismatches
with your administrator rather than exposing secrets.

**Expected result:** Azure CLI shows the intended subscription and tenant, and
the selected identity has Foundry project access. Subscription selection does
not change the endpoint in `.env`; both must be correct.

## Step 9: Register All Six Agents

Run the following from the repository root with the virtual environment active:

```bash
python manage_agents.py register
```

The command reads each agent definition and calls Foundry's versioned agent API.
It registers the prompts, schema guidance, configured threshold, and model
deployment reference. It does not execute the review workflow.

The default names are:

| Agent | Registered Name With Prefix `ulta` |
|-------|------------------------------------|
| Review Orchestrator | `ulta-review-orchestrator` |
| Sentiment Analysis | `ulta-sentiment-analysis` |
| Review Summarization | `ulta-review-summarization` |
| Personalized Response | `ulta-personalized-response` |
| Brand Compliance | `ulta-brand-compliance` |
| Human Approval | `ulta-human-approval` |

For each successful registration, the command prints a JSON line in this shape:

```json
{"id": "<returned-agent-id>", "name": "ulta-sentiment-analysis", "version": "<returned-version>"}
```

**Expected result:** Six successful registration records are printed and the
command exits successfully. Record the returned names and versions for your
deployment record. Example identifiers above are placeholders, not real results.

Registration creates a new version even if a name already exists. Do not repeat
registration merely to check visibility. If registration fails partway through,
previously created versions remain. After fixing the cause, register only the
missing or affected agent, for example:

```bash
python manage_agents.py register --agent sentiment-analysis
```

For a separate environment file:

```bash
python manage_agents.py register --env /path/to/target.env
```

Use an operating-system-appropriate path. Do not supply `register` again during
normal agent invocation.

## Step 10: Verify Registration And Portal Visibility

First check remote name presence:

```bash
python manage_agents.py verify
```

The command must print `"exists": true` for all six names and exit successfully.
If using a separate configuration file in Step 9, pass the same `--env` here.

Then verify in the portal:

1. Open [Microsoft Foundry](https://ai.azure.com).
2. Select the exact project identified by `FOUNDRY_PROJECT_ENDPOINT`.
3. Select **Build**, then **Agents** in the left navigation.
4. Refresh the list and search for the configured prefix, normally `ulta-`.
5. Open each of the six agents and inspect its instructions, model reference,
   and available version information.
6. Confirm the model deployment matches the deployment selected in Step 4.

You do not need to create six additional empty agents manually in the portal.
The SDK registration has already created the persistent definitions. This
registration path does not require a separate container deployment or application
publishing step simply to list and invoke the agents within the project.

**Expected result:** All six registered agents are visible in the same project's
**Build > Agents** list. The CLI name check alone does not prove that model
inference works or that a pre-existing definition matches the current source.

## Step 11: Perform A Manual Invocation Check

Invocations incur model usage charges. Use only non-sensitive sample data.

From the repository root, run one specialist against the supplied sample review:

```bash
sentiment-analysis-agent run --input examples/review.json
```

**Expected result:** Structured JSON contains sentiment, confidence, detected
issues, and toxicity, legal-complaint, and safety flags. Exact model output may
vary. A refusal, incomplete result, or API error must be investigated rather than
treated as a successful inference check.

Optionally open `ulta-sentiment-analysis` in the portal playground and submit the
JSON contents of [the sample review](examples/review.json) as the message. This
checks an individual remote agent, not the full Python workflow or its approval
rules. Other specialists require their own structured input contracts; see
[models.py](packages/foundry-review-core/src/foundry_review_core/models.py).

## Step 12: Run The Complete Review Workflow

To invoke all six remote agents in sequence and apply local approval rules:

```bash
review-orchestrator-agent process --input examples/review.json
```

The command returns the processing context, completed stages, sentiment, summary,
draft response, compliance decision, approval routing, and business message.
The supplied sample describes a negative experience and skin irritation; inspect
the output for `PendingHumanApproval`. Model classification is probabilistic,
so do not treat a successful API response alone as business-policy acceptance.

The deterministic policy requires human review for detected negative sentiment,
toxicity, legal complaints, safety concerns, trusted VIP status, low confidence,
compliance failures/issues, or an agent escalation. It cannot compensate for all
semantic issues that a model fails to detect.

**Important:** `review-orchestrator-agent run` and a portal chat with the
orchestrator only initialize context. They do not run the complete workflow.
The `process` command runs Python coordination and approval enforcement on the
machine where it is executed. Closing that client does not delete remote agent
definitions, but there is no continuously running workflow service after it exits.

This step does not enqueue, publish, or obtain a manager's decision. Do not send
a `PendingHumanApproval` message to publishing without a genuine authenticated
human approval process.

## Updating An Existing Deployment

1. Update the appropriate source definition or environment configuration.
2. If dependency metadata changed, regenerate and review the lockfile through
   your development process; deploy using `uv sync --all-packages --locked`.
3. Authenticate to the intended environment and confirm its endpoint and prefix.
4. Register the affected agent using `--agent`, or register all six for a
   coordinated change. Re-register after changing prompts, deployment references,
   or threshold guidance embedded in instructions.
5. Run `verify`, inspect the new versions in the portal, and perform an approved
   manual invocation check.

Invocations use names without pinning immutable versions. They therefore resolve
the latest registered versions, and an in-flight workflow is not guaranteed to
use a single coordinated release if versions are changed during processing.
Avoid updating production definitions during active processing. Use separate
projects or prefixes for development and production and plan controlled promotion.

Changing only the model name in `.env` does not update previously registered
agent definitions. Changing the prefix creates or targets a different set of
agent names; it does not rename or delete the old set.

## Troubleshooting

| Symptom | Check And Resolution |
|---------|----------------------|
| `Set FOUNDRY_PROJECT_ENDPOINT...` | Fill the root `.env` with the project endpoint containing `/api/projects/`, not the portal URL or an OpenAI model endpoint. |
| Agent not visible in portal | Compare the active project's endpoint and prefix with the registration configuration, refresh Build > Agents, and run `verify`. Do not use Agents (classic). |
| `verify` succeeds but model calls fail | Name presence is not an inference check. Confirm model availability, deployment reference, identity permissions, and API support. |
| Authentication or `401` error | Sign in to the correct tenant again and check whether another credential source is taking precedence. |
| Authorization or `403` error | Ask an administrator to verify project data-plane permissions, role scope, identity, propagation, and any network restrictions. |
| Model missing, `404`, or deployment-not-found | Match the exact Azure deployment name and ensure it is accessible to this project; re-register definitions after correcting it. |
| Quota exhausted or `429` | Check deployment quota and capacity; reduce invocation concurrency or request capacity through your administrator. |
| Structured output unsupported | Confirm that the deployed model/version and endpoint support Responses API structured outputs; do not bypass validation to force processing. |
| Imports fail or a CLI is not found | Run `uv sync --all-packages --locked` from the repository root and use its `.venv`. |
| Lockfile is out of date | Reconcile source and lockfile in development and review the result; do not silently bypass locked installation in deployment. |
| Registration stopped after some agents | Successful registrations remain. Correct the failure, use `verify` to identify missing names, and register only affected roles. |
| `.env` changes seem ignored | Check existing process environment values, the working directory, and the `--env` file. Previously registered model references also require re-registration. |
| Timeout, DNS, or private-endpoint error | Use the approved network/VPN and ask the network administrator to verify DNS and Foundry endpoint reachability. |
| Portal orchestrator chat does not call specialists | Expected behavior: coordination is Python code. Run the orchestrator's `process` command. |
| Approval output exists but nothing is published | Expected boundary: Service Bus delivery, manager approval, and publishing are not implemented here. |

## Deployment Completion Checklist

- [ ] The intended new Foundry project is selected in the correct subscription and tenant.
- [ ] Deployment users have project access; an administrator can manage model deployments.
- [ ] The approved model deployment is ready and its actual name is recorded.
- [ ] All six Python projects and shared core are installed from the lockfile.
- [ ] Environment configuration contains the correct endpoint, deployment, prefix, and threshold.
- [ ] Registration returned six successful records; names and versions are recorded.
- [ ] `verify` reports all six agents present.
- [ ] All six definitions are visible under Build > Agents with the expected model references.
- [ ] A permitted manual specialist invocation succeeds.
- [ ] The complete Python workflow has been checked with non-sensitive sample data.
- [ ] Reviewers understand that registration is not deployment of the broader business platform.

## Production Handoff And Cleanup

For unattended operation, separately host the Python client/workflow on an approved
compute service and configure managed identity, project access, secure settings,
observability, retries, durable checkpoints, and duplicate prevention. Connect
ingestion, approval, messaging, and publishing integrations explicitly. These
changes are beyond this registration guide and are not performed by its commands.

Stopping the local client does not remove agents or the model deployment. To
retire a non-production deployment, review the affected agent names and versions
in Foundry and use the portal's available delete controls only for resources
you own and no longer need. Coordinate model deletion because deployments may
be shared. Delete an entire Azure resource group only after confirming that no
other workload depends on any resource within it.

## References

- [Microsoft Foundry resource and model setup](https://learn.microsoft.com/en-us/azure/foundry/tutorials/quickstart-create-foundry-resources).
- [Microsoft Foundry SDK quickstart](https://learn.microsoft.com/en-us/azure/foundry/quickstarts/get-started-code).
- [Microsoft Foundry role-based access control](https://learn.microsoft.com/en-us/azure/foundry/concepts/rbac-foundry).
- [Repository architecture](Architecture.md).
- [Repository setup reference](SETUP.md).

Portal instructions were checked against Microsoft documentation on October 20,
2026. Actual screens, model availability, and permitted actions can differ by
tenant, region, rollout, and assigned role. This guide does not assert that a
live deployment has already been performed.