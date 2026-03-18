# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 19:14:31 2026

@author: pinhe
"""

i+mport socket
import threading
 
class PIDController:
    #
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

# Configurações do servidor
HOST = '10.52.81.106'
PORT = 2007

+def handle_client(conn, addr):
    print(f'Conectado ao LabVIEW: {addr}')
    pid = None  # Inicializa fora do loop

    while True:
        try:
            data_bytes = conn.recv(50)
            if not data_bytes:
                break

            data = data_bytes.decode().strip().replace(',', '.')
            if '%' not in data:
                resposta = "dado invalido"
            else:
                try:
                    set_point_str, density_str, kc_str, ki_str, kd_str = data.split('%')[:5]
                    set_point = float(set_point_str)
                    density_value = float(density_str)
                    kc_value = float(kc_str)
                    ki_value = float(ki_str)
                    kd_value = float(kd_str)

                    if pid is None:
                        pid = PIDController(kc_value, ki_value, kd_value)

                    dosagem, tipo = pid.calcular_dosagem(set_point, density_value)

                    if dosagem is None:
                        resposta = "Densidade aceitavel"
                    else:
                        resposta = f"{dosagem:.1f} mA, Tipo: {tipo}"
                except ValueError:
                    resposta = "dado invalido"
                except Exception as e:
                    print(f"Erro durante o cálculo: {e}")
                    resposta = "erro interno"

            resposta_formatada = resposta.ljust(32)[:32]
            conn.sendall(resposta_formatada.encode())
            print(f"Resposta enviada: {resposta}")
            print(f"Densidade enviada: {density_value}")

        except Exception as e:
            print(f"Erro: {e}")
            break
    conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Servidor PID iniciado em {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.daemon = True
            client_thread.start()

# Execução principal
if __name__ == "__main__":
    start_server()