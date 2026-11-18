"""Resmi (Colab'da, Faz 3'te eğitilmiş) modelleri YENİDEN EĞİTMEDEN yükler, Faz 3 test noktalarında değerlendirir
ve sınıf bazında IoU tablosunu (sinif_bazinda_iou.csv) bu resmi modellerden üretir.

Kullanım (proje kökünden):
    python tools/resmi_model_iou.py "<Drive'daki yapay-zeka-proje klasörü>" [çıktı.csv]
Gereken dosyalar: results/models/{RandomForest,XGBoost,SVM,MLP}.joblib, data/processed/samples_2021.csv,
data/processed/split_assignments.csv, results/tables/model_karsilastirma.csv

Neden gerekli? Aynı ayarlarla başka bir bilgisayarda yeniden eğitim XGBoost için birebir aynı ağaçları üretmedi
(macro-F1 0.776; xgboost sürümü Colab'daki ile aynı: 3.4.1). Resmi model dosyası doğrudan değerlendirildiğinde ise
resmi sonuç birebir çıkıyor. Her model için accuracy ve macro-F1 resmi tabloyla karşılaştırılır; tutmazsa betik durur.

XGBoost notu: joblib içindeki XGBoost "tam anlık görüntüsü" (Config + Model, UBJSON) bazı ortamlarda
`__setstate__` ile açılmıyor ("input stream corrupted"). Bu durumda anlık görüntünün "Model" kısmı (ağaçlar,
hiçbir değer değişmeden) standart XGBoost JSON model dosyasına çevrilip Booster.load_model ile yüklenir.
"""
import json
import struct
import sys
import tempfile
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK))
import config  # noqa: E402


class UBJSON:
    """XGBoost'un kullandığı UBJSON alt kümesini okur."""
    TUR = {"i": ">b", "U": ">B", "I": ">h", "l": ">i", "L": ">q", "d": ">f", "D": ">d"}
    DIZI = {"i": "b", "U": "B", "I": ">i2", "l": ">i4", "L": ">i8", "d": ">f4", "D": ">f8"}

    def __init__(self, b):
        self.b, self.i = memoryview(b), 0

    def _c(self):
        c = chr(self.b[self.i]); self.i += 1; return c

    def _sayi(self, t):
        v = struct.unpack_from(self.TUR[t], self.b, self.i)[0]; self.i += struct.calcsize(self.TUR[t]); return v

    def _metin(self):
        n = self._sayi(self._c()); s = bytes(self.b[self.i:self.i + n]).decode("utf-8"); self.i += n; return s

    def _baslik(self):
        tur = n = None
        if chr(self.b[self.i]) == "$":
            self.i += 1; tur = self._c()
        if chr(self.b[self.i]) == "#":
            self.i += 1; n = self._sayi(self._c())
        return tur, n

    def oku(self, t=None):
        t = t or self._c()
        if t in self.TUR:
            return self._sayi(t)
        if t == "S":
            return self._metin()
        if t in "TFZ":
            return {"T": True, "F": False, "Z": None}[t]
        if t == "[":
            tur, n = self._baslik()
            if n is not None and tur in self.DIZI:
                a = np.frombuffer(self.b, dtype=self.DIZI[tur], count=n, offset=self.i); self.i += a.nbytes
                return a.astype(float if tur in "dD" else int).tolist()
            if n is not None:
                return [self.oku(tur) for _ in range(n)]
            out = []
            while chr(self.b[self.i]) != "]":
                out.append(self.oku())
            self.i += 1; return out
        if t == "{":
            tur, n = self._baslik()
            if n is not None:
                return {self._metin(): self.oku(tur) for _ in range(n)}
            out = {}
            while chr(self.b[self.i]) != "}":
                k = self._metin(); out[k] = self.oku()
            self.i += 1; return out
        raise ValueError(f"bilinmeyen UBJSON türü {t!r}")


def yukle(yol):
    import joblib
    import xgboost
    yakalanan = {}
    asil = xgboost.core.Booster.__setstate__

    def yedekli(self, state):
        try:
            asil(self, state)
        except xgboost.core.XGBoostError:
            yakalanan["handle"] = bytes(state["handle"])
            st = dict(state); st["handle"] = None
            asil(self, st)

    xgboost.core.Booster.__setstate__ = yedekli
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            obj = joblib.load(yol)
    finally:
        xgboost.core.Booster.__setstate__ = asil
    model = obj["model"] if isinstance(obj, dict) else obj
    if "handle" in yakalanan:                                  # XGBoost: anlık görüntüden ağaçları yükle
        m = UBJSON(yakalanan["handle"]).oku()["Model"]
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(m, f)
        b = xgboost.Booster(); b.load_model(f.name); Path(f.name).unlink()
        model.named_steps["clf"]._Booster = b
    return model


def main(drive, cikti):
    from sklearn.metrics import accuracy_score, f1_score, jaccard_score
    D = Path(drive)
    df = pd.read_csv(D / "data/processed/samples_2021.csv").merge(
        pd.read_csv(D / "data/processed/split_assignments.csv")[["sample_id", "split"]], on="sample_id")
    test = df[df["split"] == "test"]
    resmi = pd.read_csv(D / "results/tables/model_karsilastirma.csv", index_col=0, encoding="utf-8-sig")
    L = sorted(config.CLASSES)
    tablo = {}
    for ad in config.MODELS:
        model = yukle(D / "results/models" / f"{ad}.joblib")
        p = model.predict(test[config.MODEL_FEATURES])
        acc, f1 = accuracy_score(test["class"], p), f1_score(test["class"], p, average="macro", labels=L)
        ok = abs(acc - resmi.loc[ad, "accuracy"]) < 5e-5 and abs(f1 - resmi.loc[ad, "f1_macro"]) < 5e-5
        print(f"{ad:13s} accuracy {acc:.4f}  macro-F1 {f1:.4f}  {'✓ resmi tabloyla aynı' if ok else '✗ RESMİ TABLOYLA FARKLI'}")
        if not ok:
            sys.exit(f"{ad}: resmi model resmi sonucu üretmedi; IoU tablosu yazılmadı.")
        tablo[ad] = jaccard_score(test["class"], p, average=None, labels=L)
    t = pd.DataFrame(tablo, index=[config.CLASSES[k] for k in L])
    t.loc["Ortalama (macro)"] = t.mean()
    t = t.round(4)
    t.to_csv(cikti, encoding="utf-8-sig")
    print(t.to_string()); print("yazıldı:", cikti)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "sinif_bazinda_iou.csv")
