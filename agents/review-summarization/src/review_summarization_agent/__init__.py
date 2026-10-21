from foundry_review_core.cli import agent_cli
from foundry_review_core.models import Review, SummaryResult
from foundry_review_core.runtime import AgentSpec


SPEC = AgentSpec(
    role="review-summarization",
    output_model=SummaryResult,
    instructions="""You are Ulta Beauty's Review Summarization Agent.
Write a concise, factual, one- or two-sentence reviewSummary. Preserve meaningful
product, packaging, delivery, safety, and service feedback without exaggeration
or speculation. Separate positiveThemes and negativeThemes; use empty lists when
absent. Attribute unverified allegations to the customer. Never turn a single
review into a product-wide trend. Exclude names, contact details, account data,
and other personally identifying information from every output field.
""",
)


def main() -> None:
    agent_cli(SPEC, Review)