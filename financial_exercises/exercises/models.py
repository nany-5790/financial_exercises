from django.db import models
from decimal import Decimal
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Account:
    id: str
    balance: Decimal


@dataclass
class Transfer:
    id: str
    idempotency_key: str
    from_account: str
    to_account: str
    amount: Decimal
    currency: str
    status: str
    processed_at: datetime


@dataclass
class Auditlog:
    action: str
    transfer_id: str
    from_account: str
    to_account: str
    amount: Decimal
    timestamp: datetime


# Database in memory
ACCOUNTS: dict[str, Account] = {
    "ACC-01": Account(id="ACC-01", balance=Decimal("1000.00")),
    "ACC-02": Account(id="ACC-02", balance=Decimal("500.00")),
}

TRANSFER: dict[str, Transfer] = {}  # key: idempotency_key
AUDIT_LOG: list[Auditlog] = []
