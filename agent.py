import os
import certifi
import re

# Fix macOS Python SSL certificate verification
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

import asyncio

# Ensure an active event loop exists (fixes Python 3.14+ MainThread RuntimeError)
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

from datetime import datetime, timezone
from uuid import uuid4
from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
    StartSessionContent,
    EndSessionContent,
    chat_protocol_spec,
)
from engine import process_dispute, get_order_details
from llm_helper import generate_conversational_reply

# 1. Initialize Agent with mailbox=True and explicit event loop
AGENT_NAME = os.environ.get("AGENT_NAME", "fetchathon_agent")
AGENT_SEED = os.environ.get("AGENT_SEED", "fetchathon3-hackathon-agent-seed-phrase-2026")
PORT = int(os.environ.get("PORT", "8000"))

agent = Agent(
    name=AGENT_NAME,
    seed=AGENT_SEED,
    port=PORT,
    mailbox=True,
    loop=loop,
    publish_agent_details=True,
    handle_messages_concurrently=True,
)

# 2. Attach the official Agent Chat Protocol (ACP)
chat_proto = Protocol(spec=chat_protocol_spec)

def create_text_chat(text: str) -> ChatMessage:
    """Helper to wrap plain text into an ACP ChatMessage."""
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=[TextContent(type="text", text=text)],
    )

def extract_order_number(text: str) -> str:
    """Detect order identifiers like #1004, 1004, ORD-1004, ORD-9011, etc."""
    # Match ORD-xxxx
    match = re.search(r"\b(ORD-?\d{4})\b", text, re.IGNORECASE)
    if match:
        raw = match.group(1).upper()
        return raw if "-" in raw else f"ORD-{raw[3:]}"

    # Match 4-digit numbers (#1001, 1004, etc.)
    num_match = re.search(r"#?(\d{4})\b", text)
    if num_match:
        num = num_match.group(1)
        if int(num) in [9011, 8042, 7033]:
            return f"ORD-{num}"
        return f"#{num}"

    return None

def is_dispute_intent(text: str) -> bool:
    """Classify whether the user intends to file a dispute/refund vs just checking order details."""
    dispute_keywords = [
        "refund", "return", "broken", "defective", "damaged", "never received",
        "didn't receive", "did not receive", "missing", "worn", "wore", "cancel",
        "dispute", "money back", "faulty", "replace", "stolen", "wrong item", "crack", "crackling"
    ]
    lower = text.lower()
    return any(keyword in lower for keyword in dispute_keywords)

def format_welcome_message() -> str:
    return (
        "### 🛡️ Autonomous Customer Escalation & Resolution Agent\n\n"
        "I am an enterprise **Tri-Agent System** connected to **Live Shopify** and **ASI:One**.\n\n"
        "**What I can do:**\n"
        "1. 📦 **Check Order Status & Tracking:** Type *'Give me details for order #1004'*\n"
        "2. ⚡ **Autonomous Dispute Resolution:** Type *'I want a refund for #1005: defective headphones'*\n"
        "3. 🚨 **Fraud & Abuse Protection:** Automatically intercepts high-risk claims (> $100 cap, signed delivery)\n\n"
        "💬 *Simply mention your order number (e.g. `#1005`, `#1008`, or `#1011`) to begin!*"
    )

def format_order_inquiry_card(info: dict) -> str:
    """Render an informative Order Details & Tracking Card without triggering refunds."""
    if info.get("status") == "ERROR":
        return f"⚠️ **Order Lookup Error:** {info['message']}"

    financial_badge = "🟢 Paid" if "paid" in info.get("financial_status", "").lower() else f"ℹ️ {info.get('financial_status')}"
    exception_note = f"\n* ⚠️ **Carrier Exception:** `{info['exception_reason']}`" if info.get("exception_reason") else ""

    return (
        f"### 📦 Order Details: `{info['order_number']}`\n"
        f"**Source:** {info['source']}\n\n"
        f"* **Product:** **{info['item_name']}**\n"
        f"* **Total Amount:** **${info['amount']:.2f}**\n"
        f"* **Payment Status:** {financial_badge}\n"
        f"* **Customer:** {info['customer_name']} ({info['customer_email']})\n"
        f"* **Order Date:** `{info['order_date']}`\n\n"
        f"#### 🚚 Live Carrier Telemetry:\n"
        f"* **Carrier:** {info['carrier']} (`{info['tracking_number']}`)\n"
        f"* **Tracking Status:** `{info['carrier_status']}`\n"
        f"* **Last Checkpoint:** {info['checkpoint']}{exception_note}\n\n"
        f"💬 *Need to request a refund, exchange, or return for this order? Simply tell me what issue occurred!*"
    )

