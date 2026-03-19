
class PIDController:
    
    def __init__(self, kc, ki, kd):
        self.kc = kc
        self.ki = ki
        self.kd = kd
        self.integral = 0
        self.erro_anterior = 0

    def calcular_dosagem(self, set_point, valor_densidade):
        erro = set_point - valor_densidade
        self.integral += erro
        derivativo = erro - self.erro_anterior

        P = self.kc * erro
        I = self.ki * self.integral
        D = self.kd * derivativo

        acao_controle = P + I + D
        self.erro_anterior = erro
        
        if abs(erro) < 0.01:
            return None, None

        tipo = 'B' if acao_controle > 0 else 'A'
        dosagem = abs(acao_controle)
        return dosagem, tipo

