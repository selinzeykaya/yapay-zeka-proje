# Rapor iskeleti

> **Nasıl kullanılır:** Her bölümde *ne yazılacağı* madde olarak, *hangi sayı/tablo/şekil* kullanılacağı dosya adıyla, *hangi kaynağa* atıf yapılacağı ID ile (`literature/aday_calismalar.md`, L01–L56) verilmiştir. Paragrafları **kendi cümlelerinizle** yazın. `[SEN YAZ]` = sizin yorumunuz/cümleniz gereken yer.
>
> Tablolar: `Drive'ım/yapay-zeka-proje/results/tables/` · Şekiller: `.../results/figures/` · Sınırlılıklar ham listesi: `report/sinirliliklar_notlari.md`
>
> Tüm sayılar Colab çıktılarından alınmıştır. Raporda yazmadan önce ilgili CSV'den bir kez kontrol edin.

---

## Kapak / Başlık
- Başlık: *Türkiye'de Coğrafi Değişimlerin İklimsel Etkilerinin Uydu ve İDA Görüntüleriyle Yapay Zekâ Destekli Analizi*
- Ders, öğrenciler, tarih

## Özet (≈200–250 kelime) — `[SEN YAZ]`, en son yazın
Sırayla değinilecek noktalar:
- Problem: arazi örtüsü değişimi ↔ yüzey sıcaklığı/nem; 7 il, 2014 → 2024
- Veri: Landsat 8/9, ESA WorldCover 2021 etiketi, MODIS, ERA5-Land, CHIRPS; GEE
- Yöntem: 4 sınıflandırıcı (RF, XGBoost, SVM, MLP) → en iyi XGBoost; değişim + Spearman + Mann-Kendall + LST regresyonu (SHAP); LOCO genelleme; YOLOv8n (açık veri)
- Ana sayılar (en fazla 4–5 tane):
  - XGBoost test macro-F1 **0.783**, Kappa **0.742**
  - LST regresyonu R² **0.921**, RMSE **2.04 °C** (10 km mekânsal blok CV); en etkili: NDVI
  - Başka ile genellemede ortalama macro-F1 düşüşü **≈ 0.11** (en çok Konya −0.19)
  - YOLOv8n mAP50 **0.388** (Endonezya nehir veri seti — Türkiye verisi değil)
- Bir cümle sınırlılık: ilişki, neden-sonuç değil

## 1. Giriş
### 1.1 Problem ve motivasyon — `[SEN YAZ]`
- Arazi örtüsü değişimi (kentleşme, orman/tarım değişimi, su alanları) yerel iklimi etkiler → L26, L27, L29
- Türkiye'de farklı iklim bölgeleri → tek bir model her yerde çalışır mı? (AS5)
- Uydu + makine öğrenmesi ile ölçeklenebilir izleme → L09, L02
- Su yüzeyinde atık izleme (İDA) → L48, L54

### 1.2 Amaç ve alt sorular
Tablo olarak verin:

| Kod | Alt soru | İller | Notebook |
|---|---|---|---|
| AS1 | Orman/bitki örtüsü değişimi ile LST ilişkisi | Artvin, Şanlıurfa | 04 |
| AS2 | Yapılaşma ve kentsel ısı adası | İstanbul, İzmir | 04 |
| AS3 | Su/sulak alan değişimi ile sıcaklık ve nem | Konya, Van, Samsun | 04 |
| AS4 | Tarım değişimi ile toprak nemi ve LST | Konya, Şanlıurfa | 04 |
| AS5 | Bir ilde eğitilen model başka ilde ne kadar başarılı? | 7 il | 06 |
| AS6 | Su yüzeyinde yüzen atık tespiti (YOLOv8n) | Açık veri seti (Endonezya) | 05 |

- AS6 notu: Türkiye verisi **değil**; İstanbul/İzmir kıyıları yalnızca *gelecekteki uygulama alanı*.

### 1.3 Raporun düzeni — tek cümle `[SEN YAZ]`

## 2. Literatür
- Tablo: `literature/literatur_karsilastirma.csv` (bizim değerler dolu, literatür değerleri `[MAKALEDEN DOLDUR]`)
- Alt başlıklar ve kaynaklar:
  - 2.1 ML ile arazi örtüsü sınıflandırması → L01, L02, L04, L05 (Türkiye: L32, L41)
  - 2.2 Arazi örtüsü – LST ilişkisi ve kentsel ısı adası → L26–L29; Türkiye: L30, L31, L34–L40
  - 2.3 İllere özel çalışmalar → Artvin/Yusufeli L43; Şanlıurfa L44; Konya L40; Samsun L41; Van `[DOĞRULANMADI]`
  - 2.4 Mekânsal doğrulama ve genelleme → L21, L22, L23, L45, L46
  - 2.5 Yüzen atık tespiti → L48, L50, L51, L53, L54
