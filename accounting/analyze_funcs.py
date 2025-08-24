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
    os.makedirs(artifact_dir, exist_ok=True)
    artifact_path = artifact_dir / Path("merged.csv")
    df.to_csv(artifact_path, index=False)
    return f"Wrote {artifact_path}"

def write_txt_category_spending_summary(artifact_dir: Path, df: pd.DataFrame, spec: Specification) -> Optional[str]:
    """
    Write a text summary of category spending, grouped by Group, Supercategory, and Category, to the artifact directory.
    """
    os.makedirs(artifact_dir, exist_ok=True)
    artifact_path = artifact_dir / Path("category_spending.txt")
    with open(artifact_path, "w") as f:
        levels = ["Group", "Supercategory", "Category"]
        groups = spec.categorization.groups
        # Calculate overall balance
        balance = df["Amount"].sum()
        f.write(f'Total Balance: {format_dollars(balance)}\n')
        regular_income: float = df.loc[(df["Category"] == "Income - Salary") | (df["Category"] == "Income - Tax"), "Amount"].sum()
        f.write(f'Regular Income: {format_dollars(regular_income)}\n')
        # Calculate group breakdown
        for group, supercategories in groups.items():
            group_df: pd.DataFrame = df.loc[df["Group"] == group]
            group_sum = group_df["Amount"].sum()
            if "Group" in levels:
                income_fraction_str = f' ({round(100*-group_sum/regular_income, 3)}% of regular income)' if group != "INCOME" else ""
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

# Mapping of analysis function names to their implementations.
ANALYZE_FUNCS: dict[str, AnalysisFunc] = {
    "print_balance": print_balance,
    "write_csv_of_merged_data": write_csv_of_merged_data,
    "write_txt_category_spending_summary": write_txt_category_spending_summary,
    "write_png_category_spending_piechart": write_png_category_spending_piechart,
    "write_png_monthly_food_spending_linechart": write_png_monthly_food_spending_linechart,
    "write_txt_biggest_irregular_spending": write_txt_biggest_irregular_spending,
}
