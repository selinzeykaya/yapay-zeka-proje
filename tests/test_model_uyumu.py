"""Web sitesi ve panel EĞİTTİĞİMİZ modelin resmi (Colab, Faz 3/4) sonuçlarını mı gösteriyor?

Kural: Site ve panel yalnızca resmi sonuçları gösterir. Yerel yeniden eğitimden gelen sayılar (xgboost sürüm farkı
nedeniyle XGBoost macro-F1 0.776 gibi) resmi değerlerin yerine geçemez. Bu testler web/data/ozet.json'daki sayıları
panel/veri/tables/ altındaki resmi Colab tablolarıyla karşılaştırır.
"""
import csv
import json
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parent.parent
OZET = KOK / "web" / "data" / "ozet.json"
TABLO = KOK / "panel" / "veri" / "tables"

pytestmark = pytest.mark.skipif(not OZET.exists(), reason="web/data/ozet.json yok (web/veri_hazirla.py çalıştırılmadı)")


def oku(ad):
    with open(TABLO / f"{ad}.csv", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def ozet():
    return json.loads(OZET.read_text(encoding="utf-8"))


def test_siniflandirma_sayilari_resmi_colab(ozet):
    resmi = {r["model"]: r for r in oku("model_karsilastirma")}
    assert float(resmi["XGBoost"]["f1_macro"]) == pytest.approx(0.7833, abs=1e-4), "panel verisi resmi değil"
    for model, s in ozet["modeller"].items():
        assert s["f1"] == pytest.approx(float(resmi[model]["f1_macro"]), abs=6e-4), model
        assert s["acc"] == pytest.approx(float(resmi[model]["accuracy"]), abs=6e-4), model
        assert s["kappa"] == pytest.approx(float(resmi[model]["kappa"]), abs=6e-4), model


def test_lst_regresyonu_resmi_colab(ozet):
    for r in oku("lst_regresyon_metrikleri"):              # resmi tablodaki her model resmi değerle görünmeli
        s = ozet["lst_regresyon"][r["model"]]
        assert s["kaynak"] == "Colab (resmi)", r["model"]
        assert s["r2"] == pytest.approx(float(r["R2_ort"]), abs=6e-4), r["model"]
    yerel = [m for m, s in ozet["lst_regresyon"].items() if s["kaynak"] != "Colab (resmi)"]
    assert yerel == ["XGBRegressor"], "yalnızca resmi tabloda olmayan XGBoost yerel olabilir"


def test_genelleme_ve_il_sayilari_resmi(ozet):
    loco = {(r["model"], r["test_city"], r["duzen"]): float(r["f1_macro"]) for r in oku("genelleme")}
    for kod, v in ozet["loco"]["XGBoost"].items():
        assert v["ayni"] == pytest.approx(loco[("XGBoost", kod, "Aynı şehir")], abs=6e-4)
        assert v["baska"] == pytest.approx(loco[("XGBoost", kod, "Başka şehir (LOCO)")], abs=6e-4)
    alan = {(r["city"], r["sinif"]): float(r["degisim_pp"]) for r in oku("sinif_alanlari_degisim")}
    for kod, il in ozet["iller"].items():
        for sinif, s in il["sinif"].items():
            assert s["pp"] == pytest.approx(alan[(kod, sinif)], abs=6e-3), (kod, sinif)


def test_hucre_dosyalari_tam(ozet):
    for kod, il in ozet["iller"].items():
        d = json.loads((KOK / "web" / "data" / "hucre" / f"{kod}.json").read_text(encoding="utf-8"))
        assert len(d["i"]) == il["hucre"] == len(d["b24"]), kod
