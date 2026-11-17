/* GeoClimate AI — etkileşimli sonuç sitesi.
 * Bütün sayılar data/ozet.json'dan, hücre değerleri data/hucre/<il>.json'dan gelir (web/veri_hazirla.py üretir).
 * Arazi örtüsü sınıfları: Faz 3'te Colab'da eğitilen XGBoost modelinin (best_model.joblib) 2014 ve 2024
 * sınıflandırması (04 notebook'u, Drive grid_1km_lc_iklim.csv). Site hiçbir şeyi yeniden hesaplamaz. */

// ---------------------------------------------------------------- yardımcılar
proj4.defs("EPSG:3035", "+proj=laea +lat_0=52 +lon_0=10 +x_0=4321000 +y_0=3210000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs");
const LAEA = proj4("EPSG:3035", "EPSG:4326");
const sayi = (x, n = 2) => x == null ? "—" : x.toLocaleString("tr-TR", { minimumFractionDigits: n, maximumFractionDigits: n }).replace("-", "−");
const isaretli = (x, n = 2) => x == null ? "—" : (x > 0 ? "+" : "") + sayi(x, n);
const guc = r => { const a = Math.abs(r); return a < 0.1 ? "ihmal edilebilir" : a < 0.3 ? "zayıf" : a < 0.5 ? "orta" : "güçlü"; };
const $ = s => document.querySelector(s);

const SINIF = [["Orman", "#1b7837"], ["Tarım", "#f1a340"], ["Yapılaşma", "#d73027"], ["Çayır/Çalı", "#a6d96a"],
  ["Çıplak", "#bababa"], ["Su/Sulak alan", "#4575b4"]];
const SINIF_KOD = ["Orman", "Tarim", "Yapilasma", "Cayir_Cali", "Ciplak", "Su_Sulak"];
const SEFFAF = "rgba(0,0,0,0)";

// ---------------------------------------------------------------- harita katmanları
// kat: kategorik [değer, etiket, renk]; kademe: sınırlar + renkler (sınır sayısı + 1 renk)
const KATMAN = {
  arazi: { ad: "Arazi örtüsü 2024", alan: "b24", tur: "kat", kat: SINIF.map(([a, r], i) => [i, a, r]).concat([[-1, "Veri yok", SEFFAF]]),
    not: "Her 1 km hücrede baskın sınıf. Sınıflandırma: eğittiğimiz XGBoost modeli." },
  degisim: { ad: "Arazi değişimi", alan: "dg", tur: "kat",
    kat: [[9, "Değişmedi", "#d9d9d9"]].concat(SINIF.map(([a, r], i) => [i, "→ " + a, r])).concat([[-1, "Veri yok", SEFFAF]]),
    not: "Baskın sınıfı 2014→2024 değişen hücreler, yeni sınıfın renginde. 2014/2024 doğruluğu ölçülemiyor." },
  lst: { ad: "Yüzey sıcaklığı 2024", alan: "lst24", tur: "kademe", dinamik: true, birim: " °C",
    renk: ["#ffffb2", "#fed976", "#feb24c", "#fd8d3c", "#f03b20", "#bd0026"],
    not: "Landsat yaz kompoziti, yer yüzeyinin sıcaklığı (hava sıcaklığı değil). Sınırlar ilin yüzdeliklerinden." },
  dlst: { ad: "Sıcaklık değişimi (göreli)", alan: "dl", tur: "kademe", sinir: [-3, -1.5, -0.5, 0.5, 1.5, 3], birim: " °C",
    renk: ["#2166ac", "#67a9cf", "#d1e5f0", "#f7f7f7", "#fddbc7", "#ef8a62", "#b2182b"],
    not: "2014→2024 yaz LST farkı − ilin medyan farkı. İki yazın genel hava farkını giderir." },
  dndvi: { ad: "Bitki örtüsü değişimi", alan: "dn", tur: "kademe", sinir: [-0.15, -0.05, 0.05, 0.15], birim: "",
    renk: ["#a6611a", "#dfc27d", "#f5f5f5", "#80cdc1", "#018571"], not: "ΔNDVI 2014→2024. Kahverengi: bitki azaldı, yeşil: arttı." },
  dndmi: { ad: "Yüzey nemi değişimi (göreli)", alan: "dm", tur: "kademe", sinir: [-0.08, -0.03, 0.03, 0.08], birim: "",
    renk: ["#8c510a", "#d8b365", "#f5f5f5", "#5ab4ac", "#01665e"], not: "ΔNDMI − ilin medyanı. NDMI bitki/yüzey nemini gösterir, doğrudan toprak nemi değildir." },
  kent: { ad: "Kentleşme", alan: "yd", tur: "kat",
    kat: [[2, "Yapılaşma (iki yılda da)", "#67000d"], [1, "Yeni yapılaşma", "#ff7f00"], [3, "Yapılaşmadan çıkan", "#fdd0a2"],
      [0, "Diğer", "rgba(120,120,120,0.08)"], [-1, "Veri yok", SEFFAF]],
    not: "Yapılaşma payı > %50 olan hücreler. \"Çıkan\" hücreler çoğunlukla sınıflandırma belirsizliğidir." },
  su: { ad: "Su yüzeyi değişimi", alan: "sd", tur: "kat",
    kat: [[2, "Kalıcı su", "#08519c"], [1, "Yeni su yüzeyi", "#00b4d8"], [3, "Kaybolan su yüzeyi", "#f16913"],
      [0, "Kara", SEFFAF], [-1, "Veri yok", SEFFAF]], not: "MNDWI > 0 olan piksellerin hücredeki payı > %50." },
  sulak: { ad: "Su ve sulak alanlar", alan: "sl", tur: "kat",
    kat: [[2, "Kalıcı su", "#2171b5"], [1, "Otsu sulak alan", "#41ab5d"], [0, "Diğer", SEFFAF]],
    not: "ESA WorldCover 2021: kalıcı su payı > %50 ya da otsu sulak alan payı ≥ %20." },
  tarim: { ad: "Tarım payı 2024", alan: "tp", tur: "kademe", sinir: [11, 33, 55, 77], birim: " %",
    renk: ["#fff5eb", "#fdd0a2", "#fd8d3c", "#d94801", "#7f2704"], not: "Hücredeki 9 noktanın kaçının tarım sınıflandırıldığı." },
  dtarim: { ad: "Tarım değişimi", alan: "dtp", tur: "kademe", sinir: [-33, -11, 11, 33], birim: " puan",
    renk: ["#8c510a", "#d8b365", "#f5f5f5", "#fdae61", "#d7301f"], not: "Tarım payı 2014→2024 (puan). Turuncu-kırmızı: tarım arttı." },
  orman: { ad: "Orman payı 2024", alan: "op", tur: "kademe", sinir: [11, 33, 55, 77], birim: " %",
    renk: ["#f7fcf5", "#c7e9c0", "#74c476", "#238b45", "#00441b"], not: "Hücredeki 9 noktanın kaçının orman sınıflandırıldığı." },
};

