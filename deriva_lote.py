#!/usr/bin/env python3
"""ATALHO: 1 requisicao por DRAMA (em vez de 1 por episodio) quando o video_pic
carrega o hash do video. Deriva o m3u8 direto da imagem do capitulo.
Uso: python3 deriva_lote.py <shard> <total>
Le queue_full.json, agrupa por drama, pega o JSON do filme e deriva.
"""
import json, os, re, sys, time, urllib.request, urllib.error

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")
BASE = "https://www.reelshort.com"
CDN = "https://v-mps.crazymaplestudios.com"
PAUSA = 1.2
HASH_NO_PIC = re.compile(r"crazymaplestudios\.com/(?:vod-\d+/)?([0-9a-f]{24,})/")


def get(url, tries=3, timeout=30):
    for i in range(tries):
        if i:
            time.sleep(1.5 * i)
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA, "Referer": BASE + "/", "Accept-Language": "pt-BR,pt;q=0.9"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:
            pass
    return ""


def canonico(book):
    """slug canonico do filme (segue o redirect)"""
    try:
        req = urllib.request.Request(f"{BASE}/movie/{book}", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.geturl().rstrip("/").split("/")[-1]
    except Exception:
        return ""


def main():
    shard = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    total = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    fila = json.load(open("queue_full.json", encoding="utf-8"))
    books = sorted({q["book"] for q in fila})
    meus = [b for i, b in enumerate(books) if i % total == shard]
    print(f"shard {shard}/{total}: {len(meus)} dramas de {len(books)}", flush=True)

    # build id atual
    html = get(f"{BASE}/pt")
    m = re.search(r'"buildId":"([^"]+)"', html or "")
    build = m.group(1) if m else ""
    print(f"buildId: {build}", flush=True)

    os.makedirs("out", exist_ok=True)
    res, derivados, nao_deriv = {}, 0, 0
    t0 = time.time()
    for n, book in enumerate(meus, 1):
        slug = canonico(book)
        if not slug:
            continue
        js = get(f"{BASE}/_next/data/{build}/pt/movie/{slug}.json")
        try:
            caps = ((json.loads(js).get("pageProps") or {}).get("data") or {}).get("online_base") or []
        except Exception:
            caps = []
        links = []
        for c in caps:
            m2 = HASH_NO_PIC.search(str(c.get("video_pic") or ""))
            if not m2:
                continue
            links.append({"ep": c.get("serial_number"),
                          "m3u8": f"{CDN}/{m2.group(1)}/h264-ordinary-fd.m3u8"})
        if links:
            res[book] = {"derivados": links, "metodo": "video_pic"}
            derivados += len(links)
        else:
            nao_deriv += 1
        if n % 5 == 0 or n == len(meus):
            print(f"  {n}/{len(meus)} | {derivados} derivados | {nao_deriv} sem atalho | {time.time()-t0:.0f}s", flush=True)
        time.sleep(PAUSA)

    json.dump(res, open(f"out/deriv_{shard}.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(f"FIM shard {shard}: {len(res)} dramas com atalho, {derivados} links derivados", flush=True)


main()
