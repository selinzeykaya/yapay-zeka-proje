"""
Proje genelindeki tüm parametreler burada.
Notebook'lar bu dosyayı `import config` ile okur; bir değeri değiştirmek
için sadece burayı düzenlemek yeterli.
"""

# ---------------------------------------------------------------------------
# Genel
# ---------------------------------------------------------------------------
RANDOM_STATE = 42

# Google Earth Engine için Google Cloud proje kimliği (Project ID).
# Noncommercial, Community tier (aylık 150 EECU-saat)
GEE_PROJECT = "yapay-zeka-proje-2026"
GEE_MONTHLY_EECU_HOURS = 150
PILOT_CITY = "Artvin"              # export'lar önce bu ilde test edilir, kota kullanımı gösterilir
# Pilot sonrası kalan illerin kaba kota tahmini aylık kotanın bu oranını aşarsa otomatik devam edilmez
PILOT_MAX_QUOTA_FRACTION = 0.30
BASEMAP = "Esri.WorldImagery"      # geemap haritaları (OpenStreetMap Colab'da 403 veriyor)

# Colab'da projenin Google Drive'daki yeri
DRIVE_PROJECT_DIR = "/content/drive/MyDrive/yapay-zeka-proje"
GEE_EXPORT_FOLDER = "yapay-zeka-proje-gee"   # GEE export'larının düştüğü Drive klasörü

# ---------------------------------------------------------------------------
# Çalışma alanları (FAO GAUL 2015, level1 = il)
# Anahtar: projede kullandığımız ad, değer: GAUL'daki ADM1_NAME.
# GAUL Türkçe karakter kullanmaz; 00 notebook'u bu adları kontrol eder.
# ---------------------------------------------------------------------------
GAUL_COLLECTION = "FAO/GAUL/2015/level1"
GAUL_COUNTRY = "Turkey"
CITIES = {
    "Istanbul": "Istanbul",
    "Izmir": "Izmir",
    "Artvin": "Artvin",
    "Samsun": "Samsun",
    "Konya": "Konya",
    "Van": "Van",
    "Sanliurfa": "Sanliurfa",
}

# Hangi alt soru hangi şehirleri kullanıyor
SUB_QUESTIONS = {
    "AS1": ["Artvin", "Sanliurfa"],              # orman/bitki kaybı - LST
    "AS2": ["Istanbul", "Izmir"],                # yapılaşma - kentsel ısı adası
    "AS3": ["Konya", "Van", "Samsun"],           # su/sulak alan - sıcaklık, nem
    "AS4": ["Konya", "Sanliurfa"],               # tarım - toprak nemi, LST
    "AS5": list(CITIES.keys()),                  # bölgeler arası genelleme
    "AS6": ["Istanbul", "Izmir"],                # İDA (açık veri seti; Türkiye verisi DEĞİL)
}

# ---------------------------------------------------------------------------
# Zaman
# ---------------------------------------------------------------------------
CHANGE_YEARS = [2014, 2024]        # değişim analizi yılları (2019 kapsam dışı)
LABEL_YEAR = 2021                  # ESA WorldCover v200 yılı = eğitim yılı
SUMMER_START = "06-01"             # Haziran-Ağustos kompoziti
SUMMER_END = "08-31"
MODIS_YEARS = list(range(2003, 2025))   # şehir bazında LST zaman serisi

# ---------------------------------------------------------------------------
# Veri koleksiyonları (GEE kimlikleri)
# ---------------------------------------------------------------------------
COLLECTIONS = {
    "landsat8": "LANDSAT/LC08/C02/T1_L2",
    "landsat9": "LANDSAT/LC09/C02/T1_L2",   # Ekim 2021'den itibaren veri var
    "worldcover": "ESA/WorldCover/v200",     # yalnızca 2021
    "modis_lst": "MODIS/061/MOD11A2",
    "era5_land": "ECMWF/ERA5_LAND/MONTHLY_AGGR",
    "jrc_water": "JRC/GSW1_4/YearlyHistory", # 1984-2021
    "chirps": "UCSB-CHG/CHIRPS/PENTAD",
    "dem": "USGS/SRTMGL1_003",               # rakım (Faz 4 regresyonu için)
}

# Landsat Collection 2 Level-2 ölçek faktörleri
SR_SCALE, SR_OFFSET = 0.0000275, -0.2        # yüzey yansıması
ST_SCALE, ST_OFFSET = 0.00341802, 149.0      # yüzey sıcaklığı (Kelvin)
LANDSAT_SCALE_M = 30
MAX_SCENE_CLOUD = 70               # sahne bulutluluğu %70 üstü olan görüntüler hiç alınmaz

SR_BANDS = ["SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B6", "SR_B7"]
INDICES = ["NDVI", "NDBI", "MNDWI", "NDMI", "SAVI", "BSI"]
FEATURES = SR_BANDS + INDICES     # örnek dosyalarındaki tüm sütunlar
# Landsat'ta NDMI = (NIR-SWIR1)/(NIR+SWIR1) = -NDBI (aynı iki bant, ters işaret) → aynı bilgi.
# Model girdisinde yalnızca NDBI tutulur (Yapılaşma sınıfını doğrudan temsil eder, literatürde yaygın).
# NDMI veri dosyalarında ve Faz 4'teki 1 km nem analizinde kullanılmaya devam eder.
MODEL_FEATURES = [f for f in FEATURES if f != "NDMI"]

