"""
Intelligent Carbon Copilot & Navigation Chatbot.
Provides natural-language app navigation, personalized enterprise metrics,
decarbonization intelligence, and 1-click action triggers.
"""

import streamlit as st
import re
from datetime import datetime
from database.db_manager import get_aggregated_activity_summary, get_activity_logs, get_user_profile
from components.calculations import calculate_carbon_credit_audit, generate_hotspot_recommendations
from components.icons import feather_icon, COLOR_SUCCESS, COLOR_WARNING, COLOR_INFO, COLOR_NEUTRAL

NAV_DESTINATIONS = {
    "dashboard": {"name": "Executive Dashboard", "icon": "pie-chart", "section": "dashboard", "step": 5},
    "activity_logs": {"name": "Daily & Weekly Activity Logs", "icon": "calendar", "section": "activity_logs", "step": 4},
    "leak_detection": {"name": "Emission Leak Detection", "icon": "alert-triangle", "section": "leak_detection", "step": 6},
    "carbon_credits": {"name": "Carbon Credit Ledger & Market", "icon": "dollar-sign", "section": "carbon_credits", "step": 7},
    "recommendations": {"name": "Green Recommendations", "icon": "zap", "section": "recommendations", "step": 8},
    "circular": {"name": "Circular Economy & 4R Framework", "icon": "refresh-cw", "section": "circular", "step": 10},
    "setup": {"name": "Business Profile & Setup", "icon": "settings", "section": "setup", "step": 3},
    "upload": {"name": "Upload Historical Data", "icon": "upload", "section": "upload", "step": 4},
    "reports": {"name": "Compliance Reports & Export", "icon": "download", "section": "reports", "step": 11},
    "settings": {"name": "Platform Settings", "icon": "sliders", "section": "settings", "step": 12},
}

def detect_navigation_intent(query: str):
    """Detects if user prompt intends to navigate to a specific section."""
    q = query.lower()
    if any(k in q for k in ["dashboard", "overview", "home", "main view", "kpi"]):
        return "dashboard"
    if any(k in q for k in ["activity", "daily", "weekly", "log fuel", "log waste", "meter", "log entry", "record", "logs"]):
        return "activity_logs"
    if any(k in q for k in ["recommend", "recommendation", "action plan", "green solution", "how to reduce", "decarbonize"]):
        return "recommendations"
    if any(k in q for k in ["leak", "hotspot", "waste point", "leakage", "diagnostics", "highest emission", "fix leak"]):
        return "leak_detection"
    if any(k in q for k in ["credit", "carbon credit", "quota", "trading", "offset", "deficit", "allowance", "market"]):
        return "carbon_credits"
    if any(k in q for k in ["circular", "4r", "recycle", "reuse", "scrap", "waste stream", "circular economy"]):
        return "circular"
    if any(k in q for k in ["setup", "profile", "business", "company info"]):
        return "setup"
    if any(k in q for k in ["upload", "import", "csv", "excel", "data file"]):
        return "upload"
    if any(k in q for k in ["report", "export", "pdf", "dossier", "download", "audit"]):
        return "reports"
    if any(k in q for k in ["setting", "theme", "dark mode", "factor", "config"]):
        return "settings"
    return None

