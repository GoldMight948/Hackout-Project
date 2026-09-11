"""
Step 1: Welcome Screen View.
Non-technical intro, value proposition cards, sample dataset pre-loaders, and call to action.
"""

import streamlit as st
from components.data_presets import DEMO_BUSINESSES

def render_welcome_view():
    user = st.session_state.get("current_user", {})
    user_name = user.get("name", "there")
    company_name = user.get("company", "your business")

    st.markdown(f"""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 16px; padding: 32px 36px; margin-bottom: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.03);">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span style="font-size: 1.8rem;">👋</span>
                <h2 style="font-size: 1.75rem; font-weight: 800; color: #065F46; margin: 0;">Welcome, {user_name}!</h2>
            </div>
            <p style="font-size: 1.05rem; color: #475569; line-height: 1.6; max-width: 780px;">
                Ready to find where <strong>{company_name}</strong> is leaking emissions and money? 
                Most small businesses can cut <strong>15% to 35% of their utility footprint</strong> in under 12 months with low-cost operational fixes.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 3-Card Value Proposition
    c1, c2, c3 = st.columns(3, gap="medium")
    
    with c1:
        st.markdown("""
            <div class="clean-card" style="height: 100%;">
                <div style="font-size: 2rem; margin-bottom: 12px;">🔍</div>
                <h4 style="font-size: 1.1rem; font-weight: 700; color: #0F172A; margin-bottom: 8px;">1. Spot Hidden Leaks</h4>
                <p style="font-size: 0.9rem; color: #64748B; line-height: 1.5;">
                    Enter your electric, fuel, transport, and waste numbers in 60 seconds. Our diagnostic engine ranks your biggest leakage source.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
            <div class="clean-card" style="height: 100%;">
                <div style="font-size: 2rem; margin-bottom: 12px;">💡</div>
                <h4 style="font-size: 1.1rem; font-weight: 700; color: #0F172A; margin-bottom: 8px;">2. Actionable Green Fixes</h4>
                <p style="font-size: 0.9rem; color: #64748B; line-height: 1.5;">
                    No confusing carbon jargon. Get tailored, high-ROI recommendations with clear dollar payback periods and difficulty ratings.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
            <div class="clean-card" style="height: 100%;">
                <div style="font-size: 2rem; margin-bottom: 12px;">📈</div>
                <h4 style="font-size: 1.1rem; font-weight: 700; color: #0F172A; margin-bottom: 8px;">3. Simulate Your Savings</h4>
                <p style="font-size: 0.9rem; color: #64748B; line-height: 1.5;">
                    Move live sliders to preview your before vs after carbon reduction and annual operational cost savings in real time.
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

    # Quick demo preset loader section
    st.markdown("""
        <div style="background: #F8FAFC; border: 1px dashed #CBD5E1; border-radius: 14px; padding: 20px 24px; margin-bottom: 24px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                <h4 style="font-size: 1.05rem; font-weight: 700; color: #1E293B; margin: 0;">🚀 Want to see it in action first? Load a sample business</h4>
                <span style="font-size: 0.8rem; color: #64748B;">Instant pre-fill</span>
            </div>
            <p style="font-size: 0.88rem; color: #64748B; margin-bottom: 16px;">
                Choose one of our verified industry presets to test with realistic numbers before entering your own:
            </p>
        </div>
    """, unsafe_allow_html=True)

    p_col1, p_col2, p_col3 = st.columns(3)
    
    with p_col1:
        if st.button("🥪 Load Food Processor (Bakery)", use_container_width=True):
            st.session_state["form_inputs"] = DEMO_BUSINESSES["food_processor"]["data"].copy()
            st.session_state["active_preset"] = "food_processor"
            st.session_state["current_step"] = 2
            st.success("Loaded GreenBite Organics data! Proceeding to Data Entry...")
            st.rerun()

    with p_col2:
        if st.button("🏪 Load Small Retail Boutique", use_container_width=True):
            st.session_state["form_inputs"] = DEMO_BUSINESSES["small_retail"]["data"].copy()
            st.session_state["active_preset"] = "small_retail"
            st.session_state["current_step"] = 2
            st.success("Loaded EcoTrend Boutique data! Proceeding to Data Entry...")
            st.rerun()

    with p_col3:
        if st.button("🚚 Load Logistics & Delivery", use_container_width=True):
            st.session_state["form_inputs"] = DEMO_BUSINESSES["logistics"]["data"].copy()
            st.session_state["active_preset"] = "logistics"
            st.session_state["current_step"] = 2
            st.success("Loaded SwiftRoute Couriers data! Proceeding to Data Entry...")
            st.rerun()

    st.markdown("<div style='margin-top: 36px; text-align: center;'>", unsafe_allow_html=True)
    col_l, col_btn, col_r = st.columns([1, 2, 1])
    with col_btn:
        if st.button("Start Assessment with My Own Data →", type="primary", use_container_width=True):
            st.session_state["current_step"] = 2
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
