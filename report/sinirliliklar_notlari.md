# Sınırlılıklar — çalışma boyunca tutulan notlar

> Bu dosya rapordaki "Sınırlılıklar" ve "Gelecek Çalışmalar" bölümleri için ham madde listesidir. Metni kendi cümlelerinizle yazın.

## GEE kota kullanımı
- Faz 1 toplam ≈ **23.3 EECU-saat** (aylık 150'nin ≈ %15.5'i; `results/tables/gee_kota_kullanimi.csv`). En pahalı: Konya (7.1), Van (4.6), Şanlıurfa (3.6), İzmir (3.3). 2024 kompozitleri (Landsat 8+9) 2014'ün ~2 katı kota harcadı.

## Kapsam kararları
- Değişim analizi yalnızca 2014 ve 2024 yıllarını kapsıyor (2019 hız için çıkarıldı).
- Şehir başına 2.000 örnek nokta; hiperparametre araması n_iter=10, 3-katlı CV ile sınırlı.
- CNN modeli kapsam dışı; İDA modülünde yalnızca YOLOv8n eğitildi.

## Veri kısıtları
- ESA WorldCover v200 yalnızca 2021 → model 2021 etiketiyle eğitilip 2014/2024'e uygulanıyor; diğer yıllardaki doğruluk ölçülemiyor.
- Landsat 9'un GEE'deki ilk görüntüsü 2021-11-08 (00 notebook'unda doğrulandı) → 2014 ve 2021 yaz kompozitleri yalnızca Landsat 8, 2024 kompoziti Landsat 8 + 9. Konya merkezde 2014 yazı 6 sahne, 2024 yazı 6 (L8) + 5 (L9) sahne → 2024 kompoziti daha fazla gözleme dayanıyor.
- JRC su verisi 2021'de bitiyor (son yıl 2021, 00 notebook'unda doğrulandı) → 2024 su alanı Landsat MNDWI eşiğiyle; iki yöntem 2021'de karşılaştırılacak.
- Landsat ST_B10 bazı piksellerde eksik → eksik oranı raporlanacak.
- 1 km grid'de yalnızca NDVI, NDBI, MNDWI, NDMI ve LST tutuldu (SAVI, BSI çıkarıldı). GEE bellek sınırı nedeniyle grid her il için 2014 / 2024 / statik olmak üzere üç görevde hesaplandı (ilk denemede "User memory limit exceeded").
- ERA5-Land ~11 km çözünürlükte → toprak nemi yalnızca şehir ölçeğinde zaman serisinde kullanıldı; 1 km grid analizinde nem göstergesi olarak NDMI kullanıldı (NDMI bitki/yüzey nemini gösterir, doğrudan toprak nemi ölçümü değildir).
- Bulgular korelasyon/ilişki düzeyindedir; neden-sonuç iddiası yoktur.

