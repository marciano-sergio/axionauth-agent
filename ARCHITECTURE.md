# Architecture -- AXIONAuth Agent

## System Overview

AXIONAuth Agent is a reference architecture demonstrating secure AI agent authentication using Auth0 Token Vault. The system is composed of four primary layers.

```
+===========================================================================+
|                          CLIENT LAYER                                      |
|   +-------------------+  +-------------------+  +-------------------+     |
|   |   Web Dashboard   |  |   Demo Runner     |  |   Audit Viewer    |     |
|   |   (Tailwind CSS)  |  |   (Interactive)   |  |   (Real-time)     |     |
|   +-------------------+  +-------------------+  +-------------------+     |
+===========================================================================+
                                    |
                                  HTTPS
                                    |
+===========================================================================+
|                          API LAYER (FastAPI)                                |
|   +-------------+  +---------------+  +------------+  +--------------+    |
|   | Auth Router |  | Token Vault   |  | Agent      |  | Demo         |    |
|   | /api/auth/* |  | Router        |  | Router     |  | Router       |    |
|   |             |  | /api/token-   |  | /api/      |  | /api/demo/*  |    |
|   |             |  | vault/*       |  | agents/*   |  |              |    |
|   +-------------+  +---------------+  +------------+  +--------------+    |
|                            |                                               |
|                     +------+------+                                        |
|                     | Middleware  |                                         |
|                     | - CORS     |                                          |
|                     | - Auth     |                                          |
|                     | - Logging  |                                          |
|                     | - Rate Lim |                                          |
|                     +------------+                                          |
+===========================================================================+
                                    |
                                  mTLS
                                    |
+===========================================================================+
|                       AUTH0 INTEGRATION LAYER                              |
|   +-------------------+  +-------------------+  +-------------------+     |
|   | Auth0 Universal   |  | Auth0 Token       |  | Auth0 Management  |     |
|   | Login             |  | Vault             |  | API               |     |
|   | - User authn      |  | - Token storage   |  | - Connection mgmt |     |
|   | - MFA             |  | - Token rotation  |  | - Scope config    |     |
|   | - Session mgmt    |  | - Token retrieval |  | - Audit export    |     |
|   +-------------------+  +-------------------+  +-------------------+     |
+===========================================================================+
                                    |
                              Scoped Tokens
                                    |
+===========================================================================+
|                       EXTERNAL SERVICE LAYER                               |
|   +----------+  +----------+  +----------+  +----------+  +----------+   |
|   |  GitHub  |  |  Slack   |  |  Gmail   |  | Calendar |  |  Custom  |   |
|   |  API     |  |  API     |  |  API     |  |  API     |  |  APIs    |   |
|   +----------+  +----------+  +----------+  +----------+  +----------+   |
+===========================================================================+
```

---

## Data Flow

### Flow 1: User Authentication

```
User                    FastAPI              Auth0
 |                         |                   |
 |-- GET /login ---------> |                   |
 |                         |-- Redirect -----> |
 |                         |                   |
 |<-------- Auth0 Login Page ------------------|
 |                         |                   |
 |-- Credentials --------------------------------> |
 |                         |                   |-- Validate
 |                         |                   |-- Issue tokens
 |                         |<-- Callback ------|
 |                         |-- Set session     |
 |<-- Dashboard ---------- |                   |
```

### Flow 2: Store Token in Vault

```
Agent Runtime           FastAPI            Token Vault         External API
     |                     |                    |                    |
     |-- POST /store ----> |                    |                    |
     |   {service, scopes} |                    |                    |
     |                     |-- Validate agent   |                    |
     |                     |-- Check scopes     |                    |
     |                     |                    |                    |
     |                     |-- Store token ---> |                    |
     |                     |                    |-- Encrypt          |
     |                     |                    |-- Store            |
     |                     |                    |-- Log audit        |
     |                     |<-- Confirmation ---|                    |
     |                     |                    |                    |
     |<-- 201 Created ---- |                    |                    |
     |   {connection_id}   |                    |                    |
```

