import json, random
ROOT = r"C:\PROJETOS\dramio site e app\reelshort-pull"
links = json.load(open(ROOT + r"\links_pt.json", encoding="utf-8"))
slow = json.load(open(ROOT + r"\links_slow.json", encoding="utf-8"))
p = []
for b, v in links.items():
    if v.get("erro") or v.get("modo") != "precisa_lento":
        continue
    ja = {e.get("episode_number") for e in (slow.get(b, {}) or {}).get("episodes", []) if e.get("m3u8")}
    for e in v.get("episodes", []):
        if e.get("slug") and not e.get("m3u8") and e.get("episode_number") not in ja:
            p.append(e["slug"])
random.seed(1); random.shuffle(p)
json.dump(p[:900], open("slugs_test.json", "w", encoding="utf-8"), ensure_ascii=False)
print("slugs de teste:", min(900, len(p)))
