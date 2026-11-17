# Rapor iskeleti

> **Nasıl kullanılır:** Her bölümde *ne yazılacağı* madde olarak, *hangi sayı/tablo/şekil* kullanılacağı dosya adıyla, *hangi kaynağa* atıf yapılacağı ID ile (`literature/aday_calismalar.md`, L01–L46) verilmiştir. Paragrafları **kendi cümlelerinizle** yazın. `[SEN YAZ]` = sizin yorumunuz/cümleniz gereken yer.
>
> Tablolar: `Drive'ım/yapay-zeka-proje/results/tables/` · Şekiller: `.../results/figures/` · Sınırlılıklar ham listesi: `report/sinirliliklar_notlari.md`
>
> Tüm sayılar Colab çıktılarından alınmıştır. Raporda yazmadan önce ilgili CSV'den bir kez kontrol edin.
>
> **Bölüm yapısı hocanın kurallarına göre:** Özet · Giriş · Literatür Taraması · Deneysel Yöntemler · Bulgular · Tartışma · Sonuç (sınırlılıklar ve gelecek çalışmalar dahil) · Kaynakça. Başlıkları bu sırayla ve bu adlarla kullanın.
>
> **Hocanın özellikle istedikleri → raporda nerede:**
> | İstek | Yer |
> |---|---|
> | 20–30 akademik çalışma, yöntem + bulgu özeti | 2. Literatür Taraması (tablo) |
> | Veri kaynağı, özellikler, örnek sayısı, sınıf dağılımı, ortalama/medyan/mod | 3.3 + 4.1 |
> | Algoritmalar ve tercih nedenleri | 3.4 |
> | Hiperparametreler ve yapılan değişiklikler | 3.7 |
> | Accuracy, Precision, Recall, F1, ROC-AUC tablo + grafik | 4.2 |
> | Literatürle karşılaştırma | 5 (Tartışma) + `literatur_karsilastirma.csv` |
> | Güçlü yönler ve sınırlılıklar | 6.2, 6.3 |
> | Turnitin YZ oranı < %40 | Tüm paragrafları kendiniz yazın; bu dosyadaki maddeleri kopyalamayın |

---

## Kapak / Başlık
- Başlık: *Türkiye'de Coğrafi Değişimlerin İklimsel Etkilerinin Uydu Görüntüleriyle Yapay Zekâ Destekli Analizi*
- Ders, öğrenciler, tarih

## Özet (Abstract) (≈200–250 kelime) — `[SEN YAZ]`, en son yazın
Sırayla değinilecek noktalar:
- Problem: arazi örtüsü değişimi ↔ yüzey sıcaklığı/nem; 7 il, 2014 → 2024
- Veri: Landsat 8/9, ESA WorldCover 2021 etiketi, MODIS, ERA5-Land, CHIRPS; GEE
- Yöntem: 4 sınıflandırıcı (RF, XGBoost, SVM, MLP) → en iyi XGBoost; değişim + Spearman + Mann-Kendall + LST regresyonu (SHAP); LOCO genelleme
- Ana sayılar (en fazla 4–5 tane):
  - XGBoost test macro-F1 **0.783**, Kappa **0.742**
  - LST regresyonu R² **0.921**, RMSE **2.04 °C** (10 km mekânsal blok CV); en etkili: NDVI
  - Başka ile genellemede ortalama macro-F1 düşüşü **≈ 0.11** (en çok Konya −0.19)
- Bir cümle sınırlılık: ilişki, neden-sonuç değil

## 1. Giriş (Introduction)
### 1.1 Problem ve motivasyon — `[SEN YAZ]`
- Arazi örtüsü değişimi (kentleşme, orman/tarım değişimi, su alanları) yerel iklimi etkiler → L26, L27, L29
- Türkiye'de farklı iklim bölgeleri → tek bir model her yerde çalışır mı? (AS5)
- Uydu + makine öğrenmesi ile ölçeklenebilir izleme → L09, L02

### 1.2 Amaç ve alt sorular
Tablo olarak verin:

