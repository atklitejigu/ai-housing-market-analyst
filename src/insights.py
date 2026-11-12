import pandas as pd
from src.streamlit_app import clean_variable_name  # adjust if needed

def generate_insights(odds_df):

    insights = []

    # Remove intercept
    df = odds_df[~odds_df["variable"].str.contains("Intercept")].copy()

    # -------------------------
    # CLEAN VARIABLE NAMES
    # -------------------------
    df["clean_var"] = df["variable"].apply(clean_variable_name)

    # -------------------------
    # REMOVE DUPLICATES
    # -------------------------
    df = df.sort_values("odds_ratio", ascending=False)
    df = df.drop_duplicates(subset="clean_var", keep="first")

    # -------------------------
    # Top positive drivers
    # -------------------------
    top_positive = df.head(5)

    for _, row in top_positive.iterrows():
        insights.append(
            f"{row['clean_var']} increases approval odds by {round(row['odds_ratio'], 2)}x"
        )

    # -------------------------
    # Top negative drivers
    # -------------------------
    df_sorted_neg = df.sort_values("odds_ratio")

    top_negative = df_sorted_neg.head(5)

    for _, row in top_negative.iterrows():
        insights.append(
            f"{row['clean_var']} decreases approval odds (OR={round(row['odds_ratio'], 2)})"
        )

    return insights
