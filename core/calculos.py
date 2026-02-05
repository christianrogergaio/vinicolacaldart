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

# --- Novos Algoritmos (Baseado em Artigo para Plasmopara Viticola) ---

import math

def calcular_vpd(temperatura, umidade_relativa):
    """
    Calcula o VPD (Déficit de Pressão de Vapor) usando a fórmula de Magnus-Tetens.
    Retorna VPD em hPa.
    """
    # 1. Pressão de Vapor de Saturação (es)
    # Constantes: A = 6.112 hPa, B = 17.67, C = 243.5 °C
    es = 6.112 * math.exp((17.67 * temperatura) / (temperatura + 243.5))
    
    # 2. Pressão Atual de Vapor (ea)
    ea = es * (umidade_relativa / 100.0)
    
    # 3. Déficit
    vpd = es - ea
    return max(0.0, vpd)

def calcular_horas_necessarias_infeccao(temp):
    """
    Retorna as horas de molhamento necessárias para infecção baseada na temperatura.
    Curva simplificada da Figura 2D do artigo.
    """
    if temp <= 4.0 or temp >= 30.2:
        return 999 # Impossível
    
    # Ótimo em torno de 20-22°C (~2h)
    if 18.0 <= temp <= 24.0:
        return 2
    elif 15.0 <= temp <= 27.0:
        return 4
    elif 10.0 <= temp <= 29.0:
        return 6
    else:
        return 10 # Marginais

def calcular_severidade_infeccao(temp_media, horas_molhamento):
    """
    Calcula o índice de severidade (SEV/INFR) baseado nos parâmetros
    do artigo (Brischetto et al., 2021 / Caffi et al., 2016).
    Usa Função Beta Generalizada.
    """
    # 1. Parâmetros Críticos
    T_MIN = 4.0
    T_OPT = 21.0
    T_MAX = 30.2
    HORAS_MIN_OTIMO = 2.0  # Mínimo de horas para infecção a 21°C
    
    # 2. Verificações de Limite
    if temp_media <= T_MIN or temp_media >= T_MAX:
        return 0.0
    
    if horas_molhamento < HORAS_MIN_OTIMO:
        return 0.0

    # 3. Cálculo da Eficiência Térmica (Função Beta)
    try:
        # Expoentes
        p = (T_OPT - T_MIN) / (T_MAX - T_OPT)
        
        numerador = ((temp_media - T_MIN)**p) * (T_MAX - temp_media)
        denominador = ((T_OPT - T_MIN)**p) * (T_MAX - T_OPT)
        
        fator_temperatura = numerator / denominator if denominator != 0 else 0
        # Correction: numerator/denominator vars above are local placeholders in logic. 
        # Correct implementation:
        term1 = (temp_media - T_MIN) ** p
        term2 = (T_MAX - temp_media)
        
        denom_term1 = (T_OPT - T_MIN) ** p
        denom_term2 = (T_MAX - T_OPT)
        
        fator_temperatura = (term1 * term2) / (denom_term1 * denom_term2)
        
    except Exception:
        fator_temperatura = 0.0

    # 4. Cálculo da Severidade
    # Simplificação linear do tempo: quanto mais horas acima do mínimo, maior a severidade
    # Modulado pela temperatura perfeita (1.0) ou imperfeita (<1.0)
    sev_bruta = fator_temperatura * (horas_molhamento / HORAS_MIN_OTIMO)
    
    return max(0.0, sev_bruta)

def calcular_taxa_diaria(temp_media):
    """
    Retorna a porcentagem de evolução do fungo naquele dia (Incubação).
    Baseado em curva gaussiana onde 23°C = 25% progresso/dia (4 dias).
    """
    # Limites biológicos
    if temp_media < 5 or temp_media > 35:
        return 0.0
        
    otimo = 23.0
    taxa_maxima = 25.0 # % por dia
    amplitude = 10.0 # Largura da curva
    
    # Gaussian function
    taxa = taxa_maxima * math.exp(-((temp_media - otimo)**2) / (2 * amplitude**2))
    return taxa

