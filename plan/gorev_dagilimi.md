# GeoClimate AI — Kalan işler ve görev dağılımı

> Ekip: 3 kişi (**A**, **B**, **C**). Her şey Google Colab + Google Earth Engine (GEE) üzerinde, bulutta çalışır. Kimsenin kendi bilgisayarında GPU olması gerekmez.
> Repo dalı: herkes kendi dalında çalışır (`ad/konu`), bitince `main`'e Pull Request açılır.

## Repoda zaten yapılmış olanlar (tekrar yapılmayacak)

Bu plan yalnızca **eksikleri** listeler. Aşağıdakiler Selin tarafından tamamlandı, sonuçları Drive'da:

| Yapılmış | Notebook |
|---|---|
| GEE kurulumu, 7 il sınırı, veri erişim testi | 00 |
| Landsat 8/9 yaz kompozitleri (2014, 2021, 2024), bulut maskesi, 6 indeks; 13.251 etiketli nokta (WorldCover 2021); 1 km grid; 2003–2024 iklim serileri (MODIS LST, ERA5-Land, CHIRPS) | 01 |
| Tanımlayıcı istatistik (ortalama/medyan/mod), grafikler, eksik/aykırı değer, ön işleme kararları | 02 |
| RF, XGBoost, SVM, MLP; hiperparametre araması; Accuracy/Precision/Recall/F1/ROC-AUC/Kappa; karışıklık matrisi; SHAP | 03 |
| 2014→2024 değişim + geçiş (değişim) matrisi; Mann-Kendall + Sen eğimi; Spearman; kentsel ısı adası; RF + doğrusal LST regresyonu (10 km mekânsal blok CV, R² 0.921); su alanı (MNDWI–JRC IoU) | 04 |
| Leave-One-City-Out genelleme, sınıf bazında düşüş, neden göstergeleri | 06 |
| 46 aday kaynak (DOI doğrulanmış), rapor ve sunum iskeleti, olası sorular, sınırlılık notları | literature/, report/, presentation/ |

## 0. Kararlar (sabit)

| Konu | Karar |
|---|---|
| İller | **7 il kalıyor** (İstanbul, İzmir, Artvin, Samsun, Konya, Van, Şanlıurfa). GeoClimate'teki 4 il (İstanbul, Artvin, Konya, Van) **ana odak**, diğer 3 il karşılaştırma ve genelleme için. |
| Alt bölgeler | Sentinel-2 ve U-Net yalnızca **alt bölgelerde** yapılır (il başına 2–3 kare, her biri ~20 × 20 km). Tüm ili 10 m'de işlemek GEE kotasını ve Colab süresini aşar. Landsat tabanlı mevcut analizler tüm ilde kalır. |
| İDA | Kapsam dışı (çıkarıldı). |
| Dönem | Sentinel-2: 2017 (ya da ilk uygun yıl) ve 2025 yazları. Landsat: mevcut 2014/2024 ve 2003–2024 iklim serileri kalır. |
| Modeller | Mevcut: RF, XGBoost, SVM, MLP (piksel bazlı). Yeni: **U-Net** (Sentinel-2 alt bölgelerinde). SegFormer ve Siamese U-Net **yapılmayacak**, raporda "gelecek çalışma" olarak geçecek. |
| Hipotezler | H1–H6 → mevcut alt sorulara eşlenir (aşağıda). |

### H1–H6 ↔ mevcut analiz eşlemesi

| Hipotez | Test eden analiz | Notebook |
|---|---|---|
| H1 Yapılaşma ↑ ↔ LST ↑ | Δyapı–ΔLST Spearman, kentsel ısı adası | 04 (AS2) |
| H2 Orman/bitki ↓ ↔ LST ↑ | ΔNDVI–ΔLST, Δorman–ΔLST | 04 (AS1) |
| H3 Tarım ↔ NDVI, toprak nemi | Δtarım–ΔNDMI, ERA5 toprak nemi | 04 (AS4) |
| H4 Su/sulak alan ↔ sıcaklık, nem | Δsu–ΔLST, MNDWI su alanı | 04 (AS3) |
| H5 İlişkiler bölgeye göre değişir | İller arası ρ karşılaştırması, LST regresyonu | 04 |
| H6 Genelleme bölgeye göre değişir | Leave-One-City-Out | 06 |

## 1. GPU yetersizse: yapılmaması gerekenler

