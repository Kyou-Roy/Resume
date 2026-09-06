from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Literal

import pandas as pd
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine, get_db
from models import InventoryItem
from seed import seed_inventory
from services import (
    InsufficientStockError,
    InventoryNotFoundError,
    adjust_inventory,
)


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_inventory(db, DATA_DIR / "inventory.xlsx")
    yield


app = FastAPI(title="SCM Management System", lifespan=lifespan)
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Existing file flows remain in place for this iteration.
inbound_df = pd.read_csv(DATA_DIR / "inbound.csv", encoding="utf-8-sig")
purchase_df = pd.read_excel(DATA_DIR / "purchase.xlsx")


def inventory_records(db: Session) -> list[dict]:
    items = db.scalars(select(InventoryItem).order_by(InventoryItem.item_code)).all()
    return [
        {
            "품목코드": item.item_code,
            "품목명": item.item_name,
            "창고": item.warehouse,
            "재고수량": item.quantity,
            "안전재고": item.safety_stock,
        }
        for item in items
    ]


@app.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
    total_inventory = db.scalar(
        select(func.coalesce(func.sum(InventoryItem.quantity), 0))
    )
    low_stock = db.scalar(
        select(func.count())
        .select_from(InventoryItem)
        .where(InventoryItem.quantity <= InventoryItem.safety_stock)
    )
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "total_inventory": total_inventory,
            "low_stock": low_stock,
            "inbound_count": len(inbound_df),
            "purchase_amount": purchase_df["구매금액"].sum(),
        },
    )


@app.get("/inventory")
def inventory_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        request=request,
        name="inventory.html",
        context={
            "inventory": inventory_records(db),
            "updated": request.query_params.get("updated") == "1",
            "error": None,
        },
    )


@app.post("/inventory/{item_code}/adjust")
def inventory_adjust(
    request: Request,
    item_code: str,
    movement_type: Annotated[Literal["입고", "출고"], Form()],
    quantity: Annotated[int, Form(gt=0)],
    reason: Annotated[str, Form(min_length=2, max_length=100)],
    db: Session = Depends(get_db),
):
    try:
        adjust_inventory(db, item_code, movement_type, quantity, reason.strip())
    except InventoryNotFoundError as exc:
        raise HTTPException(status_code=404, detail="품목을 찾을 수 없습니다.") from exc
    except InsufficientStockError:
        return templates.TemplateResponse(
            request=request,
            name="inventory.html",
            context={
                "inventory": inventory_records(db),
                "updated": False,
                "error": "출고 후 재고가 음수가 될 수 없습니다.",
            },
            status_code=400,
        )

    return RedirectResponse(url="/inventory?updated=1", status_code=303)


@app.get("/inbound")
def inbound_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="inbound.html",
        context={"inbound": inbound_df.to_dict(orient="records")},
    )


@app.get("/purchase")
def purchase_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="purchase.html",
        context={"purchase": purchase_df.to_dict(orient="records")},
    )


@app.get("/api/status")
def status():
    return {"status": "running", "system": "SCM Management System"}
