"""Google Earth Engine ile ilgili ortak yardımcı fonksiyonlar."""
import os
import shutil
import time

import ee

import config

C = config.COLLECTIONS


# ---------------------------------------------------------------------------
# Bağlantı ve şehir sınırları
# ---------------------------------------------------------------------------
def init_ee(project=None):
    """GEE'ye bağlanır. İlk seferde tarayıcıda giriş ister."""
    project = project or config.GEE_PROJECT
    if project == "BURAYA-PROJE-ID":
        raise ValueError("config.py içindeki GEE_PROJECT değerine kendi Project ID'nizi yazın.")
    try:
        ee.Initialize(project=project)
    except Exception:
        ee.Authenticate()
        ee.Initialize(project=project)
    print(f"Earth Engine hazır (proje: {project})")


def _turkey_gaul():
    return ee.FeatureCollection(config.GAUL_COLLECTION).filter(
        ee.Filter.eq("ADM0_NAME", config.GAUL_COUNTRY)
    )


def get_city_boundaries():
    """7 şehrin GAUL il sınırlarını döndürür; her özelliğe 'city' alanı eklenir."""
    fc = _turkey_gaul().filter(ee.Filter.inList("ADM1_NAME", list(config.CITIES.values())))
    gaul_to_city = ee.Dictionary({v: k for k, v in config.CITIES.items()})
    return fc.map(lambda f: f.set("city", gaul_to_city.get(f.get("ADM1_NAME"))))


def city_geometry(city):
    """Tek bir şehrin sınır geometrisi."""
    return _turkey_gaul().filter(ee.Filter.eq("ADM1_NAME", config.CITIES[city])).geometry()


def list_turkey_provinces():
    """GAUL'daki tüm Türkiye il adlarını listeler (ad eşleşmezse kontrol için)."""
    return sorted(_turkey_gaul().aggregate_array("ADM1_NAME").getInfo())


def make_map(center=(39.0, 35.0), zoom=6):
    """Etkileşimli harita. OpenStreetMap karoları Colab'da 403 verdiği için
    varsayılan arka plan Esri uydu görüntüsü, ek seçenek Google Hybrid."""
    import geemap.foliumap as gf
    try:
        m = gf.Map(center=list(center), zoom=zoom, basemap=config.BASEMAP)
    except Exception:
        m = gf.Map(center=list(center), zoom=zoom)
        m.add_basemap(config.BASEMAP)
    # OSM katmanı yine de eklendiyse kaldır (boş/403 karo göstermesin)
    for key, child in list(m._children.items()):
        if "openstreetmap" in str(getattr(child, "tiles", "")).lower():
            del m._children[key]
    try:
        m.add_basemap("HYBRID")
    except Exception:
        pass
    return m


# ---------------------------------------------------------------------------
# Landsat: bulut maskesi, ölçekleme, indeksler, kompozit
# ---------------------------------------------------------------------------
def mask_and_scale(img):
    """Bulut/gölge/doygun pikselleri maskeler, ölçek faktörlerini uygular.

    QA_PIXEL bitleri: 0 dolgu, 1 genişletilmiş bulut, 2 sirrus, 3 bulut, 4 bulut gölgesi.
    Bu 5 bitten herhangi biri 1 ise piksel atılır. Kar (bit 5) maskelenmez.
    """
    qa = img.select("QA_PIXEL")
    clear = qa.bitwiseAnd(0b11111).eq(0)
    not_saturated = img.select("QA_RADSAT").eq(0)

    sr = img.select(config.SR_BANDS).multiply(config.SR_SCALE).add(config.SR_OFFSET)
    st_raw = img.select("ST_B10")
    lst = (st_raw.multiply(config.ST_SCALE).add(config.ST_OFFSET).subtract(273.15)
           .updateMask(st_raw.gt(0)).rename("LST"))       # ST_B10 = 0 → üretilmemiş
    return (sr.addBands(lst).updateMask(clear).updateMask(not_saturated)
            .copyProperties(img, ["system:time_start"]))


def add_indices(img):
    """Spektral indeksleri ekler (formüller notebook 01'de açıklanıyor)."""
    b = img.select
    ndvi = img.normalizedDifference(["SR_B5", "SR_B4"]).rename("NDVI")
    ndbi = img.normalizedDifference(["SR_B6", "SR_B5"]).rename("NDBI")
    mndwi = img.normalizedDifference(["SR_B3", "SR_B6"]).rename("MNDWI")
    ndmi = img.normalizedDifference(["SR_B5", "SR_B6"]).rename("NDMI")
    savi = img.expression("1.5 * (N - R) / (N + R + 0.5)",
                          {"N": b("SR_B5"), "R": b("SR_B4")}).rename("SAVI")
    bsi = img.expression("((S + R) - (N + B)) / ((S + R) + (N + B))",
                         {"S": b("SR_B6"), "R": b("SR_B4"),
                          "N": b("SR_B5"), "B": b("SR_B2")}).rename("BSI")
    return img.addBands([ndvi, ndbi, mndwi, ndmi, savi, bsi])


def landsat_collection(geom, year):
    """Yaz dönemi (Haz-Ağu) Landsat 8 + 9 görüntüleri, maskelenmiş ve ölçeklenmiş."""
    start = f"{year}-{config.SUMMER_START}"
    end = ee.Date(f"{year}-{config.SUMMER_END}").advance(1, "day")
    col = ee.ImageCollection(C["landsat8"]).merge(ee.ImageCollection(C["landsat9"]))
    return (col.filterBounds(geom).filterDate(start, end)
            .filter(ee.Filter.lt("CLOUD_COVER", config.MAX_SCENE_CLOUD))
            .map(mask_and_scale))


