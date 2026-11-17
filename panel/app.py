"""GeoClimate AI — sonuç paneli (Streamlit).

Çalıştırma (proje kökünden):
    pip install -r panel/requirements.txt
    streamlit run panel/app.py

Veri panel/veri/ altındadır (panel/veri_hazirla.py ile Drive'dan hazırlanır).
Başka bir klasörü göstermek için: GEOCLIMATE_PANEL_VERI=<klasör> streamlit run panel/app.py
Panel hiçbir şey hesaplamaz ve Earth Engine'e bağlanmaz; notebook'ların ürettiği sonuçları gösterir.
"""
import os
import sys
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

PANEL = Path(__file__).resolve().parent
sys.path.insert(0, str(PANEL.parent))
import config  # noqa: E402

VERI = Path(os.environ.get("GEOCLIMATE_PANEL_VERI", PANEL / "veri"))

IL_ADI = {"Istanbul": "İstanbul", "Izmir": "İzmir", "Artvin": "Artvin", "Samsun": "Samsun",
          "Konya": "Konya", "Van": "Van", "Sanliurfa": "Şanlıurfa"}
ANA_ODAK = {"Istanbul", "Artvin", "Konya", "Van"}          # GeoClimate dokümanındaki 4 il
IL_KONUSU = {
    "Istanbul": "Kentleşme ve kentsel ısı adası", "Izmir": "Kıyı kentleşmesi ve ısı adası",
    "Artvin": "Orman örtüsü ve yüzey sıcaklığı", "Samsun": "Delta ve sulak alanlar",
    "Konya": "Tarım, kuraklık ve toprak nemi", "Van": "Göl havzası ve su yüzeyi",
    "Sanliurfa": "Sulu tarım (GAP) ve kuraklık",
}
SINIF_ADI = {"Orman": "Orman", "Tarim": "Tarım", "Yapilasma": "Yapılaşma", "Cayir_Cali": "Çayır/Çalı",
             "Ciplak": "Çıplak", "Su_Sulak": "Su/Sulak"}
SINIF_SIRA = [SINIF_ADI[config.CLASSES[k]] for k in sorted(config.CLASSES)]
SINIF_RENK = [config.CLASS_COLORS[k] for k in sorted(config.CLASSES)]
IKLIM_DEGISKEN = {
    "modis_lst_day": "MODIS yaz gündüz yüzey sıcaklığı (°C)",
    "modis_lst_night": "MODIS yaz gece yüzey sıcaklığı (°C)",
    "era5_t2m_summer": "ERA5 yaz hava sıcaklığı, 2 m (°C)",
    "era5_sm_summer": "ERA5 yaz toprak nemi (m³/m³)",
    "era5_sm_annual": "ERA5 yıllık toprak nemi (m³/m³)",
    "chirps_precip_annual": "CHIRPS yıllık yağış (mm)",
}
MODEL_ADI = {"RandomForest": "Random Forest", "XGBoost": "XGBoost", "SVM": "SVM", "MLP": "MLP"}

st.set_page_config(page_title="GeoClimate AI", page_icon="🌍", layout="wide")


# ---------------------------------------------------------------- veri
@st.cache_data
def tablo(ad, index_col=None):
    yol = VERI / "tables" / f"{ad}.csv"
    if not yol.exists():
        return None
    return pd.read_csv(yol, encoding="utf-8-sig", index_col=index_col)


def tablo_yok(ad):
    st.info(f"`{ad}.csv` panel verisinde yok. `python panel/veri_hazirla.py <Drive klasörü>` ile hazırlayın.")


def gorsel(alt_klasor, ad, aciklama):
    for uzanti in (".png", ".jpg"):
        yol = VERI / alt_klasor / f"{ad}{uzanti}"
        if yol.exists():
            st.image(str(yol), caption=aciklama, width="stretch")
            return
    st.caption(f"({aciklama}: görsel yok)")


def il(c):
    return IL_ADI.get(c, c)


