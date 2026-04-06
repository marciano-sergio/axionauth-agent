<div align="center">

```
     _    __  _____ ___  _   _    _         _   _
    / \   \ \/ /_ _/ _ \| \ | |  / \  _   _| |_| |__
   / _ \   \  / | | | | |  \| | / _ \| | | | __| '_ \
  / ___ \  /  \ | | |_| | |\  |/ ___ \ |_| | |_| | | |
 /_/   \_\/_/\_\___\___/|_| \_/_/   \_\__,_|\__|_| |_|
                    A G E N T
```

### Secure AI Agent Authentication with Auth0 Token Vault

[![Live Demo](https://img.shields.io/badge/Live%20Demo-axionauth--agent-00C853?style=for-the-badge&logo=vercel)](https://axionauth-siiu.srv1452883.hstgr.cloud)
[![Video Demo](https://img.shields.io/badge/Video%20Demo-YouTube-FF0000?style=for-the-badge&logo=youtube)](https://youtu.be/Hfa5ba1yw1I)
[![Devpost](https://img.shields.io/badge/Devpost-Submission-003E54?style=for-the-badge&logo=devpost)](https://authorizedtoact.devpost.com/submissions/986711-axionauth-agent)
[![Built with Auth0](https://img.shields.io/badge/Built%20with-Auth0%20for%20AI%20Agents-EB5424?style=for-the-badge&logo=auth0)](https://auth0.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

</div>

---

## The Problem

AI agents are becoming autonomous actors in production systems -- booking flights, managing infrastructure, processing payments, accessing sensitive data. But today's authentication landscape is dangerously unprepared:

- **Token Sprawl**: Agents accumulate long-lived API tokens with no rotation, no revocation, and no audit trail. A single leaked token can compromise entire systems.
- **Over-Privileged Access**: Most agent integrations use a single "god token" with full API access. There is no concept of scoped, least-privilege permissions per service.
- **Zero Visibility**: When an agent calls a third-party API, there is no centralized log of what token was used, what scope was granted, or whether the token was still valid.
- **Manual Token Management**: Developers hardcode tokens in environment variables, `.env` files, or worse -- directly in source code. Token refresh? Hope the agent handles it.
- **No Revocation Path**: If an agent is compromised, there is no single control plane to immediately revoke all its API access across services.

**The result**: a ticking time bomb of unmanaged credentials powering autonomous systems.

---

## The Solution

**AXIONAuth Agent** demonstrates how **Auth0 Token Vault** solves the AI agent authentication crisis with a production-grade reference architecture:

```
                        Auth0 Token Vault Architecture
 +--------+      +--------+      +-------------+      +---------+
 |  User  | ---> | Auth0  | ---> | Token Vault | ---> |  Agent  |
 | (Auth) |      | (IdP)  |      | (Secure     |      | Runtime |
 +--------+      +--------+      |  Storage)   |      +---------+
                                  +-------------+          |
                                       |                   |
                              +--------+--------+          |
                              |                 |          |
                         +---------+      +---------+     |
                         | Scoped  |      | Audit   |     |
                         | Tokens  |      | Logs    |     |
                         +---------+      +---------+     |
                              |                            |
                    +---------+---------+---------+        |
                    |         |         |         |        |
                 +------+ +------+ +------+ +------+      |
                 |GitHub| |Slack | |Gmail | | More |  <----+
                 | API  | | API  | | API  | | APIs |
                 +------+ +------+ +------+ +------+
```

**How it works:**

1. **User authenticates** via Auth0 Universal Login
2. **Auth0 issues scoped tokens** stored in Token Vault -- never exposed to the agent
3. **Agent requests access** to a specific service (e.g., GitHub) with specific scopes
4. **Token Vault provides** a short-lived, scoped token -- the agent never sees the refresh token
5. **Every token operation** is logged with full audit trail
6. **Tokens auto-rotate** and can be revoked instantly from a single control plane

---

## Screenshots

| Dashboard | Token Vault Manager | Audit Log |
|-----------|-------------------|-----------|
| Dark-themed dashboard showing agent status, active connections, and real-time token health metrics | Interactive token management panel with store, retrieve, refresh, and revoke operations | Chronological security audit log with filterable events and severity levels |

| Demo Scenarios | Security Panel |
|----------------|---------------|
| Five pre-built interactive scenarios demonstrating real-world agent authentication flows | Real-time security posture display with mTLS status, token exposure metrics, and compliance checks |

---

## Features

### Core Authentication
1. **Auth0 Universal Login** -- Secure user authentication with MFA support
2. **Token Vault Integration** -- Centralized, encrypted token storage via Auth0
3. **Scoped Token Issuance** -- Per-service, least-privilege token generation
4. **Automatic Token Rotation** -- Background refresh before expiration
5. **Instant Token Revocation** -- Single-click revocation across all services

### Agent Runtime
6. **Zero-Token-Exposure Architecture** -- Agents never see raw refresh tokens
7. **Service Connection Manager** -- Visual management of all agent-to-API connections
8. **Multi-Service Support** -- GitHub, Slack, Gmail, Calendar, and extensible
9. **Real-Time Agent Monitoring** -- Live status of all agent operations
10. **Graceful Degradation** -- Agents handle token failures without crashing

### Security & Compliance
11. **Full Audit Trail** -- Every token operation logged with timestamp and context
12. **mTLS Verification** -- Mutual TLS between agent and Token Vault
13. **Token Health Monitoring** -- Dashboard showing token age, scope, and status
14. **OWASP-Aligned Security** -- Following OWASP API Security Top 10 guidelines
15. **Role-Based Access Control** -- Different permission levels for different agent types

---

## Auth0 Integration Deep Dive

### Token Vault Usage

AXIONAuth Agent uses Auth0 Token Vault as the **single source of truth** for all agent credentials:

```python
# Store a token securely in the vault
POST /api/token-vault/store
{
    "service": "github",
    "scopes": ["repo:read", "issues:write"],
    "connection_id": "conn_abc123"
}

# Retrieve a scoped, short-lived token
GET /api/token-vault/retrieve?service=github&agent_id=agent_001

# Refresh before expiration (automatic)
POST /api/token-vault/refresh
{
    "service": "github",
    "connection_id": "conn_abc123"
}

# Instant revocation
DELETE /api/token-vault/revoke?service=github&connection_id=conn_abc123
```

### Scoped Permissions Per Service

Each service connection defines **exactly** what the agent can do:

| Service  | Available Scopes                    | Default Agent Scope     |
|----------|-------------------------------------|------------------------|
| GitHub   | `repo:read`, `repo:write`, `issues:write`, `pr:read` | `repo:read`   |
| Slack    | `channels:read`, `chat:write`, `files:read`           | `channels:read` |
| Gmail    | `mail:read`, `mail:send`, `labels:manage`             | `mail:read`    |
| Calendar | `events:read`, `events:write`                          | `events:read`  |

### Zero-Token-Exposure Architecture

```
Agent Runtime                    Token Vault
     |                               |
     |-- "I need GitHub access" ---->|
     |                               |-- Validates agent identity
     |                               |-- Checks scope permissions
     |                               |-- Generates short-lived token
     |<-- {access_token, exp: 300} --|
     |                               |
     |-- Uses token for API call     |
     |                               |
     |   (Token expires in 5 min)    |
     |                               |
     |-- "I need GitHub access" ---->|
     |<-- {new_access_token} --------|
```

- The agent **never** receives the refresh token
- Access tokens expire in **5 minutes** (configurable)
- Token Vault handles all refresh logic internally
- If the agent is compromised, revoke access instantly -- no leaked long-lived tokens

### Audit Logging

Every token operation generates an audit event:

```json
{
    "timestamp": "2026-04-04T18:30:00Z",
    "event": "token.retrieve",
    "agent_id": "agent_001",
    "service": "github",
    "scopes_requested": ["repo:read"],
    "scopes_granted": ["repo:read"],
    "token_ttl": 300,
    "source_ip": "10.0.1.50",
    "mtls_verified": true
}
```

### mTLS Verification

Agent-to-Token Vault communication is secured with mutual TLS:
- Agent presents a client certificate signed by Auth0
- Token Vault validates the certificate chain
- Connection is encrypted end-to-end
- Certificate rotation is automated

---

## Security Model

AXIONAuth Agent is built on **five core security principles**:

### 1. Least Privilege
Every agent token is scoped to the **minimum permissions** required. An agent that only reads GitHub repos cannot write to them, even if compromised.

### 2. Short-Lived Tokens
Access tokens expire in 5 minutes by default. Refresh tokens are stored exclusively in Token Vault and never exposed to the agent runtime.

### 3. Zero Trust
Every token request is authenticated and authorized independently. No implicit trust between services. mTLS ensures both parties verify identity.

### 4. Complete Auditability
Every token operation -- store, retrieve, refresh, revoke -- is logged with full context. Security teams can trace any agent action back to the specific token and scope used.

### 5. Instant Revocation
A single API call revokes all tokens for a compromised agent across all connected services. No hunting for scattered credentials.

---

## API Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/login` | Authenticate via Auth0 |
| `POST` | `/api/auth/callback` | Auth0 callback handler |
| `POST` | `/api/auth/logout` | Revoke session and tokens |

### Token Vault Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/token-vault/store` | Store a new service token |
| `GET` | `/api/token-vault/retrieve` | Get a scoped access token |
| `POST` | `/api/token-vault/refresh` | Force token refresh |
| `DELETE` | `/api/token-vault/revoke` | Revoke a service token |
| `GET` | `/api/token-vault/health` | Check token health status |

### Agent Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/agents` | List all registered agents |
| `POST` | `/api/agents/register` | Register a new agent |
| `GET` | `/api/agents/{id}/status` | Get agent status |
| `GET` | `/api/agents/{id}/audit` | Get agent audit log |

### Service Connections

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/connections` | List all service connections |
| `POST` | `/api/connections` | Create a new connection |
| `DELETE` | `/api/connections/{id}` | Remove a connection |

### Demo & Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/demo/scenarios` | List demo scenarios |
| `POST` | `/api/demo/run/{id}` | Execute a demo scenario |
| `GET` | `/health` | Health check |

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/marciano-sergio/axionauth-agent.git
cd axionauth-agent

# Configure environment
cp .env.example .env
# Edit .env with your Auth0 credentials

# Run with Docker
docker run -d \
  --name axionauth-agent \
  -p 8000:8000 \
  --env-file .env \
  axionauth-agent:latest

# Open http://localhost:8000
```

---

## Demo Scenarios

The live demo includes **5 interactive scenarios** that showcase Auth0 Token Vault in action:

### Scenario 1: Secure GitHub Access
An AI agent needs to read repository data. Watch as Token Vault issues a `repo:read` scoped token, the agent fetches data, and the token auto-expires.

### Scenario 2: Multi-Service Workflow
An agent orchestrates across GitHub, Slack, and Gmail simultaneously. Each service gets its own scoped token -- no shared credentials.

### Scenario 3: Token Rotation Under Load
Simulates an agent making rapid API calls while Token Vault transparently rotates tokens in the background. Zero downtime, zero exposure.

### Scenario 4: Compromised Agent Response
An agent is flagged as compromised. Watch as Token Vault instantly revokes all its tokens across every connected service in under 1 second.

### Scenario 5: Audit Trail Analysis
Review the complete audit log of all token operations. Filter by agent, service, event type, and time range. Full forensic capability.

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI (Python 3.11) | High-performance async API server |
| **Auth Provider** | Auth0 | Identity and Token Vault |
| **Frontend** | HTML5 + Tailwind CSS | Responsive dark-themed UI |
| **Containerization** | Docker | Reproducible deployment |
| **TLS** | Let's Encrypt + mTLS | End-to-end encryption |
| **Hosting** | Hostinger VPS | Production deployment |
| **CI/CD** | GitHub Actions | Automated testing and deployment |

---

## Future Roadmap

- [ ] **Auth0 Actions Integration** -- Custom logic on token events
- [ ] **Agent Identity Federation** -- Cross-org agent authentication
- [ ] **Token Vault Analytics** -- Usage patterns and anomaly detection
- [ ] **SDK Release** -- Python and Node.js SDKs for agent developers
- [ ] **Policy Engine** -- Declarative access policies (OPA integration)
- [ ] **Multi-Tenant Support** -- Isolated token vaults per organization
- [ ] **WebSocket Streaming** -- Real-time token event notifications
- [ ] **Compliance Reports** -- SOC2 and GDPR compliance automation

---

## Contributing

Contributions are welcome! Please see [SECURITY.md](SECURITY.md) for security-related guidelines and [ARCHITECTURE.md](ARCHITECTURE.md) for system design documentation.

---

## License

This project is licensed under the MIT License -- see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built for the [Auth0 Authorized to Act Hackathon](https://authorizedtoact.devpost.com/)**

Made with dedication by [Marciano Sergio](https://github.com/marciano-sergio) | [Axion Automacao](https://axionautomacao.tech)

</div>
