import sqlite3, os, random, datetime

DB = "database.db"  # SQLite arquivo único - viabiliza operação 100% offline sem servidor

def init_db():
    # RNF03 - Confiabilidade: só cria se não existir, evita perda de histórico local (Store-and-Forward)
    if os.path.exists(DB):
        return
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    # Tabela de catálogo local - 12 produtos fixos da MAQ-BELEM-001
    cur.execute("CREATE TABLE produtos (id INTEGER PRIMARY KEY, nome TEXT, categoria TEXT, preco REAL)")
    # Tabela de log offline - guarda todas as vendas com maquina_id para sincronização futura via MQTT
    cur.execute("CREATE TABLE compras (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente_id TEXT, produto_id INTEGER, horario TEXT, maquina_id TEXT)")
    
    produtos = [
        (1, "Água 500ml", "Bebida", 3.0),
        (2, "Água com Gás", "Bebida", 3.5),
        (3, "Refrigerante Lata", "Bebida", 5.0),
        (4, "Café Preto", "Bebida", 4.0),
        (5, "Suco Caixa", "Bebida", 5.5),
        (6, "Salgadinho", "Salgado", 6.0),
        (7, "Barra Cereal", "Saudável", 4.5),
        (8, "Chocolate", "Doce", 5.0),
        (9, "Biscoito", "Doce", 4.0),
        (10, "Sanduíche Natural", "Saudável", 8.0),
        (11, "Pão de Queijo", "Salgado", 6.5),
        (12, "Água de Coco", "Bebida", 7.0),
    ]
    cur.executemany("INSERT INTO produtos VALUES (?,?,?,?)", produtos)

    # Simulação de 100 compras para teste do algoritmo de recomendação
    # Perfil personalizado: 04144774 e leo compram mais Água com Gás, Café e Barra (prova conceito personalizado)
    for _ in range(100):
        cid = random.choice(["04144774", "leo", "2024001", "2024002"])
        pid = random.choice([2,4,7]) if cid in ["04144774","leo"] else random.choice([1,3,6,8,11])
        cur.execute("INSERT INTO compras (cliente_id, produto_id, horario, maquina_id) VALUES (?,?,?,?)",
                    (cid, pid, datetime.datetime.now().isoformat(), "MAQ-BELEM-001"))
    conn.commit()
    conn.close()