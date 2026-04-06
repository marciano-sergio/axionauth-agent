import time, json, random, re
from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path

app = FastAPI(title="AXIONAuth Agent", version="3.0.0")

# --- Simulated Token Vault State ---
TOKENS = {
    "hubspot": {
        "service": "HubSpot CRM",
        "status": "active",
        "scopes": ["crm.objects.contacts.read", "crm.objects.contacts.write", "crm.objects.deals.read"],
        "issued_at": "2026-04-04T08:00:00Z",
        "expires_in": 3600,
        "refresh_count": 14,
        "last_refresh": "2026-04-04T11:42:00Z",
        "connection_id": "con_hbs_9xK2mP",
        "token_set_id": "tks_hbs_7fR3nQ"
    },
    "gmail": {
        "service": "Gmail API",
        "status": "active",
        "scopes": ["gmail.send", "gmail.readonly", "gmail.compose"],
        "issued_at": "2026-04-04T07:30:00Z",
        "expires_in": 3600,
        "refresh_count": 11,
        "last_refresh": "2026-04-04T11:38:00Z",
        "connection_id": "con_gml_4vN8wL",
        "token_set_id": "tks_gml_2kP5xJ"
    },
    "calendly": {
        "service": "Calendly",
        "status": "active",
        "scopes": ["events.read", "events.write", "availability.read"],
        "issued_at": "2026-04-04T09:00:00Z",
        "expires_in": 7200,
        "refresh_count": 5,
        "last_refresh": "2026-04-04T11:15:00Z",
        "connection_id": "con_cal_6tM1rY",
        "token_set_id": "tks_cal_9hW4zA"
    },
    "slack": {
        "service": "Slack",
        "status": "active",
        "scopes": ["chat:write", "channels:read", "users:read"],
        "issued_at": "2026-04-04T08:15:00Z",
        "expires_in": 43200,
        "refresh_count": 2,
        "last_refresh": "2026-04-04T10:00:00Z",
        "connection_id": "con_slk_3bQ7uH",
        "token_set_id": "tks_slk_5jE2vF"
    }
}

LEADS_DB = [
    {"id": "L-1001", "name": "Sarah Chen", "company": "TechVentures Inc.", "title": "VP Engineering", "email": "sarah.chen@techventures.io", "score": 92, "stage": "Qualified", "last_activity": "2026-04-03", "deal_value": 85000},
    {"id": "L-1002", "name": "Marcus Johnson", "company": "DataFlow Systems", "title": "CTO", "email": "mjohnson@dataflow.com", "score": 87, "stage": "Proposal Sent", "last_activity": "2026-04-02", "deal_value": 120000},
    {"id": "L-1003", "name": "Emily Rodriguez", "company": "CloudScale AI", "title": "Director of Product", "email": "emily.r@cloudscale.ai", "score": 78, "stage": "Discovery", "last_activity": "2026-04-04", "deal_value": 65000},
    {"id": "L-1004", "name": "James Park", "company": "NexGen Analytics", "title": "Head of Data", "email": "jpark@nexgenanalytics.co", "score": 95, "stage": "Negotiation", "last_activity": "2026-04-04", "deal_value": 210000},
    {"id": "L-1005", "name": "Priya Sharma", "company": "Innovate Labs", "title": "CEO", "email": "priya@innovatelabs.dev", "score": 71, "stage": "New Lead", "last_activity": "2026-04-01", "deal_value": 45000},
]

def make_token_flow(service_key):
    t = TOKENS[service_key]
    return {
        "auth0_flow": "token_vault_exchange",
        "connection_id": t["connection_id"],
        "token_set_id": t["token_set_id"],
        "action": "access_token_retrieved",
        "scopes_used": t["scopes"],
        "token_refreshed": random.choice([True, False]),
        "vault_latency_ms": round(random.uniform(12, 45), 1),
        "security": {
            "encrypted_at_rest": True,
            "token_never_exposed_to_agent": True,
            "audit_logged": True,
            "mTLS_verified": True
        }
    }

def build_tool_calls(tools):
    calls = []
    for i, (name, svc, result) in enumerate(tools):
        calls.append({
            "step": i + 1,
            "tool": name,
            "service": svc,
            "auth0_token_vault": make_token_flow(svc) if svc in TOKENS else None,
            "status": "success",
            "duration_ms": round(random.uniform(80, 350), 0),
            "result": result
        })
    return calls

