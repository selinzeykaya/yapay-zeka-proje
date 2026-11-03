# Sınırlılıklar — çalışma boyunca tutulan notlar

> Bu dosya rapordaki "Sınırlılıklar" ve "Gelecek Çalışmalar" bölümleri için ham madde listesidir. Metni kendi cümlelerinizle yazın.

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
- WorldCover'ın Kar-buz (70), Mangrov (95) ve Yosun-liken (100) sınıfları örneklenmedi. Model 2014/2024 haritalarında bu pikselleri 6 sınıftan birine atar (yüksek dağlardaki kar büyük olasılıkla "Çıplak" olur). Şehir bazında alan oranları: `results/tables/worldcover_dislanan_siniflar.csv` → **[Faz 1 çalışınca sayılar buraya yazılacak]**
- Örnekler 3×3 piksel penceresinde homojen olan alanlardan alındı (karışık kenar pikselleri hariç). Bu yüzden test doğruluğu, gerçek haritanın karışık piksellerindeki doğruluğundan biraz yüksek olabilir.
- WorldCover'ın kendisi de hatasız değil; etiket hatası modele aynen geçer.
- **Su/Sulak alan sınıfı iki farklı yüzeyi birleştiriyor:** Kalıcı su (WorldCover 80) ve otsu sulak alan (90). 01 çıktısında 90 kodlu noktalar yaz kompozitinde NDVI ~0.7 ve negatif MNDWI ile sudan çok bitki gibi görünüyor. Sulak alan hidrolojik bir tanım (yılın bir kısmında su basması); tek bir yaz kompozitinde spektral olarak çayır/tarımdan ayrışmayabilir.
  - Kanıt: `results/tables/su_sulak_alt_tip_istatistik.csv` (02), `results/tables/su_sulak_alt_tip_tahminleri.csv` ve `results/figures/su_sulak_alt_tip_tahminleri.png` (03) → **[Faz 3 sonrası: 80 ve 90 için recall ve en çok karıştığı sınıf yazılacak]**
  - AS3 için sonuç: Açık su alanı değişimi (MNDWI) daha güvenilir; sulak alan değişimi tek mevsim optik veriyle sınırlı ölçülebilir.
  - Gelecek çalışma: çok mevsimli (ilkbahar + yaz) kompozit veya Sentinel-1 radar verisiyle sulak alan ayrımı.
- **NDMI model girdisinden çıkarıldı:** Landsat'ta NDMI = −NDBI (aynı NIR ve SWIR1 bantları). Model 11 özellikle eğitildi; NDMI yalnızca Faz 4 nem analizinde kullanıldı.
- Su alanı: MNDWI > 0 eşiği ile JRC'nin 2021 uyumu `results/tables/su_alani_karsilastirma.csv` → **[Faz 1 sonrası IoU değerleri yazılacak]**
- Landsat LST eksik oranı: `results/tables/lst_eksik_orani.csv` → **[Faz 1 sonrası yazılacak]**

## İDA
- Kendi İDA görüntümüz yok. Model açık FloW-Img veri seti (toplandığı yer ve ortam Faz 5'te veri setinin makalesinden doğrulanıp buraya yazılacak) üzerinde eğitilip değerlendirildi; Türkiye kıyı verisi DEĞİLDİR.
- Gelecek çalışma: İstanbul/İzmir kıyılarından İDA görüntüsü toplanıp modelin bu verilerle doğrulanması.
