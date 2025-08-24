"""Defines the Specification and Categorization classes for configuring accounting report generation, including data sources, date ranges, and category mappings."""

from datetime import datetime
import os
from pathlib import Path
from typing import TypeAlias

import yaml

CategorizationDict: TypeAlias = dict[str, dict[str, dict[str, list[str]]]]
SpecDict: TypeAlias = dict[str, str | list[str]]


class Categorization:
    """
    Loads and manages category mappings for transactions, including exact and keyword categorizers, groups, supercategories, and group assignments.
    """
    def __init__(self, categorization_path: Path):
        """
        Initialize Categorization from a YAML file.
        Args:
            categorization_path (Path): Path to the YAML file containing category definitions.
        Raises:
            KeyError: If required keys are missing in the YAML file.
        """
        # TODO make clearer error messages on misformatted file
        categorization_dict: CategorizationDict = yaml.safe_load(categorization_path.read_text())
        self.exact_categorizers = categorization_dict['categorizers']['exact']
        self.keyword_categorizers = categorization_dict['categorizers']['keyword']
        self.groups = categorization_dict['groups']
        # Invert given groups map to make the categories map of <category>: <supercategory> and of <category>: <group>
        self.category_supers: dict[str, str] = {}
        self.category_groups: dict[str, str] = {}
        for group, supercategories in self.groups.items():
            for supercategory, categories in supercategories.items():
                for category in categories:
                    self.category_supers[category] = supercategory
                    self.category_groups[category] = group


class Specification:
    """
    Represents a specification from which to produce a report.
    """
    def __init__(self, spec_path: Path):
        """
        Parse a specification YAML file and store its information for report generation.
        Args:
            spec_path (Path): Path to the YAML file containing the report specification.
        Raises:
            FileNotFoundError: If the data source path does not exist.
            TypeError: If any required field is of the wrong type.
        """
        spec_dict: SpecDict = yaml.safe_load(spec_path.read_text())

        self.path_data_source = self._safe_get_path(spec_dict, "path_data_source")
        if not self.path_data_source.exists():
            raise FileNotFoundError(f"Could not find data source {self.path_data_source}")

        self.path_data_normalized = self._safe_get_path(spec_dict, "path_data_normalized")
        os.makedirs(self.path_data_normalized, exist_ok=True)

        self.path_data_report = self._safe_get_path(spec_dict, "path_data_report")
        os.makedirs(self.path_data_report, exist_ok=True)

        self.date_start = self._safe_get_datetime(spec_dict, "date_start")

        self.date_end = self._safe_get_datetime(spec_dict, "date_end")

        categorization_path = self._safe_get_path(spec_dict, "categorization")
        self.categorization = Categorization(categorization_path)

        self.analysis_names = self._safe_get_analysis_names(spec_dict, "analyses")

    @property
    def year_range(self) -> tuple[int, int]:
        """
        Return the (start_year, end_year) tuple for the report's date range.
        Returns:
            tuple[int, int]: (start_year, end_year)
        """
        return (self.date_start.year, self.date_end.year)


    @staticmethod
    def _safe_get_path(spec_dict: SpecDict, key: str) -> Path:
        """
        Safely extract a file path from the specification dictionary.
        Args:
            spec_dict (SpecDict): The parsed YAML dictionary.
            key (str): The key to extract.
        Returns:
            Path: The extracted path.
        Raises:
            TypeError: If the value is not a string.
        """
        path_str = spec_dict[key]
        if not isinstance(path_str, str):
            raise TypeError(f"Value of key {key} must be a string")
        return Path(path_str)

    @staticmethod
    def _safe_get_datetime(spec_dict: SpecDict, key: str) -> datetime:
        """
        Safely extract a datetime from the specification dictionary.
        Args:
            spec_dict (SpecDict): The parsed YAML dictionary.
            key (str): The key to extract.
        Returns:
            datetime: The extracted datetime object.
        Raises:
            TypeError: If the value is not a string.
        """
        date_str = spec_dict[key]
        if not isinstance(date_str, str):
            raise TypeError(f"Value of key {key} must be a string")
        return datetime.strptime(date_str, "%m/%d/%Y")

    @staticmethod
    def _safe_get_analysis_names(spec_dict: SpecDict, key: str) -> list[str]:
        """
        Safely extract the list of analysis names from the specification dictionary.
        Args:
            spec_dict (SpecDict): The parsed YAML dictionary.
            key (str): The key to extract.
        Returns:
            list[str]: The list of analysis names.
        Raises:
            TypeError: If the value is not a list.
        """
        analyses_list_str = spec_dict[key]
        if not isinstance(analyses_list_str, list):
            raise TypeError(f"Value of key {key} must be a list")
        # Analyst must check that analysis names are valid.
        return analyses_list_str
