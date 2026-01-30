# Fatores de Suscetibilidade por Estádio Fenológico
# Multiplicador que ajusta o VDS base.
# > 1.0: Aumenta o risco (estádio crítico)
# < 1.0: Diminui o risco (estádio resistente)
FATORES_FENOLOGICOS = {
    "videira": {
        "míldio": {
            "Dormência": 0.1, "Brotamento (EL 4-6)": 1.5, "Floração (EL 19-25)": 2.0, 
            "Frutificação (EL 27-33)": 1.5, "Veraison (Maturação)": 0.5, "Pós-colheita": 0.2
        },
        "oídio": {
            "Dormência": 0.1, "Brotamento (EL 4-6)": 0.8, "Floração (EL 19-25)": 2.0,
            "Frutificação (EL 27-33)": 1.8, "Veraison (Maturação)": 0.5, "Pós-colheita": 0.2
        },
        "botrytis": {
            "Dormência": 0.1, "Brotamento (EL 4-6)": 0.5, "Floração (EL 19-25)": 1.5,
            "Frutificação (EL 27-33)": 1.2, "Veraison (Maturação)": 2.0, "Pós-colheita": 0.2
        },
        "antracnose": {
            "Dormência": 0.1, "Brotamento (EL 4-6)": 1.5, "Floração (EL 19-25)": 1.2,
            "Frutificação (EL 27-33)": 1.0, "Veraison (Maturação)": 0.5, "Pós-colheita": 0.2
        }
    },
    "tomateiro": {
        "requeima": {
            "Germinação/Plântula": 1.0, "Vegetativo": 1.0, "Floração": 1.2,
            "Frutificação (Verde)": 1.5, "Maturação (Vermelho)": 1.5, "Senescência": 0.1
        },
        "pinta preta": {
            "Germinação/Plântula": 0.8, "Vegetativo": 1.0, "Floração": 1.0,
            "Frutificação (Verde)": 1.5, "Maturação (Vermelho)": 1.5, "Senescência": 0.1
        },
        "botrytis": {
            "Germinação/Plântula": 0.5, "Vegetativo": 1.0, "Floração": 1.2,
            "Frutificação (Verde)": 1.5, "Maturação (Vermelho)": 1.8, "Senescência": 0.1
        }
    },
    "cannabis": {
        "botrytis": {
            "Plântula/Clones": 0.2, "Vegetativo Inicial": 0.2, "Vegetativo Tardio": 0.5,
            "Floração Inicial": 1.2, "Floração Tardia (Maturação)": 2.5, "Secagem/Cura": 1.0
        },
         "requeima": {
            "Plântula/Clones": 1.0, "Vegetativo Inicial": 1.0, "Vegetativo Tardio": 1.0,
            "Floração Inicial": 1.2, "Floração Tardia (Maturação)": 1.2, "Secagem/Cura": 0.1
        },
        "pinta preta": {
             "Plântula/Clones": 1.0, "Vegetativo Inicial": 1.0, "Vegetativo Tardio": 1.0,
            "Floração Inicial": 1.0, "Floração Tardia (Maturação)": 1.0, "Secagem/Cura": 0.1
        }
    },
    "soja": {
        "ferrugem asiática": {
            "VE (Emergência)": 0.5, "VC (Cotilédone)": 0.5, "V1-Vn (Vegetativo)": 1.0,
            "R1 (Início Floração)": 2.0, "R2 (Floração Plena)": 2.0,
            "R3-R4 (Formação Vagem)": 2.5, "R5 (Enchimento Grão)": 2.5, "R8 (Maturação Plena)": 0.1
        },
        "antracnose": {
            "VE (Emergência)": 0.8, "VC (Cotilédone)": 0.8, "V1-Vn (Vegetativo)": 1.0,
            "R1 (Início Floração)": 1.5, "R2 (Floração Plena)": 1.5,
            "R3-R4 (Formação Vagem)": 2.0, "R5 (Enchimento Grão)": 2.0, "R8 (Maturação Plena)": 0.2
        }
    }
}

def calcular_gdd(temp_max, temp_min, temp_base):
    """
    Calcula Graus-Dia (GDD).
    Fórmula simples: ((Tmax + Tmin) / 2) - Tbase
    Se a média for menor que Tbase, GDD = 0.
    """
    media = (temp_max + temp_min) / 2
    gdd = media - temp_base
    return max(gdd, 0)

def obter_fator_fenologico(doenca, planta, estadio):
    """Retorna o multiplicador de risco para a combinação."""
    try:
        fator = FATORES_FENOLOGICOS[planta.lower()][doenca.lower()][estadio]
        return fator
    except (KeyError, AttributeError):
        return 1.0 # Padrão se não encontrar