| Kod | Alt soru | İller | Notebook |
|---|---|---|---|
| AS1 | Orman/bitki örtüsü değişimi ile LST ilişkisi | Artvin, Şanlıurfa | 04 |
| AS2 | Yapılaşma ve kentsel ısı adası | İstanbul, İzmir | 04 |
| AS3 | Su/sulak alan değişimi ile sıcaklık ve nem | Konya, Van, Samsun | 04 |
| AS4 | Tarım değişimi ile toprak nemi ve LST | Konya, Şanlıurfa | 04 |
| AS5 | Bir ilde eğitilen model başka ilde ne kadar başarılı? | 7 il | 06 |

- Kapsam notu: İDA / yüzen atık tespiti çalışmanın dışında (ana araştırma sorusunu test etmiyor; Türkiye kıyı görüntüsü yok). Raporda bir cümleyle belirtin.

### 1.2b Hipotezler (GeoClimate AI) — kanıt: `hipotez_ozet.csv` (04 B9 + 06 bölüm 6)

| Hipotez | İfade | Test eden analiz |
|---|---|---|
| H1 | Yapılaşmış alan artışı ↔ LST artışı (pozitif) | Δyapılaşma–ΔLST, kentsel ısı adası (AS2) |
| H2 | Orman/bitki örtüsü azalması ↔ LST artışı | Δorman–ΔLST, ΔNDVI–ΔLST (AS1) |
| H3 | Tarım değişimi ↔ bitki örtüsü yoğunluğu ve nem | Δtarım–ΔNDMI, Δtarım–ΔLST (AS4) |
| H4 | Su/sulak alan değişimi ↔ sıcaklık ve nem | Δsu–ΔLST, Δsu–ΔNDMI (AS3) |
| H5 | İlişkiler bölgeye göre farklılaşır | Aynı ilişkinin 7 ildeki ρ aralığı ve işareti |
| H6 | Model başarısı bölgeye göre değişir | LOCO F1 düşüşü (AS5) |

- Her hipotez için Sonuç bölümünde "desteklendi / kısmen / desteklenmedi" yazın (`karar_[EKİP_YAZACAK]` sütunu). İlişki ≠ neden-sonuç.

### 1.3 Raporun düzeni — tek cümle `[SEN YAZ]`

## 2. Literatür Taraması (Literature Review)
- **Hoca 20–30 çalışmanın incelenmesini, yöntem ve bulgularının özetlenmesini istiyor.** Şu an `literatur_matrisi.csv`'de hiçbir çalışma "okundu" değil → **en büyük açık iş bu**.
- Önerilen 21 çalışma (veri/yazılım ve özgün algoritma makaleleri hariç; onlar yalnızca yöntem bölümünde atıf alır):
  - Sınıflandırma / LULC (5): L01, L02, L04, L32, L41
  - LST – arazi örtüsü / kentsel ısı adası (11): L26, L27, L28, L29, L30, L34, L35, L37, L39, L40, L38
  - İllere özel (2): L43 (Artvin/Yusufeli), L44 (Şanlıurfa)
  - Mekânsal doğrulama / genelleme (3): L21, L22, L46
- Rapordaki tablo (her çalışma 1 satır): Yazar (yıl) · Bölge · Veri/sensör · Yöntem · Metrik ve değer · Ana bulgu · Bizimle ilişkisi → `literatur_matrisi.csv` sütunlarından
- Tablonun altında 2–3 paragraf karşılaştırma `[SEN YAZ]`: hangi yöntemler yaygın, hangi değerler raporlanmış, bizim çalışma nerede duruyor
- Karşılaştırma tablosu: `literature/literatur_karsilastirma.csv` (bizim değerler dolu, literatür değerleri `[MAKALEDEN DOLDUR]`)
- Alt başlıklar ve kaynaklar:
  - 2.1 ML ile arazi örtüsü sınıflandırması → L01, L02, L04, L05 (Türkiye: L32, L41)
  - 2.2 Arazi örtüsü – LST ilişkisi ve kentsel ısı adası → L26–L29; Türkiye: L30, L31, L34–L40
  - 2.3 İllere özel çalışmalar → Artvin/Yusufeli L43; Şanlıurfa L44; Konya L40; Samsun L41; Van `[DOĞRULANMADI]`
  - 2.4 Mekânsal doğrulama ve genelleme → L21, L22, L23, L45, L46
