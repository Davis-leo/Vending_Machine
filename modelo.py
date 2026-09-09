import sqlite3, time
from collections import Counter
from database import DB

def recomendar(cliente_id: str):
    inicio = time.time()
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT produto_id FROM compras WHERE cliente_id=?", (cliente_id,))
    historico = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT id, nome, categoria, preco FROM produtos")
    todos = {r[0]: {"id": r[0], "nome": r[1], "categoria": r[2], "preco": r[3]} for r in cur.fetchall()}

    if not historico:
        cur.execute("SELECT produto_id, COUNT(*) FROM compras GROUP BY produto_id ORDER BY COUNT(*) DESC LIMIT 3")
        top_ids = [r[0] for r in cur.fetchall()]
    else:
        freq = Counter(historico)
        fav_cats = [todos[pid]["categoria"] for pid in historico if pid in todos]
        cat_fav = Counter(fav_cats).most_common(1)[0][0] if fav_cats else None
        scored = []
        for pid, prod in todos.items():
            score = freq.get(pid, 0)*2 + (1 if prod["categoria"]==cat_fav else 0)
            scored.append((score, pid))
        scored.sort(reverse=True)
        top_ids = [pid for _, pid in scored[:3]]

    recomendados = [todos[i] for i in top_ids if i in todos]
    latency = int((time.time()-inicio)*1000)
    conn.close()
    return recomendados, latency, len(historico)