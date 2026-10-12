#!/usr/bin/env python3
"""Mede quantas paginas de episodio um IP do GitHub aguenta antes do WAF bloquear.
Uso: python3 mede_tolerancia.py <pausa_segundos>
"""
import json, sys, time, urllib.request, urllib.error

PAUSA = float(sys.argv[1]) if len(sys.argv) > 1 else 1.5
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")
BASE = "https://www.reelshort.com"

slugs = json.load(open("slugs_test.json", encoding="utf-8"))
print(f"pausa={PAUSA}s | slugs disponiveis={len(slugs)}", flush=True)

ok = 0
falhas_seguidas = 0
primeira_falha = None
t0 = time.time()

for i, s in enumerate(slugs, 1):
    try:
        req = urllib.request.Request(f"{BASE}/episodes/{s}", headers={
            "User-Agent": UA, "Referer": BASE + "/"})
        with urllib.request.urlopen(req, timeout=25) as r:
            html = r.read().decode("utf-8", "replace")
        bloqueado = ("gokuProps" in html) or (len(html) < 5000)
        if bloqueado:
            falhas_seguidas += 1
            if primeira_falha is None:
                primeira_falha = i
        elif ".m3u8" in html:
            ok += 1
            falhas_seguidas = 0
        else:
            falhas_seguidas += 1
    except Exception:
        falhas_seguidas += 1
        if primeira_falha is None:
            primeira_falha = i

    if i % 25 == 0:
        print(f"  {i} tentativas | {ok} OK | falhas seguidas={falhas_seguidas} | {time.time()-t0:.0f}s", flush=True)
    if falhas_seguidas >= 25:
        print(f"PAROU: 25 falhas seguidas na tentativa {i}", flush=True)
        break
    time.sleep(PAUSA)

dt = time.time() - t0
print(f"\n=== RESULTADO pausa={PAUSA}s ===")
print(f"  paginas OK: {ok}")
print(f"  primeira falha na tentativa: {primeira_falha}")
print(f"  tempo total: {dt:.0f}s ({dt/max(1,i):.2f}s por requisicao)")
print(f"  >>> TOLERANCIA: ~{ok} paginas por IP com pausa de {PAUSA}s")
