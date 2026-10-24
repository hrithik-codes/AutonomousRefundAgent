# Autonomous Customer Escalation & Refund Resolution Agent

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

> **Built for Fetch-A-Thon 3.0: "From Intent to Action"**  
> An autonomous Tri-Agent architecture powered by **uAgents & ASI:One** that replaces slow 3–5 day dispute cycles with sub-45-second verified resolutions—cutting support labor costs by 84% while strictly preventing fraud via carrier telemetry and deterministic circuit-breakers.

---

## 📊 Business Case & Financial ROI

Retailers lose over **$100 Billion annually** to return fraud and support labor friction ($15–$45 per manual claim investigation). 

| Operational Tier | Monthly Volume (50k orders/mo) | Cost per Incident | Monthly Expenditure |
| :--- | :--- | :--- | :--- |
| **Status Quo (100% Manual)** | 2,000 tickets | $20.00 avg | $40,000 / mo ($480k / yr) |
| **Autonomous Agent Tier (70% routine)** | 1,400 tickets | $0.30 API compute | $420 / mo |
| **Human Escalation Tier (30% edge-cases)** | 600 tickets | $10.00 (half review time) | $6,000 / mo |
| **Blended Total with AI System** | **2,000 tickets** | **$3.21 blended avg** | **$6,420 / mo ($77k / yr)** |
| **Net Bottom-Line Direct Savings** | — | **84% net cost drop** | **+$402,960 / year direct savings** |

---

## 🤖 Tri-Agent System Architecture

```
                       [ Customer in ASI:One Chat ]
                                     │
                                     │ (Agent Chat Protocol - ACP)
                                     ▼
                ┌──────────────────────────────────────────┐
                │   Agent 1: Policy Arbiter (Evaluator)     │
                │  - Computes dynamic Trust Score (1-100)  │
                │  - Checks $100 auto-refund cap           │
                │  - Cross-references Carrier Telemetry    │
                └────────────────────┬─────────────────────┘
                                     │
                  ┌──────────────────┴──────────────────┐
                  │                                     │
        [ Verified Claim ]                     [ Breached Threshold ]
                  │                                     │
                  ▼                                     ▼
┌───────────────────────────────────┐ ┌───────────────────────────────────┐
│ Agent 2: Transactional Executor   │ │ Agent 3: Human Escalation Guard   │
│ - Live Carrier Telemetry Check    │ │ - Deterministic Circuit-Breaker   │
│ - Idempotent Stripe Refund Tx     │ │ - Synthesized 3-Bullet Dossier    │
│ - Prepaid Return Label Emitted    │ │ - Pauses payout & notifies lead   │
│ - Immutable DB Audit Log          │ │ - Human-in-the-Loop ticket queued │
└───────────────────────────────────┘ └───────────────────────────────────┘
```

---

## 🧪 Interactive Test Personas (Try in ASI:One)

Once connected to **ASI:One**, you can test the system with any of the following 3 orders:

1. **`ORD-9011` (Alice Walker – VIP High-Trust Buyer)**
   * *Claim:* "My wireless headphones have audio crackling defects."
   * *Outcome:* **Instant Autonomous Approval (< 0.4s)**. Issues Stripe refund and generates prepaid FedEx return label.
2. **`ORD-8042` (Bob Martinez – Carrier Delay)**
   * *Claim:* "I never received my trail jacket, tracking is stuck."
   * *Outcome:* **Carrier Telemetry Validation**. Detects severe weather delay exception and issues courtesy credit.
3. **`ORD-7033` (Charlie Vance – High Risk / Return Abuse)**
   * *Claim:* "I never received the $280 watch, refund me now."
   * *Outcome:* **Circuit-Breaker Triggered**. Detects account trust score < 50, amount > $100 cap, and carrier telemetry proof (signed delivery). Generates a 3-bullet dossier and halts the refund.

---

## 🚀 Running the Agent Locally

### 1. Requirements
* Python 3.10 – 3.13
* `uagents>=0.25.5`
* `uagents-core`
* `certifi`

### 2. Launch
```bash
python3 agent.py
```

The agent runs with `mailbox=True` and connects automatically to your Agentverse Mailbox!
