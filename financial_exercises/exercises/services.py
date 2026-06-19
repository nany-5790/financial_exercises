import uuid
from decimal import Decimal
from datetime import datetime, timezone
from models import ACCOUNTS, TRANSFER, AUDIT_LOG, Transfer, Auditlog


class InsufficientFundsError(Exception):
    pass


class AccountNotFoundError(Exception):
    pass


def process_transfer(
        idempotency_key: str
        from_account_id: str
        to_account_id: str
        amount: Decimal          # string porque viene de JSON — lo convertimos nosotras
        currency: str
) -> Transfer:

    # --- PASO 1: Idempotencia ---
    # Si ya procesamos esta operación, retornamos el resultado original
    # sin tocar la DB de nuevo. El cliente puede reintentar sin miedo.
    # if operation had been processed, return to original result
    # without touch the DB. Client can reintent without fear.

    if idempotency_key in TRANSFERS:
        return TRANSFERS[idempotency_key]

    # --- PASO 2: Validate existing accounts ---
    if from_account_id not in ACCOUNTS:
        raise AccountNotFoundError(f"Account {from_account_id} not found")
    if to_account_id not in ACCOUNTS:
        raise AccountNotFoundError(f"Account {to_account_id} not found")

    from_acc = ACCOUNTS[from_account_id]
    to_acc = ACCOUNTS[to_account_id]

    # --- PASO 3: Validadate Funds ---
    if from_acc.balance < amount:
        raise InsufficientFundsError(
            f"Insufficient funds: available {from_acc.balance}, requested {amount}"
        )

    # --- PASO 4: Atomic Transaction ---
    # In real Django: with transaction.atomic() + select_for_update()
    # Here a simulation of the atomicity with explicit try/except
    try:
        from_acc.balance -= amount
        to_acc.balance += amount

        transfer = Transfer(
            id=f"TRF-{uuid.uuid4().hex[:8].upper()}",
            idempotency_key=idempotency_key,
            from_account=from_account_id,
            to_account=to_account_id,
            amount=amount,
            currency=currency,
            status="completed",
            processed_at=datetime.now(timezone.utc)
        )

        # Audit log inside of "transaction" itself
        AUDIT_LOG.append(AuditLog(
            action="transfer",
            transfer_id=transfer.id,
            from_account=from_account_id,
            to_account=to_account_id,
            amount=amount,
            timestamp=transfer.processed_at
        ))

        # Save with idempotency_key as index
        TRANSFERS[idempotency_key] = transfer
        return transfer

    except Exception:
        # In real DB: the rollback is automatic when leave the atomic()
        # Here manual reverse
        from_acc.balance += amount
        to_acc.balance -= amount
        raise
