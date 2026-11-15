import streamlit as st
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(page_title="Interactive RCSA Dashboard", layout="wide")

st.title("🛡️ Interactive Operational Risk Control Self-Assessment (RCSA)")
st.markdown("Assess inherent risks, evaluate controls, calculate residual risk scores, and **add custom risks dynamically**.")

# Initialize Session State so user-added entries persist across reruns
if "rcsa_data" not in st.session_state:
    initial_data = [
        {
            "Risk_ID": "RSK-001",
            "Category": "Systems & Technology",
            "Risk_Description": "Core banking system downtime during peak trading hours",
            "Inherent_Likelihood": 3,
            "Inherent_Impact": 5,
            "Owner": "IT Infrastructure",
            "Control_Name": "Automated Failover & Disaster Recovery",
            "Control_Effectiveness": 0.80
        },
        {
            "Risk_ID": "RSK-002",
            "Category": "Execution & Process",
            "Risk_Description": "Manual data entry error in high-value wire transfer settlement",
            "Inherent_Likelihood": 4,
            "Inherent_Impact": 4,
            "Owner": "Operations",
            "Control_Name": "Dual-authorization maker-checker workflow",
            "Control_Effectiveness": 0.75
        },
        {
            "Risk_ID": "RSK-003",
            "Category": "Fraud & Security",
            "Risk_Description": "Unauthorized access and fraudulent external payment processing",
            "Inherent_Likelihood": 2,
            "Inherent_Impact": 5,
            "Owner": "Information Security",
            "Control_Name": "Multi-Factor Authentication (MFA) & AI Fraud Monitoring",
            "Control_Effectiveness": 0.85
        },
        {
            "Risk_ID": "RSK-004",
            "Category": "Compliance & Legal",
            "Risk_Description": "Failure to report suspicious transactions under regulatory AML guidelines",
            "Inherent_Likelihood": 2,
            "Inherent_Impact": 4,
            "Owner": "Compliance",
            "Control_Name": "Automated Transaction Monitoring Rules Engine",
            "Control_Effectiveness": 0.70
        }
    ]
    st.session_state.rcsa_data = pd.DataFrame(initial_data)

# Function to calculate scores and risk ratings automatically
def process_rcsa(df):
    df = df.copy()
    df["Inherent_Risk_Score"] = df["Inherent_Likelihood"] * df["Inherent_Impact"]
    
    # Residual Likelihood calculation based on control effectiveness
    df["Residual_Likelihood"] = np.ceil(
        df["Inherent_Likelihood"] * (1 - df["Control_Effectiveness"])
    ).clip(lower=1)

    df["Residual_Risk_Score"] = df["Residual_Likelihood"] * df["Inherent_Impact"]

    def get_risk_rating(score):
        if score >= 15:
            return "Critical"
        elif score >= 10:
            return "High"
        elif score >= 5:
            return "Medium"
        else:
            return "Low"

    df["Inherent_Rating"] = df["Inherent_Risk_Score"].apply(get_risk_rating)
    df["Residual_Rating"] = df["Residual_Risk_Score"].apply(get_risk_rating)
    return df

# --- SIDEBAR: INPUT FORM FOR NEW RISKS ---
st.sidebar.header("➕ Add New Risk & Control")

with st.sidebar.form("add_risk_form"):
    next_id = f"RSK-{len(st.session_state.rcsa_data) + 1:03d}"
    
    category = st.selectbox(
        "Risk Category", 
        ["Systems & Technology", "Execution & Process", "Fraud & Security", "Compliance & Legal", "Third-Party Risk", "People & Conduct"]
    )
    
    description = st.text_area("Risk Description", placeholder="e.g., Unpatched vulnerability in third-party payment API")
    owner = st.text_input("Risk Owner / Department", placeholder="e.g., IT Security")
    
    st.markdown("---")
    st.markdown("**Inherent Risk Scoring (1 to 5)**")
    likelihood = st.slider("Inherent Likelihood", 1, 5, 3)
    impact = st.slider("Inherent Impact", 1, 5, 3)
    
    st.markdown("---")
    st.markdown("**Mitigating Control Assessment**")
    control_name = st.text_input("Control Name", placeholder="e.g., Automated Patch Management & Testing")
    control_eff_percent = st.slider("Control Effectiveness (%)", 0, 100, 75)
    
    submit_button = st.form_submit_button(label="Submit New Risk")

# Handle Form Submission
if submit_button:
    if description.strip() and control_name.strip():
        new_row = {
            "Risk_ID": next_id,
            "Category": category,
            "Risk_Description": description,
            "Inherent_Likelihood": likelihood,
            "Inherent_Impact": impact,
            "Owner": owner if owner else "General Operations",
            "Control_Name": control_name,
            "Control_Effectiveness": control_eff_percent / 100.0
        }
        # Append to session state dataframe
        st.session_state.rcsa_data = pd.concat([st.session_state.rcsa_data, pd.DataFrame([new_row])], ignore_index=True)
        st.sidebar.success(f"Successfully added {next_id}!")
        st.rerun()
    else:
        st.sidebar.error("Please provide both a Risk Description and a Control Name.")

# --- MAIN DASHBOARD PROCESSING ---
df_rcsa = process_rcsa(st.session_state.rcsa_data)

# Top-Level Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Assessed Risks", value=len(df_rcsa))
with col2:
    critical_count = len(df_rcsa[df_rcsa["Residual_Rating"] == "Critical"])
    st.metric(label="Critical Residual Risks", value=critical_count, delta=-1 if critical_count > 0 else None)
with col3:
    avg_residual = round(df_rcsa["Residual_Risk_Score"].mean(), 1)
    st.metric(label="Average Residual Score", value=avg_residual)

st.divider()

# Sidebar Filter Options
st.sidebar.markdown("---")
st.sidebar.header("🔍 Filter Register")
selected_category = st.sidebar.selectbox("Filter by Category", ["All"] + list(df_rcsa["Category"].unique()))

if selected_category != "All":
    filtered_df = df_rcsa[df_rcsa["Category"] == selected_category]
else:
    filtered_df = df_rcsa

# Display Report Table
st.subheader("📋 Dynamic RCSA Risk Register")
columns_to_show = [
    "Risk_ID", "Category", "Risk_Description", "Owner",
    "Inherent_Risk_Score", "Inherent_Rating", 
    "Control_Name", "Control_Effectiveness", 
    "Residual_Risk_Score", "Residual_Rating"
]

st.dataframe(filtered_df[columns_to_show], use_container_width=True)

# Option to reset data
if st.sidebar.button("Reset to Default Risks"):
    del st.session_state.rcsa_data
    st.rerun()