import os
import paho.mqtt.client as paho
import time
import traceback
import json
import random
import asyncio
from threading import Thread

FAB_ID = os.getenv('FAB_ID')
ID = os.getenv('ID')
QTD_P = int(os.getenv('QTD_P'))
QTD_P_FIX = int(os.getenv('QTD_P_FIX'))
QTD_P_VAR = int(os.getenv('QTD_P_VAR'))
QTD_P_OFF = int(os.getenv('QTD_P_OFF'))

Requisitados = {i:0 for i in range(1,QTD_P+1)}
Estoque = {i:15 for i in range(1,QTD_P+1)}
Meta_Baixa = 10 #Quantidade de peça objetivo de ser mantida em estoque para cada peça
Meta_Alta = 15

def recebe_peca(msg):
    time.sleep(1)
    peca, qtd = msg.split()[1:]
    peca = int(peca)
    qtd = int(qtd)
    Estoque[peca] += qtd
    Requisitados[peca] -= qtd
    #client.publish('Monitor',f"STQ Linha_{FAB_ID}_{ID} "+json.dumps(Estoque), qos=1) 


# Função para sortear 10 números únicos no intervalo de 43 a 100
def sortear_numeros_unicos(qtd_numeros, min_valor, max_valor):
    if qtd_numeros > (max_valor - min_valor + 1):
        raise ValueError("Impossível sortear essa quantidade de números únicos neste intervalo.")
    
    numeros_sorteados = set()
    while len(numeros_sorteados) < qtd_numeros:
        numero = random.randint(min_valor, max_valor)
        numeros_sorteados.add(numero)
    
    return list(numeros_sorteados)

def on_publish(client, userdata, mid):
    print("mid: "+str(mid))

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_message(client, userdata, msg):
    try:
        msg = msg.payload.decode('utf-8')
        #client.publish('Monitor',f"O Fornecedor{ID} recebeu a msg:{msg}", qos=1)
        type_msg = msg.split()[0]

        #Verifica o tipo de requisição
        if(type_msg == 'SEND'): #MSG FORMAT "SEND PEÇA QTD"
            thread = Thread(target=recebe_peca, args=(msg,))
            thread.start()
            return

        client.publish('Monitor',f"A Linha não reconheceu a msg", qos=1)
        return

    except Exception as e:
        client.publish('Monitor',"ERRO NO RECEBER DA LINHA:"+traceback.format_exc(), qos=1) 

def on_connect(client, userdata, flags, rc):
    print('CONNACK received with code %d.' % (rc))  

try:
    client = paho.Client()
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect('localhost', 1883)
    client.subscribe(f"Linha_{FAB_ID}_{ID}", qos=1)
    
    def loop_forever():
        client.loop_forever()

    thread = Thread(target=loop_forever)
    thread.start()

    def async_forever():
       loop.run_forever()

    loop = asyncio.get_event_loop()
    thread2 = Thread(target=async_forever)
    thread2.start()

    peca_list = [i for i in range(1,QTD_P_FIX+1)]
    peca_list = peca_list + sortear_numeros_unicos(QTD_P_VAR, QTD_P_FIX+1, QTD_P)

    time.sleep(2)
    client.publish('Monitor',"Linha "+ID+" da fabrica "+FAB_ID+" em operação", qos=1)
    time.sleep(1)

    #Balanceando Estoque
    for key,value in Estoque.items():
        if(value < Meta_Baixa):
            client.publish(f"Fabrica{FAB_ID}", f"REQ {key} {Meta_Alta-value} {ID}", qos=1)
            Requisitados[key] += Meta_Alta-value

    #Produzindo
    while(True):
        # Gera um atraso aleatório entre 1 e 5 segundos
        tempo_aleatorio = random.random() * 4 + 1
        time.sleep(tempo_aleatorio)

        for j in range(random.randint(1, 10)):
            for i in peca_list:
                while(Estoque[i] <= 0):
                    pass
                Estoque[i] -= 1
                
                if(Estoque[i]+Requisitados[i] < Meta_Baixa):
                    client.publish(f"Fabrica{FAB_ID}", f"REQ {i} {Meta_Alta-(Estoque[i]+Requisitados[i])} {ID}", qos=1)
                    Requisitados[i] += Meta_Alta-(Estoque[i]+Requisitados[i])
            client.publish('Monitor',f"STQ Linha_{FAB_ID}_{ID} "+json.dumps(Estoque), qos=1) 
            time.sleep(0.5)
        pass
except Exception as e:
        client.publish('Monitor',"ERRO NA LINHA:"+traceback.format_exc(), qos=1) 