import streamlit as st
import pandas as pd
from pathlib import Path

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS = BASE_DIR / "outputs"
CHARTS = OUTPUTS / "charts"
RESULTS = OUTPUTS / "model_results"

# -----------------------------
# Cleaner (FINAL VERSION)
# -----------------------------
def clean_variable_name(var):

    # -----------------------------
    # 1. REMOVE RAW MODEL SYNTAX (ADD HERE 👇)
    # -----------------------------
    var = var.replace("C(", "")
    var = var.replace(")", "")
    var = var.replace("Treatment(reference='<75K')", "")
    var = var.replace("Treatment(reference='White')", "")
    var = var.replace("income_bin", "")
    var = var.replace("race_cat", "")
    var = var.replace("[T.", "")
    var = var.replace("]", "")
    var = var.strip()


    # -----------------------------
    # 2. HANDLE INTERACTIONS (KEEP THIS)
    # -----------------------------
    if ":" in var:
        parts = var.split(":")
        parts = [p.strip() for p in parts]
        var = " & ".join(parts)


    # -----------------------------
    # 3. FORMAT LABELS (IMPROVE READABILITY)
    # -----------------------------
    if "$" in var:
        var = f"Income {var}"
    elif any(r in var.lower() for r in ["asian", "black", "pacific", "native", "mixed", "joint"]):
        var = f"Race: {var}"


    # -----------------------------
    # 4. FINAL CLEANUP
    # -----------------------------
    var = var.replace("-", "–")

    return var
    

# AI Section
def answer_question(query, df):
    query = query.lower()

    # -------------------------
    # Income
    # -------------------------
    if "income" in query:
        max_or = round(df[df["clean_var"].str.contains("Income")]["odds_ratio"].max(), 2)
        return f"Applicants in higher income brackets have significantly higher approval likelihood, with odds increasing up to {max_or} times compared to the baseline group."

    # -------------------------
    # Race / disparities
    # -------------------------
    if "race" in query or "disparity" in query:
        lowest = df.sort_values("odds_ratio").iloc[0]
        reduction = round((1 - lowest["odds_ratio"]) * 100, 1)
        return f"{lowest['clean_var']} exhibits the largest disparity, with approximately {reduction}% lower approval odds relative to the reference group."

    # -------------------------
    # Interaction effects
    # -------------------------
    if "interaction" in query or "difference" in query:
        return "Interaction effects show that increases in income do not lead to uniform improvements in approval odds across all groups, suggesting structural differences in how approval outcomes scale with borrower characteristics."
    # -------------------------
    # Loan size
    # -------------------------
    if "loan" in query:
        loan = df[df["clean_var"] == "Loan Size"]
        if not loan.empty:
            val = round(loan["odds_ratio"].iloc[0], 2)
            return f"Larger loan amounts are associated with higher approval likelihood, with odds increasing by approximately {val} times."

    # -------------------------
    # Default fallback
    # -------------------------
    return "Try asking about income effects, racial disparities, loan size, or interaction effects."

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
OUTPUTS = BASE_DIR / "outputs"
CHARTS = OUTPUTS / "charts"
RESULTS = OUTPUTS / "model_results"

st.set_page_config(page_title="AI Housing Market Analyst", layout="wide")

st.title("🏠 AI Housing Market Analyst")
st.markdown("Mortgage approval modeling with automated insights")

# -----------------------------
# DEBUG (TEMPORARY)
# -----------------------------
st.write("BASE_DIR:", BASE_DIR)
st.write("Outputs exists:", OUTPUTS.exists())
st.write("Charts exists:", CHARTS.exists())
st.write("Results exists:", RESULTS.exists())

# -----------------------------
# Model selection
# -----------------------------
model_choice = st.radio(
    "Select Model",
    ["Full Data", "Exclude Unknown Income"]
)

if model_choice == "Full Data":
    main_chart = CHARTS / "main_effects_full.png"
    interaction_chart = CHARTS / "interactions_full.png"
    odds_file = RESULTS / "odds_ratios_full.csv"
    log_file = RESULTS / "logit_full_with_interaction.txt"
else:
    main_chart = CHARTS / "main_effects_no_unknown.png"
    interaction_chart = CHARTS / "interactions_no_unknown.png"
    odds_file = RESULTS / "odds_no_unknown.csv"
    log_file = RESULTS / "logit_no_unknown_with_interaction.txt"

# -----------------------------
# Load data ONCE (IMPORTANT)
# -----------------------------
df = None

if odds_file.exists():
    df = pd.read_csv(odds_file)
    st.write("Loaded odds file:", odds_file)

    df["clean_var"] = df["variable"].apply(clean_variable_name)
    df = df[~df["variable"].str.contains("Intercept")]

else:
    st.error(f"Missing odds file: {odds_file}")
    st.stop()

# -----------------------------
# Charts
# -----------------------------
st.subheader("📊 Main Effects")

if main_chart.exists():
    st.image(str(main_chart))
else:
    st.error(f"Missing chart: {main_chart}")

st.subheader("🔗 Interaction Effects")

if interaction_chart.exists():
    st.image(str(interaction_chart))
else:
    st.error(f"Missing chart: {interaction_chart}")

# -----------------------------
# Odds Ratios Table
# -----------------------------
st.subheader("📈 Odds Ratios")

if df is not None:
    st.dataframe(df)
else:
    st.warning("Odds ratio file not found")

# -----------------------------
# Model Summary
# -----------------------------
st.subheader("📄 Model Summary")

if log_file.exists():
    with open(log_file, "r") as f:
        st.text(f.read())
else:
    st.error(f"Missing model summary: {log_file}")

# -----------------------------
# Key Takeaways (Executive Layer)
# -----------------------------
st.markdown("### 📌 Key Takeaways")

st.write("""
- Income is the strongest predictor of mortgage approval  
- Higher income levels increase approval odds by roughly 2.5x to 3x  
- Race effects persist even after controlling for income  
- Higher income does not fully offset disparities across groups  
- Loan size also contributes positively to approval likelihood  
""")

# -----------------------------
# Insights
# -----------------------------
st.subheader("🧠 Key Insights")

if df is not None:

    df_sorted = df.sort_values("odds_ratio", ascending=False)

    # Reduce redundancy
    top_positive = df_sorted.head(3)
    top_negative = df_sorted.tail(3)

    st.markdown("### 🚀 Strongest Positive Effects")

    # Add summary instead of repetition
    st.write("Higher income groups consistently show 2.5x–3x higher approval odds relative to baseline.")

    for _, row in top_positive.iterrows():
        st.write(f"{row['clean_var']}: approval odds are {round(row['odds_ratio'],2)}x higher than baseline")

    st.markdown("### ⚠️ Strongest Negative Effects")

    for _, row in top_negative.iterrows():
        reduction = round((1 - row['odds_ratio']) * 100, 1)
        st.write(f"{row['clean_var']}: approximately {reduction}% lower approval odds (OR={round(row['odds_ratio'],2)})")

else:
    st.warning("No insights available")

st.markdown("### 🤖 Ask the Model")

query = st.text_input("Ask about income, race disparities, or approval drivers:")

if query:
    response = answer_question(query, df)

    # 🔽 REPLACE DISPLAY WITH THIS
    st.markdown("### 🤖 AI Insight")
    st.success(response)