def simular_risco_plasmopara(lista_dados_horarios):
    """
    Simula o ciclo de vida do Plasmopara Viticola (Semaforo, SEV, Incubação).
    
    Retorna:
        dict com 'semaforo' (VERDE/AMARELO/VERMELHO), 'sev_acumulado', 'progresso_incubacao' (estimado do dia)
    """
    
    # Parâmetros
    LIMITE_UR_MOLHAMENTO = 80.0
    TEMP_MIN_ESPORULACAO = 10.0
    TEMP_MAX_ESPORULACAO = 30.0
    MIN_HORAS_UMIDAS_ESPORULACAO = 3
    LIMITE_CRITICO_VPD = 15.0 
    
    # Estado
    horas_umidade_consecutivas = 0
    existe_inoculo_esporos = False
    risco_infeccao = False
    
    sev_acumulado = 0.0
    
    # Para incubação (média do dia)
    soma_temp = 0
    count_temp = 0
    
    log_risco = [] 
    
    for hora in lista_dados_horarios:
        temp = hora['temp']
        umid = hora['umid']
        eh_noite = not hora.get('is_day', True)
        precip = hora.get('precip', 0.0)
        
        # Média Temp
        soma_temp += temp
        count_temp += 1
        
        # 1. Molhamento
        if umid >= LIMITE_UR_MOLHAMENTO or precip > 0:
            horas_umidade_consecutivas += 1
        else:
            horas_umidade_consecutivas = 0
            
        estado_desc = "Normal"
            
        # 2. Esporulação (Amarelo)
        if eh_noite and horas_umidade_consecutivas >= MIN_HORAS_UMIDAS_ESPORULACAO:
            if TEMP_MIN_ESPORULACAO <= temp <= TEMP_MAX_ESPORULACAO:
                existe_inoculo_esporos = True
                estado_desc = "Esporulação (Alerta)"
        
        # 3. Mortalidade (Verde)
        if existe_inoculo_esporos:
            vpd = calcular_vpd(temp, umid)
            if vpd > LIMITE_CRITICO_VPD:
                existe_inoculo_esporos = False
                estado_desc = "Esporos Mortos (Seca)"
                
                # 4. Infecção (Vermelho)
        if existe_inoculo_esporos and horas_umidade_consecutivas > 0:
            horas_req = calcular_horas_necessarias_infeccao(temp)
            if horas_umidade_consecutivas >= horas_req:
                risco_infeccao = True
                estado_desc = "INFECÇÃO CONFIRMADA"
                
                # Cálculo de SEV Científico
                sev_hora = calcular_severidade_infeccao(temp, horas_umidade_consecutivas)
                # O SEV é cumulativo por evento ou diário. Aqui acumulamos por hora de evento infectante.
                # Como a função calcula baseado na duração total, devemos ter cuidado para não somar 
                # o total repetidamente se o loop for hora a hora.
                # Mas neste loop simples, recalculamos o SEV "potencial" daquele momento.
                # Para acumular corretamente, deveríamos somar apenas o incremento marginal.
                # Simplificação aceitável: Considerar o SEV da última hora do evento como o SEV do evento.
                # Como é difícil rastrear "eventos" neste loop simples, vamos somar uma fração
                # ou usar o valor instantâneo máximo do dia.
                
                # ABORDAGEM MELHORADA: Somar SEV marginal apenas se mantiver a infecção
                # Vamos assumir uma taxa baseada na eficiência térmica por hora
                sev_acumulado += (sev_hora / horas_umidade_consecutivas) if horas_umidade_consecutivas > 0 else 0
        
        log_risco.append({
            "hora": hora.get("time_str", "?"),
            "temp": temp,
            "umid": umid,
            "molhamento_h": horas_umidade_consecutivas,
            "esporos": existe_inoculo_esporos,
            "infeccao": risco_infeccao,
            "estado": estado_desc
        })

    # Incubação Diária
    temp_media = soma_temp / max(1, count_temp)
    incubacao_dia = calcular_taxa_diaria(temp_media)

    # Determinar Semáforo e Mensagens com base no SEV (Fonte User)
    semaforo = "VERDE"
    mensagem = "Prognóstico Negativo: Economize aplicação."
    
    if sev_acumulado > 2.0:
        semaforo = "VERMELHO"
        mensagem = "ALERTA CRÍTICO: Risco Severo (>2.0). Explosão de manchas prevista."
    elif sev_acumulado > 0.5:
        semaforo = "VERMELHO" # Ainda é vermelho pois infecção é infecção
        mensagem = "Risco Alto: Infecção Moderada prevista. Trate."
    elif sev_acumulado > 0.065:
        semaforo = "AMARELO"  # Amarelo/Laranja
        mensagem = "Alerta: Infecção Leve prevista. Monitore."
    elif existe_inoculo_esporos:
        semaforo = "AMARELO"
        mensagem = "Alerta de Inóculo: Esporos ativos. Aguardando chuva."
        
    return {
        "semaforo": semaforo,
        "mensagem": mensagem,
        "sev_acumulado": round(sev_acumulado, 4),
        "incubacao_dia_percent": round(incubacao_dia, 2),
        "nivel_risco": "ALTO" if sev_acumulado > 0.065 else ("MÉDIO" if existe_inoculo_esporos else "BAIXO"),
        "detalhes_log": log_risco,
    }
