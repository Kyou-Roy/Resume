# SCM Management System

FastAPI, Jinja2, pandas, and SQLite를 사용한 SCM 포트폴리오 프로젝트입니다.

## 이번 버전의 데이터 흐름

- `inventory.xlsx`: SQLite가 비어 있을 때 재고 마스터를 최초 1회 적재합니다.
- `scm.db`: 재고수량과 입고/출고 조정 이력을 영속적으로 저장합니다.
- `inbound.csv`: 기존 입출고 조회 데이터를 유지합니다.
- `purchase.xlsx`: 기존 구매 조회 데이터를 유지합니다.

## 실행

```bash
cd scm_web
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

브라우저에서 `http://127.0.0.1:8000`을 엽니다.

## 테스트

```bash
cd scm_web
pytest -q
```

테스트는 엑셀 최초 적재, 입고 저장, 음수 재고 방지, 미등록 품목 거부를 확인합니다.

## 주요 업무 규칙

- 조정수량은 1 이상의 정수여야 합니다.
- 출고 후 재고수량은 0보다 작아질 수 없습니다.
- 존재하지 않는 품목은 조정할 수 없습니다.
- 재고조정이 성공하면 조정 이력이 같은 트랜잭션으로 기록됩니다.