### Flow 3: Retrieve Token for API Call

```
Agent Runtime           FastAPI            Token Vault         External API
     |                     |                    |                    |
     |-- GET /retrieve --> |                    |                    |
     |   {service, agent}  |                    |                    |
     |                     |-- Verify mTLS      |                    |
     |                     |-- Check permissions|                    |
     |                     |                    |                    |
     |                     |-- Get token -----> |                    |
     |                     |                    |-- Decrypt          |
     |                     |                    |-- Check expiry     |
     |                     |                    |-- Refresh if needed|
     |                     |                    |-- Log audit        |
     |                     |<-- Access token ---|                    |
     |                     |   (short-lived)    |                    |
     |                     |                    |                    |
     |<-- 200 OK --------- |                    |                    |
     |   {access_token,    |                    |                    |
     |    expires_in: 300} |                    |                    |
     |                     |                    |                    |
     |-- API call with token ----------------------------------------> |
     |<-- API response ----------------------------------------------- |
```

### Flow 4: Emergency Revocation

```
Admin / System          FastAPI            Token Vault         External APIs
     |                     |                    |                    |
     |-- DELETE /revoke -> |                    |                    |
     |   {agent_id: all}   |                    |                    |
     |                     |-- Verify admin     |                    |
     |                     |                    |                    |
     |                     |-- Revoke all ----> |                    |
     |                     |                    |-- For each service:|
     |                     |                    |   - Revoke token   |
     |                     |                    |   - Add to denylist|
     |                     |                    |   - Log audit      |
     |                     |                    |                    |
     |                     |                    |-- Notify services -> |
     |                     |                    |                    |-- Invalidate
     |                     |<-- Confirmation ---|                    |
     |                     |                    |                    |
     |<-- 200 OK --------- |                    |                    |
     |   {revoked: 5,      |                    |                    |
     |    services: [...]} |                    |                    |
```

---

## Auth0 Integration Points

### 1. Universal Login
- **Purpose**: User authentication and consent
- **Flow**: PKCE authorization code flow
- **Configuration**: Custom login page with AXIONAuth branding
- **MFA**: Optional TOTP/WebAuthn second factor

### 2. Token Vault
- **Purpose**: Secure token storage and lifecycle management
- **Operations**: Store, retrieve, refresh, revoke
- **Encryption**: AES-256-GCM at rest, TLS 1.3 in transit
- **Access**: Authenticated via mTLS client certificates

### 3. Management API
- **Purpose**: Service connection and scope configuration
- **Operations**: CRUD on connections, scope definitions, agent registration
- **Auth**: Machine-to-machine client credentials grant

### 4. Actions (Future)
- **Purpose**: Custom logic on token lifecycle events
- **Triggers**: Post-token-issue, pre-token-refresh, post-revoke
- **Use Cases**: Custom logging, alerting, policy enforcement

---

## Token Vault Workflow

```
                    +------------------+
                    |  Token Request   |
                    +--------+---------+
                             |
                    +--------v---------+
                    | Validate Agent   |
                    | Identity (mTLS)  |
                    +--------+---------+
                             |
                    +--------v---------+
                    | Check Connection |
                    | Permissions      |
                    +--------+---------+
                             |
                 +-----------+-----------+
                 |                       |
         +-------v-------+     +--------v--------+
         | Token Valid?   |     | Token Expired?  |
         | Return cached  |     | Refresh needed  |
         +-------+-------+     +--------+--------+
                 |                       |
                 |              +--------v--------+
                 |              | Refresh via      |
                 |              | Auth0 /token     |
                 |              +--------+--------+
                 |                       |
                 |              +--------v--------+
                 |              | Store new token  |
                 |              | in Vault         |
                 |              +--------+--------+
                 |                       |
                 +----------+------------+
                            |
                   +--------v---------+
                   | Generate scoped   |
                   | access token      |
                   | (TTL: 300s)       |
                   +--------+---------+
                            |
                   +--------v---------+
                   | Log audit event   |
                   +--------+---------+
                            |
                   +--------v---------+
                   | Return to agent   |
                   +------------------+
```

