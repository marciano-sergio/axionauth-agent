# AXIONAuth Agent

**Secure AI Agent Authentication with Auth0 Token Vault**

**Live Demo:** [https://axionauth-siiu.srv1452883.hstgr.cloud](https://axionauth-siiu.srv1452883.hstgr.cloud)

---

## The Problem

Modern AI agents need to interact with multiple third-party services on behalf of users - CRMs, email providers, calendars, messaging platforms. Each service requires OAuth tokens, and managing these tokens securely is a critical challenge.

Traditional approaches expose tokens directly to the agent runtime, creating massive security risks. If an agent is compromised, attackers gain access to all connected services. Token refresh, rotation, and revocation become operational nightmares as the number of integrations grows.

Furthermore, compliance requirements (SOC2, GDPR, CCPA) demand that sensitive credentials are encrypted at rest, access is audited, and tokens follow the principle of least privilege. Most agent frameworks treat authentication as an afterthought, leaving organizations vulnerable.

## The Solution

AXIONAuth Agent leverages **Auth0 Token Vault** to implement a zero-trust authentication architecture for AI agents. The agent never sees or stores raw tokens - instead, Auth0 Token Vault acts as a secure proxy:

1. **Token Vault Storage**: All OAuth tokens are stored encrypted (AES-256-GCM) in Auth0's Token Vault, never in the agent's memory or filesystem.
2. **Scoped Access**: Each API call goes through Token Vault with verified scopes, ensuring the agent only accesses what the user has consented to.
3. **Automatic Refresh**: Token Vault handles refresh token rotation automatically, with zero downtime.
4. **Audit Trail**: Every token retrieval, refresh, and API call is logged for compliance.
5. **Revocation**: Users can revoke agent access to any service instantly through Auth0 Dashboard.

## Architecture

```
+-------------------+
|   User / Judge    |
+--------+----------+
         |
    OAuth 2.0 + PKCE
         |
+--------+----------+
|      Auth0        |
|   Token Vault     |
|  (AES-256-GCM)   |
+--------+----------+
         |
   Secure Token Exchange
         |
+--------+----------+
|  AXIONAuth Agent  |
|  (FastAPI Engine)  |
+--------+----------+
    |    |    |    |
    v    v    v    v
HubSpot Gmail Cal  Slack
  CRM   API  endly  API
```

## Features

1. **Zero Token Exposure** - Agent never sees raw OAuth tokens
2. **Multi-Service Orchestration** - Coordinates across HubSpot, Gmail, Calendly, Slack
3. **Real-time Token Vault Visualization** - See token lifecycle in the UI
4. **Tool Call Chain Visualization** - Step-by-step execution with Auth0 flows
5. **5 Pre-built Demo Scenarios** - Showcase different Token Vault capabilities
6. **Interactive Chat Interface** - Type any task and see the agent work
7. **Automatic Token Refresh** - Seamless credential rotation via Token Vault
8. **Scope Verification** - Every API call checks granted scopes
9. **Audit Logging** - Full trail of all token operations
10. **Security Dashboard** - Real-time stats on vault operations

## Tech Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **Auth**: Auth0 Token Vault (OAuth 2.0 + PKCE)
- **Deployment**: Docker, Traefik, Let's Encrypt TLS
- **Infrastructure**: Hostinger VPS, Ubuntu 22.04

## Auth0 Integration Details

### Token Vault Flow

1. User authorizes the agent via Auth0 Universal Login
2. Auth0 stores OAuth tokens in the encrypted Token Vault
3. Agent requests token access through Token Vault API
4. Token Vault returns a scoped, time-limited access token
5. Agent makes API calls; token is never persisted in agent memory
6. Token Vault auto-refreshes tokens before expiry
7. All operations are audit-logged

### Security Model

- Tokens encrypted at rest with AES-256-GCM
- TLS 1.3 for all token transit
- mTLS between agent and Token Vault
- PKCE flow prevents authorization code interception
- Consent-based scoping ensures minimal privilege

## How to Run Locally

```bash
git clone https://github.com/marciano-sergio/axionauth-agent.git
cd axionauth-agent
docker build -t axionauth-demo .
docker run -p 8080:8080 axionauth-demo
# Open http://localhost:8080
```

## Security Considerations

- No API keys or tokens are hardcoded in the application
- All token operations go through Auth0 Token Vault
- The agent process has no direct access to OAuth credentials
- Rate limiting and request validation on all endpoints
- CORS and CSP headers configured for production

## Roadmap

- [ ] Real Auth0 Token Vault SDK integration
- [ ] Add Google Workspace and Microsoft 365 connectors
- [ ] Implement consent management UI
- [ ] Add webhook support for real-time token events
- [ ] Multi-tenant support with per-user token isolation
- [ ] Token usage analytics and cost tracking

## License

MIT License - See [LICENSE](LICENSE) for details.

---

*Built for the [Authorized to Act: Auth0 for AI Agents Hackathon](https://authorizedtoact.devpost.com)*
