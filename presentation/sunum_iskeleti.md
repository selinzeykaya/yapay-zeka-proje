# Sunum iskeleti (≈15 dk, 16 slayt)

> Her slayt: **başlık**, en fazla 3–4 kısa madde, 1 görsel. Maddeler konuşma notudur, slayta kısaltarak koyun. Konuşma metnini kendiniz yazın.
> Görseller: `Drive'ım/yapay-zeka-proje/results/figures/`

| # | Başlık | Slayttaki içerik (madde) | Görsel | Süre |
|---|---|---|---|---|
| 1 | Başlık | Proje adı, ekip, ders, tarih | — | 0:20 |
| 2 | Problem | Arazi değişimi ↔ yerel iklim · 7 il, farklı iklim bölgeleri · uydu + YZ ile izleme | Türkiye haritasında 7 il (yoksa `rgb_kompozitler.png`) | 0:45 |
| 3 | Alt sorular | AS1–AS6 tablosu (rapor 1.2'deki tablo) | Tablo | 0:45 |
| 4 | Veri | Landsat 8/9 · WorldCover 2021 etiketi · MODIS/ERA5/CHIRPS · GEE · 13 251 nokta, 6 sınıf | `sinif_dagilimi.png` | 1:00 |
| 5 | Yöntem akışı | Veri → 4 model → en iyi model → 2014/2024 değişim → iklim ilişkisi → genelleme · İDA ayrı kol | Akış şeması (aşağıda) | 1:00 |
| 6 | Sınıflandırma | 4 model karşılaştırması · XGBoost macro-F1 0.783, Kappa 0.742 · Tarım en zor sınıf | `model_karsilastirma.png` + `karisiklik_matrisi_XGBoost.png` | 1:15 |
| 7 | Model neye bakıyor? | SHAP: SR_B7, MNDWI öne çıkıyor | `shap_XGBoost.png` | 0:45 |
| 8 | Değişim haritaları | 2014 / 2024 / değişim · örneklem yöntemi (9 nokta/hücre), eşleşme %98.1 | `degisim_haritalari.png` | 1:00 |
| 9 | Ne değişti? | Artvin orman +5.6 pp · Şanlıurfa tarım +4.1 pp · İstanbul yapı +0.6 pp · Van su +%12 | `sinif_degisim_pp.png` | 1:00 |
| 10 | İklim trendleri | Şanlıurfa yaz LST −1.44 °C/10 yıl (p = 0.0001) · çoğu trend anlamsız | `iklim_serileri.png` | 1:00 |
| 11 | Değişim–iklim ilişkisi | ΔNDVI–ΔLST negatif (Şanlıurfa −0.65, Artvin −0.41) · çoğu ilişki zayıf | `spearman_isi_haritasi.png` | 1:00 |
| 12 | Kentsel ısı adası | İstanbul ≈ +8 °C, İzmir ≈ +1.2–1.5 °C | `kentsel_isi_adasi.png` | 0:45 |
| 13 | LST'yi ne belirliyor? | RF R² 0.92, RMSE 2.0 °C (10 km blok CV) · NDVI ve rakım baskın | `lst_regresyon_shap.png` | 1:00 |
| 14 | Model başka ile taşınabilir mi? | Ortalama F1 düşüşü ≈ 0.11 · en çok Konya/Şanlıurfa/Van (kurak) · Tarım en zor | `genelleme_isi_haritasi.png` veya `genelleme_dusus.png` | 1:15 |
| 15 | Yüzen atık tespiti | YOLOv8n mAP50 0.388 · 5.4 ms/görüntü · **Endonezya nehir verisi, Türkiye değil** | `ida_ornek_tespitler.png` | 1:00 |
| 16 | Sonuç, sınırlılık, gelecek | Her AS için 1 satır cevap · 3 sınırlılık (etiket 2021, ilişki≠neden, İDA verisi) · 2 gelecek çalışma | — | 1:00 |

Toplam ≈ 15:00. Süre kısaysa çıkarılabilecekler: 7, 12.

## Slayt 5 için akış şeması (çizim önerisi)
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

## Sunumda söylenmesi gereken uyarılar (unutmayın)
- "İlişki" deyin, "neden oldu" demeyin.
- İDA verisi Türkiye verisi değil; kendi İDA görüntümüz yok.
- 2014 ve 2024 haritalarının doğruluğu ölçülemedi (etiket yalnızca 2021).
- Değişim haritası görselleri yalnızca görsel amaçlı; sayılar noktalardan.

## Hazırlık listesi
- [ ] Şekilleri Drive'dan indir, slayta yerleştir (yazılar okunuyor mu kontrol et)
- [ ] Her sayıyı ilgili CSV ile bir kez karşılaştır
- [ ] Olası sorular: `presentation/olasi_sorular.md` — her kişi en az 5'ini çalışsın
- [ ] Prova: süre tut (hedef 15 dk)
