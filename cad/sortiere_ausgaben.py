"""Sortiert die erzeugten Dateien in cad/out/ nach Typ in Unterordner:
cad/ (STEP, STL)  dxf/  pdf/  bilder/ (PNG, SVG)  daten/ (CSV).  Unterordner wie testfront/ bleiben erhalten
(z. B. out/testfront/X.stl -> out/cad/testfront/X.stl). Wird am Ende von build_all.sh aufgerufen."""
import os, shutil

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
ZIEL = {".step": "cad", ".stp": "cad", ".stl": "cad", ".dxf": "dxf", ".pdf": "pdf",
        ".png": "bilder", ".svg": "bilder", ".csv": "daten"}
ZIELORDNER = set(ZIEL.values())


def main():
    for root, dirs, files in os.walk(OUT, topdown=True):
        rel = os.path.relpath(root, OUT)
        if rel == ".":
            dirs[:] = [d for d in dirs if d not in ZIELORDNER]
            rel = ""
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if ext not in ZIEL:
                continue
            dst = os.path.join(OUT, ZIEL[ext], rel)
            os.makedirs(dst, exist_ok=True)
            shutil.move(os.path.join(root, fn), os.path.join(dst, fn))
    for root, dirs, files in os.walk(OUT, topdown=False):      # leere Quellordner entfernen
        if root != OUT and not os.listdir(root):
            os.rmdir(root)


if __name__ == "__main__":
    main()