def handle_leads(task):
    tools = [
        ("auth0.tokenVault.getToken", "hubspot", {"token_status": "valid", "expires_in": 2847}),
        ("hubspot.crm.contacts.search", "hubspot", {"total": len(LEADS_DB), "leads": LEADS_DB}),
        ("agent.analyze", "hubspot", {
            "high_priority": [l for l in LEADS_DB if l["score"] >= 85],
            "recommended_actions": [
                f"Prioritize {LEADS_DB[3]['name']} (score {LEADS_DB[3]['score']}) - in Negotiation stage, deal value ${LEADS_DB[3]['deal_value']:,}",
                f"Follow up with {LEADS_DB[0]['name']} (score {LEADS_DB[0]['score']}) - Qualified, ready for proposal",
                f"Schedule discovery call with {LEADS_DB[2]['name']} - showed interest today"
            ]
        })
    ]
    return {
        "agent": "AXIONAuth",
        "task": task,
        "reasoning": "Securely retrieved CRM access token from Auth0 Token Vault, queried HubSpot API for active leads, analyzed pipeline and scored priorities.",
        "tool_calls": build_tool_calls(tools),
        "summary": f"Found {len(LEADS_DB)} active leads. Top priority: {LEADS_DB[3]['name']} at {LEADS_DB[3]['company']} (score {LEADS_DB[3]['score']}, ${LEADS_DB[3]['deal_value']:,} deal in Negotiation). Recommend immediate follow-up on 3 high-value opportunities.",
        "tokens_used": ["hubspot"],
        "auth0_integration": {
            "token_vault_calls": 1,
            "tokens_refreshed": 0,
            "scopes_verified": True,
            "zero_token_exposure": True
        }
    }

def handle_email(task):
    lead = LEADS_DB[0]
    tools = [
        ("auth0.tokenVault.getToken", "hubspot", {"token_status": "valid"}),
        ("hubspot.crm.contacts.get", "hubspot", {"contact": lead}),
        ("auth0.tokenVault.getToken", "gmail", {"token_status": "refreshed", "new_expiry": 3600}),
        ("gmail.messages.send", "gmail", {
            "message_id": "msg_ax_20260404_001",
            "to": lead["email"],
            "subject": f"Following up on our conversation - {lead['company']}",
            "status": "sent",
            "thread_id": "thread_9xK2mP"
        }),
        ("hubspot.crm.contacts.update", "hubspot", {
            "contact_id": lead["id"],
            "updated_fields": {"last_contacted": "2026-04-04", "notes": "Automated follow-up sent via AXIONAuth Agent"}
        })
    ]
    return {
        "agent": "AXIONAuth",
        "task": task,
        "reasoning": "Retrieved CRM token to fetch contact details, refreshed Gmail token via Token Vault, composed and sent personalized follow-up, then updated CRM record - all with zero direct token exposure.",
        "tool_calls": build_tool_calls(tools),
        "summary": f"Sent personalized follow-up email to {lead['name']} ({lead['email']}) at {lead['company']}. Email references their {lead['stage']} stage and ${lead['deal_value']:,} opportunity. CRM record updated with activity log.",
        "tokens_used": ["hubspot", "gmail"],
        "auth0_integration": {
            "token_vault_calls": 2,
            "tokens_refreshed": 1,
            "scopes_verified": True,
            "zero_token_exposure": True
        }
    }

def handle_meeting(task):
    lead = LEADS_DB[3]
    tools = [
        ("auth0.tokenVault.getToken", "hubspot", {"token_status": "valid"}),
        ("hubspot.crm.contacts.get", "hubspot", {"contact": lead}),
        ("auth0.tokenVault.getToken", "calendly", {"token_status": "valid"}),
        ("calendly.availability.check", "calendly", {
            "available_slots": [
                {"start": "2026-04-07T10:00:00Z", "end": "2026-04-07T10:30:00Z"},
                {"start": "2026-04-07T14:00:00Z", "end": "2026-04-07T14:30:00Z"},
                {"start": "2026-04-08T09:00:00Z", "end": "2026-04-08T09:30:00Z"}
            ]
        }),
        ("auth0.tokenVault.getToken", "gmail", {"token_status": "valid"}),
        ("gmail.messages.send", "gmail", {
            "message_id": "msg_ax_20260404_002",
            "to": lead["email"],
            "subject": f"Meeting invitation - {lead['company']} x AXIONAuth",
            "status": "sent",
            "includes_calendly_link": True
        }),
        ("auth0.tokenVault.getToken", "slack", {"token_status": "valid"}),
        ("slack.chat.postMessage", "slack", {
            "channel": "#sales-pipeline",
            "text": f"Meeting invite sent to {lead['name']} ({lead['company']}) for ${lead['deal_value']:,} deal",
            "ts": "1743782400.001234"
        })
    ]
    return {
        "agent": "AXIONAuth",
        "task": task,
        "reasoning": "Orchestrated across 4 services using Auth0 Token Vault: fetched contact from CRM, checked calendar availability, sent meeting invite via email, notified sales team on Slack. Each token securely managed.",
        "tool_calls": build_tool_calls(tools),
        "summary": f"Meeting invitation sent to {lead['name']} ({lead['title']}, {lead['company']}). 3 available slots found for next week. Email sent with Calendly link. Sales team notified in #sales-pipeline. Deal value: ${lead['deal_value']:,}.",
        "tokens_used": ["hubspot", "calendly", "gmail", "slack"],
        "auth0_integration": {
            "token_vault_calls": 4,
            "tokens_refreshed": 0,
            "scopes_verified": True,
            "zero_token_exposure": True
        }
    }

