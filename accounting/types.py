from pathlib import Path
from typing import TypeAlias, Callable, Optional

import pandas as pd

from accounting.spec import Specification
from accounting.transaction_file import TransactionFile

NormalizeFunc: TypeAlias = Callable[[Path], TransactionFile]

AnalysisFunc: TypeAlias = Callable[[Path, pd.DataFrame, Specification], Optional[str]]
