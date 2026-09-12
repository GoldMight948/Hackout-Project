# Industrial Emission Leak-Point Detector & Circular Alternative Recommender

> An Enterprise-Grade SaaS Sustainability Analytics Platform (Microsoft Power BI / Tableau-grade) built with **Streamlit**, **Plotly**, **FastAPI**, and **SQLite**.

Designed for SMEs, industrial factories, manufacturers, logistics fleets, and commercial retailers to diagnose carbon leak points, benchmark government carbon credits, calculate compliance liabilities, simulate decarbonization trajectories, and unlock circular economy alternatives.

---

## 🌟 Key Capabilities & Workflow (12 Steps)

1. **Step 1 — Landing Page (`landing_view.py`)**: Modern hero section, value propositions, key capabilities, and instant call-to-action buttons.
2. **Step 2 — Authentication & Multi-User Profiles (`auth_view.py`)**: Secure login and business profile registration stored in SQLite, multi-user role management (Admin / Employee), and 1-click verified enterprise personas.
3. **Step 3 — Business Setup (`setup_view.py`)**: Multi-pillar operational activity entry covering:
   - **Energy**: Electricity (kWh), On-site Renewable %, Diesel (L), Petrol (L), Natural Gas (m³)
   - **Transport**: Heavy Truck Freight (km), Company Cars (km), Commute (km), Delivery Fleet count
   - **Waste**: Organic, Plastic, Metal, Paper, Hazardous waste streams (kg)
   - **Water**: Industrial freshwater consumption & untreated wastewater effluent (m³)
   - **Manufacturing**: Raw material embodied volume, output units, machine hours
   - **Carbon Credits**: Government allocation, carbon price ($/t), and registry balance
4. **Step 4 — Upload Existing Data (`upload_view.py`)**: CSV and Excel (`.xlsx`) file ingestion, downloadable pre-formatted templates, pre-loaded industry datasets, and live spreadsheet editing with `st.data_editor`.
5. **Step 5 — Executive Dashboard (`dashboard_view.py`)**:
   - 7 Core KPI cards (Gross Emissions, Credits Allocated, Credits Used, Deficit, Remaining, Compliance Cost, Eco Score)
   - **Plotly Visualizations**:
     - Gauge Chart (0–100 Sustainability Score)
     - Donut Chart (Carbon Credits Used vs Remaining)
     - Pie Chart (Pillar contribution)
     - Horizontal Bar Chart (Top emission categories)
     - Stacked Bar Chart (12-Month seasonal operational trajectory)
     - Line Chart (Emission trend curve)
     - Area Chart (Cumulative footprint vs carbon cap run-rate)
6. **Step 5 Extended — Deep-Dive Analytics (`analytics_view.py`)**:
   - **Sankey Diagram**: Industrial Material Flow (*Raw Input -> Production -> Scrap/Waste -> Recycling -> Recovered Feedstock*)
   - **Treemap**: Departmental emission hierarchy
   - **Intensity Heatmap**: 12-Month x 6-Pillar operational matrix
   - **Scatter Plot**: Production output correlation with OLS trendline
   - **ML 12-Month Forecast**: Polynomial regression for Business-As-Usual (BAU) vs Decarbonization pathway
   - **Industry Benchmarking**: Peer comparison against sector leaders
7. **Step 6 — Emission Leak Detection (`leak_detection_view.py`)**: Automated ranking of Top 10 operational hotspots by tonnes CO₂e, annual dollar loss, urgency index, and priority status badges.
8. **Step 7 — Carbon Credit Analysis & Marketplace (`carbon_credits_view.py`)**:
   - Automated Net Carbon Status determination (🟢 Carbon Neutral vs 🔴 Carbon Credit Deficit)
   - Compliance cost calculation and trading revenue estimations
   - Simulated Spot Carbon Market Desk with verified offsets (Verra VCS, Gold Standard, DAC)
9. **Step 8 — AI Recommendation Engine (`recommendations_view.py`)**: Expandable cards targeting the primary leak hotspot with CO₂ saved, CapEx estimate, ROI %, payback timeframe, difficulty, circular benefits, and government subsidies.
10. **Step 9 — Before vs After Simulator (`simulator_view.py`)**: Real-time multi-slider sandbox updating KPIs, grouped comparison charts, and carbon credit balance with zero latency.
11. **Step 10 — Circular Alternatives (`circular_view.py`)**: 4R closed-loop framework (Reuse, Recycle, Recover, Replace) across Plastics, Organics, Metals, and Water with commercial supplier partnerships.
12. **Step 11 — Reports & ESG Compliance (`reports_view.py`)**:
    - Multi-format exports: Excel (`.xlsx` multi-sheet workbook), CSV data tables, and browser Print/PDF Audit Dossier
    - ESG compliance checklist (GHG Protocol Scope 1-3, ISO 14064, CSRD readiness)
    - Immutable SQLite data audit trail
13. **Step 12 — Platform Settings (`settings_view.py`)**: Light/Dark theme toggle with high contrast, profile editing, and customizable regional GHG emission factors.

---

## 🛠️ Architecture & Tech Stack

- **Frontend**: Streamlit 1.63+, Plotly Graph Objects & Express
- **Backend API**: FastAPI, Uvicorn, Pydantic
- **Data Engine**: Pandas, NumPy
- **Persistence**: SQLite3 (`emissions_app.db`)
- **Exporting**: OpenPyXL, CSV, Print-Ready CSS

---

## 🚀 Quick Start Guide

### 1. Run the Streamlit Dashboard
```bash
python -m streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### 2. Run the FastAPI REST Microservice (Optional)
```bash
python -m uvicorn api:app --reload --port 8000
```
API Documentation and Swagger UI will be available at `http://localhost:8000/docs`.

### 3. Run Automated Tests
```bash
python test_app.py
```
Validates SQLite CRUD, GHG calculations, Top 10 leak diagnostics, ML forecasting, and FastAPI endpoints.
