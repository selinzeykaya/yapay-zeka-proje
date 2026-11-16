"""src/ml_utils.py testleri: metrikler doğru mu, modeller kurulup eğitilebiliyor mu?"""
import numpy as np
import pytest
from sklearn.metrics import f1_score, jaccard_score

import config
from src import ml_utils as mu

LABELS = sorted(config.CLASSES)


def ornek_veri(n=600, seed=0):
    """Her sınıfın belirgin bir özellik ortalaması olduğu küçük yapay veri."""
    rng = np.random.default_rng(seed)
    y = np.repeat(LABELS, n // len(LABELS))
    X = rng.normal(size=(len(y), len(config.MODEL_FEATURES))) + y[:, None] * 2.0
    return X, y


def test_kusursuz_tahminde_butun_metrikler_1():
    y = np.array(LABELS * 10)
    proba = np.eye(len(LABELS))[y]
    m = mu.compute_metrics(y, y, proba, LABELS)
    for k in ["accuracy", "precision_macro", "recall_macro", "f1_macro", "kappa",
              "iou_macro", "iou_weighted", "roc_auc_ovr_macro"]:
        assert m[k] == pytest.approx(1.0), k


def test_iou_f1_iliskisi_sinif_bazinda():
    # Her sınıf için IoU = F1 / (2 − F1) olmalı (rapordaki açıklamanın kanıtı)
    rng = np.random.default_rng(1)
    y = rng.choice(LABELS, 500)
    p = np.where(rng.random(500) < 0.7, y, rng.choice(LABELS, 500))
    f1 = f1_score(y, p, labels=LABELS, average=None)
    iou = jaccard_score(y, p, labels=LABELS, average=None)
    assert np.allclose(iou, f1 / (2 - f1))
    m = mu.compute_metrics(y, p, None, LABELS)
    assert m["iou_macro"] == pytest.approx(iou.mean())
    assert m["iou_macro"] <= m["f1_macro"]


def test_olasilik_yoksa_roc_auc_nan():
    y = np.array(LABELS * 5)
    assert np.isnan(mu.compute_metrics(y, y, None, LABELS)["roc_auc_ovr_macro"])


def test_testte_eksik_sinif_varken_roc_auc_hesaplanir():
    # Faz 6'da bir şehirde bazı sınıflar hiç olmayabilir
    y = np.array([0, 0, 1, 1, 2, 2])
    proba = np.full((6, len(LABELS)), 0.01)
    proba[np.arange(6), y] = 0.95
    proba /= proba.sum(axis=1, keepdims=True)
    assert mu.compute_metrics(y, y, proba, LABELS)["roc_auc_ovr_macro"] == pytest.approx(1.0)


@pytest.mark.parametrize("name", config.MODELS)
def test_modeller_kurulup_egitilebiliyor(name):
    X, y = ornek_veri()
    pipe = mu.make_pipeline(name)
    pipe.fit(X, y)
    m = mu.compute_metrics(y, pipe.predict(X), pipe.predict_proba(X), LABELS)
    assert m["accuracy"] > 0.8, f"{name} kolay veride bile öğrenemedi"


@pytest.mark.parametrize("name", config.MODELS)
def test_arama_araligi_pipeline_parametreleriyle_uyumlu(name):
    pipe = mu.make_pipeline(name)
    gecerli = set(pipe.get_params())
    for k in mu.param_space(name):
        assert k in gecerli, f"{name}: {k} Pipeline'da yok"


def test_strip_prefix():
    assert mu.strip_prefix({"clf__C": 1, "clf__gamma": "scale"}) == {"C": 1, "gamma": "scale"}


def test_bilinmeyen_model_hata_verir():
    with pytest.raises(ValueError):
        mu.make_pipeline("CNN")
