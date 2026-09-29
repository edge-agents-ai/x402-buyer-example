# Edge Agents AI: x402 buyer examples

Working examples of an AI agent buying market intelligence from [Edge Agents AI](https://edge-agents.ai) over x402. No account, API key or subscription is needed. The agent calls an endpoint, receives an HTTP 402 with payment terms, pays in USDC and gets the report back in the same exchange.

- API: `https://pay.edge-agents.ai`
- x402 manifest: `https://pay.edge-agents.ai/.well-known/x402`
- OpenAPI: `https://pay.edge-agents.ai/openapi.json`
- Service catalogue (free to read): `https://pay.edge-agents.ai/v1/services`
- Summary for models: `https://pay.edge-agents.ai/llms.txt`

The catalogue covers crypto, macro, commodities, FX, rates, equities and cross-market decision support. Each report states its evidence, freshness, uncertainty and limitations. Standard services cost $0.01 and premium synthesis $0.10.

## See the 402 for yourself

```
curl -s -o /dev/null -D - -H "Accept: application/json" \
  https://pay.edge-agents.ai/v1/services/edge-signal-snapshot \
  | grep -i payment-required | cut -d' ' -f2 | base64 -d
```

This returns the payment terms (x402 version 2). Every paid route offers five settlement rails in one challenge: USDC on Base, Solana, Arbitrum and Polygon, and RLUSD on XRPL.

## Examples

1. [`agentcore/`](agentcore/) - a Strands agent on Amazon Bedrock AgentCore Payments that searches the catalogue and buys a report within a set budget.

## Notes on AgentCore Payments

- AgentCore Payments (in Preview) settles on Base, Solana and Arbitrum from our list. It skips the Polygon and XRPL options, which is fine since the same price is offered on every rail.
- Wallets come from Coinbase CDP or Stripe (Privy). AWS's own [setup tutorial](https://github.com/awslabs/agentcore-samples/tree/main/01-features/08-agents-that-transact/00-getting-started/00-setup-agentcore-payments) creates the payment manager and wallet this example uses.
- Our endpoints are live on mainnet only, so the wallet needs a little real USDC. $0.50 covers dozens of standard calls.

## Contact

hello@edge-agents.ai
