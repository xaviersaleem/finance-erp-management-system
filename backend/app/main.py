from datetime import timedelta, date
from fastapi import FastAPI,Depends,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from .database import Base,engine,get_db,SessionLocal
from .models import *
from .schemas import *
from .seed import seed
app=FastAPI(title="Northstar Finance ERP",version="0.2.0")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
Base.metadata.create_all(engine)
with SessionLocal() as db: seed(db)
def next_id(db,model,prefix): return f"{prefix}{db.query(model).count()+1:05d}"
def line(db,e,dt,src,doc,acct,dr=0,cr=0,desc=""): db.add(JournalLine(entry_id=e,posting_date=dt,source=src,document_id=doc,account_id=acct,debit=dr,credit=cr,description=desc))
def balances(db):
    rows=db.query(JournalLine.account_id,func.sum(JournalLine.debit),func.sum(JournalLine.credit)).group_by(JournalLine.account_id).all()
    return {a:(dr or 0)-(cr or 0) for a,dr,cr in rows}
@app.get("/health")
def health(): return {"status":"ok","version":"0.2.0"}
@app.get("/masters")
def masters(db:Session=Depends(get_db)): return {"customers":db.query(Customer).all(),"vendors":db.query(Vendor).all(),"products":db.query(Product).all(),"accounts":db.query(Account).all()}
@app.post("/sales-invoices")
def sales(x:SalesInvoiceCreate,db:Session=Depends(get_db)):
    p=db.get(Product,x.product_id); c=db.get(Customer,x.customer_id)
    if not p or not c: raise HTTPException(400,"Invalid customer or product")
    iid=next_id(db,SalesInvoice,"SI-"); net=x.qty*x.unit_price; tax=net*x.tax_rate; total=net+tax; due=x.invoice_date+timedelta(days=c.payment_terms_days)
    db.add(SalesInvoice(id=iid,due_date=due,total=total,paid_amount=0,status="Posted",**x.model_dump()))
    line(db,iid,x.invoice_date,"Sales",iid,"1100",dr=total,desc="Customer receivable"); line(db,iid,x.invoice_date,"Sales",iid,"4000",cr=net,desc="Revenue"); line(db,iid,x.invoice_date,"Sales",iid,"2100",cr=tax,desc="Output tax")
    cost=x.qty*p.standard_cost; line(db,iid,x.invoice_date,"Sales",iid,"5000",dr=cost,desc="COGS"); line(db,iid,x.invoice_date,"Sales",iid,"1200",cr=cost,desc="Inventory issue")
    db.add(InventoryMovement(movement_date=x.invoice_date,product_id=x.product_id,source="Sales",document_id=iid,qty_out=x.qty,unit_cost=p.standard_cost)); db.commit()
    return {"invoice_id":iid,"due_date":due,"total":round(total,2),"posted":True}
@app.post("/purchase-invoices")
def purchases(x:PurchaseInvoiceCreate,db:Session=Depends(get_db)):
    v=db.get(Vendor,x.vendor_id)
    if not v or not db.get(Account,x.account_id): raise HTTPException(400,"Invalid vendor or account")
    bid=next_id(db,PurchaseInvoice,"PI-"); tax=x.amount*x.tax_rate; total=x.amount+tax; due=x.bill_date+timedelta(days=v.payment_terms_days)
    db.add(PurchaseInvoice(id=bid,due_date=due,total=total,paid_amount=0,status="Posted",**x.model_dump()))
    line(db,bid,x.bill_date,"Purchase",bid,x.account_id,dr=x.amount,desc="Purchase/expense"); line(db,bid,x.bill_date,"Purchase",bid,"2100",dr=tax,desc="Input tax"); line(db,bid,x.bill_date,"Purchase",bid,"2000",cr=total,desc="Accounts payable"); db.commit()
    return {"bill_id":bid,"due_date":due,"total":round(total,2),"posted":True}
@app.post("/customer-receipts")
def receipt(x:CustomerReceiptCreate,db:Session=Depends(get_db)):
    inv=db.get(SalesInvoice,x.invoice_id)
    if not inv or inv.customer_id!=x.customer_id: raise HTTPException(400,"Invalid invoice/customer")
    outstanding=inv.total-inv.paid_amount
    if x.amount>outstanding+.01: raise HTTPException(400,"Receipt exceeds outstanding invoice")
    rid=next_id(db,CustomerReceipt,"RC-"); db.add(CustomerReceipt(id=rid,**x.model_dump())); inv.paid_amount+=x.amount; inv.status="Paid" if abs(inv.total-inv.paid_amount)<.01 else "Part Paid"
    line(db,rid,x.receipt_date,"Receipt",rid,"1000",dr=x.amount,desc="Cash receipt"); line(db,rid,x.receipt_date,"Receipt",rid,"1100",cr=x.amount,desc=f"Clear {x.invoice_id}"); db.commit(); return {"receipt_id":rid,"invoice_status":inv.status}
