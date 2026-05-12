from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

app = Flask(__name__)

# ---------------- CONFIGURAÇÃO PUBNUB ----------------
pn_config = PNConfiguration()
pn_config.publish_key = 'pub-c-321e2501-878f-49c7-ac68-046cd8820f0b'
pn_config.subscribe_key = 'sub-c-41217ff2-2c55-4aa7-a562-e0ac1a0624c5'
pn_config.user_id = "server_backend"
pubnub = PubNub(pn_config)

def init_db():
    conn = sqlite3.connect('seguranca.db')
    cursor = conn.cursor()
    # Tabela de colaboradores conforme requisitos [cite: 53-59]
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            tag INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            matricula TEXT,
            cargo TEXT,
            autorizado BOOLEAN NOT NULL,
            status TEXT DEFAULT 'ativo'
        )
    ''')
    # Tabela de logs com coluna de horas para o Pandas [cite: 83, 93]
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag INTEGER,
            nome TEXT,
            atividade TEXT,
            horario TEXT,
            horas TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ---------------- ROTAS CRUD E LOGIN ----------------

@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    conn = sqlite3.connect('seguranca.db')
    cursor = conn.cursor()
    cursor.execute("SELECT tag, nome, autorizado FROM usuarios WHERE status = 'ativo'")
    usuarios = {row[0]: {"nome": row[1], "autorizado": bool(row[2])} for row in cursor.fetchall()}
    conn.close()
    return jsonify(usuarios)

@app.route('/usuarios', methods=['POST'])
def salvar_usuario():
    dados = request.json
    conn = sqlite3.connect('seguranca.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO usuarios (tag, nome, matricula, cargo, autorizado)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(tag) DO UPDATE SET
            nome=excluded.nome, autorizado=excluded.autorizado,
            matricula=excluded.matricula, cargo=excluded.cargo
    ''', (dados.get('tag'), dados.get('nome'), dados.get('matricula'), dados.get('cargo'), int(dados.get('autorizado', 0))))
    conn.commit()
    conn.close()
    return jsonify({"status": "Sucesso"}), 201

@app.route('/login', methods=['POST'])
def login():
    dados = request.json
    if dados.get('usuario') == 'admin' and dados.get('senha') == '123':
        return jsonify({"autenticado": True}), 200
    return jsonify({"autenticado": False}), 401

# ---------------- REGISTRO DE EVENTOS ----------------

@app.route('/log', methods=['POST'])
def registrar_log():
    dados = request.json
    horas = dados.get('horas', '')
   
    conn = sqlite3.connect('seguranca.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO logs (tag, nome, atividade, horario, horas) VALUES (?, ?, ?, ?, ?)',
                   (dados.get('tag'), dados.get('nome'), dados.get('atividade'), dados.get('horario'), horas))
    conn.commit()
    conn.close()
   
    pubnub.publish().channel("seguranca_sala").message({
        "nome": dados.get('nome'),
        "atividade": dados.get('atividade'),
        "horario": dados.get('horario'),
        "horas": horas,
        "alerta": dados.get('atividade') in ["invasao", "nao_autorizado"]
    }).sync()
   
    return jsonify({"status": "Ok"}), 201

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)