import mysql.connector
import pandas as pd
import joblib

from config import DB_CONFIG
from model_backup import backup_models

from sklearn.metrics import roc_auc_score

from catboost import CatBoostClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier


print("STARTING RETRAINING")

backup_models()

# ======================================
# LOAD DATASET
# ======================================

conn = mysql.connector.connect(**DB_CONFIG)

query = """
SELECT *
FROM ai_training_dataset
WHERE target IS NOT NULL
ORDER BY time ASC
"""

df = pd.read_sql(query, conn)

conn.close()

print("Rows =", len(df))

if len(df) < 500:

    print("Not enough rows")

    exit()


# ======================================
# FEATURES
# ======================================

FEATURES = [

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

"overall_positive",
"overall_negative",
"overall_neutral",
"news_strength",

"power_score",
"financial_strength"

]
X = df[FEATURES]

y = df["target"]

X = X.fillna(0)

mask = y.notna()

X = X[mask]
y = y[mask]


# ======================================
# 70 / 15 / 15
# ======================================

n = len(df)

train_end = int(n * 0.70)

val_end = int(n * 0.85)

X_train = X.iloc[:train_end]
y_train = y.iloc[:train_end]

X_val = X.iloc[train_end:val_end]
y_val = y.iloc[train_end:val_end]

X_test = X.iloc[val_end:]
y_test = y.iloc[val_end:]


# ======================================
# CATBOOST
# ======================================

print("Training CatBoost")

cat_model = CatBoostClassifier(

    iterations=500,
    depth=6,
    learning_rate=0.03,
    auto_class_weights="Balanced",
    verbose=0

)

cat_model.fit(

    X_train,
    y_train

)

cat_val_prob = cat_model.predict_proba(X_val)[:,1]

cat_test_prob = cat_model.predict_proba(X_test)[:,1]


# ======================================
# XGBOOST
# ======================================

print("Training XGBoost")

xgb_model = XGBClassifier(

    n_estimators=400,
    max_depth=6,
    learning_rate=0.03,
    eval_metric="logloss"

)

xgb_model.fit(

    X_train,
    y_train

)

xgb_val_prob = xgb_model.predict_proba(X_val)[:,1]

xgb_test_prob = xgb_model.predict_proba(X_test)[:,1]


# ======================================
# LIGHTGBM
# ======================================

print("Training LightGBM")

lgbm_model = LGBMClassifier(

    n_estimators=400,
    learning_rate=0.03,
    max_depth=6,
    class_weight="balanced"

)

lgbm_model.fit(

    X_train,
    y_train

)

lgbm_val_prob = lgbm_model.predict_proba(X_val)[:,1]

lgbm_test_prob = lgbm_model.predict_proba(X_test)[:,1]


# ======================================
# ENSEMBLE
# ======================================

ensemble_val = (

    0.33 * cat_val_prob
    +
    0.33 * xgb_val_prob
    +
    0.34 * lgbm_val_prob

)

val_auc = roc_auc_score(

    y_val,
    ensemble_val

)

print("Validation AUC =", round(val_auc,4))


ensemble_test = (

    0.33 * cat_test_prob
    +
    0.33 * xgb_test_prob
    +
    0.34 * lgbm_test_prob

)

test_auc = roc_auc_score(

    y_test,
    ensemble_test

)

print("Test AUC =", round(test_auc,4))


# ======================================
# SAVE MODELS
# ======================================

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

weights = {

    "catboost_weight":0.33,
    "xgboost_weight":0.33,
    "lightgbm_weight":0.34

}

joblib.dump(

    weights,

    "manual_ensemble_model.pkl"

)

joblib.dump(

    0.50,

    "manual_best_threshold.pkl"

)


# ======================================
# TRAINING LOG
# ======================================

with open(

    "manual_training_log.txt",

    "a"

) as f:

    f.write(

        f"\nRows={len(df)} "

        f"Val_AUC={val_auc:.4f} "

        f"Test_AUC={test_auc:.4f}"

    )

print("MODELS SAVED")
print("RETRAINING COMPLETE")
