import streamlit as st
import pandas as pd
import numpy as np

# Page Config
st.set_page_config(page_title="Operational Risk RCSA Dashboard", layout="wide")

st.title("🛡️ Operational Risk Control Self-Assessment (RCSA)")
st.markdown("This dashboard models inherent risks, control effectiveness, and calculated residual risk scores.")

# 1. Define Inherent Risk Data (Risk Register)
@st.cache_data
def load_rcsa_data():
    data_risks = [
        {
            "Risk_ID": "RSK-001",
            "Category": "Systems & Technology",
            "Risk_Description": "Core banking system downtime during peak trading hours",
            "Inherent_Likelihood": 3,
            "Inherent_Impact": 5,
            "Owner": "IT Infrastructure"
        },
        {
            "Risk_ID": "RSK-002",
            "Category": "Execution & Process",
            "Risk_Description": "Manual data entry error in high-value wire transfer settlement",
            "Inherent_Likelihood": 4,
            "Inherent_Impact": 4,
            "Owner": "Operations"
        },
        {
            "Risk_ID": "RSK-003",
            "Category": "Fraud & Security",
            "Risk_Description": "Unauthorized access and fraudulent external payment processing",
            "Inherent_Likelihood": 2,
            "Inherent_Impact": 5,
            "Owner": "Information Security"
        },
        {
            "Risk_ID": "RSK-004",
            "Category": "Compliance & Legal",
            "Risk_Description": "Failure to report suspicious transactions under regulatory AML guidelines",
            "Inherent_Likelihood": 2,
            "Inherent_Impact": 4,
            "Owner": "Compliance"
        }
    ]

    df_risks = pd.DataFrame(data_risks)

    data_controls = [
        {
            "Control_ID": "CTL-101",
            "Risk_ID": "RSK-001",
            "Control_Name": "Automated Failover & Disaster Recovery",
            "Control_Effectiveness": 0.80
        },
        {
            "Control_ID": "CTL-102",
            "Risk_ID": "RSK-002",
            "Control_Name": "Dual-authorization maker-checker workflow",
            "Control_Effectiveness": 0.75
        },
        {
            "Control_ID": "CTL-103",
            "Risk_ID": "RSK-003",
            "Control_Name": "Multi-Factor Authentication (MFA) & AI Fraud Monitoring",
            "Control_Effectiveness": 0.85
        },
        {
            "Control_ID": "CTL-104",
            "Risk_ID": "RSK-004",
            "Control_Name": "Automated Transaction Monitoring Rules Engine",
            "Control_Effectiveness": 0.70
        }
    ]

    df_controls = pd.DataFrame(data_controls)

    # Merge data and calculate scores
    df_rcsa = pd.merge(df_risks, df_controls, on="Risk_ID", how="left")
    df_rcsa["Inherent_Risk_Score"] = df_rcsa["Inherent_Likelihood"] * df_rcsa["Inherent_Impact"]

    df_rcsa["Residual_Likelihood"] = np.ceil(
        df_rcsa["Inherent_Likelihood"] * (1 - df_rcsa["Control_Effectiveness"])
    ).clip(lower=1)

    df_rcsa["Residual_Risk_Score"] = df_rcsa["Residual_Likelihood"] * df_rcsa["Inherent_Impact"]

    def get_risk_rating(score):
        if score >= 15:
            return "Critical"
        elif score >= 10:
            return "High"
        elif score >= 5:
            return "Medium"
        else:
            return "Low"

    df_rcsa["Inherent_Rating"] = df_rcsa["Inherent_Risk_Score"].apply(get_risk_rating)
    df_rcsa["Residual_Rating"] = df_rcsa["Residual_Risk_Score"].apply(get_risk_rating)

    return df_rcsa

df_rcsa = load_rcsa_data()

# 2. Add Top-Level Metrics
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

# 3. Filter Options in Sidebar
st.sidebar.header("Filter RCSA Register")
selected_category = st.sidebar.selectbox("Filter by Category", ["All"] + list(df_rcsa["Category"].unique()))

if selected_category != "All":
    filtered_df = df_rcsa[df_rcsa["Category"] == selected_category]
else:
    filtered_df = df_rcsa

# 4. Display Report Table
st.subheader("📋 RCSA Risk Register & Control Assessment")
columns_to_show = [
    "Risk_ID", "Category", "Risk_Description", 
    "Inherent_Risk_Score", "Inherent_Rating", 
    "Control_Name", "Control_Effectiveness", 
    "Residual_Risk_Score", "Residual_Rating"
]

st.dataframe(filtered_df[columns_to_show], use_container_width=True)