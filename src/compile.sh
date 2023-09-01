#!/bin/bash

cp requirements.txt Almoxarifado/
cp requirements.txt Fabrica/
cp requirements.txt Linha/
cp requirements.txt Fornecedor/
cp requirements.txt Monitor/

docker build -t almoxarifado Almoxarifado/
docker build -t fabrica Fabrica/
docker build -t linha Linha/
docker build -t fornecedor Fornecedor/
docker build -t monitor Monitor/
