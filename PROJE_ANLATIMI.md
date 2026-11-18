# GeoClimate AI — Projenin baştan sona anlatımı

> Bu belge projenin **ne yaptığını, nasıl ve neden yaptığını** baştan sona anlatır: veri toplamadan modellere,
> değişim ve iklim analizinden haritalara, panele ve web sitesine kadar. Her bölümde *ne yapıldı → nasıl → neden → sonuç* sırası izlenir.
> Son bölümde her parçanın **nasıl çalıştırılacağı** adım adım yazılıdır.
>
> Kavramlar (NDVI, LST, F1, IoU, Spearman, Mann-Kendall…) için: [plan/yapilanlar_ve_kavramlar.md](plan/yapilanlar_ve_kavramlar.md) ·
> Sınırlılıkların tam listesi: [report/sinirliliklar_notlari.md](report/sinirliliklar_notlari.md)

## İçindekiler
1. [Proje ne soruyor?](#1-proje-ne-soruyor)
2. [Kim ne yaptı? (zaman çizelgesi)](#2-kim-ne-yaptı-zaman-çizelgesi)
3. [Temel analiz hattı — notebook 00–08](#3-temel-analiz-hattı--notebook-0008)
4. [Sonradan eklenenler](#4-sonradan-eklenenler)
5. [Sonuçların özeti](#5-sonuçların-özeti)
6. [Nasıl çalıştırılır?](#6-nasıl-çalıştırılır)
7. [Dosya haritası](#7-dosya-haritası)
8. [Sınırlılıklar ve gelecek çalışmalar](#8-sınırlılıklar-ve-gelecek-çalışmalar)

---

## 1. Proje ne soruyor?

**Ana soru:** Türkiye'nin farklı coğrafyalarında arazi örtüsü değiştiğinde (kent büyüdüğünde, orman ya da tarım alanı değiştiğinde,
göl küçüldüğünde) yerel iklim göstergeleri (yüzey sıcaklığı, nem, yağış) nasıl değişiyor ve bunu uydu verisi ile yapay zekâyla ölçebilir miyiz?

**Yaklaşım (3 adım):** önce coğrafi değişimi tespit et → sonra iklim göstergeleriyle ilişkisini ölç → sonra iller arasında karşılaştır.

**Çalışma alanları (7 il).** Her il farklı bir değişimi temsil eder. GeoClimate dokümanındaki 4 il (★) ana odak, diğer 3 il karşılaştırma ve genelleme testi içindir:

| İl | Araştırma konusu | Alt soru / hipotez |
|---|---|---|
| İstanbul ★ | Kentleşme ve kentsel ısı adası | AS2 · H1 |
| İzmir | Kıyı kentleşmesi ve ısı adası | AS2 · H1 |
| Artvin ★ | Orman örtüsü ve yüzey sıcaklığı | AS1 · H2 |
| Samsun | Delta ve sulak alanlar | AS3 · H4 |
| Konya ★ | Tarım, kuraklık ve toprak nemi | AS3–AS4 · H3–H4 |
| Van ★ | Göl havzası ve su yüzeyi | AS3 · H4 |
| Şanlıurfa | Sulu tarım (GAP) ve yüzey sıcaklığı | AS1 · AS4 · H2–H3 |

**Hipotezler:** H1 yapılaşma ↑ ↔ yüzey sıcaklığı ↑ · H2 bitki/orman ↓ ↔ yüzey sıcaklığı ↑ · H3 tarım ↔ bitki ve nem ·
H4 su/sulak alan ↔ sıcaklık ve nem · H5 ilişkiler bölgeye göre farklılaşır · H6 model başarısı bölgeye göre değişir (genelleme).
Analizler **ilişki** gösterir; neden-sonuç iddiası yoktur.

---

## 2. Kim ne yaptı? (zaman çizelgesi)

| Tarih | Kim | Ne |
|---|---|---|
| 3–4 Kasım | **Zeynep Selin Kaya** | Proje iskeleti, Earth Engine veri toplama (01), veri tanıtımı (02), 4 sınıflandırma modeli (03), değişim ve iklim analizi (04), İDA nesne tespiti (05), bölgeler arası genelleme (06), literatür adayları (Faz 7) |
| 14–15 Kasım | **Zeynep Selin Kaya** | 04'ü örneklem tabanlı yönteme taşıma (GEE kotası), mekânsal blok düzeltmesi, sınırlılık notları, rapor ve sunum iskeletleri (Faz 8), teslim kontrol listesi |
| 16 Kasım | **Sena Öz** | Kapsamı GeoClimate dokümanına uyarlama, İDA'nın çıkarılması, görev planı, IoU · mekânsal blok doğrulama · XGBoost regresyonu · H1–H6 kanıt tabloları (gerçek veriyle çalıştırıldı), kavram rehberi |
| 16 Kasım | **Zeynep Selin Kaya** · **Sena Öz** | GitHub Actions otomatik kontrolleri (iki ayrı iş akışı) |
| 16–17 Kasım | **Sena Öz** | Streamlit sonuç paneli, QGIS harita üretimi (29 harita + proje), etkileşimli web sitesi, model uyumu testi |
| 17 Kasım | **Sena Öz** | Sentinel-2 veri (07) ve U-Net (08) notebook'larının yazılması; tokensiz kurulum |
| 17–18 Kasım | **Zeynep Selin Kaya** | 07 ve 08'i Colab'da (GPU) çalıştırma: 56 GeoTIFF, U-Net eğitimi, RF karşılaştırması, LOCO, 2017→2025 değişim |
| 18 Kasım | **Sena Öz** | U-Net sonuçlarının web sitesine, panele, rapor iskeletine ve bu belgeye işlenmesi; U-Net uyum testi |

Ayrıntılı geçmiş: `git log`. Birleştirmeler Pull Request #1, #2 ve #3 ile yapıldı.

---

## 3. Temel analiz hattı — notebook 00–08

Analizler Google Colab'da sırayla çalışan notebook'lardır. Bütün ayarlar tek dosyadadır (`config.py`), her yerde `RANDOM_STATE = 42`.
**Kod GitHub'da, veri ve sonuçlar Google Drive'da** (`Drive'ım/yapay-zeka-proje/`).

### Faz 0 — Kurulum ve erişim kontrolü (`00_kurulum_erisim_kontrolu`)
- **Ne:** Google Earth Engine'e (GEE) bağlanma, 7 ilin sınırları (FAO GAUL), bütün veri setlerine erişim testi.
- **Neden:** Büyük hesaplara başlamadan önce her şeyin çalıştığından emin olmak. Bu sırada iki kısıt bulundu: Landsat 9'un ilk görüntüsü
  08.11.2021 (2014 yalnızca Landsat 8 ile kurulabilir) ve JRC su verisi 2021'de bitiyor (2024 su alanı Landsat MNDWI ile hesaplanmalı).

### Faz 1 — Veri toplama (`01_veri_toplama_gee`)
- **Ne:** 2014, 2021 ve 2024 için **yaz kompozitleri** (Haziran–Ağustos, bulut maskeli, ortanca/medyan); 6 bant + 6 spektral indeks
  (NDVI, NDBI, MNDWI, NDMI, SAVI, BSI); **ESA WorldCover 2021** etiketli örnek noktalar; **1 km grid** (her hücrede indeksler, yüzey sıcaklığı, su ve sınıf payları);
  2003–2024 **iklim serileri** (MODIS yüzey sıcaklığı, ERA5-Land toprak nemi ve hava sıcaklığı, CHIRPS yağış).
- **Nasıl:** Etiket olarak WorldCover'ın 11 sınıfı projenin 6 sınıfına eşlendi (Orman, Tarım, Yapılaşma, Çayır/Çalı, Çıplak, Su/Sulak).
  Noktalar yalnızca 3×3 pikselde homojen alanlardan ve **en az 300 m arayla** alındı. Önce Artvin'de **pilot** çalıştırılıp kota ölçüldü.
- **Neden:** Aynı mevsim karşılaştırılmazsa mevsim farkı "arazi değişimi" gibi görünür. 300 m aralık yan yana piksellerin hem eğitimde hem testte olmasını
  (mekânsal sızıntı) azaltır. GEE ücretsiz kotası ayda 150 EECU-saat olduğu için pilot şarttı.
- **Sonuç:** 13 251 etiketli nokta (hedef 13 986). Faz 1 ≈ 23,3 EECU-saat. MNDWI su alanı JRC ile 2021'de uyumlu (IoU 0,64–0,94).

### Faz 2 — Veri tanıtımı (`02_eda_tanimlayici_istatistik`)
- **Ne:** Sınıf dağılımı, ortalama/medyan/mod, histogram ve kutu grafikleri, korelasyon, eksik ve aykırı değer kontrolü.
- **Önemli bulgular:** (1) Landsat'ta **NDMI = −NDBI** (aynı iki bant, ters işaret) → NDMI model girdisinden çıkarıldı; model **11 özellik** kullanır.
  (2) "Otsu sulak alan" yaz görüntüsünde bitki gibi görünüyor (NDVI ≈ 0,63) → sulak alan değişimi tek yaz görüntüsüyle güvenilir ölçülemez.

### Faz 3 — Sınıflandırma modelleri (`03_siniflandirma_modelleri`)
- **Ne:** Dört farklı yaklaşım: **Random Forest** (ağaç oylaması), **XGBoost** (hatayı düzelten ağaçlar), **SVM** (sınır çizen), **MLP** (sinir ağı).
- **Nasıl:** Veri %70 eğitim / %15 doğrulama / %15 test (9 275 / 1 988 / 1 988). Her model için 10 kombinasyonluk rastgele hiperparametre araması (3 katlı CV, macro-F1).
  En iyi model **doğrulama** kümesine göre seçildi; test kümesine yalnızca son raporlamada bakıldı.
- **Neden:** Farklı mantıktaki modelleri aynı veriyle karşılaştırmak "hangi yaklaşım bu veri için uygun?" sorusunu cevaplar. Seçimi test kümesiyle yapmak
  sonucu iyimser gösterirdi.
- **Sonuç (test):** XGBoost macro-F1 **0,783**, ROC-AUC 0,961, Kappa 0,742 → **seçilen model** (`best_model.joblib`). En zor sınıf Tarım.
  SHAP ile modelin hangi özelliklere dayandığı gösterildi.

### Faz 4 — Değişim ve iklim analizi (`04_degisim_ve_iklim_analizi`)
- **Ne:** 2014→2024 arazi değişimi, geçiş matrisi, iklim trendleri, değişim–iklim ilişkisi, kentsel ısı adası, yüzey sıcaklığı regresyonu.
- **Nasıl ve neden:**
  - **Örneklem tabanlı sınıflandırma:** Bütün ili 30 m'de GEE'de sınıflandırmak kotayı aştı (Artvin'in tek görevi 5,56 EECU-saat, diğerleri zaman aşımı).
    Bunun yerine her 1 km hücreye **9 düzenli nokta** konuldu; GEE yalnızca bu noktalardaki değerleri okudu, sınıflandırmayı Colab'da **Faz 3'ün XGBoost modeli** yaptı.
    Kontroller: noktaların %98,1'i grid ile eşleşti; GEE ile Colab modeli arasındaki F1 farkı yalnızca 0,0097.
  - **Trend:** Mann-Kendall testi + Sen eğimi (2003–2024); normal dağılım varsaymaz, aykırı yıllara dayanıklıdır.
  - **İlişki:** 1 km hücrelerde Spearman korelasyonu (Δ değişkenler). Çok büyük örneklemde p-değeri hep küçük çıktığı için ρ'nun **büyüklüğüne** bakıldı.
  - **Kentsel ısı adası:** kentsel (yapılaşma > %50) − kırsal (yapılaşma < %5, su < %10, rakım farkı ≤ 200 m) yaz yüzey sıcaklığı.
  - **LST regresyonu:** yüzey sıcaklığını arazi payları, indeksler ve rakımdan tahmin eden Random Forest; **10 km mekânsal blok** çapraz doğrulama
    (ilk sürümdeki blok hatası 15 Kasım'da düzeltildi).
- **Sonuç:** Artvin orman +5,55 puan, Şanlıurfa tarım +4,13 puan; ΔNDVI–ΔLST 7 ilin hepsinde negatif; ısı adası İstanbul +8,1 °C, İzmir +1,5 °C;
  LST regresyonu R² **0,921**, RMSE 2,04 °C; en etkili değişken NDVI.

### Faz 5 — İDA nesne tespiti (`05_ida_nesne_tespiti`) — **kapsamdan çıkarıldı**
- **Ne yapılmıştı:** Su yüzeyinde yüzen atık tespiti için YOLOv8n; açık bir veri setinde (Mendeley, Endonezya nehirleri, 1 577 görüntü) mAP50 0,388.
- **Neden çıkarıldı (16 Kasım):** (1) Atık tespiti ana soruyu (arazi değişimi ↔ iklim) test etmiyor; (2) İstanbul/İzmir kıyılarına ait İDA görüntüsü yok,
  başka ülkenin verisiyle Türkiye sonucu verilemez; (3) FloW-Img veri setine Türkiye'den erişilemedi. Notebook ve sonuçları git geçmişinde ve Drive'da duruyor.

### Faz 6 — Bölgeler arası genelleme (`06_bolgeler_arasi_genelleme`)
- **Ne:** **Leave-One-City-Out (LOCO):** bir il tamamen dışarıda bırakılıp model kalan 6 ille eğitildi, o ilde test edildi (7 tur).
- **Neden:** "Bir ilde eğitilen model başka ilde çalışır mı?" (H6). Aynı test noktalarında karşılaştırıldığı için fark yalnızca "ili görmüş olmak"tan gelir.
- **Sonuç:** XGBoost ortalama **0,109** macro-F1 kaybediyor; en çok Konya (−0,187), en az Artvin (−0,059). Kayıp kurak ve sıcak illerde büyük
  (yağışla ρ ≈ −0,96; n = 7, yalnızca örüntü).

### Notebook 07 — Sentinel-2 verisi (`07_sentinel2_veri`)
- **Ne:** GeoClimate dokümanındaki "Sentinel-2 + U-Net" adımının verisi. Her ilde ilin konusunu en iyi gösteren **iki alt bölge**
  (20 km × 20 km, toplam 14 kutu; ör. Artvin–Yusufeli, İstanbul kuzey çevresi, Konya–Karapınar, Van kent kıyısı), 10 m çözünürlükte.
- **Nasıl:** `COPERNICUS/S2_SR_HARMONIZED` yaz görüntüleri; bulut maskesi **s2cloudless** (olasılık < %40) + sahne sınıflandırma katmanı (SCL: bulut, gölge, kar).
  6 bant (B2, B3, B4, B8, B11, B12), yaz ortancası, EPSG:3035, 10 m. Yıllar: **2017** (2017–2019 arasından, bütün kutularda yeterli görüntü olan ilk yıl,
  otomatik seçildi), **2021** (etiket yılı) ve **2025**. Etiket: ESA WorldCover 2021 → aynı 6 sınıf.
  Çıktı: 14 kutu × (3 yıl + etiket) = **56 GeoTIFF** (`data/raw/s2/`).
- **Neden alt bölge:** 7 ilin tamamı 10 m'de yüzlerce GB eder ve GEE/Colab kotasını aşar; 20 km'lik kutular U-Net eğitimi için yeterli piksel
  (her kutu 4 milyon) verir. Sınırlılık: kutular ilin tamamını temsil etmez.
- **Kontrol:** Verisiz piksel oranı her yılda < %0,4 (en yüksek Konya–Karapınar 2017: %0,39), etiketsiz piksel yok (`s2_veri_ozeti.csv`).

### Notebook 08 — U-Net ile sınıflandırma (`08_unet_siniflandirma`)
- **Ne:** **U-Net**, görüntüyü 256 × 256 piksellik parçalar halinde okuyup her piksele sınıf veren bir evrişimli sinir ağıdır (segmentasyon).
  03'teki modeller her pikseli **tek başına** sınıflandırır; U-Net pikselin **komşularına da bakar** (tarla şekli, kent dokusu, kıyı çizgisi).
- **Nasıl:**
  - **Bölme:** Her kutu kuzeyden güneye şeritlere ayrıldı: %70 eğitim, %15 doğrulama, %15 test; şeritler arasında **320 m tampon**
    (yan yana pikseller hem eğitimde hem testte olmasın diye; 03'teki 300 m kuralının karşılığı).
  - **Model:** ResNet-34 kodlayıcılı U-Net (`segmentation_models_pytorch`), **ImageNet ağırlıklarıyla başlatıldı** (transfer öğrenme), ilk katman 6 banda uyarlandı.
    Kayıp: sınıf ağırlıklı çapraz entropi + Dice (az görülen yapılaşma, çıplak ve su sınıfları öne çıksın diye). Veri artırma: döndürme/yansıtma.
  - **Eğitim:** Colab GPU, karma hassasiyet (AMP), her epoch 1 600 rastgele parça; doğrulama mIoU'su 6 epoch iyileşmeyince durdu →
    27 epoch, **en iyi epoch 20** (doğrulama mIoU 0,715), ≈8 dakika. Her epoch Drive'a kaydedildiği için oturum koparsa kaldığı yerden devam eder.
  - **Önce RF, sonra U-Net:** GeoClimate dokümanı temel model olarak Random Forest ister. RF **aynı Sentinel-2 verisi ve aynı şeritlerle** eğitildi
    (60 000 piksel; 6 bant + NDVI, NDBI, MNDWI) ve iki model **aynı 500 000 test pikselinde** karşılaştırıldı. Fark yalnızca komşuluk bilgisinden gelir.
  - **H6 (LOCO):** Bir ilin iki kutusu eğitimden çıkarıldı, model kalan 6 ille (15 epoch) eğitilip o ilin test şeritlerinde ölçüldü (7 tur).
  - **Değişim:** Ana model 2017 ve 2025 görüntülerine uygulandı; geçiş matrisi km² olarak (1 piksel = 100 m²) ve değişim haritası
    (`results/unet_tahmin/*.tif`, QGIS'te açılır).
- **Sonuç (test şeritleri, 14 kutu):**

  | Model (aynı Sentinel-2 test pikselleri) | Accuracy | macro-F1 | mIoU |
  |---|---|---|---|
  | Random Forest (piksel) | 0,765 | 0,740 | 0,608 |
  | **U-Net (komşuluk)** | **0,863** | **0,845** | **0,743** |

  - Komşuluk bilgisi macro-F1'i **+0,105**, mIoU'yu **+0,135** artırdı. En büyük kazanç Yapılaşma (IoU 0,54 → 0,79), Tarım (0,65 → 0,81) ve
    Çıplak (0,35 → 0,51); Su/Sulak iki modelde de ≈0,96 (su zaten tek pikselde kolay tanınır).
  - **İl bazında** macro-F1 0,42 (Şanlıurfa) … 0,73 (Van); accuracy ise 0,71 (Samsun) … 0,92 (Van). İl bazında F1'in düşük görünmesi hata değil:
    bir ilin test şeridinde nadir sınıflar (ör. Şanlıurfa'da orman %0,4) birkaç piksele düşer ve o sınıfın F1'i macro ortalamayı aşağı çeker.
    14 kutunun birleşik testinde her sınıfın yeterli pikseli olduğu için F1 0,845'tir.
  - **LOCO (H6):** ili hiç görmeyen model ortalama **0,051** macro-F1 kaybediyor; en çok **Artvin (−0,190)**: dağlık orman/çayır dokusu başka illerde yok.
    İzmir'de kayıp yok (+0,056: başka illerin kıyı ve delta örnekleri yeterli). Landsat + XGBoost'taki 0,109'la **doğrudan karşılaştırılamaz**
    (farklı veri, çözünürlük ve test alanı) ama aynı yöne işaret eder: **başarı bölgeye göre değişir** (H6).
  - **Değişim 2017 → 2025 (iki kutunun toplamı, ≈800 km²/il):** Artvin Su/Sulak **12,1 → 30,7 km²** (Yusufeli baraj gölü; Landsat MNDWI'deki +%78,9 ile
    aynı yön), İstanbul Yapılaşma **+31,0 km²** (+%12,9), Konya Yapılaşma +16,5 km², Şanlıurfa Yapılaşma +10,8 km² ve Tarım +7,3 km².
    Samsun'da Orman −89 km², Çayır/Çalı +68 km² görünüyor: bu büyüklükte bir değişim gerçek kesimden çok **iki yazın fenoloji/görüntü farkı** olabilir
    → haritayla kontrol edilmeden yorumlanmamalı `[DOĞRULANMADI]`.

### Literatür, rapor ve sunum iskeletleri
- 46 aday çalışma (DOI'leri doğrulanmış) `literature/` altında; rapor iskeleti hocanın bölüm sırasına göre `report/rapor_iskeleti.md`;
  sunum iskeleti ve olası sorular `presentation/`; teslim kontrol listesi `report/teslim_kontrol_listesi.md`.

---

## 4. Sonradan eklenenler

### 4.1 Kapsam: GeoClimate çerçevesi ve İDA'nın çıkarılması
- **Ne:** Proje başlığı ve alt sorular GeoClimate AI dokümanına göre düzenlendi; İDA modülü çıkarıldı (bkz. Faz 5); 7 il korundu.
- **Neden:** Araştırmanın bilimsel bütünlüğü. Dokümandaki Sentinel-2 + U-Net adımı notebook 07–08 ile yapıldı; görev planı `plan/gorev_dagilimi.md`'de.

### 4.2 IoU metriği
- **Ne:** `src/ml_utils.compute_metrics`'e IoU (Jaccard = TP / (TP+FP+FN)) eklendi; 03'te sınıf bazında IoU tablosu.
- **Neden:** GeoClimate dokümanında isteniyor; U-Net gibi segmentasyon modelleriyle aynı ölçüyle karşılaştırma sağlar. IoU = F1/(2−F1) olduğundan F1'den düşüktür.
- **Sonuç (Drive'daki resmi model dosyalarından):** macro IoU RF 0,633 · XGBoost **0,657** · SVM 0,644 · MLP 0,664; en zayıf sınıf Tarım (≈0,42).

### 4.3 Mekânsal blok doğrulama (03, bölüm 10b)
- **Ne:** Aynı modeller iki şekilde 5 katlı çapraz doğrulandı: rastgele ve **10 km'lik bloklara göre** (aynı bloktaki noktalar hep aynı katmanda).
- **Neden:** Yakın yerler birbirine benzer; rastgele bölme başarıyı şişirebilir. Faz 3'teki bölme değiştirilmedi, çünkü 04 ve 06 ona bağlı.
- **Sonuç:** Fark en fazla **0,013** → 300 m aralık sızıntıyı büyük ölçüde önlemiş; 03'ün sonuçları güvenilir.

### 4.4 XGBoost regresyonu (04 B5)
- LST regresyonuna XGBoost eklendi: R² 0,921 (Random Forest ile aynı) → sonuç tek bir modele özgü değil.

### 4.5 H1–H6 kanıt tabloları (04 B9, 06 bölüm 6)
- Her hipotez için 7 ildeki ilgili korelasyonlar, beklenen yönle uyum ve güç sınıfı otomatik toplanır (`hipotez_ozet.csv`). "Desteklendi mi" kararı ekibe bırakılmıştır.
- Öneriler: H1 kısmen · **H2 destekleniyor (en sağlam bulgu)** · H3 kısmen · H4 büyük ölçüde desteklenmiyor · H5 kısmen · **H6 destekleniyor**.

> **Bu ek analizler nasıl çalıştırıldı?** GPU gerektirmedikleri için Drive'daki gerçek veriyle yerel bilgisayarda çalıştırıldı. Kontrol olarak modeller
> Faz 3 ayarlarıyla yeniden eğitildi: RF, SVM ve MLP Colab sonuçlarıyla **birebir** aynı çıktı; test bölmesi 13 251 noktada 0 farkla aynıydı.
> XGBoost yeniden eğitildiğinde 0,776 çıktı: sürüm aynı (3.4.1), ama başka bir bilgisayarda birebir aynı ağaçlar oluşmadı.
> Bu yüzden IoU, Drive'daki **resmi model dosyaları yeniden eğitilmeden** yüklenerek hesaplandı (`tools/resmi_model_iou.py`):
> dört modelin accuracy ve F1'i resmi tabloyla birebir aynı çıktı. **Raporda ve bütün çıktılarda resmi Colab değeri (0,783) kullanılır.**
> Drive'daki orijinal dosyalara dokunulmadı; yalnızca 11 yeni dosya eklendi.

### 4.6 GitHub Actions (otomatik kontrol)
- **Ne:** Her push'ta GitHub kendi sunucusunda kontroller çalıştırır (`.github/workflows/ci.yml`; Selin'in `kontrol.yml`'si de çalışır).
- **Neyi denetler:** notebook'lar geçerli mi, yazım hatası var mı, **çıktılı notebook commit'lenmiş mi**; `config.py` tutarlı mı; metrikler doğru mu
  (IoU formülü dahil); 4 model eğitilebiliyor mu; notebook'ların çağırdığı her fonksiyon `src/`'de var mı; panel her seçimde hatasız açılıyor mu;
  **site ve paneldeki sayılar resmi Colab sonuçlarıyla aynı mı** (`tests/test_model_uyumu.py`).
- **Neden:** Earth Engine ve Drive gerektiren analizler GitHub'da çalışamaz; ama "bu değişiklik kodu bozdu mu?" sorusu her seferinde otomatik sorulabilir.

### 4.7 Streamlit sonuç paneli (`panel/`)
- 5 sekmeli etkileşimli panel (genel bakış, arazi değişimi, iklim, ilişkiler ve hipotezler, model başarısı). Hesap yapmaz; notebook çıktılarını gösterir.
- U-Net: *Arazi değişimi* sekmesinde seçili ilin iki alt bölgesinin 2017→2025 değişim görselleri ve km² kartları; *Model başarısı* sekmesinde
  RF–U-Net karşılaştırması, sınıf bazında IoU, LOCO tablosu, eğitim eğrileri ve karışıklık matrisi.

### 4.8 QGIS haritaları (`qgis/haritalar.py`)
- **Ne:** PyQGIS ile rapor ve sunum için **29 harita** (çalışma alanları + her il için 2024 arazi örtüsü, 2014→2024 değişim, göreli ΔLST, ΔNDVI);
  lejant, ölçek çubuğu, kuzey oku ve kaynak notuyla. Ayrıca düzenlenebilir QGIS projesi (29 baskı düzeni) ve GeoPackage.
- **Neden ve nasıl:** Earth Engine'den gelen küçük PNG'lerde lejant ve ölçek yoktu. Harita projeksiyonu **Türkiye merkezli Lambert konik** seçildi;
  analiz ızgarası EPSG:3035 (Avrupa merkezli) Türkiye'yi döndürüp bozuyordu. **Göreli ΔLST** = hücrenin değişimi − ilin medyan değişimi;
  iki yazın genel hava farkını giderir.

### 4.9 Etkileşimli web sitesi (`web/`)
- **Ne:** Sonuçları görsel olarak anlatan tek sayfalık site. Türkiye haritasından il seçilir; her ilin **kendi araştırma sorusu** etkileşimli 1 km hücre
  haritası (sade ya da uydu altlık, katman seçimi, hücre üzerine gelince değerler), sayı kartları, kısa yorum ve grafiklerle gösterilir.
  Hipotezler, model başarısı ve yöntem bölümleri vardır.
- **U-Net bölümü:** il seçilince ilin iki Sentinel-2 alt bölgesi (10 m, 2017 → 2025 değişim görseli), il bazında F1 ve km² kartları; model bölümünde
  RF–U-Net sınıf bazında IoU grafiği ve Landsat + XGBoost ile U-Net'in il dışı (LOCO) kayıp karşılaştırması.
- **Nasıl:** Düz HTML + MapLibre GL (harita) + proj4js + Chart.js; sunucu gerektirmez. Hücre verisi kompakt tutuldu (37 MB → 7 MB): her hücrenin yalnızca
  numarası saklanır, köşeleri tarayıcı EPSG:3035'ten hesaplar.
- **Model uyumu:** Haritalardaki sınıflar **eğittiğimiz XGBoost modelinin** 2014/2024 sınıflandırmasıdır; bütün sayılar resmi Colab tablolarından gelir.
  U-Net sayıları Selin'in Colab çalıştırmasının tablolarından gelir. Site hiçbir şeyi yeniden hesaplamaz; CI bunu denetler.

---

## 5. Sonuçların özeti

| Konu | Sonuç | Kaynak |
|---|---|---|
| Sınıflandırma (test) | XGBoost macro-F1 **0,783**, Accuracy 0,785, ROC-AUC 0,961, Kappa 0,742 | `model_karsilastirma.csv` |
| Diğer modeller | MLP 0,789 · SVM 0,772 · RF 0,764 (macro-F1) | aynı |
| Mekânsal sızıntı | rastgele − 10 km blok ≤ **0,013** | `mekansal_blok_ozet.csv` |
| Arazi değişimi | Artvin orman +5,55 puan · Şanlıurfa tarım +4,13 · İstanbul yapılaşma +0,64 · İzmir +0,56 · Konya tarım −0,13 | `sinif_alanlari_degisim.csv` |
| İklim trendleri | Şanlıurfa yaz LST −1,44 °C/10 yıl (p = 0,0001) · Konya −1,42 °C/10 yıl (p = 0,011) · Van yaz toprak nemi −0,017/10 yıl (p = 0,024) | `iklim_trend_mann_kendall.csv` |
| Kentsel ısı adası | İstanbul +8,1 / +8,0 °C · İzmir +1,2 / +1,5 °C (2014 / 2024) | `kentsel_isi_adasi.csv` |
| En güçlü ilişki | ΔNDVI–ΔLST 7/7 ilde negatif, ρ −0,41 … −0,65 (H2) | `hipotez_kanit_H1_H5.csv` |
| LST regresyonu | R² **0,921**, RMSE 2,04 °C (RF, 10 km blok CV); en etkili NDVI ve rakım | `lst_regresyon_metrikleri.csv` |
| Genelleme | başka ilde ortalama −0,109 macro-F1; en çok Konya | `genelleme_dusus.csv` |
| Su alanı (MNDWI) | Artvin +%78,9 · Van +%12,1 · İstanbul +%9,8 · Samsun +%9,0 · İzmir −%6,0 | `su_alani_karsilastirma.csv` |
| U-Net (Sentinel-2, 10 m) | macro-F1 **0,845**, mIoU **0,743**, Accuracy 0,863 (14 alt bölge, test şeritleri) | `unet_metrikleri.csv` |
| Önce RF, sonra U-Net | aynı piksellerde RF 0,740 → U-Net 0,845 macro-F1 (+0,105); mIoU 0,608 → 0,743 | `unet_vs_rf.csv` |
| U-Net il dışı (LOCO) | ortalama −0,051 macro-F1; en çok Artvin −0,190 | `unet_loco.csv` |
| U-Net değişim 2017→2025 | Artvin su 12,1 → 30,7 km² · İstanbul yapılaşma +31,0 km² | `unet_degisim_ozet.csv` |

---

## 6. Nasıl çalıştırılır?

### 6.1 Analiz notebook'ları (Google Colab)
1. **Earth Engine kaydı (bir kez):** https://code.earthengine.google.com/register → *Noncommercial* → *Academia & Research* → yeni Cloud projesi.
   Project ID'yi `config.py` → `GEE_PROJECT` satırına yazın.
2. **GitHub token gerekmez:** repo herkese açık; kurulum hücresi kodu doğrudan çeker. (Repo gizli yapılırsa: *Contents: Read-only* izinli bir
   fine-grained token oluşturup Colab'ın 🔑 **Secrets** bölümüne `GITHUB_TOKEN` adıyla ekleyin. Token'ı kodun içine yazmayın.)
3. **Drive:** Proje klasörü `Drive'ım/yapay-zeka-proje/` olmalı (paylaşılan klasörse: sağ tık → *Kısayol ekle → Drive'ım*).
4. **Açma:** Colab → *Dosya → Not defteri aç → GitHub* → `selinzeykaya/yapay-zeka-proje` → notebook'u seçin.
   Başka bir dalı denemek için kurulum hücresinde `GITHUB_BRANCH = "dal-adı"` yapın.
5. **Sıra:** 00 → 01 → 02 → 03 → 04 → 06 → 07 → 08 (*Çalışma zamanı → Tümünü çalıştır*). 01, 04 ve 07'nin baş kısmı GEE kotası harcar; sonuçlar
   önbelleğe yazılır, tekrar çalıştırmada yeniden hesaplanmaz. 00–07 GPU gerektirmez.
   - **07:** GEE'ye 56 GeoTIFF dışa aktarma görevi gönderir; görevler GEE'nin sunucusunda çalışır (≈1–2 saat). Hücre görevlerin bitmesini bekler;
     oturum koparsa tekrar çalıştırın, biten dosyalar atlanır.
   - **08:** *Çalışma zamanı → Çalışma zamanı türünü değiştir → T4 GPU* seçin. Eğitim ≈10 dakika, LOCO (7 tur) ≈30 dakika. Her epoch Drive'a kaydedilir;
     oturum koparsa aynı hücreyi tekrar çalıştırın, kaldığı yerden devam eder. Tabloları eğitmeden yenilemek için `YENIDEN_DEGERLENDIR = True`.
6. **Kaydetmeden önce:** Colab → *Düzenle → Tüm çıktıları temizle* (repo çıktısız notebook tutar; CI çıktılı notebook'u reddeder).

### 6.2 Otomatik kontrolleri yerelde çalıştırma
```bash
pip install -r requirements-ci.txt
python tools/notebook_kontrol.py
pytest
```

### 6.3 Streamlit paneli
```bash
pip install -r panel/requirements.txt
streamlit run panel/app.py                       # http://localhost:8501
# Notebook'lar yeniden çalıştıysa paneli güncellemek için:
python panel/veri_hazirla.py "<Drive'daki yapay-zeka-proje klasörü>"
```

### 6.4 Web sitesi
```bash
python -m http.server 8600 -d web                # http://127.0.0.1:8600
# Notebook'lar yeniden çalıştıysa veriyi güncellemek için (önce paneli güncelleyin):
python web/veri_hazirla.py "<Drive>/data/processed/grid_1km_lc_iklim.csv" <tur_adm1.geojson> panel/veri/tables
```
- `tur_adm1.geojson`: [geoBoundaries TUR ADM1 (sadeleştirilmiş)](https://github.com/wmgeolab/geoBoundaries/raw/main/releaseData/gbOpen/TUR/ADM1/geoBoundaries-TUR-ADM1_simplified.geojson) (CC BY 4.0).
- Dosyayı doğrudan çift tıklayarak açmayın (`file://`); tarayıcı veri dosyalarını yükleyemez, yukarıdaki yerel sunucuyu kullanın.
- **Herkese açık yayın (isteğe bağlı):** repo sahibi GitHub'da *Settings → Pages → Source: Deploy from a branch → main / (root)* seçer;
  site `https://selinzeykaya.github.io/yapay-zeka-proje/web/` adresinde açılır.

### 6.5 QGIS haritaları (QGIS 3.44 ile denendi)
```powershell
$q = "<QGIS klasörü>\bin\python-qgis-ltr.bat"
& $q qgis/haritalar.py <grid_1km_lc_iklim.csv> <tur_adm1.geojson> <çıktı klasörü> gpkg     # 1) GeoPackage
& $q qgis/haritalar.py <grid_1km_lc_iklim.csv> <tur_adm1.geojson> <çıktı klasörü> harita   # 2) 29 harita + QGIS projesi
```
Çıktı klasöründe `png/` (29 harita), `geoclimate.qgz` (QGIS'te çift tıklayın; *Proje → Düzen Yöneticisi*'nden 29 sayfa) ve `geoclimate.gpkg` oluşur.
İki adım ayrı çalıştırılmalı ve `QT_QPA_PLATFORM=offscreen` kullanılmamalıdır (nedenleri betiğin başında yazılı).

---

## 7. Dosya haritası

```
config.py                 Tüm ayarlar: iller, yıllar, sınıflar, model aralıkları, hipotezler (HYPOTHESES)
src/gee_utils.py          Earth Engine yardımcıları (kompozit, export, sınıflandırıcı)
src/ml_utils.py           Modeller ve metrikler (Accuracy … ROC-AUC, Kappa, IoU)
notebooks/00 … 08         Analiz hattı (05 yok: İDA çıkarıldı; 07–08 Sentinel-2 + U-Net)
tests/, tools/            Otomatik kontroller (pytest, notebook kontrolü)
.github/workflows/        GitHub Actions (ci.yml, kontrol.yml)
panel/                    Streamlit paneli + özet veri (panel/veri/)
web/                      Etkileşimli site (index.html, app.js, style.css, data/)
qgis/haritalar.py         QGIS harita üretimi
literature/               46 aday çalışma, literatür matrisi, karşılaştırma tablosu
report/                   Rapor iskeleti, sınırlılık notları, teslim kontrol listesi
presentation/             Sunum iskeleti, olası sorular, ekip içi rehber sayfası
plan/                     Görev dağılımı, kavramlar ve yapılanlar rehberi
```

| Notebook | Ürettiği önemli dosyalar (Drive `results/` ve `data/processed/`) |
|---|---|
| 01 | `samples_2021.csv`, `grid_1km_2014_2024.csv`, `iklim_sehir_yillik.csv`, `su_alani_karsilastirma.csv` |
| 02 | `tanimlayici_istatistik.csv`, `sinif_dagilimi.png`, `korelasyon_isi_haritasi.png` |
| 03 | `model_karsilastirma.csv`, `best_model.joblib`, `sinif_bazinda_iou.csv`, `mekansal_blok_ozet.csv`, karışıklık matrisleri, ROC, SHAP |
| 04 | `grid_1km_lc_iklim.csv`, `sinif_alanlari_degisim.csv`, `gecis_matrisi.csv`, `iklim_trend_mann_kendall.csv`, `spearman_degisim_iklim.csv`, `kentsel_isi_adasi.csv`, `lst_regresyon_metrikleri.csv`, `hipotez_ozet_H1_H5.csv` |
| 06 | `genelleme.csv`, `genelleme_dusus.csv`, `genelleme_neden_spearman.csv`, `hipotez_ozet.csv` |
| 07 | `data/raw/s2/s2_<kutu>_<yıl>.tif`, `s2_<kutu>_etiket.tif`, `s2_yillar.json`, `s2_alt_bolgeler.csv`, `s2_veri_ozeti.csv`, `s2_kutular.png` |
| 08 | `unet_metrikleri.csv`, `unet_vs_rf.csv`, `unet_il_bazinda.csv`, `unet_loco.csv`, `unet_degisim_ozet.csv`, `unet_degisim_<kutu>.png`, `results/unet_tahmin/*.tif`, `results/models/unet/` |

---

## 8. Sınırlılıklar ve gelecek çalışmalar

**Sınırlılıklar (en önemlileri):**
- Etiket yalnızca 2021 için var → 2014 ve 2024 haritalarının doğruluğu ölçülemiyor; küçük değişimler temkinli yorumlanmalı.
- Bulgular ilişki düzeyinde; neden-sonuç iddiası yok. Hücreler bağımsız olmadığı için p-değerleri yorumlanmadı.
- Değişim örneklem tabanlı (hücre başına 9 nokta); hücre düzeyinde gürültülü, il düzeyinde kararlı.
- Tek yaz kompoziti; 2014 yalnızca Landsat 8, 2024 Landsat 8+9.
- Su/Sulak sınıfı iki farklı yüzeyi birleştiriyor; otsu sulak alanlar yaz görüntüsünde bitki gibi görünüyor.
- ERA5-Land ~9–11 km çözünürlükte, yalnızca il ölçeğinde kullanıldı; 1 km'de nem göstergesi NDMI (doğrudan toprak nemi değil).
- Doğrulanması gereken yorumlar: Artvin su artışı (Yusufeli barajı?), Şanlıurfa (GAP sulaması?), Van su artışı (göl seviyesi mi, kompozit mi?),
  İstanbul–İzmir ısı adası farkı (tanım etkisi?).
- **U-Net:** etiket yine yalnızca 2021 (2017/2025 doğruluğu ölçülemiyor); kutular ilin tamamını temsil etmez; şerit bölmesi kutu içinde yapıldığından
  test şeritleri eğitimle aynı bölgededir (bunu LOCO ölçer); il bazında F1 nadir sınıflar yüzünden düşük görünür; LOCO modelleri 15 epoch, ana model 27 epoch
  eğitildi; Samsun orman azalması gibi büyük değişimler fenoloji farkı olabilir.

**Gelecek çalışmalar:** U-Net'i alt bölgelerden il geneline genişletme ve yıllık (2017–2025) değişim serisi; çok mevsimli veri ya da Sentinel-1 radar ile sulak alanlar;
ERA5 ölçeğinde (~9 km) analiz; SPI kuraklık indeksi; bağımsız referans veriyle 2014/2024 doğruluk değerlendirmesi; kurak iller için bölgesel model.
Ayrıntılı plan: [plan/gorev_dagilimi.md](plan/gorev_dagilimi.md).
