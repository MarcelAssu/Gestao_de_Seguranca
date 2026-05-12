import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
from datetime import datetime
import json
import requests
import os
import csv

# --- CONFIGURAÇÃO ---
API_URL = "http://10.1.25.118:5000" # Ajuste para o IP do servidor
FILE_USUARIOS = "usuarios_local.json"
FILE_PENDENTES = "logs_pendentes.json"

# --- GPIO [cite: 21] ---
LED_VERDE, LED_VERMELHO, BUZZER = 17, 27, 18
GPIO.setmode(GPIO.BCM)
for pin in [LED_VERDE, LED_VERMELHO, BUZZER]: GPIO.setup(pin, GPIO.OUT)

leitor = SimpleMFRC522()

# --- LÓGICA OFFLINE (RESILIÊNCIA) [cite: 75-81] ---

def sincronizar_usuarios():
    """Busca dados no servidor. Se falhar, usa arquivo local [cite: 76, 77]"""
    try:
        r = requests.get(f"{API_URL}/usuarios", timeout=3)
        if r.status_code == 200:
            dados = r.json()
            with open(FILE_USUARIOS, "w") as f: json.dump(dados, f)
            return {int(k): v for k, v in dados.items()}
    except:
        print("Servidor offline. Usando backup local...")
    
    if os.path.exists(FILE_USUARIOS):
        with open(FILE_USUARIOS, "r") as f:
            return {int(k): v for k, v in json.load(f).items()}
    return {}

def registrar_evento(tag, nome, atividade, horas=""):
    """Envia log para API ou salva localmente se houver falha [cite: 79, 80]"""
    horario = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    payload = {"tag": tag, "nome": nome, "atividade": atividade, "horario": horario}
    
    eventos_sessao.append({**payload, "horas": horas}) # Para o CSV final

    try:
        requests.post(f"{API_URL}/log", json=payload, timeout=2)
    except:
        print("Falha na rede. Log armazenado localmente.")
        logs = []
        if os.path.exists(FILE_PENDENTES):
            with open(FILE_PENDENTES, "r") as f: logs = json.load(f)
        logs.append(payload)
        with open(FILE_PENDENTES, "w") as f: json.dump(logs, f)

# --- FEEDBACK VISUAL/SONORO [cite: 23-26] ---
def feedback(tipo):
    if tipo == "sucesso":
        GPIO.output(LED_VERDE, True); GPIO.output(BUZZER, True)
        time.sleep(0.5)
        GPIO.output(LED_VERDE, False); GPIO.output(BUZZER, False)
    elif tipo == "negado":
        GPIO.output(LED_VERMELHO, True)
        for _ in range(3):
            GPIO.output(BUZZER, True); time.sleep(0.1)
            GPIO.output(BUZZER, False); time.sleep(0.1)
        GPIO.output(LED_VERMELHO, False)

# --- EXECUÇÃO [cite: 14-20] ---
usuarios = sincronizar_usuarios()
entradas = {}
ja_entraram_hoje = {}
eventos_sessao = []

try:
    print("Aguardando tag...")
    while True:
        tag, _ = leitor.read()
        agora = datetime.now()

        if tag in usuarios:
            user = usuarios[tag]
            if user["autorizado"]:
                if tag not in entradas:
                    # Lógica de Entrada [cite: 17, 22, 24]
                    msg = "Bem-vindo de volta" if tag in ja_entraram_hoje else "Bem-vindo"
                    print(f"{msg}, {user['nome']}")
                    entradas[tag] = agora
                    ja_entraram_hoje[tag] = agora.date()
                    registrar_evento(tag, user["nome"], "entrada")
                else:
                    # Lógica de Saída [cite: 17, 18]
                    permanencia = (agora - entradas[tag]).total_seconds() / 3600
                    print(f"Saída: {user['nome']} | Tempo: {permanencia:.2f}h")
                    registrar_evento(tag, user["nome"], "saida", f"{permanencia:.2f}h")
                    del entradas[tag]
                feedback("sucesso")
            else:
                # Acesso Negado (Cadastrado mas sem permissão) [cite: 26]
                print(f"Acesso negado para {user['nome']}")
                registrar_evento(tag, user["nome"], "nao_autorizado")
                feedback("negado")
        else:
            # Tentativa de Invasão (Tag desconhecida) [cite: 20, 35]
            print(f"ALERTA: Tentativa de invasão! Tag: {tag}")
            registrar_evento(tag, "Desconhecido", "invasao")
            feedback("negado")
        
        time.sleep(2)

except KeyboardInterrupt:
    # Salva CSV final para análise Pandas ao encerrar [cite: 83, 97]
    with open("relatorio_final.csv", "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["tag", "nome", "atividade", "horario", "horas"])
        writer.writeheader()
        writer.writerows(eventos_sessao)
    GPIO.cleanup()