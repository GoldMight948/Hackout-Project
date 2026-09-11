"""
Step 4: Recommendations View & Green Suggestion Box.
Shows 3-5 prioritized fixes for the selected/top leak point with:
- Fix Name, CO2 Saved, Cost, Difficulty (Easy/Med/Hard), Payback Time
- Toggle to add fixes directly into the customized Action Plan
- Interactive Community & Team Green Suggestion Box with voting and idea submissions.
"""

import streamlit as st
import datetime
from components.data_presets import CATEGORY_FIXES, DEFAULT_SUGGESTIONS
from components.calculations import CATEGORY_METADATA

def init_recommendations_state():
    """Initializes selected fixes and suggestions in session state."""
    if "selected_fixes" not in st.session_state:
        # Pre-select quick wins by default
        st.session_state["selected_fixes"] = {"elec_led", "elec_hvac_tune", "fuel_insul", "trans_telematics", "waste_segregation"}
    if "suggestions_list" not in st.session_state:
        st.session_state["suggestions_list"] = list(DEFAULT_SUGGESTIONS)

def render_recommendations_view():
    init_recommendations_state()

    results = st.session_state.get("emissions_results", {})
    top_leak = results.get("top_leak")
    active_cat = st.session_state.get("selected_leak_category", top_leak["category"] if top_leak else "electricity")
    meta = CATEGORY_METADATA.get(active_cat, CATEGORY_METADATA["electricity"])

    st.markdown(f"""
        <div style="margin-bottom: 20px;">
            <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #059669; font-weight: 700;">
                Targeted Green Fixes & ROI
            </span>
            <h2 style="font-size: 1.8rem; font-weight: 800; color: #0F172A; margin: 4px 0 6px 0;">
                Solutions for {meta['icon']} {meta['label']} Leaks
            </h2>
            <p style="font-size: 0.95rem; color: #64748B;">
                Practical, field-tested interventions sorted by implementation difficulty and return on investment.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Category Switcher Pills
    cat_keys = ["electricity", "fuel", "transport", "waste"]
    cols = st.columns(4)
    for idx, ckey in enumerate(cat_keys):
        cmeta = CATEGORY_METADATA[ckey]
        is_selected = (ckey == active_cat)
        is_top = (top_leak and top_leak["category"] == ckey)
        top_badge = " 🔥 (Top Leak)" if is_top else ""
        button_text = f"{cmeta['icon']} {cmeta['label']}{top_badge}"
        
        with cols[idx]:
            if st.button(button_text, key=f"tab_{ckey}", type="primary" if is_selected else "secondary", use_container_width=True):
                st.session_state["selected_leak_category"] = ckey
                st.rerun()

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # Fixes list for current category
    fixes = CATEGORY_FIXES.get(active_cat, [])
    cat_co2 = results.get("co2_by_category", {}).get(active_cat, 10.0)

    st.markdown(f"#### 🛠️ Recommended Interventions for {meta['label']}")
    st.caption("Select the fixes you want to include in your customized Action Plan:")

    for fix in fixes:
        saved_tonnes = round((fix["co2_saved_pct"] / 100.0) * cat_co2, 2)
        diff_color = "#10B981" if fix["difficulty"] == "Easy" else ("#F59E0B" if fix["difficulty"] == "Medium" else "#EF4444")
        diff_bg = "#ECFDF5" if fix["difficulty"] == "Easy" else ("#FEF3C7" if fix["difficulty"] == "Medium" else "#FEE2E2")
        is_checked = fix["id"] in st.session_state["selected_fixes"]

        with st.container():
            st.markdown(f"""
                <div class="fix-card" style="border-left-color: {diff_color};">
                    <div class="fix-card-header">
                        <div>
                            <div class="fix-title">{fix['name']}</div>
                            <div style="font-size: 0.88rem; color: #475569; margin-top: 4px; line-height: 1.4;">
                                {fix['description']}
                            </div>
                        </div>
                        <span style="background: {diff_bg}; color: {diff_color}; font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 20px; text-transform: uppercase;">
                            {fix['difficulty']} Effort
                        </span>
                    </div>
                    <div style="display: flex; flex-wrap: wrap; gap: 16px; margin-top: 14px; padding-top: 12px; border-top: 1px solid #F1F5F9; font-size: 0.85rem;">
                        <div>
                            <span style="color: #64748B;">🌱 CO₂ Reduction:</span> 
                            <strong style="color: #065F46;">~{fix['co2_saved_pct']}%</strong> ({saved_tonnes} t/yr)
                        </div>
                        <div>
                            <span style="color: #64748B;">💵 Est. Investment:</span> 
                            <strong>{fix['cost_estimate']}</strong>
                        </div>
                        <div>
                            <span style="color: #64748B;">⏱️ Payback Period:</span> 
                            <strong style="color: #2563EB;">{fix['payback_time']}</strong>
                        </div>
                        <div>
                            <span style="color: #64748B;">📅 Timeline:</span> 
                            <strong style="color: #475569;">{fix['timeframe_label']}</strong>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Checkbox to include in action plan
            toggle_key = f"toggle_fix_{fix['id']}"
            toggled = st.checkbox(
                f"Include '{fix['name']}' in My Action Plan",
                value=is_checked,
                key=toggle_key
            )
            if toggled:
                st.session_state["selected_fixes"].add(fix["id"])
            else:
                st.session_state["selected_fixes"].discard(fix["id"])

            st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # Interactive Green Suggestion Box
    # -------------------------------------------------------------
    st.markdown("<hr style='margin: 36px 0 24px 0; border: none; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
            <div>
                <h3 style="font-size: 1.35rem; font-weight: 800; color: #065F46; margin: 0;">
                    💡 Green Suggestion Box
                </h3>
                <p style="font-size: 0.88rem; color: #64748B; margin: 4px 0 0 0;">
                    Have an idea for saving energy or reducing waste in your facility? Submit it below or vote on ideas from your team!
                </p>
            </div>
            <span style="background: #ECFDF5; color: #047857; font-size: 0.8rem; font-weight: 700; padding: 4px 10px; border-radius: 8px;">
                COMMUNITY & TEAM
            </span>
        </div>
    """, unsafe_allow_html=True)

    sug_col_list, sug_col_form = st.columns([1.25, 1.0], gap="large")

    with sug_col_list:
        st.markdown("##### 🗳️ Active Suggestions & Team Votes")
        suggestions = st.session_state.get("suggestions_list", [])
        
        for idx, sug in enumerate(suggestions):
            cat_icon = CATEGORY_METADATA.get(sug.get("category", "electricity"), {}).get("icon", "🌱")
            with st.container():
                st.markdown(f"""
                    <div class="suggestion-card">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div>
                                <span style="font-size: 0.75rem; background: #E2E8F0; color: #334155; padding: 2px 6px; border-radius: 4px; font-weight: 600; text-transform: uppercase;">
                                    {cat_icon} {sug.get('category', 'general')}
                                </span>
                                <div style="font-weight: 700; color: #0F172A; font-size: 0.95rem; margin-top: 4px;">
                                    {sug['title']}
                                </div>
                            </div>
                        </div>
                        <p style="font-size: 0.85rem; color: #475569; margin: 6px 0 8px 0; line-height: 1.4;">
                            {sug['description']}
                        </p>
                        <div style="font-size: 0.78rem; color: #94A3B8;">
                            Submitted by <strong>{sug['author']}</strong> ({sug['company']}) &bull; {sug.get('date', 'Recent')}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Voting button
                c_vote, _ = st.columns([1, 2])
                with c_vote:
                    if st.button(f"👍 Upvote ({sug['votes']})", key=f"vote_{sug['id']}_{idx}"):
                        sug["votes"] += 1
                        st.rerun()

    with sug_col_form:
        st.markdown("##### ✍️ Submit a New Green Fix Idea")
        user = st.session_state.get("current_user", {})
        
        with st.form("new_suggestion_form"):
            s_name = st.text_input("Your Name", value=user.get("name", "Team Member"))
            s_comp = st.text_input("Company / Department", value=user.get("company", "Operations"))
            s_cat = st.selectbox("Related Leak Area", ["electricity", "fuel", "transport", "waste"])
            s_title = st.text_input("Idea Headline", placeholder="e.g. Turn off packaging conveyor during lunch break")
            s_desc = st.text_area("How does it save carbon or money?", placeholder="Explain the practical step and expected savings...")
            
            submit_sug = st.form_submit_button("Post Suggestion to Box 📮", type="primary", use_container_width=True)
            
            if submit_sug:
                if not s_title.strip() or not s_desc.strip():
                    st.error("Please provide both a title and description for your suggestion.")
                else:
                    new_item = {
                        "id": f"sug_{len(suggestions) + 1}_{int(datetime.datetime.now().timestamp())}",
                        "author": s_name.strip(),
                        "company": s_comp.strip(),
                        "category": s_cat,
                        "title": s_title.strip(),
                        "description": s_desc.strip(),
                        "votes": 1,
                        "date": datetime.date.today().isoformat()
                    }
                    st.session_state["suggestions_list"].insert(0, new_item)
                    st.success("🎉 Thank you! Your green suggestion has been added.")
                    st.rerun()

    st.markdown("<hr style='margin: 30px 0 20px 0; border: none; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)

    # Navigation buttons
    col_nav_left, col_nav_right = st.columns([1, 1])
    with col_nav_left:
        if st.button("← Back to Emissions Dashboard", key="recom_back"):
            st.session_state["current_step"] = 3
            st.rerun()

    with col_nav_right:
        if st.button("Test Changes in Simulator →", type="primary", key="recom_next", use_container_width=True):
            st.session_state["current_step"] = 5
            st.rerun()
