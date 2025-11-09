import numpy as np
import pandas as pd
import joblib
from datetime import datetime

NUMBER_FEATURES = 12

def create_matrix(df, state):
    rows = []
    for _, row in df.iterrows():
        rows.append(create_row(row, state))
    return np.vstack(rows) if rows else np.zeros((0, NUMBER_FEATURES))


# converting the transaction into numbers to be added to the matrix
def create_row(txn, state):
    features = []

    # adding amount features
    amount = float(txn.get('amount', 0.0))
    features.append(amount)
    # log to reduce impact from spike
    features.append(np.log1p(max(amount, 0.0)))


    # adding date and time related features
    dt = pd.to_datetime(txn.get('date', datetime.utcnow()), errors='coerce')
    if pd.isna(dt):
        dt = pd.Timestamp(datetime.utcnow())

    features.extend([
        dt.dayofweek,
        dt.day,
        dt.month,
        getattr(dt, 'hour', 12) if not pd.isna(getattr(dt, 'hour', np.nan)) else 12,
    ])
    features.append(1 if dt.dayofweek >= 5 else 0)

    # get merchant and the channel encodings
    merchant = txn.get('merchant_name', 'Unknown')
    if pd.isna(merchant):
        merchant = 'Unknown'
    channel = txn.get('payment_channel', 'online')
    if pd.isna(channel):
        channel = 'online'

    merchant_encoder = state['merchant_encoder']
    channel_encoder = state['channel_encoder']

    if merchant not in merchant_encoder.classes_:
        merchant = 'Unknown'
    if channel not in channel_encoder.classes_:
        channel = 'online'


    merchant_encoded = int(merchant_encoder.transform([merchant])[0])
    channel_encoded  = int(channel_encoder.transform([channel])[0])

    features.append(merchant_encoded)
    features.append(channel_encoded)

    # adding txn status feature
    features.append(1 if bool(txn.get('pending', False)) else 0)

    mean_merchant = state['merchant_mean']
    std_merchant  = state['merchant_std']

    # using zscore to determine how far from the avg it is
    if merchant in mean_merchant:
        m_mean = float(mean_merchant[merchant])
        m_std  = float(std_merchant.get(merchant, 0.0))
        denom  = m_std if m_std and m_std > 0 else 1.0
        z = (amount - m_mean) / (denom + 1e-6)
        
    else:
        g_mean = float(state.get('global_amount_mean', amount))
        g_std  = float(state.get('global_amount_std', 1.0))
        denom  = g_std if g_std and g_std > 0 else 1.0
        z = (amount - g_mean) / (denom + 1e-6)
    z = float(np.clip(z, -5.0, 5.0))

    features.append(z)
    features.append(abs(z))
    return np.array(features, dtype=float)

# using scaler created to normalize data
def apply_scaler(df, state):
    data = create_matrix(df, state)
    return state['scaler'].transform(data)

def predict_single(transaction, feature_state, models):
    df = pd.DataFrame([transaction])

    thresholds = feature_state.get('risk_thresholds', {})
    LOW_RISK_MAX  = thresholds.get('LOW_RISK_MAX')
    HIGH_RISK_MIN = thresholds.get('HIGH_RISK_MIN')
    
    data = apply_scaler(df, feature_state)

    if_pred = models['isolation_forest'].predict(data)[0]
    if_score = float(-models['isolation_forest'].score_samples(data)[0])

    is_fraud = (if_pred == -1)

    if if_score >= HIGH_RISK_MIN:
        tier = "high"
    elif if_score >= LOW_RISK_MAX:
        tier = "medium"
    else:
        tier = "low"

    return if_score, bool(is_fraud), tier
    # {
    #     'is_fraud': bool(is_fraud),
    #     'fraud_score': if_score,
    #     'isolation_forest_prediction': int(if_pred),
    #     'risk_level': tier
    # }


# will need util to load model and data
def load_pipeline(filepath):
    bundle = joblib.load(filepath)
    return bundle['feature_state'], bundle['models']


def predict_new_transaction(transaction_dict, model_path="fraud_model.joblib"):
    feature_state, models = load_pipeline(model_path)

    return predict_single(transaction_dict, feature_state, models)