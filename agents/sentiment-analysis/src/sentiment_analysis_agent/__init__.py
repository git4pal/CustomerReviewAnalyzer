from foundry_review_core.cli import agent_cli
from foundry_review_core.models import Review, SentimentResult
from foundry_review_core.runtime import AgentSpec


SPEC = AgentSpec(
    role="sentiment-analysis",
    output_model=SentimentResult,
    instructions="""You are Ulta Beauty's Sentiment Analysis Agent.
Classify the supplied review as Positive, Neutral, or Negative based on the entire
review, not just its rating or isolated words. Report a calibrated confidence from
0 to 1 and specific detectedIssues grounded in the text. Flag toxicContent,
legalComplaint, and safetyConcern independently of sentiment. Irritation,
injury, allergic reactions, or potential unsafe use are safety concerns.
Ambiguity, sarcasm, mixed sentiment, or missing context should reduce confidence.
Do not repeat personal information or offensive quotations in detectedIssues.
""",
)


def main() -> None:
    agent_cli(SPEC, Review)