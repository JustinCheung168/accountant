"""
Functions for analyzing transaction data and producing reports.

All functions here must fit the schema specified in `AnalysisFunc`:
Args:
    artifact_dir (Path): Directory for report artifacts (unused).
    df (pd.DataFrame): The transaction DataFrame.
    spec (Specification): The report specification (unused).
Returns:
    Optional[str]: None (side effect only).
"""

import os
from pathlib import Path
from typing import Optional

import pandas as pd
import matplotlib.pyplot as plt
import calendar

from accounting.utils import format_dollars
from accounting.spec import Specification
from accounting.types import AnalysisFunc

def print_balance(artifact_dir: Path, df: pd.DataFrame, spec: Specification) -> Optional[str]:
    """
    Print the total balance of all transactions in the DataFrame.
    """
    print(f'Balance: {format_dollars(df["Amount"].sum())}')

def write_csv_of_merged_data(artifact_dir: Path, df: pd.DataFrame, spec: Specification) -> Optional[str]:
    """
    Write the merged transaction DataFrame to a CSV file in the artifact directory.
    """
    artifact_path = artifact_dir / Path("merged.csv")
    df.to_csv(artifact_path, index=False)
    return f"Wrote {artifact_path}"

def write_sorted_csv_of_merged_data(artifact_dir: Path, df: pd.DataFrame, spec: Specification) -> Optional[str]:
    """
    Write the merged transaction DataFrame to a CSV file in the artifact directory.
    """
    artifact_path = artifact_dir / Path("sorted.csv")
    df.sort_values(by="Amount").to_csv(artifact_path, index=False)
    return f"Wrote {artifact_path}"

def write_csv_above_1k_of_merged_data(artifact_dir: Path, df: pd.DataFrame, spec: Specification) -> Optional[str]:
    """
    Write the merged transaction DataFrame to a CSV file in the artifact directory.
    """
    artifact_path = artifact_dir / Path("merged_over_1k.csv")
    df[(df["Amount"]>=1000.00) | (df["Amount"]<=-1000.00)].to_csv(artifact_path, index=False)
    return f"Wrote {artifact_path}"

def write_txt_category_spending_summary(artifact_dir: Path, df: pd.DataFrame, spec: Specification) -> Optional[str]:
    """
    Write a text summary of category spending, grouped by Group, Supercategory, and Category, to the artifact directory.
    """
    artifact_path = artifact_dir / Path("category_spending.txt")
    with open(artifact_path, "w") as f:
        levels = ["Group", "Supercategory", "Category"]
        groups = spec.categorization.groups
        # Calculate overall balance
        balance = df["Amount"].sum()
        f.write(f'Total Balance: {format_dollars(balance)}\n')
        # Calculate after-tax salary (salary minus tax)
        after_tax_salary: float = df.loc[(df["Category"] == "Income - Salary") | (df["Category"] == "Income - Tax"), "Amount"].sum()
        f.write(f'After-Tax Salary: {format_dollars(after_tax_salary)}\n')
        # Calculate group breakdown
        for group, supercategories in groups.items():
            group_df: pd.DataFrame = df.loc[df["Group"] == group]
            group_sum = group_df["Amount"].sum()
            if "Group" in levels:
                income_fraction_str = f' ({round(100*-group_sum/after_tax_salary, 3)}% of after-tax salary)' if group != "INCOME" else ""
                f.write(f'{format_dollars(group_sum)} --- {group} {income_fraction_str}\n')
            for supercategory, categories in supercategories.items():
                supercategory_df: pd.DataFrame = df.loc[df["Supercategory"] == supercategory]
                supercategory_sum = supercategory_df["Amount"].sum()
                if "Supercategory" in levels:
                    f.write(f'\t{format_dollars(supercategory_sum)} --- {supercategory}\n')
                for category in categories:
                    category_df: pd.DataFrame = df.loc[df["Category"] == category]
                    category_sum = category_df["Amount"].sum()
                    if "Category" in levels:
                        f.write(f'\t\t{format_dollars(category_sum)} --- {category}\n')
    return f"Wrote {artifact_path}"

