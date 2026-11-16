"""src/ modülleri içe aktarılabiliyor mu ve notebook'ların çağırdığı her fonksiyon gerçekten tanımlı mı?

Selin'in kontrol.yml'sindeki "gee_utils içe aktarılabiliyor mu" kontrolü buraya taşındı ve genişletildi:
notebook'larda geçen her `gu.<ad>` (gee_utils) ve `mu.<ad>` (ml_utils) çağrısı modülde var mı?
Böylece src/ içinde bir fonksiyonun adı değişip notebook güncellenmezse CI kırmızı olur.
Earth Engine'e bağlanılmaz (ee.Initialize çağrılmaz); yalnızca kütüphane içe aktarılır.
"""
import glob
import json
import re

import pytest

from src import ml_utils


def notebook_cagrilari(kisaltma):
    """Notebook kod hücrelerinde `kisaltma.ad` biçimindeki bütün çağrı adlarını döndürür."""
    adlar = set()
    for path in glob.glob("notebooks/*.ipynb"):
        with open(path, encoding="utf-8") as f:
            nb = json.load(f)
        for cell in nb["cells"]:
            if cell["cell_type"] == "code":
                adlar |= set(re.findall(rf"\b{kisaltma}\.(\w+)", "".join(cell["source"])))
    return adlar


def test_gee_utils_ice_aktarilir_ve_notebook_cagrilari_tanimli():
    pytest.importorskip("ee", reason="earthengine-api kurulu değil (CI'da kurulu)")
    from src import gee_utils
    eksik = sorted(a for a in notebook_cagrilari("gu") if not hasattr(gee_utils, a))
    assert not eksik, f"notebook'lar gee_utils'te olmayan fonksiyon çağırıyor: {eksik}"
    assert callable(gee_utils.init_ee)


def test_ml_utils_notebook_cagrilari_tanimli():
    eksik = sorted(a for a in notebook_cagrilari("mu") if not hasattr(ml_utils, a))
    assert not eksik, f"notebook'lar ml_utils'te olmayan fonksiyon çağırıyor: {eksik}"