// ---------------------------------------------------------------- il temaları (sayılar ozet.json'dan)
const TEMA = {
  Istanbul: { renk: "#b2182b", tema: "Kentleşme ve kentsel ısı adası", soru: "AS2 · H1 — Yapılaşmış alanların genişlemesi yüzey sıcaklığıyla ilişkili mi?",
    katman: ["lst", "kent", "dlst", "arazi", "degisim", "dndvi"],
    kartlar: o => [["Kentsel ısı adası 2024", isaretli(o.uhi["2024"], 1) + " °C", "kent − kırsal yaz LST · 2014: " + isaretli(o.uhi["2014"], 1) + " °C"],
      ["Yapılaşma payı", isaretli(o.sinif.Yapilasma.pp) + " puan", "%" + sayi(o.sinif.Yapilasma.y0, 1) + " → %" + sayi(o.sinif.Yapilasma.y1, 1)],
      ["Δyapılaşma ↔ ΔLST", "ρ = " + isaretli(o.rho.yapi), guc(o.rho.yapi) + " ilişki (H1)"]],
    hikaye: o => `<p>Kentsel hücreler (yapılaşma payı &gt; %50) kırsal hücrelerden yazın yüzeyde <b>${sayi(o.uhi["2024"], 1)} °C</b> daha sıcak.
      <b>Yüzey sıcaklığı</b> ile <b>Kentleşme</b> katmanlarını sırayla açın: en sıcak alanlar yapılaşmış alanlarla örtüşüyor.</p>
      <p>2014→2024 arasında yapılaşma payı ${isaretli(o.sinif.Yapilasma.pp)} puan değişti. Hücre düzeyinde yapılaşma artışı ile sıcaklık
      değişimi arasındaki ilişki <b>${guc(o.rho.yapi)}</b> (ρ = ${isaretli(o.rho.yapi)}): ısı adası belirgin, on yıllık değişimin etkisi küçük.</p>` },
  Izmir: { renk: "#d6604d", tema: "Kıyı kentleşmesi ve kentsel ısı adası", soru: "AS2 · H1 — Yapılaşmış alanların genişlemesi yüzey sıcaklığıyla ilişkili mi?",
    katman: ["lst", "kent", "dlst", "arazi", "degisim", "sulak"],
    kartlar: o => [["Kentsel ısı adası 2024", isaretli(o.uhi["2024"], 1) + " °C", "kent − kırsal yaz LST · 2014: " + isaretli(o.uhi["2014"], 1) + " °C"],
      ["Yapılaşma payı", isaretli(o.sinif.Yapilasma.pp) + " puan", "%" + sayi(o.sinif.Yapilasma.y0, 1) + " → %" + sayi(o.sinif.Yapilasma.y1, 1)],
      ["Δyapılaşma ↔ ΔLST", "ρ = " + isaretli(o.rho.yapi), guc(o.rho.yapi) + " ilişki (H1)"]],
    hikaye: o => `<p>İzmir'de ısı adası İstanbul'dan çok daha zayıf: kent ile kırsal arasındaki yaz yüzey sıcaklığı farkı <b>${sayi(o.uhi["2024"], 1)} °C</b>
      (2014: ${sayi(o.uhi["2014"], 1)} °C). Kıyıya yakın kent dokusu ve kırsal referansın konumu bu farkı etkiliyor olabilir.</p>
      <p>Yapılaşma payı ${isaretli(o.sinif.Yapilasma.pp)} puan değişti; yapılaşma artışı ile sıcaklık değişimi arasındaki ilişki <b>${guc(o.rho.yapi)}</b>.</p>`,
    uyari: "İstanbul–İzmir ısı adası farkının bir kısmı tanımdan (kırsal referans hücreleri) kaynaklanabilir." },
  Artvin: { renk: "#1b7837", tema: "Orman örtüsü ve yüzey sıcaklığı", soru: "AS1 · H2 — Orman ve bitki örtüsündeki değişim yüzey sıcaklığıyla ilişkili mi?",
    katman: ["dndvi", "dlst", "orman", "su", "degisim", "arazi"],
    kartlar: o => [["Orman payı", isaretli(o.sinif.Orman.pp) + " puan", "%" + sayi(o.sinif.Orman.y0, 1) + " → %" + sayi(o.sinif.Orman.y1, 1)],
      ["ΔNDVI ↔ ΔLST", "ρ = " + isaretli(o.rho.ndvi), guc(o.rho.ndvi) + " · bitki azalan yer görece ısınıyor (H2)"],
      ["Açık su alanı", isaretli(o.su_degisim_yuzde, 1) + " %", "MNDWI 2014 → 2024"]],
    hikaye: o => `<p><b>Bitki örtüsü değişimi</b> ile <b>Sıcaklık değişimi</b> katmanlarını karşılaştırın: kahverengi (bitki azalan) hücreler
      çoğunlukla kırmızı (görece ısınan), yeşil hücreler mavi. İlişki <b>${guc(o.rho.ndvi)}</b> (ρ = ${isaretli(o.rho.ndvi)}).</p>
      <p>Orman payı ${isaretli(o.sinif.Orman.pp)} puan değişti. Açık su alanı %${sayi(o.su_degisim_yuzde, 1)} arttı; <b>Su yüzeyi değişimi</b>
      katmanında yeni su yüzeylerinin vadilerde toplandığını görebilirsiniz.</p>`,
    uyari: "Su artışının olası nedeni yeni baraj gölleri (ör. Yusufeli) — kaynakla doğrulanmalı. Dağlık ve bulutlu bölge: 2014 LST eksik oranı daha yüksek." },
  Samsun: { renk: "#2166ac", tema: "Delta ve sulak alanlar", soru: "AS3 · H4 — Su yüzeyi ve sulak alan değişimi sıcaklık ve nemle ilişkili mi?",
    katman: ["sulak", "su", "dlst", "arazi", "degisim", "dndvi"],
    kartlar: o => [["Açık su alanı", isaretli(o.su_degisim_yuzde, 1) + " %", "MNDWI 2014 → 2024"],
      ["Otsu sulak alan", sayi(o.sulak_km2, 0) + " km²", "WorldCover 2021, payı ≥ %20 olan hücreler"],
      ["Δsu ↔ ΔLST", "ρ = " + isaretli(o.rho.su), guc(o.rho.su) + " ilişki (H4)"]],
    hikaye: o => `<p><b>Su ve sulak alanlar</b> katmanı kalıcı suyu ve otsu sulak alanları gösteriyor; nerede toplandıklarına bakın.
      Otsu sulak alanlar yaz görüntüsünde bitki gibi göründüğü için modelimiz bunları çoğunlukla başka sınıflara atıyor.</p>
      <p>Açık su alanı %${sayi(o.su_degisim_yuzde, 1)} değişti. Su değişimi ile sıcaklık değişimi arasındaki ilişki <b>${guc(o.rho.su)}</b>
      (ρ = ${isaretli(o.rho.su)}): 1 km hücrelerde su değişimi küçük olduğu için H4 burada desteklenmiyor.</p>`,
    uyari: "Sulak alan değişimi tek bir yaz görüntüsüyle güvenilir ölçülemez; çok mevsimli veri ya da radar (Sentinel-1) gerekir." },
  Konya: { renk: "#b8860b", tema: "Tarım, kuraklık ve toprak nemi", soru: "AS4 · H3 — Tarımsal alan değişimi bitki örtüsü ve nemle ilişkili mi?",
    katman: ["tarim", "dndmi", "dtarim", "dlst", "arazi", "degisim"],
    kartlar: o => [["Δtarım ↔ ΔNDMI", "ρ = " + isaretli(o.rho.tarim_ndmi), guc(o.rho.tarim_ndmi) + " · 7 il içinde en güçlü (H3)"],
      ["Tarım payı", isaretli(o.sinif.Tarim.pp) + " puan", "%" + sayi(o.sinif.Tarim.y0, 1) + " → %" + sayi(o.sinif.Tarim.y1, 1)],
      ["Yaz toprak nemi (ERA5)", isaretli(o.trend.era5_sm_summer.sen10, 3), "10 yılda · p = " + sayi(o.trend.era5_sm_summer.p, 3)]],
    hikaye: o => `<p>Konya'da tarım payı il genelinde neredeyse değişmedi (${isaretli(o.sinif.Tarim.pp)} puan), ama <b>yerel</b> değişimler büyük.
      <b>Tarım değişimi</b> ve <b>Yüzey nemi değişimi</b> katmanlarını karşılaştırın: tarımın arttığı hücrelerde yüzey nemi de artıyor
      (ρ = ${isaretli(o.rho.tarim_ndmi)}, ${guc(o.rho.tarim_ndmi)}).</p>
      <p>Modelin hiç görmediği bir ile taşınınca en çok başarı kaybettiği il Konya: kurak iç illerde aynı sınıf başka türlü görünüyor.</p>`,
    uyari: "NDMI bitki ve yüzey nemini gösterir, doğrudan toprak nemi ölçümü değildir. ERA5 toprak nemi ~9–11 km çözünürlükte, yalnızca il ortalaması." },
  Van: { renk: "#2171b5", tema: "Göl havzası ve su yüzeyi", soru: "AS3 · H4 — Göl ve su yüzeyi değişimi çevresel göstergelerle ilişkili mi?",
    katman: ["su", "dlst", "dndvi", "arazi", "degisim", "sulak"],
    kartlar: o => [["Açık su alanı", isaretli(o.su_degisim_yuzde, 1) + " %", "MNDWI 2014 → 2024"],
      ["Yaz toprak nemi (ERA5)", isaretli(o.trend.era5_sm_summer.sen10, 3), "10 yılda · p = " + sayi(o.trend.era5_sm_summer.p, 3) + (o.trend.era5_sm_summer.p < 0.05 ? " (anlamlı)" : "")],
      ["ΔNDVI ↔ ΔLST", "ρ = " + isaretli(o.rho.ndvi), guc(o.rho.ndvi) + " ilişki (H2)"]],
    hikaye: o => `<p><b>Su yüzeyi değişimi</b> katmanında göl kıyısında yeni ve kaybolan su yüzeylerine bakın. Açık su alanı %${sayi(o.su_degisim_yuzde, 1)} değişti;
      su değişimi ile sıcaklık değişimi arasındaki ilişki <b>${guc(o.rho.su)}</b> (ρ = ${isaretli(o.rho.su)}).</p>
      <p>Van'da yaz toprak nemi 2003–2024 arasında anlamlı biçimde azalıyor (10 yılda ${isaretli(o.trend.era5_sm_summer.sen10, 3)} m³/m³).
      Bitki örtüsü ile sıcaklık arasındaki ilişki <b>${guc(o.rho.ndvi)}</b>.</p>`,
    uyari: "Su artışının göl seviyesinden mi, 2014 kompozitinin kalitesinden mi kaynaklandığı kontrol edilmeli." },
  Sanliurfa: { renk: "#e08214", tema: "Sulu tarım (GAP) ve yüzey sıcaklığı", soru: "AS1 · AS4 · H2–H3 — Tarımın genişlemesi bitki örtüsü ve yüzey sıcaklığıyla ilişkili mi?",
    katman: ["dtarim", "dlst", "dndvi", "tarim", "arazi", "degisim"],
    kartlar: o => [["Tarım payı", isaretli(o.sinif.Tarim.pp) + " puan", "%" + sayi(o.sinif.Tarim.y0, 1) + " → %" + sayi(o.sinif.Tarim.y1, 1)],
      ["ΔNDVI ↔ ΔLST", "ρ = " + isaretli(o.rho.ndvi), guc(o.rho.ndvi) + " · 7 il içinde en güçlü"],
      ["Yaz yüzey sıcaklığı (MODIS)", isaretli(o.trend.modis_lst_day.sen10, 2) + " °C", "10 yılda · p = " + sayi(o.trend.modis_lst_day.p, 4)]],
    hikaye: o => `<p>Şanlıurfa'da tarım payı ${isaretli(o.sinif.Tarim.pp)} puan arttı. <b>Tarım değişimi</b>, <b>Bitki örtüsü değişimi</b> ve
      <b>Sıcaklık değişimi</b> katmanlarını sırayla açın: bitki artan yerler görece serinliyor (ρ = ${isaretli(o.rho.ndvi)}, 7 il içinde en güçlü ilişki).</p>
      <p>Uzun dönemde de yaz yüzey sıcaklığı 10 yılda ${isaretli(o.trend.modis_lst_day.sen10, 2)} °C azalıyor (MODIS, 2003–2024).</p>`,
    uyari: "Bu örüntü sulu tarımla (GAP) tutarlı, ama neden-sonuç iddiası değildir; kaynakla desteklenmeli." },
};

