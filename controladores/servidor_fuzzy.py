# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 19:21:37 2026

@author: pinhe
"""
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np
import socket
import threading
 
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


HOST = '10.52.81.106'
PORT = 2007

def handle_client(conn, addr):
    print(f'Conectado ao LabVIEW: {addr}')

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
                    set_point_str, density_str = data.split('%')[:2]
                    set_point = float(set_point_str)
                    density_value = float(density_str)

                    # Usa o controlador fuzzy
                    dos_agua, dos_barita, tipo = controlador_fuzzy(density_value, set_point)

                    resposta = f"Agua: {dos_agua:.1f} mA | Barita: {dos_barita:.1f} mA | Tipo: {tipo}"

                except ValueError:
                    resposta = "dado invalido"
                except Exception as e:
                    print(f"Erro durante o cálculo: {e}")
                    resposta = "erro interno"

            resposta_formatada = resposta.ljust(64)[:64]
            conn.sendall(resposta_formatada.encode())
            print(f"Resposta enviada: {resposta}")
            print(f"Densidade recebida: {density_value}")

        except Exception as e:
            print(f"Erro: {e}")
            break
    conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Servidor Fuzzy iniciado em {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.daemon = True
            client_thread.start()

# Execução principal
if __name__ == "__main__":
    start_server()
