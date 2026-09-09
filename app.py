from flask import Flask, render_template, request, jsonify
import sqlite3, datetime
from database import init_db, DB
from modelo import recomendar

app = Flask(__name__)
init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/recomendar", methods=["POST"])
def api_recomendar():
    data = request.json
    cliente_id = data.get("cliente_id","anonimo").strip()
    online = data.get("online", False)
    recs, lat, hist = recomendar(cliente_id)
    status = "SALVO OFFLINE (SQLite) - Edge Computing" if not online else "SINCRONIZADO NUVEM (MQTT Simulado)"
    return jsonify({
        "cliente_id": cliente_id,
        "recomendacoes": recs,
        "latencia_ms": lat,
        "historico_qtd": hist,
        "status": status,
        "edge_node": "MAQ-BELEM-001 - Raspberry Pi 4 (2GB RAM) Simulado",
        "modelo_size": "4.2KB (Regra) / 4.8MB (TFLite)"
    })

@app.route("/api/comprar", methods=["POST"])
def comprar():
    data = request.json
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("INSERT INTO compras (cliente_id, produto_id, horario, maquina_id) VALUES (?,?,?,?)",
                (data.get("cliente_id"), data.get("produto_id"), datetime.datetime.now().isoformat(), "MAQ-BELEM-001"))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True, port=5000)