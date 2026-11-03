"""Sınıflandırma modelleri ve metrikler (Faz 3 ve Faz 6 ortak kullanır)."""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, cohen_kappa_score, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from xgboost import XGBClassifier

import config

RS = config.RANDOM_STATE


def make_pipeline(name, params=None):
    """Modeli bir Pipeline içinde döndürür.

    SVM ve MLP için önce StandardScaler var. Pipeline sayesinde ölçekleyici her
    CV katmanında yalnızca o katmanın eğitim kısmıyla fit edilir (veri sızıntısı yok).
    params: {"n_estimators": 300, ...} (önek olmadan)
    """
    if name == "RandomForest":
        clf = RandomForestClassifier(random_state=RS, n_jobs=-1)
        steps = [("clf", clf)]
    elif name == "XGBoost":
        clf = XGBClassifier(random_state=RS, n_jobs=-1, tree_method="hist",
                            objective="multi:softprob", eval_metric="mlogloss")
        steps = [("clf", clf)]
    elif name == "SVM":
        clf = SVC(kernel="rbf", probability=True, random_state=RS)
        steps = [("scaler", StandardScaler()), ("clf", clf)]
    elif name == "MLP":
        clf = MLPClassifier(max_iter=500, early_stopping=True, random_state=RS)
        steps = [("scaler", StandardScaler()), ("clf", clf)]
    else:
        raise ValueError(name)
    pipe = Pipeline(steps)
    if params:
        pipe.set_params(**{f"clf__{k}": v for k, v in params.items()})
    return pipe


def param_space(name):
    """config.PARAM_SPACES'i Pipeline'ın beklediği 'clf__' önekiyle döndürür."""
    return {f"clf__{k}": v for k, v in config.PARAM_SPACES[name].items()}


def strip_prefix(params):
    return {k.replace("clf__", ""): v for k, v in params.items()}


def compute_metrics(y_true, y_pred, proba=None, labels=None):
    """Hocanın istediği 5 metrik (+ weighted sürümler ve Kappa)."""
    labels = labels if labels is not None else sorted(config.CLASSES)
    m = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision_macro": precision_score(y_true, y_pred, average="macro", labels=labels, zero_division=0),
        "recall_macro": recall_score(y_true, y_pred, average="macro", labels=labels, zero_division=0),
        "f1_macro": f1_score(y_true, y_pred, average="macro", labels=labels, zero_division=0),
        "precision_weighted": precision_score(y_true, y_pred, average="weighted", labels=labels, zero_division=0),
        "recall_weighted": recall_score(y_true, y_pred, average="weighted", labels=labels, zero_division=0),
        "f1_weighted": f1_score(y_true, y_pred, average="weighted", labels=labels, zero_division=0),
        "kappa": cohen_kappa_score(y_true, y_pred),
        "roc_auc_ovr_macro": np.nan,
    }
    if proba is not None:
        present = np.unique(y_true)
        if len(present) == len(labels):
            m["roc_auc_ovr_macro"] = roc_auc_score(y_true, proba, multi_class="ovr",
                                                   average="macro", labels=labels)
        elif len(present) > 1:
            # Test kümesinde bazı sınıflar yoksa (Faz 6'da olabilir) yalnızca var olanlarla hesapla
            idx = [labels.index(c) for c in present]
            p = proba[:, idx]
            p = p / p.sum(axis=1, keepdims=True)
            m["roc_auc_ovr_macro"] = roc_auc_score(y_true, p, multi_class="ovr",
                                                   average="macro", labels=list(present))
    return m
