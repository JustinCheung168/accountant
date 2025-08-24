import os
from pathlib import Path

import pandas as pd

from accounting.logger import LoggerMixin
from accounting.normalize_funcs import NORMALIZE_FUNCS
from accounting.spec import Specification
from accounting.transaction_file import TransactionFile
from accounting.transaction_file_descriptor import TransactionFileDescriptor

class MissingNormalizationStrategyException(ValueError):
    """Raised when a normalization strategy for a given transaction file type is not found."""

class Normalizer(LoggerMixin):
    def __init__(self, spec: Specification):
        self.spec = spec

    def normalize(self, transaction_file_desc: TransactionFileDescriptor, cache: bool = True) -> TransactionFile:
        """
        Normalize a transaction file.
        
        Args:
            transaction_file_desc (TransactionFileDescriptor): Descriptor to produce a normalized transaction file from.
        """
        if transaction_file_desc.transaction_file_type not in NORMALIZE_FUNCS:
            raise MissingNormalizationStrategyException(f"Second part of path must be one of {list(NORMALIZE_FUNCS.keys())}. Got {transaction_file_desc.transaction_file_type}.")

        source_path = self.spec.path_data_source / transaction_file_desc.relpath

        # Read cache
        normalized_path = Path()
        if cache:
            normalized_path = self.spec.path_data_normalized / transaction_file_desc.relpath.with_suffix(".csv")
            if normalized_path.exists():
                df = self.read_from_cache(normalized_path)
                self.logger.debug(f"Found cache for {source_path} at {normalized_path}, will not reprocess")
                return TransactionFile(df)

        normalize_func = NORMALIZE_FUNCS[transaction_file_desc.transaction_file_type]
        self.logger.debug(f"Normalizing {source_path} via {transaction_file_desc.transaction_file_type}")
        transaction_file = normalize_func(source_path)

        # Write cache
        if cache:
            os.makedirs(normalized_path.parent, exist_ok=True)
            transaction_file.table.to_csv(normalized_path, index=False)

        return transaction_file

    def read_from_cache(self, cache_path: Path) -> pd.DataFrame:
        return pd.read_csv(cache_path, header=0, parse_dates=[0], dtype = {'Alt Source': str, 'Alt Source Official Name': str}) # type: ignore[reportUnknownMemberType]
