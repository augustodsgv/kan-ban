import os
import paho.mqtt.client as paho
import time
import traceback
import json
from threading import Thread

ID = os.getenv('ID')
QTD_P = int(os.getenv('QTD_P'))

Requisitados = {i:0 for i in range(1,QTD_P+1)}
Estoque = {i:30 for i in range(1,QTD_P+1)}
Pendentes = {i:[] for i in range(1,QTD_P+1)}
Meta_Baixa = 20 #Quantidade de peça objetivo de ser mantida em estoque para cada peça
Meta_Alta = 30

def recebe_peca(msg):
    time.sleep(1)
    peca, qtd = msg.split()[1:]
    peca = int(peca)
    qtd = int(qtd)
    Estoque[peca] += qtd
    Requisitados[peca] -= qtd
    while(Estoque[peca]>0 and len(Pendentes[peca])>0):
        pendente = Pendentes[peca].pop(0)
        send_to_line(peca,pendente[1],pendente[0])

def send_to_line(peca,qtd,line_id):
    peca = int(peca)
    qtd = int(qtd)
    client.publish('Monitor',f"STQ Fabrica{ID} "+json.dumps(Estoque), qos=1) 
    #Verifica se tem o suficiente para mandar
    if(Estoque[peca] < qtd):
        Pendentes[peca].append([line_id, qtd - Estoque[peca]])
        qtd = Estoque[peca]

    #Atualiza valor em estoque
    Estoque[peca] -= qtd
    client.publish(f"Linha_{ID}_{line_id}",f"SEND {peca} {qtd}", qos=1)
    client.publish('Monitor',f"A Fabrica {ID} enviou {qtd} peças do tipo {peca} para a linha {line_id}", qos=1)

    #Verifica se estoque esta abaixo da meta e pede reposicao
    if(Estoque[peca]+Requisitados[peca] < Meta_Baixa):
        client.publish(f"Almoxarifado", f"REQ {peca} {Meta_Alta - (Estoque[peca]+Requisitados[peca])} {ID}", qos=1)
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
            
        if(type_msg == 'REQ'): #MSG FORMAT "REQ PEÇA QTD LINE_ID"
            peca, qtd, line_id = msg.split()[1:]
            peca = int(peca)
            qtd = int(qtd)
            send_to_line(peca,qtd,line_id)
            return

        client.publish('Monitor',f"A Fabrica não reconheceu a msg", qos=1)
        return

    except Exception as e:
        client.publish('Monitor',"ERRO NO RECEBER DA FABRICA:"+traceback.format_exc(), qos=1)

def on_connect(client, userdata, flags, rc):
    print('CONNACK received with code %d.' % (rc))  

client = paho.Client()
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_connect = on_connect
client.on_publish = on_publish
client.connect('localhost', 1883)
client.subscribe(f"Fabrica{ID}", qos=1)

client.publish('Monitor',"Fabrica "+ID+" em operação", qos=1)

client.loop_forever()