def handle_full_cycle(task):
    lead = LEADS_DB[4]
    tools = [
        ("auth0.tokenVault.getToken", "hubspot", {"token_status": "valid"}),
        ("hubspot.crm.contacts.search", "hubspot", {"new_leads": [lead]}),
        ("agent.qualifyLead", "hubspot", {"lead_id": lead["id"], "qualification": "MQL", "fit_score": 82, "intent_signals": ["visited pricing page", "downloaded whitepaper", "attended webinar"]}),
        ("hubspot.crm.deals.create", "hubspot", {"deal_id": "D-5001", "amount": lead["deal_value"], "stage": "Qualified", "associated_contact": lead["id"]}),
        ("auth0.tokenVault.getToken", "gmail", {"token_status": "refreshed", "new_expiry": 3600}),
        ("gmail.messages.send", "gmail", {"message_id": "msg_ax_20260404_003", "to": lead["email"], "subject": f"Welcome to AXIONAuth, {lead['name'].split()[0]}!", "status": "sent", "template": "new_lead_nurture_v2"}),
        ("auth0.tokenVault.getToken", "calendly", {"token_status": "valid"}),
        ("calendly.events.create", "calendly", {"event_id": "evt_ax_001", "type": "Discovery Call", "duration": 30, "invitee": lead["email"]}),
        ("auth0.tokenVault.getToken", "slack", {"token_status": "valid"}),
        ("slack.chat.postMessage", "slack", {"channel": "#sales-pipeline", "text": f"New qualified lead: {lead['name']} ({lead['company']}) - ${lead['deal_value']:,}", "ts": "1743782500.005678"})
    ]
    return {
        "agent": "AXIONAuth",
        "task": task,
        "reasoning": "Executed full sales cycle automation: identified new lead, qualified via scoring model, created deal in CRM, sent personalized welcome email, scheduled discovery call, and notified team. Auth0 Token Vault managed all 4 service tokens securely throughout the workflow.",
        "tool_calls": build_tool_calls(tools),
        "summary": f"Full sales cycle completed for {lead['name']} ({lead['title']}, {lead['company']}): Lead qualified (score 82), deal created (${lead['deal_value']:,}), welcome email sent, discovery call scheduled, team notified. All 4 API integrations secured via Auth0 Token Vault with zero token exposure.",
        "tokens_used": ["hubspot", "gmail", "calendly", "slack"],
        "auth0_integration": {
            "token_vault_calls": 4,
            "tokens_refreshed": 1,
            "scopes_verified": True,
            "zero_token_exposure": True
        }
    }

def handle_token_status(task):
    vault_info = {}
    for k, v in TOKENS.items():
        vault_info[k] = {
            **v,
            "token_preview": f"eyJ***{random.randint(1000,9999)}",
            "vault_encrypted": True,
            "rotation_policy": "auto_refresh_on_expiry"
        }
    tools = [
        ("auth0.tokenVault.listTokenSets", "hubspot", {"total_token_sets": len(TOKENS), "services": list(TOKENS.keys())}),
        ("auth0.tokenVault.audit", "hubspot", {
            "total_token_retrievals_24h": 147,
            "total_refreshes_24h": 32,
            "failed_auth_attempts": 0,
            "revocations_24h": 0,
            "avg_vault_latency_ms": 23.4
        })
    ]
    return {
        "agent": "AXIONAuth",
        "task": task,
        "reasoning": "Queried Auth0 Token Vault for all managed token sets and ran security audit. All tokens are active, encrypted at rest, and auto-refreshing. Zero security incidents detected.",
        "tool_calls": build_tool_calls(tools),
        "summary": f"Token Vault Status: {len(TOKENS)} active connections, all healthy. 147 token retrievals in last 24h, 32 auto-refreshes, 0 failures. Average vault latency: 23.4ms. All tokens encrypted at rest with AES-256.",
        "vault_status": vault_info,
        "tokens_used": list(TOKENS.keys()),
        "auth0_integration": {
            "token_vault_calls": 2,
            "tokens_refreshed": 0,
            "scopes_verified": True,
            "zero_token_exposure": True
        }
    }

