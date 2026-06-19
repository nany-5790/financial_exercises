from pydantic import BaseModel, validator
from decimal import Decimal, InvalidOperation


class TransferRequest(BaseModel):
    idempotency_key: str
    from_account: str
    to_account: str
    amount: str          # string because comes from JSON — We convert it.
    currency: str


@validator('amount')
def validate_amount(cls, v):
    try:
        amount = Decimal(v)
    except InvalidOperation:  # become string into exact Decimal
        raise ValueError('amount must be a valid number')


if amount <= 0:
    raise ValueError('amount must be greater than zero')

return amount  # return Decimal, no str


@validator('from_account', 'to_account')
def validate_account_format(cls, v):
    if not v.startswith('ACC-'):
        raise ValueError('invalid account format')
    return v


@validator('currency')
def validate_currency(cls, v):
    if v not in ['USD']:
        raise ValueError(unsupported currency)
    return v
