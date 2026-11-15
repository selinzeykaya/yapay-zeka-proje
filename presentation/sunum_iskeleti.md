# Sunum iskeleti (≈20 slayt)

> Slayt sırası **hocanın "Sunum İçeriği" listesine göre** (8 başlık, aynı sırayla). Her slayt: başlık, en fazla 3–4 kısa madde, 1 görsel. Maddeler konuşma notudur; konuşma metnini kendiniz yazın.
> Görseller: `Drive'ım/yapay-zeka-proje/results/figures/` · Süre belirtilmediği için ≈ 1 dk/slayt varsayıldı; süre öğrenilince kısaltın (çıkarılabilirler: 9, 15, 16).

## Hocanın 8 başlığı → slaytlar
| Hocanın başlığı | Slaytlar |
|---|---|
| 1. Araştırma sorusu ve amaç | 2, 3 |
| 2. Literatür taraması (20–30 çalışma) | 4, 5 |
| 3. Kullanılan algoritmalar ve tercih nedenleri | 6 |
| 4. Veri setinin tanıtılması (kaynak, özellik, örnek sayısı, sınıf dağılımı, grafik, ortalama/medyan/mod) | 7, 8 |
| 5. Model seçimi ve parametreler (hiperparametreler, yapılan değişiklikler) | 9, 10 |
| 6. Deneysel sonuçlar (Accuracy, Precision, Recall, F1, ROC-AUC; tablo + grafik) | 11–17 |
| 7. Literatürle karşılaştırma | 18 |
| 8. Genel değerlendirme ve sonuç (cevap, bulgular, güçlü yönler, sınırlılıklar) | 19, 20 |

## Slaytlar
| # | Başlık | Slayttaki içerik (madde) | Görsel |
|---|---|---|---|
| 1 | Başlık | Proje adı, ekip, ders, tarih | — |
| 2 | Problem ve araştırma sorusu | Arazi değişimi ↔ yerel iklim · Türkiye'de 7 il, farklı iklim bölgeleri · Ana soru: "Arazi örtüsü 2014→2024 nasıl değişti ve yüzey sıcaklığı/nemle ilişkisi ne?" `[SEN YAZ — tek cümle]` | 7 il haritası (yoksa `rgb_kompozitler.png`) |
| 3 | Alt sorular | AS1–AS6 tablosu (rapor 1.2) | Tablo |
| 4 | Literatür taraması (1) | Kaç çalışma incelendi (25) · konu grupları: sınıflandırma, LST/ısı adası, Türkiye çalışmaları, genelleme, yüzen atık · en sık yöntemler (RF, SVM; NDVI–LST ilişkisi) `[MAKALELERDEN]` | Konu grubu başına çalışma sayısı (çubuk grafik) |
| 5 | Literatür taraması (2) | 5–6 önemli çalışmanın tablosu: yazar, bölge, yöntem, bulgu `[literatur_matrisi.csv'den]` | Tablo |
| 6 | Algoritmalar ve neden | RF (dayanıklı, az ayar) · XGBoost (güçlü, tablo verisi) · SVM (az örnekle iyi) · MLP (doğrusal olmayan) · YOLOv8n (hızlı nesne tespiti) · kaynak `model_gerekceleri.csv` | Tablo |
| 7 | Veri seti | Landsat 8/9 + WorldCover 2021 etiketi (GEE) · 13 251 nokta, 7 il, 11 özellik, 6 sınıf · İklim: MODIS, ERA5, CHIRPS | `sinif_dagilimi.png` |
| 8 | Tanımlayıcı istatistik | Ortalama/medyan/mod tablosu (3–4 özellik: NDVI, NDBI, MNDWI, LST) · sınıflar arası fark | `tanimlayici_istatistik.csv` kısaltılmış + `kutu_grafikleri_indeksler.png` |
| 9 | Ön işleme ve yöntem akışı | 3×3 homojen pencere, 300 m filtre · eğitim/doğrulama/test bölmesi (`veri_bolme.csv`) · akış şeması (aşağıda) | Akış şeması |
| 10 | Hiperparametreler ve değişiklikler | Rastgele arama n_iter=10, 3-katlı CV, seçim doğrulama macro-F1 · seçilen değerler (`hiperparametre_arama.csv`) · yapılan değişiklikler: NDMI çıkarıldı, 9 nokta/hücre örneklemesi, blok CV düzeltmesi | Tablo |
| 11 | Sınıflandırma sonuçları | **Accuracy, Precision, Recall, F1, ROC-AUC** 4 model tablosu · XGBoost: acc 0.785, F1 0.783, ROC-AUC 0.961 | Tablo + `model_karsilastirma.png` |
| 12 | Hata analizi ve SHAP | Karışıklık matrisi: Tarım ↔ Çayır/Orman, Yapılaşma ↔ Çıplak · SHAP: SR_B7, MNDWI | `karisiklik_matrisi_XGBoost.png` + `roc_tumu.png` veya `shap_XGBoost.png` |
| 13 | Arazi değişimi 2014→2024 | Artvin orman +5.6 pp · Şanlıurfa tarım +4.1 pp · İstanbul yapı +0.6 pp · Van su +%12 · eşleşme %98.1 | `degisim_haritalari.png` / `sinif_degisim_pp.png` |
| 14 | İklim trendleri ve ilişkiler | Şanlıurfa yaz LST −1.44 °C/10 yıl (p = 0.0001) · ΔNDVI–ΔLST negatif (Şanlıurfa −0.65, Artvin −0.41) · çoğu ilişki zayıf | `iklim_serileri.png` + `spearman_isi_haritasi.png` |
| 15 | Kentsel ısı adası | İstanbul ≈ +8 °C, İzmir ≈ +1.2–1.5 °C | `kentsel_isi_adasi.png` |
| 16 | LST regresyonu | RF R² 0.92, RMSE 2.0 °C (10 km blok CV) · NDVI ve rakım baskın | `lst_regresyon_shap.png` |
| 17 | Genelleme + yüzen atık | LOCO: ortalama F1 düşüşü ≈ 0.11, en çok kurak illerde · YOLOv8n: P 0.50, R 0.39, F1 0.44, mAP50 0.388 — **Endonezya verisi, Türkiye değil** | `genelleme_isi_haritasi.png` + `ida_ornek_tespitler.png` |
| 18 | Literatürle karşılaştırma | Tablo: bizim değer vs 3–5 çalışmanın değeri (veri/bölge farkı sütunuyla) · İDA: yalnızca "farklı veri setinde raporlanan" | `literatur_karsilastirma.csv` → tablo |
| 19 | Sonuç | Her AS için 1 satır cevap · güçlü yönler: 7 il, 4 model, mekânsal doğrulama, SHAP, açık veri | — |
| 20 | Sınırlılıklar ve gelecek | Etiket yalnızca 2021 · ilişki ≠ neden · İDA verisi Türkiye değil · gelecek: çok mevsimli veri, Türkiye kıyısında İDA görüntüsü | — |

