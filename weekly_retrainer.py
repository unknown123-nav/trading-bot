import mysql.connector
import pandas as pd
import numpy as np
import joblib
from model_backup import backup_models
from config import DB_CONFIG

from sklearn.metrics import roc_auc_score

from catboost import CatBoostClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

print("STARTING RETRAINING")

backup_models()
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

print("Rows:", len(df))

if len(df) < 500:

    print("Not enough data")

    exit()


# ==========================================
# FEATURES
# ==========================================

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

"confidence",

"power_score",

"financial_strength"

]

X = df[FEATURES]

y = df["target"]


# ==========================================
# 70 15 15 SPLIT
# ==========================================

n = len(df)

train_end = int(n*0.70)

tune_end = int(n*0.85)

X_train = X.iloc[:train_end]
y_train = y.iloc[:train_end]

X_val = X.iloc[train_end:tune_end]
y_val = y.iloc[train_end:tune_end]

X_test = X.iloc[tune_end:]
y_test = y.iloc[tune_end:]


# ==========================================
# CATBOOST
# ==========================================

cat_model = CatBoostClassifier(

iterations=500,
depth=6,
learning_rate=0.03,
verbose=0

)

cat_model.fit(

X_train,
y_train

)

cat_val_prob = cat_model.predict_proba(X_val)[:,1]


# ==========================================
# XGBOOST
# ==========================================

xgb_model = XGBClassifier(

n_estimators=400,
max_depth=6,
learning_rate=0.03

)

xgb_model.fit(

X_train,
y_train

)

xgb_val_prob = xgb_model.predict_proba(X_val)[:,1]


# ==========================================
# LIGHTGBM
# ==========================================

lgbm_model = LGBMClassifier(

n_estimators=400,
learning_rate=0.03,
max_depth=6

)

lgbm_model.fit(

X_train,
y_train

)

lgbm_val_prob = lgbm_model.predict_proba(X_val)[:,1]


# ==========================================
# ENSEMBLE
# ==========================================

ensemble_prob = (

0.33*cat_val_prob

+

0.33*xgb_val_prob

+

0.34*lgbm_val_prob

)

auc = roc_auc_score(

y_val,

ensemble_prob

)

print("Validation AUC =", auc)


# ==========================================
# SAVE MODELS
# ==========================================

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

0.5,

"ensemble_threshold.pkl"

)

print("MODELS SAVED")
