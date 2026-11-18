"""Web sitesinin verisini hazırlar (web/data/).

Kullanım (proje kökünden):
    python web/veri_hazirla.py <grid_1km_lc_iklim.csv> <tur_adm1.geojson> <tablolar klasörü>
    ör. python web/veri_hazirla.py "<Drive>/data/processed/grid_1km_lc_iklim.csv" tur_adm1.geojson panel/veri/tables

Üretilenler:
    web/data/hucre/<il>.json   1 km hücreler (sütunlu: hücre numarası + değerler; köşeler tarayıcıda proj4js ile)
    web/data/iller.json        7 çalışma ilinin sınırı + Türkiye'nin 81 il sınırı (sadeleştirilmiş)
    web/data/ozet.json         sayı kartları, hipotezler, model sonuçları, iklim serileri, sınıf payları, U-Net (08)
    web/data/unet/<kutu>.jpg   U-Net 2017→2025 değişim görselleri (08 çıktısından, küçültülmüş; elle kopyalanır)
Gerekenler: pandas, numpy.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402

KOK = Path(__file__).resolve().parent
OUT = KOK / "data"
Y0, Y1 = 2014, 2024
ILLER = {"Istanbul": ("İstanbul", "TR-34"), "Izmir": ("İzmir", "TR-35"), "Artvin": ("Artvin", "TR-08"),
         "Samsun": ("Samsun", "TR-55"), "Konya": ("Konya", "TR-42"), "Van": ("Van", "TR-65"),
         "Sanliurfa": ("Şanlıurfa", "TR-63")}
ANA_ODAK = ["Istanbul", "Artvin", "Konya", "Van"]


def yuvarla(x, n):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), n)


def hucreler(grid_csv):
    c = pd.read_csv(grid_csv)
    gecerli = (c[f"lc_valid_{Y0}"] > 0.5) & (c[f"lc_valid_{Y1}"] > 0.5)
    for y in (Y0, Y1):
        lc = c[[f"lc{k}_{y}" for k in range(6)]].to_numpy()
        c[f"b{y}"] = np.where(c[f"lc_valid_{y}"] > 0.5, lc.argmax(axis=1), -1)
    c["dg"] = np.where(~gecerli, -1, np.where(c[f"b{Y0}"] != c[f"b{Y1}"], c[f"b{Y1}"], 9))
    st_ok = (c[f"st_valid_{Y0}"] >= 0.5) & (c[f"st_valid_{Y1}"] >= 0.5)
    c["lst24"] = np.where(c[f"st_valid_{Y1}"] >= 0.5, c[f"LST_{Y1}"], np.nan)
    d_lst = np.where(st_ok, c[f"LST_{Y1}"] - c[f"LST_{Y0}"], np.nan)
    c["dl"] = d_lst - pd.Series(d_lst).groupby(c["city"]).transform("median")      # göreli ΔLST
    c["dn"] = c[f"NDVI_{Y1}"] - c[f"NDVI_{Y0}"]                                       # ΔNDVI
    d_ndmi = c[f"NDMI_{Y1}"] - c[f"NDMI_{Y0}"]
    c["dm"] = d_ndmi - d_ndmi.groupby(c["city"]).transform("median")                  # göreli ΔNDMI
    k0, k1 = c[f"lc2_{Y0}"] > 0.5, c[f"lc2_{Y1}"] > 0.5
    c["yd"] = np.select([~gecerli, k0 & k1, ~k0 & k1, k0 & ~k1], [-1, 2, 1, 3], 0)    # yapılaşma durumu
    w0, w1 = c[f"mndwi_water_{Y0}"], c[f"mndwi_water_{Y1}"]
    c["sd"] = np.select([w0.isna() | w1.isna(), (w0 > 0.5) & (w1 > 0.5), (w0 <= 0.5) & (w1 > 0.5),
                         (w0 > 0.5) & (w1 <= 0.5)], [-1, 2, 1, 3], 0)                 # su durumu
    c["sl"] = np.select([c["wc_80"] > 0.5, c["wc_90"] >= 0.2], [2, 1], 0)             # su / otsu sulak alan (2021)
    c["tp"] = 100 * c[f"lc1_{Y1}"]                                                     # tarım payı 2024 (%)
    c["dtp"] = 100 * (c[f"lc1_{Y1}"] - c[f"lc1_{Y0}"])                                 # tarım payı değişimi (puan)
    c["op"] = 100 * c[f"lc0_{Y1}"]                                                     # orman payı 2024 (%)
    c["yp"] = 100 * c[f"lc2_{Y1}"]                                                     # yapılaşma payı 2024 (%)

    # Sütunlu, kompakt biçim: geometri yerine hücre numarası (i, j) saklanır. Hücre merkezi EPSG:3035'te
    # ((i + x0) + 0.5) * 1000, ((j + y0) + 0.5) * 1000 metre; tarayıcı köşeleri proj4js ile WGS84'e kesin çevirir.
    # Böylece dosyalar ~10 kat küçülür ve kareler analizdeki hücrelerle birebir aynı yerde durur.
    (OUT / "hucre").mkdir(parents=True, exist_ok=True)
    tam = {"b24": f"b{Y1}", "dg": "dg", "yd": "yd", "sd": "sd", "sl": "sl"}
    ondalik = {"lst24": 1, "dl": 1, "dn": 2, "dm": 3, "tp": 0, "dtp": 0, "op": 0, "yp": 0, "elev": 0}
    c["elev"] = c["elevation"]
    boyut = {}
    for kod in ILLER:
        d = c[c["city"] == kod]
        gi = np.floor(d["x"].to_numpy()).astype(int)       # x = 5823.5 → hücre 5823
        gj = np.floor(d["y"].to_numpy()).astype(int)
        x0, y0 = int(gi.min()), int(gj.min())
        veri = {"x0": x0, "y0": y0, "i": (gi - x0).tolist(), "j": (gj - y0).tolist()}
        for k, v in tam.items():
            veri[k] = d[v].astype(int).tolist()
        for k, n in ondalik.items():
            veri[k] = [yuvarla(x, n) for x in d[k].to_numpy()]
            if n == 0:
                veri[k] = [None if x is None else int(x) for x in veri[k]]
        yol = OUT / "hucre" / f"{kod}.json"
        yol.write_text(json.dumps(veri, separators=(",", ":")), encoding="utf-8")
        boyut[kod] = (len(d), yol.stat().st_size / 1e6)
    return c, boyut


def sinirlar(tur_geojson):
    d = json.loads(Path(tur_geojson).read_text(encoding="utf-8"))
    iso2 = {v[1]: k for k, v in ILLER.items()}

    def sade(coords, n=3):          # ~100 m hassasiyet yeter; dosya küçülür
        if isinstance(coords[0], (int, float)):
            return [round(coords[0], n), round(coords[1], n)]
        return [sade(x, n) for x in coords]

    feats = []
    for f in d["features"]:
        iso = f["properties"]["shapeISO"]
        kod = iso2.get(iso)
        feats.append({"type": "Feature",
                      "properties": {"ad": f["properties"]["shapeName"], "il": kod or "",
                                     "calisma": int(kod is not None), "ana": int(kod in ANA_ODAK)},
                      "geometry": {"type": f["geometry"]["type"], "coordinates": sade(f["geometry"]["coordinates"])}})
    (OUT / "iller.json").write_text(json.dumps({"type": "FeatureCollection", "features": feats},
                                               separators=(",", ":"), ensure_ascii=False), encoding="utf-8")


def ozet(c, tablolar):
    T = Path(tablolar)
    oku = lambda ad, **k: pd.read_csv(T / f"{ad}.csv", encoding="utf-8-sig", **k)
    sp = oku("spearman_degisim_iklim")
    alan = oku("sinif_alanlari_degisim")
    uhi = oku("kentsel_isi_adasi")
    su = oku("su_alani_karsilastirma").set_index("city")
    tr = oku("iklim_trend_mann_kendall")
    ik = oku("iklim_sehir_yillik")
    mk = oku("model_karsilastirma", index_col=0)
    iou = oku("sinif_bazinda_iou", index_col=0)
    mb = oku("mekansal_blok_ozet")
    gen = oku("genelleme")
    # Resmi (Colab) değerler önce; yerel tabloda yalnızca resmi tabloda olmayan modeller (XGBoost) alınır ve işaretlenir
    lst_resmi = oku("lst_regresyon_metrikleri").assign(kaynak="Colab (resmi)")
    lst_yerel = oku("lst_regresyon_metrikleri_xgboost_eklendi")
    lst = pd.concat([lst_resmi, lst_yerel[~lst_yerel.model.isin(lst_resmi.model)].assign(kaynak="yerel çalıştırma")])
    shap = oku("lst_regresyon_shap", index_col=0)
    hk = oku("hipotez_kanit_H1_H5")

    def rho(kod, x, y="ΔLST (Landsat)"):
        q = sp[(sp.city == kod) & (sp.degisken == x) & (sp.hedef == y)]
        return round(float(q.spearman_r.iloc[0]), 2)

    def pp(kod, sinif):
        q = alan[(alan.city == kod) & (alan.sinif == sinif)].iloc[0]
        return {"pp": round(float(q.degisim_pp), 2), "y0": round(float(q[f"pay_{Y0}_yuzde"]), 1),
                "y1": round(float(q[f"pay_{Y1}_yuzde"]), 1)}

    def trend(kod, deg):
        q = tr[(tr.city == kod) & (tr.degisken == deg)].iloc[0]
        return {"sen10": round(float(q.sen_egimi_10yil), 3), "p": round(float(q.p), 4)}

    iller = {}
    for kod, (ad, iso) in ILLER.items():
        d = c[c.city == kod]
        u = uhi[(uhi.city == kod) & (uhi.kaynak == "Landsat")].set_index("year")["UHI_C"]
        iller[kod] = {
            "ad": ad, "iso": iso, "ana": kod in ANA_ODAK, "hucre": int(len(d)),
            "bbox": [float(d.lon.min()) - 0.05, float(d.lat.min()) - 0.05, float(d.lon.max()) + 0.05, float(d.lat.max()) + 0.05],
            "lst24_q": [round(float(v), 1) for v in np.nanpercentile(d["lst24"], [5, 25, 50, 75, 95])],
            "rho": {"yapi": rho(kod, "Δyapılaşma"), "orman": rho(kod, "Δorman"), "ndvi": rho(kod, "ΔNDVI"),
                    "su": rho(kod, "Δsu"), "tarim_ndmi": rho(kod, "Δtarım", "ΔNDMI (nem)"),
                    "tarim": rho(kod, "Δtarım")},
            "sinif": {s: pp(kod, s) for s in ["Orman", "Tarim", "Yapilasma", "Cayir_Cali", "Ciplak", "Su_Sulak"]},
            "uhi": {str(k): round(float(v), 2) for k, v in u.items()},
            "su_degisim_yuzde": round(float(su.loc[kod, "mndwi_degisim_yuzde_2014_2024"]), 1),
            "sulak_km2": int((d["sl"] == 1).sum()),
            "trend": {v: trend(kod, v) for v in ["modis_lst_day", "era5_sm_summer", "chirps_precip_annual", "era5_t2m_summer"]},
            "dl_medyan": round(float(np.nanmedian(np.where(
                (d[f"st_valid_{Y0}"] >= 0.5) & (d[f"st_valid_{Y1}"] >= 0.5), d[f"LST_{Y1}"] - d[f"LST_{Y0}"], np.nan))), 2),
            "iklim": {v: [None if pd.isna(x) else round(float(x), 3) for x in ik[ik.city == kod].sort_values("year")[v]]
                      for v in ["modis_lst_day", "era5_sm_summer", "chirps_precip_annual"]},
        }
    yillar = sorted(ik.year.unique().tolist())
    g = gen[gen.duzen.isin(["Aynı şehir", "Başka şehir (LOCO)"])]
    modeller = {m: {"acc": round(float(mk.loc[m, "accuracy"]), 3), "f1": round(float(mk.loc[m, "f1_macro"]), 3),
                    "auc": round(float(mk.loc[m, "roc_auc_ovr_macro"]), 3), "kappa": round(float(mk.loc[m, "kappa"]), 3),
                    "iou": round(float(iou.loc["Ortalama (macro)", m]), 3)} for m in mk.index}
    blok = {r.model: {} for r in mb.itertuples()}
    for r in mb.itertuples():
        blok[r.model][r.bolme] = round(float(r.f1_macro_mean), 3)
    loco = {m: {r.test_city: {"ayni" if r.duzen == "Aynı şehir" else "baska": round(float(r.f1_macro), 3)}
                for r in g[g.model == m].itertuples()} for m in g.model.unique()}
    for m in loco:
        for kod in loco[m]:
            q = g[(g.model == m) & (g.test_city == kod)].set_index("duzen")["f1_macro"]
            loco[m][kod] = {"ayni": round(float(q["Aynı şehir"]), 3), "baska": round(float(q["Başka şehir (LOCO)"]), 3)}
    ndvi_neg = int(hk[(hk.iliski.str.startswith("ΔNDVI")) & (hk.rho < 0)].city.nunique())
    veri = {
        "yillar": yillar, "iller": iller, "modeller": modeller, "blok": blok, "loco": loco,
        "lst_regresyon": {r.model: {"r2": round(float(r.R2_ort), 3), "rmse": round(float(r.RMSE_ort_C), 2),
                                    "mae": round(float(r.MAE_ort_C), 2), "kaynak": r.kaynak} for r in lst.itertuples()},
        "shap": {k: {"deger": round(float(v.ortalama_abs_shap_C), 2), "yon": 1 if v.yon_korelasyonu > 0 else -1}
                 for k, v in shap.iterrows()},
        "iou_sinif": {s: round(float(iou.loc[s, "XGBoost"]), 3) for s in iou.index if s != "Ortalama (macro)"},
        "ndvi_negatif_il": ndvi_neg,
        "loco_ort_dusus": round(float(np.mean([v["ayni"] - v["baska"] for v in loco["XGBoost"].values()])), 3),
    }
    if (T / "unet_metrikleri.csv").exists():
        veri["unet"] = unet_ozet(oku)
    (OUT / "ozet.json").write_text(json.dumps(veri, ensure_ascii=False, indent=1), encoding="utf-8")


def unet_ozet(oku):
    """08'in (Colab, T4 GPU) resmi sonuçları: U-Net ve aynı piksellerde RF, il bazında, LOCO, 2017→2025 değişim."""
    r = lambda x, n=3: None if pd.isna(x) else round(float(x), n)
    vs = oku("unet_vs_rf").set_index("model")
    modeller = {}
    for ad, anahtar in [("U-Net (Sentinel-2)", "unet"), ("Random Forest (piksel, Sentinel-2)", "rf")]:
        s = vs.loc[ad]
        modeller[anahtar] = {"acc": r(s.accuracy), "f1": r(s.f1_macro), "iou": r(s.iou_macro),
                             "iou_sinif": {k: r(s[f"IoU_{k}"]) for k in ["Orman", "Tarim", "Yapilasma", "Cayir_Cali", "Ciplak", "Su_Sulak"]}}
    test = oku("unet_metrikleri", index_col=0).iloc[0]
    il = oku("unet_il_bazinda").set_index("il")
    loco = oku("unet_loco").set_index("il")
    deg = oku("unet_degisim_ozet")
    yil0, yil1 = [c for c in deg.columns if c.isdigit()]
    kutular = oku("s2_alt_bolgeler")
    iller = {}
    for kod in ILLER:
        d = deg[deg.il == kod].set_index("sinif")
        iller[kod] = {
            "f1": r(il.loc[kod, "f1_macro"]), "iou": r(il.loc[kod, "iou_macro"]), "acc": r(il.loc[kod, "accuracy"]),
            "loco": {"ayni": r(loco.loc[kod, "f1_ayni"]), "baska": r(loco.loc[kod, "f1_baska"]), "dusus": r(loco.loc[kod, "dusus_f1"])},
            "degisim": {s: {"y0": r(d.loc[s, yil0], 1), "y1": r(d.loc[s, yil1], 1), "fark": r(d.loc[s, "degisim_km2"], 1)} for s in d.index},
            "uyari": config.UNET_DEGISIM_UYARI.get(kod),
            "kutular": [{"kod": k.kutu, "ad": k.alt_bolge.replace("_", " "), "lat": k.merkez_enlem, "lon": k.merkez_boylam}
                        for k in kutular[kutular.il == kod].itertuples()],
        }
    return {"test": {"acc": r(test.accuracy), "precision": r(test.precision_macro), "recall": r(test.recall_macro),
                     "f1": r(test.f1_macro), "iou": r(test.iou_macro)},
            "modeller": modeller, "iller": iller, "yil0": int(yil0), "yil1": int(yil1),
            "loco_ort_dusus": r(loco["dusus_f1"].mean()), "kutu_km": int(kutular.boyut_km.iloc[0])}


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    c, boyut = hucreler(sys.argv[1])
    sinirlar(sys.argv[2])
    ozet(c, sys.argv[3])
    for k, (n, mb_) in boyut.items():
        print(f"{k:10s} {n:6d} hücre  {mb_:5.2f} MB")
    toplam = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file()) / 1e6
    print(f"web/data toplam: {toplam:.1f} MB")
