import os, joblib


MODEL_DIR = "app/ml/models"
VEC_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")
CLF_PATH = os.path.join(MODEL_DIR, "model.pkl")
LBL_PATH = os.path.join(MODEL_DIR, "labels.pkl")


def _ensure_dir():
   os.makedirs(MODEL_DIR, exist_ok=True)


def save_model(vec, clf, labels):
   _ensure_dir()
joblib.dump(vec, VEC_PATH)
joblib.dump(clf, CLF_PATH)
joblib.dump(labels, LBL_PATH)


def load_model():
    if not (os.path.exists(VEC_PATH) and os.path.exists(CLF_PATH) and os.path.exists(LBL_PATH)):
        return None, None, None
    return joblib.load(VEC_PATH), joblib.load(CLF_PATH), joblib.load(LBL_PATH)