def calcular_vds_numerico(temp, umid, doenca, planta, estadio="Frutificação"):
    """
    Calcula o Valor Diário de Severidade (VDS) numérico ajustado pela fenologia.
    Retorna valor corrigido (pode ser > 1.0 se estádio for crítico).
    """
    doenca_low = doenca.lower()
    planta_low = planta.lower()
    vds_base = 0.0

    if planta_low == "videira":
        if doenca_low == "míldio":
            if not (18 <= temp <= 25):
                vds_base = 0
            elif umid >= 85:
                vds_base = 1.0
            elif 75 <= umid < 85:
                vds_base = 0.5
            elif 60 <= umid < 75:
                vds_base = 0.25
        
        elif doenca_low == "oídio":
            vds_base = 1.0 if (23 <= temp <= 27 and 40 <= umid <= 60) else 0.0
        elif doenca_low == "botrytis":
            vds_base = 1.0 if (temp < 20 and umid > 90) else 0.0
        elif doenca_low == "antracnose":
            vds_base = 1.0 if (24 <= temp <= 28 and umid >= 85) else 0.0

    elif planta_low == "tomateiro":
        if doenca_low == "requeima":
            vds_base = 1.0 if (16 <= temp <= 22 and umid >= 85) else 0.0
        elif doenca_low == "pinta preta":
            vds_base = 1.0 if (24 <= temp <= 30 and umid >= 80) else 0.0
        elif doenca_low == "botrytis":
            vds_base = 1.0 if (17 <= temp <= 22 and umid >= 85) else 0.0

    elif planta_low == "cannabis":
        if doenca_low == "requeima":
            vds_base = 1.0 if (16 <= temp <= 22 and umid >= 85) else 0.0
        elif doenca_low == "pinta preta":
            vds_base = 1.0 if (24 <= temp <= 30 and umid >= 80) else 0.0
        elif doenca_low == "botrytis":
            vds_base = 1.0 if (17 <= temp <= 26 and umid > 80) else 0.0

    elif planta_low == "soja":
        if doenca_low == "ferrugem asiática":
            # Ferrugem: Crítico 18-26C e molhamento foliar (Umid > 90% como proxy)
            vds_base = 1.0 if (18 <= temp <= 26 and umid >= 90) else 0.0
        elif doenca_low == "antracnose":
             # Antracnose: Gosta de calor e umidade alta
            vds_base = 1.0 if (23 <= temp <= 30 and umid >= 85) else 0.0

    # Aplica o fator fenológico
    fator = obter_fator_fenologico(doenca, planta, estadio)
    return round(vds_base * fator, 2)

def calcular_vds_complexo_mildio(temp_media, umid_media, horas_umidade_alta):
    """
    Calcula o risco de míldio baseado na persistência da umidade (Sugestão Gemini/User).
    horas_umidade_alta: contador de horas consecutivas com UR > 85%
    """
    vds_base = 0.0
    
    # Faixa de temperatura ótima para Plasmopara viticola
    if 18 <= temp_media <= 25:
        # Se a umidade persistir por muito tempo, o risco dispara
        if horas_umidade_alta >= 12:
            vds_base = 1.0  # Infecção provável
        elif horas_umidade_alta >= 6:
            vds_base = 0.6  # Risco moderado
        elif horas_umidade_alta >= 3:
            vds_base = 0.3  # Alerta inicial
    elif 10 <= temp_media < 18:
        # Em temperaturas baixas, precisa de muito mais tempo de molhamento
        if horas_umidade_alta >= 15:
            vds_base = 0.5
    
    # Ajuste simples se a umidade média do dia for extrema (safe guard)
    if umid_media > 95 and temp_media > 20:
        vds_base = max(vds_base, 0.8)
            
    return vds_base

def calcular_nivel_risco_imediato(temperatura, umidade, doenca, planta, estadio="Frutificação", horas_molhamento=6):
    """
    Calcula risco qualitativo considerando fenologia.
    Se o VDS Base for alto E o estádio for crítico, o risco é exacerbado.
    """
    # Usa o VDS numérico como proxy para simplificar, já que ele já considera os fatores
    vds_ajustado = calcular_vds_numerico(temperatura, umidade, doenca, planta, estadio)
    
    # Limiares arbitrários baseados no multiplicador
    # Se VDS Base for 1.0 e Fator for 1.5 (crítico) -> 1.5 -> ALTO
    # Se VDS Base for 0.5 e Fator for 0.5 (resistente) -> 0.25 -> BAIXO
    
    if vds_ajustado >= 0.8:
        return "ALTO"
    elif vds_ajustado >= 0.4:
        return "MODERADO"
    else:
        return "BAIXO"

def classificar_risco_por_vds_acumulado(vds_total):
    """
    Retorna (Nivel, Cor) baseado no VDS acumulado.
    """
    if vds_total >= 10:
        return "RISCO SEVERO", "red"
    elif vds_total >= 6:
        return "RISCO MODERADO", "orange"
    elif vds_total >= 3:
        return "RISCO LEVE", "blue"
    else:
        return "SEM RISCO", "green"

REGRAS_DESCRITIVAS = {
    "Videira - Míldio": [
        ("18–25°C", "≥ 85%", "1.0", "Condições ideais"),
        ("18–25°C", "75–84%", "0.5", "Favorável"),
        ("18–25°C", "60–74%", "0.25", "Possível infecção leve"),
        ("Fora da faixa", "< 60%", "0", "Sem risco"),
    ],
    "Videira - Oídio": [
        ("23–27°C", "40–60%", "1", "Alta suscetibilidade"),
    ],
    "Videira - Botrytis": [
        ("< 20°C", "> 90%", "1", "Alta suscetibilidade"),
    ],
    "Videira - Antracnose": [
        ("24–28°C", "≥ 85%", "1", "Alta suscetibilidade"),
    ],
    "Tomateiro - Requeima": [
        ("16–22°C", "≥ 85%", "1", "Alta suscetibilidade"),
    ],
    "Tomateiro - Pinta Preta": [
        ("24–30°C", "≥ 80%", "1", "Alta suscetibilidade"),
    ],
    "Tomateiro - Botrytis": [
        ("17–22°C", "≥ 85%", "1", "Alta suscetibilidade"),
    ]
}
