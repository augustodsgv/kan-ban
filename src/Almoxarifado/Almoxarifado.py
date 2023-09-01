import paho.mqtt.client as paho
import time
import os
import traceback
import json
from threading import Thread

QTD_F = int(os.getenv('QTD_F'))
QTD_P = int(os.getenv('QTD_P'))

Requisitados = {i:0 for i in range(1,QTD_P+1)}
Estoque = {i:60 for i in range(1,QTD_P+1)}
Pendentes = {i:[] for i in range(1,QTD_P+1)}


Meta_Baixa = 40 #Quantidade de peça objetivo de ser mantida em estoque para cada peça
Meta_Alta = 60

def recebe_peca(msg):
    time.sleep(1)
    peca, qtd = msg.split()[1:]
    peca = int(peca)
    qtd = int(qtd)
    Estoque[peca] += qtd
    Requisitados[peca] -= qtd
    while(Estoque[peca]>0 and len(Pendentes[peca])>0):
        pendente = Pendentes[peca].pop(0)
        send_to_fab(peca,pendente[1],pendente[0])

def send_to_fab(peca,qtd,fab_id):
    peca = int(peca)
    qtd = int(qtd)
    client.publish('Monitor',f"STQ Almoxarifado "+json.dumps(Estoque), qos=1) 
    #Verifica se tem o suficiente para mandar 
    if(Estoque[peca] < qtd):
        Pendentes[peca].append([fab_id, qtd - Estoque[peca]])
        qtd = Estoque[peca]

    #Atualiza valor em estoque
    Estoque[peca] -= qtd
    client.publish(f"Fabrica{fab_id}",f"SEND {peca} {qtd}", qos=1)
    client.publish('Monitor',f"O Almoxarifado enviou {qtd} peças do tipo {peca} para a fabrica {fab_id}", qos=1)

    #Verifica se estoque esta abaixo da meta e pede reposicao
    if(Estoque[peca]+Requisitados[peca] < Meta_Baixa):
        client.publish(f"Fornecedor{(int(peca)-1)//(QTD_P//QTD_F)+1}", f"REQ {peca} {Meta_Alta - (Estoque[peca]+Requisitados[peca])}", qos=1)
        Requisitados[peca] += Meta_Alta - (Estoque[peca]+Requisitados[peca])

def on_publish(client, userdata, mid):
    print("mid: "+str(mid))

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_message(client, userdata, msg):
    try:
        msg = msg.payload.decode('utf-8')
        type_msg = msg.split()[0]

        #Verifica o tipo de requisição
        if(type_msg == 'SEND'): #MSG FORMAT "SEND PEÇA QTD"
            thread = Thread(target=recebe_peca, args=(msg,))
            thread.start()
            return
            
        if(type_msg == 'REQ'): #MSG FORMAT "REQ PEÇA QTD FAB_ID"
            peca, qtd, fab_id = msg.split()[1:]
            peca = int(peca)
            qtd = int(qtd)
            send_to_fab(peca,qtd,fab_id)
            return

        client.publish('Monitor',f"O Almoxarifado não reconheceu a msg", qos=1)
        return

    except Exception as e:
        client.publish('Monitor',"ERRO NO RECEBER DO ALMOXARIFADO:"+traceback.format_exc(), qos=1)

def on_connect(client, userdata, flags, rc):
    print('CONNACK received with code %d.' % (rc))  

try:
    client = paho.Client()
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect('localhost', 1883)
    client.subscribe('Almoxarifado', qos=1)
    
    client.publish('Monitor', "Almoxarifado em operação", qos=1)

    client.loop_forever()

except Exception as e:
    client.publish('Monitor',"ERRO NO ALMOXARIFADO:"+str(e), qos=1)
    