- Bu çalışmanın farkı (madde): 7 il aynı yöntemle · iki yıl karşılaştırma + 22 yıllık iklim serisi · mekânsal blok CV · LOCO genelleme testi · SHAP — `[SEN YAZ]`
- **Eksik:** 1. öncelikli makalelerin bulguları `literatur_matrisi.csv`'ye yazılmalı (sizden bekleniyor)

## 3. Deneysel Yöntemler (Experimental Methods)
### 3.1 Çalışma alanı
- 7 il, il sınırları FAO GAUL (L09 platform) — şekil: 00'daki il sınırları haritası (yoksa `rgb_kompozitler.png`)
- Neden bu iller: alt soru tablosuna bağla

### 3.2 Veri setleri
- Tablo: README "Veri kaynakları ve lisanslar" tablosu (kısaltılmış) → L10–L16
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
- Metrikler: Accuracy, Precision, Recall, F1 (macro), ROC-AUC, Kappa (Kappa eleştirisi L20), IoU (`sinif_bazinda_iou.csv`)
- Mekânsal blok doğrulama (03 bölüm 10b): rastgele bölme ile 10 km blok GroupKFold karşılaştırması → L21, L23; `mekansal_blok_ozet.csv`, `mekansal_blok_dogrulama.png`
- Açıklanabilirlik: SHAP (L24)

### 3.5 Değişim analizi (04, AS1–AS4)
- Yöntem şeması (şekil önerisi — sunumda da kullanılır): 1 km hücre → 3×3 = 9 nokta → GEE'den bant değerleri → Colab'da XGBoost → hücre oranları → 2014/2024 farkı
- Neden örneklem: tam il sınıflandırması GEE kotasını aştı (sınırlılıklar)
- Kontrol: grid eşleşme %98.1 (`lc_nokta_ozet.csv`); GEE–Colab model farkı +0.0097 (`gee_vs_colab_karsilastirma.csv`)
- İklim trendi: Mann-Kendall + Sen eğimi, 2003–2024 (MODIS L13, ERA5 L14, CHIRPS L15)
- Hücre düzeyi ilişki: Spearman (Δ değişkenler)
- Kentsel ısı adası: kentsel (>%50 yapı) − kırsal (<%5 yapı, ±200 m rakım)
- Su: MNDWI > 0; JRC (L16) ile 2021 karşılaştırması
- LST regresyonu: RF Regressor + XGBoost Regressor + doğrusal regresyon, 10 km mekânsal blok GroupKFold (5 katman) → L21, L22; SHAP

### 3.6 Bölgeler arası genelleme (06, AS5)
- Leave-One-City-Out: 6 ilde eğit, 7.'de test; aynı-şehir sonuçlarıyla aynı test noktalarında karşılaştırma → L22, L23
- Neden göstergeleri: spektral kayma, sınıf dağılımı farkı, iklim ortalamaları

