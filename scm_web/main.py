from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import pandas as pd
import os


app = FastAPI(title="SCM Management System")


# -----------------------------
# 폴더 설정
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")


templates = Jinja2Templates(directory=TEMPLATE_DIR)

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)


# -----------------------------
# 데이터 읽기 함수
# -----------------------------

# -----------------------------
# 서버 시작 시 데이터 로딩
# -----------------------------

inventory_df = pd.read_excel(
    os.path.join(DATA_DIR, "inventory.xlsx")
)

inbound_df = pd.read_csv(
    os.path.join(DATA_DIR, "inbound.csv"),
    encoding="utf-8-sig"
)

purchase_df = pd.read_excel(
    os.path.join(DATA_DIR, "purchase.xlsx")
)


# -----------------------------
# 메인 대시보드
# -----------------------------

@app.get("/")
def dashboard(request: Request):

    total_inventory = inventory_df["재고수량"].sum()

    low_stock = len(
        inventory_df[
            inventory_df["재고수량"]
            <= inventory_df["안전재고"]
        ]
    )

    inbound_count = len(inbound_df)

    purchase_amount = purchase_df["구매금액"].sum()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "total_inventory": total_inventory,
            "low_stock": low_stock,
            "inbound_count": inbound_count,
            "purchase_amount": purchase_amount,
        }
    )

# -----------------------------
# 재고관리
# -----------------------------

@app.get("/inventory")
def inventory_page(request: Request):

    data = inventory_df.to_dict(
        orient="records"
    )

    return templates.TemplateResponse(
        request=request,
        name="inventory.html",
        context={
            "inventory": data
        }
    )



# -----------------------------
# 입출고관리
# -----------------------------

@app.get("/inbound")
def inbound_page(request: Request):

    data = inbound_df.to_dict(
        orient="records"
    )

    return templates.TemplateResponse(
        request=request,
        name="inbound.html",
        context={
            "inbound": data
        }
    )

# -----------------------------
# 구매관리
# -----------------------------

@app.get("/purchase")
def purchase_page(request: Request):

    data = purchase_df.to_dict(
        orient="records"
    )

    return templates.TemplateResponse(
        request=request,
        name="purchase.html",
        context={
            "purchase": data
        }
    )


# -----------------------------
# 서버 테스트
# -----------------------------

@app.get("/api/status")
def status():

    return {
        "status": "running",
        "system": "SCM Management System"
    }
