import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from azure.core.exceptions import AzureError
from openai import OpenAIError

from foundry_review_core.models import (
    ApprovalInput,
    ApprovalResult,
    ComplianceInput,
    ComplianceResult,
    ProcessingContext,
    ProcessingResult,
    ResponseInput,
    ResponseResult,
    Review,
    SentimentResult,
    SummaryResult,
)
from foundry_review_core.policy import enforce_approval_policy
from foundry_review_core.runtime import FoundryRuntime, Settings


def process_review(runtime: FoundryRuntime, review: Review) -> ProcessingResult:
    context = runtime.invoke("review-orchestrator", review, ProcessingContext)
    if context.reviewId != review.reviewId or context.productId != review.productId:
        raise RuntimeError("Orchestrator changed review identity; processing stopped.")
    sentiment = runtime.invoke("sentiment-analysis", review, SentimentResult)
    summary = runtime.invoke("review-summarization", review, SummaryResult)
    response_input = ResponseInput(review=review, sentiment=sentiment, summary=summary)
    response = runtime.invoke("personalized-response", response_input, ResponseResult)
    compliance_input = ComplianceInput(**response_input.model_dump(), response=response)
    compliance = runtime.invoke("brand-compliance", compliance_input, ComplianceResult)
    approval_input = ApprovalInput(
        review=review, sentiment=sentiment, response=response, compliance=compliance
    )
    proposed = runtime.invoke(
        "human-approval",
        approval_input,
        ApprovalResult,
    )
    approval = enforce_approval_policy(approval_input, proposed, runtime.settings.confidence_threshold)
    pending = approval.humanApprovalRequired
    return ProcessingResult(
        processingContext=context,
        sentimentAnalysis=sentiment,
        summary=summary,
        response=response,
        compliance=compliance,
        approval=approval,
        workflowStatus="PendingHumanApproval" if pending else "ReadyForPublishing",
        destination="HumanApproval" if pending else "Publishing",
        completedStages=[
            "review-orchestrator", "sentiment-analysis", "review-summarization",
            "personalized-response", "brand-compliance", "human-approval",
        ],
        message={
            "reviewId": review.reviewId,
            "productId": review.productId,
            "sentiment": sentiment.sentiment,
            "reviewSummary": summary.reviewSummary,
            "generatedResponse": response.generatedResponse,
            "approvalStatus": approval.approvalStatus,
            "createdTimestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


def workflow_cli() -> None:
    parser = argparse.ArgumentParser(description="Process one review through all six registered Foundry agents.")
    parser.add_argument("command", choices=["process"])
    parser.add_argument("--env", type=Path)
    parser.add_argument("--input", type=Path)
    args = parser.parse_args()
    try:
        settings = Settings.load(args.env)
        raw = args.input.read_text(encoding="utf-8") if args.input else sys.stdin.read()
        review = Review.model_validate_json(raw)
        with FoundryRuntime(settings) as runtime:
            result = process_review(runtime, review)
        print(result.model_dump_json(indent=2))
    except (ValueError, RuntimeError, OSError, AzureError, OpenAIError) as error:
        print(f"Review processing stopped: {error}", file=sys.stderr)
        raise SystemExit(1) from error