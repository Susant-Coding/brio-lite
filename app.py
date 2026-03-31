"""
BRIO Lite — AI-Powered Order-to-Cash Operations Agent
Built with Google Gemini 2.0 Flash | Google Gen AI Academy APAC Edition
"""

import streamlit as st
import google.generativeai as genai
import json
import random
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
#  MOCK DATA  (simulates a real OTC backend)
# ─────────────────────────────────────────────────────────────────────────────

ORDERS = {
    "ORD-2026-001": {
        "customer": "Raj Motors Pvt Ltd", "dealer_id": "DLR-101",
        "product": "Bridgestone Turanza T005 205/55R16", "quantity": 40,
        "status": "Processing", "order_date": "2026-03-25",
        "eta": "2026-04-02", "amount_inr": 128000,
    },
    "ORD-2026-002": {
        "customer": "Mumbai Fleet Services", "dealer_id": "DLR-205",
        "product": "Bridgestone Ecopia EP150 185/65R15", "quantity": 100,
        "status": "Shipped", "order_date": "2026-03-20",
        "eta": "2026-03-31", "amount_inr": 285000,
    },
    "ORD-2026-003": {
        "customer": "Delhi Tyre Hub", "dealer_id": "DLR-089",
        "product": "Bridgestone Potenza Sport 225/45R17", "quantity": 20,
        "status": "Delivered", "order_date": "2026-03-15",
        "eta": "2026-03-22", "amount_inr": 96000,
    },
}

WARRANTY_CLAIMS = {
    "WC-2026-501": {
        "dealer_id": "DLR-101", "customer": "Raj Motors Pvt Ltd",
        "product": "Bridgestone Turanza T005", "issue": "Premature tread wear",
        "status": "Under Review", "filed_date": "2026-03-10",
        "resolution": "Pending field inspection report",
    },
    "WC-2026-502": {
        "dealer_id": "DLR-205", "customer": "Mumbai Fleet Services",
        "product": "Bridgestone Ecopia EP150", "issue": "Sidewall bulge detected",
        "status": "Approved", "filed_date": "2026-03-05",
        "resolution": "Replacement approved — 4 units to be dispatched",
    },
}

DEALERS = {
    "DLR-101": {
        "name": "Raj Motors Pvt Ltd", "city": "Bengaluru", "tier": "Gold",
        "contact": "rajmotors@example.com", "ytd_revenue_inr": 450000,
        "active_since": "2018-06-01", "fleet_account": False,
    },
    "DLR-205": {
        "name": "Mumbai Fleet Services", "city": "Mumbai", "tier": "Platinum",
        "contact": "fleet@mfs.example.com", "ytd_revenue_inr": 1200000,
        "active_since": "2015-01-15", "fleet_account": True,
    },
    "DLR-089": {
        "name": "Delhi Tyre Hub", "city": "Delhi", "tier": "Silver",
        "contact": "dth@example.com", "ytd_revenue_inr": 210000,
        "active_since": "2020-03-20", "fleet_account": False,
    },
}

# ─────────────────────────────────────────────────────────────────────────────
#  TOOL FUNCTIONS  (these are called by Gemini automatically)
# ─────────────────────────────────────────────────────────────────────────────

def check_order_status(order_id: str) -> dict:
    """Check the live status of a customer order using its order ID.

    Args:
        order_id: The order ID to look up, e.g. ORD-2026-001.

    Returns:
        Full order details including status, ETA, product, and customer name.
    """
    data = ORDERS.get(order_id.upper())
    if data:
        return {"found": True, "order_id": order_id.upper(), **data}
    return {
        "found": False,
        "error": f"Order '{order_id}' not found.",
        "hint": f"Valid orders: {', '.join(ORDERS)}",
    }


def check_warranty_claim(claim_id: str) -> dict:
    """Look up the status and resolution of a warranty claim by claim ID.

    Args:
        claim_id: The warranty claim ID, e.g. WC-2026-501.

    Returns:
        Claim details including issue description, status, and resolution action.
    """
    data = WARRANTY_CLAIMS.get(claim_id.upper())
    if data:
        return {"found": True, "claim_id": claim_id.upper(), **data}
    return {
        "found": False,
        "error": f"Claim '{claim_id}' not found.",
        "hint": f"Valid claims: {', '.join(WARRANTY_CLAIMS)}",
    }


