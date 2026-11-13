# Zlozi jeden samostatny HTML subor (bez internetu funguje, pisma su volitelne):
#   ../optimalizacia.html          - na otvorenie v prehliadaci (aj offline)
#   dist/optimalizacia_artifact.html - obsah bez <html>/<head> na publikovanie
import json, os
TU = os.path.dirname(os.path.abspath(__file__))
rd = lambda n: open(os.path.join(TU, n), encoding="utf-8").read()
seed_dir = os.path.join(TU, "..", "seed")
priklady = json.load(open(os.path.join(seed_dir, "seed_priklady.json"), encoding="utf-8"))
vys = json.load(open(os.path.join(seed_dir, "seed_vysledky.json"), encoding="utf-8"))
vys = {k: ({"chyba": v["chyba"]} if "chyba" in v else {"bod": v["bod"], "iteracie": v["iteracie"], "f": v["f"]}) for k, v in vys.items()}
seed = json.dumps({"priklady": priklady, "vysledky": vys}, ensure_ascii=False)
body = rd("app.html").replace("{{ENGINE}}", rd("engine.js")).replace("{{SEED}}", seed).replace("{{APP}}", rd("app.js"))
os.makedirs(os.path.join(TU, "dist"), exist_ok=True)
open(os.path.join(TU, "dist", "optimalizacia_artifact.html"), "w", encoding="utf-8").write(body)
full = ('<!doctype html>\n<html lang="sk">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<style>[hidden]{display:none!important}body{margin:0}img{max-width:100%}</style>\n'
        + body.replace("<div class=\"app\">", "</head>\n<body>\n<div class=\"app\">", 1) + "\n</body>\n</html>\n")
open(os.path.join(TU, "..", "optimalizacia.html"), "w", encoding="utf-8").write(full)
print("ok", len(full) // 1024, "kB")