// ---------------------------------------------------------------- durum
let OZET, ILLER_GEO, HARITA, GENEL, seciliIl = "Istanbul", seciliKatman = null, iklimGrafik, sinifGrafik, haritaHazir;
const HUCRE = {};

// Anahtar gerektirmeyen Esri altlıkları (CARTO artık API anahtarı istiyor)
const ESRI = "https://server.arcgisonline.com/ArcGIS/rest/services/";
const ALTLIK = {
  sade: { tiles: [ESRI + "Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}"], maxzoom: 16,
    attribution: "Altlık: Esri, HERE, Garmin, © OpenStreetMap katkıcıları" },
  uydu: { tiles: [ESRI + "World_Imagery/MapServer/tile/{z}/{y}/{x}"], maxzoom: 19,
    attribution: "Uydu: Esri, Maxar, Earthstar Geographics" },
  koyu: { tiles: [ESRI + "Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"], maxzoom: 16,
    attribution: "Altlık: Esri, HERE, Garmin, © OpenStreetMap katkıcıları" },
};
const stil = altlik => ({ version: 8, glyphs: "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
  sources: { altlik: { type: "raster", tiles: ALTLIK[altlik].tiles, tileSize: 256, attribution: ALTLIK[altlik].attribution, maxzoom: ALTLIK[altlik].maxzoom } },
  layers: [{ id: "altlik", type: "raster", source: "altlik" }] });

