
# Sistema de Controle de Densidade com PID e Lógica Fuzzy

## Descrição

Este projeto implementa um sistema de controle de densidade para uma planta simulada de preparo de fluido de perfuração de poços de petróleo. A comunicação é realizada via sockets entre um cliente desenvolvido em LabVIEW e um servidor em Python.

O sistema permite a utilização de dois tipos de controladores:

- PID (implementado manualmente, sem uso de bibliotecas)
- Fuzzy (utilizando a biblioteca `scikit-fuzzy`)

O servidor recebe os dados da planta simulada, processa utilizando o controlador selecionado e retorna a ação de controle necessária.

---

## Arquitetura do Sistema

O sistema é composto por três partes principais:

### Cliente (LabVIEW)
- Simula a planta de processo.
- Permite ao usuário definir o setpoint.
- Envia dados ao servidor.
- Recebe e aplica a ação de controle.

### Servidor (Python)
- Recebe os dados via TCP/IP.
- Permite escolher o tipo de controlador (`pid` ou `fuzzy`).
- Processa os dados utilizando os módulos de controle.
- Retorna a resposta ao cliente.

### Módulos de Controle

- `modulo_pid.py`
  - Implementação manual de um controlador PID.
- `modulo_fuzzy.py`
  - Implementação de controle fuzzy com `scikit-fuzzy`.
- `modulo_fuzzypdi.py`
  - Módulo auxiliar relacionado à lógica fuzzy.

---

## Funcionamento

1. O cliente (LabVIEW) envia os dados da planta:
   - Setpoint (definido pelo usuário)
   - Densidade medida na saída da planta simulada
   - Parâmetros do PID (quando aplicável)

2. O servidor:
   - Recebe e interpreta os dados.
   - Permite a escolha do controlador via terminal (`pid` ou `fuzzy`).
   - Executa o cálculo da ação de controle.

3. O servidor retorna:
   - Valor da dosagem (em mA)
   - Tipo de ação (ex: aumento, redução, etc.)

---

## Estrutura do Projeto


.
├── servidor.py
├── modulo_pid.py
├── modulo_fuzzy.py
└── modulo_fuzzypdi.py


---

## Comunicação

- Protocolo: TCP/IP  
- Porta: `2007`  

### Formato dos Dados

#### Cliente PID

O cliente PID envia **5 valores**:


setpoint%densidade%kp%ki%kd


Exemplo:


1.2%1.0%2.0%0.5%0.1


#### Cliente Fuzzy

O cliente Fuzzy envia **2 valores**:


setpoint%densidade


Exemplo:


1.2%1.0
---
## Execução do Cliente (LabVIEW)

O cliente foi desenvolvido em LabVIEW e é responsável por simular a planta de preparo de fluido, enviar dados ao servidor e receber a ação de controle.

### Configuração de Conexão

Para executar o cliente corretamente:

1. Insira o **IP do servidor** (mesmo IP exibido ao iniciar o `servidor.py`).
2. Configure a **porta** como:

2007

3. Garanta que o servidor esteja em execução antes de iniciar o cliente.

---

### Configuração dos Parâmetros

Os parâmetros são definidos diretamente na interface do cliente LabVIEW:

#### Para o Cliente PID
- Setpoint (valor desejado de densidade)
- Densidade inicial (condição da planta simulada)
- Ganhos do controlador:
- Kp
- Ki
- Kd

#### Para o Cliente Fuzzy
- Setpoint
- Densidade inicial

---

### Funcionamento

1. O cliente envia os dados ao servidor conforme o tipo de controlador:
- PID: envia 5 parâmetros (setpoint, densidade, kp, ki, kd)
- Fuzzy: envia 2 parâmetros (setpoint e densidade)

2. O servidor processa os dados e retorna:
- Valor da dosagem (mA)
- Tipo de ação de controle

3. O cliente aplica essa resposta ao modelo da planta simulada.

---

### Simulação em Malha Fechada (Feedback)

O cliente possui um botão que permite:

- Variar o **setpoint dinamicamente** durante a execução.
- Simular o comportamento da densidade em **malha fechada**.

Esse recurso permite analisar respostas típicas de controle do tipo **servo**, como:

- Tempo de subida
- Sobressinal (overshoot)
- Tempo de acomodação
- Erro em regime permanente

A cada alteração no setpoint:
- O sistema reage automaticamente.
- O controlador (PID ou Fuzzy) ajusta a dosagem.
- A densidade evolui conforme o modelo matemático da planta.

---

### Observações

- Certifique-se de que o tipo de cliente (PID ou Fuzzy) corresponde ao controlador escolhido no servidor.
- O sistema funciona em tempo real, dependendo da taxa de envio/recebimento de dados.
- O modelo da planta pode ser ajustado diretamente na interface do LabVIEW para diferentes cenários de teste.
- Os dados são enviados como string.
- O caractere `%` é usado como delimitador.
- O servidor converte automaticamente vírgulas para ponto decimal.

---

## Resposta do Servidor

O servidor retorna uma string contendo:


<dosagem> mA, <tipo>


Exemplo:


10.5 mA, aumento


A resposta é formatada para tamanho fixo de 32 caracteres.

---

## Execução

### Requisitos

- Python 3.x
- Biblioteca `scikit-fuzzy`

Instalação:


pip install scikit-fuzzy


### Executando o Servidor


python servidor.py


O servidor será iniciado no IP local da máquina na porta 2007.

---

## Características

- Comunicação em tempo real via sockets.
- Suporte a múltiplas conexões com threads.
- Implementação de dois tipos de controle:
  - PID clássico
  - Controle Fuzzy
- Integração com LabVIEW.
- Processamento de dados simulados de uma planta industrial.

---

## Aplicações

- Estudo de controle de processos industriais.
- Simulação de sistemas de controle.
- Integração entre LabVIEW e Python.
- Comparação entre controle PID e lógica fuzzy.

---

## Observações Importantes

- Existem **clientes diferentes no LabVIEW**:
  - Um cliente específico para PID (envia 5 parâmetros).
  - Um cliente específico para Fuzzy (envia 2 parâmetros).
- O controlador PID foi implementado manualmente para fins educacionais.
- O controlador Fuzzy utiliza regras linguísticas via `scikit-fuzzy`.

---

## Melhorias Futuras

- Adicionar o cliente PID e fuzzy em código único.
- Melhorar o tratamento de erros.
- Integrar com sistemas reais (sensores e atuadores físicos).

---
