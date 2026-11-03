# Sınırlılıklar — çalışma boyunca tutulan notlar

> Bu dosya rapordaki "Sınırlılıklar" ve "Gelecek Çalışmalar" bölümleri için ham madde listesidir. Metni kendi cümlelerinizle yazın.

## Kapsam kararları
- Değişim analizi yalnızca 2014 ve 2024 yıllarını kapsıyor (2019 hız için çıkarıldı).
- Şehir başına 2.000 örnek nokta; hiperparametre araması n_iter=10, 3-katlı CV ile sınırlı.
- CNN modeli kapsam dışı; İDA modülünde yalnızca YOLOv8n eğitildi.

## Veri kısıtları
- ESA WorldCover v200 yalnızca 2021 → model 2021 etiketiyle eğitilip 2014/2024'e uygulanıyor; diğer yıllardaki doğruluk ölçülemiyor.
- Landsat 9 Ekim 2021'de başladı → 2014 kompoziti yalnızca Landsat 8, 2024 kompoziti Landsat 8 + 9.
- JRC su verisi 2021'de bitiyor → 2024 su alanı Landsat MNDWI eşiğiyle; iki yöntem 2021'de karşılaştırılacak.
- Landsat ST_B10 bazı piksellerde eksik → eksik oranı raporlanacak.
- ERA5-Land ~11 km çözünürlükte → toprak nemi yalnızca şehir ölçeğinde zaman serisinde kullanıldı; 1 km grid analizinde nem göstergesi olarak NDMI kullanıldı (NDMI bitki/yüzey nemini gösterir, doğrudan toprak nemi ölçümü değildir).
- Bulgular korelasyon/ilişki düzeyindedir; neden-sonuç iddiası yoktur.

## Etiket ve sınıf eşlemesi
- WorldCover'ın Kar-buz (70), Mangrov (95) ve Yosun-liken (100) sınıfları örneklenmedi. Model 2014/2024 haritalarında bu pikselleri 6 sınıftan birine atar (yüksek dağlardaki kar büyük olasılıkla "Çıplak" olur). Şehir bazında alan oranları: `results/tables/worldcover_dislanan_siniflar.csv` → **[Faz 1 çalışınca sayılar buraya yazılacak]**
- Örnekler 3×3 piksel penceresinde homojen olan alanlardan alındı (karışık kenar pikselleri hariç). Bu yüzden test doğruluğu, gerçek haritanın karışık piksellerindeki doğruluğundan biraz yüksek olabilir.
- WorldCover'ın kendisi de hatasız değil; etiket hatası modele aynen geçer.
- Su alanı: MNDWI > 0 eşiği ile JRC'nin 2021 uyumu `results/tables/su_alani_karsilastirma.csv` → **[Faz 1 sonrası IoU değerleri yazılacak]**
- Landsat LST eksik oranı: `results/tables/lst_eksik_orani.csv` → **[Faz 1 sonrası yazılacak]**

## İDA
- Kendi İDA görüntümüz yok. Model açık FloW-Img veri seti (toplandığı yer ve ortam Faz 5'te veri setinin makalesinden doğrulanıp buraya yazılacak) üzerinde eğitilip değerlendirildi; Türkiye kıyı verisi DEĞİLDİR.
- Gelecek çalışma: İstanbul/İzmir kıyılarından İDA görüntüsü toplanıp modelin bu verilerle doğrulanması.