- Bu çalışmanın farkı (madde): 7 il aynı yöntemle · iki yıl karşılaştırma + 22 yıllık iklim serisi · mekânsal blok CV · LOCO genelleme testi · SHAP — `[SEN YAZ]`
- **Eksik:** 1. öncelikli makalelerin bulguları `literatur_matrisi.csv`'ye yazılmalı (sizden bekleniyor)

## 3. Veri ve Yöntem
### 3.1 Çalışma alanı
- 7 il, il sınırları FAO GAUL (L09 platform) — şekil: 00'daki il sınırları haritası (yoksa `rgb_kompozitler.png`)
- Neden bu iller: alt soru tablosuna bağla

### 3.2 Veri setleri
- Tablo: README "Veri kaynakları ve lisanslar" tablosu (kısaltılmış) → L10–L16, L47
- Yaz kompoziti Haziran–Ağustos; 2014 yalnızca Landsat 8, 2024 Landsat 8+9 (sınırlılık)
- Etiket: ESA WorldCover 2021 (L12) → 6 sınıf: Orman, Tarım, Yapılaşma, Çayır/Çalı, Çıplak, Su/Sulak

### 3.3 Ön işleme ve örnekleme (02)
- 13 251 nokta (hedef 13 986), 3×3 homojen pencere, 300 m mesafe filtresi
- Özellikler: Landsat bantları + NDVI, NDBI (L18), MNDWI (L17) vb. — 11 özellik; NDMI = −NDBI olduğu için modelden çıkarıldı
- Tablolar: `veri_seti_ozeti.csv`, `sinif_dagilimi.csv`, `on_isleme_kararlari.csv`
- Şekiller: `sinif_dagilimi.png`, `kutu_grafikleri_indeksler.png`, `korelasyon_isi_haritasi.png`

### 3.4 Sınıflandırma modelleri (03)
- 4 model: RF (L06), XGBoost (L08), SVM (L07), MLP; gerekçe tablosu `model_gerekceleri.csv`
- Hiperparametre: rastgele arama n_iter=10, 3-katlı CV (`hiperparametre_arama.csv`); seçim doğrulama macro-F1 ile
- Veri bölme: `veri_bolme.csv`
- Metrikler: Accuracy, Precision, Recall, F1 (macro), ROC-AUC, Kappa (Kappa eleştirisi L20)
- Açıklanabilirlik: SHAP (L24)

### 3.5 Değişim analizi (04, AS1–AS4)
- Yöntem şeması (şekil önerisi — sunumda da kullanılır): 1 km hücre → 3×3 = 9 nokta → GEE'den bant değerleri → Colab'da XGBoost → hücre oranları → 2014/2024 farkı
- Neden örneklem: tam il sınıflandırması GEE kotasını aştı (sınırlılıklar)
- Kontrol: grid eşleşme %98.1 (`lc_nokta_ozet.csv`); GEE–Colab model farkı +0.0097 (`gee_vs_colab_karsilastirma.csv`)
- İklim trendi: Mann-Kendall + Sen eğimi, 2003–2024 (MODIS L13, ERA5 L14, CHIRPS L15)
- Hücre düzeyi ilişki: Spearman (Δ değişkenler)
- Kentsel ısı adası: kentsel (>%50 yapı) − kırsal (<%5 yapı, ±200 m rakım)
- Su: MNDWI > 0; JRC (L16) ile 2021 karşılaştırması
- LST regresyonu: RF Regressor + doğrusal regresyon, 10 km mekânsal blok GroupKFold (5 katman) → L21, L22; SHAP

### 3.6 Bölgeler arası genelleme (06, AS5)
- Leave-One-City-Out: 6 ilde eğit, 7.'de test; aynı-şehir sonuçlarıyla aynı test noktalarında karşılaştırma → L22, L23
- Neden göstergeleri: spektral kayma, sınıf dağılımı farkı, iklim ortalamaları

### 3.7 Yüzen atık tespiti (05, AS6)
- Veri: Radam ve ark. (L47), 1 577 görüntü, 2 sınıf (floating_waste, river_vegetation), Endonezya nehirleri, CC BY 4.0
- Model: YOLOv8n (L49), transfer öğrenme; metrikler P, R, F1, mAP50, mAP50-95 (L56)
- FloW-Img kullanılamadı (erişim) → yalnızca "farklı veri setinde raporlanan değerler" (L48)

## 4. Bulgular
> Her alt bölümde: 1 tablo + 1–2 şekil + 2–4 maddelik gözlem. Yorum/neden kısmı Tartışma'ya.

