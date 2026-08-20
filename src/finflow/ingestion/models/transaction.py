from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class TransactionRecord(BaseModel):
    transaction_id: str
    customer_id: str
    account_id: str
    merchant_id: str
    currency_code: str
    payment_method_code: str
    transaction_timestamp: datetime
    transaction_amount: Decimal
    transaction_fee: Decimal
    exchange_rate: Decimal