def write_png_category_spending_piechart(artifact_dir: Path, df: pd.DataFrame, spec: Specification) -> Optional[str]:
    raise NotImplementedError()

def write_png_monthly_food_spending_linechart(artifact_dir: Path, df: pd.DataFrame, spec: Specification) -> Optional[str]:
    raise NotImplementedError()

def write_txt_biggest_irregular_spending(artifact_dir: Path, df: pd.DataFrame, spec: Specification) -> Optional[str]:
    raise NotImplementedError()

def write_png_monthly_food_spending_stacked_barchart(artifact_dir: Path, df: pd.DataFrame, spec: Specification) -> Optional[str]:
    """
    Write a stacked bar chart of monthly food spending, grouped by specific categories.
    """
    artifact_path = artifact_dir / Path("monthly_food_spending_stacked_barchart.png")

    # Define the categories to include in the chart
    categories = [
        "Luxury Food - Restaurant",
        "Food - Groceries",
        "Food - Snacks",
        "Food - Drinks",
        "Food - Tip",
        "Food - Credit Card Processing",
    ]

    # Filter the DataFrame for the relevant categories
    df_filtered = df[df["Category"].isin(categories)].copy()

    # Extract the month from the transaction date
    df_filtered["Month"] = pd.to_datetime(df_filtered["Datetime"]).dt.month

    # Group by month and category, summing the amounts
    monthly_data = df_filtered.groupby(["Month", "Category"])["Amount"].sum().unstack(fill_value=0)

    # Calculate supercategory totals
    df_filtered["Supercategory"] = df_filtered["Category"].apply(
        lambda x: "Luxury Food" if x.startswith("Luxury Food") else "Food"
    )
    supercategory_totals = df_filtered.groupby(["Month", "Supercategory"])["Amount"].sum().unstack(fill_value=0)

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot the stacked bar chart
    bottom = None
    for category in categories:
        if category in monthly_data:
            ax.bar(
                monthly_data.index,
                monthly_data[category],
                label=category,
                bottom=bottom,
            )
            bottom = monthly_data[category] if bottom is None else bottom + monthly_data[category]

    # Add supercategory totals as text labels
    for month, row in supercategory_totals.iterrows():
        total_luxury_food = row.get("Luxury Food", 0)
        total_food = row.get("Food", 0)
        total_combined = total_luxury_food + total_food
        difference = total_combined - monthly_data.loc[month].sum()
        ax.text(
            month,
            total_combined + 50,  # Adjust position slightly above the bar
            f"Total: ${total_combined:.2f}\nDiff: ${difference:.2f}",
            ha="center",
            fontsize=10,
            color="black",
        )

    # Customize the chart
    ax.set_title("Monthly Food Spending (Stacked by Category)", fontsize=16)
    ax.set_xlabel("Month", fontsize=14)
    ax.set_ylabel("Spending ($)", fontsize=14)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels([calendar.month_abbr[i] for i in range(1, 13)], fontsize=12)
    ax.legend(title="Categories", fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    # Save the figure
    plt.tight_layout()
    plt.savefig(artifact_path)
    plt.close()

    return f"Wrote {artifact_path}"

# Mapping of analysis function names to their implementations.
ANALYZE_FUNCS: dict[str, AnalysisFunc] = {
    "print_balance": print_balance,
    "write_csv_of_merged_data": write_csv_of_merged_data,
    "write_sorted_csv_of_merged_data": write_sorted_csv_of_merged_data,
    "write_csv_above_1k_of_merged_data": write_csv_above_1k_of_merged_data,
    "write_txt_category_spending_summary": write_txt_category_spending_summary,
    "write_png_category_spending_piechart": write_png_category_spending_piechart,
    "write_png_monthly_food_spending_linechart": write_png_monthly_food_spending_linechart,
    "write_txt_biggest_irregular_spending": write_txt_biggest_irregular_spending,
    "write_png_monthly_food_spending_stacked_barchart": write_png_monthly_food_spending_stacked_barchart,
}
