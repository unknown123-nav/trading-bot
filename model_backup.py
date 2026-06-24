import os
import shutil
from datetime import datetime

BACKUP_FOLDER = "model_backups"

os.makedirs(
    BACKUP_FOLDER,
    exist_ok=True
)

MODELS = [

    "manual_catboost.pkl",

    "manual_xgboost.pkl",

    "manual_lgbm.pkl",

    "ensemble_threshold.pkl"
]


def backup_models():

    timestamp = datetime.now().strftime(
        "%Y_%m_%d_%H_%M"
    )

    for model in MODELS:

        if not os.path.exists(model):
            continue

        filename = (
            model.replace(
                ".pkl",
                ""
            )
            +
            f"_{timestamp}.pkl"
        )

        destination = os.path.join(
            BACKUP_FOLDER,
            filename
        )

        shutil.copy2(
            model,
            destination
        )

        print(
            f"BACKUP CREATED → {filename}"
        )
