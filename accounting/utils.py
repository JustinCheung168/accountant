from pathlib import Path
import re
import warnings

from typing import Optional

import pandas as pd

class SectionNotFoundException(ValueError):
    """"""

def find_row(df: pd.DataFrame, label: str) -> Optional[int]:
    """
    Get the index for the first row whose first column value is `label`.
    Assume the index is integer-valued (i.e. can be used for iloc lookup)
    """
    matches = df[df.iloc[:, 0] == label]
    if matches.empty:
        return None # Could not find a row whose first entry is `label`.
    # Take the first match's index.
    return matches.index[0]

def list_after(lst: list[str], value: str) -> list[str]:
    if value not in lst:
        raise ValueError(f"{value} not in {lst}")
    return lst[lst.index(value)+1:]

def extract_section(df: pd.DataFrame, section_label: str, possible_section_labels: list[str]) -> pd.DataFrame:
    """
    Extract a section from the DataFrame given a start label and possible next section labels.
    
    """
    # This section's content starts on the next row after the row with the section's label.
    section_label_row = find_row(df, section_label)
    if section_label_row is None:
        raise SectionNotFoundException(f"Could not find section {section_label}.")
    
    # Find the next section
    # (or if there is no next section, then this is the last section,
    # so its end is the end of the table.)
    end = len(df)
    for label in list_after(possible_section_labels, section_label):
        end = find_row(df, label)
        if end is not None:
            break

    section_header_row = df.iloc[section_label_row + 1]
    section = df.iloc[(section_label_row + 2):end].copy()
    section.columns = section_header_row.tolist()
    return section

def read_excel(path: Path) -> pd.DataFrame:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning, module=re.escape('openpyxl.styles.stylesheet'))
        df = pd.read_excel(path, engine='openpyxl') # type: ignore[reportUnknownMemberType]
    return df

def fillna(df: pd.DataFrame):
    with pd.option_context("future.no_silent_downcasting", True):
        df.fillna(0, inplace=True) # type: ignore[reportUnknownMemberType]

def get_unique(df: pd.DataFrame, col: str) -> list[str]:
    unique = list(df[col].unique())
    unique.sort()
    return unique

def get_categories(df: pd.DataFrame) -> list[str]:
    """"""
    return get_unique(df, "Category")

def get_supercategories(df: pd.DataFrame) -> list[str]:
    """"""
    return get_unique(df, "Supercategory")

def format_dollars(amount_sum: float) -> str:
    amount_sum = round(amount_sum, 2)
    zeropad = "0" if round(amount_sum * 100, 2) % 10 == 0 else ""
    if amount_sum < 0:
        return f"-${-amount_sum}{zeropad}"
    return f" ${amount_sum}{zeropad}"