1. **Kendi bilgisayarında U-Net eğitme.** NVIDIA GPU yoksa (Intel/AMD dahili grafik) PyTorch CPU'da çalışır ve 10–50 kat yavaştır. Eğitim yalnızca Colab'da: *Çalışma zamanı → Çalışma zamanı türünü değiştir → T4 GPU*.
2. **Tüm ili 10 m'de indirme veya eğitme.** Yalnızca alt bölge kareleri.
3. **Eğitimi doğrudan Drive'dan okuyarak yapma.** Drive çok yavaştır. Veriyi her oturum başında tek bir `.zip`/`.npz` olarak `/content/` altına kopyalayın, eğitim oradan okusun.
4. **Büyük model seçme.** SegFormer, ResNet-101 ve büyük kodlayıcılar yok. U-Net + **ResNet-18 veya ResNet-34** (ImageNet ön eğitimli) yeterli.
5. **Büyük kare ve büyük batch.** 256 × 256 piksel kare, batch 8–16. "CUDA out of memory" hatasında önce batch'i yarıya indirin.
6. **Checkpoint'siz uzun eğitim.** Ücretsiz Colab oturumu birkaç saat sonra ya da sekme boştayken kopar. Her epoch sonunda model Drive'a kaydedilsin, kaldığı yerden devam edilsin.
7. **Aynı GEE export'unu birden fazla kişinin çalıştırması.** Kota proje başına aylık 150 EECU-saat. Export'u yalnızca **B** yapar, herkes Drive'dan okur.
8. **GPU açıkken GPU'suz iş yapmak.** Veri hazırlama, istatistik, grafik ve RF/XGBoost GPU istemez. Bunları CPU oturumunda çalıştırın, GPU kotasını eğitime saklayın.

## 2. Eğitimi hızlandırma

- **3 hesap = 3 GPU.** Colab'ın ücretsiz GPU kotası hesap başınadır. B ve C aynı anda farklı deneyleri kendi hesaplarında çalıştırır (ör. B: aynı il eğitimi; C: Leave-One-City-Out katmanları). A gerekirse üçüncü GPU olur.
- **Karma hassasiyet (AMP):** `torch.autocast("cuda")` + `GradScaler`. T4'te yaklaşık 2 kat hızlanma sağlar.
- **Erken durdurma:** Doğrulama kaybı 5 epoch boyunca iyileşmezse durur. Genelde 20–30 epoch yeter.
- **Hazır kütüphane:** `segmentation-models-pytorch` (U-Net + ResNet kodlayıcı tek satırla kurulur).
- **Veri bir kez hazırlanır:** GEE → GeoTIFF → kareler `.npz` olarak Drive'a. Eğitim notebook'u GEE'ye hiç bağlanmaz.
- **Kısa deneme:** Önce 1 il ve 3 epoch ile hatasız çalıştığını görün, sonra tam eğitime geçin.

## 3. Ortak kurulum (herkes, bir kez)

1. Selin'in Drive'daki `yapay-zeka-proje` klasörü A, B ve C ile **Düzenleyen** yetkisiyle paylaşılır.
2. Herkes kendi Drive'ında bu klasöre sağ tık → **Düzenle → Kısayol ekle → Drive'ım**. Böylece notebook'lardaki `/content/drive/MyDrive/yapay-zeka-proje` yolu herkeste çalışır.
3. Repo erişimi ve Colab'da `GITHUB_TOKEN` gizli anahtarı: README'deki adımlar.
4. GEE: yalnızca B için zorunlu (export). Diğerlerinin hesabı yalnızca kontrol amaçlıdır.

## 4. Görevler