def get_dealer_profile(dealer_id: str) -> dict:
    """Retrieve a dealer's full profile including tier, city, and YTD revenue.

    Args:
        dealer_id: The dealer ID, e.g. DLR-101.

    Returns:
        Dealer profile with tier, contact, YTD revenue, and fleet account flag.
    """
    data = DEALERS.get(dealer_id.upper())
    if data:
        return {"found": True, "dealer_id": dealer_id.upper(), **data}
    return {
        "found": False,
        "error": f"Dealer '{dealer_id}' not found.",
        "hint": f"Valid dealers: {', '.join(DEALERS)}",
    }


def list_all_orders() -> dict:
    """List all orders currently in the OTC system with status and amount.

    Returns:
        Summary list of all orders.
    """
    return {
        "total_orders": len(ORDERS),
        "orders": [
            {
                "order_id": k,
                "customer": v["customer"],
                "status": v["status"],
                "amount_inr": v["amount_inr"],
                "eta": v["eta"],
            }
            for k, v in ORDERS.items()
        ],
    }


def list_all_dealers() -> dict:
    """List all registered dealers with their tier and city.

    Returns:
        Summary list of all dealers.
    """
    return {
        "total_dealers": len(DEALERS),
        "dealers": [
            {
                "dealer_id": k,
                "name": v["name"],
                "city": v["city"],
                "tier": v["tier"],
                "fleet_account": v["fleet_account"],
            }
            for k, v in DEALERS.items()
        ],
    }


def create_dr_request(dealer_id: str, product: str, quantity: int, reason: str) -> dict:
    """Create a new Dealer Request (DR) for additional inventory or products.

    Args:
        dealer_id: The dealer making the request, e.g. DLR-101.
        product: Name of the product being requested.
        quantity: Number of units required.
        reason: Business justification for the request.

    Returns:
        Confirmation with DR ID and submission status.
    """
    if dealer_id.upper() not in DEALERS:
        return {"success": False, "error": f"Dealer '{dealer_id}' not found."}
    dr_id = f"DR-2026-{random.randint(100, 999)}"
    dealer_name = DEALERS[dealer_id.upper()]["name"]
    return {
        "success": True,
        "dr_id": dr_id,
        "dealer_id": dealer_id.upper(),
        "dealer_name": dealer_name,
        "product": product,
        "quantity": quantity,
        "reason": reason,
        "status": "Submitted for Approval",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": f"✅ DR {dr_id} created for {dealer_name} and sent for approval.",
    }


AGENT_TOOLS = [
    check_order_status,
    check_warranty_claim,
    get_dealer_profile,
    list_all_orders,
    list_all_dealers,
    create_dr_request,
]

SYSTEM_PROMPT = """You are BRIO Lite, an intelligent AI-powered Order-to-Cash (OTC) Operations Agent built for Bridgestone GCC.

You assist operations teams with:
- 📦 Real-time order status tracking
- 🔧 Warranty claim lookups and resolution tracking
- 🏪 Dealer profile and tier management
- 📋 Dealer Request (DR) creation
- 🚗 Fleet account inquiries

Guidelines:
- Always use your tools to fetch live data before answering
- Present data in clean, readable markdown tables or bullet points
- Be concise and action-oriented — operations teams are busy
- Suggest logical next steps after each response
- If an ID isn't found, show available options from the hint

Sample IDs to try:
- Orders: ORD-2026-001, ORD-2026-002, ORD-2026-003
- Warranty Claims: WC-2026-501, WC-2026-502
- Dealers: DLR-101 (Bengaluru/Gold), DLR-205 (Mumbai/Platinum), DLR-089 (Delhi/Silver)
"""

# ─────────────────────────────────────────────────────────────────────────────
#  DEMO MODE RESPONSES
# ─────────────────────────────────────────────────────────────────────────────

