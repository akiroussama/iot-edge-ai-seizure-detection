from __future__ import annotations

import pandas as pd


def leave_center_out_split(df: pd.DataFrame, test_center: str) -> pd.DataFrame:
    """Assign test split to one center and train split to the remaining centers."""
    if "center_id" not in df.columns:
        raise ValueError("df must contain center_id for center-wise evaluation")
    out = df.copy()
    out["split"] = "train"
    out.loc[out["center_id"].eq(test_center), "split"] = "test"
    return out
