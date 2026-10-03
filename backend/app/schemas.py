from datetime import date
from pydantic import BaseModel, Field
class SalesInvoiceCreate(BaseModel):
    invoice_date:date; customer_id:str; product_id:str; qty:float=Field(gt=0); unit_price:float=Field(gt=0); tax_rate:float=Field(default=.05,ge=0)
class PurchaseInvoiceCreate(BaseModel):
    bill_date:date; vendor_id:str; account_id:str; amount:float=Field(gt=0); tax_rate:float=Field(default=.05,ge=0)
class CustomerReceiptCreate(BaseModel):
    receipt_date:date; customer_id:str; invoice_id:str; amount:float=Field(gt=0); method:str="Bank Transfer"
class VendorPaymentCreate(BaseModel):
    payment_date:date; vendor_id:str; bill_id:str; amount:float=Field(gt=0); method:str="Bank Transfer"