if not (VERI / "tables").exists():
    st.error(f"Panel verisi bulunamadı: `{VERI}`. Önce `python panel/veri_hazirla.py <Drive klasörü>` çalıştırın.")
    st.stop()

# ---------------------------------------------------------------- kenar çubuğu
with st.sidebar:
    st.title("🌍 GeoClimate AI")
    st.caption("Türkiye'de arazi örtüsü değişimi ve yerel iklim göstergeleri")
    il_secenek = {il(c) + (" ★" if c in ANA_ODAK else ""): c for c in config.CITIES}
    secili = il_secenek[st.selectbox("İl", list(il_secenek))]
    st.markdown(f"**Konu:** {IL_KONUSU[secili]}")
    st.caption("★ GeoClimate dokümanındaki ana odak illeri")
    st.divider()
    st.caption("Veri: Landsat 8/9, ESA WorldCover 2021, MODIS, ERA5-Land, CHIRPS · "
               f"Değişim: {config.CHANGE_YEARS[0]} → {config.CHANGE_YEARS[1]} yaz kompozitleri")
    st.caption("⚠️ Bulgular **ilişki** gösterir, neden-sonuç değil.")

Y0, Y1 = config.CHANGE_YEARS
sekmeler = st.tabs(["Genel bakış", "Arazi değişimi", "İklim", "İlişkiler ve hipotezler", "Model başarısı"])

# ================================================================ 1. Genel bakış
with sekmeler[0]:
    st.header("Genel bakış")
    st.write("7 ilde uydu görüntülerinden arazi örtüsü yapay zekâyla sınıflandırıldı, "
             f"{Y0} ile {Y1} arasındaki değişim ölçüldü ve yüzey sıcaklığı, nem ve yağış göstergeleriyle ilişkisi incelendi.")
    mk, lst_m, gen_d, hk = (tablo("model_karsilastirma", 0), tablo("lst_regresyon_metrikleri"),
                            tablo("genelleme_dusus"), tablo("hipotez_kanit_H1_H5"))
    k = st.columns(4)
    if mk is not None:
        k[0].metric("Sınıflandırma (XGBoost, macro-F1)", f"{mk.loc['XGBoost', 'f1_macro']:.3f}",
                    help="Test kümesi, Faz 3 (Colab). 6 sınıf.")
    if lst_m is not None:
        k[1].metric("Yüzey sıcaklığı regresyonu (R²)", f"{lst_m['R2_ort'].iloc[0]:.3f}",
                    help="Random Forest, 10 km mekânsal blok çapraz doğrulama, 111 950 hücre.")
    if gen_d is not None:
        d = gen_d[gen_d["model"] == "XGBoost"]["dusus_f1_macro"]
        k[2].metric("Başka ile taşınınca F1 kaybı", f"−{d.mean():.3f}",
                    help="Leave-One-City-Out: model hiç görmediği ilde test edildi (7 il ortalaması).")
    if hk is not None:
        n = hk[(hk["iliski"].str.startswith("ΔNDVI")) & (hk["rho"] < 0)]["city"].nunique()
        k[3].metric("Bitki ↓ ↔ sıcaklık ↑ (ΔNDVI–ΔLST)", f"{n}/7 il",
                    help="7 ilin kaçında ilişki negatif (H2). En güçlü bulgu.")
    sol, sag = st.columns([3, 2])
    with sol:
        if (VERI / "sehir_sinirlari.png").exists():
            st.image(str(VERI / "sehir_sinirlari.png"), caption="Çalışma alanları (il sınırları, FAO GAUL)",
                     width="stretch")
    with sag:
        st.subheader("İller ve araştırma konuları")
        st.dataframe(pd.DataFrame({"İl": [il(c) + (" ★" if c in ANA_ODAK else "") for c in config.CITIES],
                                   "Konu": [IL_KONUSU[c] for c in config.CITIES]}),
                     hide_index=True, width="stretch")

