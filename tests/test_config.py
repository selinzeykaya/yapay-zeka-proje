"""config.py'nin kendi içinde tutarlı olduğunu kontrol eder.
Bir ayar değiştirilirken başka bir yerle çelişki oluşursa (ör. alt soruya tanımsız bir il yazılırsa) CI kırmızı olur."""
import config


def test_alt_sorulardaki_iller_tanimli():
    for kod, iller in config.SUB_QUESTIONS.items():
        bilinmeyen = set(iller) - set(config.CITIES)
        assert not bilinmeyen, f"{kod} tanımsız il içeriyor: {bilinmeyen}"


def test_ida_kapsam_disi():
    assert "AS6" not in config.SUB_QUESTIONS
    assert not any(k.startswith(("IDA_", "YOLO_", "MENDELEY")) for k in dir(config))


def test_hipotezler_H1_H6_ve_alt_soru_baglantisi():
    assert sorted(config.HYPOTHESES) == [f"H{i}" for i in range(1, 7)]
    for h, (ifade, alt_soru) in config.HYPOTHESES.items():
        assert ifade.strip(), f"{h} ifadesi boş"
        if h in ("H1", "H2", "H3", "H4", "H6"):   # 04 B9 bu alt sorulardan il listesi okuyor
            assert alt_soru in config.SUB_QUESTIONS, f"{h} → {alt_soru} SUB_QUESTIONS'ta yok"


def test_worldcover_eslemesi_gecerli_siniflara_gidiyor():
    assert set(config.WORLDCOVER_TO_CLASS) == set(config.WORLDCOVER_NAMES)
    for kod, sinif in config.WORLDCOVER_TO_CLASS.items():
        assert sinif is None or sinif in config.CLASSES, f"WorldCover {kod} → geçersiz sınıf {sinif}"
    assert set(config.CLASS_COLORS) == set(config.CLASSES)


def test_ndmi_model_girdisinde_yok():
    # Landsat'ta NDMI = −NDBI; aynı bilgi iki kez verilmesin
    assert "NDMI" not in config.MODEL_FEATURES
    assert "NDBI" in config.MODEL_FEATURES
    assert set(config.MODEL_FEATURES) <= set(config.FEATURES)


def test_bolme_oranlari_toplami_1():
    assert abs(config.TRAIN_SIZE + config.VAL_SIZE + config.TEST_SIZE - 1) < 1e-9


def test_her_modelin_arama_araligi_var():
    assert set(config.MODELS) == set(config.PARAM_SPACES)


def test_degisim_yillari_ve_blok_boyu():
    y0, y1 = config.CHANGE_YEARS
    assert y0 < config.LABEL_YEAR < y1
    assert config.SPATIAL_BLOCK_M > config.GRID_SIZE_M > 0


def test_sentinel2_alt_bolgeleri():
    # Her ilde 2 alt bölge; merkezler Türkiye kutusu içinde; kutu adları tekil (07 ve 08 dosya adlarında kullanılır)
    assert set(config.S2_ALT_BOLGELER) == set(config.CITIES)
    adlar = []
    for il, liste in config.S2_ALT_BOLGELER.items():
        assert len(liste) == 2, il
        for ad, lat, lon in liste:
            assert 35.8 < lat < 42.2 and 25.6 < lon < 44.9, (il, ad)
            assert ad.isascii() and " " not in ad, (il, ad)
            adlar.append(f"{il}_{ad}")
    assert len(adlar) == len(set(adlar)) == 14
    assert sum(config.UNET_BOLME) == 1
    assert config.S2_KUTU_KM * 1000 / config.S2_SCALE_M >= 4 * config.UNET_PATCH   # şeritlere yetecek boyut
    assert config.S2_ETIKET_YILI == config.LABEL_YEAR
