import sqlite3
import os
from . import config
from datetime import datetime, timedelta

DB_PATH = os.path.join(config.PASTA_DADOS, "dados_locais.db")

def get_connection():
    """Retorna conexão com o banco de dados."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Cria as tabelas se não existirem."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabela para leituras do sensor (substitui JSONs diários)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sensores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_hora DATETIME,
        temperatura REAL,
        umidade REAL,
        latitude REAL,
        longitude REAL,
        origem TEXT
    )
    ''')

    # Tabela para registros manuais/avaliações (substitui historico_avaliacoes.csv)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS avaliacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_hora DATETIME,
        temperatura REAL,
        umidade REAL,
        doenca TEXT,
        planta TEXT,
        estadio TEXT,
        risco_nivel TEXT,
        vds REAL,
        comentario TEXT
    )
    ''') # Adicionado estadio

    # Tabela para Diário de Campo (Intervenções)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS intervencoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_hora DATETIME,
        tipo TEXT, 
        produto TEXT,
        observacoes TEXT
    )
    ''')

    conn.commit()
    conn.close()
    print(f"Banco de dados inicializado em: {DB_PATH}")

def salvar_leitura(temp, umid, lat, lon):
    """Salva uma nova leitura do sensor."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Ajuste Fuso Horario Brasil (UTC-3)
        agora = datetime.utcnow() - timedelta(hours=3)
        
        cursor.execute('''
        INSERT INTO sensores (data_hora, temperatura, umidade, latitude, longitude, origem)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (agora, temp, umid, lat, lon, "Bluetooth"))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao salvar no SQLite: {e}")
        return False

def registrar_intervencao(tipo, produto, obs=""):
    """Registra uma ação realizada no campo (ex: Aplicação de Defensivo)."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        agora = datetime.now()
        
        cursor.execute('''
        INSERT INTO intervencoes (data_hora, tipo, produto, observacoes)
        VALUES (?, ?, ?, ?)
        ''', (agora, tipo, produto, obs))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao salvar intervenção: {e}")
        return False

def buscar_historico(dias=7):
    """Busca histórico de sensores dos últimos X dias."""
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        data_limite = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('SELECT * FROM sensores WHERE data_hora >= ? ORDER BY data_hora ASC', (data_limite,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Erro ao buscar histórico: {e}")
        return []

def buscar_intervencoes(dias=30):
    """Busca intervenções dos últimos X dias."""
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        data_limite = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('SELECT * FROM intervencoes WHERE data_hora >= ? ORDER BY data_hora ASC', (data_limite,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Erro ao buscar intervenções: {e}")
        return []

    except Exception as e:
        print(f"Erro ao salvar intervenção: {e}")
        return False



def registrar_sinal_visual(sinal, severidade="baixa", obs=""):
    """Registra um sinal visual relatado pelo usuário (ex: mancha de óleo)."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        agora = datetime.now()
        
        # Reutilizando tabela 'intervencoes' ou 'avaliacoes' com tipo especifico
        # Vamos usar 'avaliacoes' pois é um feedback sobre o risco
        
        cursor.execute('''
        INSERT INTO avaliacoes (data_hora, doenca, risco_nivel, comentario)
        VALUES (?, ?, ?, ?)
        ''', (agora, "Míldio", severidade, f"Sinal Visual Detectado: {sinal}. {obs}"))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao registrar sinal visual: {e}")
        return False

# Inicializa ao importar (garante que tabela existe)
init_db()
