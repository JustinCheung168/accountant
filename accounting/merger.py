import pandas as pd

from accounting.logger import LoggerMixin
from accounting.spec import Specification
from accounting.transaction_file import TransactionFile, MergedTransactionFile

class Merger(LoggerMixin):
    def __init__(self, spec: Specification):
        self.spec = spec

    def merge(self, transaction_files: list[TransactionFile]) -> MergedTransactionFile:
        records: list[pd.DataFrame] = []
        for transaction_file in transaction_files:
            records.append(transaction_file.table)

        concatenated_record = pd.concat(records)

        # Sort using the stable mergesort
        concatenated_record.sort_values(by=["Datetime"], inplace=True, kind='mergesort')
        concatenated_record.reset_index(inplace=True, drop=True)

        # Find and remove redundant entries
        merged_record = Merger._consolidate_redundant(concatenated_record)

        # Filter to the requested dates
        merged_record = merged_record[(self.spec.date_start <= merged_record['Datetime']) & (merged_record['Datetime'] <= self.spec.date_end)]

        merged_record["Category"] = None
        merged_record["Supercategory"] = None
        merged_record["Group"] = None

        return MergedTransactionFile(merged_record)

    @staticmethod
    def _consolidate_redundant(record: pd.DataFrame) -> pd.DataFrame:
        # Move certain rows to be supplemental.
        # Make sure these have information introduced elsewhere
        paystub_ge_redundant = record["Official Name"].str.contains("GENERAL ELECTRIC REG.SALARY") # Corresponds to Pay Stubs (GE)
        paystub_gehc_redundant = record["Official Name"].str.contains("GE HEALTHCARE TE REG.SALARY") # Corresponds to Pay Stubs (GEHC)
        paystub_redundant = paystub_ge_redundant | paystub_gehc_redundant
        venmo_redundant = record["Official Name"].str.contains("VENMO PAYMENT") # Corresponds to Venmo

        from_wf_checking = record["Source"].str.contains("WF Checking")

        redundant = from_wf_checking & (paystub_redundant | venmo_redundant)

        # TODO add some cross-comparison of the two sources to make sure their totals are about the same

        return record.loc[~redundant].copy().reset_index(drop=True)
    