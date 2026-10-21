import argparse
import json
from pathlib import Path
import sys

from azure.core.exceptions import AzureError
from openai import OpenAIError
from pydantic import BaseModel

from foundry_review_core.models import ApprovalInput, ApprovalResult
from foundry_review_core.policy import enforce_approval_policy
from foundry_review_core.runtime import AgentSpec, FoundryRuntime, Settings


def agent_cli(spec: AgentSpec, input_model: type[BaseModel]) -> None:
    parser = argparse.ArgumentParser(description=f"Register or invoke the {spec.role} Foundry agent.")
    parser.add_argument("command", choices=["register", "run"])
    parser.add_argument("--env", type=Path, help="Path to a .env file; otherwise search from the current directory upward.")
    parser.add_argument("--input", type=Path, help="JSON input file; otherwise read JSON from stdin.")
    args = parser.parse_args()
    try:
        settings = Settings.load(args.env)
        with FoundryRuntime(settings) as runtime:
            if args.command == "register":
                result = runtime.register(spec)
            else:
                raw = args.input.read_text(encoding="utf-8") if args.input else sys.stdin.read()
                payload = input_model.model_validate_json(raw)
                output = runtime.invoke(spec.role, payload, spec.output_model)
                if isinstance(payload, ApprovalInput) and isinstance(output, ApprovalResult):
                    output = enforce_approval_policy(payload, output, settings.confidence_threshold)
                result = output.model_dump(mode="json")
            print(json.dumps(result, indent=2))
    except (ValueError, RuntimeError, OSError, AzureError, OpenAIError) as error:
        print(f"{spec.role}: {error}", file=sys.stderr)
        raise SystemExit(1) from error