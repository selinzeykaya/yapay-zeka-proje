# Ne yaptık, neden yaptık? — Kavramlar, kararlar ve dosya haritası

> Bu belge, projede kullanılan her terimi ve bizim (Amine + Claude) `amine/geoclimate-uyum` dalında yaptığımız her değişikliği **hiç bilmeyen birine anlatır gibi** açıklar. Amaç: biri "neden?" diye sorduğunda cevap verebilmek.
>
> Okuma sırası: 1 → 2 → 3 → 4 kavramları öğretir; 5 bizim yaptıklarımızı anlatır; 6 dosyaların yerini gösterir; 7 olası soruların cevaplarıdır.

---

## 1. Büyük resim: Proje ne yapıyor?

Soru şu: **Türkiye'de araziler değişiyor (şehir büyüyor, orman azalıyor/artıyor, tarım değişiyor, göller küçülüyor). Bu değişimler yerel sıcaklık ve nemle ilişkili mi? Ve bunu yapay zekâyla ölçebilir miyiz?**

Akış 5 adımdır:

```
1. Uydu görüntüsü al          (Landsat, Google Earth Engine)
2. Her pikselin ne olduğunu   (orman mı, tarım mı, şehir mi...)  → yapay zekâ ile sınıflandır
3. İki yılı karşılaştır       (2014 ↔ 2024: ne değişti?)
4. Değişimi iklimle eşleştir  (değişen yerde sıcaklık/nem de değişti mi?)
5. Bölgeler arası karşılaştır (bir ilde öğrenen model başka ilde de çalışıyor mu?)
```

Projede 7 il var. GeoClimate dokümanındaki 4 il (İstanbul, Artvin, Konya, Van) **ana odak**; İzmir, Samsun ve Şanlıurfa karşılaştırma ve genelleme için.

---

## 2. Uzaktan algılama ve veri kavramları

### Uzaktan algılama
Bir yere gitmeden, uzaktan (uydudan) ölçüm yapmak. Uydu, yeryüzünün yansıttığı ışığı farklı "renklerde" ölçer.

### Piksel ve çözünürlük
Uydu görüntüsü küçük karelerden (piksel) oluşur. **Çözünürlük** bir pikselin yerdeki boyutudur:
- Landsat: 30 m × 30 m (bir piksel ≈ yarım futbol sahası)
- Sentinel-2: 10 m × 10 m (daha keskin)
- ERA5-Land iklim verisi: ~9–11 km (bir piksel bir ilçe büyüklüğünde)

**Neden önemli?** Çözünürlüğü çok farklı verileri doğrudan karşılaştıramazsın. 9 km'lik bir sıcaklık değeri, içindeki 30 m'lik tek bir tarlayı anlatamaz. Bu yüzden projede 30 m veriler **1 km'lik hücrelere ortalanıyor**.

### Bant
Uydunun ölçtüğü her "renk" kanalı. İnsan gözü 3 renk görür (kırmızı, yeşil, mavi). Landsat bunların yanında gözün görmediği **yakın kızılötesi (NIR)** ve **kısa dalga kızılötesi (SWIR)** de ölçer. Projede kullanılanlar: `SR_B2` (mavi), `SR_B3` (yeşil), `SR_B4` (kırmızı), `SR_B5` (NIR), `SR_B6` (SWIR1), `SR_B7` (SWIR2). "SR" = Surface Reflectance (yüzey yansıması, atmosfer etkisi düzeltilmiş).

### Spektral indeks
İki bandı formülle birleştirip tek bir anlamlı sayı üretmek. Hepsi −1 ile +1 arasındadır.

| İndeks | Formül | Ne gösterir | Neden çalışır |
|---|---|---|---|
| **NDVI** | (NIR − Kırmızı) / (NIR + Kırmızı) | Bitki örtüsü yoğunluğu | Sağlıklı yaprak kırmızıyı emer, NIR'ı çok yansıtır |
| **NDBI** | (SWIR1 − NIR) / (SWIR1 + NIR) | Yapılaşma (beton) | Beton SWIR'ı NIR'dan çok yansıtır |
| **MNDWI** | (Yeşil − SWIR1) / (Yeşil + SWIR1) | Su yüzeyi | Su SWIR'ı neredeyse tamamen emer |
| **NDMI** | (NIR − SWIR1) / (NIR + SWIR1) | Bitki/yüzey nemi | Nemli bitki SWIR'ı emer |
| SAVI, BSI | (benzer formüller) | Seyrek bitki, çıplak toprak | |

**Önemli tuzak:** NDMI = −NDBI (aynı iki bant, ters işaret). Bu yüzden Selin NDMI'yı modelden çıkardı: model aynı bilgiyi iki kez görmesin. NDMI yalnızca nem göstergesi olarak kullanılıyor.

**NDVI iklim değişkeni değildir.** Bitki örtüsünü gösteren bir göstergedir. Raporda "iklim göstergesi" diye yazmayın.