def generate_copilot_response(user_prompt: str, user_email: str, company_name: str, res: dict) -> dict:
    """
    Generates personalized enterprise response with optional navigation target.
    Returns: {"text": str, "nav_target": str or None, "suggestions": list}
    """
    q = user_prompt.lower().strip()
    nav_target = detect_navigation_intent(q)
    
    user = st.session_state.get("current_user", {})
    user_name = user.get("owner_name", user.get("name", "David Kovac"))
    user_role = user.get("role", "Admin")

    # Extract live personalized company metrics
    total_co2 = res.get("total_co2", 0.0) if res else 0.0
    s_score = res.get("sustainability_score", 0.0) if res else 0.0
    govt_credits = res.get("govt_credits", 0.0) if res else 0.0
    credits_used = res.get("credits_used", 0.0) if res else 0.0
    credits_remaining = res.get("credits_remaining", 0.0) if res else 0.0
    credits_required = res.get("credits_required", 0.0) if res else 0.0
    is_deficit = res.get("is_deficit", False) if res else False
    comp_cost = res.get("compliance_cost", 0.0) if res else 0.0
    credit_price = res.get("credit_price", 38.0) if res else 38.0
    pillars = res.get("pillar_co2", {}) if res else {}
    grade = "Tier A (Industry Leader)" if s_score >= 75 else ("Tier B (Standard Compliant)" if s_score >= 50 else "Tier C (Action Needed)")
    
    # Live activity logs summary from SQLite
    agg_activity = get_aggregated_activity_summary(user_email)
    
    # 1. Navigation query (e.g. "Take me to leaks")
    if any(w in q for w in ["go to", "take me to", "navigate", "open", "switch to", "jump to", "show page"]) and nav_target:
        dest = NAV_DESTINATIONS[nav_target]
        text = f"Navigating you to **{dest['name']}** right away! You can also use the direct action button below."
        return {
            "text": text,
            "nav_target": nav_target,
            "auto_redirect": True,
            "suggestions": ["📊 Go to Dashboard", "🔥 Check Top Leaks", "📝 Log Today's Fuel"]
        }

    # 1.5 General Navigation Guidance
    if any(w in q for w in ["help me navigate", "how to navigate", "menu", "navigation guide", "where can i go", "where to go", "how to use"]):
        text = (
            f"### 🧭 Quick Navigation Guide for {company_name}\n\n"
            f"You can jump to any section using the 1-click buttons above, or ask me directly:\n"
            f"- **📊 Executive Dashboard**: High-level KPIs, Scope distribution, and live operational sync.\n"
            f"- **📅 Daily & Weekly Logs**: Record shift fuel, waste, electricity, delete records, and log sequential next-day shifts.\n"
            f"- **🔍 Emission Leak Hotspots**: Inspect your Top 10 industrial loss points and financial payback.\n"
            f"- **💰 Carbon Credits & Market**: Review statutory quotas, excess reserves, and compliance trading.\n"
            f"- **♻️ Circular Economy (4R)**: Explore industrial scrap reuse, recycling, and material alternatives.\n"
            f"- **⚙️ Business Profile & Setup**: Manage facility parameters and baseline quotas.\n\n"
            f"Where would you like to jump?"
        )
        return {
            "text": text,
            "nav_target": "dashboard",
            "suggestions": ["📊 Go to Dashboard", "📅 Open Daily Logs", "🔍 View Leak Points", "💰 Check Carbon Balance"]
        }

    # 2. Comprehensive Personalized Info & Profile Query
    if any(w in q for w in ["personalize", "personal info", "my info", "company info", "my company", "my details", "profile info", "about me", "who am i", "overview of my business"]):
        top_pillar = max(pillars.items(), key=lambda x: x[1]) if pillars else ("Operations", 0)
        text = (
            f"### 🏢 Personalized Enterprise Profile & Metrics\n\n"
            f"- **Organization**: `{company_name}`\n"
            f"- **Account Owner**: `{user_name}` ({user_role})\n"
            f"- **Annual Carbon Footprint**: `{total_co2:,.1f} tonnes CO₂e`\n"
            f"- **Primary Operational Leak**: `{top_pillar[0]}` ({top_pillar[1]:,.1f} t CO₂e)\n"
            f"- **Government Carbon Quota**: `{govt_credits:,.0f} credits`\n"
            f"- **Net Compliance Position**: `{'⚠️ Deficit: ' + f'{credits_required:,.1f} tonnes' if is_deficit else '🟢 Surplus: ' + f'{credits_remaining:,.1f} credits'}`\n"
            f"- **Statutory Financial Liability**: `${comp_cost:,.0f}` (benchmark `${credit_price:,.0f}/credit`)\n"
            f"- **Sustainability Eco-Score**: `{s_score:.0f} / 100` ({grade})\n"
            f"- **High-Frequency Ledger**: `{agg_activity['total_entries']} entries logged` (`{agg_activity['total_diesel_liters']:,.0f} L diesel`, `{agg_activity['total_gas_m3']:,.0f} m³ gas`, `{agg_activity['total_waste_kg']:,.0f} kg waste`)\n\n"
            f"Would you like to jump to any operational area or log new entries?"
        )
        return {
            "text": text,
            "nav_target": "dashboard",
            "suggestions": ["🔥 Check Top Leaks", "📝 Log Shift Activity", "💰 Check Carbon Balance", "📊 View Dashboard"]
        }

    # 2.5 Green Decarbonization Recommendations (Targeted to Hotspot Leaks)
    if any(w in q for w in ["recommend", "green recommend", "what should i do", "how to reduce", "how can i reduce", "cut emission", "solution", "action plan", "fix leak", "decarbonize"]):
        user_prof = get_user_profile(user_email) or {}
        hotspot_recs = generate_hotspot_recommendations(res, user_prof)
        top_3 = hotspot_recs[:3]
        rec_lines = []
        for i, rec in enumerate(top_3, 1):
            badge = "🔥 Hotspot #1 Fix" if rec.get("is_top_leak") else f"Targeted: {rec.get('targeted_leak')}"
            rec_lines.append(
                f"{i}. **{rec['title']}** ({badge})\n"
                f"   - **CO₂ Saved**: Cuts `{rec['co2_saved_t']:,.1f} t CO₂e/yr` ({rec['co2_saved_pct']:.1f}% of total)\n"
                f"   - **Financial Savings**: `${rec['annual_savings_usd']:,.0f}/yr` &bull; CapEx `{rec['cost_estimate']}` &bull; ROI `{rec['expected_roi']}`\n"
                f"   - **Incentive**: {rec.get('govt_incentives', 'Standard green transition tax credit')}"
            )
        recs_formatted = "\n\n".join(rec_lines)
        text = (
            f"### 💡 Hotspot-Targeted Green Recommendations for {company_name}\n\n"
            f"Based on your operational emission leak hotspots, here are the highest-return decarbonization interventions:\n\n"
            f"{recs_formatted}\n\n"
            f"Would you like to explore the interactive Green Recommendations workspace or simulate these interventions?"
        )
        return {
            "text": text,
            "nav_target": "recommendations",
            "suggestions": ["💡 Open Recommendations", "🧪 Test in Simulator", "📊 Return to Dashboard"]
        }

    # 3. Personalized Emissions & Footprint Queries
    if any(w in q for w in ["total emission", "carbon footprint", "how much co2", "my emission", "emissions", "footprint"]):
        top_pillar = max(pillars.items(), key=lambda x: x[1]) if pillars else ("Operations", 0)
        text = (
            f"### 🏢 {company_name} Carbon Assessment\n\n"
            f"- **Annual Gross Footprint**: `{total_co2:,.1f} tonnes CO₂e`\n"
            f"- **Primary Operational Hotspot**: `{top_pillar[0]}` ({top_pillar[1]:,.1f} t CO₂e, "
            f"representing {round((top_pillar[1]/max(total_co2, 0.001))*100, 1)}% of total footprint)\n"
            f"- **High-Frequency Activity Ledger**: `{agg_activity['total_co2']:,.2f} tonnes CO₂e` recorded across "
            f"`{agg_activity['total_entries']}` daily/weekly shift entries.\n\n"
            f"Where would you like to focus next?"
        )
        return {"text": text, "nav_target": "dashboard", "suggestions": ["🔥 Inspect Top Hotspots", "📝 Log Operational Data", "💰 Check Carbon Balance"]}

    # 3.8 Daily / Weekly Carbon Credit Usage & Statutory Quota Cross-Check
    if any(w in q for w in ["daily credit", "weekly credit", "expected credit", "expected carbon", "government issue", "govt issue", "initially issue", "initial quota", "initial credit", "cross check", "crosscheck", "statutory quota", "daily use", "weekly use"]):
        user_prof = get_user_profile(user_email) or {}
        user_logs = get_activity_logs(user_email, limit=500)
        audit = calculate_carbon_credit_audit(user_prof, user_logs, res)
        
        status_badge_line = f"⚠️ Projected Deficit of {audit['projected_credits_needed']:,.1f} credits" if audit['is_projected_deficit'] else f"🟢 Projected Surplus of {audit['projected_surplus_credits']:,.1f} credits"
        
        text = (
            f"### 🏛️ Carbon Credit Quota Audit & Burn Rate for {company_name}\n\n"
            f"- **🏛️ Government Initial Quota Issued**: `{audit['initial_govt_quota']:,.0f} credits` (Calibrated under `{audit['regulatory_regime']}` for {audit['employees']} employees)\n"
            f"- **🌅 Daily Carbon Credit Use**: `{audit['actual_daily_avg']:.3f} credits / day` (Statutory cap: `{audit['daily_quota_target']:.3f}/day`, `{audit['daily_pct_of_allowance']:.1f}%` of daily allowance)\n"
            f"- **📅 Weekly Carbon Credit Use**: `{audit['actual_weekly_avg']:.2f} credits / week` (Statutory cap: `{audit['weekly_quota_target']:.2f}/week`, `{audit['weekly_pct_of_allowance']:.1f}%` of weekly allowance)\n"
            f"- **📈 Expected Annual Credit Use**: `{audit['expected_annual_burn']:,.1f} credits / yr` (Monthly expected burn: `{audit['expected_monthly_burn']:.2f} credits/mo`)\n"
            f"- **🏦 Accrued Credits Used to Date**: `{audit['accrued_credits_used']:,.2f} credits` across `{audit['total_entries_count']}` recorded operational shifts\n"
            f"- **💰 Quota Remaining in Bank**: `{audit['accrued_remaining_balance']:,.2f} credits` ({audit['accrued_balance_pct']:.1f}% available, ~`{audit['quota_runway_days']}` operational days runway)\n"
            f"- **⚖️ Compliance Audit Verdict**: `{status_badge_line}`\n\n"
            f"You can review the full cross-check audit table directly on the Executive Dashboard."
        )
        return {
            "text": text,
            "nav_target": "dashboard",
            "suggestions": ["📊 View Quota Cross-Check", "💰 Open Carbon Desk", "📝 Log Today's Activity"]
        }

    # 4. Personalized Carbon Credits & Compliance Cost
    if any(w in q for w in ["credit", "deficit", "quota", "compliance cost", "penalty", "market", "liability", "balance"]):
        if is_deficit:
            text = (
                f"### ⚠️ Carbon Credit Deficit Warning for {company_name}\n\n"
                f"- **Government Allocation**: `{govt_credits:,.0f} credits`\n"
                f"- **Credits Consumed**: `{credits_used:,.1f} tonnes CO₂e`\n"
                f"- **Net Deficit**: `{credits_required:,.1f} tonnes` beyond statutory quota\n"
                f"- **Compliance Financial Liability**: `${comp_cost:,.0f}` (based on statutory rate of `${credit_price:,.0f}/credit`)\n\n"
                f"💡 **Recommendation**: Purchase verified offsets on the Carbon Credit Desk or implement equipment retrofits to mitigate compliance penalties."
            )
        else:
            text = (
                f"### 🟢 Carbon Neutral Compliance for {company_name}\n\n"
                f"- **Allocated Quota**: `{govt_credits:,.0f} credits`\n"
                f"- **Credits Consumed**: `{credits_used:,.1f} tonnes`\n"
                f"- **Surplus Registry Balance**: `{credits_remaining:,.1f} excess credits`\n"
                f"- **Monetization Potential**: You can trade surplus credits on the spot exchange for approximately `${credits_remaining * credit_price:,.0f}`!"
            )
        return {"text": text, "nav_target": "carbon_credits", "suggestions": ["🌍 Open Carbon Credit Desk", "🔥 View Emission Leaks", "📊 View Dashboard"]}

    # 5. Leak Hotspots Query
    if any(w in q for w in ["leak", "hotspot", "loss", "biggest source", "diagnostics", "where are"]):
        sorted_p = sorted(pillars.items(), key=lambda x: x[1], reverse=True)[:3]
        hotspot_str = "\n".join([f"{i+1}. **{p[0]}**: `{p[1]:,.1f} tonnes CO₂e`" for i, p in enumerate(sorted_p)])
        text = (
            f"### 🔥 Top Operational Emission Hotspots for {company_name}\n\n"
            f"{hotspot_str}\n\n"
            f"Addressing these areas yields your highest return on decarbonization investment. Upgrading heating and recycling waste streams provides the quickest emission drops."
        )
        return {"text": text, "nav_target": "leak_detection", "suggestions": ["🔍 Open Leak Diagnostics", "📊 Go to Dashboard", "♻️ Circular Alternatives"]}

    # 6. Sustainability Score Query
    if any(w in q for w in ["score", "rating", "benchmark", "grade", "eco score"]):
        text = (
            f"### 🌿 Sustainability Performance Score\n\n"
            f"- **Current Eco Score**: `{s_score:.0f} / 100` ({grade})\n"
            f"- **Status**: {'Above statutory benchmark 🌟' if s_score >= 70 else 'Requires targeted Scope 1/2 efficiency measures ⚠️'}\n\n"
            f"Increasing renewable electricity to 40%+ and recycling scrap waste streams will raise your score by +12 to +18 points."
        )
        return {"text": text, "nav_target": "dashboard", "suggestions": ["🔥 Check Leaks", "📝 Record Daily Activity", "📊 View Dashboard"]}

    # 7. Activity Logs (Fuel & Waste)
    if any(w in q for w in ["fuel", "waste", "diesel", "gas", "electricity", "meter", "log"]):
        text = (
            f"### 📋 Operational Activity Ledger Summary\n\n"
            f"- **Total Recorded Entries**: `{agg_activity['total_entries']} records`\n"
            f"- **Period Covered**: `{agg_activity['date_range']}`\n"
            f"- **Fuel Consumed**: `{agg_activity['total_diesel_liters']:,.0f} L diesel` &bull; `{agg_activity['total_gas_m3']:,.0f} m³ gas`\n"
            f"- **Solid Waste Collected**: `{agg_activity['total_waste_kg']:,.0f} kg`\n"
            f"- **Metered Electricity**: `{agg_activity['total_electricity_kwh']:,.0f} kWh`\n"
            f"- **High-Frequency CO₂e**: `{agg_activity['total_co2']:,.2f} tonnes`\n\n"
            f"Would you like to record a new shift entry or review historical ledger logs?"
        )
        return {"text": text, "nav_target": "activity_logs", "suggestions": ["➕ Record Shift Activity", "📋 View Full Ledger", "📊 Back to Dashboard"]}

    # 8. Default Assistant Overview
    text = (
        f"I'm **Carbon Copilot**, your sustainability assistant for **{company_name}**.\n\n"
        f"Here is what I can do for you:\n"
        f"- 🚀 **Instant Navigation**: Say *'Take me to dashboard'*, *'Open leaks'*, *'Go to daily logs'*, or *'Show carbon credits'*.\n"
        f"- 🏢 **Personalized Info**: Say *'Tell personalize info'* to get an instant snapshot of your `{total_co2:,.1f} t` footprint, compliance liability, and recent fuel/waste logs.\n"
        f"- ⛽ **Operations**: Check diesel, gas, electricity, and waste metrics stored in your SQLite database.\n\n"
        f"What would you like to explore?"
    )
    return {
        "text": text,
        "nav_target": nav_target,
        "suggestions": ["🏢 Tell personalize info", "🎯 What are my top leaks?", "💰 Check credit balance & liability", "📝 Record shift activity"]
    }

