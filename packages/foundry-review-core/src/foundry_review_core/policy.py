from foundry_review_core.models import ApprovalInput, ApprovalResult


def enforce_approval_policy(
    context: ApprovalInput, proposed: ApprovalResult, confidence_threshold: float
) -> ApprovalResult:
    reasons = list(proposed.reasons)
    if context.sentiment.sentiment == "Negative":
        reasons.append("Negative review")
    if context.review.isVip:
        reasons.append("VIP customer")
    if context.sentiment.toxicContent:
        reasons.append("Toxic content")
    if context.sentiment.legalComplaint:
        reasons.append("Legal complaint")
    if context.sentiment.safetyConcern:
        reasons.append("Product safety concern")
    if min(context.sentiment.confidence, context.response.confidence) < confidence_threshold:
        reasons.append("Low confidence")
    if not context.compliance.passed or context.compliance.issues:
        reasons.append("Brand compliance requires review")
    if proposed.humanApprovalRequired or proposed.approvalStatus == "PendingHumanApproval":
        reasons.append("Human approval agent requested review")
    required = bool(reasons)
    return ApprovalResult(
        humanApprovalRequired=required,
        approvalStatus="PendingHumanApproval" if required else "Approved",
        reasons=list(dict.fromkeys(reasons)),
    )