from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class DatasetTables:
    """Canonical tables returned by all dataset loaders."""

    metadata: pd.DataFrame
    events: pd.DataFrame
    windows: pd.DataFrame
    modality_availability: pd.DataFrame


class BaseDataset(ABC):
    """Dataset abstraction for wearable seizure forecasting.

    Loaders should return event tables with seizure onset/end times and window tables with
    leakage-safe identifiers. Actual signal loading can be added later without changing labels
    or metrics.
    """

    def __init__(self, raw_root: str | Path, processed_root: str | Path | None = None) -> None:
        self.raw_root = Path(raw_root)
        self.processed_root = Path(processed_root) if processed_root else self.raw_root / "processed"

    @abstractmethod
    def load_metadata(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def load_events(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def load_windows(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def load_modality_availability(self) -> pd.DataFrame:
        pass

    def load_tables(self) -> DatasetTables:
        return DatasetTables(
            metadata=self.load_metadata(),
            events=self.load_events(),
            windows=self.load_windows(),
            modality_availability=self.load_modality_availability(),
        )
