from flask import Flask, render_template, request, jsonify
import sqlite3, datetime
from database import init_db, DB
from modelo import recomendar

app = Flask(__name__)
init_db()  # Garante criação do database.db (SQLite offline) na primeira execução - padrão Store-and-Forward

@app.route("/")
def index():
    return render_template("index.html")  # Tela única da máquina MAQ-BELEM-001

@app.route("/api/recomendar", methods=["POST"])
def api_recomendar():
    data = request.json
    # RF02 - LGPD: Apenas ID anônimo (ex: 04144774), sem CPF/nome
    cliente_id = data.get("cliente_id","anonimo").strip()
    online = data.get("online", False)  # RF04 - Flag para simular Online vs Offline

    # RNF01 - Processamento 100% no Edge Node (Raspberry Pi simulado)
    # Retorna Top 3 + latência em ms + qtd histórico
    recs, lat, hist = recomendar(cliente_id)

    # Diferencial do MVP: prova funcionamento offline
    status = "SALVO OFFLINE (SQLite) - Edge Computing" if not online else "SINCRONIZADO NUVEM (MQTT Simulado)"
    
    return jsonify({
        "cliente_id": cliente_id,
        "recomendacoes": recs,  # Saída: lista Top 3 produtos (id, nome, cat, preço)
        "latencia_ms": lat,     # Métrica chave: 8-25ms vs 800ms-2s da nuvem (SHI et al., 2016)
        "historico_qtd": hist,
        "status": status,
        "edge_node": "MAQ-BELEM-001 - Raspberry Pi 4 (2GB RAM) Simulado", # RNF02 - Baixo custo R$400
        "modelo_size": "4.2KB (Regra) / 4.8MB (TFLite)" # Modelo leve para caber em microcontrolador
    })

@app.route("/api/comprar", methods=["POST"])
def comprar():
    # RF03 - Registro de compra offline, nenhuma venda é perdida
    data = request.json
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    # Persiste localmente com timestamp e maquina_id para futura sincronização via MQTT
    cur.execute("INSERT INTO compras (cliente_id, produto_id, horario, maquina_id) VALUES (?,?,?,?)",
                (data.get("cliente_id"), data.get("produto_id"), datetime.datetime.now().isoformat(), "MAQ-BELEM-001"))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

if __name__ == "__main__":
    # Roda em http://127.0.0.1:5000 - simula o hardware de borda
    app.run(debug=True, port=5000)