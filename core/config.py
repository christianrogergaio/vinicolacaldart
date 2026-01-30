import os

# Caminhos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENCIAIS_FIREBASE = os.path.join(BASE_DIR, "config", "evcr-monitor-firebase-key.json")
PASTA_DADOS = os.path.join(BASE_DIR, 'dados')
ARQUIVO_HISTORICO_CSV = os.path.join(PASTA_DADOS, "historico_avaliacoes.csv")

# Arduino / Serial
# Arduino / Serial
PORTA_SERIAL = 'COM4'
BAUD_RATE = 9600
INTERVALO_LEITURA = 1  # Segundos entre leituras

# Geolocalização
LATITUDE = -29.0305
LONGITUDE = -51.1916

# Telegram (Configuração)
TELEGRAM_TOKEN = "8225397256:AAFmShbROE8yYWbykbGY7Z-HS5NqcD21XsA"
TELEGRAM_CHAT_ID = "5933325252" # Pode pegar via userinfobot

# Sincronização Remota (Dashboard no Mac/Outro PC)
# Exemplo: "http://192.168.1.50:8000/api/readings"
API_URL_SYNC = None 

# Constantes de Domínio
DOENCAS = [
    "Míldio", "Oídio", "Botrytis", "Antracnose", 
    # "Requeima", "Pinta Preta", "Ferrugem Asiática" # Outras culturas
]
PLANTAS = ["Videira"] #, "Tomateiro", "Cannabis", "Soja"]

# Constantes GDD (Graus-Dia)
BASE_TEMP_SOJA = 10

ESTADIOS_POR_PLANTA = {
    "Videira": [
        "Dormência", "Brotamento (EL 4-6)", "Floração (EL 19-25)", 
        "Frutificação (EL 27-33)", "Veraison (Maturação)", "Pós-colheita"
    ],
    # "Tomateiro": [
    #     "Germinação/Plântula", "Vegetativo", "Floração", 
    #     "Frutificação (Verde)", "Maturação (Vermelho)", "Senescência"
    # ],
    # "Cannabis": [
    #     "Plântula/Clones", "Vegetativo Inicial", "Vegetativo Tardio",
    #     "Floração Inicial", "Floração Tardia (Maturação)", "Secagem/Cura"
    # ],
    # "Soja": [
    #     "VE (Emergência)", "VC (Cotilédone)", "V1-Vn (Vegetativo)", 
    #     "R1 (Início Floração)", "R2 (Floração Plena)", 
    #     "R3-R4 (Formação Vagem)", "R5 (Enchimento Grão)", "R8 (Maturação Plena)"
    # ]
}

# Fallback genérico caso a planta não esteja no dicionário
ESTADIOS_GENERICOS = ["Inicial", "Vegetativo", "Reprodutivo", "Maturação", "Final"]
# Mantendo ESTADIOS por compatibilidade temporária (pega o da Videira como default)
ESTADIOS = ESTADIOS_POR_PLANTA["Videira"]
