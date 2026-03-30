
import pandas as pd

def generate_insights(odds_df):
    """
    Generate human-readable insights from odds ratios
    """

    insights = []

    # Remove intercept
    df = odds_df[~odds_df["variable"].str.contains("Intercept")].copy()

    # Sort for strongest effects
    df_sorted = df.sort_values("odds_ratio", ascending=False)

    # -------------------------
    # Top positive drivers
    # -------------------------
    top_positive = df_sorted.head(5)

    for _, row in top_positive.iterrows():
        insights.append(
            f"{row['variable']} increases approval odds by {round(row['odds_ratio'], 2)}x"
        )

    # -------------------------
    # Top negative drivers
    # -------------------------
    df_sorted_neg = df.sort_values("odds_ratio")

    top_negative = df_sorted_neg.head(5)

    for _, row in top_negative.iterrows():
        insights.append(
            f"{row['variable']} decreases approval odds (OR={round(row['odds_ratio'], 2)})"
        )

    return insights