def get_demo_response(prompt: str) -> str:
    p = prompt.lower()

    if any(x in p for x in ["all order", "show order", "list order", "current order"]):
        return """Here's a summary of all **3 current orders** in the OTC system:

| Order ID | Customer | Product | Qty | Status | Amount (₹) | ETA |
|---|---|---|---|---|---|---|
| ORD-2026-001 | Raj Motors Pvt Ltd | Turanza T005 205/55R16 | 40 | 🔄 Processing | 1,28,000 | 2 Apr 2026 |
| ORD-2026-002 | Mumbai Fleet Services | Ecopia EP150 185/65R15 | 100 | 🚚 Shipped | 2,85,000 | 31 Mar 2026 |
| ORD-2026-003 | Delhi Tyre Hub | Potenza Sport 225/45R17 | 20 | ✅ Delivered | 96,000 | 22 Mar 2026 |

**Total pipeline value: ₹5,09,000**

💡 *Next steps: ORD-2026-002 is arriving today — want me to notify the dealer?*"""

    elif "001" in p:
        return """**Order ORD-2026-001** — Full Details

| Field | Value |
|---|---|
| 👤 Customer | Raj Motors Pvt Ltd |
| 🏪 Dealer ID | DLR-101 (Bengaluru · Gold Tier) |
| 📦 Product | Bridgestone Turanza T005 205/55R16 |
| 🔢 Quantity | 40 units |
| 💰 Amount | ₹1,28,000 |
| 📅 Order Date | 25 Mar 2026 |
| 🔄 Status | **Processing** |
| 🚚 ETA | 2 Apr 2026 |

⚠️ *Order is still being processed. Want me to escalate for faster dispatch?*"""

    elif "002" in p:
        return """**Order ORD-2026-002** — Full Details

| Field | Value |
|---|---|
| 👤 Customer | Mumbai Fleet Services |
| 🏪 Dealer ID | DLR-205 (Mumbai · Platinum Tier) |
| 📦 Product | Bridgestone Ecopia EP150 185/65R15 |
| 🔢 Quantity | 100 units |
| 💰 Amount | ₹2,85,000 |
| 📅 Order Date | 20 Mar 2026 |
| 🚚 Status | **Shipped** |
| 📬 ETA | **31 Mar 2026 — arriving today!** |

✅ *This is a fleet account — high priority. Delivery expected today.*"""

    elif "003" in p:
        return """**Order ORD-2026-003** — Full Details

| Field | Value |
|---|---|
| 👤 Customer | Delhi Tyre Hub |
| 🏪 Dealer ID | DLR-089 (Delhi · Silver Tier) |
| 📦 Product | Bridgestone Potenza Sport 225/45R17 |
| 🔢 Quantity | 20 units |
| 💰 Amount | ₹96,000 |
| 📅 Order Date | 15 Mar 2026 |
| ✅ Status | **Delivered** |
| 📬 Delivered On | 22 Mar 2026 |

✅ *Order successfully delivered. No further action needed.*"""

    elif "wc-2026-501" in p or "501" in p:
        return """**Warranty Claim WC-2026-501** — Status Report

| Field | Value |
|---|---|
| 🏪 Dealer | Raj Motors Pvt Ltd (DLR-101) |
| 📦 Product | Bridgestone Turanza T005 |
| ⚠️ Issue | Premature tread wear |
| 📅 Filed Date | 10 Mar 2026 |
| 🔄 Status | **Under Review** |
| 📋 Resolution | Pending field inspection report |

🔍 *Claim is under active review. Field inspection team has been assigned. Expected resolution: 3–5 business days.*

💡 *Want me to send a status update to the dealer?*"""

    elif "wc-2026-502" in p or "502" in p:
        return """**Warranty Claim WC-2026-502** — Status Report

| Field | Value |
|---|---|
| 🏪 Dealer | Mumbai Fleet Services (DLR-205) |
| 📦 Product | Bridgestone Ecopia EP150 |
| ⚠️ Issue | Sidewall bulge detected |
| 📅 Filed Date | 5 Mar 2026 |
| ✅ Status | **Approved** |
| 📋 Resolution | Replacement approved — 4 units to be dispatched |

✅ *Claim approved! Replacement dispatch is being coordinated with the warehouse.*"""

    elif "dlr-205" in p or "205" in p:
        return """**Dealer Profile — DLR-205**

| Field | Value |
|---|---|
| 🏪 Name | Mumbai Fleet Services |
| 📍 City | Mumbai |
| ⭐ Tier | **Platinum** |
| 📧 Contact | fleet@mfs.example.com |
| 💰 YTD Revenue | ₹12,00,000 |
| 📅 Active Since | 15 Jan 2015 |
| 🚗 Fleet Account | ✅ Yes |

🏆 *Platinum-tier fleet account — top priority dealer. YTD revenue tracking above target.*"""

    elif "dlr-101" in p or "raj motor" in p:
        return """**Dealer Profile — DLR-101**

| Field | Value |
|---|---|
| 🏪 Name | Raj Motors Pvt Ltd |
| 📍 City | Bengaluru |
| ⭐ Tier | **Gold** |
| 📧 Contact | rajmotors@example.com |
| 💰 YTD Revenue | ₹4,50,000 |
| 📅 Active Since | 1 Jun 2018 |
| 🚗 Fleet Account | ❌ No |

💡 *Gold-tier dealer with consistent ordering history. Consider upselling Potenza Sport range.*"""

    elif "dlr-089" in p or "delhi" in p:
        return """**Dealer Profile — DLR-089**

| Field | Value |
|---|---|
| 🏪 Name | Delhi Tyre Hub |
| 📍 City | Delhi |
| ⭐ Tier | **Silver** |
| 📧 Contact | dth@example.com |
| 💰 YTD Revenue | ₹2,10,000 |
| 📅 Active Since | 20 Mar 2020 |
| 🚗 Fleet Account | ❌ No |

📈 *Silver-tier dealer — growing steadily. Eligible for Gold tier at ₹5L YTD revenue.*"""

    elif any(x in p for x in ["all dealer", "list dealer", "dealer list", "dealer tier"]):
        return """Here are all **3 registered dealers** in the system:

| Dealer ID | Name | City | Tier | Fleet Account | YTD Revenue |
|---|---|---|---|---|---|
| DLR-101 | Raj Motors Pvt Ltd | Bengaluru | 🥇 Gold | No | ₹4,50,000 |
| DLR-205 | Mumbai Fleet Services | Mumbai | 💎 Platinum | ✅ Yes | ₹12,00,000 |
| DLR-089 | Delhi Tyre Hub | Delhi | 🥈 Silver | No | ₹2,10,000 |

**Total YTD Revenue across all dealers: ₹18,60,000**

💡 *Delhi Tyre Hub is close to Gold tier eligibility — consider a targeted promotion.*"""

    elif any(x in p for x in ["dr ", "dealer request", "create", "replenish", "restock"]):
        dr_id = f"DR-2026-{random.randint(700, 999)}"
        return f"""✅ **Dealer Request Created Successfully!**

| Field | Value |
|---|---|
| 📋 DR ID | **{dr_id}** |
| 🏪 Dealer | Raj Motors Pvt Ltd (DLR-101) |
| 📦 Product | Bridgestone Turanza T005 205/55R16 |
| 🔢 Quantity | 50 units |
| 📝 Reason | Q2 stock replenishment |
| 🔄 Status | **Submitted for Approval** |
| 🕐 Created | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} |

📬 *DR {dr_id} has been submitted to the approvals queue. Expected approval: 1–2 business days.*

💡 *Want me to check the status of other pending DRs for this dealer?*"""

    elif any(x in p for x in ["fleet", "fleet account"]):
        return """**Fleet Account Summary**

We currently have **1 active fleet account**:

| Dealer ID | Name | City | Tier | YTD Revenue |
|---|---|---|---|---|
| DLR-205 | Mumbai Fleet Services | Mumbai | 💎 Platinum | ₹12,00,000 |

🚗 *Fleet accounts get priority processing, dedicated support, and bulk pricing.*

💡 *Want to view open orders or warranty claims for this fleet account?*"""

    elif any(x in p for x in ["process", "processing"]):
        return """**Orders currently in Processing status:**

| Order ID | Customer | Product | Qty | Amount | Order Date |
|---|---|---|---|---|---|
| ORD-2026-001 | Raj Motors Pvt Ltd | Turanza T005 205/55R16 | 40 | ₹1,28,000 | 25 Mar 2026 |

⚠️ *1 order is still being processed. ETA: 2 Apr 2026.*

💡 *Want me to escalate this order for priority dispatch?*"""

    else:
        return """I'm **BRIO Lite**, your AI-powered OTC Operations Agent. Here's what I can help you with:

| Capability | Example Query |
|---|---|
| 📦 Order Tracking | *"Show me all orders"* or *"Status of ORD-2026-002"* |
| 🔧 Warranty Claims | *"Check warranty claim WC-2026-501"* |
| 🏪 Dealer Profiles | *"Get profile for DLR-205"* |
| 📋 DR Creation | *"Create a DR for DLR-101 — 50 units Turanza T005"* |
| 📊 Reports | *"List all dealers and their tiers"* |

**Available IDs:**
- Orders: `ORD-2026-001`, `ORD-2026-002`, `ORD-2026-003`
- Claims: `WC-2026-501`, `WC-2026-502`
- Dealers: `DLR-101`, `DLR-205`, `DLR-089`

What would you like to check? 🚀"""