# ================================================================ 2. Arazi değişimi
with sekmeler[1]:
    st.header(f"Arazi değişimi — {il(secili)}")
    g = st.columns(3)
    with g[0]:
        gorsel("lc_maps", f"{secili}_{Y0}", f"{Y0} arazi örtüsü")
    with g[1]:
        gorsel("lc_maps", f"{secili}_{Y1}", f"{Y1} arazi örtüsü")
    with g[2]:
        gorsel("lc_maps", f"{secili}_degisim", "Değişen alanlar (2024'teki yeni sınıfın rengiyle)")
    st.caption("Harita görselleri yalnızca görsel amaçlıdır; sayılar 1 km hücrelerdeki 9'ar noktadan hesaplanmıştır.")
    with st.expander("Gerçek renkli uydu görüntüleri (Landsat)"):
        r = st.columns(2)
        with r[0]:
            gorsel("rgb", f"{secili}_{Y0}", f"{Y0} yaz")
        with r[1]:
            gorsel("rgb", f"{secili}_{Y1}", f"{Y1} yaz")

    alan = tablo("sinif_alanlari_degisim")
    if alan is None:
        tablo_yok("sinif_alanlari_degisim")
    else:
        a = alan[alan["city"] == secili].copy()
        a["Sınıf"] = a["sinif"].map(SINIF_ADI)
        st.subheader("Sınıf payları")
        mcol = st.columns(len(a))
        for c, (_, row) in zip(mcol, a.set_index("Sınıf").loc[SINIF_SIRA].iterrows()):
            c.metric(row.name, f"%{row[f'pay_{Y1}_yuzde']:.1f}", f"{row['degisim_pp']:+.2f} puan")
        uzun = a.melt(id_vars="Sınıf", value_vars=[f"pay_{Y0}_yuzde", f"pay_{Y1}_yuzde"],
                      var_name="Yıl", value_name="Pay (%)")
        uzun["Yıl"] = uzun["Yıl"].str.extract(r"(\d{4})")[0]
        st.altair_chart(
            alt.Chart(uzun).mark_bar().encode(
                x=alt.X("Sınıf:N", sort=SINIF_SIRA, title=None),
                xOffset="Yıl:N",
                y=alt.Y("Pay (%):Q"),
                color=alt.Color("Yıl:N", scale=alt.Scale(range=["#9ecae1", "#08519c"])),
                tooltip=["Sınıf", "Yıl", alt.Tooltip("Pay (%):Q", format=".2f")],
            ).properties(height=320), width="stretch")

    gm = tablo("gecis_matrisi")
    if gm is not None:
        st.subheader(f"Geçiş matrisi ({Y0} → {Y1})")
        st.caption("Satır: 2014 sınıfı. Hücre: o sınıftaki noktaların yüzde kaçı 2024'te sütundaki sınıfta. Köşegen = değişmedi.")
        m = gm[gm["city"] == secili].copy()
        m["2014"] = m["sinif_2014"].map(SINIF_ADI)
        m["2024"] = m["sinif_2024"].map(SINIF_ADI)
        taban = alt.Chart(m).encode(x=alt.X("2024:N", sort=SINIF_SIRA), y=alt.Y("2014:N", sort=SINIF_SIRA))
        st.altair_chart(
            (taban.mark_rect().encode(color=alt.Color("satir_yuzde:Q", title="%", scale=alt.Scale(scheme="greens")),
                                      tooltip=["2014", "2024", alt.Tooltip("satir_yuzde:Q", format=".1f"),
                                               alt.Tooltip("tahmini_km2:Q", format=",.0f", title="tahmini km²")])
             + taban.mark_text(fontSize=11).encode(text=alt.Text("satir_yuzde:Q", format=".0f"),
                                                   color=alt.condition("datum.satir_yuzde > 50", alt.value("white"),
                                                                       alt.value("black"))))
            .properties(height=320), width="stretch")

