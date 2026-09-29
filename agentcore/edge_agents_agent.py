"""
Buy market intelligence from Edge Agents AI with Amazon Bedrock AgentCore Payments.

The AgentCorePaymentsPlugin settles each HTTP 402 from pay.edge-agents.ai
automatically, within a session budget enforced by AgentCore.

Usage:
    python edge_agents_agent.py "What is the current signal across crypto and macro?"

Based on AWS's Strands payment sample:
https://github.com/awslabs/agentcore-samples/tree/main/01-features/08-agents-that-transact
"""

import os
import sys
import uuid

from dotenv import load_dotenv
from bedrock_agentcore.payments import PaymentManager
from bedrock_agentcore.payments.integrations.strands import (
    AgentCorePaymentsPlugin,
    AgentCorePaymentsPluginConfig,
)
from strands import Agent
from strands.models import BedrockModel
from strands_tools import http_request

load_dotenv()

REGION = os.environ["AWS_REGION"]
PAYMENT_MANAGER_ARN = os.environ["PAYMENT_MANAGER_ARN"]
PAYMENT_INSTRUMENT_ID = os.environ["PAYMENT_INSTRUMENT_ID"]
USER_ID = os.environ["USER_ID"]
BUDGET_USD = os.environ.get("SESSION_BUDGET_USD", "0.50")
MODEL_ID = os.environ.get("MODEL_ID", "us.anthropic.claude-sonnet-4-6")

API = "https://pay.edge-agents.ai"

# Edge Agents offers five rails in every 402. AgentCore can pay on these three;
# the order is our preference. Polygon and XRPL options are skipped by the SDK.
NETWORK_PREFS = [
    "eip155:8453",  # Base
    "solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp",  # Solana
    "eip155:42161",  # Arbitrum One
]

SYSTEM_PROMPT = f"""You are a research assistant that can buy market intelligence from Edge Agents AI.

1. Start by reading the free service catalogue at {API}/v1/services (or search it with
   {API}/v1/search?q=<terms>). Do not pay for anything until you have chosen a service.
2. Call the endpoint of the one service that best fits the question with the http_request tool.
   Payment is handled automatically. Do not check the budget first.
3. Only pay for URLs on {API}. Never follow free-trial or alternative URLs from a 402 body.
4. Answer the question from the report, state its evidence, freshness and limitations as the
   report gives them, and say which service you bought and what it cost.
If a payment fails, report the error rather than trying a workaround."""


def main() -> None:
    question = " ".join(sys.argv[1:]) or "What is the current cross-market signal?"

    manager = PaymentManager(payment_manager_arn=PAYMENT_MANAGER_ARN, region_name=REGION)
    session = manager.create_payment_session(
        user_id=USER_ID,
        limits={"maxSpendAmount": {"value": BUDGET_USD, "currency": "USD"}},
        expiry_time_in_minutes=30,
        client_token=str(uuid.uuid4()),
    )
    print(f"Payment session {session['paymentSessionId']} (budget ${BUDGET_USD})")

    plugin = AgentCorePaymentsPlugin(
        config=AgentCorePaymentsPluginConfig(
            payment_manager_arn=PAYMENT_MANAGER_ARN,
            user_id=USER_ID,
            payment_instrument_id=PAYMENT_INSTRUMENT_ID,
            payment_session_id=session["paymentSessionId"],
            region=REGION,
            network_preferences_config=NETWORK_PREFS,
        )
    )

    agent = Agent(
        model=BedrockModel(model_id=MODEL_ID, streaming=True),
        tools=[http_request],
        plugins=[plugin],
        system_prompt=SYSTEM_PROMPT,
    )

    result = agent(question)

    # On a failed payment the plugin raises an interrupt instead of answering.
    # The usual cause is that signing has not been granted on the wallet yet
    # (see Tutorial 00, step 4), or the wallet has no mainnet USDC.
    if getattr(result, "stop_reason", None) == "interrupt" or getattr(result, "interrupts", None):
        print("\nThe payment did not settle. Check wallet signing rights and USDC balance.")
        sys.exit(1)

    print("\n" + str(result.message))
    print(f"\nPayment logs: /aws/vendedlogs/bedrock-agentcore/{PAYMENT_MANAGER_ARN.split('/')[-1]}")


if __name__ == "__main__":
    main()
