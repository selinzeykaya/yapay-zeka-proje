# Kontrol: Samsun'da U-Net'in gösterdiği orman azalması gerçek mi?

**Soru:** 08'in değişim tablosunda (`unet_degisim_ozet.csv`) Samsun'un iki alt bölgesinde Orman 2017 → 2025 arasında **−89 km²**, Çayır/Çalı **+68 km²** görünüyor.
Bu, 800 km²'lik alanda orman alanının yaklaşık yarısı demek. Gerçek bir kesim mi, yoksa modelin/görüntünün yarattığı sahte değişim mi?

**Kullanılan veriler** (hepsi 08'in Colab çıktısı, yeniden hesaplama yok): `unet_sinif_alanlari.csv`, `unet_degisim_matrisi.csv`,
`unet_degisim_Samsun_*.png`, `s2_veri_ozeti.csv` (WorldCover 2021 etiket payları), `unet_il_bazinda.csv`, 04'ün Landsat tablosu `sinif_alanlari_degisim.csv`.

## Bulgular

| # | Kontrol | Sonuç |
|---|---|---|
| 1 | Azalma hangi kutuda? | Orman azalmasının **%96'sı tek kutuda**: Yeşilırmak deltası 158,5 → 72,7 km² (**−85,7 km², −%54**). Kızılırmak deltası 22,5 → 19,0 km² (−3,5 km²). |
| 2 | Orman neye dönüşmüş? | Yeşilırmak'ta 2017 ormanının 84,5 km²'si 2025'te **Çayır/Çalı**, 16,2 km²'si Tarım, yalnızca 3,6 km²'si Yapılaşma. Gerçek kesimde açılan alan genelde tarım, yapı ya da çıplak toprağa geçer; burada neredeyse hepsi "daha seyrek yeşil" sınıfa kaymış. |
| 3 | Mekânsal örüntü | Değişim haritasında değişen pikseller **bütün kutuya küçük lekeler halinde eşit dağılmış**. Kesim, yangın ya da yapılaşma kümelenmiş, sınırları belirgin alanlar üretir. Bütün ovada aynı anda gerçekleşen, eşit dağılmış bir değişim sınıflandırma kaymasının tipik işaretidir. |
| 4 | Bağımsız referans (etiket yılı) | WorldCover 2021'de bu kutunun **%40,2'si ağaç örtüsü** (≈161 km²). U-Net 2017 tahmini (158,5 km²) etiketle uyumlu. 2025 tahmini (72,7 km²) ise etiketten 4 yıl sonra ağaç örtüsünün yarısının kaybolduğunu söylüyor. Bu büyüklükte bir kesim bölgede bilinmiyor ve haritada kesim izi yok. |
| 5 | Landsat analizi (04, bütün il, 2014 → 2024) | Samsun'un tamamında Orman yalnızca **−2,06 puan (−%3,7)**. Bütün ilde 10 yılda %4 azalma varken 400 km²'lik bir ovada 8 yılda %54 azalma tutarsız. |
| 6 | Modelin Samsun'daki başarısı | Samsun U-Net accuracy'si **0,708**, 7 il içinde en düşük (diğerleri 0,83–0,92). Modelin bu ilde Orman ile Çayır/Çalı'yı ayırmakta zorlandığı biliniyor. |

## Sonuç

**Samsun orman azalması gerçek bir arazi değişimi değil; büyük olasılıkla sahte değişim.** Raporda bulgu olarak kullanılmamalı. Sınırlılık örneği olarak kullanılabilir.

**Olası neden:** Yeşilırmak deltası (Çarşamba Ovası) ağaçlık alanlarının önemli kısmı fındık bahçesi ve kavaklık gibi tarımsal ağaçlıklardır. WorldCover bunları
"ağaç örtüsü" sayar. Bu alanların yaz görüntüsü yıldan yıla çok değişir (hasat Ağustos'ta, budama, kuraklık, kompozite giren görüntülerin tarihleri). 2025 yaz ortancası
daha seyrek görünen bir tabloya denk gelince model bu alanları Çayır/Çalı'ya kaydırmış olabilir. Bu açıklama `[DOĞRULANMADI]` (fındık bahçesi yoğunluğu için kaynak eklenmeli);
ama sonuç (gerçek değişim değil) bu açıklamaya bağlı değil: 1–6 numaralı kontroller tek başına yeterli.

**Aynı nedenle temkinli okunacaklar:** Samsun Çayır/Çalı +68 km² (aynı kaymanın öbür yüzü). Diğer illerde benzer bir tek-kutu kayması yok:
en büyük değişimler Artvin Su/Sulak +18,6 km² (Yusufeli baraj gölü, Landsat MNDWI ile tutarlı) ve İstanbul Yapılaşma +31,0 km² (kümelenmiş, kent çeperinde).

## Kesin doğrulama için (isteğe bağlı)
- Earth Engine'de aynı kutuda Sentinel-2 2017 ve 2025 yaz RGB/NDVI ortancalarını yan yana açmak. NDVI bütün ovada aynı anda düşüyorsa görüntü farkıdır.
- Hansen Global Forest Change (`UMD/hansen/global_forest_change_2024_v1_12`) `lossyear` 17–24 katmanında bu kutudaki kayıp alanı (km²).
- 2025 tahminini Haziran–Temmuz ile sınırlı bir kompozitle tekrarlamak (hasat dönemini dışarıda bırakır).