// ---------------------------------------------------------------- başlat
(async function () {
  [OZET, ILLER_GEO] = await Promise.all([fetch("data/ozet.json").then(r => r.json()), fetch("data/iller.json").then(r => r.json())]);
  istatistikler();
  genelHarita();
  ilSecici();
  hipotezler();
  modelGrafikleri();
  haritaHazir = ilHaritasi();            // beklenmez: yazılar ve grafikler harita yüklenmeden gösterilir
  ilSec(location.hash.replace("#", "") in TEMA ? location.hash.replace("#", "") : "Istanbul", false);
})();

function istatistikler() {
  const m = OZET.modeller.XGBoost, r = OZET.lst_regresyon.RandomForestRegressor;
  $("#istatistikler").innerHTML = [
    [sayi(m.f1, 3), "arazi örtüsü sınıflandırma başarısı (XGBoost, macro-F1)"],
    [sayi(r.r2, 2), "yüzey sıcaklığını açıklama gücü (R²)"],
    [OZET.ndvi_negatif_il + "/7", "ilde bitki azalan yer görece ısınıyor"],
    ["−" + sayi(OZET.loco_ort_dusus, 2), "F1 kaybı: model hiç görmediği ile taşınınca"],
  ].map(([b, s]) => `<div class="istatistik"><b>${b}</b><span>${s}</span></div>`).join("");
}

