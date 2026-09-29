# Edge Agents AI on Amazon Bedrock AgentCore Payments

A Strands agent that finds a relevant Edge Agents AI service and pays for it over x402, using AgentCore Payments for the wallet and the spending limit. The agent never handles keys, and the session budget is enforced by AWS, not by the agent.

## Before you start

1. An AWS account in a region where AgentCore Payments is available, with Bedrock model access.
2. Complete AWS's [Tutorial 00](https://github.com/awslabs/agentcore-samples/tree/main/01-features/08-agents-that-transact/00-getting-started/00-setup-agentcore-payments). It gives you a payment manager ARN, a wallet (payment instrument) and a user ID, and walks through granting the agent signing rights on the wallet.
3. Fund that wallet with a small amount of mainnet USDC on Base (or Solana or Arbitrum). Our endpoints do not run on testnets.

## Run it

```
pip install -r requirements.txt
cp .env.example .env    # then fill in the values from Tutorial 00
python edge_agents_agent.py "What is the current signal across crypto and macro?"
```

The agent reads the free catalogue at `/v1/services`, picks a service, calls it, and reports what it bought and what it cost. The default session budget is $0.50 and expires after 30 minutes, so a runaway loop may cost at most that.

## What happens under the hood

1. The agent calls, for example, `GET https://pay.edge-agents.ai/v1/services/edge-signal-snapshot`.
2. The server replies 402 with a `Payment-Required` header listing five rails.
3. The AgentCore Payments plugin picks a rail your wallet supports, checks the budget, signs a USDC payment and retries with a `PAYMENT-SIGNATURE` header.
4. The server verifies the payment and returns the report.

Each payment shows up in CloudWatch under `/aws/vendedlogs/bedrock-agentcore/<payment-manager-id>`.

## Status

This is based on AWS's own Strands payment sample and version 1.24 of the `bedrock-agentcore` SDK, which we checked handles x402 version 2 and our rails. It has not yet been run end to end against production, so please raise an issue if anything does not work.