---

## Error Handling and Recovery

### Token Errors

| Error | Cause | Recovery |
|-------|-------|----------|
| `token_expired` | Access token past TTL | Automatic refresh via Token Vault |
| `refresh_failed` | Refresh token invalid | Prompt user re-authentication |
| `scope_denied` | Requested scope not permitted | Return 403, log security event |
| `service_unavailable` | Target API is down | Retry with exponential backoff |
| `vault_unreachable` | Token Vault connectivity issue | Use cached token if valid, alert |

### Circuit Breaker Pattern

```
CLOSED (normal) --[5 failures]--> OPEN (failing)
                                      |
                                  [30s timer]
                                      |
                                  HALF-OPEN
                                      |
                              [success] / [failure]
                                /           \
                           CLOSED          OPEN
```

- Each service connection has an independent circuit breaker
- Prevents cascade failures across services
- Metrics exposed via `/health` endpoint

---

## Scale Considerations

### Current Architecture (Demo)
- Single FastAPI instance
- In-memory token cache
- SQLite audit log
- Suitable for demo and small deployments

### Production Architecture (Recommended)
- Multiple FastAPI instances behind load balancer
- Redis for distributed token cache
- PostgreSQL for audit log persistence
- Auth0 Token Vault handles token storage (no local persistence needed)
- Horizontal scaling of agent runtime instances

### Performance Characteristics

| Operation | Latency (p99) | Throughput |
|-----------|--------------|------------|
| Token retrieve (cached) | < 5ms | 10,000 rps |
| Token retrieve (refresh) | < 200ms | 500 rps |
| Token store | < 100ms | 1,000 rps |
| Token revoke | < 50ms | 2,000 rps |
| Audit log write | < 10ms | 20,000 rps |

---

## Deployment Architecture

```
                    +-------------------+
                    |   Cloudflare      |
                    |   (CDN + WAF)     |
                    +--------+----------+
                             |
                    +--------v----------+
                    |   Nginx Reverse   |
                    |   Proxy + TLS     |
                    +--------+----------+
                             |
              +--------------+--------------+
              |                             |
     +--------v----------+       +----------v--------+
     |   FastAPI          |       |   FastAPI          |
     |   Instance 1       |       |   Instance 2       |
     +--------+-----------+       +----------+---------+
              |                              |
              +-------------+----------------+
                            |
                   +--------v---------+
                   |   Auth0 Cloud    |
                   |   Token Vault    |
                   +------------------+
```

---

## Directory Structure

```
axionauth-agent/
|-- main.py                 # FastAPI application entry point
|-- requirements.txt        # Python dependencies
|-- Dockerfile              # Container definition
|-- .env.example            # Environment variable template
|-- README.md               # Project documentation
|-- SECURITY.md             # Security policy
|-- ARCHITECTURE.md         # This document
|-- LICENSE                 # MIT License
|-- static/
|   |-- index.html          # Dashboard UI
|   |-- styles.css          # Tailwind CSS styles
|   +-- scripts.js          # Frontend JavaScript
|-- routers/
|   |-- auth.py             # Authentication endpoints
|   |-- token_vault.py      # Token Vault operations
|   |-- agents.py           # Agent management
|   +-- demo.py             # Demo scenarios
|-- models/
|   |-- token.py            # Token data models
|   |-- agent.py            # Agent data models
|   +-- audit.py            # Audit log models
+-- tests/
    |-- test_auth.py         # Auth flow tests
    |-- test_vault.py        # Token Vault tests
    +-- test_demo.py         # Demo scenario tests
```
