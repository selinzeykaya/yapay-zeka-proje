"""GeoClimate AI — QGIS haritaları (PyQGIS, ekransız).

Çalıştırma (PowerShell):
    & "<QGIS>\bin\python-qgis-ltr.bat" haritalar.py <grid_1km_lc_iklim.csv> <tur_adm1.geojson> <çıktı> gpkg
    & "<QGIS>\bin\python-qgis-ltr.bat" haritalar.py <grid_1km_lc_iklim.csv> <tur_adm1.geojson> <çıktı> harita
    İki ayrı çalıştırma gerekir: aynı işlemde GeoPackage yazılıp hemen QGIS ile okununca ilk okuma boş dönüyor.
    QT_QPA_PLATFORM=offscreen KULLANMAYIN: yazı tipleri bulunamaz, yazılar kara kutu çıkar.

Üretilenler (çıktı klasöründe):
    geoclimate.gpkg        hucre_1km (1 km kareler, EPSG:3035), iller (7 çalışma ili), turkiye_iller (81 il, geoBoundaries)
    geoclimate.qgz         QGIS projesi: katmanlar, stiller ve 29 baskı düzeni (Proje → Düzen Yöneticisi)
    png/*.png              29 harita (A4 yatay, 150 dpi)
"""
import math
import os
import sys