# ---------------------------------------------------------------------------
# Sınıflar: WorldCover (11 sınıf) -> projenin 6 sınıfı
# Onaylandı (Faz 1 öncesi). Dışarıda bırakılan sınıfların şehir bazında alan oranı:
# results/tables/worldcover_dislanan_siniflar.csv
# None = örneklemeye alınmaz.
# ---------------------------------------------------------------------------
WORLDCOVER_NAMES = {
    10: "Agac ortusu", 20: "Calilik", 30: "Cayir", 40: "Tarim", 50: "Yapilasma",
    60: "Ciplak/seyrek", 70: "Kar ve buz", 80: "Kalici su", 90: "Otsu sulak alan",
    95: "Mangrov", 100: "Yosun ve liken",
}
MNDWI_WATER_THRESHOLD = 0.0        # MNDWI > 0 → su (2024 su alanı ve JRC karşılaştırması)

CLASSES = {
    0: "Orman",
    1: "Tarim",
    2: "Yapilasma",
    3: "Cayir_Cali",
    4: "Ciplak",
    5: "Su_Sulak",
}
WORLDCOVER_TO_CLASS = {
    10: 0,     # Tree cover            -> Orman
    20: 3,     # Shrubland             -> Çayır/Çalı
    30: 3,     # Grassland             -> Çayır/Çalı
    40: 1,     # Cropland              -> Tarım
    50: 2,     # Built-up              -> Yapılaşma
    60: 4,     # Bare / sparse         -> Çıplak
    70: None,  # Snow and ice          -> dışarıda (yaz kompozitinde çok az)
    80: 5,     # Permanent water       -> Su/Sulak alan
    90: 5,     # Herbaceous wetland    -> Su/Sulak alan
    95: None,  # Mangroves             -> Türkiye'de yok
    100: None, # Moss and lichen       -> dışarıda (çok az)
}

# ---------------------------------------------------------------------------
# Örnekleme
# ---------------------------------------------------------------------------
N_SAMPLES_PER_CITY = 2000          # şehir başına toplam nokta (sınıf dengeli)
MIN_POINT_DISTANCE_M = 300         # noktalar arası min. mesafe (komşu piksel sızıntısı)
OVERSAMPLE_FACTOR = 2              # mesafe filtresi sonrası yeterli nokta kalsın diye fazla örnekle
LABEL_HOMOGENEITY_RADIUS = 1       # 3x3 piksel penceresinde tek WorldCover sınıfı olan pikseller

# ---------------------------------------------------------------------------
# Modelleme (Faz 3 ve 6)
# ---------------------------------------------------------------------------
TRAIN_SIZE, VAL_SIZE, TEST_SIZE = 0.70, 0.15, 0.15
MODELS = ["RandomForest", "XGBoost", "SVM", "MLP"]   # CNN kapsam dışı
SEARCH_N_ITER = 10
SEARCH_CV_FOLDS = 3
SEARCH_SCORING = "f1_macro"

# RandomizedSearchCV arama aralıkları (her modelden n_iter=10 kombinasyon denenir)
PARAM_SPACES = {
    "RandomForest": {
        "n_estimators": [200, 300, 500],
        "max_depth": [None, 10, 20, 30],
        "min_samples_leaf": [1, 2, 4],
        "max_features": ["sqrt", "log2", 0.5],
    },
    "XGBoost": {
        "n_estimators": [200, 400, 600],
        "max_depth": [3, 5, 7, 9],
        "learning_rate": [0.03, 0.05, 0.1, 0.2],
        "subsample": [0.7, 0.85, 1.0],
        "colsample_bytree": [0.6, 0.8, 1.0],
    },
    "SVM": {
        "C": [0.1, 0.3, 1, 3, 10, 30, 100],
        "gamma": ["scale", 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1],
    },
    "MLP": {
        "hidden_layer_sizes": [(64,), (128,), (64, 32), (128, 64)],
        "alpha": [1e-5, 1e-4, 1e-3, 1e-2],
        "learning_rate_init": [1e-3, 3e-3, 1e-2],
    },
}

# ---------------------------------------------------------------------------
# İklim analizi (Faz 4)
# ---------------------------------------------------------------------------
GRID_SIZE_M = 1000
GRID_CRS = "EPSG:3035"             # eşit alanlı projeksiyon (km² hesapları doğru olsun)
# 1 km grid'de nem göstergesi = NDMI (ERA5-Land ~11 km olduğu için grid'de kullanılmaz).
# ERA5-Land toprak nemi yalnızca şehir ölçeğindeki zaman serisinde kullanılır.
GRID_MOISTURE_PROXY = "NDMI"
ERA5_BANDS = ["volumetric_soil_water_layer_1", "temperature_2m"]

# ---------------------------------------------------------------------------
# İDA nesne tespiti (Faz 5)
# ---------------------------------------------------------------------------
IDA_DATASET = "FloW-Img"           # github.com/ORCA-Uboat/FloW-Dataset
YOLO_MODEL = "yolov8n.pt"          # yalnızca YOLOv8n (v8s karşılaştırması kapsam dışı)
YOLO_EPOCHS = 50
YOLO_IMG_SIZE = 640

# ---------------------------------------------------------------------------
# Klasörler (proje köküne göre)
# ---------------------------------------------------------------------------
DATA_RAW = "data/raw"
DATA_PROCESSED = "data/processed"
TABLES_DIR = "results/tables"
FIGURES_DIR = "results/figures"
MODELS_DIR = "results/models"
