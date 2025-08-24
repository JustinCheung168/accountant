"""Defines the Categorizer class for inferring and assigning categories, supercategories, and groups to transactions based on categorization rules."""

import os

import colorama

from accounting.logger import LoggerMixin
from accounting.spec import Specification
from accounting.transaction_file import MergedTransactionFile


class Categorizer(LoggerMixin):
    """
    Infers and assigns categories, supercategories, and groups to transactions in a merged transaction file based on rules from a Categorization.
    """
    def __init__(self, spec: Specification):
        """
        Initialize the Categorizer with a given Specification.
        Args:
            spec (Specification): The report specification containing categorization rules.
        """
        self.spec = spec

    def categorize(self, merged_transaction_file: MergedTransactionFile) -> None:
        """
        Infer categorization for all transactions in the merged transaction file.
        Populates the Category, Supercategory, and Group columns in-place.
        - Uses keyword and exact match rules from the specification.
        - Ensures all categories have valid supercategories and groups.
        - Writes uncategorized entries to a CSV for manual review if needed.
        Args:
            merged_transaction_file (MergedTransactionFile): The merged transaction file to categorize.
        Raises:
            AssertionError: If any category is missing a supercategory or group.
        """
        df = merged_transaction_file.table
        category_supers = self.spec.categorization.category_supers
        category_groups = self.spec.categorization.category_groups
        exactmatch_categories = self.spec.categorization.exact_categorizers
        keyword_categories = self.spec.categorization.keyword_categorizers

        # Assign categories based on keyword matches
        for category, keywords in keyword_categories.items():
            for keyword in keywords:
                df.loc[df["Official Name"].str.upper().str.contains(keyword, na = False, regex=False), "Category"] = category

        # Assign categories based on exact matches
        for category, exactmatches in exactmatch_categories.items():
            for exactmatch in exactmatches:
                df.loc[df["Official Name"] == exactmatch, "Category"] = category

        # Map supercategories and groups
        df["Supercategory"] = df["Category"].map(category_supers)
        df["Group"] = df["Category"].map(category_groups)

        # Ensure that for any given category, the supercategory and group are also populated
        if (df["Category"].isna() ^ df["Supercategory"].isna()).any():
            self.logger.error(df.loc[df["Category"].isna() ^ df["Supercategory"].isna(), "Category"])
            raise AssertionError("One of the provided categorizers is using an invalid Category label; offending entries are above")
        if (df["Category"].isna() ^ df["Group"].isna()).any():
            self.logger.error(df.loc[df["Category"].isna() ^ df["Group"].isna(), "Category"])
            raise AssertionError("One of the provided categorizers is using an invalid Category label")

        uncategorized_mask = df["Category"].isna()
        num_uncategorized = uncategorized_mask.sum()

        # Temporary file to help identify uncategorized entries.
        UNCATEGORIZED_CSV = "./uncategorized.csv"
        if num_uncategorized > 0:
            self.logger.warning(f"Number of entries that were not autocategorized: {num_uncategorized}")
            value_uncategorized = df.loc[uncategorized_mask, "Amount"].sum()
            self.logger.warning(f"Total value of entries not autocategorized: {value_uncategorized}")
            df.loc[uncategorized_mask].sort_values(by="Amount").to_csv(UNCATEGORIZED_CSV, index=False)
            self.logger.warning(f"{colorama.Style.BRIGHT}Please look at {UNCATEGORIZED_CSV} and decide categories for its entries.{colorama.Style.RESET_ALL}")
        elif os.path.exists(UNCATEGORIZED_CSV):
            self.logger.info(f"Successfully autocategorized all expenses.")
            os.remove(UNCATEGORIZED_CSV)

        merged_transaction_file.table = df
