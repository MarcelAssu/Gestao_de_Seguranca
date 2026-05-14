import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
from datetime import datetime
import json
import requests
import os
import csv
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub, SubscribeCallback

# --- CONFIGURAÇÃO ---
API_URL = "http://10.1.25.118:5000" # Ajuste para o IP do servidor
FILE_USUARIOS = "usuarios_local.json"
FILE_PENDENTES = "logs_pendentes.json"

# Configuração PubNub na Raspberry
pn_config = PNConfiguration()
pn_config.publish_key = 'pub-c-321e2501-878f-49c7-ac68-046cd8820f0b'
pn_config.subscribe_key = 'sub-c-41217ff2-2c55-4aa7-a562-e0ac1a0624c5'
pn_config.user_id = "raspberry_pi_01"
pubnub = PubNub(pn_config)

# --- GPIO ---
LED_VERDE, LED_VERMELHO, BUZZER = 17, 27, 18
GPIO.setmode(GPIO.BCM)
for pin in [LED_VERDE, LED_VERMELHO, BUZZER]: GPIO.setup(pin, GPIO.OUT)

leitor = SimpleMFRC522()

# --- VARIÁVEIS GLOBAIS ---
usuarios = {}
entradas = {}
ja_entraram_hoje = {}
eventos_sessao = []

# --- LÓGICA OFFLINE (RESILIÊNCIA) E ATUALIZAÇÃO ---

def sincronizar_usuarios():
    """Busca dados no servidor. Se falhar, usa arquivo local"""
    global usuarios
    try:
        r = requests.get(f"{API_URL}/usuarios", timeout=3)
        if r.status_code == 200:
            dados = r.json()
            with open(FILE_USUARIOS, "w") as f: json.dump(dados, f)
            usuarios = {int(k): v for k, v in dados.items()}
            print("🔄 Lista de usuários atualizada via API/PubNub!")
    except:
        print("Servidor offline. Usando backup local...")
        if os.path.exists(FILE_USUARIOS):
            with open(FILE_USUARIOS, "r") as f:
                usuarios = {int(k): v for k, v in json.load(f).items()}

# --- LISTENER DO PUBNUB ---
class MySubscribeCallback(SubscribeCallback):
    def message(self, pubnub, message):
        if message.message.get("acao") == "atualizar_usuarios":
            sincronizar_usuarios()

pubnub.add_listener(MySubscribeCallback())
pubnub.subscribe().channels(["controle_dispositivos"]).execute()


def registrar_evento(tag, nome, atividade, horas=""):
    """Envia log para API ou salva localmente se houver falha"""
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

# --- FEEDBACK VISUAL/SONORO ---
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

# --- EXECUÇÃO ---
# Inicializa a primeira vez para garantir os dados antes do loop começar
sincronizar_usuarios()

try:
    print("Aguardando tag...")
    while True:
        tag, _ = leitor.read()
        agora = datetime.now()

        if tag in usuarios:
            user = usuarios[tag]
            if user["autorizado"]:
                if tag not in entradas:
                    # Lógica de Entrada
                    msg = "Bem-vindo de volta" if tag in ja_entraram_hoje else "Bem-vindo"
                    print(f"{msg}, {user['nome']}")
                    entradas[tag] = agora
                    ja_entraram_hoje[tag] = agora.date()
                    registrar_evento(tag, user["nome"], "entrada")
                else:
                    # Lógica de Saída
                    permanencia = (agora - entradas[tag]).total_seconds() / 3600
                    print(f"Saída: {user['nome']} | Tempo: {permanencia:.4f}h")
                    registrar_evento(tag, user["nome"], "saida", f"{permanencia:.4f}h")
                    del entradas[tag]
                feedback("sucesso")
            else:
                # Acesso Negado (Cadastrado mas sem permissão)
                print(f"Acesso negado para {user['nome']}")
                registrar_evento(tag, user["nome"], "nao_autorizado")
                feedback("negado")
        else:
            # Tentativa de Invasão (Tag desconhecida)
            print(f"ALERTA: Tentativa de invasão! Tag: {tag}")
            registrar_evento(tag, "Desconhecido", "invasao")
            feedback("negado")
       
        time.sleep(2)

except KeyboardInterrupt:
    print("\nEncerrando sistema e salvando relatórios...")
   
    # Salva CSV final para análise Pandas ao encerrar
    arquivo_existe = os.path.isfile("relatorio_final.csv")

    with open("relatorio_final.csv", "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["tag", "nome", "atividade", "horario", "horas"])
       
        if not arquivo_existe:
            writer.writeheader()
           
        writer.writerows(eventos_sessao)
       
    GPIO.cleanup()
    print("Concluído. Até logo!")