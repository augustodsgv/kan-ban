import os
import paho.mqtt.client as paho
import time
import traceback

ID = int(os.getenv('ID'))
QTD_F = int(os.getenv('QTD_F'))
QTD_P = int(os.getenv('QTD_P'))

peca_list = []

for i in range(QTD_P//QTD_F*(ID-1)+1,QTD_P//QTD_F*(ID)+1):
    peca_list.append(i)

def on_publish(client, userdata, mid):
    print("mid: "+str(mid))

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_message(client, userdata, msg): #MSG FORMAT "REQ PEÇA QTD"
    msg = msg.payload.decode('utf-8')
    #client.publish('Monitor',f"O Fornecedor{ID} recebeu a msg:{msg}", qos=1)
    type_msg = msg.split()[0]
    #Verifica o tipo de requisição
    if(type_msg == 'REQ'):
        peca, qtd = msg.split()[1:]
        #Verifica se o fornecedor possui a peçã
        if(not int(peca) in peca_list):
            client.publish('Monitor',f"O Fornecedor {ID} não possui a peça {peca}", qos=1)
            return
        client.publish('Almoxarifado',f"SEND {peca} {qtd}", qos=1)
        client.publish('Monitor',f"O Fornecedor{ID} enviou {qtd} peças do tipo {peca} para o almoxarifado", qos=1)
        return

    client.publish('Monitor',f"O Fornecedor {ID} não reconheceu a msg", qos=1)
    return

def on_connect(client, userdata, flags, rc):
    print('CONNACK received with code %d.' % (rc))  

client = paho.Client()
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_connect = on_connect
client.on_publish = on_publish
client.connect('localhost', 1883)
client.subscribe(f"Fornecedor{ID}", qos=1)

client.publish('Monitor',f"Fornecedor {ID} em operação", qos=1)

client.loop_forever()
