# Olası sorular ve cevap noktaları

> Cevaplar **anahtar noktalar** halindedir. Kendi cümlelerinizle söyleyin. Sayıların kaynağı parantez içinde.

## Veri ve etiket
1. **Neden ESA WorldCover? 2014 ve 2024 için etiket yok, doğruluğu nasıl biliyorsunuz?**
   - WorldCover v200 açık, 10 m, Türkiye'yi kapsıyor; yalnızca 2021 var
   - 2014/2024 doğruluğunu **bilmiyoruz** → sınırlılık; yön güvenilir, büyüklük temkinli
   - Gelecek: bağımsız referans verisi (Olofsson ve ark., L19)
2. **WorldCover'ın kendi hataları modelinize geçmiyor mu?**
   - Evet, geçer; 3×3 homojen pencere ile karışık pikselleri azalttık
   - Test başarısı gerçek haritadan biraz iyimser olabilir
3. **Neden 2014 ve 2024? Neden 2019 yok?**
   - Landsat 8 2013'te başladı → ilk tam yaz 2014; 2024 son tam yıl
   - 2019 süre/kota nedeniyle kapsam dışı
4. **2014'te yalnızca Landsat 8, 2024'te 8+9 — karşılaştırma adil mi?**
   - Aynı sensör ailesi, aynı işleme (C2 L2); 2024 daha fazla gözleme dayanıyor
   - Sınırlılık olarak yazdık
5. **Neden 7 il, neden bu iller?**
   - Her alt soru için uygun il (orman, kent, su, tarım) + farklı iklim bölgeleri (genelleme testi için)

## Model
6. **Testte MLP (0.789) XGBoost'tan (0.783) iyi, neden XGBoost?**
   - Model **doğrulama** kümesinde seçildi; test yalnızca son değerlendirme → test'e göre seçmek bilgi sızıntısı olur
   - Fark 0.006, test belirsizliği içinde
   - XGBoost ayrıca SHAP (TreeExplainer) ve GEE karşılığı için uygun
7. **Neden derin öğrenme (CNN) yok?**
   - Nokta tabanlı, tablo verisi (11 özellik) → ağaç modelleri güçlü; kapsam/süre
8. **Tarım neden en kötü sınıf (F1 ≈ 0.59)?**
   - Tek yaz kompoziti: hasat edilmiş tarla çıplak/çayır gibi görünüyor; ürün çeşitliliği
   - Genellemede de en zor sınıf (LOCO F1 0.30–0.56)
9. **Kappa'yı neden veriyorsunuz, eleştiriliyor?**
   - Yaygın raporlandığı için karşılaştırma amaçlı; asıl metrik macro-F1 (Foody 2020, L20)
10. **Sınıf dengesizliği?**
    - Şehir başına sınıf dengeli örnekleme hedeflendi; Artvin'de bazı sınıflar az (Tarım 108); macro-F1 her sınıfa eşit ağırlık verir

## Değişim ve iklim
11. **Neden tüm ili değil de 9 noktayı sınıflandırdınız?**
    - Tüm ili 30 m'de GEE'de sınıflandırmak kotayı aştı (zaman aşımı, bellek hatası)
    - Hücre başına 9 nokta → il başına on binlerce nokta → il düzeyinde kararlı; tek hücre düzeyinde gürültülü
    - Kontrol: grid eşleşmesi %98.1
12. **Korelasyonlar çok zayıf (|ρ| < 0.2) ama p < 0.001, bu ne demek?**
    - n çok büyük (5 000–39 000 hücre) → küçük ilişkiler de anlamlı çıkıyor
    - Ayrıca komşu hücreler bağımsız değil → p olduğundan küçük
    - Bu yüzden ρ'nun büyüklüğüne ve yönüne bakıyoruz
13. **Şanlıurfa'da sıcaklık düşmüş, ısınma yok mu?**
    - Yaz gündüz **yüzey** sıcaklığı (MODIS LST), hava sıcaklığı değil
    - Tarım +4.1 pp ile birlikte → sulama ile tutarlı **ilişki**; neden-sonuç değil; literatürle (L44) destekleyin
