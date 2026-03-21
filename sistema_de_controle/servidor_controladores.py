
import socket
import threading
import modulo_pid
import modulo_fuzzy
import modulo_fuzzypdi

hostname = socket.gethostname()
HOST = socket.gethostbyname(hostname)
PORT = 2007

def handle_client(conn, addr):
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
                controlador =  input('escolha um controlador(fuzzy ou pid): ')
                if controlador == 'pid':
                    try:
                        set_point_str, density_str, kc_str, ki_str, kd_str = data.split('%')[:5]
                        set_point = float(set_point_str)
                        density_value = float(density_str)
                        kc_value = float(kc_str)
                        ki_value = float(ki_str)
                        kd_value = float(kd_str)

                        if pid is None:
                            pid = modulo_pid.PIDController(kc_value, ki_value, kd_value)

                        dosagem, tipo = pid.calcular_dosagem(set_point, density_value)

                        if dosagem is None:
                            resposta = "Densidade aceitavel"
                        else:
                            resposta = f"{dosagem:.1f} mA,{tipo}"
                    except ValueError:
                        resposta = "dado invalido"
                    except Exception as e:
                        print(f"Erro durante o cálculo: {e}")
                        resposta = "erro interno"
                elif controlador =='fuzzy'  :
                    
                    try:
                        set_point_str, density_str = data.split('%')[:2]
                        set_point = float(set_point_str)
                        density_value = float(density_str)

                        # Usa o controlador fuzzy
                        dos_agua, dos_barita, tipo = modulo_fuzzy.controlador_fuzzy(density_value, set_point)
                        dosagem = max(dos_agua, dos_barita)
                        resposta = f"{dosagem} mA , {tipo}"

                    except ValueError:
                        resposta = "dado invalido"
                    except Exception as e:
                        print(f"Erro durante o cálculo: {e}")
                        resposta = "erro interno"
                        
                else: 
                    print('escolha invalida')
                    

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