## Etiket ve sınıf eşlemesi
- WorldCover'ın Kar-buz (70), Mangrov (95) ve Yosun-liken (100) sınıfları örneklenmedi. Model 2014/2024 haritalarında bu pikselleri 6 sınıftan birine atar (yüksek dağlardaki kar büyük olasılıkla "Çıplak" olur). Şehir bazında alan oranları (`results/tables/worldcover_dislanan_siniflar.csv`): yalnızca Artvin'de kayda değer — kar-buz 1.0 km² (%0.014) + yosun-liken 10.1 km² (%0.137) = **%0.15**; Van'da %0.001; diğer 5 ilde 0. Mangrov hiçbir ilde yok. → Etkisi ihmal edilebilir düzeyde.
- Nihai örnek sayısı 13.251 (hedef 7 × ~2.000 = 13.986). Hedefin altında kalanlar (300 m mesafe filtresi sonrası, `results/tables/ornek_sayilari.csv`): **Artvin** Tarım 108, Yapılaşma 104, Su/Sulak 239 (toplam 1.450); Samsun Çıplak 167; İstanbul Çıplak 321; İzmir Çıplak 324. Bu sınıflar o illerde küçük ve dağınık alanlarda; Artvin'in sınıf bazında test sonuçları az örnekle hesaplanacağı için daha oynak olacak.
- Örnekler 3×3 piksel penceresinde homojen olan alanlardan alındı (karışık kenar pikselleri hariç). Bu yüzden test doğruluğu, gerçek haritanın karışık piksellerindeki doğruluğundan biraz yüksek olabilir.
- WorldCover'ın kendisi de hatasız değil; etiket hatası modele aynen geçer.
- **Su/Sulak alan sınıfı iki farklı yüzeyi birleştiriyor:** Kalıcı su (WorldCover 80) ve otsu sulak alan (90). 01 çıktısında 90 kodlu noktalar yaz kompozitinde NDVI ~0.7 ve negatif MNDWI ile sudan çok bitki gibi görünüyor. Sulak alan hidrolojik bir tanım (yılın bir kısmında su basması); tek bir yaz kompozitinde spektral olarak çayır/tarımdan ayrışmayabilir.
  - 02 sonucu: otsu sulak alan toplam 133 nokta (Su/Sulak'ın %6); büyük kısmı **Samsun**'da (110 nokta, Samsun Su/Sulak'ının %33'ü; olası: Kızılırmak/Yeşilırmak deltaları — doğrulanmalı), İzmir'de 17 (%5), diğer illerde ≤ 3. Ortalama NDVI: kalıcı su −0.04, otsu sulak alan **0.63**; ortalama MNDWI: kalıcı su +0.39, otsu sulak alan **−0.36** → otsu sulak alan spektral olarak bitki gibi.
  - Kanıt: `results/tables/su_sulak_alt_tip_istatistik.csv` (02), `results/tables/su_sulak_alt_tip_tahminleri.csv` ve `results/figures/su_sulak_alt_tip_tahminleri.png` (03) → **[Faz 3 sonrası: 80 ve 90 için recall ve en çok karıştığı sınıf yazılacak]**
  - AS3 için sonuç: Açık su alanı değişimi (MNDWI) daha güvenilir; sulak alan değişimi tek mevsim optik veriyle sınırlı ölçülebilir.
  - Gelecek çalışma: çok mevsimli (ilkbahar + yaz) kompozit veya Sentinel-1 radar verisiyle sulak alan ayrımı.
- **NDMI model girdisinden çıkarıldı:** Landsat'ta NDMI = −NDBI (aynı NIR ve SWIR1 bantları). Model 11 özellikle eğitildi; NDMI yalnızca Faz 4 nem analizinde kullanıldı.
- Su alanı: MNDWI > 0 ile JRC'nin 2021 uyumu (`results/tables/su_alani_karsilastirma.csv`): IoU Şanlıurfa 0.94, Van 0.85, Samsun 0.82, Konya 0.81, İstanbul 0.81, İzmir 0.79, **Artvin 0.64**. MNDWI her ilde JRC'den daha az su buluyor (−%5 Şanlıurfa … −%24 Artvin). Olası neden: JRC'de mevsimsel su (waterClass 2) da su sayılıyor, yaz kompozitinde ise kuruyan kıyı şeritleri ve karışık kenar pikselleri su çıkmıyor; Artvin'de dar vadi barajları kenar piksel etkisini büyütüyor. → MNDWI değişimi yorumlanabilir, mutlak alanlar JRC'den düşük.
- MNDWI su alanı değişimi 2014→2024: Artvin **+%78.9**, Van +%12.1, İstanbul +%9.8, Samsun +%9.0, Şanlıurfa +%1.9, Konya −%1.4, İzmir −%6.0. Artvin'deki büyük artış için olası açıklama yeni baraj göllerinin dolması (ör. Yusufeli) — kaynaktan doğrulanmalı. Van'daki +%12 dikkatle kontrol edilmeli (göl seviyesi mi, 2014 kompozit kalitesi mi?).
- Landsat LST eksik oranı (`results/tables/lst_eksik_orani.csv`, kompozitte LST'siz piksel %): Artvin 2014 %5.6 → 2024 %0.4; Konya %2.6 (iki yılda da); Şanlıurfa %0.9 (iki yılda da); İstanbul 2014 %1.1; diğerleri < %0.4. Tamamen LST'siz 1 km hücre: Artvin 2014 %1.4, Konya %1.1, Şanlıurfa %0.2, diğerleri 0. Konya ve Şanlıurfa'da eksikliğin iki yılda **aynı** olması bulut değil sabit bir yüzey nedenine işaret ediyor (olası: Landsat ST ürününün dayandığı ASTER GED emisivite verisindeki boşluklar, ör. tuz gölü yüzeyi — doğrulanmalı). Artvin 2014'teki fazlalık büyük olasılıkla bulut kaynaklı (dağlık, bulutlu bölge, 2014'te yalnızca Landsat 8).

## Faz 4 (değişim ve iklim analizi)
- Haritalar Earth Engine'deki karşılık modelle üretildi (RF → smileRandomForest / XGBoost → smileGradientTreeBoost). Eşleme birebir değil; iki model aynı test noktalarında karşılaştırıldı: `results/tables/gee_vs_colab_karsilastirma.csv` → **[Faz 4 sonrası fark yazılacak]**
- 2014→2024 geçiş matrisi il başına 20.000 rastgele pikselden tahmin edildi (oran başına hata payı ≲ ±0.7 puan).
- Modelin 2014/2024 doğruluğu ölçülemiyor (etiket yok); yıllar arası atmosfer/fenoloji farkı sahte değişim üretebilir → küçük değişimler temkinli yorumlanmalı.
- 1 km hücreler mekânsal olarak bağımsız değil (otokorelasyon) → Spearman p-değerleri olduğundan küçük; yorumda r'nin büyüklüğü/yönü esas alındı. Regresyonda mekânsal blok CV (10 km) kullanıldı.
- ΔLST iki tek yaz kompozitinden (2014, 2024) hesaplandı; yıl-yıl hava farkı il genelinde sabit bir kayma yaratır (Spearman bundan etkilenmez, mutlak ΔLST değerleri etkilenir).
- Kentsel ısı adası tanımı eşiklere bağlı (kentsel > %50 yapı, kırsal < %5 yapı, ±200 m rakım).

## İDA
- Kendi İDA görüntümüz yok. Model açık veri setiyle eğitilip değerlendirildi; Türkiye kıyı verisi DEĞİLDİR.
- Kullanılan veri seti: *Floating Waste and Aquatic Vegetation Image Dataset from Turbid Rivers* (Radam ve ark., Mendeley Data, DOI 10.17632/j26w4m645z.2, CC BY 4.0): Banjarmasin (Endonezya) bulanık nehirleri; çekim platformu (İDA / drone / el kamerası) veri sayfasında belirtilmemiş → "İDA görüntüsü" diye nitelendirilmemeli, "su yüzeyi görüntüleri" denmeli.
- Nehir ortamı ≠ deniz kıyısı (dalga, yansıma, tuzlu su köpüğü farklı) → İstanbul/İzmir kıyılarına aktarılabilirlik belirsiz.
- FloW-Img (gerçek İDA görüntüleri) indirme için başvuru gerektiriyor; onaylanırsa ana veri olarak kullanılacak. MMOS (95.5 GB, drone) boyut ve platform nedeniyle kullanılmadı.
- Gelecek çalışma: İstanbul/İzmir kıyılarından İDA görüntüsü toplanıp modelin bu verilerle doğrulanması.
