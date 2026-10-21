# Ulta Beauty Agentic AI Review Response Platform

Python implementation and setup: [SETUP.md](SETUP.md). Each of the six agents is
a separate Python project under `agents/`, with persistent Microsoft Foundry
registration and an environment-configured Azure OpenAI deployment.

## Overview

The Ulta Beauty Agentic AI Review Response Platform is an intelligent, scalable solution built on **Microsoft Azure AI Foundry** that automatically analyzes customer product reviews, generates personalized brand responses, and ensures appropriate human oversight for sensitive customer interactions.

The solution addresses two key business challenges:

- **Customer Retention** by acknowledging every customer review and responding appropriately to negative feedback.
- **Operational Scalability** by automating review analysis and response generation for thousands of product reviews.

Using a multi-agent architecture, the platform processes product reviews from an enterprise database, performs sentiment analysis, generates review summaries, creates personalized responses, and routes reviews through automated or human-approved publishing workflows.

---

# Business Objectives

## Customer Engagement

Ensure every customer review receives an acknowledgment, creating a stronger connection between the customer and the Ulta Beauty brand.

## Customer Retention

Identify and prioritize negative customer experiences to prevent churn and improve brand loyalty.

## Actionable Insights

Generate product-level review summaries and sentiment trends that help product teams identify opportunities for improvement.

## Operational Efficiency

Enable automated handling of large review volumes without increasing customer service staffing requirements.

---

# High-Level Solution Architecture

```text
Enterprise Review Database
        │
        ▼
Review Ingestion Service
        │
        ▼
Azure AI Foundry Project
        │
        ├── Review Orchestrator Agent
        ├── Sentiment Analysis Agent
        ├── Review Summarization Agent
        ├── Personalized Response Agent
        ├── Brand Compliance Agent
        └── Human Approval Agent
        │
        ▼
Decision Engine
        │
 ┌──────┴───────────┐
 │                  │
 ▼                  ▼
Positive          Negative
Review            Review
 │                  │
 ▼                  ▼
Azure         Human Approval
Service Bus       Workflow
 │                  │
 └──────┬───────────┘
        ▼
Azure Service Bus
        ▼
Review Publishing Microservice
        ▼
Ulta Beauty Review Platform
```

---

# Agent Design

## 1. Review Orchestrator Agent

### Responsibilities

- Receive incoming reviews
- Coordinate execution of specialized agents
- Manage workflow state
- Route reviews to appropriate approval paths

### Inputs

- Product Review
- Product Metadata
- Customer Metadata

### Outputs

- Processing Context
- Workflow Status

---

## 2. Sentiment Analysis Agent

### Responsibilities

Classify review sentiment into:

- Positive
- Neutral
- Negative

### Generated Information

```json
{
  "sentiment": "Negative",
  "confidence": 0.94,
  "detectedIssues": [
    "Product Packaging",
    "Skin Irritation"
  ]
}
```

### Business Usage

- Determine approval routing
- Prioritize escalations
- Generate customer service metrics

---

## 3. Review Summarization Agent

### Responsibilities

Generate concise summaries of customer feedback.

### Example

**Customer Review**

> The product arrived leaking and caused skin irritation. Customer service was difficult to reach.

**AI Summary**

> Customer experienced packaging leakage and product irritation concerns, resulting in a poor experience.

### Business Usage

- Product insights
- Review analytics
- Executive dashboards

---

## 4. Personalized Response Agent

### Responsibilities

Generate customer-specific responses aligned with:

- Ulta brand voice
- Customer sentiment
- Product category
- Review context

### Positive Example

> Thank you for sharing your experience. We're thrilled that you enjoyed the product and appreciate your feedback.

### Negative Example

> Thank you for bringing this issue to our attention. We're sorry your experience did not meet expectations and appreciate the opportunity to improve.

---

## 5. Brand Compliance Agent

### Responsibilities

Validate generated responses against:

- Brand guidelines
- Compliance requirements
- Tone consistency
- Safety policies

### Validation Checks

- Offensive Language
- Hallucinations
- Legal Claims
- Product Claims
- PII Exposure

---

## 6. Human Approval Agent

### Responsibilities

Route sensitive responses for customer service manager review.

### Approval Triggers