# ================================================================ 3. İklim
with sekmeler[2]:
    st.header("İklim göstergeleri (2003–2024)")
    ik = tablo("iklim_sehir_yillik")
    if ik is None:
        tablo_yok("iklim_sehir_yillik")
    else:
        gosterge = {v: k for k, v in IKLIM_DEGISKEN.items()}
        deg = gosterge[st.selectbox("Gösterge", list(gosterge))]
        d = ik[["city", "year", deg]].rename(columns={deg: "değer"})
        d["İl"] = d["city"].map(il)
        d["seçili"] = d["city"] == secili
        st.altair_chart(
            alt.Chart(d).mark_line(point=True).encode(
                x=alt.X("year:O", title=None),
                y=alt.Y("değer:Q", title=IKLIM_DEGISKEN[deg], scale=alt.Scale(zero=False)),
                color=alt.Color("İl:N"),
                opacity=alt.condition("datum['seçili']", alt.value(1.0), alt.value(0.25)),
                strokeWidth=alt.condition("datum['seçili']", alt.value(3), alt.value(1.2)),
                tooltip=["İl", "year", alt.Tooltip("değer:Q", format=".3f")],
            ).properties(height=380), width="stretch")
        st.caption(f"Kalın çizgi: {il(secili)}. Yüzey sıcaklığı (LST) ile hava sıcaklığı aynı şey değildir.")

    tr = tablo("iklim_trend_mann_kendall")
    if tr is not None:
        st.subheader(f"Trend testi — {il(secili)}")
        t = tr[tr["city"] == secili].copy()
        t["Gösterge"] = t["degisken"].map(IKLIM_DEGISKEN).fillna(t["degisken"])
        t["10 yılda değişim (Sen eğimi)"] = t["sen_egimi_10yil"]
        t["Anlamlı mı? (p < 0.05)"] = t["p"].lt(0.05).map({True: "✅ evet", False: "—"})
        st.dataframe(t[["Gösterge", "10 yılda değişim (Sen eğimi)", "p", "Anlamlı mı? (p < 0.05)"]],
                     hide_index=True, width="stretch",
                     column_config={"p": st.column_config.NumberColumn(format="%.4f"),
                                    "10 yılda değişim (Sen eğimi)": st.column_config.NumberColumn(format="%+.3f")})
        st.caption("Mann-Kendall: düzenli bir artış/azalış var mı? Sen eğimi: eğilimin büyüklüğü.")

# ================================================================ 4. İlişkiler ve hipotezler
with sekmeler[3]:
    st.header("Değişim–iklim ilişkileri ve hipotezler")
    hk = tablo("hipotez_kanit_H1_H5")
    if hk is None:
        tablo_yok("hipotez_kanit_H1_H5")
    else:
        h = hk.copy()
        h["İl"] = h["city"].map(il)
        h["İlişki"] = h["hipotez"] + ": " + h["iliski"]
        st.subheader("H1–H5 kanıtı: 7 ilde Spearman korelasyonu (ρ)")
        taban = alt.Chart(h).encode(x=alt.X("İl:N", sort=[il(c) for c in config.CITIES], title=None),
                                    y=alt.Y("İlişki:N", title=None))
        st.altair_chart(
            (taban.mark_rect().encode(color=alt.Color("rho:Q", title="ρ",
                                                      scale=alt.Scale(scheme="redblue", domain=[-0.6, 0.6], reverse=True)),
                                      tooltip=["İlişki", "İl", alt.Tooltip("rho:Q", format="+.3f"), "guc", "n_hucre"])
             + taban.mark_text(fontSize=11).encode(text=alt.Text("rho:Q", format="+.2f")))
            .properties(height=320), width="stretch")
        st.caption("|ρ| < 0.1 ihmal edilebilir · 0.1–0.3 zayıf · 0.3–0.5 orta · ≥ 0.5 güçlü. "
                   "Hücre sayısı çok büyük olduğu için p-değerleri neredeyse hep < 0.001; ρ'nun büyüklüğüne bakın.")

    ho = tablo("hipotez_ozet")
    if ho is not None:
        st.subheader("Hipotez özeti (H1–H6)")
        for kod, (ifade, _) in config.HYPOTHESES.items():
            with st.expander(f"**{kod}** — {ifade}"):
                q = ho[ho["hipotez"] == kod]
                st.dataframe(q[["kanit", "beklenen_yon", "rho_min", "rho_max", "en_guclu_il"]].rename(columns={
                    "kanit": "Kanıt", "beklenen_yon": "Beklenen yön", "rho_min": "en küçük", "rho_max": "en büyük",
                    "en_guclu_il": "Not"}), hide_index=True, width="stretch")
        st.caption("\"Desteklendi / kısmen / desteklenmedi\" kararı rapordadır; tablo yalnızca sayıları toplar.")

    uhi = tablo("kentsel_isi_adasi")
    if uhi is not None and secili in set(uhi["city"]):
        st.subheader(f"Kentsel ısı adası — {il(secili)}")
        u = uhi[uhi["city"] == secili]
        c = st.columns(len(u))
        for col, (_, row) in zip(c, u.iterrows()):
            col.metric(f"{row['kaynak']} {row['year']}", f"{row['UHI_C']:+.2f} °C",
                       help=f"kentsel {row['kentsel_LST']:.1f} °C − kırsal {row['kirsal_LST']:.1f} °C")
    su = tablo("su_alani_karsilastirma")
    if su is not None and secili in set(su["city"]):
        r = su.set_index("city").loc[secili]
        st.subheader(f"Açık su alanı — {il(secili)}")
        c = st.columns(3)
        c[0].metric(f"{Y0} (MNDWI)", f"{r[f'mndwi_{Y0}_km2']:.1f} km²")
        c[1].metric(f"{Y1} (MNDWI)", f"{r[f'mndwi_{Y1}_km2']:.1f} km²", f"%{r['mndwi_degisim_yuzde_2014_2024']:+.1f}")
        c[2].metric("JRC ile uyum (IoU, 2021)", f"{r['iou_2021']:.2f}")

