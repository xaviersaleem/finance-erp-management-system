# Northstar Finance ERP

A portfolio-grade Finance ERP prototype that evolves the accompanying Excel ERP model into a database-backed web application. The project demonstrates accounting process design, double-entry posting, relational data modeling, API development, financial reporting and management controls.

> Northstar Integrated Trading LLC is fictional and all data is synthetic.

## Architecture

**React/Vite UI → FastAPI REST API → PostgreSQL → Double-entry journal → Financial KPIs & reporting**

SQLite is the zero-configuration local fallback; Docker Compose runs PostgreSQL.

## Current MVP

- Chart of accounts, customer, vendor and product masters
- Sales invoice entry API with automatic AR, revenue, tax, COGS and inventory journal posting
- Purchase invoice entry API with automatic AP and tax posting
- Double-entry general ledger
- Management dashboard API
- Responsive finance dashboard UI
- PostgreSQL-ready schema and Docker environment
- Health endpoint and API documentation through FastAPI `/docs`

## Run locally

### Fastest backend demo
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open API docs at `http://localhost:8000/docs`.

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

### Full PostgreSQL stack
```bash
docker compose up --build
```

## Accounting design

Operational documents do not directly become financial statements. Approved transactions generate balanced journal lines. Reporting reads from the journal, preserving an auditable accounting trail.

Example sales posting:
- Dr Accounts Receivable
- Cr Sales Revenue
- Cr Tax Payable
- Dr Cost of Goods Sold
- Cr Inventory

## Roadmap

Next iterations add receipts/payments, AR/AP aging, purchase orders, inventory movements, fixed assets/depreciation, department budgets, approval workflow, period locks, bank reconciliation, month-end close, authentication/RBAC, audit logs, Excel import/export and richer financial statements.

## Excel finance prototype

`Project_2_Advanced_ERP_Finance.xlsx` is included alongside the application. It serves as the finance prototype, synthetic operating dataset, accounting validation model and reference design for the coded ERP. The long-term application architecture is database-backed rather than AppSheet-dependent.

## Portfolio disclosure

This is a fictional portfolio simulation created to demonstrate finance, accounting systems, ERP architecture and software-development skills. It contains no employer or confidential data.
