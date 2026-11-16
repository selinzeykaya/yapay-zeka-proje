"""Notebook kontrolü (CI'da ve elle çalıştırılabilir: `python tools/notebook_kontrol.py`).

Her notebook için:
  1. Geçerli JSON ve nbformat 4 mü?
  2. Her kod hücresi Python olarak ayrıştırılabiliyor mu? (`!pip`, `%magic` satırları atlanır)
  3. Çıktı kaydedilmemiş mi? Repo çıktısız notebook tutar: çıktılar büyük olur ve sonuçlar Drive'da.
  4. Colab kurulum hücresinde GITHUB_BRANCH ayarı var mı?
Hata varsa hepsini listeler ve 1 ile çıkar (CI kırmızı olur).
"""
import ast
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []
notebooks = sorted(glob.glob(os.path.join(ROOT, "notebooks", "*.ipynb")))
if not notebooks:
    errors.append("notebooks/ altında hiç notebook bulunamadı")

for path in notebooks:
    name = os.path.basename(path)
    try:
        with open(path, encoding="utf-8") as f:
            nb = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        errors.append(f"{name}: geçerli JSON değil ({e})")
        continue
    if nb.get("nbformat") != 4:
        errors.append(f"{name}: nbformat 4 değil ({nb.get('nbformat')})")

    has_branch = False
    for i, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        src = "".join(cell.get("source", []))
        has_branch |= "GITHUB_BRANCH" in src
        code = "".join(line for line in src.splitlines(keepends=True)
                       if not line.lstrip().startswith(("!", "%")))
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"{name}, hücre {i}: yazım hatası, satır {e.lineno}: {e.msg}")
        if cell.get("outputs") or cell.get("execution_count") is not None:
            errors.append(f"{name}, hücre {i}: çıktı kaydedilmiş (Colab'da Düzenle → Tüm çıktıları temizle)")
    if not has_branch:
        errors.append(f"{name}: kurulum hücresinde GITHUB_BRANCH ayarı yok")

for e in errors:
    print("HATA:", e)
print(f"{len(notebooks)} notebook kontrol edildi, {len(errors)} hata.")
sys.exit(1 if errors else 0)
