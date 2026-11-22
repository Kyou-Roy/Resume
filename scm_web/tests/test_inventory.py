import pandas as pd
import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from models import InventoryAdjustment, InventoryItem
from seed import seed_inventory
from services import InsufficientStockError, InventoryNotFoundError, adjust_inventory


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    session.add(
        InventoryItem(
            item_code="MAT001",
            item_name="알루미늄 프레임",
            warehouse="A",
            quantity=10,
            safety_stock=5,
        )
    )
    session.commit()
    try:
        yield session
    finally:
        session.close()


def test_inbound_adjustment_is_persisted(db):
    item = adjust_inventory(db, "MAT001", "입고", 5, "입고 테스트")
    assert item.quantity == 15
    assert db.scalar(select(func.count()).select_from(InventoryAdjustment)) == 1


def test_outbound_cannot_make_stock_negative(db):
    with pytest.raises(InsufficientStockError):
        adjust_inventory(db, "MAT001", "출고", 11, "출고 테스트")
    assert db.scalar(select(InventoryItem.quantity)) == 10


def test_unknown_item_is_rejected(db):
    with pytest.raises(InventoryNotFoundError):
        adjust_inventory(db, "UNKNOWN", "입고", 1, "오류 테스트")


def test_excel_seed_runs_only_once(tmp_path):
    engine = create_engine("sqlite://", poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    excel_path = tmp_path / "inventory.xlsx"
    pd.DataFrame(
        [
            {
                "품목코드": "MAT100",
                "품목명": "센서",
                "창고": "B",
                "재고수량": 20,
                "안전재고": 4,
            }
        ]
    ).to_excel(excel_path, index=False)

    assert seed_inventory(session, excel_path) == 1
    assert seed_inventory(session, excel_path) == 0
    assert session.scalar(select(func.count()).select_from(InventoryItem)) == 1
    session.close()
