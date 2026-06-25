import mysql.connector
import pandas as pd
import numpy as np
import joblib
from datetime import datetime

from config import DB_CONFIG
from model_backup import backup_models

from catboost import CatBoostClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

from sklearn.metrics import (
    roc_auc_score,
    f1_score
)
print("=" * 60)
print("STARTING WEEKLY MANUAL AI RETRAINING")
print("=" * 60)

# ==========================================
# BACKUP CURRENT MODELS
# ==========================================

backup_models()

print("Previous models backed up")

# ==========================================
# LOAD DATASET
# ==========================================

conn = mysql.connector.connect(**DB_CONFIG)

query = """
SELECT *
FROM ai_training_dataset
WHERE target IS NOT NULL
ORDER BY time ASC
"""

df = pd.read_sql(query, conn)

conn.close()

print(f"Training Rows : {len(df)}")

if len(df) < 500:

    print("Not enough historical data for retraining.")
    exit()

# ==========================================
# FEATURES
# ==========================================

FEATURES = [

    # Technical Indicators
    "EMA20",
    "EMA50",
    "RSI",
    "ATR",
    "NATR",
    "BB_WIDTH",
    "CHAIKIN_VOL",
    "VQI",
    "TREND_STRENGTH",
    "CHANNEL_POSITION",

    # Manual AI Features
    "SLOPE_SIGNAL",
    "ACTIVE_PASSIVE",
    "power_score",
    "financial_strength",

    # Encoded Features
    "pair",
    "timeframe",
    "market_state",
    "frequency_type",
    "candle_type",

    # Live FinBERT
    "positive",
    "negative",
    "neutral",
    "news_strength",
    "dominant_sentiment"

]

# ==========================================
# VERIFY FEATURES EXIST
# ==========================================

missing = [
    feature
    for feature in FEATURES
    if feature not in df.columns
]

if missing:

    print()

    print("Missing Columns Found")

    for m in missing:
        print(" -", m)

    raise ValueError(
        "Training dataset is missing required features."
    )

# ==========================================
# PREPARE DATA
# ==========================================

X = df[FEATURES].copy()

y = df["target"].copy()

# Replace missing numeric values

X = X.fillna(0)

# Remove rows with missing targets

mask = y.notna()

X = X.loc[mask]

y = y.loc[mask]

print()

print("Features :", len(FEATURES))

print("Samples  :", len(X))

print()

# ==========================================
# CHRONOLOGICAL SPLIT
# 70 / 15 / 15
# ==========================================

n = len(X)

train_end = int(n * 0.70)

val_end = int(n * 0.85)

X_train = X.iloc[:train_end]
y_train = y.iloc[:train_end]

X_val = X.iloc[train_end:val_end]
y_val = y.iloc[train_end:val_end]

X_test = X.iloc[val_end:]
y_test = y.iloc[val_end:]

print("Training :", len(X_train))
print("Validation :", len(X_val))
print("Testing :", len(X_test))

print("=" * 60)
# ==========================================
# CATBOOST
# ==========================================

print()
print("Training CatBoost...")

cat_model = CatBoostClassifier(

    iterations=500,
    depth=6,
    learning_rate=0.03,
    auto_class_weights="Balanced",
    loss_function="Logloss",
    verbose=0

)

cat_model.fit(
    X_train,
    y_train
)

cat_val_prob = cat_model.predict_proba(X_val)[:,1]
cat_test_prob = cat_model.predict_proba(X_test)[:,1]

cat_auc = roc_auc_score(
    y_val,
    cat_val_prob
)

print(
    f"CatBoost Validation AUC : {cat_auc:.4f}"
)

# ==========================================
# XGBOOST
# ==========================================

print()
print("Training XGBoost...")

xgb_model = XGBClassifier(

    n_estimators=400,
    max_depth=6,
    learning_rate=0.03,
    eval_metric="logloss",
    random_state=42

)

xgb_model.fit(
    X_train,
    y_train
)

xgb_val_prob = xgb_model.predict_proba(X_val)[:,1]
xgb_test_prob = xgb_model.predict_proba(X_test)[:,1]

xgb_auc = roc_auc_score(
    y_val,
    xgb_val_prob
)

print(
    f"XGBoost Validation AUC : {xgb_auc:.4f}"
)

# ==========================================
# LIGHTGBM
# ==========================================

print()
print("Training LightGBM...")

lgbm_model = LGBMClassifier(

    n_estimators=400,
    learning_rate=0.03,
    max_depth=6,
    class_weight="balanced",
    random_state=42

)

lgbm_model.fit(
    X_train,
    y_train
)

lgbm_val_prob = lgbm_model.predict_proba(X_val)[:,1]
lgbm_test_prob = lgbm_model.predict_proba(X_test)[:,1]

lgb_auc = roc_auc_score(
    y_val,
    lgbm_val_prob
)

print(
    f"LightGBM Validation AUC : {lgb_auc:.4f}"
)

# ==========================================
# DYNAMIC ENSEMBLE WEIGHTS
# ==========================================