def render_copilot_chat(key_prefix: str = "copilot"):
    """
    Renders the Carbon Copilot chatbot interface.
    Guarantees unique element keys using the key_prefix parameter.
    """
    user = st.session_state.get("current_user", {})
    user_email = user.get("email", "guest@enterprise.com")
    comp_name = user.get("company_name", "Enterprise Facility")
    res = st.session_state.get("emissions_results", {})

    if "copilot_history" not in st.session_state:
        st.session_state["copilot_history"] = [
            {
                "sender": "bot",
                "text": f"👋 Hello! I am **Carbon Copilot**, your AI sustainability advisor for **{comp_name}**.\n\nAsk me for **personalize info**, your carbon footprint, carbon credits, leak hotspots, or tell me where you'd like to navigate!",
                "nav_target": None,
                "suggestions": ["🏢 Tell personalize info", "🎯 What are our biggest leaks?", "💰 Check carbon credit balance", "📝 Log today's fuel & waste"]
            }
        ]

    # Header section with clear chat button
    c_head1, c_head2 = st.columns([3.5, 1])
    with c_head1:
        st.markdown(f"""
            <div style="display: flex; align-items: center;">
                {feather_icon('message-square', color=COLOR_SUCCESS, size=18, margin_right=8)}
                <span style="font-weight: 700; font-size: 0.95rem; color: var(--text-primary);">Carbon Copilot AI</span>
                <span style="background: rgba(16,185,129,0.15); color: #047857; padding: 2px 8px; border-radius: 6px; font-weight: 700; font-size: 0.72rem; margin-left: 8px;">
                    ONLINE &bull; {comp_name}
                </span>
            </div>
        """, unsafe_allow_html=True)
    with c_head2:
        if st.button("🔄 Reset Chat", key=f"{key_prefix}_reset_chat_btn", use_container_width=True):
            st.session_state["copilot_history"] = [
                {
                    "sender": "bot",
                    "text": f"Conversation reset. How can I assist you with **{comp_name}**?",
                    "nav_target": None,
                    "suggestions": ["🏢 Tell personalize info", "🎯 What are our biggest leaks?", "💰 Check carbon credit balance", "📊 Go to Dashboard"]
                }
            ]
            st.rerun()

    # Extract live personalized profile & compliance numbers
    user_name = user.get("owner_name", user.get("name", "David Kovac"))
    user_role = user.get("role", "Admin")
    res = res or {}
    total_co2 = res.get("total_co2", 0.0)
    s_score = res.get("sustainability_score", 50.0)
    is_deficit = res.get("is_deficit", False)
    credits_required = res.get("credits_required", 0.0)
    credits_remaining = res.get("credits_remaining", 0.0)
    agg_activity = get_aggregated_activity_summary(user_email)

    # 1. Sleek High-Contrast Personalized Enterprise Profile Card
    st.markdown(f"""
        <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 12px 16px; margin-bottom: 12px; box-shadow: var(--shadow-card);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <div style="font-size: 0.72rem; font-weight: 800; text-transform: uppercase; color: #10B981; letter-spacing: 0.08em;">
                        🏢 ACTIVE ENTERPRISE PROFILE
                    </div>
                    <div style="font-weight: 800; font-size: 1.05rem; color: var(--text-primary); margin-top: 2px;">
                        {comp_name}
                    </div>
                    <div style="font-size: 0.8rem; color: var(--text-muted);">
                        👤 {user_name} ({user_role}) &bull; {user_email}
                    </div>
                </div>
                <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                    <div style="background: var(--bg-subtle); padding: 5px 10px; border-radius: 8px; border: 1px solid var(--border-color); text-align: center;">
                        <div style="font-size: 0.68rem; color: var(--text-muted); font-weight: 700;">ANNUAL CO₂e</div>
                        <div style="font-weight: 800; font-size: 0.92rem; color: var(--text-primary);">{total_co2:,.1f} t</div>
                    </div>
                    <div style="background: var(--bg-subtle); padding: 5px 10px; border-radius: 8px; border: 1px solid var(--border-color); text-align: center;">
                        <div style="font-size: 0.68rem; color: var(--text-muted); font-weight: 700;">CREDIT STATUS</div>
                        <div style="font-weight: 800; font-size: 0.85rem; color: {'#EF4444' if is_deficit else '#10B981'};">
                            {'Deficit: ' + f'{credits_required:,.1f}t' if is_deficit else 'Surplus: ' + f'{credits_remaining:,.1f}t'}
                        </div>
                    </div>
                    <div style="background: var(--bg-subtle); padding: 5px 10px; border-radius: 8px; border: 1px solid var(--border-color); text-align: center;">
                        <div style="font-size: 0.68rem; color: var(--text-muted); font-weight: 700;">ECO SCORE</div>
                        <div style="font-weight: 800; font-size: 0.92rem; color: #10B981;">{s_score:.0f}/100</div>
                    </div>
                    <div style="background: var(--bg-subtle); padding: 5px 10px; border-radius: 8px; border: 1px solid var(--border-color); text-align: center;">
                        <div style="font-size: 0.68rem; color: var(--text-muted); font-weight: 700;">DAILY SHIFTS</div>
                        <div style="font-weight: 800; font-size: 0.92rem; color: #3B82F6;">{agg_activity['total_entries']} logs</div>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. 1-Click Fast App Navigation Bar
    st.markdown("<div style='font-size: 0.75rem; font-weight: 800; color: var(--text-muted); letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 6px;'>⚡ 1-Click Fast App Navigation:</div>", unsafe_allow_html=True)
    n_c1, n_c2, n_c3, n_c4, n_c5, n_c6 = st.columns(6)
    with n_c1:
        if st.button("📊 Dashboard", key=f"{key_prefix}_nav_dash", use_container_width=True):
            st.session_state["nav_section"] = "dashboard"
            st.session_state["current_step"] = 5
            st.rerun()
    with n_c2:
        if st.button("📅 Daily Logs", key=f"{key_prefix}_nav_act", use_container_width=True):
            st.session_state["nav_section"] = "activity_logs"
            st.session_state["current_step"] = 4
            st.rerun()
    with n_c3:
        if st.button("🔍 Leak Points", key=f"{key_prefix}_nav_leaks", use_container_width=True):
            st.session_state["nav_section"] = "leak_detection"
            st.session_state["current_step"] = 6
            st.rerun()
    with n_c4:
        if st.button("💰 Carbon Credits", key=f"{key_prefix}_nav_credits", use_container_width=True):
            st.session_state["nav_section"] = "carbon_credits"
            st.session_state["current_step"] = 7
            st.rerun()
    with n_c5:
        if st.button("♻️ Circular 4R", key=f"{key_prefix}_nav_circ", use_container_width=True):
            st.session_state["nav_section"] = "circular"
            st.session_state["current_step"] = 10
            st.rerun()
    with n_c6:
        if st.button("⚙️ Setup", key=f"{key_prefix}_nav_setup", use_container_width=True):
            st.session_state["nav_section"] = "setup"
            st.session_state["current_step"] = 3
            st.rerun()

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    # Chat history container with fixed scroll height
    chat_container = st.container(height=300)
    with chat_container:
        for idx, msg in enumerate(st.session_state["copilot_history"]):
            if msg["sender"] == "user":
                st.markdown(f"""
                    <div class="chat-bubble-user">
                        <strong>You:</strong> {msg['text']}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="chat-bubble-bot">
                        <div style="display: flex; align-items: center; margin-bottom: 4px; font-weight: 700; color: #10B981; font-size: 0.8rem;">
                            {feather_icon('cpu', color=COLOR_SUCCESS, size=14, margin_right=5)} Carbon Copilot
                        </div>
                        {msg['text']}
                    </div>
                """, unsafe_allow_html=True)

                # Render navigation action button if response recommends navigation
                if msg.get("nav_target") and msg["nav_target"] in NAV_DESTINATIONS:
                    target_info = NAV_DESTINATIONS[msg["nav_target"]]
                    btn_col, _ = st.columns([1.5, 1])
                    with btn_col:
                        if st.button(
                            f"🚀 Jump to {target_info['name']}",
                            key=f"{key_prefix}_nav_btn_{idx}_{msg['nav_target']}",
                            type="primary",
                            use_container_width=True
                        ):
                            st.session_state["nav_section"] = target_info["section"]
                            st.session_state["current_step"] = target_info["step"]
                            st.rerun()

    # Quick Suggestion Chips with guaranteed unique keys
    last_msg = st.session_state["copilot_history"][-1]
    suggestions = last_msg.get("suggestions", ["🏢 Tell personalize info", "🎯 What are my top leaks?", "💰 Check credit balance", "📊 Go to Dashboard"])
    
    st.markdown("<div style='font-size: 0.76rem; font-weight: 700; color: var(--text-muted); margin: 8px 0 4px 0;'>SUGGESTED PROMPTS:</div>", unsafe_allow_html=True)
    chip_cols = st.columns(len(suggestions))
    for c_idx, chip_text in enumerate(suggestions):
        with chip_cols[c_idx]:
            chip_key = f"{key_prefix}_chip_{c_idx}_{abs(hash(chip_text)) % 1000000}"
            if st.button(chip_text, key=chip_key, use_container_width=True):
                # Append user prompt
                st.session_state["copilot_history"].append({"sender": "user", "text": chip_text})
                # Generate response
                resp = generate_copilot_response(chip_text, user_email, comp_name, res)
                st.session_state["copilot_history"].append({
                    "sender": "bot",
                    "text": resp["text"],
                    "nav_target": resp.get("nav_target"),
                    "suggestions": resp.get("suggestions", [])
                })
                if resp.get("auto_redirect") and resp.get("nav_target") in NAV_DESTINATIONS:
                    dest = NAV_DESTINATIONS[resp["nav_target"]]
                    st.session_state["nav_section"] = dest["section"]
                    st.session_state["current_step"] = dest["step"]
                st.rerun()

    # User Input Field in Form with guaranteed unique keys
    with st.form(f"{key_prefix}_chat_form", clear_on_submit=True):
        c_in, c_sub = st.columns([4.2, 1])
        with c_in:
            user_input = st.text_input(
                "Ask Copilot",
                placeholder="Ask e.g. 'Tell personalize info', 'Take me to leaks', 'Check carbon deficit'",
                label_visibility="collapsed",
                key=f"{key_prefix}_chat_input_field"
            )
        with c_sub:
            submitted = st.form_submit_button("Send 💬", type="primary", use_container_width=True)

        if submitted and user_input.strip():
            # Append user message
            st.session_state["copilot_history"].append({"sender": "user", "text": user_input.strip()})
            # Generate assistant reply
            resp = generate_copilot_response(user_input.strip(), user_email, comp_name, res)
            st.session_state["copilot_history"].append({
                "sender": "bot",
                "text": resp["text"],
                "nav_target": resp.get("nav_target"),
                "suggestions": resp.get("suggestions", [])
            })
            if resp.get("auto_redirect") and resp.get("nav_target") in NAV_DESTINATIONS:
                dest = NAV_DESTINATIONS[resp["nav_target"]]
                st.session_state["nav_section"] = dest["section"]
                st.session_state["current_step"] = dest["step"]
            st.rerun()

def render_copilot_view():
    """Renders the full-page dedicated AI Carbon Copilot view."""
    user = st.session_state.get("current_user", {})
    comp_name = user.get("company_name", "Enterprise Facility")
    
    st.markdown("""
        <div style="margin-bottom: 8px;">
            <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #10B981; font-weight: 700;">
                AI Intelligence & Copilot
            </span>
        </div>
    """, unsafe_allow_html=True)

    header_icon = feather_icon("cpu", color="#10B981", size=30, margin_right=10)
    st.markdown(f"""
        <div style="margin-bottom: 20px;">
            <h1 style="font-size: 2.0rem; font-weight: 800; margin: 0; letter-spacing: -0.02em; display: flex; align-items: center;">
                {header_icon} Carbon Copilot & Enterprise Advisor
            </h1>
            <p style="font-size: 0.95rem; color: var(--text-muted); margin-top: 4px; margin-bottom: 0;">
                Conversational sustainability intelligence, personalized carbon accounting, and instant application routing for {comp_name}.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="saas-card" style="padding: 24px;">
    """, unsafe_allow_html=True)
    render_copilot_chat(key_prefix="copilot_full_view")
    st.markdown("</div>", unsafe_allow_html=True)
