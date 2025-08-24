"""Functions for normalization."""
import logging
from pathlib import Path

import pandas as pd

from accounting.transaction_file import TransactionFile
from accounting.types import NormalizeFunc

# Module-wide logger
_NORMALIZE_FUNCS_LOGGER = logging.getLogger(__name__)

class Manual:
    @staticmethod
    def normalize(path: Path) -> TransactionFile:
        record = pd.read_csv(path, parse_dates=[0]) # type: ignore[reportUnknownMemberType]
        record["Alt Source"] = None
        record["Alt Source Official Name"] = None
        return TransactionFile(record)

class _WellsFargo:
    @staticmethod
    def _normalize(path: Path, source: str) -> TransactionFile:
        # Read from file
        record = pd.read_csv(path, parse_dates=[0], names=["Datetime", "Amount", "unknown0", "unknown1", "Official Name"]) # type: ignore[reportUnknownMemberType]

        # Move Amount column
        record["Amount"] = record.pop("Amount")

        record.drop(["unknown0", "unknown1"], axis=1, inplace=True)
        record.insert(1, "Source", source) # type: ignore[reportUnknownMemberType]
        record["Alt Source"] = None
        record["Alt Source Official Name"] = None

        record.reset_index(inplace=True, drop=True)

        return TransactionFile(record)

class WFChecking(_WellsFargo):
    @staticmethod
    def normalize(path: Path) -> TransactionFile:
        return _WellsFargo._normalize(path, source = "WF Checking")

class WFActiveCash(_WellsFargo):
    @staticmethod
    def normalize(path: Path) -> TransactionFile:
        return _WellsFargo._normalize(path, source = "WF Active Cash")

class Venmo:
    @staticmethod
    def normalize(path: Path) -> TransactionFile:
        # Read from CSV file
        original_record = pd.read_csv(path, header=2, parse_dates=[2]) # type: ignore[reportUnknownMemberType]

        # Drop the last row (which is final balance)
        original_record.drop(index=len(original_record)-1, inplace=True)
        # Drop the first row (which is blanks)
        original_record.drop(index=0, inplace=True)

        # Convert the dollar amount to a float.
        for char in ["$", " ", ","]:
            original_record["Amount (total)"] = original_record["Amount (total)"].str.replace(char, "")
        original_record["Amount (total)"] = original_record["Amount (total)"].astype(float)
        record = pd.DataFrame()

        # Entries that are not yet represented in the checking account.
        record["Datetime"] = original_record["Datetime"]
        record["Source"] = "Venmo"

        # Convention for Venmo transaction name generation specified here
        record["Official Name"] = "(" + original_record["From"] + "->" + original_record["To"]+ ") " + original_record["Note"]
        record.loc[original_record["Type"] == "Standard Transfer", "Official Name"] = "Venmo Cashout"

        record["Amount"] = original_record["Amount (total)"]
        record["Alt Source"] = None
        record["Alt Source Official Name"] = None

        record.reset_index(inplace=True, drop=True)

        return TransactionFile(record)

# Must add one of the above normalization functions here.
NORMALIZE_FUNCS: dict[str, NormalizeFunc] = {
    "Manual": Manual.normalize,
    "WF Checking": WFChecking.normalize,
    "WF Active Cash": WFActiveCash.normalize,
    "Venmo": Venmo.normalize,
}

# Add personal functions which will not be tracked by git.
try:
    from my.accounting.normalize_funcs import PERSONAL_NORMALIZE_FUNCS
    NORMALIZE_FUNCS.update(PERSONAL_NORMALIZE_FUNCS)
except ModuleNotFoundError as e:
    pass