def handle_security(task):
    tools = [
        ("auth0.tokenVault.securityReport", "hubspot", {
            "encryption": "AES-256-GCM at rest, TLS 1.3 in transit",
            "access_control": "OAuth 2.0 with PKCE, consent-based scoping",
            "audit_trail": "Full audit log with IP, timestamp, action",
            "token_isolation": "Agent never sees raw tokens - vault proxies all API calls",
            "rotation": "Automatic refresh before expiry, revocation on anomaly",
            "compliance": ["SOC2 Type II", "GDPR", "CCPA"]
        })
    ]
    return {
        "agent": "AXIONAuth",
        "task": task,
        "reasoning": "Generated comprehensive security report for Auth0 Token Vault integration. All security controls are active and compliant.",
        "tool_calls": build_tool_calls(tools),
        "summary": "Security posture: STRONG. All tokens encrypted (AES-256-GCM), agent never accesses raw tokens, full audit trail enabled, automatic rotation active. Compliant with SOC2, GDPR, CCPA.",
        "tokens_used": [],
        "auth0_integration": {
            "token_vault_calls": 1,
            "tokens_refreshed": 0,
            "scopes_verified": True,
            "zero_token_exposure": True
        }
    }

def classify_and_respond(task):
    t = task.lower()
    if any(w in t for w in ["lead", "crm", "pipeline", "contact", "prospect", "hubspot"]):
        return handle_leads(task)
    elif any(w in t for w in ["email", "send", "follow", "message", "gmail", "mail"]):
        return handle_email(task)
    elif any(w in t for w in ["meeting", "schedule", "book", "calendar", "call", "calendly"]):
        return handle_meeting(task)
    elif any(w in t for w in ["full", "cycle", "automate", "workflow", "end-to-end", "complete"]):
        return handle_full_cycle(task)
    elif any(w in t for w in ["token", "vault", "status", "auth", "security", "scope", "refresh"]):
        return handle_token_status(task)
    elif any(w in t for w in ["secure", "encrypt", "audit", "compliance", "protect"]):
        return handle_security(task)
    elif any(w in t for w in ["slack", "notify", "team", "channel"]):
        return handle_meeting(task)
    else:
        return handle_full_cycle(task)

@app.get("/", response_class=HTMLResponse)
async def root():
    html_path = Path(__file__).parent / "index.html"
    return HTMLResponse(content=html_path.read_text(), status_code=200)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "AXIONAuth Agent", "version": "3.0.0", "auth0_token_vault": "connected", "uptime_seconds": int(time.time()) % 86400}

@app.post("/api/agent/run")
async def agent_run(request: Request):
    body = await request.json()
    task = body.get("task", "")
    if not task:
        return JSONResponse({"error": "No task provided"}, status_code=400)
    return JSONResponse(classify_and_respond(task))

@app.get("/api/status")
async def status():
    return {
        "agent": "AXIONAuth",
        "version": "3.0.0",
        "status": "operational",
        "auth0_token_vault": {
            "connected": True,
            "active_connections": len(TOKENS),
            "total_token_sets": len(TOKENS),
            "vault_health": "healthy",
            "encryption": "AES-256-GCM",
            "last_audit": "2026-04-04T11:45:00Z"
        },
        "connected_services": {k: {"service": v["service"], "status": v["status"]} for k, v in TOKENS.items()},
        "uptime": "99.97%",
        "requests_24h": 1247
    }

@app.get("/api/tokens")
async def tokens():
    return {"token_vault": TOKENS, "total": len(TOKENS), "all_active": all(t["status"] == "active" for t in TOKENS.values())}

@app.post("/api/auth/connect")
async def connect_service(request: Request):
    body = await request.json()
    service = body.get("service", "unknown")
    return {
        "status": "connected",
        "service": service,
        "auth0_flow": {
            "type": "authorization_code_with_pkce",
            "connection_id": f"con_{service[:3]}_{random.randint(1000,9999)}",
            "token_set_id": f"tks_{service[:3]}_{random.randint(1000,9999)}",
            "scopes_granted": ["read", "write"],
            "consent": "user_approved"
        }
    }

SCENARIOS = {
    "1": ("Check CRM Leads", "Check my CRM for high-priority leads and recommend actions"),
    "2": ("Send Follow-up Email", "Send a follow-up email to our top lead with a personalized message"),
    "3": ("Book Meeting", "Schedule a meeting with our hottest prospect and notify the team"),
    "4": ("Full Sales Cycle", "Run the complete sales automation cycle for new leads"),
    "5": ("Token Vault Status", "Show me the Auth0 Token Vault status and security report"),
}

@app.get("/api/demo/scenario/{scenario_id}")
async def demo_scenario(scenario_id: str):
    if scenario_id not in SCENARIOS:
        return JSONResponse({"error": "Scenario not found. Use 1-5."}, status_code=404)
    name, task = SCENARIOS[scenario_id]
    result = classify_and_respond(task)
    result["scenario"] = {"id": scenario_id, "name": name}
    return JSONResponse(result)