def summer_composite(geom, year):
    """Medyan yaz kompoziti: 6 bant + 6 indeks + LST (°C)."""
    comp = landsat_collection(geom, year).median()
    return add_indices(comp).select(config.FEATURES + ["LST"])


# ---------------------------------------------------------------------------
# Etiket (ESA WorldCover 2021)
# ---------------------------------------------------------------------------
def worldcover():
    return ee.ImageCollection(C["worldcover"]).first().select("Map")


def label_image():
    """WorldCover'ı 6 sınıfa indirir; eşlenmeyen sınıflar maskelenir.

    Ayrıca homojenlik filtresi: komşuluk penceresinde tek bir WorldCover sınıfı
    varsa piksel tutulur (karışık kenar piksellerinden kaçınmak için).
    """
    wc = worldcover()
    codes = [k for k, v in config.WORLDCOVER_TO_CLASS.items() if v is not None]
    values = [config.WORLDCOVER_TO_CLASS[k] for k in codes]
    cls = wc.remap(codes, values).rename("class")
    homogeneous = wc.reduceNeighborhood(
        ee.Reducer.countDistinct(), ee.Kernel.square(config.LABEL_HOMOGENEITY_RADIUS)
    ).eq(1)
    return cls.updateMask(homogeneous).addBands(wc.rename("wc_code"))


# ---------------------------------------------------------------------------
# Drive'a tablo export'u (uzun hesaplamalar için; zaman aşımına uğramaz)
# ---------------------------------------------------------------------------
def start_table_export(fc, name, selectors=None):
    task = ee.batch.Export.table.toDrive(
        collection=fc, description=name, folder=config.GEE_EXPORT_FOLDER,
        fileNamePrefix=name, fileFormat="CSV", selectors=selectors,
    )
    task.start()
    print(f"Export başladı: {name}")
    return task


def wait_for_tasks(tasks, poll_seconds=30):
    """Tüm export görevleri bitene kadar bekler, durumlarını yazdırır.

    Bitince her görevin harcadığı kotayı (EECU-saat) tablo olarak döndürür ve
    results/tables/gee_kota_kullanimi.csv dosyasına ekler. Başarısız görev
    olursa önce kota kaydı yapılır, sonra hata verilir.
    """
    done_states = {"COMPLETED", "FAILED", "CANCELLED"}
    while True:
        states = {n: t.status()["state"] for n, t in tasks.items()}
        n_done = sum(s in done_states for s in states.values())
        print(time.strftime("%H:%M:%S"), f"{n_done}/{len(tasks)} bitti", states)
        if n_done == len(tasks):
            break
        time.sleep(poll_seconds)

    usage = task_usage(tasks)
    log_usage(usage)
    failed = usage[usage["state"] != "COMPLETED"]
    if len(failed):
        raise RuntimeError(f"Başarısız export'lar:\n{failed.to_string()}")
    return usage


def task_usage(tasks):
    """Görev başına durum ve kota kullanımı (EECU-saat)."""
    import pandas as pd
    rows = []
    for name, t in tasks.items():
        s = t.status()
        sec = s.get("batch_eecu_usage_seconds")
        rows.append({
            "zaman": time.strftime("%Y-%m-%d %H:%M"),
            "task": name, "state": s["state"],
            "eecu_saat": None if sec is None else round(float(sec) / 3600, 4),
            "hata": s.get("error_message", ""),
        })
    df = pd.DataFrame(rows)
    df["aylik_kota_yuzde"] = (100 * df["eecu_saat"] / config.GEE_MONTHLY_EECU_HOURS).round(3)
    return df


def log_usage(df, path=None):
    path = path or os.path.join(config.TABLES_DIR, "gee_kota_kullanimi.csv")
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False, encoding="utf-8-sig")


def run_exports(exports, raw_dir, force=False):
    """exports = {ad: (FeatureCollection, sütunlar)}. Var olan dosyaları atlar,
    kalanları başlatır, bekler ve Drive'dan raw_dir'e kopyalar."""
    tasks = {}
    for name, (fc, cols) in exports.items():
        if os.path.exists(os.path.join(raw_dir, f"{name}.csv")) and not force:
            print("zaten var, atlandı:", name)
            continue
        tasks[name] = start_table_export(fc, name, cols)
    if not tasks:
        return None
    usage = wait_for_tasks(tasks)
    for name in tasks:
        fetch_export(name, raw_dir)
    return usage


def fetch_export(name, dest_dir, timeout_seconds=900):
    """Drive'a düşen CSV'yi proje klasörüne kopyalar (Drive senkronu gecikebilir)."""
    src = os.path.join("/content/drive/MyDrive", config.GEE_EXPORT_FOLDER, f"{name}.csv")
    waited = 0
    while not os.path.exists(src):
        if waited >= timeout_seconds:
            raise FileNotFoundError(
                f"{src} Drive'da görünmedi. Birkaç dakika bekleyip bu hücreyi tekrar çalıştırın.")
        time.sleep(15)
        waited += 15
    dest = os.path.join(dest_dir, f"{name}.csv")
    shutil.copy(src, dest)
    return dest
