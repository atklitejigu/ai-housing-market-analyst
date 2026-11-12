import sys
from pathlib import Path
import numpy as np

# Add project root to Python path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
from src.config import DATA_RAW, DATA_PROCESSED


def load_raw_data(filename):
    file_path = DATA_RAW / filename
    df = pd.read_csv(file_path)
    return df


def create_approval_flag(df):
    # 1 = originated, 2 = approved but not accepted
    df = df[df["action_taken"].isin([1, 2, 3])].copy()
    df["approval_flag"] = df["action_taken"].isin([1, 2]).astype(int)
    return df


def create_income_bins(df):
    print("Creating income bins...")

    # Step 1: Clean income
    df["income_clean"] = df["income"]
    df.loc[df["income_clean"] <= 0, "income_clean"] = np.nan

    # Step 2: Define bins (HMDA uses thousands)
    bins = [0, 75, 150, 250, np.inf]
    labels = ["<$75K", "$75K-$150K", "$150K-$250K", "$250K+"]

    df["income_bin"] = pd.cut(
        df["income_clean"],
        bins=bins,
        labels=labels,
        right=False
    )

    # Step 3: Add Unknown category
    df["income_bin"] = df["income_bin"].cat.add_categories(["Unknown"])
    df["income_bin"] = df["income_bin"].fillna("Unknown")

    return df

    # Handle missing income explicitly
    df["income_bin"] = df["income_bin"].cat.add_categories("Unknown")
    df["income_bin"] = df["income_bin"].fillna("Unknown")

    return df

def create_income_flag(df):
    print("Creating income flag...")

    df["income_flag"] = "Valid"

    df.loc[df["income"].isna(), "income_flag"] = "Missing"
    df.loc[df["income"] == 0, "income_flag"] = "Zero"
    df.loc[df["income"] < 0, "income_flag"] = "Negative"

    return df

def create_log_loan_amount(df):
    print("Creating log loan amount...")

    df["loan_amount_clean"] = df["loan_amount"]
    df.loc[df["loan_amount_clean"] <= 0, "loan_amount_clean"] = np.nan

    df["log_loan_amount"] = np.log(df["loan_amount_clean"])

    return df

def clean_race(df):

    race_labels = {
        "Black or African American": "Black",
        "2 or more minority races": "Mixed minority",
        "Native Hawaiian or Other Pacific Islander": "Pacific Islander",
        "American Indian or Alaska Native": "Native American"
    }

    df["race_cat"] = df["derived_race"].replace(race_labels)

    # remove free form
    df = df[~df["race_cat"].isin(["Free Form Text Only"])]

    return df

def main():
    print("Loading HMDA raw dataset...")

    df = load_raw_data("hmda2024_dcmetro.csv")

    df = create_approval_flag(df)

    df = create_income_bins(df)        # ✅ UPDATED

    df=create_income_flag(df)
    
    df=create_log_loan_amount(df)

    df = clean_race(df)

    print("Saving processed dataset...")

    df.to_csv(DATA_PROCESSED / "hmda_2024_dcmetro_clean.csv", index=False)

    print("Dataset saved successfully.")


if __name__ == "__main__":
    main()