function genelHarita() {
  GENEL = new maplibregl.Map({ container: "genel-harita", style: stil("koyu"), bounds: [25.5, 35.6, 45, 42.3],
    fitBoundsOptions: { padding: 10 }, attributionControl: { compact: true }, dragRotate: false });
  GENEL.once("style.load", () => {
    GENEL.addSource("iller", { type: "geojson", data: ILLER_GEO, generateId: true });   // id = dizideki sıra
    GENEL.addLayer({ id: "tum", type: "line", source: "iller", paint: { "line-color": "rgba(255,255,255,0.18)", "line-width": 0.6 } });
    const renk = ["match", ["get", "il"]]; Object.entries(TEMA).forEach(([k, t]) => renk.push(k, t.renk)); renk.push("#555");
    GENEL.addLayer({ id: "calisma", type: "fill", source: "iller", filter: ["==", ["get", "calisma"], 1],
      paint: { "fill-color": renk, "fill-opacity": ["case", ["boolean", ["feature-state", "secili"], false], 0.95, 0.6] } });
    GENEL.addLayer({ id: "calisma-cizgi", type: "line", source: "iller", filter: ["==", ["get", "calisma"], 1], paint: { "line-color": "#fff", "line-width": 1.2 } });
    GENEL.on("click", "calisma", e => { ilSec(e.features[0].properties.il, true); });
    GENEL.on("mouseenter", "calisma", () => GENEL.getCanvas().style.cursor = "pointer");
    GENEL.on("mouseleave", "calisma", () => GENEL.getCanvas().style.cursor = "");
    GENEL.on("mousemove", "calisma", e => ipucu(e.originalEvent, `<b>${OZET.iller[e.features[0].properties.il].ad}</b><br>${TEMA[e.features[0].properties.il].tema}`));
    GENEL.on("mouseleave", "calisma", () => ipucu(null));
  });
}

function ilSecici() {
  $("#il-secici").innerHTML = Object.keys(TEMA).map(k =>
    `<button role="tab" data-il="${k}" style="--il-renk:${TEMA[k].renk}">${OZET.iller[k].ad}${OZET.iller[k].ana ? '<span class="yildiz">★</span>' : ""}</button>`).join("");
  $("#il-secici").addEventListener("click", e => { const b = e.target.closest("button"); if (b) ilSec(b.dataset.il, false); });
}

// ---------------------------------------------------------------- il haritası
function ilHaritasi() {
  return new Promise(res => {
    HARITA = new maplibregl.Map({ container: "harita", style: stil("sade"), bounds: OZET.iller.Istanbul.bbox, attributionControl: { compact: true }, dragRotate: false });
    HARITA.addControl(new maplibregl.NavigationControl({ showCompass: false }), "bottom-right");
    HARITA.addControl(new maplibregl.ScaleControl({ unit: "metric" }), "bottom-left");
    HARITA.once("style.load", () => { katmanlariEkle(); res(); });   // altlık karolarını beklemez
    document.querySelectorAll(".altlik button").forEach(b => b.addEventListener("click", () => {
      document.querySelectorAll(".altlik button").forEach(x => x.classList.toggle("secili", x === b));
      HARITA.getSource("altlik").setTiles(ALTLIK[b.dataset.altlik].tiles);
    }));
    $("#saydamlik").addEventListener("input", e => HARITA.setPaintProperty("hucre", "fill-opacity", +e.target.value));
  });
}

