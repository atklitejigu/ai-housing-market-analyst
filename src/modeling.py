
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
from insights import generate_insights

from config import DATA_PROCESSED, OUTPUT_MODELS, OUTPUT_CHARTS


def load_data():

    print("Loading processed dataset...")

    df = pd.read_csv(DATA_PROCESSED / "hmda_2024_dcmetro_clean.csv")

    return df


def run_logit(df):

    print("Running logistic regression (formula-based)...")

    model = smf.logit(
    formula="""
    approval_flag ~ 
    C(race_cat, Treatment(reference='White')) *
    C(income_bin, Treatment(reference='<$75K')) +
    log_loan_amount
    """,
    data=df
)

    results = model.fit()

    return results


def save_results(results, filename):
    print(f"Saving model results: {filename}")

    summary = results.summary().as_text()

    with open(OUTPUT_MODELS / filename, "w") as f:
        f.write(summary)

    odds_ratios = np.exp(results.params)

    odds_df = pd.DataFrame({
        "variable": results.params.index,
        "coefficient": results.params.values,
        "odds_ratio": odds_ratios
    })

    odds_df.to_csv(OUTPUT_MODELS / "odds_ratios_full.csv", index=False)

    print("Results saved.")


def plot_odds_ratios(results, filename, include_interactions=False):

    odds = np.exp(results.params)

    df_plot = pd.DataFrame({
        "variable": odds.index,
        "odds_ratio": odds.values
    })

    # Drop intercept
    df_plot = df_plot[df_plot["variable"] != "Intercept"]

    # Split logic
    if include_interactions:
        df_plot = df_plot[df_plot["variable"].str.contains(":")]
    else:
        df_plot = df_plot[~df_plot["variable"].str.contains(":")]

    # Sort for readability
    df_plot = df_plot.sort_values("odds_ratio")

    plt.figure(figsize=(10, 8))
    plt.barh(df_plot["variable"], df_plot["odds_ratio"])

    plt.axvline(1, linestyle="--")
    plt.title("Odds Ratios" + (" (Interactions)" if include_interactions else " (Main Effects)"))
    plt.xlabel("Odds Ratio")

    plt.tight_layout()
    plt.savefig(OUTPUT_CHARTS / filename)
    plt.close()

def save_odds_ratios(results, filename):
    import numpy as np
    import pandas as pd

    odds = np.exp(results.params)

    df_odds = pd.DataFrame({
        "variable": odds.index,
        "odds_ratio": odds.values
    })

    df_odds.to_csv(OUTPUT_MODELS / filename, index=False)

def main():
    df = load_data()

    # =========================
    # MODEL 1: FULL DATASET
    # =========================
    print("\n=== MODEL 1: FULL DATA ===")

    results_full = run_logit(df)

    save_results(results_full, filename="logit_full_with_interaction.txt")
    save_odds_ratios(results_full, filename="odds_full.csv")

    # ✅ STEP 5 GOES HERE
    odds_full = pd.read_csv(OUTPUT_MODELS / "odds_full.csv")

    insights_full = generate_insights(odds_full)

    print("\n--- AUTO INSIGHTS (FULL MODEL) ---")
    for i in insights_full:
        print(i)

    # Plot
    plot_odds_ratios(results_full, "main_effects_full.png", include_interactions=False)
    plot_odds_ratios(results_full, "interactions_full.png", include_interactions=True)


    # =========================
    # MODEL 2: EXCLUDE UNKNOWN INCOME
    # =========================
    print("\n=== MODEL 2: EXCLUDING UNKNOWN INCOME ===")

    df_clean = df[df["income_bin"] != "Unknown"].copy()

    results_clean = run_logit(df_clean)

    save_results(results_clean, filename="logit_no_unknown_with_interaction.txt")
    save_odds_ratios(results_clean, filename="odds_no_unknown.csv")

    # ✅ STEP 5 AGAIN (for second model)
    odds_clean = pd.read_csv(OUTPUT_MODELS / "odds_no_unknown.csv")

    insights_clean = generate_insights(odds_clean)

    print("\n--- AUTO INSIGHTS (NO UNKNOWN MODEL) ---")
    for i in insights_clean:
        print(i)

    # Plot
    plot_odds_ratios(results_clean, "main_effects_no_unknown.png", include_interactions=False)
    plot_odds_ratios(results_clean, "interactions_no_unknown.png", include_interactions=True)


    print("\n✅ Both models completed with insights.")
    
if __name__ == "__main__":

    main()