14. **İstanbul ısı adası 8 °C, İzmir 1.5 °C — neden bu kadar fark?**
    - Tanıma bağlı: kırsal referans (orman/deniz kenarı), eşikler (>%50 yapı, <%5 yapı, ±200 m rakım)
    - Olası (kontrol edilmedi): İzmir'in kırsal referansı kurak/çıplak alanlar → gündüz kendisi de sıcak, fark küçülüyor
    - Kesin cevap için harita ile kontrol gerekli (sınırlılık)
15. **Artvin'de orman +5.6 pp gerçekten artmış mı?**
    - Kısmen model hatası olabilir (doğruluk ~%78); 2014 Artvin'de bulut daha fazlaydı (LST eksik %5.6)
    - Su +%78.9 → Yusufeli barajı ile tutarlı (L43)
16. **LST regresyonunda R² 0.92 çok yüksek değil mi, ezber olabilir mi?**
    - 10 km mekânsal blok CV ile ölçüldü (1 435 blok) → komşu hücre sızıntısı engellendi (L21)
    - NDVI ve rakım LST'yi fiziksel olarak güçlü açıklıyor
    - İlk denemede bloklar yanlış tanımlanmıştı; düzelttik → yalnızca düzeltilmiş değer raporda
17. **SHAP'ta arazi sınıflarının etkisi neden küçük?**
    - Sınıf bilgisi NDVI'nın içinde de var (ilişkili girdiler) → etki NDVI'ya "geçiyor"
    - SHAP önemi neden-sonuç değildir

## Genelleme
18. **LOCO nedir, neden yaptınız?**
    - Bir ili tamamen dışarıda bırakıp diğer 6 ilde eğitmek → modelin hiç görmediği bölgede başarısı
    - Rastgele bölme başarıyı olduğundan iyi gösterebilir (L22, L23)
19. **Düşüş veri azlığından olabilir mi?**
    - Hayır: LOCO'da eğitim verisi daha fazla (≈11 250 vs 9 275)
20. **Neden kurak illerde daha çok düşüş?**
    - Yağış ile düşüş ρ ≈ −0.96 ama yalnızca 7 il → örüntü, kanıt değil
    - Olası: fenoloji farkı, tuzlu/sığ göller (Konya su F1 0.89 → 0.39), parlak toprak

## İDA (yüzen atık)
21. **Bu Türkiye verisi mi?**
    - **Hayır.** Endonezya (Banjarmasin) nehir görüntüleri, açık veri (L47); kendi İDA görüntümüz yok
    - FloW-Img'e erişemedik (başvuru sitesi açılmadı)
22. **mAP50 0.388 düşük değil mi?**
    - Bulanık su, küçük nesneler, atık–bitki karışması; en küçük model (YOLOv8n); n_test = 158
    - Literatür değerleri farklı veri setlerinde → doğrudan karşılaştırılamaz
23. **İstanbul/İzmir kıyılarına uygulanabilir mi?**
    - Bilinmiyor: nehir ≠ deniz (dalga, yansıma, köpük) → gelecek çalışma: yerel görüntü toplayıp test etmek
24. **5.39 ms/görüntü ne anlama geliyor?**
    - GPU'da (Colab T4) gerçek zamanlıya yakın; İDA üzerinde gömülü donanımda daha yavaş olur

## Genel
25. **Projenin en önemli bulgusu ne?** `[SEN YAZ]` — önerilen aday: genelleme sonucu (model kurak illere iyi taşınmıyor) veya NDVI'nın LST'deki baskın rolü
26. **Yapay zekâ burada ne katıyor, klasik yöntemlerden farkı?** `[SEN YAZ]` — 4 model karşılaştırması, SHAP ile açıklanabilirlik, mekânsal doğrulama
27. **Tekrar yapılabilir mi?**
    - Tüm kod GitHub'da, parametreler `config.py`, RANDOM_STATE = 42; veri GEE ve açık veri setlerinden
