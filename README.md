# Türkiye'de Coğrafi Değişimlerin İklimsel Etkilerinin Uydu Görüntüleriyle Yapay Zekâ Destekli Analizi

[![CI](https://github.com/selinzeykaya/yapay-zeka-proje/actions/workflows/ci.yml/badge.svg)](https://github.com/selinzeykaya/yapay-zeka-proje/actions/workflows/ci.yml)

Yapay Zekâ dersi projesi. Türkiye'deki 7 ilde (İstanbul, İzmir, Artvin, Samsun, Konya, Van, Şanlıurfa) arazi örtüsü değişimini makine öğrenmesiyle sınıflandırıyoruz. Bu değişimin yüzey sıcaklığı (LST) ve nem göstergeleriyle ilişkisini inceliyoruz.

> **Kapsam notu:** İDA (insansız deniz aracı) modülü kapsamdan çıkarıldı. Deniz yüzeyinde atık tespiti, arazi örtüsü değişimi ile iklimsel göstergeler arasındaki ilişkiyi doğrudan test etmiyor; ayrıca İstanbul/İzmir kıyılarına ait İDA görüntüsü yok (önceki deneme Endonezya nehir veri setiyleydi). Eski 05 notebook'u ve sonuçları git geçmişinde duruyor. Notebook numaralarında 05 bu yüzden boştur.

## Klasör yapısı
```
config.py            Tüm parametreler (şehirler, yıllar, sınıflar, model ayarları)
requirements.txt     Paketler
notebooks/           Colab notebook'ları (00 → 06 sırasıyla çalıştırılır)
src/                 Notebook'ların ortak fonksiyonları
data/raw, processed  Veri (büyük dosyalar GitHub'a yüklenmez)
results/             tables/ (CSV), figures/ (PNG/HTML), models/
literature/          Literatür matrisi ve aday çalışmalar
report/              Rapor iskeleti ve sınırlılık notları
presentation/        Sunum iskeleti ve olası sorular
```

## Notebook'lar
| # | Notebook | Ne yapar |
|---|---|---|
| 00 | `00_kurulum_erisim_kontrolu` | GEE girişi, şehir sınırları haritası, veri erişim testi |
| 01 | `01_veri_toplama_gee` | Landsat kompozitleri, örnek noktalar, iklim serileri |
| 02 | `02_eda_tanimlayici_istatistik` | Veri tanıtımı, tanımlayıcı istatistik, grafikler |
| 03 | `03_siniflandirma_modelleri` | RF, XGBoost, SVM, MLP; Accuracy/Precision/Recall/F1/ROC-AUC |
| 04 | `04_degisim_ve_iklim_analizi` | 2014→2024 değişim, LST/nem ilişkisi, kentsel ısı adası |
| 06 | `06_bolgeler_arasi_genelleme` | Leave-One-City-Out |

## Nasıl çalıştırılır (Google Colab)

### 1. Google Earth Engine kaydı (bir kez)
1. https://code.earthengine.google.com/register adresine Google hesabınızla girin.
2. **Use without a Cloud Project** değil, **Register a Noncommercial or Commercial Cloud project** seçin.
3. Kullanım türü olarak **Unpaid usage → Academia & Research** seçin.
4. **Create a new Google Cloud Project** seçin ve bir Project ID yazın (ör. `yapay-zeka-proje-<sayılar>`).
5. Devam edip onaylayın. Fatura hesabı istenmez.
6. Project ID'yi `config.py` içindeki `GEE_PROJECT` satırına yazın.

### 2. Kod nerede, sonuçlar nerede?
- **Kod:** Özel GitHub reposu `selinzeykaya/yapay-zeka-proje`. Notebook'lar GitHub'dan açılır. İlk hücre repoyu Colab'ın geçici diskine (`/content/yapay-zeka-proje`) klonlar ya da günceller.
- **Veri ve sonuçlar:** Google Drive → `Drive'ım/yapay-zeka-proje/` (`data/`, `results/`). İlk çalıştırmada otomatik oluşturulur.
- **GEE export'ları:** Drive → `Drive'ım/yapay-zeka-proje-gee/`. Ara dosyalardır, notebook bunları otomatik olarak `data/raw/gee/` altına kopyalar.

### 3. Colab kurulumu (bir kez)
1. GitHub'da okuma yetkili bir **fine-grained token** oluşturun: Settings → Developer settings → Fine-grained tokens. Yalnızca bu repo, Contents: Read-only.
2. Colab'da sol menüdeki **anahtar simgesi (Secrets)** → **Yeni gizli anahtar ekle**. Ad: `GITHUB_TOKEN`, değer: token. **Not defteri erişimi** anahtarını açın.

### 4. Çalıştırma
Colab → **Dosya → Not defteri aç → GitHub** sekmesi → "Özel depoları dahil et" kutusunu işaretleyin → `selinzeykaya/yapay-zeka-proje` → notebook'u seçin. Sonra **Çalışma zamanı → Tümünü çalıştır** deyin. Sırayla 00, 01, 02... çalıştırın.

GitHub'dan açılan notebook'taki değişiklikler (çıktılar dahil) otomatik kaydedilmez. Sonuçlar zaten Drive'a yazıldığı için bu sorun değil.

## Sonuç paneli (Streamlit)
Notebook'ların ürettiği sonuçları tek ekranda gösteren etkileşimli panel: `panel/app.py`. Hiçbir şey hesaplamaz, Earth Engine'e bağlanmaz.

```bash
pip install -r panel/requirements.txt
streamlit run panel/app.py        # tarayıcıda http://localhost:8501
```

Sekmeler: **Genel bakış** (ana sayılar) · **Arazi değişimi** (il il 2014/2024 haritaları, sınıf payları, geçiş matrisi) · **İklim** (2003–2024 serileri, Mann-Kendall trendleri) · **İlişkiler ve hipotezler** (H1–H6, ısı adası, su alanı) · **Model başarısı** (4 model, IoU, mekânsal blok, LOCO, LST regresyonu ve SHAP).

Veri `panel/veri/` altındadır (≈5 MB, yalnızca özet tablolar ve küçültülmüş görseller). Notebook'lar yeniden çalıştırılıp sonuçlar değişirse: `python panel/veri_hazirla.py "<Drive'daki yapay-zeka-proje klasörü>"`.

## Otomatik kontrol (GitHub Actions)
Her push'ta ve `main`'e açılan her Pull Request'te `.github/workflows/ci.yml` çalışır (≈1–2 dk):
1. `tools/notebook_kontrol.py`: notebook'lar geçerli mi, kod hücrelerinde yazım hatası var mı, **çıktı kaydedilmiş mi** (repo çıktısız notebook tutar).
2. `pytest` (`tests/`): `config.py` tutarlılığı, `src/ml_utils.py` metrikleri (IoU = F1/(2−F1) dahil), 4 modelin kurulup eğitilebilmesi, `src/gee_utils.py`'nin içe aktarılabilmesi ve notebook'larda çağrılan her `gu.*` / `mu.*` fonksiyonunun tanımlı olması; panelin her il, gösterge ve model seçiminde hatasız açılması.

Earth Engine ve Drive verisi gerektiren analizler CI'da çalışmaz. Yerelde aynı kontrol: `pip install -r requirements-ci.txt` → `python tools/notebook_kontrol.py` → `pytest`.
Kırmızı (❌) olursa: Actions sekmesinde hangi adımın düştüğüne bakın; en sık neden Colab'dan **çıktılı** notebook commit'lemek (Colab → Düzenle → Tüm çıktıları temizle).

## Veri kaynakları ve lisanslar
| Veri | Kaynak (GEE kimliği) | Not |
|---|---|---|
| İl sınırları | `FAO/GAUL/2015/level1` | FAO GAUL; ticari olmayan kullanım |
| Landsat 8/9 C2 L2 | `LANDSAT/LC08/C02/T1_L2`, `LANDSAT/LC09/C02/T1_L2` | USGS, kamu malı |
| Arazi örtüsü etiketi | `ESA/WorldCover/v200` | Yalnızca 2021; CC BY 4.0 |
| Yüzey sıcaklığı | `MODIS/061/MOD11A2` | NASA LP DAAC, kamu malı |
| Toprak nemi, hava sıcaklığı | `ECMWF/ERA5_LAND/MONTHLY_AGGR` | Copernicus lisansı; ~11 km, yalnızca şehir ölçeğinde |
| Su yüzeyi | `JRC/GSW1_4/YearlyHistory` | 1984–2021; 2024 için Landsat MNDWI |
| Yağış | `UCSB-CHG/CHIRPS/PENTAD` | Kamu malı |
| Rakım | `USGS/SRTMGL1_003` | NASA/USGS, kamu malı |

## Tekrarlanabilirlik
Her yerde `RANDOM_STATE = 42` kullanılır. Bütün parametreler `config.py` dosyasındadır.
