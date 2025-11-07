import asyncio
from datetime import date as DateType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from fraud_detection.prediction import load_pipeline, predict_single
from infrastructure.db.repos.transaction_repo import SqlTransactionRepo


class FraudDetectionService:
    def __init__(
            self, 
            session_factory: async_sessionmaker[AsyncSession], 
            model_path: str, 
            *, 
            enabled: bool = True
        ):
        
        self.session_factory = session_factory
        self.model_path = model_path
        self.enabled = enabled

        self._loaded = False
        self._feature_state = None
        self._models = None
        

    def _load_pipeline_model(self):
        if not self._loaded:
            self._feature_state, self._models = load_pipeline(self.model_path)
            self._loaded = True


    def enqueue_ids(self, ids) -> None:
        if not self.enabled:
            return
        ids = list({int(i) for i in ids or []})
        if not ids:
            return
        asyncio.create_task(self._run_prediction(ids))



    async def _run_prediction(self, ids: list[int]) -> None:
        self._load_pipeline_model()
        async with self.session_factory() as db:
            repo = SqlTransactionRepo(db)
            rows = await repo.fetch_transactions_for_ML_Model(ids)

            updates = []
            for txn_id, amount, payment_channel, pending, txn_date, merchant in rows:
                date_str = (
                    txn_date.isoformat()
                    if isinstance(txn_date, DateType)
                    else (str(txn_date) if txn_date else None)
                )
                
                features = {
                    "amount": float(amount or 0.0),
                    "payment_channel": payment_channel,
                    "pending": bool(pending),
                    "date": date_str,
                    "merchant_name": merchant,
                }

                prediction_score, is_suspected, risk_tier = predict_single(
                    features, 
                    self._feature_state, 
                    self._models
                )
                updates.append((txn_id, prediction_score, is_suspected, risk_tier))

            await repo.set_fraud_results(updates)
            await db.commit()