# ================================================================ 5. Model başarısı
with sekmeler[4]:
    st.header("Yapay zekâ modellerinin başarısı")
    mk = tablo("model_karsilastirma", 0)
    iou = tablo("sinif_bazinda_iou", 0)
    if mk is not None:
        st.subheader("Sınıflandırma (test kümesi, 1 988 nokta)")
        g = mk[["accuracy", "precision_macro", "recall_macro", "f1_macro", "roc_auc_ovr_macro", "kappa"]].copy()
        if iou is not None and "Ortalama (macro)" in iou.index:
            g["iou_macro"] = iou.loc["Ortalama (macro)"]
        g.index = g.index.map(MODEL_ADI)
        st.dataframe(g.rename(columns={"accuracy": "Accuracy", "precision_macro": "Precision", "recall_macro": "Recall",
                                       "f1_macro": "F1 (macro)", "roc_auc_ovr_macro": "ROC-AUC", "kappa": "Kappa",
                                       "iou_macro": "IoU"}).style.format("{:.3f}").highlight_max(axis=0, color="#c7e9c0"),
                     width="stretch")
        st.caption("Model seçimi doğrulama kümesine göre yapıldı → XGBoost. IoU, Drive'daki resmi model dosyalarından "
                   "yeniden eğitilmeden hesaplandı (tools/resmi_model_iou.py).")
    if iou is not None:
        st.subheader("Sınıf bazında IoU")
        i2 = iou.drop(index="Ortalama (macro)", errors="ignore").reset_index(names="Sınıf")
        i2["Sınıf"] = i2["Sınıf"].map(SINIF_ADI)
        uzun = i2.melt(id_vars="Sınıf", var_name="Model", value_name="IoU")
        st.altair_chart(
            alt.Chart(uzun).mark_bar().encode(
                x=alt.X("Sınıf:N", sort=SINIF_SIRA, title=None), xOffset="Model:N",
                y=alt.Y("IoU:Q", scale=alt.Scale(domain=[0, 1])), color="Model:N",
                tooltip=["Sınıf", "Model", alt.Tooltip("IoU:Q", format=".3f")]).properties(height=300),
            width="stretch")
        st.caption("En zor sınıf Tarım: hasat edilmiş tarla, kuru çayır ve çıplak toprakla karışıyor.")

    mb = tablo("mekansal_blok_ozet")
    if mb is not None:
        st.subheader("Rastgele bölme mi, mekânsal blok mu?")
        p = mb.pivot(index="model", columns="bolme", values="f1_macro_mean")
        p.index = p.index.map(MODEL_ADI)
        p["fark"] = p["Rastgele"] - p["Mekânsal blok (10 km)"]
        st.dataframe(p.style.format("{:.3f}"), width="stretch")
        st.caption("Komşu noktalar birbirine benzer; rastgele bölme başarıyı şişirebilir. "
                   "10 km blok doğrulamada fark en fazla ≈0.013 → mekânsal sızıntı küçük.")

    gen = tablo("genelleme")
    if gen is not None:
        st.subheader("Model başka bir ile taşınınca (Leave-One-City-Out)")
        model_secenek = {v: k for k, v in MODEL_ADI.items()}
        mod = model_secenek[st.radio("Model", list(model_secenek), horizontal=True, index=1)]
        q = gen[(gen["model"] == mod) & gen["duzen"].isin(["Aynı şehir", "Başka şehir (LOCO)"])].copy()
        q["İl"] = q["test_city"].map(il)
        st.altair_chart(
            alt.Chart(q).mark_bar().encode(
                x=alt.X("İl:N", sort=[il(c) for c in config.CITIES], title=None), xOffset="duzen:N",
                y=alt.Y("f1_macro:Q", title="macro-F1", scale=alt.Scale(domain=[0.4, 0.9])),
                color=alt.Color("duzen:N", title=None, scale=alt.Scale(range=["#4575b4", "#d73027"])),
                tooltip=["İl", "duzen", alt.Tooltip("f1_macro:Q", format=".3f")]).properties(height=320),
            width="stretch")
        st.caption("Kırmızı: model o ili hiç görmeden eğitildi. Düşüş kurak ve sıcak illerde (Konya, Şanlıurfa, Van) daha büyük.")

    # Resmi Colab değerleri esas; yerel tablodan yalnızca resmi tabloda olmayan model (XGBoost) eklenir
    lm = tablo("lst_regresyon_metrikleri")
    yerel = tablo("lst_regresyon_metrikleri_xgboost_eklendi")
    if lm is not None:
        lm = lm.assign(kaynak="Colab (resmi)")
        if yerel is not None:
            lm = pd.concat([lm, yerel[~yerel["model"].isin(lm["model"])].assign(kaynak="yerel çalıştırma")])
    shap = tablo("lst_regresyon_shap", 0)
    if lm is not None:
        st.subheader("Yüzey sıcaklığını (LST) tahmin etme")
        c = st.columns(len(lm))
        for col, (_, row) in zip(c, lm.iterrows()):
            col.metric(row["model"].replace("Regressor", "").replace("LinearRegression", "Doğrusal"),
                       f"R² {row['R2_ort']:.3f}", f"RMSE {row['RMSE_ort_C']:.2f} °C", delta_color="off",
                       help=f"Kaynak: {row['kaynak']}")
    if shap is not None:
        s = shap.reset_index(names="Değişken")
        s["Yön"] = s["yon_korelasyonu"].map(lambda v: "arttıkça LST artıyor" if v > 0 else "arttıkça LST azalıyor")
        st.altair_chart(
            alt.Chart(s).mark_bar().encode(
                y=alt.Y("Değişken:N", sort="-x", title=None),
                x=alt.X("ortalama_abs_shap_C:Q", title="ortalama |SHAP| (°C)"),
                color=alt.Color("Yön:N", scale=alt.Scale(domain=["arttıkça LST artıyor", "arttıkça LST azalıyor"],
                                                         range=["#d73027", "#4575b4"])),
                tooltip=["Değişken", alt.Tooltip("ortalama_abs_shap_C:Q", format=".2f"), "Yön"]).properties(height=320),
            width="stretch")
        st.caption("SHAP, modelin neye baktığını gösterir; neden-sonuç değildir.")
