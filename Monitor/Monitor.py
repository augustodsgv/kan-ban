import paho.mqtt.client as paho
import json
import matplotlib.pyplot as plt
import numpy as np
import time
from threading import Thread

All_Stocks = {}
x_count = 4
fig, ax = plt.subplots(x_count,x_count,figsize=(12, 16))
plt.subplots_adjust(hspace=0.5)
# Função para plotar o gráfico
def plot_bar_chart(): 
    i = 0
    j = 0
    for key, value in All_Stocks.items():
        ax[i,j].clear()
        ax[i,j].bar(range(len(value)), value.values())
        ax[i,j].set_title(key)
        i += 1
        if(i >= x_count):
            i=0
            j+=1
    plt.draw()
    plt.pause(0.1)

def check_and_update():
    client.loop_forever()

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_message(client, userdata, msg):
    msg = msg.payload.decode('utf-8')
    #client.publish('Monitor',f"O Fornecedor{ID} recebeu a msg:{msg}", qos=1)
    type_msg = msg.split()[0]

    #Verifica o tipo de requisição
    if(type_msg == 'STQ'): #MSG FORMAT "STQ ORIGEM ESTOQUE[]"
        stock_received = json.loads("".join(msg.split()[2:]))
        All_Stocks[msg.split()[1]] = stock_received
        #plot_bar_chart()
        
        return

    print(msg)
    return 

def on_connect(client, userdata, flags, rc):
    print('CONNACK received with code %d.' % (rc))  

client = paho.Client()
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_connect = on_connect
client.connect('localhost', 1883)
client.subscribe('Monitor', qos=1)

def loop_forever():
    client.loop_forever()

thread = Thread(target=loop_forever)
thread.start()
time.sleep(2)
while(True):
    try:
        plot_bar_chart()
    except:
        pass

