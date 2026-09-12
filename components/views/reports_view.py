"""
Step 11: Reports, Audit Logs, and ESG Compliance View.
Generates:
1. Business Sustainability Report
2. Carbon Audit Report
3. Circular Economy Report
Exports to PDF (Print-ready HTML), CSV, and Excel (.xlsx multi-tab workbook).
Includes an ESG Compliance Checklist and SQLite Audit Log viewer.
"""

import streamlit as st
import pandas as pd
import io
from components.data_presets import AI_RECOMMENDATIONS
from database.db_manager import get_audit_logs
from components.icons import feather_icon, render_icon_heading, COLOR_WARNING, COLOR_SUCCESS, COLOR_NEUTRAL, COLOR_INFO

def render_reports_view():
    """Renders Step 11 Reports & Compliance screen."""
    res = st.session_state.get("emissions_results")
    if not res:
        st.warning("Please complete Step 3 Setup or load a preset first.")
        return

    user = st.session_state.get("current_user", {})
    user_email = user.get("email", "guest@enterprise.com")
    comp_name = user.get("company_name", res.get("raw_inputs", {}).get("business_name", "Enterprise Facility"))

    st.markdown("""
        <div style="margin-bottom: 8px;">
            <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #10B981; font-weight: 700;">
                Step 11 — Compliance Reporting & Data Export
            </span>
        </div>
    """, unsafe_allow_html=True)
    st.markdown(render_icon_heading(
        "download",
        "Verified Sustainability Reports & Export Engine",
        level="h2",
        color=COLOR_NEUTRAL,
        subtitle="Generate certified carbon audits, executive briefs, and circular economy roadmaps in PDF, Excel, and CSV formats."
    ), unsafe_allow_html=True)

    tab_reports, tab_esg, tab_audit = st.tabs(["Exportable Reports", "ESG Compliance Checklist", "SQLite Audit Trail"])

    # Tab 1: Exportable Reports
    with tab_reports:
        c_exp_l, c_exp_r = st.columns([1, 1], gap="large")

        # Prepare DataFrames for Exports
        # 1. Summary DF
        df_summary = pd.DataFrame([{
            "Company": comp_name,
            "Total Baseline CO2 (tonnes)": res["total_co2"],
            "Annual Operational Spend ($)": res["total_cost"],
            "Govt Credits Allocated": res["govt_credits"],
            "Credit Balance": res["credit_balance"],
            "Compliance Status": res["net_carbon_status"],
            "Estimated Compliance Cost ($)": res["compliance_cost"],
            "Sustainability Score (0-100)": res["sustainability_score"]
        }])

        # 2. Leaks DF
        df_leaks = pd.DataFrame(res.get("top_10_leaks", []))
        if not df_leaks.empty:
            cols_to_keep = [c for c in ["rank", "source", "category", "current_co2", "share_pct", "cost_impact", "potential_saving_co2", "potential_saving_cost", "priority", "status"] if c in df_leaks.columns]
            df_leaks = df_leaks[cols_to_keep]

        # 3. Recommendations DF
        selected_ids = st.session_state.get("selected_action_recs", set())
        recs_data = [r for r in AI_RECOMMENDATIONS if r["id"] in selected_ids]
        df_recs = pd.DataFrame(recs_data)
        if not df_recs.empty:
            cols_r = [c for c in ["title", "category", "co2_saved_t", "cost_estimate", "expected_roi", "payback_time", "difficulty", "impact_level"] if c in df_recs.columns]
            df_recs = df_recs[cols_r]

        # Excel Export (multi-sheet)
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_summary.to_excel(writer, sheet_name="Executive Summary", index=False)
            if not df_leaks.empty:
                df_leaks.to_excel(writer, sheet_name="Top 10 Leak Points", index=False)
            if not df_recs.empty:
                df_recs.to_excel(writer, sheet_name="AI Decarbonization Plan", index=False)
        excel_bytes = excel_buffer.getvalue()

        # CSV Export
        csv_bytes = df_leaks.to_csv(index=False).encode('utf-8')

        with c_exp_l:
            st.markdown(f"""
                <div class="saas-card">
                    <div class="saas-card-title">{feather_icon('download', color=COLOR_NEUTRAL, size=18)} Multi-Format Downloads</div>
                    <div class="saas-card-subtitle" style="margin-bottom: 16px;">
                        Enterprise data packages formatted for Microsoft Excel, Google Sheets, or ERP integration:
                    </div>
            """, unsafe_allow_html=True)

            st.download_button(
                label="Download Complete Excel Workbook (.XLSX)",
                data=excel_bytes,
                file_name=f"{comp_name.lower().replace(' ', '_')}_sustainability_workbook.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True
            )

            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

            st.download_button(
                label="Download Top 10 Leaks CSV (.CSV)",
                data=csv_bytes,
                file_name=f"{comp_name.lower().replace(' ', '_')}_leak_points.csv",
                mime="text/csv",
                use_container_width=True
            )

            st.markdown("</div>", unsafe_allow_html=True)

            # Executive Summary Brief snippet
            st.markdown(f"""
                <div class="saas-card">
                    <div class="saas-card-title">{feather_icon('file-text', color=COLOR_NEUTRAL, size=18)} Executive Boardroom Summary</div>
                    <div class="saas-card-subtitle" style="margin-bottom: 12px;">
                        Formatted text for quick copy-pasting into executive memos and investor emails:
                    </div>
            """, unsafe_allow_html=True)

            exec_text = (
                f"SUSTAINABILITY AUDIT BRIEF — {comp_name.upper()}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• Gross Operational Emissions: {res['total_co2']:,.1f} tonnes CO₂e/yr\n"
                f"• Direct Annual Cost Exposure: ${res['total_cost']:,.0f}/yr\n"
                f"• Statutory Government Cap: {res['govt_credits']:,.0f} carbon credits\n"
                f"• Net Compliance Status: {res['net_carbon_status']}\n"
                f"• Compliance Deficit / Surplus: {res['credit_balance']:+,.1f} credits\n"
                f"• Overall Eco Sustainability Score: {res['sustainability_score']}/100\n"
                f"• Priority Operational Leak: #{res.get('top_leak', {}).get('rank', 1)} {res.get('top_leak', {}).get('source', 'Operations')} ({res.get('top_leak', {}).get('share_pct', 0)}% of footprint)\n"
                f"• Target Reductions: {len(selected_ids)} active decarbonization initiatives selected."
            )
            st.code(exec_text, language="text")
            st.markdown("</div>", unsafe_allow_html=True)

        with c_exp_r:
            st.markdown(f"""
                <div class="saas-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <div class="saas-card-title">{feather_icon('download', color=COLOR_NEUTRAL, size=18)} Printable PDF Audit Dossier</div>
                        <span class="badge-low">PRINT / PDF READY</span>
                    </div>
                    <div class="saas-card-subtitle" style="margin-bottom: 14px;">
                        Press <strong>Ctrl+P</strong> (or Cmd+P) in your browser to print or save this dossier as a clean, styled PDF:
                    </div>
                    <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 20px; font-size: 0.88rem;">
                        <div style="border-bottom: 2px solid #10B981; padding-bottom: 10px; margin-bottom: 14px;">
                            <h3 style="margin: 0; color: #065F46; font-size: 1.25rem;">CARBON EMISSION AUDIT & CIRCULAR ROADMAP</h3>
                            <div style="color: var(--text-muted); font-size: 0.82rem; margin-top: 2px;">
                                Facility: <strong>{comp_name}</strong> &bull; Lead Auditor: {user.get("owner_name", "Sustainability Lead")}
                            </div>
                        </div>
                        <div style="margin-bottom: 14px;">
                            <strong>Operational Key Metrics:</strong>
                            <ul style="margin: 6px 0 12px 20px; padding: 0; line-height: 1.6;">
                                <li>Total Greenhouse Footprint: <strong>{res['total_co2']:,.1f} tonnes CO₂e</strong></li>
                                <li>Associated Operational Utilities: <strong>${res['total_cost']:,.0f} / yr</strong></li>
                                <li>Regulatory Status: <strong>{res['net_carbon_status']}</strong></li>
                                <li>Eco Sustainability Rating: <strong>{str(res['sustainability_score'])} / 100</strong></li>
                            </ul>
                        </div>
                        <div style="margin-bottom: 14px;">
                            <strong>Top 3 Diagnosed Emission Leaks:</strong>
                            <ol style="margin: 6px 0 12px 20px; padding: 0; line-height: 1.6;">
            """, unsafe_allow_html=True)

            top_3 = res.get("top_10_leaks", [])[:3]
            for l in top_3:
                st.markdown(f"<li><strong>{l['source']}</strong> — {l['current_co2']:,.1f} t CO₂ ({l['share_pct']}%) &bull; Potential Cut: -{l['potential_saving_co2']} t</li>", unsafe_allow_html=True)

            st.markdown("""
                            </ol>
                        </div>
                        <div>
                            <strong>Planned Decarbonization Interventions:</strong>
                            <ul style="margin: 6px 0 0 20px; padding: 0; line-height: 1.6;">
            """, unsafe_allow_html=True)

            for rec in recs_data[:3]:
                st.markdown(f"<li><strong>{rec['title']}</strong> (Payback: {rec['payback_time']}, ROI: +{rec['expected_roi']}%)</li>", unsafe_allow_html=True)

            st.markdown("""
                            </ul>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # Tab 2: ESG Compliance Checklist
    with tab_esg:
        st.markdown(f"""
            <div class="saas-card">
                <div class="saas-card-title">{feather_icon('check-circle', color=COLOR_SUCCESS, size=18)} Corporate ESG & Regulatory Compliance Readiness</div>
                <div class="saas-card-subtitle" style="margin-bottom: 16px;">
                    Track statutory reporting requirements against GHG Protocol, ISO 14064, EU CSRD, and SEC climate disclosure rules:
                </div>
        """, unsafe_allow_html=True)

        esg_items = [
            ("Scope 1 Direct Stationary & Mobile Combustion Documented", "Compliant", True, "Diesel, natural gas, and company vehicle logs registered in system."),
            ("Scope 2 Purchased Grid Electricity & Renewable Reconciliation", "Compliant", True, "Electricity kWh and renewable PPA offset calculated accurately."),
            ("Scope 3 Value Chain Solid Waste & Water Effluent Accounting", "In Progress", True, "Waste streams and municipal sewer effluent quantified."),
            ("Government Carbon Credit Compliance Balance Verified", "Audited", not res["is_deficit"], "Reconciled against official credit allowance registry."),
            ("Circular Economy Waste Diversion Strategy Formalized", "Action Required", len(selected_ids) >= 3, "4R alternatives selected for primary industrial scrap streams."),
            ("Executive Decarbonization Roadmap Approved by Leadership", "Scheduled", True, "Quarterly audit dossier exported for board review.")
        ]

        for item_title, status_text, is_passed, note in esg_items:
            s_badge = "badge-low" if is_passed else "badge-critical"
            status_icon = feather_icon("check-circle", color=COLOR_SUCCESS, size=16) if is_passed else feather_icon("alert-triangle", color=COLOR_WARNING, size=16)
            st.markdown(f"""
                <div style="background: var(--bg-subtle); border: 1px solid var(--border-color); border-radius: 10px; padding: 12px 16px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 0.95rem; font-weight: 600; display: flex; align-items: center;">
                            {status_icon} <span>{item_title}</span>
                        </div>
                        <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 2px;">{note}</div>
                    </div>
                    <span class="{s_badge}">{status_text}</span>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Tab 3: SQLite Audit Trail
    with tab_audit:
        st.markdown(f"""
            <div class="saas-card">
                <div class="saas-card-title">{feather_icon('file-text', color=COLOR_NEUTRAL, size=18)} Immutable Data Audit Trail (SQLite)</div>
                <div class="saas-card-subtitle" style="margin-bottom: 14px;">
                    Chronological record of all updates, assessments, file uploads, and carbon trading transactions:
                </div>
        """, unsafe_allow_html=True)

        logs = get_audit_logs(user_email, limit=25)
        if not logs:
            st.info("No audit entries recorded yet for this session.")
        else:
            df_logs = pd.DataFrame(logs)
            cols_show = [c for c in ["timestamp", "action", "field_changed", "new_value"] if c in df_logs.columns]
            st.dataframe(df_logs[cols_show], use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Navigation
    st.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid var(--border-color);'/>", unsafe_allow_html=True)
    c_b1, c_b2 = st.columns([1, 1])
    with c_b1:
        if st.button("← Back to Circular Alternatives", key="rep_back_circ"):
            st.session_state["current_step"] = 10
            st.session_state["nav_section"] = "circular"
            st.rerun()
    with c_b2:
        if st.button("Manage Platform Settings & Factors →", type="primary", key="rep_next_set", use_container_width=True):
            st.session_state["current_step"] = 12
            st.session_state["nav_section"] = "settings"
            st.rerun()
