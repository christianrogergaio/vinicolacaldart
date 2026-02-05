
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core import calculos

def print_scenario_result(name, result):
    print(f"\n--- Cenário: {name} ---")
    print(f"Risco Final: {result['nivel_risco']}")
    print(f"Infectado: {result['infected']}")
    print(f"Esporos Vivos: {result['spores_alive']}")
    
    print("\nLog Detalhado (Últimas 8 horas):")
    for log in result['detalhes_log'][-8:]:
        print(f"  {log['hora']}: T={log['temp']}°C, U={log['umid']}%, Molh={log['molhamento_h']}h, Estado={log['estado']}")

def run_tests():
    print("Iniciando Simulação de Risco - Plasmopara Viticola")

    # --- Cenário 1: Condições Perfeitas (Esporulação Noturna + Infecção Imediata) ---
    # Noite: 20°C, 90% (4 horas) -> Esporula
    # Dia Seguinte: Continua úmido/chuva -> Infecta
    print("\n[TESTE 1] Esporulação Noturna + Chuva Pela Manhã")
    dados_cenario_1 = []
    
    # 4 horas de noite úmida
    for h in range(4):
        dados_cenario_1.append({"time_str": f"Noite_{h}h", "temp": 20, "umid": 90, "is_day": 0})
        
    # 4 horas de dia chuvoso (tão úmido quanto)
    for h in range(4):
        dados_cenario_1.append({"time_str": f"Dia_{h}h", "temp": 22, "umid": 95, "is_day": 1})

    res1 = calculos.simular_risco_plasmopara(dados_cenario_1)
    print_scenario_result("Infecção Provável", res1)


    # --- Cenário 2: Mortalidade (Esporula mas morre com sol forte) ---
    # Noite: Úmida (Esporula)
    # Dia: Sol forte, Umidade baixa (VPD Alto) -> Morte
    print("\n[TESTE 2] Esporulação seguida de Sol Forte")
    dados_cenario_2 = []
    
    # 4 horas de noite úmida
    for h in range(4):
        dados_cenario_2.append({"time_str": f"Noite_{h}h", "temp": 20, "umid": 90, "is_day": 0})
        
    # 3 horas de dia seco e quente (30°C, 40% UR)
    for h in range(3):
        dados_cenario_2.append({"time_str": f"DiaSeco_{h}h", "temp": 30, "umid": 40, "is_day": 1})

    res2 = calculos.simular_risco_plasmopara(dados_cenario_2)
    print_scenario_result("Mortalidade de Esporos", res2)


    # --- Cenário 3: Noite Seca (Sem Esporulação) ---
    print("\n[TESTE 3] Noite Seca = Sem Risco")
    dados_cenario_3 = []
    
    # Noite seca
    for h in range(5):
        dados_cenario_3.append({"time_str": f"NoiteSeca_{h}h", "temp": 15, "umid": 60, "is_day": 0})
        
    # Dia seguinte chove, mas não adianta pois não houve esporulação prévia
    for h in range(3):
        dados_cenario_3.append({"time_str": f"DiaChuva_{h}h", "temp": 20, "umid": 90, "is_day": 1})

    res3 = calculos.simular_risco_plasmopara(dados_cenario_3)
    print_scenario_result("Sem Inóculo Inicial", res3)


if __name__ == "__main__":
    run_tests()