## Slayt 9 için akış şeması (çizim önerisi)
```
Landsat + WorldCover (GEE) ──► 13 251 nokta ──► RF / XGBoost / SVM / MLP ──► en iyi: XGBoost
                                                                     │
          ┌──────────────────────────────────────────────────────────┤
          ▼                                                          ▼
2014 & 2024 sınıflandırma (9 nokta/1 km hücre)              LOCO genelleme (AS5)
          │
          ▼
Değişim + MODIS/ERA5/CHIRPS ──► Mann-Kendall · Spearman · UHI · LST regresyonu (AS1–AS4)

Ayrı kol: Mendeley açık veri ──► YOLOv8n ──► yüzen atık tespiti (AS6)
```

## Sunumda söylenmesi gereken uyarılar
- "İlişki" deyin, "neden oldu" demeyin.
- İDA verisi Türkiye verisi değil; kendi İDA görüntümüz yok.
- 2014 ve 2024 haritalarının doğruluğu ölçülemedi (etiket yalnızca 2021).
- Değişim haritası görselleri yalnızca görsel amaçlı; sayılar noktalardan.

## Hazırlık listesi
- [ ] Literatür slaytları (4, 5, 18) için makaleler okunmuş olmalı → `literatur_matrisi.csv`
- [ ] Şekilleri Drive'dan indir, slayta yerleştir (yazılar okunuyor mu kontrol et)
- [ ] Slayt 11 tablosundaki eksik metrikleri `model_karsilastirma.csv`'den doldur
- [ ] Her sayıyı ilgili CSV ile bir kez karşılaştır
- [ ] Olası sorular: `presentation/olasi_sorular.md` — hoca "konuya hâkimiyet" değerlendiriyor, ekipteki herkes hepsini çalışsın
- [ ] Prova: süre tut
