import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np


class FuzzyController:
    def __init__(self):
    # Memória para ação integral
        self.integral_error = 0
        self.last_error = 0
        
        # Definir antecedentes e consequentes
        self.error = ctrl.Antecedent(np.arange(-0.4, 0.41, 0.01), 'error')
        self.derror = ctrl.Antecedent(np.arange(-0.2, 0.21, 0.01), 'derror')
        
        self.dosagem_agua = ctrl.Consequent(np.arange(0, 21, 1), 'dosagem_agua')
        self.dosagem_barita = ctrl.Consequent(np.arange(0, 21, 1), 'dosagem_barita')
        
        # Configurar funções de pertinência
        self._setup_membership_functions()
        self._setup_rules()
        
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulator = ctrl.ControlSystemSimulation(self.control_system)
    
    def _setup_membership_functions(self):
        # Funções de pertinência para erro
        self.error['neg_grande'] = fuzz.trimf(self.error.universe, [-0.4, -0.4, -0.25])
        self.error['neg_medio'] = fuzz.trimf(self.error.universe, [-0.3, -0.2, -0.1])
        self.error['neg_pequeno'] = fuzz.trimf(self.error.universe, [-0.15, -0.08, -0.02])
        self.error['zero'] = fuzz.trimf(self.error.universe, [-0.03, 0, 0.03])
        self.error['pos_pequeno'] = fuzz.trimf(self.error.universe, [0.02, 0.08, 0.15])
        self.error['pos_medio'] = fuzz.trimf(self.error.universe, [0.1, 0.2, 0.3])
        self.error['pos_grande'] = fuzz.trimf(self.error.universe, [0.25, 0.4, 0.4])
        
        # Funções de pertinência para derivada do erro
        self.derror['negativo'] = fuzz.trimf(self.derror.universe, [-0.2, -0.2, 0])
        self.derror['zero'] = fuzz.trimf(self.derror.universe, [-0.05, 0, 0.05])
        self.derror['positivo'] = fuzz.trimf(self.derror.universe, [0, 0.2, 0.2])
        
        # Funções de pertinência para saídas
        self.dosagem_barita['minimo'] = fuzz.trapmf(self.dosagem_barita.universe, [0, 0, 2, 4])
        self.dosagem_barita['baixo'] = fuzz.trapmf(self.dosagem_barita.universe, [2, 4, 6, 8])
        self.dosagem_barita['medio'] = fuzz.trapmf(self.dosagem_barita.universe, [6, 8, 12, 14])
        self.dosagem_barita['alto'] = fuzz.trapmf(self.dosagem_barita.universe, [12, 15, 20, 20])

        self.dosagem_agua['minimo'] = fuzz.trapmf(self.dosagem_agua.universe, [0, 0, 2, 4])
        self.dosagem_agua['baixo'] = fuzz.trapmf(self.dosagem_agua.universe, [2, 4, 6, 8])
        self.dosagem_agua['medio'] = fuzz.trapmf(self.dosagem_agua.universe, [6, 8, 12, 14])
        self.dosagem_agua['alto'] = fuzz.trapmf(self.dosagem_agua.universe, [12, 15, 20, 20])
    
    def _setup_rules(self):
        # Regras baseadas no erro e sua derivada (controlador fuzzy PD-like)
        self.rules = [
            # Quando o erro é negativo (densidade acima do setpoint)
            ctrl.Rule(self.error['neg_grande'] | 
                     (self.error['neg_medio'] & self.derror['negativo']), 
                     (self.dosagem_agua['alto'], self.dosagem_barita['minimo'])),
            
            ctrl.Rule(self.error['neg_medio'] & self.derror['zero'], 
                     (self.dosagem_agua['medio'], self.dosagem_barita['minimo'])),
            
            ctrl.Rule(self.error['neg_medio'] & self.derror['positivo'] | 
                     self.error['neg_pequeno'], 
                     (self.dosagem_agua['baixo'], self.dosagem_barita['minimo'])),
            
            # Quando o erro é próximo de zero
            ctrl.Rule(self.error['zero'] & self.derror['zero'], 
                     (self.dosagem_agua['minimo'], self.dosagem_barita['minimo'])),
            
            ctrl.Rule(self.error['zero'] & self.derror['negativo'], 
                     (self.dosagem_agua['baixo'], self.dosagem_barita['minimo'])),
            
            ctrl.Rule(self.error['zero'] & self.derror['positivo'], 
                     (self.dosagem_agua['minimo'], self.dosagem_barita['baixo'])),
            
            # Quando o erro é positivo (densidade abaixo do setpoint)
            ctrl.Rule(self.error['pos_pequeno'] | 
                     (self.error['pos_medio'] & self.derror['negativo']), 
                     (self.dosagem_agua['minimo'], self.dosagem_barita['medio'])),
            
            ctrl.Rule(self.error['pos_medio'] & self.derror['zero'], 
                     (self.dosagem_agua['minimo'], self.dosagem_barita['alto'])),
            
            ctrl.Rule(self.error['pos_medio'] & self.derror['positivo'] | 
                     self.error['pos_grande'], 
                     (self.dosagem_agua['minimo'], self.dosagem_barita['alto']))
        ]
    
    def calculate(self, set_point, current_value):
        # Calcular erro e derivada do erro
        error = set_point - current_value
        derror = error - self.last_error
        
        # Atualizar integral do erro (ação integral)
        self.integral_error += error
        self.last_error = error
        
        # Limitar a integral para evitar windup
        self.integral_error = max(min(self.integral_error, 0.5), -0.5)
        
        # Configurar entradas do controlador fuzzy
        self.simulator.input['error'] = error + 0.1 * self.integral_error  # Adicionar ação integral
        self.simulator.input['derror'] = derror
        
        try:
            self.simulator.compute()
            dos_agua = self.simulator.output['dosagem_agua']
            dos_barita = self.simulator.output['dosagem_barita']
            
            # Determinar qual dosagem é maior
            if dos_agua > dos_barita:
                return round(dos_agua, 1), 'A'
            else:
                return round(dos_barita, 1), 'B'
                
        except Exception as e:
            print(f"Erro no controlador fuzzy: {e}")
            return None, "aceitavel"

# Criar instância global do controlador
fuzzy_controller = FuzzyController()

def calcular_dosagem(set_point, valor_densidade):
    return fuzzy_controller.calculate(set_point, valor_densidade)

