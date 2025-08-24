"""Defines data container classes for transaction records, enforcing schema and type checks."""
from typing import Callable

import pandas as pd

from accounting.logger import LoggerMixin

class SchemaMismatchException(Exception):
    """"""

class RigidDataFrame(LoggerMixin):
    """
    Base class for a rigidly-typed pandas DataFrame container.
    Enforces column names, order, and types as specified by COLUMN_TYPE_CHECKS.
    Subclasses should define COLUMN_TYPE_CHECKS.
    """
    COLUMN_TYPE_CHECKS: dict[str, Callable[[pd.Series], bool]] = {}
    def __init__(self, table: pd.DataFrame):
        """
        Initialize the RigidDataFrame with a DataFrame and validate its schema.
        Args:
            table (pd.DataFrame): The DataFrame to wrap and validate.
        Raises:
            SchemaMismatchException: If the DataFrame does not match the required schema.
        """
        self.table = table
        self._assert_valid()

    def _assert_valid(self):
        """
        Check that this is a valid file object. This defines what constitutes a valid file.
        """
        # Check the number of columns
        if len(self.table.columns) != len(self.COLUMN_TYPE_CHECKS):
            raise SchemaMismatchException(f'Wrong number of columns (expected {len(self.COLUMN_TYPE_CHECKS)}, found {len(self.table.columns)})')
        
        # Check each column's datatype
        for col_name, col_type_check in self.COLUMN_TYPE_CHECKS.items():
            if col_name not in self.table.columns:
                raise SchemaMismatchException(f'Missing column {col_name}')
            elif not col_type_check(self.table[col_name]):
                raise SchemaMismatchException(f'Wrong type "{self.table[col_name].dtype}" for {col_name}')

        # Check the order of columns
        if list(self.table.columns) != list(self.COLUMN_TYPE_CHECKS.keys()):
            raise SchemaMismatchException(f'Columns are in wrong order: got {self.table.columns}, should be {self.COLUMN_TYPE_CHECKS.keys()}')

class TransactionFile(RigidDataFrame):
    COLUMN_TYPE_CHECKS: dict[str, Callable[[pd.Series], bool]] = {
        "Datetime": pd.api.types.is_datetime64_ns_dtype, # type: ignore[reportUnknownMemberType]
        "Source": pd.api.types.is_object_dtype, # type: ignore[reportUnknownMemberType]
        "Official Name": pd.api.types.is_object_dtype, # type: ignore[reportUnknownMemberType]
        "Amount": pd.api.types.is_float_dtype, # type: ignore[reportUnknownMemberType]
        "Alt Source": pd.api.types.is_object_dtype, # type: ignore[reportUnknownMemberType]
        "Alt Source Official Name": pd.api.types.is_object_dtype, # type: ignore[reportUnknownMemberType]
    }

class MergedTransactionFile(RigidDataFrame):
    COLUMN_TYPE_CHECKS: dict[str, Callable[[pd.Series], bool]] = {
        "Datetime": pd.api.types.is_datetime64_ns_dtype, # type: ignore[reportUnknownMemberType]
        "Source": pd.api.types.is_object_dtype, # type: ignore[reportUnknownMemberType]
        "Official Name": pd.api.types.is_object_dtype, # type: ignore[reportUnknownMemberType]
        "Amount": pd.api.types.is_float_dtype, # type: ignore[reportUnknownMemberType]
        "Alt Source": pd.api.types.is_object_dtype, # type: ignore[reportUnknownMemberType]
        "Alt Source Official Name": pd.api.types.is_object_dtype, # type: ignore[reportUnknownMemberType]
        "Category": pd.api.types.is_object_dtype, # type: ignore[reportUnknownMemberType]
        "Supercategory": pd.api.types.is_object_dtype, # type: ignore[reportUnknownMemberType]
        "Group": pd.api.types.is_object_dtype, # type: ignore[reportUnknownMemberType]
    }
