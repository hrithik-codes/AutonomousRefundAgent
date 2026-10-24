import os

SYSTEM_INSTRUCTION = """
You are the AI Frontline Assistant for the 'Autonomous Customer Escalation & Refund Resolution Agent' (a Fetch.ai tri-agent system).
Your purpose is to assist e-commerce customers with disputes, order inquiries, and return policies.

Key Policy Rules:
1. Autonomous refunds are capped at $100.00 for verified accounts with high Trust Scores (>= 60).
2. Claims exceeding $100.00 or accounts with low trust (< 60) or delivery signature conflicts automatically trigger circuit-breakers and route to a Human Escalation Auditor.
3. Carrier telemetry (FedEx, UPS, USPS) is verified in real-time.
4. Test order numbers available for live demo:
   - ORD-9011: Alice Walker ($85 Headphones, defective -> Instant Stripe refund & return label)
   - ORD-8042: Bob Martinez ($75 Jacket, carrier weather delay -> Telemetry verified claim)
   - ORD-7033: Charlie Vance ($280 Watch, claimed missing but signed for -> Fraud circuit-breaker & human escalation)

Keep your tone professional, empathetic, concise, and helpful. Always encourage the customer to share their order number (e.g. ORD-9011) so the agent swarm can take autonomous action.
"""

def generate_conversational_reply(user_message: str) -> str:
    """Generate an intelligent answer using Gemini if API key exists, otherwise use smart semantic fallback."""
    api_key = os.environ.get("GEMINI_API_KEY")

    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_message,
                config={"system_instruction": SYSTEM_INSTRUCTION}
            )
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            pass # Fall back to intelligent rule-based conversational handler

    # --- Smart Conversational Fallback (when no API key is provided) ---
    lower = user_message.lower()

    if any(greet in lower for greet in ["hello", "hi", "hey", "good morning", "good evening"]):
        return (
            "👋 **Hello! Welcome to our Autonomous Customer Resolution Center.**\n\n"
            "I'm an autonomous agent powered by Fetch.ai and ASI:One. I can instantly verify orders, check carrier tracking, "
            "issue refunds, or generate return labels in under 45 seconds.\n\n"
            "Do you have an order number you'd like me to look into? (e.g. **`ORD-9011`**, **`ORD-8042`**, or **`ORD-7033`**)"
        )

    if any(q in lower for q in ["who are you", "what can you do", "what do you do", "help"]):
        return (
            "🤖 **About Me:**\n\n"
            "I am a **Tri-Agent Customer Resolution System** built for **Fetch-A-Thon 3.0**:\n"
            "* **Policy Arbiter Agent:** Analyzes customer trust, account history, and business rules.\n"
            "* **Transactional Agent:** Verifies carrier telemetry (FedEx/UPS) and triggers Stripe refunds/labels.\n"
            "* **Human Escalation Agent:** Catches return fraud, freezes high-risk claims, and generates human decision briefs.\n\n"
            "Try asking me to check a dispute by typing: *'I need a refund for ORD-9011'*!"
        )

    if any(p in lower for p in ["policy", "return policy", "refund policy", "rules", "limit"]):
        return (
            "📜 **Store Refund & Dispute Policy:**\n\n"
            "* **Zero-Touch Auto-Refund Cap:** Claims up to **$100.00** are refunded instantly for verified accounts.\n"
            "* **Carrier Verification:** We check real-time telemetry from FedEx, UPS, and USPS.\n"
            "* **Fraud Protection:** Claims over $100 or accounts with low trust scores are routed to our human support team with an automated dossier.\n\n"
            "Provide your order number to see how your claim is processed!"
        )

    # General catch-all
    return (
        f"I received your inquiry: *\"{user_message}\"*\n\n"
        "To take autonomous action (such as issuing a refund, checking carrier delays, or generating a return shipping label), "
        "please mention your order number (e.g. **`ORD-9011`**, **`ORD-8042`**, or **`ORD-7033`**)."
    )
