#!/usr/bin/env python3
"""Colhe links de episodio dos dramas dublados. Roda dentro de um runner do GitHub.
Uso: python3 harvest_dub.py <shard> <total>
Le queue.json (lista de entradas drama x idioma) e grava out/shard_<n>.json
"""
import json, os, re, sys, time, urllib.request, urllib.error

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")
BASE = "https://www.reelshort.com"
M3U8 = re.compile(r'https?://[^"\'\s\\]*?\.m3u8')
SLUG = re.compile(r'/episodes/([A-Za-z0-9\-%]+)')


def get(url, tries=3, timeout=30):
    for i in range(tries):
        if i:
            time.sleep(2 * i)
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA, "Referer": BASE + "/", "Accept-Language": "pt-BR,pt;q=0.9"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return ""
        except Exception:
            pass
    return ""


def slugs_do_drama(book_id):
    """Abre o filme e devolve os slugs dos episodios, na ordem."""
    html = get(f"{BASE}/movie/{book_id}")
    if not html:
        return []
    vistos, saida = set(), []
    for m in SLUG.finditer(html):
        s = m.group(1)
        if s in vistos:
            continue
        vistos.add(s)
        saida.append(s)
    return saida


def main():
    shard = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    total = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    fila = json.load(open("queue.json", encoding="utf-8"))
    minha = [q for i, q in enumerate(fila) if i % total == shard]
    print(f"shard {shard}/{total}: {len(minha)} entradas de {len(fila)}", flush=True)

    os.makedirs("out", exist_ok=True)
    res = {}
    t0 = time.time()
    for n, item in enumerate(minha, 1):
        bid = item["book_idioma"]
        slugs = slugs_do_drama(bid)
        links = []
        for ep, slug in enumerate(slugs, 1):
            html = get(f"{BASE}/episodes/{slug}")
            achou = M3U8.search(html or "")
            if achou:
                links.append({"ep": ep, "slug": slug, "m3u8": achou.group(0)})
            time.sleep(0.7)
        if links:
            res[bid] = {"drama_pt": item.get("drama_pt"), "book_pt": item.get("book_pt"),
                        "idioma": item.get("idioma"), "eps_declarados": item.get("eps"),
                        "slugs": len(slugs), "links": links}
        if n % 5 == 0 or n == len(minha):
            tot = sum(len(v["links"]) for v in res.values())
            print(f"  {n}/{len(minha)} | {len(res)} dramas | {tot} links | {time.time()-t0:.0f}s", flush=True)

    saida = f"out/shard_{shard}.json"
    json.dump(res, open(saida, "w", encoding="utf-8"), ensure_ascii=False)
    tot = sum(len(v["links"]) for v in res.values())
    print(f"FIM shard {shard}: {len(res)} dramas, {tot} links -> {saida}", flush=True)


main()

