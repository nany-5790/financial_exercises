import logging
from fastapi import FastAPI, HTTPException
from schemas import TransferRequest
from services import process_transfer, InsufficientFundsError, AccountNotFoundError

logger = logging.getLogger(__name__)
app = FastAPI()


@app.post("/api/v1/transfers", status_code=201)
def create_transfer(request: TransferRequest):
    try:
        transfer = process_transfer(
            idempotency_key=request.idempotency_key,
            from_account_id=request.from_account,
            to_account_id=request.to_account,
            amount=request.amount,
            currency=request.currency,
        )
        return {
            "transfer_id": transfer.id,
            "status": transfer.status,
            "processed_at": transfer.processed_at.isoformat(),
        }

    except AccountNotFoundError as e:
        # 404 — el recurso no existe
        raise HTTPException(status_code=404, detail=str(e))

    except InsufficientFundsError:
        # 422 — input válido pero regla de negocio no cumplida
        raise HTTPException(status_code=422, detail="Insufficient funds")

    except Exception as e:
        # 500 — error interno, se loggea pero NUNCA se expone
        logger.error("Unexpected error in create_transfer", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
