from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.models.transaction import Transaction
from app.models.category import Category
from app.ml.model_store import load_model, save_model

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np


router = APIRouter(prefix="/model", tags=["model"])

class PredictIn(BaseModel):
  description: str
  amount: Optional[float] = None
  merchant: Optional[str] = None

class PredictOut(BaseModel):
    predicted_category_id: Optional[str]
    predicted_category_name: Optional[str]
    proba: Optional[float]

def _build_text(desc: str, merchant: Optional[str]) -> str:
    return f"{(desc or '').strip()} {(merchant or '').strip()}".strip()

def _rule_based(text: str):
    t = text.upper()
    if any(x in t for x in ["GRAB", "GOJEK", "GOCAR"]):
        return "Transport", 0.65
    if any(x in t for x in ["STARBUCKS", "KFC", "MCD", "WARTEG", "NASI", "RESTO", "BAKSO"]):
        return "Food", 0.60
    if any(x in t for x in ["PLN", "TOKEN", "PULSA", "TELKOM", "PDAM"]):
        return "Bills", 0.60
    return None, None

async def _category_map():
    cats = await Category.find_all().to_list()
    return {str(c.id): c.name for c in cats}

@router.post("/predict", response_model=List[PredictOut])
async def predict(items: List[PredictIn]):
    vec, clf, labels = load_model()
    cat_names = await _category_map()
    texts = [_build_text(i.description, i.merchant) for i in items]

    if vec is None or clf is None or labels is None:
        out = []
        for t in texts:
            name, p = _rule_based(t)
            cid = None
            if name:
                cid = next((k for k, v in cat_names.items() if v.lower() == name.lower()), None)
            out.append({"predicted_category_id": cid, "predicted_category_name": name, "proba": p})
        return out

    X = vec.transform(texts)
    proba = clf.predict_proba(X)
    idx = np.argmax(proba, axis=1)
    preds = [labels[i] for i in idx]
    confs = [float(proba[j, i]) for j, i in enumerate(idx)]
    return [
        {"predicted_category_id": pid,
         "predicted_category_name": cat_names.get(pid, "(unknown)"),
         "proba": conf}
        for pid, conf in zip(preds, confs)
    ]

class RetrainOut(BaseModel):
    trained_on_rows: int
    classes: List[str]
    accuracy: Optional[float] = None

@router.post("/retrain", response_model=RetrainOut)
async def retrain():
    txs = await Transaction.find({"category_id": {"$ne": None}}).to_list()
    if len(txs) < 10:
        raise HTTPException(status_code=400, detail="Butuh minimal 10 transaksi berlabel untuk training.")

    texts = [_build_text(t.description, t.merchant) for t in txs]
    y = [t.category_id for t in txs]

    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=30000)
    X = vec.fit_transform(texts)

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    clf = LogisticRegression(max_iter=300, solver="liblinear")
    clf.fit(Xtr, ytr)

    acc = accuracy_score(yte, clf.predict(Xte))
    labels = clf.classes_ # urutan label sesuai kolom predict_proba

    save_model(vec, clf, labels)
    return {"trained_on_rows": len(txs), "classes": list(labels), "accuracy": float(acc)}

@router.get("/metrics")
async def metrics():
    vec, clf, labels = load_model()
    return {"has_model": vec is not None, "num_labels": 0 if labels is None else len(labels)}