import pandas as pd
import numpy as np

def run_rcsa_assessment():
    # 1. Define Inherent Risk Data (Risk Register)
    # Likelihood and Impact scored on a standard 1-5 scale
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

    # 2. Define Control Assessment Data
    # Control Effectiveness expressed as a percentage reduction in likelihood (0.0 to 1.0)
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

    # 3. Merge data and calculate scores
    # Inherent Risk Score = Inherent Likelihood * Inherent Impact (Max 25)
    df_rcsa = pd.merge(df_risks, df_controls, on="Risk_ID", how="left")
    df_rcsa["Inherent_Risk_Score"] = df_rcsa["Inherent_Likelihood"] * df_rcsa["Inherent_Impact"]

    # Residual Risk Likelihood Calculation: 
    # Reduces the likelihood based on control effectiveness, rounded up and bounded at minimum 1
    df_rcsa["Residual_Likelihood"] = np.ceil(
        df_rcsa["Inherent_Likelihood"] * (1 - df_rcsa["Control_Effectiveness"])
    ).clip(lower=1)

    # Residual Risk Score = Adjusted Residual Likelihood * Inherent Impact
    df_rcsa["Residual_Risk_Score"] = df_rcsa["Residual_Likelihood"] * df_rcsa["Inherent_Impact"]

    # 4. Define Risk Rating Bandings Function
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

    # 5. Format Output Report View
    columns_to_show = [
        "Risk_ID", "Category", "Risk_Description", 
        "Inherent_Risk_Score", "Inherent_Rating", 
        "Control_Name", "Control_Effectiveness", 
        "Residual_Risk_Score", "Residual_Rating"
    ]

    report = df_rcsa[columns_to_show]
    return report

if __name__ == "__main__":
    report_df = run_rcsa_assessment()
    print("==================================================================")
    print("                 OPERATIONAL RISK RCSA REPORT                     ")
    print("==================================================================")
    print(report_df.to_string(index=False))