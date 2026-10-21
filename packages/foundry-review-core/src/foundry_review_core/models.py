from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Review(Contract):
    reviewId: str = Field(min_length=1)
    productId: str = Field(min_length=1)
    reviewText: str = Field(min_length=1, max_length=50000)
    productMetadata: dict = Field(default_factory=dict)
    customerMetadata: dict = Field(default_factory=dict)
    isVip: bool = False


class ProcessingContext(Contract):
    reviewId: str
    productId: str
    workflowStatus: Literal["Received"]
    contextNotes: list[str]


class SentimentResult(Contract):
    sentiment: Literal["Positive", "Neutral", "Negative"]
    confidence: float = Field(ge=0, le=1)
    detectedIssues: list[str]
    toxicContent: bool
    legalComplaint: bool
    safetyConcern: bool


class SummaryResult(Contract):
    reviewSummary: str = Field(min_length=1)
    positiveThemes: list[str]
    negativeThemes: list[str]


class ResponseInput(Contract):
    review: Review
    sentiment: SentimentResult
    summary: SummaryResult


class ResponseResult(Contract):
    generatedResponse: str = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)


class ComplianceInput(ResponseInput):
    response: ResponseResult


class ComplianceResult(Contract):
    passed: bool
    issues: list[str]
    explanation: str


class ApprovalInput(Contract):
    review: Review
    sentiment: SentimentResult
    response: ResponseResult
    compliance: ComplianceResult


class ApprovalResult(Contract):
    humanApprovalRequired: bool
    approvalStatus: Literal["Approved", "PendingHumanApproval"]
    reasons: list[str]


class ProcessingResult(Contract):
    processingContext: ProcessingContext
    sentimentAnalysis: SentimentResult
    summary: SummaryResult
    response: ResponseResult
    compliance: ComplianceResult
    approval: ApprovalResult
    workflowStatus: Literal["ReadyForPublishing", "PendingHumanApproval"]
    destination: Literal["Publishing", "HumanApproval"]
    completedStages: list[str]
    message: dict