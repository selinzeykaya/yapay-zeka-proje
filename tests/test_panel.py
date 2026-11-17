"""Panel (panel/app.py) her il, gösterge ve model seçiminde hatasız açılıyor mu?
Streamlit'in kendi test aracı (AppTest) kullanılır; tarayıcı açılmaz. Veri: panel/veri/."""
from pathlib import Path

import pytest

st_test = pytest.importorskip("streamlit.testing.v1", reason="streamlit kurulu değil")
# AppTest göreli yolu test dosyasının klasörüne göre çözer; mutlak yol veriyoruz
APP = str(Path(__file__).resolve().parent.parent / "panel" / "app.py")


@pytest.fixture(scope="module")
def panel():
    at = st_test.AppTest.from_file(APP, default_timeout=120).run()
    assert not at.exception, [e.value for e in at.exception]
    return at


def hatasiz(at):
    assert not at.exception, [str(e.value)[:300] for e in at.exception]
    assert not at.error, [e.value for e in at.error]


def test_ilk_acilis_ve_ana_metrikler(panel):
    hatasiz(panel)
    etiketler = [m.label for m in panel.metric]
    assert "Sınıflandırma (XGBoost, macro-F1)" in etiketler
    assert panel.metric[0].value == "0.783"          # resmi Colab sonucu (Faz 3), yerel 0.776 değil


def test_her_il_hatasiz(panel):
    for ad in panel.sidebar.selectbox[0].options:
        panel.sidebar.selectbox[0].select(ad).run()
        hatasiz(panel)


def test_her_iklim_gostergesi_ve_model_hatasiz(panel):
    for ad in panel.main.selectbox[0].options:
        panel.main.selectbox[0].select(ad).run()
        hatasiz(panel)
    for ad in panel.main.radio[0].options:
        panel.main.radio[0].set_value(ad).run()
        hatasiz(panel)
