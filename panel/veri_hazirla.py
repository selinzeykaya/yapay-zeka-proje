"""Panelin verisini hazırlar: Drive'daki proje klasöründen gereken küçük dosyaları panel/veri/ altına kopyalar.

Kullanım (proje kökünden):
    python panel/veri_hazirla.py "<Drive'daki proje klasörü>"
    ör. Colab:  python panel/veri_hazirla.py /content/drive/MyDrive/yapay-zeka-proje
        Yerel:  python panel/veri_hazirla.py "G:/Drive'ım/yapay-zeka-proje"

Kaynak klasörde results/tables, results/figures ve data/processed olmalı.
Uydu görüntüleri (rgb) küçültülüp JPEG'e çevrilir; panel/veri toplamı birkaç MB kalır ve repoya konabilir.
Notebook'lar yeniden çalıştırılıp sonuçlar değişirse bu betik tekrar çalıştırılır.
"""
import shutil
import sys
from pathlib import Path

from PIL import Image

TABLOLAR = [
    "model_karsilastirma", "sinif_bazinda_f1", "sinif_bazinda_iou", "mekansal_blok_ozet",
    "lst_regresyon_metrikleri_xgboost_eklendi", "lst_regresyon_metrikleri", "lst_regresyon_shap",
    "sinif_alanlari_degisim", "gecis_matrisi", "iklim_trend_mann_kendall", "spearman_degisim_iklim",
    "kentsel_isi_adasi", "su_alani_karsilastirma", "genelleme", "genelleme_dusus",
    "genelleme_neden_gostergeleri", "hipotez_kanit_H1_H5", "hipotez_ozet",
]
VERI_DOSYALARI = ["iklim_sehir_yillik"]
RGB_GENISLIK = 900


def main(kaynak, hedef):
    kaynak, hedef = Path(kaynak), Path(hedef)
    (hedef / "tables").mkdir(parents=True, exist_ok=True)
    (hedef / "lc_maps").mkdir(exist_ok=True)
    (hedef / "rgb").mkdir(exist_ok=True)
    eksik = []

    for ad in TABLOLAR:
        src = kaynak / "results" / "tables" / f"{ad}.csv"
        if src.exists():
            shutil.copy2(src, hedef / "tables" / src.name)
        else:
            eksik.append(str(src))
    for ad in VERI_DOSYALARI:
        src = kaynak / "data" / "processed" / f"{ad}.csv"
        if src.exists():
            shutil.copy2(src, hedef / "tables" / src.name)
        else:
            eksik.append(str(src))

    fig = kaynak / "results" / "figures"
    for png in sorted((fig / "lc_maps").glob("*.png")):
        shutil.copy2(png, hedef / "lc_maps" / png.name)
    if (fig / "sehir_sinirlari.png").exists():
        shutil.copy2(fig / "sehir_sinirlari.png", hedef / "sehir_sinirlari.png")
    for png in sorted((fig / "rgb").glob("*.png")):
        im = Image.open(png).convert("RGB")
        if im.width > RGB_GENISLIK:
            im = im.resize((RGB_GENISLIK, round(im.height * RGB_GENISLIK / im.width)), Image.LANCZOS)
        im.save(hedef / "rgb" / f"{png.stem}.jpg", quality=82, optimize=True)

    toplam = sum(p.stat().st_size for p in hedef.rglob("*") if p.is_file())
    print(f"panel verisi hazır: {hedef} ({toplam / 1e6:.1f} MB)")
    for e in eksik:
        print("UYARI: bulunamadı →", e)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1], Path(__file__).resolve().parent / "veri")
