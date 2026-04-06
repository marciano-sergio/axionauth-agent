# Security Policy -- AXIONAuth Agent

## Overview

AXIONAuth Agent is designed with security as a first-class concern. This document describes the security model, token lifecycle management, and best practices for deploying and operating the system.

---

## Token Lifecycle Management

### Creation
- Tokens are created exclusively through Auth0's authorization flow
- User consent is required for each service connection
- Tokens are immediately encrypted and stored in Token Vault
- The agent runtime never handles raw credentials during creation

### Storage
- All tokens are stored in Auth0 Token Vault with AES-256 encryption at rest
- Refresh tokens are **never** exposed to the agent runtime
- Access tokens are short-lived (default: 300 seconds / 5 minutes)
- Token metadata (scopes, expiry, service) is stored separately from token values

### Retrieval
- Agents request tokens via authenticated API calls to the Token Vault
- Each retrieval is logged in the audit trail
- Token Vault verifies agent identity via mTLS before issuing tokens
- Only the minimum required scopes are included in the issued token

### Refresh
- Token Vault automatically refreshes tokens before expiration
- Refresh operations are transparent to the agent
- Failed refreshes trigger alerts and graceful degradation
- Refresh tokens are rotated on each use (rotation policy)

### Revocation
- Tokens can be revoked instantly via the management API
- Revocation propagates to all connected services within 1 second
- Revoked tokens are added to a deny list for the remainder of their TTL
- Bulk revocation is supported for compromised agent scenarios

---

## Scope-Based Access Control

### Principle of Least Privilege
Every agent-to-service connection defines explicit scopes:

```
Agent "data-reader" -> GitHub:
  ALLOWED: repo:read
  DENIED:  repo:write, admin:org, delete_repo

Agent "notification-bot" -> Slack:
  ALLOWED: chat:write (to #notifications only)
  DENIED:  channels:manage, users:read
```

### Scope Enforcement
- Scopes are enforced at **two levels**: Token Vault and the target API
- Token Vault will not issue a token with scopes exceeding the connection definition
- Scope escalation attempts are logged as security events
- Periodic scope audits compare granted vs. used scopes

---

## Token Rotation Policies

| Policy | Value | Rationale |
|--------|-------|-----------|
| Access token TTL | 300s (5 min) | Minimize window of exposure |
| Refresh token rotation | Every use | Prevent refresh token replay |
| Refresh token absolute lifetime | 24 hours | Force re-authentication daily |
| Idle timeout | 1 hour | Revoke unused connections |
| Maximum active tokens per agent | 10 | Prevent token accumulation |

---

## Audit Trail

### Events Logged
- `token.store` -- New token stored in vault
- `token.retrieve` -- Token issued to agent
- `token.refresh` -- Token refreshed (automatic or manual)
- `token.revoke` -- Token revoked
- `token.expired` -- Token reached end of life
- `token.denied` -- Token request denied (scope/permission)
- `agent.register` -- New agent registered
- `agent.compromised` -- Agent flagged as compromised
- `connection.create` -- New service connection established
- `connection.remove` -- Service connection removed

### Audit Record Format
```json
{
    "id": "evt_20260404_001",
    "timestamp": "2026-04-04T18:30:00.000Z",
    "event": "token.retrieve",
    "severity": "info",
    "agent_id": "agent_001",
    "service": "github",
    "scopes": ["repo:read"],
    "source_ip": "10.0.1.50",
    "mtls_cn": "agent_001.axionauth.local",
    "result": "success",
    "token_ttl": 300,
    "correlation_id": "req_abc123"
}
```

### Retention
- Audit logs are retained for 90 days in hot storage
- Archived to cold storage for 1 year
- Immutable -- logs cannot be modified or deleted

---

## Zero-Trust Architecture

### Principles Applied

1. **Never trust, always verify**: Every request is authenticated regardless of source network
2. **Assume breach**: System is designed to limit blast radius of any single compromise
3. **Verify explicitly**: Agent identity verified via mTLS certificates, not just API keys
4. **Least privilege access**: Tokens scoped to minimum required permissions
5. **Microsegmentation**: Each agent-to-service connection is isolated

### Network Security
- All communication encrypted with TLS 1.3
- mTLS between agent runtime and Token Vault
- No direct agent-to-database connections
- Token Vault accessible only via API gateway

---

## OWASP Compliance

### API Security Top 10 (2023) Alignment

| OWASP Risk | Mitigation |
|------------|------------|
| API1: Broken Object Level Authorization | Per-agent, per-service token isolation |
| API2: Broken Authentication | Auth0 with MFA, mTLS for agents |
| API3: Broken Object Property Level Authorization | Strict scope enforcement |
| API4: Unrestricted Resource Consumption | Rate limiting on token operations |
| API5: Broken Function Level Authorization | Role-based access to management APIs |
| API6: Unrestricted Access to Sensitive Business Flows | Audit logging of all operations |
| API7: Server Side Request Forgery | No user-controlled URLs in token operations |
| API8: Security Misconfiguration | Secure defaults, no debug in production |
| API9: Improper Inventory Management | Centralized connection registry |
| API10: Unsafe Consumption of APIs | Token validation before forwarding |

---

## Reporting Security Issues

If you discover a security vulnerability, please report it responsibly:

- Email: contato@axionautomacao.tech
- Subject: `[SECURITY] AXIONAuth Agent - Brief Description`
- Do NOT open a public GitHub issue for security vulnerabilities
- We will acknowledge receipt within 24 hours
- We aim to provide a fix within 72 hours for critical issues

---

## Security Checklist for Deployment

- [ ] Auth0 domain and credentials configured via environment variables (not hardcoded)
- [ ] TLS certificates valid and auto-renewing
- [ ] mTLS certificates provisioned for all agent instances
- [ ] Audit log destination configured and verified
- [ ] Token TTL values reviewed for your use case
- [ ] Rate limiting enabled on all API endpoints
- [ ] Health check monitoring active
- [ ] Incident response runbook reviewed