print()
print("Calculating Dynamic Ensemble Weights...")

total_auc = (
    cat_auc +
    xgb_auc +
    lgb_auc
)

CAT_WEIGHT = cat_auc / total_auc
XGB_WEIGHT = xgb_auc / total_auc
LGBM_WEIGHT = lgb_auc / total_auc

weights = {

    "catboost_weight": CAT_WEIGHT,
    "xgboost_weight": XGB_WEIGHT,
    "lightgbm_weight": LGBM_WEIGHT

}

print()

print("CatBoost Weight :", round(CAT_WEIGHT,4))
print("XGBoost Weight  :", round(XGB_WEIGHT,4))
print("LightGBM Weight :", round(LGBM_WEIGHT,4))

# ==========================================
# VALIDATION ENSEMBLE
# ==========================================

ensemble_val = (

    CAT_WEIGHT * cat_val_prob

    +

    XGB_WEIGHT * xgb_val_prob

    +

    LGBM_WEIGHT * lgbm_val_prob

)

val_auc = roc_auc_score(
    y_val,
    ensemble_val
)

print()

print(
    "Ensemble Validation AUC :",
    round(val_auc,4)
)

# ==========================================
# TEST ENSEMBLE
# ==========================================

ensemble_test = (

    CAT_WEIGHT * cat_test_prob

    +

    XGB_WEIGHT * xgb_test_prob

    +

    LGBM_WEIGHT * lgb_test_prob

)

test_auc = roc_auc_score(
    y_test,
    ensemble_test
)

print(
    "Ensemble Test AUC :",
    round(test_auc,4)
)

print("="*60)
# ==========================================
# FIND BEST THRESHOLD
# ==========================================

print()
print("Searching for Best Threshold...")

best_threshold = 0.50
best_f1 = 0

for threshold in np.arange(0.30, 0.91, 0.01):

    predictions = (
        ensemble_val >= threshold
    ).astype(int)

    score = f1_score(
        y_val,
        predictions
    )

    if score > best_f1:

        best_f1 = score
        best_threshold = float(threshold)

print()

print(
    "Best Threshold :",
    round(best_threshold,2)
)

print(
    "Best F1 Score :",
    round(best_f1,4)
)

print("=" * 60)

# ==========================================
# SAVE MODELS
# ==========================================

print("Saving Models...")

joblib.dump(
    cat_model,
    "manual_catboost.pkl"
)

joblib.dump(
    xgb_model,
    "manual_xgboost.pkl"
)

joblib.dump(
    lgbm_model,
    "manual_lgbm.pkl"
)

joblib.dump(
    weights,
    "manual_ensemble_model.pkl"
)

joblib.dump(
    best_threshold,
    "manual_best_threshold.pkl"
)

print("Models Saved")

# ==========================================
# SAVE TRAINING METADATA
# ==========================================

training_info = {

    "training_date":
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

    "rows":
        len(df),

    "features":
        len(FEATURES),

    "validation_auc":
        round(val_auc,4),

    "test_auc":
        round(test_auc,4),

    "catboost_auc":
        round(cat_auc,4),

    "xgboost_auc":
        round(xgb_auc,4),

    "lightgbm_auc":
        round(lgb_auc,4),

    "catboost_weight":
        round(CAT_WEIGHT,4),

    "xgboost_weight":
        round(XGB_WEIGHT,4),

    "lightgbm_weight":
        round(LGBM_WEIGHT,4),

    "best_threshold":
        round(best_threshold,2)

}

joblib.dump(
    training_info,
    "manual_training_info.pkl"
)

# ==========================================
# TRAINING LOG
# ==========================================

with open(
    "manual_training_log.txt",
    "a"
) as f:

    f.write("\n")

    f.write("=" * 60)

    f.write("\n")

    f.write(
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    f.write("\n")

    f.write(
        f"Rows : {len(df)}\n"
    )

    f.write(
        f"Features : {len(FEATURES)}\n"
    )

    f.write(
        f"Validation AUC : {val_auc:.4f}\n"
    )

    f.write(
        f"Test AUC : {test_auc:.4f}\n"
    )

    f.write(
        f"CatBoost Weight : {CAT_WEIGHT:.4f}\n"
    )

    f.write(
        f"XGBoost Weight : {XGB_WEIGHT:.4f}\n"
    )

    f.write(
        f"LightGBM Weight : {LGBM_WEIGHT:.4f}\n"
    )

    f.write(
        f"Best Threshold : {best_threshold:.2f}\n"
    )

print()
print("=" * 60)
print("WEEKLY RETRAINING COMPLETE")
print("=" * 60)
print()

print("Validation AUC :", round(val_auc,4))
print("Test AUC       :", round(test_auc,4))

print()

print("CatBoost Weight :", round(CAT_WEIGHT,4))
print("XGBoost Weight  :", round(XGB_WEIGHT,4))
print("LightGBM Weight :", round(LGBM_WEIGHT,4))

print()

print("Best Threshold :", round(best_threshold,2))

print()

print("Models Updated Successfully")
