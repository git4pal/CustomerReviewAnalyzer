from foundry_review_core.cli import agent_cli
from foundry_review_core.models import ProcessingContext, Review
from foundry_review_core.runtime import AgentSpec


SPEC = AgentSpec(
    role="review-orchestrator",
    output_model=ProcessingContext,
    instructions="""You are Ulta Beauty's Review Orchestrator Agent.
Receive an incoming product review and its metadata. Initialize a processing
context using the exact reviewId and productId supplied. Set workflowStatus to
Received. Record concise factual contextNotes about missing or relevant context
without PII. The Python workflow invokes sentiment analysis, summarization,
response generation, brand compliance, and human-approval routing in that order.
You do not have tools to invoke those agents in a portal chat; never claim to
have called them or completed their work. Never invent findings, approve a
sensitive review, or claim publishing has occurred.
""",
)


def main() -> None:
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "process":
        from review_orchestrator_agent.workflow import workflow_cli

        workflow_cli()
    else:
        agent_cli(SPEC, Review)