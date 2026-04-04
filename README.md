# AxionAuth — AI Agent with Auth0 Token Vault
## Authorized to Act: Auth0 for AI Agents Hackathon
**Prize:** $10,000 | **Deadline:** Apr 6, 2026

## What It Does
AxionAuth is an AI agent that manages multi-service OAuth authentication via Auth0 Token Vault, enabling autonomous agents to securely access external APIs (CRM, calendar, email, WhatsApp) without exposing credentials.

## The Problem
AI agents need to call external APIs on behalf of users. Current approaches either:
- Store tokens insecurely in plaintext
- Require user re-authentication for every action
- Can't rotate/revoke tokens without breaking agent workflows

## Solution: Auth0 Token Vault + AI Agent
AxionAuth uses Auth0 Token Vault as the secure credential store, so the agent can:
1. Authenticate users once via OAuth
2. Store tokens securely in Token Vault
3. Autonomously call APIs (Gmail, HubSpot, Calendly) using stored tokens
4. Auto-refresh tokens without user intervention

## Architecture
User → Auth0 Login → Token Vault stores token → Agent calls APIs autonomously

## Use Case
Sales automation agent that:
- Reads leads from HubSpot (OAuth via Token Vault)
- Sends follow-up emails via Gmail (OAuth via Token Vault)  
- Books meetings via Calendly (OAuth via Token Vault)
- All without the user logging in repeatedly

## Tech Stack
Python, Auth0, Token Vault SDK, Claude Haiku (MCP), FastAPI