# ─────────────────────────────────────────────────────────────────────────────
#  STREAMLIT UI
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="BRIO Lite — OTC Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* Header */
    .hero {
        background: linear-gradient(135deg, #CC0000 0%, #7a0000 100%);
        color: white;
        padding: 1.4rem 2rem;
        border-radius: 14px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .hero h1 { color: white; margin: 0; font-size: 1.7rem; }
    .hero p  { color: rgba(255,255,255,0.8); margin: 0.2rem 0 0 0; font-size: 0.88rem; }

    /* Sidebar sample prompts */
    .prompt-chip {
        background: #f0f4ff;
        border: 1px solid #c9d5ff;
        border-radius: 8px;
        padding: 0.4rem 0.7rem;
        font-size: 0.82rem;
        margin: 0.2rem 0;
        cursor: pointer;
        display: block;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #aaa;
        font-size: 0.75rem;
        margin-top: 0.5rem;
    }
    
    /* Hide default Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    demo_mode = st.toggle("🎮 Demo Mode (no API key needed)", value=True)
    if not demo_mode:
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            placeholder="AIza...",
            help="Get your free key at aistudio.google.com → Get API Key",
        )
        if api_key:
            st.success("✅ API Key configured")
        else:
            st.info("🔑 Paste your Gemini API key above to start")
    else:
        api_key = None
        st.success("🎮 Demo Mode active — no API key needed!")

    st.divider()

    st.markdown("## 💡 Sample Queries")
    sample_prompts = [
        "Show me all current orders",
        "Status of order ORD-2026-002?",
        "Check warranty claim WC-2026-501",
        "Get profile for dealer DLR-205",
        "List all dealers and their tiers",
        "Create a DR for DLR-101 — 50 units of Turanza T005 for Q2 stock replenishment",
        "Which orders are still being processed?",
        "How many fleet accounts do we have?",
    ]
    for p in sample_prompts:
        st.markdown(f"*• {p}*")

    st.divider()

    col1, col2, col3 = st.columns(3)
    col1.metric("Orders", len(ORDERS))
    col2.metric("Dealers", len(DEALERS))
    col3.metric("Claims", len(WARRANTY_CLAIMS))

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat = None
        st.rerun()

    st.markdown(
        '<p class="footer">Powered by Gemini 2.0 Flash<br>'
        "Google Gen AI Academy APAC 2026</p>",
        unsafe_allow_html=True,
    )

# ── Main area ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div>
        <h1>🤖 BRIO Lite &nbsp;·&nbsp; OTC Operations Agent</h1>
        <p>AI-Powered · Orders · Warranty Claims · Dealer Intelligence · DR Management &nbsp;|&nbsp; Powered by Gemini</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Greeting
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "👋 **Hello! I'm BRIO Lite**, your AI-powered OTC Operations Agent.\n\n"
            "I can help you with:\n"
            "- 📦 **Order tracking** — check status, ETA, and details\n"
            "- 🔧 **Warranty claims** — lookup status and resolutions\n"
            "- 🏪 **Dealer profiles** — tier, city, YTD revenue\n"
            "- 📋 **Dealer Requests (DR)** — create new requests instantly\n\n"
            "Try: *\"Show me all orders\"* or *\"Check warranty claim WC-2026-501\"*"
        ),
    })

if "chat" not in st.session_state:
    st.session_state.chat = None

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat Input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask about orders, warranties, dealers, or create a DR..."):
    if not demo_mode and not api_key:
        st.error("⚠️ Please enter your Gemini API key in the sidebar first.")
        st.stop()

    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    if demo_mode:
        # Demo mode — instant response, no API needed
        import time
        with st.chat_message("assistant"):
            with st.spinner("🤖 BRIO is thinking..."):
                time.sleep(0.8)
                reply = get_demo_response(prompt)
            st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
    else:
        # Live Gemini mode
        try:
            genai.configure(api_key=api_key)
            if st.session_state.chat is None:
                model = genai.GenerativeModel(
                    model_name="gemini-2.0-flash-lite",
                    tools=AGENT_TOOLS,
                    system_instruction=SYSTEM_PROMPT,
                )
                st.session_state.chat = model.start_chat(
                    enable_automatic_function_calling=True
                )
            with st.chat_message("assistant"):
                with st.spinner("🤖 Thinking..."):
                    response = st.session_state.chat.send_message(prompt)
                    reply = response.text
                st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            err = str(e)
            st.error(f"❌ Error: {err}")
            if "quota" in err.lower():
                st.warning("⏳ Quota exceeded. Switch to Demo Mode in the sidebar.")
