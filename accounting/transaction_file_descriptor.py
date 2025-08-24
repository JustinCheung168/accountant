from pathlib import Path

class IgnoreTransactionFileException(Exception):
    """Special exception for a transaction file to intentionally silently ignore."""

class TransactionFileDescriptor:
    """Metadata useful for finding a transaction file and deciding whether to normalize it."""
    def __init__(self, relpath: Path):
        # Ensure this relpath is of the expected format.
        if len(relpath.parent.parts) < 2:
            raise ValueError(f"Relative path of transaction files must have at least 2 directories from the provided source directory. Got: {relpath}")

        year_str = relpath.parts[0]
        # Throw error if it is not possible to cast to int.
        year = int(year_str)

        transaction_file_type = relpath.parts[1]

        # This file does not need description.
        if transaction_file_type == "IGNORE":
            raise IgnoreTransactionFileException()

        self.relpath = relpath
        self.year = year
        self.transaction_file_type = transaction_file_type