### A — Kod düzeltmeleri, istatistik, panel (GPU gerekmez)
1. `config.py`: H1–H6 eşlemesi, alt bölge tanımları (B ile birlikte).
2. **03: mekânsal bölme.** Rastgele `train_test_split` yerine 10 km blok bazlı bölme (04'teki mantık). Sonuçlar yeniden hesaplanır, eski ve yeni değerler raporda yan yana verilir.
3. **IoU** (sınıf bazında ve ortalama) 03 ve 06'ya eklenir.
4. **XGBoost regresyonu** 04'teki LST regresyonuna eklenir (RF ve doğrusal regresyonun yanına).
5. 06'daki "neden göstergeleri" Spearman'ı notebook'ta hesaplanıp yalnızca ekrana yazdırılıyor → CSV'ye kaydedilsin, sınırlılık notundaki "elle hesaplandı" ifadesi düzeltilsin.
6. **Ölçek analizi:** 1 km hücreler ERA5-Land hücrelerine (~9 km) toplanır, sınıf oranları ↔ ERA5 toprak nemi/hava sıcaklığı ilişkisi hesaplanır.
7. Kuraklık göstergesi: CHIRPS'ten **SPI-3/SPI-12**; DEM'den **eğim**.
8. Hafta 3: **Streamlit paneli** (il seç → harita, değişim, iklim serisi, metrikler). Bulutta Streamlit Community Cloud'da yayınlanır.
9. Literatür: L01–L22 arasından 7 çalışma.
10. Rapor bölümleri: 3.4–3.7 (yöntem), 4.2–4.6 (bulgular).

### B — Sentinel-2 veri hattı (GEE, GPU gerekmez) + U-Net (GPU)
1. **00 kontrolü:** Türkiye için `COPERNICUS/S2_SR_HARMONIZED` 2017 yaz kapsamı var mı? (L2A küresel olarak Aralık 2018'den itibaren düzenli.) Yoksa başlangıç 2019 olur ya da 2017 için L1C kullanılır. Karar `config.py`'ye yazılır.
2. Alt bölge kareleri: il başına 2–3 kare (~20 × 20 km). Konu odaklı seçilir: İstanbul kent çeperi, Artvin orman havzası, Konya tarım ovası, Van Gölü kıyısı, Şanlıurfa Harran Ovası, Samsun delta, İzmir Gediz deltası/kent.
3. Yaz kompozitleri (bulut maskeli, 10 m bantlar + 20 m bantlar 10 m'ye) ve etiket olarak **ESA WorldCover 2021 (10 m, Sentinel-2 ile aynı çözünürlük)** Drive'a GeoTIFF olarak export edilir.
4. Yeni notebook `07_sentinel2_kareler.ipynb`: GeoTIFF → 256 × 256 kareler → `.npz` (eğitim/doğrulama/test **il ve blok bazında** ayrılır, sızıntı yok).
5. Literatür: L23–L35 arasından 7 çalışma (LST, kentsel ısı adası).
6. Rapor bölümleri: 3.1–3.3 (çalışma alanı, veri), 4.1 (veri tanıtımı).

### C — U-Net eğitimi ve değişim tespiti (GPU, Colab T4)
1. Yeni notebook `08_unet_siniflandirma.ipynb`: U-Net + ResNet-34, AMP, erken durdurma, checkpoint. B'nin kareleri gelene kadar sahte veriyle iskelet hazırlanır.
2. Metrikler: Accuracy, Precision, Recall, F1, **IoU (mIoU)**. RF ile **aynı test karelerinde** karşılaştırma (dokümandaki "önce RF, sonra U-Net").
3. **U-Net ile genelleme (H6):** 6 ilde eğit, 7. ilde test. B'nin GPU'suyla paralel, katmanlar ikiye bölünür.
4. 2017 ve 2025 karelerine uygulanır → sınıflandırma sonrası karşılaştırma, değişim matrisi.
5. Literatür: L36–L46 arasından 7 çalışma (Türkiye çalışmaları, genelleme).
6. Rapor bölümleri: 4.7 (genelleme), U-Net bulguları, 5 (Tartışma) taslağı.

### Herkes
- Okunan her çalışma `literature/literatur_matrisi.csv`'ye işlenir: `okundu_mu = evet`, yöntem, metrik, değer, ana bulgu. Toplam 21 çalışma (en az 20).
- `[DOĞRULANMADI]` iddialar kaynakla desteklenir: Yusufeli (Artvin, C), GAP sulaması (Şanlıurfa, A), Tuz Gölü (Konya, B), Kızılırmak/Yeşilırmak deltaları (Samsun, B), Van su artışı (B), İstanbul–İzmir ısı adası farkı (A).
- Raporu herkes kendi cümleleriyle yazar (Turnitin YZ oranı < %40).

## 5. Sıra ve bağımlılıklar

| Hafta | A | B | C |
|---|---|---|---|
| 1 | 03 mekânsal bölme, IoU, XGBoost regresyonu | S2 kapsam kontrolü, alt bölgeler, GEE export | U-Net iskeleti (sahte veri), literatür |
| 2 | ERA5 ölçeği, SPI, eğim, H1–H6 tablosu | Kareler `.npz` → Drive; U-Net LOCO'nun yarısı | U-Net eğitimi, RF karşılaştırması, LOCO'nun yarısı |
| 3 | Streamlit paneli | Rapor bölümleri | 2017→2025 değişim, rapor bölümleri |
| 4 | Ortak: rapor birleştirme, sunum, prova | | |

**Kritik yol:** B'nin kareleri → C'nin eğitimi. B gecikirse C, 1. haftada mevcut 1 ilde (Artvin) küçük bir deneme seti üzerinden ilerler.

## 6. Kapsam dışı (raporda "gelecek çalışma")
SegFormer · Siamese U-Net · Sentinel-1 radar · PostGIS · meteoroloji istasyonu verisi (erişim izni gerekir) · tüm illerin 10 m tam haritası.