@app.post("/vendor-payments")
def payment(x:VendorPaymentCreate,db:Session=Depends(get_db)):
    bill=db.get(PurchaseInvoice,x.bill_id)
    if not bill or bill.vendor_id!=x.vendor_id: raise HTTPException(400,"Invalid bill/vendor")
    outstanding=bill.total-bill.paid_amount
    if x.amount>outstanding+.01: raise HTTPException(400,"Payment exceeds outstanding bill")
    pid=next_id(db,VendorPayment,"PAY-"); db.add(VendorPayment(id=pid,**x.model_dump())); bill.paid_amount+=x.amount; bill.status="Paid" if abs(bill.total-bill.paid_amount)<.01 else "Part Paid"
    line(db,pid,x.payment_date,"Payment",pid,"2000",dr=x.amount,desc=f"Clear {x.bill_id}"); line(db,pid,x.payment_date,"Payment",pid,"1000",cr=x.amount,desc="Bank payment"); db.commit(); return {"payment_id":pid,"bill_status":bill.status}
@app.get("/ar-aging")
def ar_aging(as_of:date|None=None,db:Session=Depends(get_db)):
    as_of=as_of or date.today(); out=[]
    for i in db.query(SalesInvoice).all():
        o=i.total-i.paid_amount
        if o>.01: out.append({"invoice_id":i.id,"customer_id":i.customer_id,"due_date":i.due_date,"outstanding":round(o,2),"days_past_due":max(0,(as_of-i.due_date).days)})
    return out
@app.get("/ap-aging")
def ap_aging(as_of:date|None=None,db:Session=Depends(get_db)):
    as_of=as_of or date.today(); out=[]
    for i in db.query(PurchaseInvoice).all():
        o=i.total-i.paid_amount
        if o>.01: out.append({"bill_id":i.id,"vendor_id":i.vendor_id,"due_date":i.due_date,"outstanding":round(o,2),"days_past_due":max(0,(as_of-i.due_date).days)})
    return out
@app.get("/trial-balance")
def trial_balance(db:Session=Depends(get_db)):
    rows=db.query(Account).all(); b=balances(db)
    return [{"account_id":a.id,"account_name":a.name,"type":a.account_type,"balance":round(b.get(a.id,0),2)} for a in rows]
@app.get("/financial-statements")
def statements(db:Session=Depends(get_db)):
    b=balances(db); revenue=-b.get("4000",0); cogs=b.get("5000",0); opex=sum(b.get(a,0) for a in ["6100","6200","6300","6400","6500","6600"])
    assets=sum(b.get(a,0) for a in ["1000","1100","1200"]); liabilities=-sum(b.get(a,0) for a in ["2000","2100"]); equity=-b.get("3000",0); profit=revenue-cogs-opex
    return {"p_and_l":{"revenue":round(revenue,2),"cogs":round(cogs,2),"gross_profit":round(revenue-cogs,2),"opex":round(opex,2),"operating_profit":round(profit,2)},"balance_sheet":{"assets":round(assets,2),"liabilities":round(liabilities,2),"equity_and_current_profit":round(equity+profit,2),"difference":round(assets-liabilities-equity-profit,2)}}
@app.get("/journal")
def journal(limit:int=100,db:Session=Depends(get_db)): return db.query(JournalLine).order_by(JournalLine.id.desc()).limit(limit).all()
@app.get("/inventory")
def inventory(db:Session=Depends(get_db)):
    result=[]
    for p in db.query(Product).all():
        qin=db.query(func.sum(InventoryMovement.qty_in)).filter(InventoryMovement.product_id==p.id).scalar() or 0; qout=db.query(func.sum(InventoryMovement.qty_out)).filter(InventoryMovement.product_id==p.id).scalar() or 0
        result.append({"product_id":p.id,"product_name":p.name,"qty_in":qin,"qty_out":qout,"net_movement":qin-qout,"standard_cost":p.standard_cost})
    return result
@app.get("/dashboard")
def dashboard(db:Session=Depends(get_db)):
    b=balances(db); revenue=-b.get("4000",0); cogs=b.get("5000",0); opex=sum(b.get(a,0) for a in ["6100","6200","6300","6400","6500","6600"]); dr=db.query(func.sum(JournalLine.debit)).scalar() or 0; cr=db.query(func.sum(JournalLine.credit)).scalar() or 0
    return {"revenue":round(revenue,2),"gross_profit":round(revenue-cogs,2),"operating_profit":round(revenue-cogs-opex,2),"cash":round(b.get("1000",0),2),"accounts_receivable":round(b.get("1100",0),2),"inventory":round(b.get("1200",0),2),"accounts_payable":round(-b.get("2000",0),2),"gl_difference":round(dr-cr,2)}