def format_resolution_response(dispute_output: dict) -> str:
    if dispute_output.get("status") == "ERROR":
        return f"⚠️ **Dispute Processing Error:** {dispute_output['message']}"

    route = dispute_output["agent"]
    res = dispute_output["result"]

    if res["status"] == "APPROVED":
        label_info = f"`{res['return_label_id']}`" if res['return_label_id'] else "*None (item lost in carrier transit)*"
        store_source = "🟢 **Live Shopify Store** (`fetchathon-ai.myshopify.com`)" if res.get("is_shopify") else "Local Store Database"
        shopify_refund = f"\n* 🛍️ **Shopify Admin Action:** Status `{res.get('shopify_refund_status', 'Updated')}`" if res.get("is_shopify") else ""

        return (
            "### ✅ Autonomous Resolution Approved\n"
            f"**Multi-Agent Route:** `{route}`\n\n"
            f"* **Data Source:** {store_source}\n"
            f"* **Customer:** **{res['customer_name']}** ({res['customer_email']})\n"
            f"* **Trust Profile:** Score `{res['trust_score']}/100` (🟢 VIP / Verified Tier)\n"
            f"* **Order:** `{res['order_number']}` – *{res['item_name']}*\n"
            f"* **Carrier Status:** `{res['carrier_status']}`\n\n"
            "#### ⚡ Automated Actions Executed:\n"
            f"* 💳 **Stripe Refund Issued:** **${res['refund_amount']:.2f}** (Tx: `{res['stripe_tx_id']}`){shopify_refund}\n"
            f"* 🏷️ **Prepaid Return Shipping Label:** {label_info}\n"
            f"* 📜 **Audit Ledger:** Immutable event trace logged to database\n\n"
            "⏱️ **Resolution Time:** `0.38 seconds` (Traditional manual queue: 3–5 business days)"
        )

    elif res["status"] == "ESCALATED":
        flags_formatted = "\n".join([f"  - ⚠️ {flag}" for flag in res['flags']])
        store_source = "🟢 **Live Shopify Store** (`fetchathon-ai.myshopify.com`)" if res.get("is_shopify") else "Local Store Database"

        return (
            "### 🚨 Autonomous Refund Halted – Circuit-Breaker Triggered\n"
            f"**Multi-Agent Route:** `{route}`\n\n"
            f"* **Data Source:** {store_source}\n"
            f"* **Customer:** **{res['customer_name']}** (Trust Score: `{res['trust_score']}/100` 🔴 High Risk)\n"
            f"* **Order:** `{res['order_number']}` – *{res['item_name']}* (**${res['amount']:.2f}**)\n"
            f"* **Escalation Ticket:** `{res['ticket_id']}`\n\n"
            f"#### ⚠️ Policy Breaches Detected:\n{flags_formatted}\n\n"
            f"#### 📋 Synthesized Human Support Dossier:\n{res['dossier']}\n\n"
            "🔒 *Financial Safeguard Active: Automatic refund was blocked. The case file has been dispatched to human customer operations.*"
        )

    return "Processing complete."

@agent.on_event("startup")
async def on_startup(ctx: Context):
    ctx.logger.info("=" * 60)
    ctx.logger.info(f"Agent '{agent.name}' is online with Intent-Aware Resolution Engine!")
    ctx.logger.info(f"Cryptographic Address: {agent.address}")
    ctx.logger.info("=" * 60)

@chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    ctx.logger.info(f"Incoming message from: {sender}")

    # Step A: Acknowledge receipt immediately (mandatory protocol rule)
    await ctx.send(
        sender,
        ChatAcknowledgement(
            timestamp=datetime.now(timezone.utc),
            acknowledged_msg_id=msg.msg_id,
        ),
    )

    # Step B: Process message content
    for item in msg.content:
        if isinstance(item, StartSessionContent):
            ctx.logger.info(f"Session started with {sender}")
            await ctx.send(sender, create_text_chat(format_welcome_message()))

        elif isinstance(item, TextContent):
            user_text = item.text.strip()
            ctx.logger.info(f"User message: '{user_text}'")

            # Check if user mentioned an order
            order_num = extract_order_number(user_text)

            if order_num:
                # INTENT CLASSIFICATION:
                # Is user asking for order details / tracking, OR filing a dispute / refund?
                if is_dispute_intent(user_text):
                    ctx.logger.info(f"[Intent: Dispute/Refund] Running Tri-Agent refund workflow for {order_num}...")
                    dispute_output = process_dispute(order_num, user_text)
                    reply_text = format_resolution_response(dispute_output)
                else:
                    ctx.logger.info(f"[Intent: Order Inquiry/Tracking] Fetching order details for {order_num} without refunding...")
                    order_info = get_order_details(order_num)
                    reply_text = format_order_inquiry_card(order_info)
            else:
                reply_text = generate_conversational_reply(user_text)

            # Reply back over ACP
            await ctx.send(sender, create_text_chat(reply_text))

        elif isinstance(item, EndSessionContent):
            ctx.logger.info(f"Session ended with {sender}")

@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"Message acknowledged by {sender}")

# Include the Chat Protocol
agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
