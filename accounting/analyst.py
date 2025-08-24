"""Defines the Analyst class, which orchestrates the normalization, merging, categorization, and analysis of transaction data for accounting reports."""

import glob
from pathlib import Path

from accounting.analyze_funcs import ANALYZE_FUNCS
from accounting.categorizer import Categorizer
from accounting.logger import LoggerMixin
from accounting.merger import Merger
from accounting.normalizer import Normalizer, MissingNormalizationStrategyException
from accounting.spec import Specification
from accounting.transaction_file import TransactionFile
from accounting.transaction_file_descriptor import TransactionFileDescriptor, IgnoreTransactionFileException

class Analyst(LoggerMixin):
    """
    Top-level manager for the accounting workflow.
    Orchestrates normalization, merging, categorization, and analysis of transaction data as specified by a Specification.
    """
    def __init__(self, spec: Specification):
        """
        Initialize the Analyst with a given Specification.
        Args:
            spec (Specification): The report specification containing data sources, date range, and analyses to run.
        Raises:
            KeyError: If any requested analysis is not found in ANALYZE_FUNCS.
        """
        self._validate_analyses_in_spec(spec)
        self.spec = spec
        self.normalizer = Normalizer(spec)
        self.merger = Merger(spec)
        self.categorizer = Categorizer(spec)

    def _validate_analyses_in_spec(self, spec: Specification):
        """
        Ensure all requested analyses in the specification are implemented.
        Args:
            spec (Specification): The report specification.
        Raises:
            KeyError: If an analysis name is not found in ANALYZE_FUNCS.
        """
        for analysis in spec.analysis_names:
            if analysis not in ANALYZE_FUNCS:
                raise KeyError(f"Analysis {analysis} provided in specification does not exist in `ANALYZE_FUNCS`")

    def run_analysis(self):
        """
        Run the full accounting workflow:
        - Normalize all transaction files in the data source directory
        - Merge them into a single transaction file
        - Categorize all transactions
        - Run all requested analyses and save their results
        """
        transaction_files: list[TransactionFile] = []
        transaction_file_relpaths = self.list_all_files_relative_recursively(self.spec.path_data_source)
        for transaction_file_relpath in transaction_file_relpaths:
            try:
                transaction_file_desc = TransactionFileDescriptor(transaction_file_relpath)
            except IgnoreTransactionFileException:
                continue
            in_relevant_year = (self.spec.date_start.year <= transaction_file_desc.year) and (transaction_file_desc.year <= self.spec.date_end.year)
            if in_relevant_year:
                try:
                    transaction_file = self.normalizer.normalize(transaction_file_desc)
                    transaction_files.append(transaction_file)
                except MissingNormalizationStrategyException as e:
                    self.logger.warning(f"Cannot normalize {transaction_file_relpath}; skipping it. {e}")
        merged_transaction_file = self.merger.merge(transaction_files)
        self.categorizer.categorize(merged_transaction_file)
        self.logger.info(f"Writing analyses...")
        # Perform the requested analyses.
        for analysis_name in self.spec.analysis_names:
            analysis = ANALYZE_FUNCS[analysis_name]
            result_message = analysis(self.spec.path_data_report, merged_transaction_file.table, self.spec)
            if result_message is not None:
                self.logger.info(result_message)

    @staticmethod
    def list_all_files_relative_recursively(directory: Path) -> list[Path]:
        """
        Recursively list all files in a directory, returning paths relative to the directory root.
        Args:
            directory (Path): The root directory to search.
        Returns:
            list[Path]: List of relative file paths.
        """
        return [Path(x).relative_to(directory) for x in glob.glob(str(directory / Path("./**/*.*")), recursive=True)]
