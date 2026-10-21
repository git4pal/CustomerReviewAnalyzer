import argparse
from importlib import import_module
import json
from pathlib import Path
import sys

from azure.core.exceptions import AzureError
from openai import OpenAIError

from foundry_review_core.runtime import FoundryRuntime, Settings


AGENTS = {
    "review-orchestrator": "review_orchestrator_agent",
    "sentiment-analysis": "sentiment_analysis_agent",
    "review-summarization": "review_summarization_agent",
    "personalized-response": "personalized_response_agent",
    "brand-compliance": "brand_compliance_agent",
    "human-approval": "human_approval_agent",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Register or verify persistent Microsoft Foundry agents.")
    parser.add_argument("command", choices=["register", "verify"])
    parser.add_argument("--agent", choices=list(AGENTS), help="Omit to select all six agents.")
    parser.add_argument("--env", type=Path, default=Path(__file__).resolve().parent / ".env")
    args = parser.parse_args()
    roles = [args.agent] if args.agent else list(AGENTS)
    try:
        settings = Settings.load(args.env)
        with FoundryRuntime(settings) as runtime:
            if args.command == "register":
                for role in roles:
                    spec = import_module(AGENTS[role]).SPEC
                    print(json.dumps(runtime.register(spec)), flush=True)
            else:
                names = {agent.name for agent in runtime.project.agents.list()}
                missing = []
                for role in roles:
                    name = settings.agent_name(role)
                    exists = name in names
                    print(json.dumps({"name": name, "exists": exists}))
                    if not exists:
                        missing.append(name)
                if missing:
                    raise RuntimeError(f"Agents not found in this Foundry project: {', '.join(missing)}")
    except (ValueError, RuntimeError, OSError, AzureError, OpenAIError) as error:
        print(f"Foundry operation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()