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
}
