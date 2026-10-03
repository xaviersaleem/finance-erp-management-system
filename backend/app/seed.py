from .models import Account, Customer, Vendor, Product, JournalLine
from datetime import date

def seed(db):
    if db.query(Account).count():
        return
    accounts=[
        ("1000","Cash","Asset","Current Asset"),("1100","Accounts Receivable","Asset","Current Asset"),
        ("1200","Inventory","Asset","Current Asset"),("2000","Accounts Payable","Liability","Current Liability"),
        ("2100","Tax Payable","Liability","Current Liability"),("3000","Owner Equity","Equity","Equity"),
        ("4000","Sales Revenue","Revenue","Revenue"),("5000","COGS","Expense","COGS"),
        ("6100","Payroll Expense","Expense","Operating Expense"),("6200","Marketing Expense","Expense","Operating Expense"),
        ("6300","Rent & Facilities","Expense","Operating Expense"),("6400","IT & Systems","Expense","Operating Expense"),
        ("6500","Logistics Expense","Expense","Operating Expense"),("6600","G&A Expense","Expense","Operating Expense")]
    db.add_all([Account(id=a,name=b,account_type=c,fs_group=d) for a,b,c,d in accounts])
    db.add_all([Customer(id="C001",name="Orion Retail",segment="Retail",payment_terms_days=30,credit_limit=50000),Customer(id="C002",name="Atlas Stores",segment="Retail",payment_terms_days=30,credit_limit=65000),Customer(id="C003",name="Nova Wholesale",segment="Wholesale",payment_terms_days=45,credit_limit=90000)])
    db.add_all([Vendor(id="V001",name="Prime Supply Co",category="Inventory",payment_terms_days=30),Vendor(id="V002",name="FastRoute Logistics",category="Logistics",payment_terms_days=30),Vendor(id="V003",name="CloudCore Systems",category="IT",payment_terms_days=15)])
    db.add_all([Product(id="P001",name="Core Product",product_line="Core",sales_price=35,standard_cost=21),Product(id="P002",name="Premium Product",product_line="Premium",sales_price=55,standard_cost=31),Product(id="P003",name="Value Product",product_line="Value",sales_price=24,standard_cost=16)])
    db.add_all([
        JournalLine(entry_id="OPEN-1",posting_date=date(2026,1,1),source="Opening",document_id="OPEN",account_id="1000",debit=250000,credit=0,description="Opening cash"),
        JournalLine(entry_id="OPEN-1",posting_date=date(2026,1,1),source="Opening",document_id="OPEN",account_id="3000",debit=0,credit=250000,description="Opening equity"),
        JournalLine(entry_id="OPEN-2",posting_date=date(2026,1,1),source="Opening",document_id="OPEN",account_id="1200",debit=100000,credit=0,description="Opening inventory"),
        JournalLine(entry_id="OPEN-2",posting_date=date(2026,1,1),source="Opening",document_id="OPEN",account_id="3000",debit=0,credit=100000,description="Opening equity"),
    ])
    db.commit()
