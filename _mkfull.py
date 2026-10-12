import json
ROOT = r"C:\PROJETOS\dramio site e app\reelshort-pull"
links = json.load(open(ROOT + r"\links_pt.json", encoding="utf-8"))
slow = json.load(open(ROOT + r"\links_slow.json", encoding="utf-8"))
fila = []
for b, v in links.items():
    if v.get("erro"):
        continue
    ja = {e.get("episode_number") for e in (slow.get(b, {}) or {}).get("episodes", []) if e.get("m3u8")}
    for e in v.get("episodes", []):
        if e.get("slug") and not e.get("m3u8") and e.get("episode_number") not in ja:
            fila.append({"book": b, "ep": e.get("episode_number"), "slug": e["slug"]})
json.dump(fila, open("queue_full.json", "w", encoding="utf-8"), ensure_ascii=False)
dramas = len({x["book"] for x in fila})
print(f"fila do catalogo completo: {len(fila)} episodios | {dramas} dramas")
