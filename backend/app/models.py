from datetime import date
from sqlalchemy import String, Float, Date, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class Account(Base):
    __tablename__="accounts"
    id:Mapped[str]=mapped_column(String,primary_key=True); name:Mapped[str]=mapped_column(String); account_type:Mapped[str]=mapped_column(String); fs_group:Mapped[str]=mapped_column(String); active:Mapped[bool]=mapped_column(Boolean,default=True)
class Customer(Base):
    __tablename__="customers"
    id:Mapped[str]=mapped_column(String,primary_key=True); name:Mapped[str]=mapped_column(String); segment:Mapped[str]=mapped_column(String); payment_terms_days:Mapped[int]=mapped_column(default=30); credit_limit:Mapped[float]=mapped_column(Float,default=0)
class Vendor(Base):
    __tablename__="vendors"
    id:Mapped[str]=mapped_column(String,primary_key=True); name:Mapped[str]=mapped_column(String); category:Mapped[str]=mapped_column(String); payment_terms_days:Mapped[int]=mapped_column(default=30)
class Product(Base):
    __tablename__="products"
    id:Mapped[str]=mapped_column(String,primary_key=True); name:Mapped[str]=mapped_column(String); product_line:Mapped[str]=mapped_column(String); sales_price:Mapped[float]=mapped_column(Float); standard_cost:Mapped[float]=mapped_column(Float)
class SalesInvoice(Base):
    __tablename__="sales_invoices"
    id:Mapped[str]=mapped_column(String,primary_key=True); invoice_date:Mapped[date]=mapped_column(Date); due_date:Mapped[date]=mapped_column(Date); customer_id:Mapped[str]=mapped_column(ForeignKey("customers.id")); product_id:Mapped[str]=mapped_column(ForeignKey("products.id")); qty:Mapped[float]=mapped_column(Float); unit_price:Mapped[float]=mapped_column(Float); tax_rate:Mapped[float]=mapped_column(Float,default=.05); total:Mapped[float]=mapped_column(Float); paid_amount:Mapped[float]=mapped_column(Float,default=0); status:Mapped[str]=mapped_column(String,default="Posted")
class PurchaseInvoice(Base):
    __tablename__="purchase_invoices"
    id:Mapped[str]=mapped_column(String,primary_key=True); bill_date:Mapped[date]=mapped_column(Date); due_date:Mapped[date]=mapped_column(Date); vendor_id:Mapped[str]=mapped_column(ForeignKey("vendors.id")); account_id:Mapped[str]=mapped_column(ForeignKey("accounts.id")); amount:Mapped[float]=mapped_column(Float); tax_rate:Mapped[float]=mapped_column(Float,default=.05); total:Mapped[float]=mapped_column(Float); paid_amount:Mapped[float]=mapped_column(Float,default=0); status:Mapped[str]=mapped_column(String,default="Posted")
class CustomerReceipt(Base):
    __tablename__="customer_receipts"
    id:Mapped[str]=mapped_column(String,primary_key=True); receipt_date:Mapped[date]=mapped_column(Date); customer_id:Mapped[str]=mapped_column(ForeignKey("customers.id")); invoice_id:Mapped[str]=mapped_column(ForeignKey("sales_invoices.id")); amount:Mapped[float]=mapped_column(Float); method:Mapped[str]=mapped_column(String,default="Bank Transfer")
class VendorPayment(Base):
    __tablename__="vendor_payments"
    id:Mapped[str]=mapped_column(String,primary_key=True); payment_date:Mapped[date]=mapped_column(Date); vendor_id:Mapped[str]=mapped_column(ForeignKey("vendors.id")); bill_id:Mapped[str]=mapped_column(ForeignKey("purchase_invoices.id")); amount:Mapped[float]=mapped_column(Float); method:Mapped[str]=mapped_column(String,default="Bank Transfer")
class InventoryMovement(Base):
    __tablename__="inventory_movements"
    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True); movement_date:Mapped[date]=mapped_column(Date); product_id:Mapped[str]=mapped_column(ForeignKey("products.id")); source:Mapped[str]=mapped_column(String); document_id:Mapped[str]=mapped_column(String); qty_in:Mapped[float]=mapped_column(Float,default=0); qty_out:Mapped[float]=mapped_column(Float,default=0); unit_cost:Mapped[float]=mapped_column(Float,default=0)
class JournalLine(Base):
    __tablename__="journal_lines"
    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True); entry_id:Mapped[str]=mapped_column(String,index=True); posting_date:Mapped[date]=mapped_column(Date); source:Mapped[str]=mapped_column(String); document_id:Mapped[str]=mapped_column(String); account_id:Mapped[str]=mapped_column(ForeignKey("accounts.id")); debit:Mapped[float]=mapped_column(Float,default=0); credit:Mapped[float]=mapped_column(Float,default=0); description:Mapped[str]=mapped_column(String,default="")
