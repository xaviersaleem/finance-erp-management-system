from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from .database import Base, engine, get_db, SessionLocal
from .models import *
from .schemas import SalesInvoiceCreate, PurchaseInvoiceCreate
from .seed import seed

app=FastAPI(title="Northstar Finance ERP",version="0.1.0")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
Base.metadata.create_all(engine)
with SessionLocal() as db: seed(db)

def next_id(db, model, prefix):
    return f"{prefix}{db.query(model).count()+1:05d}"

def add_line(db, entry, dt, source, doc, account, debit=0, credit=0, desc=""):
    db.add(JournalLine(entry_id=entry,posting_date=dt,source=source,document_id=doc,account_id=account,debit=debit,credit=credit,description=desc))

@app.get("/health")
def health(): return {"status":"ok"}

@app.get("/masters")
def masters(db:Session=Depends(get_db)):
    return {"customers":db.query(Customer).all(),"vendors":db.query(Vendor).all(),"products":db.query(Product).all(),"accounts":db.query(Account).all()}

@app.post("/sales-invoices")
def create_sales_invoice(x:SalesInvoiceCreate, db:Session=Depends(get_db)):
    p=db.get(Product,x.product_id); c=db.get(Customer,x.customer_id)
    if not p or not c: raise HTTPException(400,"Invalid customer or product")
    iid=next_id(db,SalesInvoice,"SI-")
    inv=SalesInvoice(id=iid,status="Approved",**x.model_dump()); db.add(inv)
    net=x.qty*x.unit_price; tax=net*x.tax_rate; cost=x.qty*p.standard_cost
    add_line(db,iid,x.invoice_date,"Sales",iid,"1100",debit=net+tax,desc="Customer receivable")
    add_line(db,iid,x.invoice_date,"Sales",iid,"4000",credit=net,desc="Sales revenue")
    add_line(db,iid,x.invoice_date,"Sales",iid,"2100",credit=tax,desc="Output tax")
    add_line(db,iid,x.invoice_date,"Sales",iid,"5000",debit=cost,desc="Cost of goods sold")
    add_line(db,iid,x.invoice_date,"Sales",iid,"1200",credit=cost,desc="Inventory issue")
    db.commit(); return {"invoice_id":iid,"total":round(net+tax,2),"posted":True}

@app.post("/purchase-invoices")
def create_purchase_invoice(x:PurchaseInvoiceCreate, db:Session=Depends(get_db)):
    if not db.get(Vendor,x.vendor_id) or not db.get(Account,x.account_id): raise HTTPException(400,"Invalid vendor or account")
    bid=next_id(db,PurchaseInvoice,"PI-")
    bill=PurchaseInvoice(id=bid,status="Approved",**x.model_dump()); db.add(bill)
    tax=x.amount*x.tax_rate
    add_line(db,bid,x.bill_date,"Purchase",bid,x.account_id,debit=x.amount,desc="Purchase/expense")
    add_line(db,bid,x.bill_date,"Purchase",bid,"2100",debit=tax,desc="Input tax")
    add_line(db,bid,x.bill_date,"Purchase",bid,"2000",credit=x.amount+tax,desc="Accounts payable")
    db.commit(); return {"bill_id":bid,"total":round(x.amount+tax,2),"posted":True}

@app.get("/journal")
def journal(limit:int=100, db:Session=Depends(get_db)):
    return db.query(JournalLine).order_by(JournalLine.id.desc()).limit(limit).all()

@app.get("/dashboard")
def dashboard(db:Session=Depends(get_db)):
    rows=db.query(JournalLine.account_id,func.sum(JournalLine.debit).label("dr"),func.sum(JournalLine.credit).label("cr")).group_by(JournalLine.account_id).all()
    bal={a:(dr or 0)-(cr or 0) for a,dr,cr in rows}
    revenue=-bal.get("4000",0); cogs=bal.get("5000",0)
    opex=sum(bal.get(a,0) for a in ["6100","6200","6300","6400","6500","6600"])
    debits=db.query(func.sum(JournalLine.debit)).scalar() or 0; credits=db.query(func.sum(JournalLine.credit)).scalar() or 0
    return {"revenue":round(revenue,2),"gross_profit":round(revenue-cogs,2),"operating_profit":round(revenue-cogs-opex,2),"cash":round(bal.get("1000",0),2),"accounts_receivable":round(bal.get("1100",0),2),"inventory":round(bal.get("1200",0),2),"accounts_payable":round(-bal.get("2000",0),2),"gl_difference":round(debits-credits,2)}