### 3.7 Hiperparametreler ve yapılan değişiklikler
- Tablo 1 — arama uzayı ve seçilen değerler: `hiperparametre_arama.csv` (model × parametre × aralık × seçilen); arama ayarları `config.py`
- Tablo 2 — süreç içinde yapılan değişiklikler (neden + etkisi), maddeler:
  - Kapsam daraltma: 2019 çıkarıldı, il başına 2 000 nokta, n_iter=10, 3-katlı CV (süre)
  - NDMI modelden çıkarıldı (Landsat'ta NDMI = −NDBI, aynı bilgi)
  - SAVI, BSI 1 km grid'den çıkarıldı (GEE bellek sınırı)
  - Değişim analizi tam haritadan 9 nokta/hücre örneklemesine geçti (GEE zaman aşımı/bellek)
  - İDA / yüzen atık modülü kapsamdan çıkarıldı (ana soruyu test etmiyor, Türkiye verisi yok)
  - LST regresyonunda mekânsal blok tanımı düzeltildi (ilk sürüm il bazlı CV yapıyordu; R² −0.26 → 0.921)
  - Kaynak: `on_isleme_kararlari.csv`, `model_gerekceleri.csv`, `report/sinirliliklar_notlari.md`

## 4. Bulgular (Results)
> Her alt bölümde: 1 tablo + 1–2 şekil + 2–4 maddelik gözlem. Yorum/neden kısmı Tartışma'ya.

### 4.1 Veri seti tanıtımı (02)
- Tablo: `veri_seti_ozeti.csv`, `sinif_dagilimi.csv`
- **Tanımlayıcı istatistik (hoca: ortalama, medyan, mod):** `tanimlayici_istatistik.csv` (ortalama, std, medyan, mod vb. her özellik için); sınıf bazında `sinif_bazinda_ortalama.csv`, `sinif_bazinda_medyan.csv`; iklim `iklim_tanimlayici_istatistik.csv`
- Grafikler: `sinif_dagilimi.png`, `histogramlar.png`, `kutu_grafikleri_indeksler.png`, `kutu_grafikleri_sehir.png`, `korelasyon_isi_haritasi.png`
- Eksik ve aykırı değer: `eksik_deger.csv`, `aykiri_deger.csv`
- Gözlem: Artvin'de Tarım (108) ve Yapılaşma (104) az örnek; otsu sulak alan Su/Sulak'ın %6'sı

### 4.2 Sınıflandırma sonuçları (03)
- **Hoca bu 5 metriği açıkça istiyor:** Accuracy, Precision, Recall, F1-Score, ROC-AUC. Tablo `model_karsilastirma.csv` (test kümesi) — eksik hücreleri CSV'den doldurun:

| Model | Accuracy | Precision (macro) | Recall (macro) | F1 (macro) | ROC-AUC (macro, OvR) | Kappa | IoU (macro) |
|---|---|---|---|---|---|---|---|
| XGBoost (doğrulamada en iyi) | 0.785 | 0.784 | 0.783 | 0.783 | 0.961 | 0.742 | 0.657 |
| MLP | 0.791 | 0.791 | 0.790 | 0.789 | 0.964 | 0.749 | 0.664 |
| SVM | 0.778 | 0.777 | 0.775 | 0.772 | 0.959 | 0.733 | 0.644 |
| RF | 0.768 | 0.766 | 0.765 | 0.764 | 0.957 | 0.721 | 0.633 |

- Kaynak: Drive `model_karsilastirma.csv` (Faz 3). IoU: `sinif_bazinda_iou.csv`, Drive'daki **resmi model dosyalarından** (`tools/resmi_model_iou.py`; dört modelin accuracy ve F1'i resmi tabloyla birebir aynı). Not: aynı ayarlarla başka bir bilgisayarda yeniden eğitim birebir aynı ağaçları üretmedi (xgboost sürümü Colab'dakiyle aynı, 3.4.1; olası neden işletim sistemi/işlemci farkı); bu yüzden yeniden eğitilen XGBoost 0.776 verdi, raporda resmi değerler kullanılır.
- Sınıf bazında IoU (XGBoost, resmi): Orman 0.71, **Tarım 0.42** (en zayıf), Yapılaşma 0.67, Çayır/Çalı 0.57, Çıplak 0.66, Su/Sulak 0.92
- **Mekânsal blok doğrulama** (`mekansal_blok_ozet.csv`, 5 katlı CV, 1 327 blok): macro-F1 rastgele → 10 km blok: RF 0.773 → 0.761, XGBoost 0.786 → 0.773, SVM 0.775 → 0.768, MLP 0.787 → 0.780. **Fark en fazla 0.013** → 300 m mesafe filtresi mekânsal sızıntıyı büyük ölçüde önlemiş; blok doğrulamada katmanlar arası std 2–4 kat büyük (±0.012–0.022).

- Sınıf bazında Precision/Recall/F1: `sinif_raporu_XGBoost.csv`, `sinif_bazinda_f1.csv`; sınıf bazında ROC-AUC: `roc_auc_sinif_bazinda.csv`

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
- Tablo: `lst_regresyon_metrikleri.csv` (111 950 hücre, 1 435 blok, 10 km blok CV):

| Model | R² | RMSE (°C) | MAE (°C) |
|---|---|---|---|
| Random Forest | 0.921 | 2.04 | 1.52 |
| XGBoost | 0.921 | 2.04 | 1.54 |
| Doğrusal (çoklu) regresyon | 0.824 | 3.04 | 2.38 |

- RF ve XGBoost neredeyse aynı → R² 0.92 tek bir modele özgü değil; doğrusal modelden belirgin iyi → ilişkiler doğrusal değil
- Şekil: `lst_regresyon_shap.png`
- SHAP sırası: NDVI 4.81 °C (−), rakım 2.28 °C (−), MNDWI 0.61, Su/Sulak oranı 0.52, Tarım oranı 0.30 (+) …

### 4.7 Bölgeler arası genelleme (06)
- Tablo: `genelleme_dusus.csv` (7 il × aynı/başka şehir macro-F1)
- Şekiller: `genelleme_isi_haritasi.png`, `genelleme_dusus.png`, `genelleme_sinif_bazinda.png`
- Gözlemler: ortalama düşüş ≈ 0.11; en çok Konya (−0.187), Şanlıurfa (−0.147), Van (−0.125); en az Artvin (−0.059); en zor sınıf Tarım; Konya Su/Sulak 0.89 → 0.39
- `genelleme_neden_gostergeleri.csv`: düşüş yağışla ρ ≈ −0.96 (n = 7, `genelleme_neden_spearman.csv` — raporda n'yi belirtin)

### 4.9 Hipotezler (H1–H6) — `hipotez_ozet.csv`, `hipotez_kanit_H1_H5.png`
Sayılar otomatik; **karar sütununu siz yazın** (öneri parantez içinde, tartışarak kesinleştirin):

| Hipotez | Kanıt (7 il) | Öneri |
|---|---|---|
| H1 Yapılaşma ↑ ↔ LST ↑ | Δyapı–ΔLST ρ −0.04…+0.15, yalnızca İstanbul ≥ 0.1; UHI İstanbul +8.1/+8.0 °C, İzmir +1.2/+1.5 °C | (kısmen: ısı adası belirgin, hücre düzeyinde değişim ilişkisi çok zayıf) |
| H2 Orman/bitki ↓ ↔ LST ↑ | ΔNDVI–ΔLST **7/7 ilde negatif, ρ −0.41…−0.65** (orta–güçlü); Δorman–ΔLST 6/7 ilde ≤ −0.1 | (desteklendi; en güçlü bulgu) |
| H3 Tarım ↔ bitki/nem | Δtarım–ΔNDMI 4 ilde ≥ 0.1, en güçlü Konya +0.39; Δtarım–ΔLST zayıf | (kısmen; kurak iç illerde belirgin) |
| H4 Su ↔ sıcaklık/nem | Δsu–ΔLST yalnızca Artvin −0.19, İstanbul −0.13; Δsu–ΔNDMI hiçbir ilde ≥ 0.1 | (büyük ölçüde desteklenmedi; 1 km'de su değişimi küçük) |
| H5 Bölgeye göre farklılaşır | Aynı ilişkinin iller arası ρ aralığı 0.07–0.33 (en geniş Δtarım–ΔNDMI); işaret değişen ilişki yok | (kısmen: güç değişiyor, yön değişmiyor) |
| H6 Genelleme bölgeye göre değişir | LOCO macro-F1 düşüşü XGBoost ort. 0.109 (Artvin 0.059 … Konya 0.187); düşüş–yağış ρ = −0.96 (n = 7) | (desteklendi; kurak illerde daha büyük düşüş) |

## 5. Tartışma (Discussion) — `[SEN YAZ]` (her madde için 2–4 cümle, literatürle)
- **Hoca: sonuçlar literatürle karşılaştırılmalı** → her maddede en az bir çalışmanın değeriyle yan yana koyun (`literatur_karsilastirma.csv`); veri/bölge/sınıf farkını mutlaka belirtin
- Sınıflandırma başarısı literatürle nasıl? → L04, L32, L41 (değerler `literatur_karsilastirma.csv`)
- NDVI–LST negatif ilişkisi literatürle uyumlu mu? → L26, L27, L34, L35
- Şanlıurfa: tarım artışı + yaz LST düşüşü → sulama (GAP) ile tutarlı mı? → L44 (kaynakla destekleyin, neden-sonuç demeyin)
- Artvin: orman artışı ve su +%78.9 → Yusufeli barajı → L43
- İstanbul–İzmir UHI farkı neden bu kadar büyük? (tanım, kırsal referans, deniz etkisi) → L28, L29, L30, L36
- Korelasyonların zayıf olması: 9 noktalı hücre gürültüsü, iki tek yaz kompoziti, otokorelasyon
- Genelleme: kurak illerde daha büyük düşüş; mekânsal doğrulama literatürüyle uyum → L22, L23, L46

## 6. Sonuç (Conclusion)
> Hocanın yapısında sınırlılıklar ve gelecek çalışmalar Sonuç bölümünün içinde.

### 6.1 Genel değerlendirme — `[SEN YAZ]` (her alt soruya bir cümlelik cevap: AS1 … AS5)

### 6.2 Güçlü yönler (madde → cümleye çevirin)
- 7 il aynı yöntem ve aynı veriyle; 4 model karşılaştırması
- Mekânsal blok CV ve LOCO ile gerçekçi başarı ölçümü (sızıntıya karşı)
- SHAP ile açıklanabilirlik
- 22 yıllık iklim serisi + iki yıllık değişim
- Tamamen açık veri ve tekrarlanabilir kod (GitHub, RANDOM_STATE = 42)

### 6.3 Sınırlılıklar
- Ham liste: `report/sinirliliklar_notlari.md` — en önemli 6–8 maddeyi seçin:
  1. Etiket yalnızca 2021 → 2014/2024 doğruluğu ölçülemiyor
  2. İlişki ≠ neden-sonuç; n büyük, ρ küçük
  3. Örneklem tabanlı (9 nokta/hücre) değişim tahmini
  4. Tek yaz kompoziti; 2014 L8, 2024 L8+9
  5. Su/Sulak sınıfı iki farklı yüzeyi birleştiriyor
  6. LOCO'da küçük test kümeleri (±0.05)
  7. Kapsam daraltma: 2 yıl, 2 000 nokta/il, n_iter=10

### 6.4 Gelecek çalışmalar (madde)
- Çok mevsimli kompozit / Sentinel-1 ile sulak alan
- 2019 ara yılı ve yıllık zaman serisi
- Bağımsız referans verisiyle 2014/2024 doğruluk değerlendirmesi (L19)
- Kurak iller için bölgesel model veya alan uyarlaması (L46)

## Kaynakça (References)
- `literature/aday_calismalar.md` tablolarından; yalnızca metinde atıf yaptıklarınız
- Veri setleri ve yazılım (GEE, scikit-learn, XGBoost, SHAP) künyeleri aynı dosyanın sonunda
- `[DOĞRULANMADI]` olanları kullanmayın

## Ekler (isteğe bağlı)
- Tüm modellerin karışıklık matrisleri (`karisiklik_matrisleri_tumu.png`)
- Hiperparametre tablosu, sınıf bazında ROC-AUC
- GEE kota kullanımı (`gee_kota_kullanimi.csv`, toplam ≈ 45.9 EECU-saat)
- Kod: GitHub reposu, `config.py` (RANDOM_STATE = 42)
