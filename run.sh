#!/bin/bash
QTD_P_FIX=3;
QTD_P_VAR=7;
QTD_P_OFF=5;
QTD_P=$((QTD_P_FIX+QTD_P_VAR+QTD_P_OFF));

QTD_F=1;

docker run -dt -e ID=1 -e QTD_F=$QTD_F -e QTD_P=$QTD_P -p 1883:1883 --network=host -p 8080:8080 -it --rm --name running-almoxarifado almoxarifado
docker run -dt -e ID=1 -e QTD_P=$QTD_P -p 1883:1883 --network=host -p 8080:8080 -it --rm --name running-fabrica-1 fabrica
docker run -dt -e ID=2 -e QTD_P=$QTD_P -p 1883:1883 --network=host -p 8080:8080 -it --rm --name running-fabrica-2 fabrica

for ((i = 1; i <= 5; i++)); do
    docker run -dt -e ID=$i -e FAB_ID=1 -e QTD_P=$QTD_P -e QTD_P_FIX=$QTD_P_FIX -e QTD_P_VAR=$QTD_P_VAR -e QTD_P_OFF=$QTD_P_OFF --network=host -p 1883:1883 -p 8080:8080 -it --rm --name running-linha-1-$i linha
done

for ((i = 1; i <= 8; i++)); do
    docker run -dt -e ID=$i -e FAB_ID=2 -e QTD_P=$QTD_P -e QTD_P_FIX=$QTD_P_FIX -e QTD_P_VAR=$QTD_P_VAR -e QTD_P_OFF=$QTD_P_OFF --network=host -p 1883:1883 -p 8080:8080 -it --rm --name running-linha-2-$i linha
done

for ((i = 1; i <= 1; i++)); do
    docker run -dt -e ID=$i -e QTD_F=$QTD_F -e QTD_P=$QTD_P  -p 1883:1883 --network=host -p 8080:8080 -it --rm --name running-fornecedor-$i fornecedor
done

export QTD_P
python3 Monitor/Monitor.py
#docker run -e ID=$i -e QTD_P=$QTD_P  --network=host -p 1883:1883 -p 8080:8080 -it --rm --name running-monitor monitor
