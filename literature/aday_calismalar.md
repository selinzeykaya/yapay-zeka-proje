# Aday çalışmalar (Faz 7)

- Toplam 56 aday. Hepsinin DOI'si doi.org üzerinden doğrulandı (2026-11-04). Yazar, başlık ve dergi bilgileri DOI kaydından otomatik alındı.
- "Konu" sütunu yalnızca başlıktan/künyeden çıkarılmış etikettir, **makalenin bulgusu değildir**. Bulgular makale okunduktan sonra `literatur_matrisi.csv` dosyasına yazılır.
- Öncelik: 1 = mutlaka okunmalı/atıf yapılmalı, 2 = yararlı, 3 = yedek.
- FloW (Cheng ve ark., 2021): veri seti kullanılamadı. Sonuçları yalnızca **farklı veri setinde raporlanan değerler** olarak verilir, doğrudan karşılaştırma yapılmaz.
- Boşluklar: Van ve Şanlıurfa için DOI'li LST çalışması bulunamadı. Artvin için Landsat tabanlı çalışma bulunamadı (Yusufeli çalışması Sentinel-2 kullanıyor).
- Doğrulanamayan kaynaklar en altta **[DOĞRULANMADI]** başlığı altında. Künye ve DOI kontrol edilmeden kullanılmamalı.

## A. Sınıflandırma yöntemleri (8)