| Condition | Human Approval Required |
|-----------|------------------------|
| Positive Review | No |
| Neutral Review | No |
| Negative Review | Yes |
| Toxic Content | Yes |
| Legal Complaints | Yes |
| VIP Customer | Yes |
| Low Confidence Response | Yes |

---

# Review Processing Workflow

## Step 1 - Fetch Reviews

A scheduled ingestion process retrieves reviews from the enterprise review database.

## Step 2 - Agent Processing

The Review Orchestrator sends the review to:

1. Sentiment Analysis Agent
2. Summarization Agent
3. Response Generation Agent
4. Compliance Agent

## Step 3 - Sentiment Decision

### Positive/Neutral Reviews

Generated response is automatically approved.

```text
AI Response
    │
    ▼
Azure Service Bus
    │
    ▼
Publishing Service
    │
    ▼
Review Platform
```

### Negative Reviews

Generated response requires manager approval.

```text
AI Response
    │
    ▼
Human Approval Queue
    │
Approved?
    │
    ▼
Azure Service Bus
    │
    ▼
Publishing Service
    │
    ▼
Review Platform
```

---

# Azure Components

## Data Layer

### Enterprise Review Database

Supported Sources:

- Azure SQL Database
- Azure Cosmos DB
- SQL Server
- PostgreSQL

---

## Integration Layer

### Azure Functions

Responsibilities:

- Poll review database
- Invoke Azure AI Foundry agents
- Publish events

### Azure Service Bus

Used for:

- Decoupled processing
- Event-driven communication
- Scalable downstream integration

---

## AI Layer

### Azure AI Foundry Project

Hosts:

- Agent Definitions
- Prompt Templates
- Evaluation Pipelines
- Observability
- Agent Tracing

### Azure OpenAI Models

Recommended Models:

- GPT-4o
- GPT-5

Used For:

- Sentiment Analysis
- Summarization
- Response Generation

---

## Human Approval Layer

### Approval Portal

Options:

- Power Apps
- Custom React UI
- Internal Employee Portal

Manager Actions:

- Approve
- Reject
- Edit
- Escalate

---

## Publishing Layer

### Review Publisher Microservice

Responsibilities:

- Subscribe to Service Bus Topics
- Process approved responses
- Call Ulta Review API
- Update review status

---

# Azure Service Bus Message Schema

```json
{
  "reviewId": "RVW-12345",
  "productId": "PRD-5001",
  "sentiment": "Positive",
  "reviewSummary": "Customer loved the product results.",
  "generatedResponse": "Thank you for sharing your experience.",
  "approvalStatus": "Approved",
  "createdTimestamp": "2026-10-20T15:00:00Z"
}
```

---

# Non-Functional Requirements

## Scalability

- Process millions of reviews annually
- Support horizontal scaling

## Reliability

- Message durability via Service Bus
- Retry capabilities
- Dead-letter queues

## Security

- Managed Identity
- Key Vault
- RBAC
- Private Endpoints

## Observability

- Application Insights
- Azure Monitor
- Foundry Tracing
- Agent Execution Logs

---

# Monitoring Metrics

## AI Metrics

- Sentiment Accuracy
- Response Quality
- Hallucination Rate
- Approval Rate

## Business Metrics

- Customer Engagement Rate
- Review Response Rate
- Negative Review Recovery Rate
- Customer Retention Impact

## Operational Metrics

- Processing Time
- Queue Length
- Service Bus Throughput
- Agent Failure Rate

---

# Future Enhancements

- Multilingual review support
- Voice of Customer analytics
- Product issue clustering
- Trend detection
- Auto-ticket creation in CRM
- Customer loyalty integration
- Root cause analysis dashboards
- Agent-to-Agent collaborative workflows

---

# Expected Business Benefits

| Benefit | Outcome |
|----------|----------|
| Improved Customer Experience | Every review receives acknowledgment |
| Higher Customer Retention | Faster response to negative feedback |
| Operational Efficiency | Reduced manual workload |
| Product Improvements | Actionable review insights |
| Brand Consistency | AI-generated compliant responses |
| Scalability | Supports high review volumes |

---

# Technology Stack

- Azure AI Foundry
- Azure OpenAI (GPT-4o / GPT-5)
- Azure Functions
- Azure Service Bus
- Azure SQL Database / Cosmos DB
- Azure Key Vault
- Azure Monitor
- Application Insights
- Power Apps (Approval Workflow)
- React-based Approval Portal
- Event-Driven Microservices