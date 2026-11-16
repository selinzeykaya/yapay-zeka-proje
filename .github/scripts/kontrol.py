"""GitHub Actions kontrolü: veri ya da GEE gerektirmez, hiçbir şey eğitmez.
1) Notebook'lar geçerli JSON mu, kod hücrelerinde sözdizimi hatası var mı?
2) config.py ve src/ içe aktarılabiliyor mu?
3) ml_utils: 4 model sahte küçük veriyle kurulup metrikler hesaplanabiliyor mu?
"""
import ast
import glob
import json
import sys

import numpy as np

sys.path.insert(0, ".")
hata = 0

for nb in sorted(glob.glob("notebooks/*.ipynb")):
    try:
        d = json.load(open(nb, encoding="utf-8"))
    except Exception as e:
        print(f"::error file={nb}::Notebook açılamıyor (bozuk JSON): {e}")
        hata += 1
        continue
    kod = [c for c in d["cells"] if c["cell_type"] == "code"]
    for i, c in enumerate(kod, 1):
        src = "".join(c["source"])
        # Colab'a özgü !komut ve %sihirli satırlar Python değildir → atla
        src = "\n".join(("pass  # " + l) if l.lstrip().startswith(("!", "%")) else l for l in src.split("\n"))
        try:
            ast.parse(src)
        except SyntaxError as e:
            print(f"::error file={nb}::{i}. kod hücresinde sözdizimi hatası (satır {e.lineno}): {e.msg}")
            hata += 1
    print(f"OK  {nb}  ({len(kod)} kod hücresi)")

import config  # noqa: E402
from src import gee_utils, ml_utils  # noqa: E402,F401

print("OK  config.py, src/gee_utils.py, src/ml_utils.py içe aktarıldı")

rng = np.random.default_rng(0)
labels = sorted(config.CLASSES)
n_feat = len(config.MODEL_FEATURES)
X = rng.normal(size=(len(labels) * 20, n_feat))
y = np.repeat(labels, 20)
for name in config.MODELS:
    try:
        m = ml_utils.make_pipeline(name).fit(X, y)
        met = ml_utils.compute_metrics(y, m.predict(X), m.predict_proba(X), labels)
        print(f"OK  {name}: model kuruldu, metrikler hesaplandı ({len(met)} metrik)")
    except Exception as e:
        print(f"::error::{name} modeli sahte veriyle çalışmadı: {e}")
        hata += 1

if hata:
    sys.exit(f"{hata} hata bulundu")
print("Tüm kontroller geçti.")
