from pathlib import Path

import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models import InventoryItem


def seed_inventory(db: Session, excel_path: Path) -> int:
    existing_count = db.scalar(select(func.count()).select_from(InventoryItem))
    if existing_count:
        return 0

    dataframe = pd.read_excel(excel_path)
    required_columns = {"품목코드", "품목명", "창고", "재고수량", "안전재고"}
    missing_columns = required_columns.difference(dataframe.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"inventory.xlsx 필수 열 누락: {missing}")

    items = [
        InventoryItem(
            item_code=str(row["품목코드"]).strip(),
            item_name=str(row["품목명"]).strip(),
            warehouse=str(row["창고"]).strip(),
            quantity=int(row["재고수량"]),
            safety_stock=int(row["안전재고"]),
        )
        for _, row in dataframe.iterrows()
    ]
    db.add_all(items)
    db.commit()
    return len(items)