### Kompozit ve bulut maskesi
Tek bir gün bulutlu olabilir. Bu yüzden **bir yazın (Haziran–Ağustos) bütün görüntüleri** üst üste konup her piksel için ortanca (medyan) değer alınır. Buna **kompozit** denir. Bulut ve gölge pikselleri önce **maskelenir** (çıkarılır). Her yıl için aynı mevsim kullanılır, çünkü yaz ve kış görüntüsü karşılaştırılırsa mevsim farkı "arazi değişimi" gibi görünür.

### LST (Land Surface Temperature, arazi yüzey sıcaklığı)
Yüzeyin (asfalt, toprak, yaprak) **kendi sıcaklığı**. Landsat'ın termal bandından hesaplanır. **Hava sıcaklığı değildir!** Yazın asfalt 55 °C olurken hava 35 °C olabilir. Projede:
- Landsat LST (30 m): değişim analizi ve regresyon
- MODIS LST (1 km, 2003–2024): uzun dönem trend

### Veri kaynakları

| Kaynak | Ne | Projede neden |
|---|---|---|
| **Landsat 8/9** | NASA/USGS uydusu, 30 m, 2013'ten beri | 2014 ve 2024'ü karşılaştırmak için (Sentinel-2 2014'te yoktu) |
| **ESA WorldCover 2021** | Avrupa Uzay Ajansı'nın hazır dünya arazi örtüsü haritası (10 m) | Modelin "doğru cevapları" (etiket). Yalnızca 2021 için var |
| **MODIS** | Günlük gözlem yapan, 1 km çözünürlüklü uydu | 2003–2024 yaz yüzey sıcaklığı trendi |
| **ERA5-Land** | Avrupa'nın iklim "yeniden analiz" verisi (ölçüm + model) | Toprak nemi, 2 m hava sıcaklığı |
| **CHIRPS** | Uydu + istasyon tabanlı yağış verisi | Yıllık yağış |
| **JRC Su** | 1984–2021 su yüzeyi haritası | MNDWI su alanını kontrol etmek |
| **SRTM** | Yükselti (rakım) haritası | Dağ serinliğini kontrol etmek |
| **FAO GAUL** | İl sınırları | Çalışma alanını kesmek |

### Google Earth Engine (GEE)
Google'ın uydu verisi platformu. Bütün bu veriler orada hazır, hesap Google'ın sunucularında yapılır; biz indirmeden işleriz. Ücretsiz akademik kullanımda **ayda 150 EECU-saat** kota var (EECU = hesap birimi). Kota bittiğinde iş durur; bu yüzden Selin önce Artvin'de "pilot" yapıp kotayı ölçtü.

### Colab, GPU, CPU
- **Colab:** Google'ın tarayıcıda çalışan Python ortamı. Kod Google'ın bilgisayarında çalışır.
- **CPU:** Bilgisayarın genel işlemcisi. İstatistik, Random Forest, XGBoost için yeterli.
- **GPU:** Ekran kartı. Aynı anda binlerce küçük hesap yapar; **derin öğrenme (U-Net)** için gerekli. Senin bilgisayarında NVIDIA GPU yok (Intel Iris Xe), o yüzden U-Net Colab'ın T4 GPU'sunda eğitilecek.

---

## 3. Yapay zekâ / makine öğrenmesi kavramları

### Denetimli sınıflandırma
Modele örnekler ve doğru cevapları gösterilir ("bu piksel orman, bu tarım"), model aradaki kuralı öğrenir, sonra görmediği piksellere cevap verir.
- **Özellik (feature):** Modelin baktığı sayılar → 6 bant + 5 indeks = 11 özellik.
- **Etiket (label):** Doğru cevap → WorldCover sınıfı.
- **Sınıflar (6):** Orman, Tarım, Yapılaşma, Çayır/Çalı, Çıplak, Su/Sulak.

### Eğitim / doğrulama / test
Veri üçe bölünür:
- **Eğitim (%70):** Model buradan öğrenir.
- **Doğrulama (%15):** Modeller arasında seçim yapılır ("hangisi daha iyi?").
- **Test (%15):** En sona saklanır, **bir kez** kullanılır. Sınav kâğıdı gibidir: önceden görülürse sonuç sahte olur.

### Hiperparametre ve çapraz doğrulama (CV)
- **Hiperparametre:** Modelin öğrenmediği, bizim seçtiğimiz ayarlar (ağaç sayısı, derinlik...).
- **RandomizedSearchCV:** Ayar aralıklarından rastgele 10 kombinasyon dener.
- **Çapraz doğrulama (k-katlı CV):** Eğitim verisi k parçaya bölünür; model k−1 parçada eğitilip kalan parçada test edilir; bu k kez tekrarlanır ve ortalama alınır. Tek bir şanslı/şanssız bölmeye bağlı kalmamak için.

### Kullanılan modeller

| Model | Basit anlatım | Neden seçildi |
|---|---|---|
| **Random Forest (RF)** | Yüzlerce karar ağacı ("NDVI > 0.5 mi? → evet → MNDWI < 0 mı?...") ayrı ayrı oy verir, çoğunluk kazanır | Uzaktan algılamada en yaygın temel model; dayanıklı. GeoClimate'te "önce RF" deniyor |
| **XGBoost** | Ağaçlar sırayla eklenir; her yeni ağaç öncekilerin hatasını düzeltir (boosting) | Tablo verisinde genelde en güçlüsü. Projede en iyi model |
| **SVM** | Sınıflar arasına mümkün olan en geniş boşluklu sınırı çizer | Klasik uzaktan algılamada çok kullanılmış; karşılaştırma için |
| **MLP** | Basit yapay sinir ağı (katmanlı nöronlar) | Derin öğrenmeye giriş; esnek |
| **U-Net** *(planlanan)* | Görüntünün tamamına bakıp her piksele sınıf veren derin öğrenme ağı (segmentasyon). Pikselin komşularını da görür | GeoClimate'te isteniyor. Mevcut 4 model pikselleri tek tek, komşusuz sınıflandırıyor |

### Metrikler
Bir sınıf için, örneğin "Su":
- **TP** (doğru pozitif): Gerçekte su, model de su dedi.
- **FP** (yanlış alarm): Gerçekte su değil, model su dedi.
- **FN** (kaçırma): Gerçekte su, model başka bir şey dedi.

| Metrik | Formül | Sorduğu soru |
|---|---|---|
| **Accuracy** | doğru / tümü | Toplamda yüzde kaçını bildik? |
| **Precision** | TP / (TP+FP) | "Su" dediklerimizin kaçı gerçekten su? |
| **Recall** | TP / (TP+FN) | Gerçek suların kaçını bulduk? |
| **F1** | 2·P·R / (P+R) | Precision ve Recall'un dengesi |
| **ROC-AUC** | ROC eğrisi altındaki alan | Model olasılıklarıyla sınıfları ne kadar iyi sıralıyor? 0.5 = yazı-tura, 1 = mükemmel |
| **Kappa** | şans düzeltilmiş uyum | Şansa doğru tahminler çıkarılınca kalan başarı |
| **IoU** (Jaccard) | TP / (TP+FP+FN) | Tahmin edilen alan ile gerçek alan ne kadar örtüşüyor? |

- **Macro ortalama:** Her sınıfın puanı eşit ağırlıkla ortalanır. Küçük sınıflardaki başarısızlık gizlenmez. Ana metriğimiz **macro-F1**.
- **IoU ile F1 farkı:** IoU, F1'den daha serttir. Bir sınıf için **IoU = F1 / (2 − F1)**. Örnek: F1 = 0.80 → IoU = 0.67. Yani IoU'nun düşük çıkması kötüleşme değil, ölçünün doğasıdır.

**Projenin mevcut sonuçları (03, test kümesi):**

| Model | Accuracy | Precision | Recall | macro-F1 | ROC-AUC | Kappa |
|---|---|---|---|---|---|---|
| XGBoost (seçilen) | 0.785 | 0.784 | 0.783 | 0.783 | 0.961 | 0.742 |
| MLP | 0.791 | 0.791 | 0.790 | 0.789 | 0.964 | 0.749 |
| SVM | 0.778 | 0.777 | 0.775 | 0.772 | 0.959 | 0.733 |
| RF | 0.768 | 0.766 | 0.765 | 0.764 | 0.957 | 0.721 |

**"MLP testte daha iyi, neden XGBoost seçildi?"** Çünkü seçim **doğrulama** kümesine göre yapılır. Test kümesine bakarak seçseydik testi "kopya çekmek" için kullanmış olurduk. Fark (0.006) da çok küçük.

---

## 4. Sızıntı, mekân ve istatistik kavramları

### Veri sızıntısı (data leakage)
Test bilgisinin bir şekilde eğitime karışması. Sonuç olduğundan iyi görünür ama gerçek hayatta model o kadar iyi çalışmaz.

### Mekânsal otokorelasyon
**"Yakın yerler birbirine benzer."** (Tobler'in coğrafya yasası.) Aynı ormanın iki ucundaki piksel neredeyse aynıdır. Rastgele bölmede biri eğitime, diğeri teste düşerse model aslında "ezberlediği" bir yeri test ediyor olur → **mekânsal sızıntı**.

Selin'in önlemleri:
1. Noktalar arası en az **300 m** mesafe.
2. 04'teki regresyonda **mekânsal blok CV**.

### Mekânsal blok çapraz doğrulama
Harita **10 km × 10 km karelere (blok)** bölünür. Bir bloktaki bütün noktalar **hep birlikte** ya eğitime ya teste gider (scikit-learn'de `GroupKFold`). Böylece test noktasının yakın komşuları eğitimde olmaz. Daha zor ama daha dürüst bir sınavdır.

### Leave-One-City-Out (LOCO)
Bir il tamamen dışarıda bırakılır, model kalan 6 ille eğitilip o ilde test edilir. 7 kez tekrarlanır. "Model hiç görmediği bir ilde çalışır mı?" sorusunun (H6) cevabıdır. Sonuç: macro-F1 ortalama **0.11** düşüyor, en çok Konya'da (−0.19).

Üç sınavın zorluk sırası: **rastgele bölme** (en kolay) → **mekânsal blok** (komşu yok ama il tanıdık) → **LOCO** (il tamamen yabancı).

### Korelasyon, Spearman, ρ
- **Korelasyon:** İki şey birlikte artıyor/azalıyor mu? −1 (tam ters) … 0 (ilişki yok) … +1 (tam birlikte).
- **Spearman (ρ, "ro"):** Değerlerin kendisi yerine **sıralarını** kullanır. Doğrusal olmayan ilişkileri de yakalar ve aykırı değerlerden az etkilenir. **Pearson** ise yalnızca düz çizgi ilişkiyi ölçer.
- **Güç kuralı (bizim tabloda):** |ρ| < 0.1 ihmal edilebilir, 0.1–0.3 zayıf, 0.3–0.5 orta, ≥ 0.5 güçlü.

### p-değeri ve neden ona güvenmiyoruz
p-değeri: "Gerçekte hiç ilişki yokken bu kadar güçlü bir sonucu tesadüfen görme olasılığı." p < 0.05 genelde "anlamlı" sayılır. **Ama:**
1. 100.000 hücre gibi çok büyük örneklemde **çok zayıf** ilişkiler bile p < 0.001 çıkar.
2. Komşu hücreler bağımsız olmadığı için (otokorelasyon) p olduğundan küçük çıkar.

Bu yüzden raporda **"istatistiksel olarak anlamlı ama zayıf"** deriz ve ρ'nun büyüklüğüne bakarız.

### Korelasyon ≠ nedensellik
"Tarım arttı ve sıcaklık düştü" → bu **ilişkidir**, "tarım sıcaklığı düşürdü" demek değildir. Arada üçüncü bir neden (ör. sulama, yağışlı bir yıl) olabilir. Raporda hep "ilişkili" deyin.

### Mann-Kendall testi ve Sen eğimi
- **Mann-Kendall:** Bir zaman serisinde (2003–2024) düzenli bir artış/azalış eğilimi var mı? Normal dağılım varsaymaz, aykırı yıllara dayanıklıdır. İklim serilerinde standart testtir.
- **Sen eğimi:** Eğilimin büyüklüğü (ör. "10 yılda −1.44 °C"). Tüm yıl çiftleri arasındaki eğimlerin ortancasıdır. **Arazi eğimiyle (slope) karıştırmayın**: o dağın dikliğidir, bu trendin hızıdır.

### Regresyon, R², RMSE, MAE
- **Regresyon:** Bir sayıyı (LST) diğer sayılardan (NDVI, sınıf oranları, rakım) tahmin etmek.
- **R²:** Değişkenliğin yüzde kaçı açıklanıyor (1 = tamamı). 0.921 → %92.
- **RMSE:** Tipik hata (°C); büyük hataları daha çok cezalandırır.
- **MAE:** Ortalama mutlak hata (°C).

Mevcut sonuç (04): RF R² **0.921**, RMSE 2.04 °C; doğrusal regresyon R² 0.824, RMSE 3.04 °C.

### SHAP
Bir modelin tahmininde **her özelliğin ne kadar ve hangi yönde pay sahibi olduğunu** hesaplar (oyun teorisinden). LST regresyonunda en etkili NDVI (4.81 °C), sonra rakım (2.28 °C). SHAP "model neye bakıyor"u söyler, **neden-sonucu söylemez**.

### Hipotez
Önceden kurulan, verinin test edeceği iddia (ör. "Yapılaşma artınca LST artar"). Verinin cevabı üç türlü olabilir: **desteklendi / kısmen desteklendi / desteklenmedi**.

---

## 5. Bizim yaptıklarımız — neden, nasıl, nerede

### 5.1 Repoyu indirdim ve sana özel dal açtım
- **Ne:** `git clone` ile repo `C:\Users\ozsen\yapay-zeka-proje` klasörüne indirildi. `amine/geoclimate-uyum` adında bir **dal (branch)** açıldı.
- **Dal nedir?** Projenin bir kopya kolu. Biz burada değiştiririz, `main` (Selin'in ana kolu) bozulmaz. Beğenilirse sonra birleştirilir (merge / Pull Request).
- **Commit:** Değişikliklerin kaydedilmiş bir "anlık fotoğrafı". Her biri bir açıklama mesajı taşır.
- **Push yapmadım:** Push = GitHub'a göndermek. Başkasının reposuna izinsiz gönderilmez. Göndermek istediğinde söylemen yeterli.

### 5.2 İDA'yı çıkardık (commit `0f29f83`)
- **Neden:** (1) Deniz yüzeyinde atık tespiti, ana soruyu (arazi değişimi ↔ iklim) test etmiyor. (2) Elimizdeki tek İDA verisi Endonezya nehirlerinden; İstanbul/İzmir olamazdı. Senin kararın: **C seçeneği**.
- **Nasıl:** 05 notebook'u silindi (git geçmişinde duruyor, geri getirilebilir); `config.py`'den İDA ayarları, `requirements.txt`'den `ultralytics`, raporlardan İDA bölümleri, literatürden L47–L56 çıkarıldı. Yerlerine tek cümlelik kapsam notu kondu.
- **Sonuç:** Alt sorular AS1–AS5, önerilen literatür 21 çalışma (hâlâ 20–30 aralığında).

### 5.3 Görev planı (`plan/gorev_dagilimi.md`)
Üç kişilik iş bölümü, Colab/GPU kuralları, hafta hafta sıra. Başında "repoda zaten yapılmış olanlar" tablosu var.

### 5.4 IoU metriği eklendi
- **Neden:** GeoClimate dokümanı istiyor; ileride U-Net (segmentasyon) sonuçlarıyla aynı ölçüyle karşılaştırma sağlıyor.
- **Nasıl:** `src/ml_utils.py` içindeki `compute_metrics` fonksiyonuna `iou_macro` ve `iou_weighted` eklendi (`jaccard_score`). Bu fonksiyonu 03 ve 06 kullandığı için ikisinde de **otomatik** hesaplanıyor.
- **Nerede:** 03 → bölüm **7a** (sınıf bazında IoU). Çıktı: `results/tables/sinif_bazinda_iou.csv`, `results/figures/sinif_bazinda_iou.png`.

### 5.5 03'e mekânsal blok doğrulama eklendi
- **Neden:** 03'teki bölme rastgele. GeoClimate "mekânsal sızıntı önlenecek" diyor. Rastgele bölme başarıyı şişiriyor mu, ölçmemiz lazım.
- **Neden mevcut bölmeyi değiştirmedik?** 04 (değişim haritaları) ve 06 (genelleme) o bölmeye ve o modele bağlı. Değiştirseydik her şeyi yeniden hesaplamak ve Earth Engine kotası harcamak gerekirdi. Bunun yerine **ek bir test** yaptık: aynı modeller, aynı ayarlar, iki ayrı 5 katlı CV (rastgele ve 10 km blok), sonuçlar yan yana.
- **Nasıl:** Noktaların enlem/boylamı metreye çevrilir (`pyproj`, EPSG:3035 eşit alanlı projeksiyon); koordinat 10.000'e bölünerek blok numarası bulunur; `GroupKFold` ile bölünür.
- **Nerede:** 03 → bölüm **10b**. Çıktılar: `mekansal_blok_dogrulama.csv` (katman katman), `mekansal_blok_ozet.csv` (ortalama ± std), `mekansal_blok_dogrulama.png`.
- **Yorum:** Fark küçükse (≈0.01–0.02) 300 m filtresi işe yaramış; büyükse (≥0.05) rapordaki "gerçekçi başarı" blok sonucu olmalı.

### 5.6 04'e XGBoost regresyonu eklendi
- **Neden:** GeoClimate'te isteniyor. Ayrıca "R² = 0.92 Random Forest'a özgü mü?" sorusunu kontrol ediyor: iki farklı model benzer sonuç verirse bulgu sağlamdır.
- **Nerede:** 04 → **B5**. Çıktı: `lst_regresyon_metrikleri.csv` artık 3 satır (RF, XGBoost, doğrusal). SHAP ve özet tablolar RF üzerinden kalıyor.

### 5.7 H1–H6 hipotez tabloları
- **Neden:** GeoClimate dokümanı 6 hipotez tanımlıyor; repo ise AS1–AS5 alt sorularıyla çalışıyordu. Analizler aslında hipotezleri test ediyordu, sadece eşleştirilmemişti.
- **Nasıl:**
  - `config.py` → `HYPOTHESES` sözlüğü (her hipotezin metni ve ilgili alt sorusu).
  - 04 → **B9**: H1–H5 için 7 ilin hepsinde ilgili Spearman ρ alınır, beklenen yönle karşılaştırılır (H1: +, H2: −), güç sınıfı yazılır. H5 için aynı ilişkinin iller arasında ne kadar değiştiğine bakılır (ρ aralığı, işaret değişiyor mu).
  - 06 → **bölüm 6**: H6 (LOCO düşüşü) eklenir ve hepsi tek tabloda birleştirilir.
- **Çıktılar:** `hipotez_kanit_H1_H5.csv` (il il), `hipotez_ozet_H1_H5.csv`, `hipotez_kanit_H1_H5.png`, `hipotez_ozet.csv` (H1–H6).
- **Karar sütunu (`karar_[EKİP_YAZACAK]`) bilerek boş:** "Desteklendi mi" yorumu ekibin işi. Hem bilimsel yorumdur hem de raporu kendiniz yazmanız gerekiyor (Turnitin).

### 5.8 06'daki Spearman artık kaydediliyor
Eskiden yalnızca ekrana yazdırılıyordu. Şimdi `genelleme_neden_spearman.csv` dosyasına kaydediliyor. Sınırlılık notundaki "elle hesaplandı" ifadesi düzeltildi.

### 5.9 `GITHUB_BRANCH` ayarı
- **Sorun:** Notebook'lar Colab'da açılınca hep `main` dalını çekiyordu; senin dalındaki değişiklikler Colab'a gelmiyordu.
- **Çözüm:** Her notebook'un kurulum hücresine `GITHUB_BRANCH = "main"` satırı eklendi. Kendi dalını denemek için bunu `"amine/geoclimate-uyum"` yapman yeterli (önce dalın GitHub'a push edilmiş olması gerekir).

### 5.10 Drive'dan veri indirdim, analizleri yerelde çalıştırıyorum
- Paylaştığın Drive klasörü bağlantıya sahip herkese açık. 67 tablo ve gereken veri dosyaları geçici bir çalışma klasörüne indirildi. **Drive'daki hiçbir dosya değiştirilmedi.**
- Yeni analizler GPU istemediği için senin bilgisayarında gerçek veriyle çalıştırılabiliyor. Bunun için geçici bir **sanal ortam (venv)** kuruldu: sistem Python'una dokunmadan gerekli paketleri (pandas, scikit-learn, xgboost...) içine kurduğumuz ayrı bir kutu.
- İlk kurulum takıldı: bilgisayardaki Python 3.14 için pip paketleri kaynaktan derlemeye çalışıyordu. `--only-binary` seçeneğiyle hazır paket kullanmaya zorladım.
- İkinci takılma: C diski doluydu (4,85 GB boş) ve pip'in indirme bağlantısı takılıyordu. Çözüm: her şey D'ye taşındı (`D:\geoclimate-calisma`), paket listesi pip ile çıkarıldı, dosyalar `curl` ile indirildi, pip internete çıkmadan bu dosyalardan kurdu. Docker Desktop'ın 12 GB'lık diski de D'ye taşındı; C'de boş alan 17 GB oldu.
- Fan neden çalıştı? LST regresyonu 112 bin hücrede 300 ağaçlı modeli 5 kez eğitiyor ve hızlı olsun diye bütün işlemci çekirdeklerini kullanıyor (`n_jobs=-1`). Normal ve zararsız.

### 5.12 GitHub Actions (otomatik kontrol)
- **Ne:** `.github/workflows/ci.yml`. GitHub, her push'ta kendi sunucusunda (ubuntu-latest, Python 3.12) repoyu indirip kontroller yapar; sonuç yeşil ✅ ya da kırmızı ❌.
- **Neden analizleri değil de kontrolleri çalıştırıyor?** Analizler Earth Engine girişi ve Drive'daki büyük veriyi ister; bunlar GitHub'ın sunucusunda yok. CI'nın işi "bu değişiklik kodu bozdu mu?" sorusunu her seferinde otomatik sormak.
- **Kontroller:** (1) `tools/notebook_kontrol.py`: notebook JSON'u, kod hücrelerinin sözdizimi, çıktı kaydedilmemiş olması, `GITHUB_BRANCH` ayarı. (2) `tests/test_config.py`: alt sorulardaki iller tanımlı mı, hipotezler doğru alt sorulara bağlı mı, NDMI modelde yok mu, bölme oranları toplamı 1 mi. (3) `tests/test_ml_utils.py`: kusursuz tahminde metrikler 1 mi, IoU = F1/(2−F1) tutuyor mu, 4 model eğitilebiliyor mu, arama aralıkları modele uyuyor mu.
- **Ayrıntılar:** `permissions: contents: read` (iş akışı repoya yazamaz), `concurrency` (art arda push'ta eskisi iptal), `cache: pip` (paketler önbellekten, daha hızlı), `workflow_dispatch` (Actions sekmesinden elle çalıştırma).

### 5.11 Sonuçlar (gerçek veriyle, 16.11.2026)

**Önce kontrol:** Modeller Faz 3'teki ayarlarla yeniden eğitildi. RF, SVM, MLP Drive'daki sonuçlarla **birebir** aynı çıktı → veri ve bölme doğru kuruldu. XGBoost 0.776 (Drive: 0.783): sürüm aynı (3.4.1), yeniden eğitim başka bilgisayarda birebir aynı ağaçları üretmedi. Resmi model dosyası doğrudan değerlendirilince 0.783 birebir çıkıyor (`tools/resmi_model_iou.py`); raporda Drive değeri kullanılır.

**IoU (macro, resmi modellerden):** RF 0.633 · XGBoost 0.657 · SVM 0.644 · MLP 0.664. En zayıf Tarım (≈0.42), en güçlü Su (≈0.92).

**Mekânsal blok doğrulama (macro-F1, rastgele → 10 km blok):** RF 0.773 → 0.761 · XGBoost 0.786 → 0.773 · SVM 0.775 → 0.768 · MLP 0.787 → 0.780. Fark en fazla 0.013 → sızıntı küçük, 03'ün sonuçları güvenilir.

**LST regresyonu (R² / RMSE):** RF 0.921 / 2.04 °C · XGBoost 0.921 / 2.04 °C · doğrusal 0.824 / 3.04 °C → sonuç modele özgü değil; ilişki doğrusal değil.

**Hipotezler (karar ekibin; öneriler):**
- H1 (yapılaşma ↔ LST): kısmen. Isı adası belirgin (İstanbul +8 °C) ama hücre düzeyinde Δyapı–ΔLST çok zayıf (ρ ≤ 0.15).
- H2 (bitki ↓ ↔ LST ↑): **desteklendi, en güçlü bulgu.** ΔNDVI–ΔLST 7 ilin hepsinde negatif, ρ −0.41…−0.65.
- H3 (tarım ↔ nem): kısmen. Δtarım–ΔNDMI Konya'da +0.39, Van'da +0.28; diğerlerinde zayıf.
- H4 (su ↔ sıcaklık/nem): büyük ölçüde desteklenmedi. Yalnızca Artvin (−0.19) ve İstanbul (−0.13) zayıf ilişki.
- H5 (bölgeye göre farklı): kısmen. İlişkinin gücü ilden ile değişiyor (aralık 0.07–0.33) ama yönü hiçbir ilişkide değişmiyor.
- H6 (genelleme): desteklendi. Başka ilde ortalama 0.11 macro-F1 kaybı; kurak illerde daha büyük (yağışla ρ = −0.96, n = 7).

Yeni dosyalar: `D:\geoclimate-calisma\yeni_sonuclar\` (tables + figures) → Drive `results/` altına yüklenmeli.

---

## 6. Dosya haritası

### 6.1 Repo (`C:\Users\ozsen\yapay-zeka-proje`)

```
config.py                 Tüm ayarlar: iller, yıllar, sınıflar, model aralıkları, HYPOTHESES
requirements.txt          Gerekli Python paketleri
src/
  gee_utils.py            Earth Engine yardımcıları (kompozit, export, sınıflandırıcı)
  ml_utils.py             Modeller ve metrikler (compute_metrics → IoU burada)
notebooks/                Sırayla çalıştırılır: 00 → 01 → 02 → 03 → 04 → 06 (05 yok, İDA çıkarıldı)
literature/
  aday_calismalar.md      46 aday makale (DOI doğrulanmış)
  literatur_matrisi.csv   Okunan makalelerin bulguları buraya (henüz boş!)
  literatur_karsilastirma.csv  Bizim sonuç ↔ literatür değeri
report/
  rapor_iskeleti.md       Raporun bölüm bölüm planı (H1–H6 tablosu eklendi)
  sinirliliklar_notlari.md  Sınırlılıklar için ham notlar
  teslim_kontrol_listesi.md Hocanın teslim kuralları
presentation/
  sunum_iskeleti.md, olasi_sorular.md, proje_rehberi.html
plan/
  gorev_dagilimi.md       3 kişilik görev planı
  yapilanlar_ve_kavramlar.md  Bu belge
```

### 6.2 Notebook → ne yapar → hangi dosyayı üretir

| Notebook | Ne yapar | GPU/GEE | Ürettiği önemli dosyalar |
|---|---|---|---|
| **00** | Kurulum, il sınırları, erişim testi | GEE | `erisim_kontrolu.csv`, `sehir_sinirlari.png` |
| **01** | Kompozitler, etiketli noktalar, 1 km grid, iklim serileri | GEE (kota!) | `samples_2021.csv`, `grid_1km_2014_2024.csv`, `iklim_sehir_yillik.csv` |
| **02** | Tanımlayıcı istatistik, grafikler | CPU | `tanimlayici_istatistik.csv`, `sinif_dagilimi.png` |
| **03** | 4 model, metrikler, SHAP, **IoU (7a)**, **mekânsal blok (10b)** | CPU | `model_karsilastirma.csv`, `best_model.joblib`, **`sinif_bazinda_iou.csv`**, **`mekansal_blok_ozet.csv`** |
| **04** | Değişim, trend, Spearman, ısı adası, LST regresyonu (**+XGBoost**), **hipotezler (B9)** | GEE (baş kısım) + CPU | `sinif_alanlari_degisim.csv`, `spearman_degisim_iklim.csv`, `lst_regresyon_metrikleri.csv`, **`hipotez_ozet_H1_H5.csv`** |
| **06** | LOCO genelleme, **H6 + hepsi (bölüm 6)** | CPU | `genelleme_dusus.csv`, **`genelleme_neden_spearman.csv`**, **`hipotez_ozet.csv`** |

Kalın olanlar bizim eklediklerimiz.

### 6.3 Google Drive (`Drive'ım/yapay-zeka-proje/`)

```
data/processed/   İşlenmiş veri: samples_2021.csv, grid_1km_*.csv, iklim_sehir_yillik.csv ...
data/raw/gee/     Earth Engine export'ları (ara dosyalar)
results/tables/   Bütün CSV sonuçlar (raporun sayıları buradan)
results/figures/  Bütün grafikler (raporun şekilleri buradan)
results/models/   Eğitilmiş modeller (.joblib)
results/ida/      Eski İDA çıktıları (artık kullanılmıyor)
```

**Kural:** Kod GitHub'da, veri ve sonuçlar Drive'da. Büyük dosyalar GitHub'a konmaz.

### 6.4 Commit'lerimiz (sırayla)

| Commit | Ne |
|---|---|
| `0f29f83` | İDA modülü çıkarıldı |
| `a9d01fe` | Görev planı |
| `64fb5fe` | Plana "yapılmış olanlar" tablosu |
| `0778e76` | IoU, mekânsal blok doğrulama, XGBoost regresyonu, H1–H6, dal seçimi |

---

## 7. "Neden?" diye sorulursa — kısa cevaplar

**Neden 7 il?** Türkiye'nin farklı iklim ve coğrafyalarını temsil ediyorlar: kent (İstanbul, İzmir), nemli orman (Artvin, Samsun), kurak tarım (Konya, Şanlıurfa), göl havzası (Van). Ana odak GeoClimate'teki 4 il; diğer 3 il genelleme testini güçlendiriyor.

**Neden Landsat, Sentinel-2 değil?** 2014'ü 2024 ile karşılaştırıyoruz; Sentinel-2 2015'te fırlatıldı. Landsat 2013'ten beri aynı sensörle çalışıyor. Sentinel-2 + U-Net, 2017–2025 için ek adım olarak planlandı.

**Neden etiket 2021?** ESA WorldCover yalnızca 2020 ve 2021 için var; 2021 (v200) daha doğru sürüm. Sınırlılık: 2014 ve 2024 haritalarının doğruluğunu ölçemiyoruz.

**Neden yaz kompoziti?** Bulut az, bitki dönemi belirgin; her yıl aynı mevsim kullanılınca mevsim farkı değişim gibi görünmüyor.

**Neden 1 km hücre?** 30 m pikseller çok gürültülü ve iklim verileri kaba çözünürlükte; 1 km ikisi arasında bir denge. ERA5 (~9–11 km) 1 km'ye bile çok kaba olduğu için yalnızca il ölçeğinde kullanılıyor.

**Neden Spearman, Pearson değil?** İlişkiler düz çizgi olmayabilir ve aykırı hücreler var; Spearman sıralara baktığı için ikisine de dayanıklı.

**Korelasyonlar neden zayıf (|ρ| < 0.2)?** Hücre oranları 9 noktadan geliyor (gürültülü), iki tek yaz karşılaştırılıyor (hava farkı), ve gerçek dünyada sıcaklığı tek bir değişken belirlemiyor.

**p < 0.001 ise neden "zayıf" diyorsunuz?** Çok büyük örneklemde en küçük ilişki bile anlamlı çıkar; önemli olan ρ'nun büyüklüğü.

**Neden XGBoost seçildi, MLP testte daha iyiyken?** Seçim doğrulama kümesine göre yapıldı; teste bakarak seçmek kopya çekmek olurdu. Fark 0.006, ihmal edilebilir.

**IoU neden F1'den düşük?** Formülü gereği: IoU = F1 / (2 − F1). Daha sert bir ölçü; U-Net literatürüyle karşılaştırma için ekledik.

**Mekânsal blok doğrulama neden gerekli?** Yakın yerler birbirine benzer; rastgele bölmede model "komşusunu" görmüş olur ve başarı şişer. 10 km bloklar komşuları ayırıyor.

**Neden 03'teki bölmeyi değiştirmediniz?** 04 ve 06 o bölmeye bağlı; değiştirmek her şeyi yeniden hesaplamayı ve Earth Engine kotası harcamayı gerektirirdi. Ek test olarak yan yana koymak hem dürüst hem ucuz.

**LOCO ne gösteriyor?** Model hiç görmediği ilde ortalama 0.11 macro-F1 kaybediyor, en çok kurak illerde. Yani "bir ilde eğit, her yerde kullan" demek doğru değil (H6).

**Neden İDA yok?** Ana araştırma sorusunu test etmiyordu ve İstanbul/İzmir'e ait İDA görüntüsü yoktu; başka ülkenin verisiyle Türkiye sonucu veremezdik.

**SHAP'ta NDVI en önemli çıktı, demek ki bitki sıcaklığı düşürüyor mu?** SHAP modelin neye baktığını söyler, neden-sonucu değil. Literatürle (NDVI–LST negatif ilişkisi) tutarlı olduğunu söyleyebiliriz.

**Neden GPU yok, nasıl U-Net eğiteceksiniz?** Colab'ın ücretsiz T4 GPU'sunda; küçük alt bölgelerde, küçük modelle (ResNet-34), karma hassasiyetle ve her epoch'ta kayıt alarak.
