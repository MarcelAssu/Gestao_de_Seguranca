from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime
import os
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

app = Flask(__name__,
    template_folder=os.path.join('..', 'Front-end', 'templates'),
    static_folder=os.path.join('..', 'Front-end', 'static')
    )

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
    cursor.execute("SELECT tag, nome, matricula, cargo, autorizado, status FROM usuarios WHERE status = 'ativo'")
    usuarios = {row[0]: {"nome": row[1], "matricula": row[2], "cargo": row[3], "autorizado": bool(row[4]), "status": row[5]} for row in cursor.fetchall()}
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


@app.route('/')
def tela_login():
    return render_template('login.html')

@app.route('/gerencia-users')
def gerencia_users():
    return render_template('gerencia-users.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/dashboard/dados')
def dashboard_dados():
    conn = sqlite3.connect('seguranca.db')
    cursor = conn.cursor()
    hoje = datetime.now().strftime('%Y-%m-%d')

    # Entradas hoje
    cursor.execute("SELECT COUNT(*), nome, horario FROM logs WHERE atividade='entrada' AND horario LIKE ? ORDER BY id DESC", (f'{hoje}%',))
    entradas = cursor.fetchone()

    # Saídas hoje
    cursor.execute("SELECT COUNT(*), nome, horario FROM logs WHERE atividade='saida' AND horario LIKE ? ORDER BY id DESC", (f'{hoje}%',))
    saidas = cursor.fetchone()

    # Tentativas negadas
    cursor.execute("SELECT COUNT(*) FROM logs WHERE atividade='nao_autorizado' AND horario LIKE ?", (f'{hoje}%',))
    negadas = cursor.fetchone()[0]

    # Tentativas de invasão
    cursor.execute("SELECT COUNT(*) FROM logs WHERE atividade='invasao' AND horario LIKE ?", (f'{hoje}%',))
    invasoes = cursor.fetchone()[0]

    # Atualmente na sala
    cursor.execute("SELECT nome, horario, tag FROM logs WHERE atividade='entrada' AND tag NOT IN (SELECT tag FROM logs WHERE atividade='saida') ORDER BY id DESC")
    na_sala = [{"nome": r[0], "horario": r[1], "tag": r[2]} for r in cursor.fetchall()]

    # Últimas entradas autorizadas
    cursor.execute("SELECT nome, horario, tag FROM logs WHERE atividade='entrada' ORDER BY id DESC LIMIT 5")
    ultimas_entradas = [{"nome": r[0], "horario": r[1], "tag": r[2]} for r in cursor.fetchall()]

    # Últimas saídas
    cursor.execute("SELECT nome, horario, tag FROM logs WHERE atividade='saida' ORDER BY id DESC LIMIT 5")
    ultimas_saidas = [{"nome": r[0], "horario": r[1], "tag": r[2]} for r in cursor.fetchall()]

    # Tentativas de invasão detalhadas
    cursor.execute("SELECT nome, horario, tag FROM logs WHERE atividade='invasao' ORDER BY id DESC LIMIT 5")
    lista_invasoes = [{"nome": r[0], "horario": r[1], "tag": r[2]} for r in cursor.fetchall()]

    conn.close()

    return jsonify({
        "entradas_count": entradas[0],
        "entradas_ultima": f"{entradas[1]} às {entradas[2]}" if entradas[1] else "--",
        "saidas_count": saidas[0],
        "saidas_ultima": f"{saidas[1]} às {saidas[2]}" if saidas[1] else "--",
        "negadas": negadas,
        "invasoes": invasoes,
        "na_sala": na_sala,
        "ultimas_entradas": ultimas_entradas,
        "ultimas_saidas": ultimas_saidas,
        "lista_invasoes": lista_invasoes
    })
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