function katmanlariEkle() {
  HARITA.addSource("hucre", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
  HARITA.addLayer({ id: "hucre", type: "fill", source: "hucre", paint: { "fill-color": SEFFAF, "fill-opacity": 0.85, "fill-antialias": false } });
  HARITA.addSource("sinir", { type: "geojson", data: ILLER_GEO });
  HARITA.addLayer({ id: "sinir-dis", type: "line", source: "sinir", filter: ["==", ["get", "il"], ""],
    paint: { "line-color": "#ffffff", "line-width": 4, "line-opacity": 0.8 } });
  HARITA.addLayer({ id: "sinir", type: "line", source: "sinir", filter: ["==", ["get", "il"], ""],
    paint: { "line-color": "#1c2421", "line-width": 1.6 } });
  HARITA.on("mousemove", "hucre", e => {
    const p = e.features[0].properties, k = KATMAN[seciliKatman];
    const deger = p[k.alan], kat = k.tur === "kat" ? (k.kat.find(x => x[0] === deger) || [])[1] : null;
    ipucu(e.originalEvent, `<b>${k.ad}</b>: ${kat ?? (deger == null || deger === "null" ? "veri yok" : sayi(+deger, k.alan === "dm" ? 3 : k.alan === "dn" ? 2 : Number.isInteger(+deger) ? 0 : 1) + (k.birim || ""))}
      <div class="s"><span>2024 sınıfı</span><span>${p.b24 >= 0 ? SINIF[p.b24][0] : "—"}</span></div>
      <div class="s"><span>Yüzey sıcaklığı 2024</span><span>${p.lst24 == null || p.lst24 === "null" ? "—" : sayi(+p.lst24, 1) + " °C"}</span></div>
      <div class="s"><span>Tarım / orman / yapı</span><span>%${p.tp ?? "—"} / %${p.op ?? "—"} / %${p.yp ?? "—"}</span></div>
      <div class="s"><span>Rakım</span><span>${p.elev ?? "—"} m</span></div>`);
  });
  HARITA.on("mouseleave", "hucre", () => ipucu(null));
}

async function hucreleriYukle(kod) {
  if (HUCRE[kod]) return HUCRE[kod];
  $("#yukleniyor").hidden = false;
  const d = await fetch(`data/hucre/${kod}.json`).then(r => r.json());
  const alanlar = Object.keys(d).filter(k => !["x0", "y0", "i", "j"].includes(k));
  const kose = [[-500, -500], [500, -500], [500, 500], [-500, 500], [-500, -500]];
  const features = d.i.map((i, n) => {
    const cx = (d.x0 + i + 0.5) * 1000, cy = (d.y0 + d.j[n] + 0.5) * 1000;     // hücre merkezi, EPSG:3035
    const ring = kose.map(([dx, dy]) => LAEA.forward([cx + dx, cy + dy]).map(v => +v.toFixed(5)));
    const properties = {}; alanlar.forEach(a => properties[a] = d[a][n]);
    return { type: "Feature", properties, geometry: { type: "Polygon", coordinates: [ring] } };
  });
  $("#yukleniyor").hidden = true;
  return HUCRE[kod] = { type: "FeatureCollection", features };
}

function renkIfadesi(k) {
  if (k.tur === "kat") {
    const e = ["match", ["get", k.alan]]; k.kat.forEach(([v, , r]) => e.push(v, r)); e.push(SEFFAF); return e;
  }
  const sinir = k.dinamik ? lstSinirlari() : k.sinir;
  const e = ["step", ["get", k.alan], k.renk[0]]; sinir.forEach((s, i) => e.push(s, k.renk[i + 1]));
  return ["case", ["==", ["typeof", ["get", k.alan]], "number"], e, SEFFAF];
}
const lstSinirlari = () => { const q = OZET.iller[seciliIl].lst24_q; return [q[0], q[1], q[2], q[3], q[4]]; };

function katmanSec(ad) {
  seciliKatman = ad;
  const k = KATMAN[ad];
  HARITA.setPaintProperty("hucre", "fill-color", renkIfadesi(k));
  document.querySelectorAll(".katman-secici button").forEach(b => b.classList.toggle("secili", b.dataset.k === ad));
  let satirlar;
  if (k.tur === "kat") satirlar = k.kat.filter(x => x[2] !== SEFFAF).map(([, a, r]) => [r, a]);
  else {
    const s = k.dinamik ? lstSinirlari() : k.sinir, n = s.length, b = k.birim || "", f = v => sayi(v, Math.abs(v) < 1 && v !== 0 ? 2 : Number.isInteger(v) ? 0 : 1);
    satirlar = k.renk.map((r, i) => [r, i === 0 ? `< ${f(s[0])}${b}` : i === n ? `≥ ${f(s[n - 1])}${b}` : `${f(s[i - 1])} … ${f(s[i])}${b}`]);
  }
  $("#lejant").innerHTML = `<h4>${k.ad}</h4>` + satirlar.map(([r, a]) => `<div class="satir"><i style="background:${r}"></i>${a}</div>`).join("") + `<p>${k.not}</p>`;
}

async function ilSec(kod, kaydir) {
  seciliIl = kod;
  const t = TEMA[kod], o = OZET.iller[kod];
  document.documentElement.style.setProperty("--il-renk", t.renk);
  history.replaceState(null, "", "#" + kod);
  document.querySelectorAll("#il-secici button").forEach(b => b.classList.toggle("secili", b.dataset.il === kod));
  $("#il-etiket").textContent = `${o.ad}${o.ana ? " · ana odak ili" : " · karşılaştırma ili"} · ${sayi(o.hucre, 0)} hücre (1 km²)`;
  $("#il-tema").textContent = t.tema;
  $("#il-soru").textContent = t.soru;
  $("#kartlar").innerHTML = t.kartlar(o).map(([a, b, n]) => `<div class="kart"><span class="ad">${a}</span><b>${b}</b><span class="not">${n}</span></div>`).join("");
  $("#hikaye").innerHTML = `<h3>Ne görüyoruz?</h3>${t.hikaye(o)}${t.uyari ? `<p class="uyari">⚠ ${t.uyari}</p>` : ""}`;
  $("#katman-secici").innerHTML = t.katman.map((k, i) => `<button data-k="${k}" class="${i < 2 ? "tema" : ""}">${KATMAN[k].ad}</button>`).join("");
  document.querySelectorAll(".katman-secici button").forEach(b => b.addEventListener("click", () => katmanSec(b.dataset.k)));
  if (GENEL && GENEL.getSource("iller")) {
    ILLER_GEO.features.forEach((f, i) => f.properties.calisma && GENEL.setFeatureState({ source: "iller", id: i }, { secili: f.properties.il === kod }));
  }
  if (kaydir) document.getElementById("iller").scrollIntoView({ behavior: "smooth" });
  iklimCiz(); sinifCiz();
  const [veri] = await Promise.all([hucreleriYukle(kod), haritaHazir]);
  if (seciliIl !== kod) return;          // yükleme sırasında başka il seçildiyse
  ["sinir", "sinir-dis"].forEach(l => HARITA.setFilter(l, ["==", ["get", "il"], kod]));
  HARITA.fitBounds(o.bbox, { padding: 30, duration: 800 });
  HARITA.getSource("hucre").setData(veri);
  katmanSec(t.katman[0]);
}

// ---------------------------------------------------------------- grafikler
Chart.defaults.font.family = "Inter, system-ui, sans-serif";
Chart.defaults.font.size = 11;
Chart.defaults.color = "#5d6b66";

const IKLIM_ADI = { modis_lst_day: ["Yaz yüzey sıcaklığı", "°C", 2], era5_sm_summer: ["Yaz toprak nemi", "m³/m³", 3], chirps_precip_annual: ["Yıllık yağış", "mm", 0] };
$("#iklim-secim").addEventListener("change", iklimCiz);
function iklimCiz() {
  const v = $("#iklim-secim").value, [ad, birim, n] = IKLIM_ADI[v];
  const ds = Object.keys(TEMA).map(k => ({ label: OZET.iller[k].ad, data: OZET.iller[k].iklim[v], borderColor: k === seciliIl ? TEMA[k].renk : "rgba(120,130,125,0.22)",
    borderWidth: k === seciliIl ? 3 : 1.2, pointRadius: k === seciliIl ? 2 : 0, tension: 0.3, order: k === seciliIl ? 0 : 1 }));
  const veri = { labels: OZET.yillar, datasets: ds };
  if (iklimGrafik) { iklimGrafik.data = veri; iklimGrafik.options.scales.y.title.text = birim; iklimGrafik.update(); }
  else iklimGrafik = new Chart($("#iklim-grafik"), { type: "line", data: veri,
    options: { plugins: { legend: { display: false }, tooltip: { filter: i => i.dataset.label === OZET.iller[seciliIl].ad } },
      scales: { y: { title: { display: true, text: birim } }, x: { ticks: { maxTicksLimit: 8 } } }, interaction: { mode: "index", intersect: false } } });
  const tr = OZET.iller[seciliIl].trend[v];
  $("#trend-not").innerHTML = `${OZET.iller[seciliIl].ad}: Sen eğimi 10 yılda <b>${isaretli(tr.sen10, n)} ${birim}</b>, Mann-Kendall p = ${sayi(tr.p, 4)}
    ${tr.p < 0.05 ? "→ <b>anlamlı trend</b>" : "→ anlamlı trend yok"}.`;
}
function sinifCiz() {
  const o = OZET.iller[seciliIl];
  const veri = { labels: SINIF.map(s => s[0]), datasets: [
    { label: "2014", data: SINIF_KOD.map(k => o.sinif[k].y0), backgroundColor: SINIF.map(s => s[1] + "66") },
    { label: "2024", data: SINIF_KOD.map(k => o.sinif[k].y1), backgroundColor: SINIF.map(s => s[1]) }] };
  if (sinifGrafik) { sinifGrafik.data = veri; sinifGrafik.update(); }
  else sinifGrafik = new Chart($("#sinif-grafik"), { type: "bar", data: veri,
    options: { plugins: { legend: { position: "bottom" }, tooltip: { callbacks: { label: c => `${c.dataset.label}: %${sayi(c.raw, 1)}` } } },
      scales: { y: { title: { display: true, text: "il alanının %" } } } } });
}

function hipotezler() {
  const I = Object.keys(TEMA), il = k => OZET.iller[k];
  const renk = r => { const a = Math.min(Math.abs(r) / 0.6, 1); return r < 0 ? `rgba(103,169,207,${0.25 + 0.75 * a})` : `rgba(239,138,98,${0.25 + 0.75 * a})`; };
  const serit = f => `<div class="seridi">${I.map(k => `<span style="background:${renk(f(k))}">${isaretli(f(k))}</span>`).join("")}</div>
    <div class="seridi-ad">${I.map(k => `<span>${il(k).ad.slice(0, 4)}</span>`).join("")}</div>`;
  const loco = OZET.loco.XGBoost;
  const H = [
    ["H1", "Yapılaşma artışı ↔ yüzey sıcaklığı artışı", "kismen", "Kısmen",
      `Isı adası belirgin (İstanbul ${isaretli(il("Istanbul").uhi["2024"], 1)} °C, İzmir ${isaretli(il("Izmir").uhi["2024"], 1)} °C), ama hücre düzeyinde Δyapılaşma–ΔLST çok zayıf.`, serit(k => il(k).rho.yapi)],
    ["H2", "Bitki örtüsü azalması ↔ yüzey sıcaklığı artışı", "evet", "Destekleniyor",
      `ΔNDVI–ΔLST ${OZET.ndvi_negatif_il}/7 ilde negatif, orta–güçlü. Projenin en sağlam bulgusu.`, serit(k => il(k).rho.ndvi)],
    ["H3", "Tarım değişimi ↔ bitki örtüsü ve nem", "kismen", "Kısmen",
      `Δtarım–ΔNDMI kurak iç illerde belirgin (Konya ${isaretli(il("Konya").rho.tarim_ndmi)}), diğerlerinde zayıf.`, serit(k => il(k).rho.tarim_ndmi)],
    ["H4", "Su / sulak alan değişimi ↔ sıcaklık ve nem", "hayir", "Büyük ölçüde desteklenmiyor",
      "Δsu–ΔLST yalnızca birkaç ilde zayıf; 1 km hücrelerde su değişimi küçük.", serit(k => il(k).rho.su)],
    ["H5", "İlişkiler bölgeye göre farklılaşır", "kismen", "Kısmen",
      "Aynı ilişkinin gücü ilden ile değişiyor (ör. ΔNDVI–ΔLST); yönü değişmiyor.", serit(k => il(k).rho.ndvi)],
    ["H6", "Model başarısı bölgeye göre değişir", "evet", "Destekleniyor",
      `Model hiç görmediği ilde ortalama ${sayi(OZET.loco_ort_dusus, 3)} macro-F1 kaybediyor; kurak illerde daha çok.`,
      serit(k => -(loco[k].ayni - loco[k].baska))],
  ];
  $("#hipotezler-izgara").innerHTML = H.map(([k, i, c, e, kn, s]) =>
    `<div class="hipotez"><span class="kod">${k}</span><p class="ifade">${i}</p><span class="karar ${c}">öneri: ${e}</span><p class="kanit">${kn}</p>${s}</div>`).join("");
}

function modelGrafikleri() {
  const M = ["RandomForest", "XGBoost", "SVM", "MLP"], ad = { RandomForest: "Random Forest", XGBoost: "XGBoost ✓", SVM: "SVM", MLP: "MLP" };
  const renk = ["#1b7837", "#74c476", "#4575b4", "#bababa"];
  new Chart($("#model-grafik"), { type: "bar", data: { labels: M.map(m => ad[m]),
    datasets: [["Accuracy", "acc"], ["macro-F1", "f1"], ["Kappa", "kappa"], ["IoU", "iou"]].map(([l, k], i) =>
      ({ label: l, data: M.map(m => OZET.modeller[m][k]), backgroundColor: renk[i] })) },
    options: { scales: { y: { min: 0.5, max: 1 } }, plugins: { legend: { position: "bottom" },
      tooltip: { callbacks: { label: c => `${c.dataset.label}: ${sayi(c.raw, 3)}` } } } } });
  const L = OZET.loco.XGBoost, I = Object.keys(TEMA);
  new Chart($("#loco-grafik"), { type: "bar", data: { labels: I.map(k => OZET.iller[k].ad), datasets: [
    { label: "Aynı il (eğitimde görüldü)", data: I.map(k => L[k].ayni), backgroundColor: "#4575b4" },
    { label: "Başka il (hiç görülmedi)", data: I.map(k => L[k].baska), backgroundColor: "#d73027" }] },
    options: { scales: { y: { min: 0.4, max: 0.9 } }, plugins: { legend: { position: "bottom" } } } });
  $("#loco-not").textContent = `XGBoost · ortalama kayıp ${sayi(OZET.loco_ort_dusus, 3)}. En büyük kayıp kurak ve sıcak illerde; yağışla ilişkisi ρ ≈ −0,96 (n = 7, yalnızca örüntü).`;
  const R = OZET.lst_regresyon, rad = { RandomForestRegressor: "Random Forest", XGBRegressor: "XGBoost", LinearRegression: "Doğrusal" };
  $("#regresyon-kartlar").innerHTML = Object.entries(R).map(([k, v]) =>
    `<div class="kart"><span class="ad">${rad[k] || k}</span><b>R² ${sayi(v.r2, 3)}</b><span class="not">RMSE ${sayi(v.rmse, 2)} °C · ${v.kaynak}</span></div>`).join("");
  const S = Object.entries(OZET.shap).sort((a, b) => b[1].deger - a[1].deger);
  const shapAdi = s => s.replace("Su_Sulak", "Su/Sulak alan").replace("Tarim", "Tarım").replace("Yapilasma", "Yapılaşma")
    .replace("Cayir_Cali", "Çayır/Çalı").replace("Ciplak", "Çıplak").replace(" oranı", " payı");
  new Chart($("#shap-grafik"), { type: "bar", data: { labels: S.map(s => shapAdi(s[0])), datasets: [{ data: S.map(s => s[1].deger),
    backgroundColor: S.map(s => s[1].yon > 0 ? "#d73027" : "#4575b4") }] },
    options: { indexAxis: "y", plugins: { legend: { display: false }, tooltip: { callbacks: { label: c => `${sayi(c.raw, 2)} °C` } } },
      scales: { x: { title: { display: true, text: "ortalama |SHAP| (°C)" } } } } });
  const B = OZET.blok;
  new Chart($("#blok-grafik"), { type: "bar", data: { labels: M.map(m => ad[m]), datasets: [
    { label: "Rastgele bölme", data: M.map(m => B[m]["Rastgele"]), backgroundColor: "#9ecae1" },
    { label: "10 km mekânsal blok", data: M.map(m => B[m]["Mekânsal blok (10 km)"]), backgroundColor: "#08519c" }] },
    options: { scales: { y: { min: 0.7, max: 0.82 } }, plugins: { legend: { position: "bottom" } } } });
}

// ---------------------------------------------------------------- ipucu kutusu
function ipucu(olay, html) {
  const k = $("#ipucu-kutu");
  if (!olay) { k.hidden = true; return; }
  k.innerHTML = html; k.hidden = false;
  const x = Math.min(olay.clientX + 16, innerWidth - k.offsetWidth - 8), y = Math.min(olay.clientY + 16, innerHeight - k.offsetHeight - 8);
  k.style.left = x + "px"; k.style.top = y + "px";
}
