import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np

 
def controlador_fuzzy(densidade, setpoint):
    # Ajusta o universo de discurso da entrada para melhor resposta
    density = ctrl.Antecedent(np.arange(1.0, 1.4, 0.01), 'density')
    dosagem_agua = ctrl.Consequent(np.arange(4, 21, 1), 'dosagem_agua')
    dosagem_barita = ctrl.Consequent(np.arange(4, 21, 1), 'dosagem_barita')

    # Funções de pertinência para density
    density['muito_baixo'] = fuzz.trimf(density.universe, [1.0, 1.0, setpoint - 0.05])
    density['baixo'] = fuzz.trimf(density.universe, [setpoint - 0.1, setpoint - 0.05, setpoint])
    density['ideal'] = fuzz.trapmf(density.universe, [setpoint - 0.03, setpoint - 0.01, setpoint + 0.01, setpoint + 0.03])
    density['alto'] = fuzz.trimf(density.universe, [setpoint, setpoint + 0.05, setpoint + 0.1])
    density['muito_alto'] = fuzz.trimf(density.universe, [setpoint + 0.05, setpoint + 0.1, 1.4])

    # Funções de pertinência para dosagem
    for var in [dosagem_agua, dosagem_barita]:
        var['nao_dosar'] = fuzz.trapmf(var.universe, [4, 4, 6, 8])
        var['dosar_pouco'] = fuzz.trapmf(var.universe, [6, 8, 10, 12])
        var['dosar_moderadamente'] = fuzz.trapmf(var.universe, [10, 12, 14, 16])
        var['dosar_muito'] = fuzz.trapmf(var.universe, [14, 16, 20, 20])

    # Regras fuzzy
    rules = [
        ctrl.Rule(density['muito_alto'], (dosagem_agua['dosar_muito'], dosagem_barita['nao_dosar'])),
        ctrl.Rule(density['muito_baixo'], (dosagem_barita['dosar_muito'], dosagem_agua['nao_dosar'])),
        ctrl.Rule(density['alto'], (dosagem_agua['dosar_moderadamente'], dosagem_barita['nao_dosar'])),
        ctrl.Rule(density['baixo'], (dosagem_barita['dosar_moderadamente'], dosagem_agua['nao_dosar'])),
        ctrl.Rule(density['ideal'], (dosagem_agua['nao_dosar'], dosagem_barita['nao_dosar']))
    ]

    sistema = ctrl.ControlSystem(rules)
    simulador = ctrl.ControlSystemSimulation(sistema)

    simulador.input['density'] = densidade

    try:
        simulador.compute()
        dos_agua = simulador.output['dosagem_agua']
        dos_barita = simulador.output['dosagem_barita']
    except Exception as e:
        print(f"Erro no controlador fuzzy: {e}")
        dos_agua = 4
        dos_barita = 4

    # Tipo de ação
    if dos_agua > dos_barita:
        tipo = 'A'
    elif dos_barita > dos_agua:
        tipo = 'B'
    else:
        tipo = 'N'

    return dos_agua, dos_barita, tipo

