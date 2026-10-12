import json
q = json.load(open("queue.json", encoding="utf-8"))
json.dump(q[:3], open("queue_teste.json", "w", encoding="utf-8"), ensure_ascii=False)
print("entradas de teste:", [x["book_idioma"] for x in q[:3]])
print("exemplo:", json.dumps(q[0], ensure_ascii=False)[:200])
