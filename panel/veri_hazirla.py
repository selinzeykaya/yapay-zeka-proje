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
    # Faz 07-08: Sentinel-2 + U-Net
    "s2_alt_bolgeler", "s2_veri_ozeti", "unet_metrikleri", "unet_vs_rf", "unet_sinif_bazinda", "unet_il_bazinda",
    "unet_loco", "unet_degisim_ozet", "unet_sinif_dagilimi", "unet_egitim_gecmisi",
]
VERI_DOSYALARI = ["iklim_sehir_yillik"]
RGB_GENISLIK = 900
UNET_GENISLIK = 1800


def jpg_kaydet(png, hedef, genislik):
    im = Image.open(png).convert("RGB")
    if im.width > genislik:
        im = im.resize((genislik, round(im.height * genislik / im.width)), Image.LANCZOS)
    im.save(hedef, quality=82, optimize=True)


def main(kaynak, hedef):
    kaynak, hedef = Path(kaynak), Path(hedef)
    (hedef / "tables").mkdir(parents=True, exist_ok=True)
    (hedef / "lc_maps").mkdir(exist_ok=True)
    (hedef / "rgb").mkdir(exist_ok=True)
    (hedef / "unet").mkdir(exist_ok=True)
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
        jpg_kaydet(png, hedef / "rgb" / f"{png.stem}.jpg", RGB_GENISLIK)
    # U-Net: kutu başına 2017→2025 değişim görseli (unet_degisim_<kutu>.png → <kutu>.jpg) ve özet grafikler
    for png in sorted(fig.glob("unet_degisim_*.png")):
        jpg_kaydet(png, hedef / "unet" / f"{png.stem.removeprefix('unet_degisim_')}.jpg", UNET_GENISLIK)
    for ad in ("unet_vs_rf", "unet_loco", "unet_karisiklik_matrisi", "unet_egitim_egrileri"):
        if (fig / f"{ad}.png").exists():
            jpg_kaydet(fig / f"{ad}.png", hedef / "unet" / f"{ad}.jpg", UNET_GENISLIK)

    toplam = sum(p.stat().st_size for p in hedef.rglob("*") if p.is_file())
    print(f"panel verisi hazır: {hedef} ({toplam / 1e6:.1f} MB)")
    for e in eksik:
        print("UYARI: bulunamadı →", e)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1], Path(__file__).resolve().parent / "veri")