### 4.1 Veri seti tanıtımı (02)
- Tablo: `veri_seti_ozeti.csv`, `sinif_dagilimi.csv`
- Gözlem: Artvin'de Tarım (108) ve Yapılaşma (104) az örnek; otsu sulak alan Su/Sulak'ın %6'sı

### 4.2 Sınıflandırma sonuçları (03)
- Tablo `model_karsilastirma.csv`:

| Model | Test macro-F1 |
|---|---|
| XGBoost (doğrulamada en iyi) | 0.783 (acc 0.785, Kappa 0.742, ROC-AUC 0.961) |
| MLP | 0.789 |
| SVM | 0.772 |
| RF | 0.764 |

- Not: Model seçimi **doğrulama** kümesine göre yapıldı; testte MLP biraz önde ama fark küçük → `[SEN YAZ]` (neden test'e göre seçmediğimiz)
- Şekiller: `model_karsilastirma.png`, `karisiklik_matrisi_XGBoost.png`, `sinif_bazinda_f1.png`, `roc_tumu.png`, `shap_XGBoost.png`
- Gözlemler: Tarım F1 ≈ 0.59 (Çayır/Orman ile karışıyor); Yapılaşma ↔ Çıplak karışması; SHAP'ta SR_B7 ve MNDWI öne çıkıyor; otsu sulak alan recall 0.44 (n=18)

### 4.3 Arazi örtüsü değişimi 2014 → 2024 (04 B1–B2)
- Tablolar: `sinif_alanlari_degisim.csv`, `gecis_matrisi.csv`
- Şekiller: `degisim_haritalari.png`, `sinif_degisim_pp.png`, `gecis_matrisleri.png`
- Öne çıkanlar: Artvin orman +5.55 pp; Şanlıurfa tarım +4.13 pp, orman +1.99 pp; İstanbul yapılaşma +0.64 pp; İzmir +0.56 pp; Konya tarım −0.13 pp

### 4.4 İklim trendleri 2003–2024 (04 B3)
- Tablo: `iklim_trend_mann_kendall.csv`; şekiller `iklim_serileri.png`, `iklim_trend_ozet.png`
- Anlamlı olanlar: Şanlıurfa MODIS yaz LST **−1.44 °C/10 yıl (p = 0.0001)**; Van yaz toprak nemi −0.017/10 yıl (p = 0.024)
- Anlamlı olmayanlar da yazılmalı (ör. Artvin LST p = 0.955; AS3 illerinin yağış trendlerinin hiçbiri p < 0.05 değil; diğer iller için CSV'ye bakın)

### 4.5 Alt soru bulguları (04 B4, B6, B7) — `alt_soru_ozet_AS1_AS4.csv`
Tablo önerisi (rapor için kısaltılmış):

| AS | İl | Değişim | En ilgili ilişki |
|---|---|---|---|
| AS1 | Artvin | Orman +5.55 pp | ΔNDVI–ΔLST ρ = −0.41 |
| AS1 | Şanlıurfa | Orman +1.99 pp | ΔNDVI–ΔLST ρ = −0.65 |
| AS2 | İstanbul | Yapılaşma +0.64 pp | UHI +8.14 → +8.00 °C; Δyapı–ΔLST ρ = +0.15 |
| AS2 | İzmir | Yapılaşma +0.56 pp | UHI +1.18 → +1.49 °C; Δyapı–ΔLST ρ = +0.05 |
| AS3 | Konya | Su −%1.4 | Δsu–ΔLST ρ = −0.09 |
| AS3 | Van | Su +%12.1 | Δsu–ΔLST ρ = −0.02 |
| AS3 | Samsun | Su +%9.0 | Δsu–ΔLST ρ = −0.04 |
| AS4 | Konya | Tarım −0.13 pp | Δtarım–ΔNDMI ρ = +0.39 |
| AS4 | Şanlıurfa | Tarım +4.13 pp | Δtarım–ΔNDMI ρ = +0.10 |

- Şekiller: `spearman_isi_haritasi.png`, `degisim_iklim_dagilim.png`, `kentsel_isi_adasi.png`, `su_alani_degisim.png`
- Tüm p < 0.001 (Şanlıurfa Δtarım–ΔLST hariç, p = 0.093) ama çoğu |ρ| < 0.2 → "anlamlı ama zayıf"

### 4.6 LST regresyonu (04 B5)
- Tablo: `lst_regresyon_metrikleri.csv` — RF R² 0.921, RMSE 2.04 °C, MAE 1.52 °C (111 950 hücre, 1 435 blok); doğrusal regresyon satırını da CSV'den ekleyin
- Şekil: `lst_regresyon_shap.png`
- SHAP sırası: NDVI 4.81 °C (−), rakım 2.28 °C (−), MNDWI 0.61, Su/Sulak oranı 0.52, Tarım oranı 0.30 (+) …

### 4.7 Bölgeler arası genelleme (06)
- Tablo: `genelleme_dusus.csv` (7 il × aynı/başka şehir macro-F1)
- Şekiller: `genelleme_isi_haritasi.png`, `genelleme_dusus.png`, `genelleme_sinif_bazinda.png`
- Gözlemler: ortalama düşüş ≈ 0.11; en çok Konya (−0.187), Şanlıurfa (−0.147), Van (−0.125); en az Artvin (−0.059); en zor sınıf Tarım; Konya Su/Sulak 0.89 → 0.39
- `genelleme_neden_gostergeleri.csv`: düşüş yağışla ρ ≈ −0.96 (n = 7, elle hesap — raporda belirtin)

### 4.8 Yüzen atık tespiti (05)
- Tablo `ida_metrikleri.csv`: TÜMÜ P 0.500, R 0.388, F1 0.437, mAP50 0.388, mAP50-95 0.121; floating_waste mAP50 0.414, river_vegetation 0.362; n_test = 158; 5.39 ms/görüntü
- Şekiller: `ida_eda.png`, `ida_egitim_egrileri.png`, `ida_ornek_tespitler.png`, PR eğrisi
- Literatür değerleri yalnızca "farklı veri setinde" (`ida_literatur_karsilastirma.csv`)

## 5. Tartışma — `[SEN YAZ]` (her madde için 2–4 cümle, literatürle)
- Sınıflandırma başarısı literatürle nasıl? → L04, L32, L41 (değerler `literatur_karsilastirma.csv`)
- NDVI–LST negatif ilişkisi literatürle uyumlu mu? → L26, L27, L34, L35
- Şanlıurfa: tarım artışı + yaz LST düşüşü → sulama (GAP) ile tutarlı mı? → L44 (kaynakla destekleyin, neden-sonuç demeyin)
- Artvin: orman artışı ve su +%78.9 → Yusufeli barajı → L43
- İstanbul–İzmir UHI farkı neden bu kadar büyük? (tanım, kırsal referans, deniz etkisi) → L28, L29, L30, L36
- Korelasyonların zayıf olması: 9 noktalı hücre gürültüsü, iki tek yaz kompoziti, otokorelasyon
- Genelleme: kurak illerde daha büyük düşüş; mekânsal doğrulama literatürüyle uyum → L22, L23, L46
- İDA: mAP50 0.388 düşük/orta; küçük nesne, bulanık su, 2 sınıf karışması → L50, L51, L53

## 6. Sınırlılıklar
- Ham liste: `report/sinirliliklar_notlari.md` — en önemli 6–8 maddeyi seçin:
  1. Etiket yalnızca 2021 → 2014/2024 doğruluğu ölçülemiyor
  2. İlişki ≠ neden-sonuç; n büyük, ρ küçük
  3. Örneklem tabanlı (9 nokta/hücre) değişim tahmini
  4. Tek yaz kompoziti; 2014 L8, 2024 L8+9
  5. Su/Sulak sınıfı iki farklı yüzeyi birleştiriyor
  6. LOCO'da küçük test kümeleri (±0.05)
  7. İDA verisi Türkiye verisi değil; FloW erişilemedi
  8. Kapsam daraltma: 2 yıl, 2 000 nokta/il, n_iter=10, yalnızca YOLOv8n

## 7. Gelecek çalışmalar (madde)
- Çok mevsimli kompozit / Sentinel-1 ile sulak alan
- 2019 ara yılı ve yıllık zaman serisi
- Bağımsız referans verisiyle 2014/2024 doğruluk değerlendirmesi (L19)
- Kurak iller için bölgesel model veya alan uyarlaması (L46)
- Türkiye kıyılarında İDA görüntüsü toplama ve modeli yeniden değerlendirme

## 8. Sonuç — `[SEN YAZ]` (her alt soruya bir cümlelik cevap: AS1 … AS6)

## Kaynakça
- `literature/aday_calismalar.md` tablolarından; yalnızca metinde atıf yaptıklarınız
- Veri setleri ve yazılım (GEE, scikit-learn, XGBoost, Ultralytics, SHAP) künyeleri aynı dosyanın sonunda
- `[DOĞRULANMADI]` olanları kullanmayın

## Ekler (isteğe bağlı)
- Tüm modellerin karışıklık matrisleri (`karisiklik_matrisleri_tumu.png`)
- Hiperparametre tablosu, sınıf bazında ROC-AUC
- GEE kota kullanımı (`gee_kota_kullanimi.csv`, toplam ≈ 45.9 EECU-saat)
- Kod: GitHub reposu, `config.py` (RANDOM_STATE = 42)
