#!/usr/bin/env python3
"""Colhe o catalogo PT INTEIRO. Os slugs ja sao conhecidos; so falta baixar cada pagina.
Uso: python3 harvest_full.py <shard> <total>
Le queue_full.json (lista de {book, ep, slug}) e grava out/shard_<n>.json
"""
import json, os, re, sys, time, urllib.request, urllib.error

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")
BASE = "https://www.reelshort.com"
M3U8 = re.compile(r'https?://[^"\'\s\\]*?\.m3u8')
PAUSA = 0.7   # ritmo MEDIDO como seguro (0,5s aguentou 900 requisicoes sem bloqueio)


def get(url, tries=3, timeout=25):
    for i in range(tries):
        if i:
            time.sleep(1.5 * i)
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


def main():
    shard = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    total = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    fila = json.load(open("queue_full.json", encoding="utf-8"))
    minha = [q for i, q in enumerate(fila) if i % total == shard]
    print(f"shard {shard}/{total}: {len(minha)} episodios de {len(fila)}", flush=True)

    os.makedirs("out", exist_ok=True)
    res = {}
    t0 = time.time()
    ok = falhas = 0
    for n, item in enumerate(minha, 1):
        html = get(f"{BASE}/episodes/{item['slug']}")
        achou = M3U8.search(html or "")
        if achou:
            ok += 1
            res.setdefault(item["book"], []).append(
                {"ep": item["ep"], "slug": item["slug"], "m3u8": achou.group(0)})
        else:
            falhas += 1
        if n % 50 == 0 or n == len(minha):
            print(f"  {n}/{len(minha)} | ok={ok} falhas={falhas} | {time.time()-t0:.0f}s", flush=True)
        time.sleep(PAUSA)

    for b in res:
        res[b].sort(key=lambda x: x["ep"] or 0)
    saida = f"out/shard_{shard}.json"
    json.dump(res, open(saida, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"FIM shard {shard}: {len(res)} dramas, {ok} links ({falhas} falhas) -> {saida}", flush=True)


main()