import numpy as np
import pandas as pd
from osgeo import ogr, osr
from qgis.core import (
    QgsApplication, QgsCategorizedSymbolRenderer, QgsCoordinateReferenceSystem, QgsFillSymbol,
    QgsGraduatedSymbolRenderer, QgsLayerTreeLayer, QgsLayoutExporter, QgsLayoutItemLabel,
    QgsLayoutItemLegend, QgsLayoutItemMap, QgsLayoutItemPicture, QgsLayoutItemScaleBar, QgsLayoutPoint,
    QgsLayoutSize, QgsPalLayerSettings, QgsPrintLayout, QgsProject, QgsRendererCategory, QgsRendererRange,
    QgsSingleSymbolRenderer, QgsTextFormat, QgsUnitTypes, QgsVectorLayer, QgsVectorLayerSimpleLabeling,
    QgsLegendStyle, QgsRectangle, QgsLayoutMeasurement, QgsCoordinateTransform, QgsFeatureRequest,
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor, QFont

GRID_CSV, TUR_GEOJSON, OUT, ADIM = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
assert ADIM in ("gpkg", "harita"), "4. argüman: gpkg ya da harita"
GPKG = os.path.join(OUT, "geoclimate.gpkg")
PNG = os.path.join(OUT, "png")
os.makedirs(PNG, exist_ok=True)

ILLER = {"Istanbul": ("İstanbul", "TR-34"), "Izmir": ("İzmir", "TR-35"), "Artvin": ("Artvin", "TR-08"),
         "Samsun": ("Samsun", "TR-55"), "Konya": ("Konya", "TR-42"), "Van": ("Van", "TR-65"),
         "Sanliurfa": ("Şanlıurfa", "TR-63")}
ANA_ODAK = {"Istanbul", "Artvin", "Konya", "Van"}
SINIF = {0: ("Orman", "#1b7837"), 1: ("Tarım", "#f1a340"), 2: ("Yapılaşma", "#d73027"),
         3: ("Çayır/Çalı", "#a6d96a"), 4: ("Çıplak", "#bababa"), 5: ("Su/Sulak alan", "#4575b4")}
Y0, Y1 = 2014, 2024
KAYNAK = ("Veri: Landsat 8/9 Collection 2 (USGS), etiket ESA WorldCover 2021; sınıflandırma XGBoost (bu çalışma). "
          "İl sınırları: geoBoundaries (CC BY 4.0). Analiz ızgarası ETRS89-LAEA (EPSG:3035); "
          "harita projeksiyonu: Türkiye Lambert konik konform (GRS80). "
          "Hücre 1 km; sınıf payları hücre başına 9 noktadan. Analizde il sınırı FAO GAUL olduğundan "
          "hücreler kenarlarda geoBoundaries sınırından birkaç yüz metre taşabilir.")

# ------------------------------------------------------------------ 1) veri ve türetilen alanlar
c = pd.read_csv(GRID_CSV)
lc = {y: c[[f"lc{k}_{y}" for k in range(6)]].to_numpy() for y in (Y0, Y1)}
for y in (Y0, Y1):
    ok = c[f"lc_valid_{y}"] > 0.5
    c[f"baskin_{y}"] = np.where(ok, lc[y].argmax(axis=1), -1)
gecerli = (c[f"baskin_{Y0}"] >= 0) & (c[f"baskin_{Y1}"] >= 0)
c["degisim"] = np.where(~gecerli, -1, np.where(c[f"baskin_{Y0}"] != c[f"baskin_{Y1}"], c[f"baskin_{Y1}"], 9))
st_ok = (c[f"st_valid_{Y0}"] >= 0.5) & (c[f"st_valid_{Y1}"] >= 0.5)
c["d_lst"] = np.where(st_ok, c[f"LST_{Y1}"] - c[f"LST_{Y0}"], np.nan)
# Göreli ΔLST: iki yaz arasındaki genel hava farkı il medyanı çıkarılarak giderilir (Spearman ile aynı mantık)
c["d_lst_goreli"] = c["d_lst"] - c.groupby("city")["d_lst"].transform("median")
c["d_ndvi"] = c[f"NDVI_{Y1}"] - c[f"NDVI_{Y0}"]
c["d_yapi_pp"] = 100 * (c[f"lc2_{Y1}"] - c[f"lc2_{Y0}"])

# ------------------------------------------------------------------ 2) GeoPackage (OGR)
if ADIM == "gpkg":
    if os.path.exists(GPKG):
        os.remove(GPKG)
    srs = osr.SpatialReference(); srs.ImportFromEPSG(3035)
    ds = ogr.GetDriverByName("GPKG").CreateDataSource(GPKG)
    lyr = ds.CreateLayer("hucre_1km", srs, ogr.wkbPolygon, options=["SPATIAL_INDEX=YES"])
    alanlar = [("il", ogr.OFTString), ("il_adi", ogr.OFTString), ("elevation", ogr.OFTReal),
               (f"baskin_{Y0}", ogr.OFTInteger), (f"baskin_{Y1}", ogr.OFTInteger), ("degisim", ogr.OFTInteger),
               (f"LST_{Y0}", ogr.OFTReal), (f"LST_{Y1}", ogr.OFTReal), ("d_lst", ogr.OFTReal), ("d_lst_goreli", ogr.OFTReal),
               (f"NDVI_{Y0}", ogr.OFTReal), (f"NDVI_{Y1}", ogr.OFTReal), ("d_ndvi", ogr.OFTReal), ("d_yapi_pp", ogr.OFTReal)]
    alanlar += [(f"lc{k}_{y}", ogr.OFTReal) for y in (Y0, Y1) for k in range(6)]
    for ad, tip in alanlar:
        lyr.CreateField(ogr.FieldDefn(ad, tip))
    defn = lyr.GetLayerDefn()
    ds.StartTransaction()
    kaynak = {"il": "city", "il_adi": None}
    for r in c.itertuples(index=False):
        f = ogr.Feature(defn)
        for ad, _ in alanlar:
            if ad == "il":
                f.SetField(ad, r.city)
            elif ad == "il_adi":
                f.SetField(ad, ILLER[r.city][0])
            else:
                v = getattr(r, ad)
                if v is not None and not (isinstance(v, float) and math.isnan(v)):
                    f.SetField(ad, float(v) if isinstance(v, float) else int(v))
        x, y = r.x * 1000, r.y * 1000          # hücre merkezi (EPSG:3035, metre)
        ring = ogr.Geometry(ogr.wkbLinearRing)
        for dx, dy in [(-500, -500), (500, -500), (500, 500), (-500, 500), (-500, -500)]:
            ring.AddPoint_2D(x + dx, y + dy)
        poly = ogr.Geometry(ogr.wkbPolygon); poly.AddGeometry(ring)
        f.SetGeometry(poly)
        lyr.CreateFeature(f)
    ds.CommitTransaction()

    # İl sınırları: geoBoundaries'ten 7 il (analizdeki il sınırlarıyla aynı idari birimler), EPSG:3035'e çevrilir
    tur = ogr.Open(TUR_GEOJSON)
    tl = tur.GetLayer()
    wgs = osr.SpatialReference(); wgs.ImportFromEPSG(4326); wgs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    tr = osr.CoordinateTransformation(wgs, srs)
    out_tur = ds.CreateLayer("turkiye_iller", srs, ogr.wkbMultiPolygon)
    out_il = ds.CreateLayer("iller", srs, ogr.wkbMultiPolygon)
    for L in (out_tur, out_il):
        for ad in ("ad", "iso", "il", "ana_odak"):
            L.CreateField(ogr.FieldDefn(ad, ogr.OFTInteger if ad == "ana_odak" else ogr.OFTString))
    iso2il = {v[1]: k for k, v in ILLER.items()}
    for ft in tl:
        g = ft.GetGeometryRef().Clone(); g.Transform(tr)
        g = ogr.ForceToMultiPolygon(g)
        iso = ft.GetField("shapeISO")
        for L in ([out_tur] + ([out_il] if iso in iso2il else [])):
            nf = ogr.Feature(L.GetLayerDefn())
            nf.SetField("ad", ft.GetField("shapeName")); nf.SetField("iso", iso)
            if iso in iso2il:
                nf.SetField("il", iso2il[iso]); nf.SetField("ana_odak", int(iso2il[iso] in ANA_ODAK))
            nf.SetGeometry(g); L.CreateFeature(nf)
    # Bütün OGR başvurularını bırak: dosya ancak hepsi kapanınca diske tam yazılır (uzamsal dizin dahil).
    # Aksi halde QGIS ilk okumada yarım dosya görüp boş katman döndürüyor.
    del lyr, out_tur, out_il, tl, defn, f, ft, nf, L
    ds = None; tur = None
    import gc; gc.collect()
    print("GeoPackage hazır:", GPKG, f"({len(c)} hücre)")
    sys.exit(0)

# ------------------------------------------------------------------ 3) QGIS
QgsApplication.setPrefixPath(os.environ.get("QGIS_PREFIX_PATH")
                             or r"D:\D_SenaOz\Program File\QGIS 3.44.15\apps\qgis-ltr", True)
app = QgsApplication([], False); app.initQgis()
prj = QgsProject.instance()
# Harita projeksiyonu: Türkiye merkezli Lambert konik konform. EPSG:3035 (Avrupa LAEA) Türkiye'yi döndürüp bozar;
# veri EPSG:3035'te kalır, QGIS çizimde dönüştürür.
TR = QgsCoordinateReferenceSystem.fromProj("+proj=lcc +lat_0=39 +lon_0=35 +lat_1=37 +lat_2=41 +x_0=0 +y_0=0 "
                                           "+ellps=GRS80 +units=m +no_defs")
assert TR.isValid()
prj.setCrs(TR)
LAEA = QgsCoordinateReferenceSystem("EPSG:3035")
prj.setTitle("GeoClimate AI — haritalar")


BEKLENEN_ALAN = {"hucre_1km": f"baskin_{Y1}", "iller": "il", "turkiye_iller": "iso"}


def katman(ad, tablo, filtre=None, ekle=True):
    # IMMUTABLE=YES: GeoPackage salt okunur açılır, yanına WAL günlük dosyaları (-wal/-shm) oluşturulmaz.
    # Bu olmadan aynı dosyaya açılan ikinci bağlantının ilk okuması "unable to open database file" ile boş
    # dönüyor ve ilk harita boş çıkıyordu. Haritalar yalnızca okuma yaptığı için salt okunur yeterli.
    # Döngü güvenlik içindir: katmanın sütunları ve en az bir hücresi gerçekten okunabiliyor mu?
    for deneme in range(5):
        v = QgsVectorLayer(f"{GPKG}|layername={tablo}|option:IMMUTABLE=YES", ad, "ogr")
        if filtre:
            v.setSubsetString(filtre)
        ilk = next(v.getFeatures(QgsFeatureRequest().setLimit(1)), None) if v.isValid() else None
        if ilk is not None and v.fields().indexOf(BEKLENEN_ALAN[tablo]) >= 0:
            break
        print(f"katman okunamadı, yeniden deneniyor ({deneme + 1}): {ad}")
    else:
        raise RuntimeError(f"katman açılamadı: {ad}")
    if ekle:
        prj.addMapLayer(v)
    return v


def dolgu(renk, cizgi="no", cizgi_renk="#000000", genislik="0.2"):
    return QgsFillSymbol.createSimple({"color": renk, "outline_style": "solid" if cizgi != "no" else "no",
                                       "outline_color": cizgi_renk, "outline_width": genislik})


def sinif_stili(v, alan, degisim=False):
    kat = []
    if degisim:
        kat.append(QgsRendererCategory(9, dolgu("#e6e6e6"), "Değişmedi"))
    for k, (ad, renk) in SINIF.items():
        kat.append(QgsRendererCategory(k, dolgu(renk), ("→ " + ad) if degisim else ad))
    kat.append(QgsRendererCategory(-1, dolgu("#ffffff", "solid", "#cccccc", "0.05"), "Veri yok (bulut vb.)"))
    v.setRenderer(QgsCategorizedSymbolRenderer(alan, kat))


def kademeli_stil(v, alan, sinirlar, renkler, etiketler):
    araliklar = [QgsRendererRange(lo, hi, dolgu(r), e) for (lo, hi), r, e in zip(sinirlar, renkler, etiketler)]
    v.setRenderer(QgsGraduatedSymbolRenderer(alan, araliklar))


def sinir_stili(v, kalin="0.6", renk="#222222"):
    v.setRenderer(QgsSingleSymbolRenderer(QgsFillSymbol.createSimple(
        {"color": "0,0,0,0", "outline_color": renk, "outline_width": kalin})))


def yazi(layout, metin, x, y, w, h, boyut, kalin=False, renk="#000000"):
    lab = QgsLayoutItemLabel(layout)
    lab.setText(metin)
    fmt = QgsTextFormat(); f = QFont("Arial"); f.setBold(kalin); fmt.setFont(f); fmt.setSize(boyut)
    fmt.setColor(QColor(renk)); lab.setTextFormat(fmt)
    lab.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
    lab.attemptResize(QgsLayoutSize(w, h, QgsUnitTypes.LayoutMillimeters))
    lab.setMode(QgsLayoutItemLabel.ModeFont)
    layout.addLayoutItem(lab)
    return lab


KUZEY = next((os.path.join(p, "arrows", "NorthArrow_02.svg") for p in QgsApplication.svgPaths()
              if os.path.exists(os.path.join(p, "arrows", "NorthArrow_02.svg"))), None)


def duzen(ad, baslik, alt_baslik, katmanlar, lejant_katmanlari, kapsam, not_metni=""):
    lay = QgsPrintLayout(prj); lay.initializeDefaults(); lay.setName(ad)
    pg = lay.pageCollection().page(0); pg.setPageSize("A4", pg.Landscape)    # 297 × 210 mm
    yazi(lay, baslik, 10, 7, 277, 10, 16, kalin=True)
    yazi(lay, alt_baslik, 10, 16, 277, 7, 10, renk="#444444")
    m = QgsLayoutItemMap(lay)
    m.attemptMove(QgsLayoutPoint(10, 25, QgsUnitTypes.LayoutMillimeters))
    m.attemptResize(QgsLayoutSize(200, 165, QgsUnitTypes.LayoutMillimeters))
    m.setLayers(katmanlar); m.setKeepLayerSet(True)
    m.setCrs(TR)
    k = QgsCoordinateTransform(LAEA, TR, prj).transformBoundingBox(kapsam); k.scale(1.06)
    m.zoomToExtent(k)
    m.setFrameEnabled(True)
    lay.addLayoutItem(m)
    lg = QgsLayoutItemLegend(lay); lg.setLinkedMap(m); lg.setAutoUpdateModel(False)
    kok = lg.model().rootGroup(); kok.removeAllChildren()
    for L, ad_ in lejant_katmanlari:
        node = kok.addLayer(L); node.setName(ad_)
    lg.setTitle("Lejant")
    for stil, boyut, kalin in [(QgsLegendStyle.Title, 12, True), (QgsLegendStyle.Group, 10, True),
                               (QgsLegendStyle.Subgroup, 9, True), (QgsLegendStyle.SymbolLabel, 8, False)]:
        tf = lg.rstyle(stil).textFormat(); fnt = QFont("Arial"); fnt.setBold(kalin)
        tf.setFont(fnt); tf.setSize(boyut); lg.rstyle(stil).setTextFormat(tf)
    lg.setSymbolWidth(6); lg.setSymbolHeight(4)
    lg.attemptMove(QgsLayoutPoint(215, 25, QgsUnitTypes.LayoutMillimeters))
    lay.addLayoutItem(lg)
    sb = QgsLayoutItemScaleBar(lay); sb.setStyle("Single Box"); sb.setLinkedMap(m)
    sb.setUnits(QgsUnitTypes.DistanceKilometers); sb.setUnitLabel("km"); sb.setNumberOfSegments(4)
    sb.setNumberOfSegmentsLeft(0); sb.applyDefaultSize(QgsUnitTypes.DistanceKilometers)
    sb.attemptMove(QgsLayoutPoint(12, 177, QgsUnitTypes.LayoutMillimeters))
    lay.addLayoutItem(sb)
    if KUZEY:
        n = QgsLayoutItemPicture(lay); n.setPicturePath(KUZEY)
        n.attemptMove(QgsLayoutPoint(195, 28, QgsUnitTypes.LayoutMillimeters))
        n.attemptResize(QgsLayoutSize(12, 12, QgsUnitTypes.LayoutMillimeters))
        lay.addLayoutItem(n)
    yazi(lay, (not_metni + "\n" if not_metni else "") + KAYNAK, 215, 150, 75, 45, 7, renk="#555555")
    prj.layoutManager().addLayout(lay)
    ayar = QgsLayoutExporter.ImageExportSettings(); ayar.dpi = 150
    sonuc = QgsLayoutExporter(lay).exportToImage(os.path.join(PNG, f"{ad}.png"), ayar)
    if sonuc != QgsLayoutExporter.Success:
        print("UYARI: dışa aktarılamadı:", ad, sonuc)
    return lay


# ortak katmanlar
tur = katman("Türkiye il sınırları", "turkiye_iller")
tur.setRenderer(QgsSingleSymbolRenderer(dolgu("#f2f2f2", "solid", "#9e9e9e", "0.15")))
iller = katman("Çalışma illeri", "iller")
iller.setRenderer(QgsCategorizedSymbolRenderer("ana_odak", [
    QgsRendererCategory(1, dolgu("#08519c", "solid", "#08306b", "0.4"), "Ana odak (GeoClimate)"),
    QgsRendererCategory(0, dolgu("#6baed6", "solid", "#08306b", "0.4"), "Karşılaştırma ili")]))
etiket = QgsPalLayerSettings(); etiket.fieldName = "ad"
fmt = QgsTextFormat(); fmt.setFont(QFont("Arial")); fmt.setSize(9); fmt.buffer().setEnabled(True)
etiket.setFormat(fmt); iller.setLabeling(QgsVectorLayerSimpleLabeling(etiket)); iller.setLabelsEnabled(True)

# 0) genel bakış
duzen("00_calisma_alanlari", "GeoClimate AI — çalışma alanları",
      "7 il: kent (İstanbul, İzmir), orman (Artvin), delta (Samsun), kurak tarım (Konya, Şanlıurfa), göl havzası (Van)",
      [iller, tur], [(iller, "Çalışma illeri")], tur.extent())

LST_SINIR = [(-99, -3), (-3, -1.5), (-1.5, -0.5), (-0.5, 0.5), (0.5, 1.5), (1.5, 3), (3, 99)]
LST_RENK = ["#2166ac", "#67a9cf", "#d1e5f0", "#f7f7f7", "#fddbc7", "#ef8a62", "#b2182b"]
LST_ETIKET = ["≤ −3 °C (görece soğudu)", "−3 … −1,5", "−1,5 … −0,5", "−0,5 … +0,5 (il geneliyle aynı)",
              "+0,5 … +1,5", "+1,5 … +3", "≥ +3 °C (görece ısındı)"]
NDVI_SINIR = [(-2, -0.15), (-0.15, -0.05), (-0.05, 0.05), (0.05, 0.15), (0.15, 2)]
NDVI_RENK = ["#a6611a", "#dfc27d", "#f5f5f5", "#80cdc1", "#018571"]
NDVI_ETIKET = ["≤ −0,15 (bitki azaldı)", "−0,15 … −0,05", "−0,05 … +0,05 (değişmedi)", "+0,05 … +0,15",
               "≥ +0,15 (bitki arttı)"]

for i, (kod, (ad, _)) in enumerate(ILLER.items(), start=1):
    f = f"\"il\" = '{kod}'"
    sinir = katman(f"{ad} sınırı", "iller", f, ekle=True); sinir_stili(sinir)
    kapsam = sinir.extent()
    yildiz = " ★" if kod in ANA_ODAK else ""

    b = katman(f"{ad} — {Y1} baskın arazi örtüsü", "hucre_1km", f); sinif_stili(b, f"baskin_{Y1}")
    duzen(f"{i:02d}a_{kod}_arazi_{Y1}", f"{ad}{yildiz} — {Y1} arazi örtüsü",
          "Her 1 km hücrede en çok rastlanan sınıf (9 noktadan)", [sinir, b], [(b, "Baskın sınıf")], kapsam)

    d = katman(f"{ad} — değişim {Y0}→{Y1}", "hucre_1km", f); sinif_stili(d, "degisim", degisim=True)
    duzen(f"{i:02d}b_{kod}_degisim", f"{ad}{yildiz} — arazi örtüsü değişimi {Y0} → {Y1}",
          "Baskın sınıfı değişen hücreler, 2024'teki yeni sınıfın rengiyle", [sinir, d],
          [(d, "Yeni sınıf")], kapsam,
          "Not: 2014 ve 2024 haritalarının doğruluğu ölçülemiyor (etiket yalnızca 2021); küçük değişimleri temkinli yorumlayın.")

    t = katman(f"{ad} — göreli ΔLST", "hucre_1km", f)
    kademeli_stil(t, "d_lst_goreli", LST_SINIR, LST_RENK, LST_ETIKET)
    med = c.loc[c["city"] == kod, "d_lst"].median()
    duzen(f"{i:02d}c_{kod}_lst_degisim", f"{ad}{yildiz} — yüzey sıcaklığı değişimi (göreli ΔLST)",
          f"Landsat yaz LST farkı {Y0}→{Y1}, il medyanına göre (il medyanı: {med:+.1f} °C)", [sinir, t],
          [(t, "Göreli ΔLST")], kapsam,
          "Göreli ΔLST = hücrenin ΔLST'si − ilin medyan ΔLST'si. İki yazın genel hava farkını giderir; "
          "il içinde hangi alanların görece ısındığını gösterir.")

    n = katman(f"{ad} — ΔNDVI", "hucre_1km", f)
    kademeli_stil(n, "d_ndvi", NDVI_SINIR, NDVI_RENK, NDVI_ETIKET)
    duzen(f"{i:02d}d_{kod}_ndvi_degisim", f"{ad}{yildiz} — bitki örtüsü değişimi (ΔNDVI)",
          f"Landsat yaz NDVI farkı {Y0}→{Y1}", [sinir, n], [(n, "ΔNDVI")], kapsam,
          "ΔNDVI ile ΔLST 7 ilin hepsinde negatif ilişkili (Spearman ρ −0,41 … −0,65): bitki azalan yerler görece ısınıyor (H2).")
    print("bitti:", ad, flush=True)

prj.write(os.path.join(OUT, "geoclimate.qgz"))
print("proje:", os.path.join(OUT, "geoclimate.qgz"), "| düzen sayısı:", len(prj.layoutManager().layouts()))
app.exitQgis()