| ID | Kaynak | Başlık | Dergi / yayın | DOI | Bölge | Konu | Kullanılacağı yer | Öncelik |
|---|---|---|---|---|---|---|---|---|
| L01 | Belgiu ve Drăguţ (2016) | Random forest in remote sensing: A review of applications and future directions | ISPRS Journal of Photogrammetry and Remote Sensing | [10.1016/j.isprsjprs.2016.01.011](https://doi.org/10.1016/j.isprsjprs.2016.01.011) | Küresel (derleme) | RF'nin uzaktan algılamada kullanımı; RF seçiminin gerekçesi | Yöntem / 03 | 1 |
| L02 | Maxwell ve ark. (2018) | Implementation of machine-learning classification in remote sensing: an applied review | International Journal of Remote Sensing | [10.1080/01431161.2018.1433343](https://doi.org/10.1080/01431161.2018.1433343) | Küresel (derleme) | ML sınıflandırma uygulama rehberi (RF, SVM, ANN...) | Yöntem / 03 | 1 |
| L03 | Mountrakis ve ark. (2011) | Support vector machines in remote sensing: A review | ISPRS Journal of Photogrammetry and Remote Sensing | [10.1016/j.isprsjprs.2010.11.001](https://doi.org/10.1016/j.isprsjprs.2010.11.001) | Küresel (derleme) | SVM'nin uzaktan algılamadaki yeri | Yöntem / 03 | 2 |
| L04 | Talukdar ve ark. (2020) | Land-Use Land-Cover Classification by Machine Learning Classifiers for Satellite Observations—A Review | Remote Sensing | [10.3390/rs12071135](https://doi.org/10.3390/rs12071135) | Küresel (karşılaştırma) | ML sınıflandırıcılarının LULC karşılaştırması (4 model karşılaştırmamıza en yakın) | Literatür / Tartışma | 1 |
| L05 | Amini ve ark. (2022) | Urban Land Use and Land Cover Change Analysis Using Random Forest Classification of Landsat Time Series | Remote Sensing | [10.3390/rs14112654](https://doi.org/10.3390/rs14112654) | İran (Tahran) | Landsat zaman serisi + RF ile kentsel LULC değişimi | Literatür / Tartışma | 2 |
| L06 | Breiman (2001) | Random Forests | Machine Learning | [10.1023/A:1010933404324](https://doi.org/10.1023/A:1010933404324) | — | RF özgün kaynağı | Yöntem | 1 |
| L07 | Cortes ve Vapnik (1995) | Support-vector networks | Machine Learning | [10.1007/BF00994018](https://doi.org/10.1007/BF00994018) | — | SVM özgün kaynağı | Yöntem | 1 |
| L08 | Chen ve Guestrin (2016) | XGBoost | Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining | [10.1145/2939672.2939785](https://doi.org/10.1145/2939672.2939785) | — | XGBoost özgün kaynağı (en iyi modelimiz) | Yöntem | 1 |

## B. Veri ve platform (8)

| ID | Kaynak | Başlık | Dergi / yayın | DOI | Bölge | Konu | Kullanılacağı yer | Öncelik |
|---|---|---|---|---|---|---|---|---|
| L09 | Gorelick ve ark. (2017) | Google Earth Engine: Planetary-scale geospatial analysis for everyone | Remote Sensing of Environment | [10.1016/j.rse.2017.06.031](https://doi.org/10.1016/j.rse.2017.06.031) | — | GEE platformu | Veri / 01 | 1 |
| L10 | Roy ve ark. (2014) | Landsat-8: Science and product vision for terrestrial global change research | Remote Sensing of Environment | [10.1016/j.rse.2014.02.001](https://doi.org/10.1016/j.rse.2014.02.001) | — | Landsat 8 görevi ve ürünleri | Veri / 01 | 1 |
| L11 | Crawford ve ark. (2023) | The 50-year Landsat collection 2 archive | Science of Remote Sensing | [10.1016/j.srs.2023.100103](https://doi.org/10.1016/j.srs.2023.100103) | — | Landsat Collection 2 (kullandığımız L2 ürünler) | Veri / 01 | 1 |
| L12 | Zanaga ve ark. (2022) | ESA WorldCover 10 m 2021 v200 | Zenodo | [10.5281/zenodo.7254221](https://doi.org/10.5281/zenodo.7254221) | Küresel | ESA WorldCover v200 (etiket kaynağımız) | Veri / 01 | 1 |
| L13 | Wan (2014) | New refinements and validation of the collection-6 MODIS land-surface temperature/emissivity product | Remote Sensing of Environment | [10.1016/j.rse.2013.08.027](https://doi.org/10.1016/j.rse.2013.08.027) | Küresel | MODIS C6 LST ürünü (MOD11A2) | Veri / 04 | 1 |
| L14 | Muñoz-Sabater ve ark. (2021) | ERA5-Land: a state-of-the-art global reanalysis dataset for land applications | Earth System Science Data | [10.5194/essd-13-4349-2021](https://doi.org/10.5194/essd-13-4349-2021) | Küresel | ERA5-Land (toprak nemi, hava sıcaklığı) | Veri / 04 | 1 |
| L15 | Funk ve ark. (2015) | The climate hazards infrared precipitation with stations—a new environmental record for monitoring extremes | Scientific Data | [10.1038/sdata.2015.66](https://doi.org/10.1038/sdata.2015.66) | Küresel | CHIRPS yağış | Veri / 04 | 2 |
| L16 | Pekel ve ark. (2016) | High-resolution mapping of global surface water and its long-term changes | Nature | [10.1038/nature20584](https://doi.org/10.1038/nature20584) | Küresel | JRC Global Surface Water (su IoU kontrolü) | Veri / 01 | 1 |

## C. Spektral indeksler (2)

| ID | Kaynak | Başlık | Dergi / yayın | DOI | Bölge | Konu | Kullanılacağı yer | Öncelik |
|---|---|---|---|---|---|---|---|---|
| L17 | Xu (2006) | Modification of normalised difference water index (NDWI) to enhance open water features in remotely sensed imagery | International Journal of Remote Sensing | [10.1080/01431160600589179](https://doi.org/10.1080/01431160600589179) | — | MNDWI (SHAP'ta en önemli değişkenlerden) | Yöntem / 02–03 | 1 |
| L18 | Zha ve ark. (2003) | Use of normalized difference built-up index in automatically mapping urban areas from TM imagery | International Journal of Remote Sensing | [10.1080/01431160304987](https://doi.org/10.1080/01431160304987) | — | NDBI | Yöntem / 02 | 1 |

## D. Doğruluk ve mekânsal doğrulama (5)

| ID | Kaynak | Başlık | Dergi / yayın | DOI | Bölge | Konu | Kullanılacağı yer | Öncelik |
|---|---|---|---|---|---|---|---|---|
| L19 | Olofsson ve ark. (2014) | Good practices for estimating area and assessing accuracy of land change | Remote Sensing of Environment | [10.1016/j.rse.2014.02.015](https://doi.org/10.1016/j.rse.2014.02.015) | — | Doğruluk değerlendirme ve alan tahmini iyi uygulamaları | Yöntem / 03–04 | 1 |
| L20 | Foody (2020) | Explaining the unsuitability of the kappa coefficient in the assessment and comparison of the accuracy of thematic maps obtained by image classification | Remote Sensing of Environment | [10.1016/j.rse.2019.111630](https://doi.org/10.1016/j.rse.2019.111630) | — | Kappa'nın sınırlılıkları | Tartışma / Sınırlılık | 1 |
| L21 | Roberts ve ark. (2017) | Cross‐validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure | Ecography | [10.1111/ecog.02881](https://doi.org/10.1111/ecog.02881) | — | Mekânsal yapılı verilerde CV (blok CV gerekçesi) | Yöntem / 04–06 | 1 |
| L22 | Meyer ve ark. (2018) | Improving performance of spatio-temporal machine learning models using forward feature selection and target-oriented validation | Environmental Modelling & Software | [10.1016/j.envsoft.2017.12.001](https://doi.org/10.1016/j.envsoft.2017.12.001) | — | Konum dışı (leave-location-out) CV | Yöntem / 06 | 1 |
| L23 | Ploton ve ark. (2020) | Spatial validation reveals poor predictive performance of large-scale ecological mapping models | Nature Communications | [10.1038/s41467-020-18321-y](https://doi.org/10.1038/s41467-020-18321-y) | Küresel | Mekânsal doğrulama ve rastgele CV farkı | Tartışma / 06 | 1 |

## E. Açıklanabilirlik (SHAP) (2)

| ID | Kaynak | Başlık | Dergi / yayın | DOI | Bölge | Konu | Kullanılacağı yer | Öncelik |
|---|---|---|---|---|---|---|---|---|
| L24 | Lundberg ve Lee (2017) | A Unified Approach to Interpreting Model Predictions | arXiv | [10.48550/arXiv.1705.07874](https://doi.org/10.48550/arXiv.1705.07874) | — | SHAP özgün kaynağı (NeurIPS 2017; arXiv DOI) | Yöntem / 03 | 1 |
| L25 | Lundberg ve ark. (2020) | From local explanations to global understanding with explainable AI for trees | Nature Machine Intelligence | [10.1038/s42256-019-0138-9](https://doi.org/10.1038/s42256-019-0138-9) | — | TreeSHAP (ağaç modelleri için SHAP) | Yöntem / 03 | 2 |

## F. LST ve kentsel ısı adası (genel) (4)

| ID | Kaynak | Başlık | Dergi / yayın | DOI | Bölge | Konu | Kullanılacağı yer | Öncelik |
|---|---|---|---|---|---|---|---|---|
| L26 | Weng ve ark. (2004) | Estimation of land surface temperature–vegetation abundance relationship for urban heat island studies | Remote Sensing of Environment | [10.1016/j.rse.2003.11.005](https://doi.org/10.1016/j.rse.2003.11.005) | ABD (Indianapolis) | LST–bitki örtüsü ilişkisi; UHI | Literatür / 04 | 1 |
| L27 | Yuan ve Bauer (2007) | Comparison of impervious surface area and normalized difference vegetation index as indicators of surface urban heat island effects in Landsat imagery | Remote Sensing of Environment | [10.1016/j.rse.2006.09.003](https://doi.org/10.1016/j.rse.2006.09.003) | ABD (Minnesota) | Geçirimsiz yüzey ve NDVI'nin LST göstergesi olarak karşılaştırması | Literatür / 04 | 1 |
| L28 | Peng ve ark. (2011) | Surface Urban Heat Island Across 419 Global Big Cities | Environmental Science & Technology | [10.1021/es2030438](https://doi.org/10.1021/es2030438) | Küresel (419 şehir) | Yüzey UHI'nin küresel karşılaştırması | Literatür / 04 | 1 |
| L29 | Zhou ve ark. (2018) | Satellite Remote Sensing of Surface Urban Heat Islands: Progress, Challenges, and Perspectives | Remote Sensing | [10.3390/rs11010048](https://doi.org/10.3390/rs11010048) | Küresel (derleme) | Uydudan yüzey UHI derlemesi | Literatür / 04 | 1 |

## G. Türkiye çalışmaları (15)

| ID | Kaynak | Başlık | Dergi / yayın | DOI | Bölge | Konu | Kullanılacağı yer | Öncelik |
|---|---|---|---|---|---|---|---|---|
| L30 | Kuru ve Okay (2025) | Investigating the relationship between urban growth pattern and urban heat islands: the case of Istanbul, Turkey | Environmental Earth Sciences | [10.1007/s12665-024-12064-5](https://doi.org/10.1007/s12665-024-12064-5) | İstanbul | Kentsel büyüme deseni – UHI | Literatür / 04 / Tartışma | 1 |
| L31 | Uygur Erdoğan ve ark. (2024) | Evaluation of the Land Use/Land Cover (LULC) Change Effects on Land Surface Temperature (LST): A Case Study of Kağıthane Watershed | Kastamonu Üniversitesi Orman Fakültesi Dergisi | [10.17475/kastorman.1557407](https://doi.org/10.17475/kastorman.1557407) | İstanbul (Kağıthane) | LULC değişimi – LST | Literatür / 04 | 2 |
| L32 | Büyüksalih (2016) | Landsat Images Classification and Change Analysis of Land Cover/Use in Istanbul | International Journal of Environment and Geoinformatics | [10.30897/ijegeo.304484](https://doi.org/10.30897/ijegeo.304484) | İstanbul | Landsat sınıflandırma ve değişim analizi | Literatür / 03–04 | 2 |
| L33 | Yagmur ve ark. (2022) | Assessment of Rapid Urbanization Effects with Remote Sensing Techniques | Lecture Notes in Networks and Systems | [10.1007/978-3-030-94191-8_46](https://doi.org/10.1007/978-3-030-94191-8_46) | İstanbul (Büyükçekmece) | Hızlı kentleşme etkileri, uzaktan algılama | Literatür | 3 |
| L34 | KESGİN ATAK (2020) | ANALYSING THE RELATIONSHIPS BETWEEN LAND USE/LAND COVER AND URBAN LAND SURFACE TEMPERATURE USING REGRESSION TREE IN İZMİR | lnternational Journal of Geography and Geography Education | [10.32003/igge.632841](https://doi.org/10.32003/igge.632841) | İzmir | LULC – kentsel LST, regresyon ağacı | Literatür / 04 | 1 |
| L35 | KESGİN ATAK ve ERSOY TONYALOĞLU (2020) | Evaluation of the effect of land use / land cover and vegetation cover change on land surface temperature: The case of Aydın province | Turkish Journal of Forestry | Türkiye Ormancılık Dergisi | [10.18182/tjf.786827](https://doi.org/10.18182/tjf.786827) | Aydın | LULC ve bitki örtüsü değişimi – LST | Literatür / 04 | 2 |
| L36 | Aslan ve Koc-San (2021) | The Use of Land Cover Indices for Rapid Surface Urban Heat Island Detection from Multi-Temporal Landsat Imageries | ISPRS International Journal of Geo-Information | [10.3390/ijgi10060416](https://doi.org/10.3390/ijgi10060416) | Bursa | Arazi örtüsü indeksleriyle yüzey UHI tespiti | Literatür / 04 | 2 |
| L37 | Orhan ve Yakar (2016) | Investigating Land Surface Temperature Changes Using Landsat Data in Konya, Turkey | The International Archives of the Photogrammetry, Remote Sensing and Spatial Information Sciences | [10.5194/isprs-archives-XLI-B8-285-2016](https://doi.org/10.5194/isprs-archives-XLI-B8-285-2016) | Konya | Landsat ile LST değişimi | Literatür / 04 | 1 |
| L38 | ORHAN ve ark. (2019) | Investigating land surface temperature changes using Landsat-5 data and real-time infrared thermometer measurements at Konya Closed Basin in Turkey | International Journal of Engineering and Geosciences | [10.26833/ijeg.417151](https://doi.org/10.26833/ijeg.417151) | Konya Kapalı Havzası | Landsat-5 LST ve yer ölçümü | Literatür / 04 | 2 |
| L39 | Akdeniz (2023) | SPATIO-TEMPORAL ANALYSIS OF THE EFFECTS OF URBAN GROWTH ON URBAN HEAT ISLAND: CASE OF KONYA, TURKIYE | The International Archives of the Photogrammetry, Remote Sensing and Spatial Information Sciences | [10.5194/isprs-archives-XLVIII-M-1-2023-441-2023](https://doi.org/10.5194/isprs-archives-XLVIII-M-1-2023-441-2023) | Konya | Kentsel büyümenin UHI'ye etkisi | Literatür / 04 | 1 |
| L40 | Koklu ve ark. (2025) | THE IMPACT OF URBAN GROWTH ON LAND SURFACE TEMPERATURE IN KONYA PROVINCE's SELÇUKLU DISTRICT | Konya Journal of Engineering Sciences | [10.36306/konjes.1552187](https://doi.org/10.36306/konjes.1552187) | Konya (Selçuklu) | Kentsel büyüme – LST | Literatür / 04 | 2 |
| L41 | Güler ve ark. (2006) | Using landsat data to determine land use/land cover changes in Samsun, Turkey | Environmental Monitoring and Assessment | [10.1007/s10661-006-9270-1](https://doi.org/10.1007/s10661-006-9270-1) | Samsun | Landsat ile LULC değişimi | Literatür / 03–04 | 1 |
| L42 | Degerli ve Çetin (2022) | Using the Remote Sensing Method to Simulate the Land Change in the Year 2030 | Turkish Journal of Agriculture - Food Science and Technology | [10.24925/turjaf.v10i12.2453-2466.5555](https://doi.org/10.24925/turjaf.v10i12.2453-2466.5555) | Samsun | Arazi değişimi simülasyonu (2030) | Literatür | 3 |
| L43 | Saralıoğlu ve Alahmed (2025) | Yusufeli Barajı Su Tutma Sonrası Arazi Örtüsü Değişimlerinin Google Earth Engine ile Analizi | Turkish Journal of Remote Sensing and GIS | [10.48123/rsgis.1660237](https://doi.org/10.48123/rsgis.1660237) | Artvin (Yusufeli) | Baraj sonrası arazi örtüsü değişimi, GEE (Sentinel-2) | Literatür / 04 (Artvin yorumu) | 1 |
| L44 | Karabulut ve ark. (2023) | Socioeconomic driving forces of land use/cover changes in the semi-arid Harran plain and their probable implications on arising groundwater level, the GAP area of southeastern Türkiye | Acta Geophysica | [10.1007/s11600-023-01162-w](https://doi.org/10.1007/s11600-023-01162-w) | Şanlıurfa (Harran) | GAP bölgesi LULC değişimi ve yeraltı suyu | Literatür / 04 (Şanlıurfa yorumu) | 1 |

## H. Bölgeler arası genelleme (2)

| ID | Kaynak | Başlık | Dergi / yayın | DOI | Bölge | Konu | Kullanılacağı yer | Öncelik |
|---|---|---|---|---|---|---|---|---|
| L45 | Tong ve ark. (2020) | Land-cover classification with high-resolution remote sensing images using transferable deep models | Remote Sensing of Environment | [10.1016/j.rse.2019.111322](https://doi.org/10.1016/j.rse.2019.111322) | Çin | Aktarılabilir derin modelle arazi örtüsü sınıflandırma | Literatür / 06 | 2 |
| L46 | Siddamsetty ve ark. (2023) | INTER-REGION TRANSFER LEARNING FOR LAND USE LAND COVER CLASSIFICATION | ISPRS Annals of the Photogrammetry, Remote Sensing and Spatial Information Sciences | [10.5194/isprs-annals-X-1-W1-2023-881-2023](https://doi.org/10.5194/isprs-annals-X-1-W1-2023-881-2023) | Avrupa (BigEarthNet) | Bölgeler arası transfer öğrenme (LULC) | Literatür / 06 | 2 |

## I. İDA / yüzen atık tespiti (10)

| ID | Kaynak | Başlık | Dergi / yayın | DOI | Bölge | Konu | Kullanılacağı yer | Öncelik |
|---|---|---|---|---|---|---|---|---|
| L47 | Radam ve ark. (2026) | Floating Waste and Aquatic Vegetation Image Dataset from Turbid Rivers | Mendeley Data | [10.17632/j26w4m645z.2](https://doi.org/10.17632/j26w4m645z.2) | Endonezya (Banjarmasin) | Faz 5'te KULLANILAN veri seti | Veri / 05 | 1 |
| L48 | Cheng ve ark. (2021) | FloW: A Dataset and Benchmark for Floating Waste Detection in Inland Waters | 2021 IEEE/CVF International Conference on Computer Vision (ICCV) | [10.1109/ICCV48922.2021.01077](https://doi.org/10.1109/ICCV48922.2021.01077) | Çin (iç sular) | FloW veri seti — KULLANILAMADI; yalnızca farklı veri setinde raporlanan değer | Literatür / 05 (dolaylı) | 1 |
| L49 | Redmon ve ark. (2016) | You Only Look Once: Unified, Real-Time Object Detection | 2016 IEEE Conference on Computer Vision and Pattern Recognition (CVPR) | [10.1109/CVPR.2016.91](https://doi.org/10.1109/CVPR.2016.91) | — | YOLO özgün kaynağı | Yöntem / 05 | 1 |
| L50 | Li ve ark. (2023) | A Floating-Waste-Detection Method for Unmanned Surface Vehicle Based on Feature Fusion and Enhancement | Journal of Marine Science and Engineering | [10.3390/jmse11122234](https://doi.org/10.3390/jmse11122234) | — | İDA (USV) için yüzen atık tespiti | Literatür / 05 | 1 |
| L51 | Dong ve ark. (2025) | Optimized YOLOv8 for Lightweight Floating Object Detection on Unmanned Surface Vehicles | Information Technology and Control | [10.5755/j01.itc.54.3.38966](https://doi.org/10.5755/j01.itc.54.3.38966) | — | İDA (USV) üzerinde hafif YOLOv8 ile yüzen nesne tespiti | Literatür / 05 | 1 |
| L52 | Chen ve ark. (2025) | A Novel Method for Water Surface Debris Detection Based on YOLOV8 with Polarization Interference Suppression | Photonics | [10.3390/photonics12060620](https://doi.org/10.3390/photonics12060620) | — | YOLOv8 + polarizasyon; su yansıması sorunu | Literatür / 05 (sınırlılık) | 2 |
| L53 | Kataoka ve ark. (2024) | Instance segmentation models for detecting floating macroplastic debris from river surface images | Frontiers in Earth Science | [10.3389/feart.2024.1427132](https://doi.org/10.3389/feart.2024.1427132) | Japonya (nehirler) | YOLOv8 örnek bölütleme ile nehir makroplastiği | Literatür / 05 | 1 |
| L54 | van Lieshout ve ark. (2020) | Automated River Plastic Monitoring Using Deep Learning and Cameras | Earth and Space Science | [10.1029/2019EA000960](https://doi.org/10.1029/2019EA000960) | Endonezya (Jakarta) | Kamera + derin öğrenmeyle nehir plastiği izleme | Literatür / 05 | 1 |
| L55 | Devi ve ark. (2024) | Yolo-based Deep Learning Techniques for Identifying Floating Bottles in Inland Water: A Comprehensive Analysis | 2024 15th International Conference on Computing Communication and Networking Technologies (ICCCNT) | [10.1109/icccnt61001.2024.10724494](https://doi.org/10.1109/icccnt61001.2024.10724494) | — | İç sularda şişe tespiti için YOLO sürümleri | Literatür / 05 | 3 |
| L56 | Padilla ve ark. (2021) | A Comparative Analysis of Object Detection Metrics with a Companion Open-Source Toolkit | Electronics | [10.3390/electronics10030279](https://doi.org/10.3390/electronics10030279) | — | Nesne tespiti metrikleri (mAP) | Yöntem / 05 | 1 |

## [DOĞRULANMADI]

| Bölge | Konu (arama sonucundan) | Bağlantı | Kullanılacağı yer | Durum |
|---|---|---|---|---|
| Van | Van kentinde ısı adası ve sıcaklık değişimi (Landsat + ASTER, 1990–2021) | https://dergipark.org.tr/en/pub/visbid/article/1084820 | Literatür / 04 (Van yorumu) | DOI bulunamadı; makale sayfasından künye ve DOI kontrol edilmeli |

## Yazılım (DOI'siz, künye olarak verilir)

| Yazılım | Kullanıldığı yer | Not |
|---|---|---|
| Ultralytics YOLOv8 (Jocher ve ark., 2023) | 05 | Künye: github.com/ultralytics/ultralytics; sürüm numarası requirements.txt ile aynı yazılmalı |
| scikit-learn (Pedregosa ve ark., 2011, JMLR 12) | 03, 06 | JMLR makalesinin DOI'si yok; dergi künyesiyle verilir |
