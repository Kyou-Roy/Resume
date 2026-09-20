from sqlalchemy import select
from sqlalchemy.orm import Session

from models import InventoryAdjustment, InventoryItem


class InventoryNotFoundError(Exception):
    pass


class InsufficientStockError(Exception):
    pass


def adjust_inventory(
    db: Session,
    item_code: str,
    movement_type: str,
    quantity: int,
    reason: str,
) -> InventoryItem:
    item = db.scalar(
        select(InventoryItem).where(InventoryItem.item_code == item_code)
    )
    if item is None:
        raise InventoryNotFoundError(item_code)

    delta = quantity if movement_type == "입고" else -quantity
    new_quantity = item.quantity + delta
    if new_quantity < 0:
        raise InsufficientStockError(item_code)

    try:
        item.quantity = new_quantity
        db.add(
            InventoryAdjustment(
                item=item,
                movement_type=movement_type,
                quantity=quantity,
                reason=reason,
            )
        )
        db.commit()
        db.refresh(item)
    except Exception:
        db.rollback()
        raise

    return item
