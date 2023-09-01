# kanban
Solução de um problema de entrega de recursos para fábricas usando Kanban\

## O Problema
Há uma indústria coposta por:
* 100 Fornecedores que fornece peças infinitas (um para cada peça)
* 1 Almoxarifado que guarda peças para as fábricas
* 2 Fábricas que produzem pacotes com linhas que consomem as peças e produzem itens
* 8 linhas de produção na primeira fábrica e 5 linhas de produção na segunda

## Instalação
### Docker
* [Instale o docker](https://docs.docker.com/engine/install/)
* Mude as permissões de execução para todos os usuários\
```sudo group add docker```\
```sudo usermod -aG docker $USER```
* Reinicie o computador
* Mude as permissões dos arquivos _compile.sh_, _run.sh_ e _exe.sh_\
```chmod +x compile.sh run.sh exe.sh```

### HiveMQ
* Confira que você tem o Java JRE instalado\
[Open JDK para linux](https://openjdk.org/)
* Instale o [MQTT](https://mosquitto.org/download/)

## Como rodar
1. Inicie o server do MQTT
```
# No path da pasta raiz do MQTT /bin
./run.sh
```
3. Rode o script
```./exe.sh```

# Autores
[Augusto dos Santos Gomes Vaz](https://github.com/Augustodsgv)\
[Guilherme José da Silva](https://github.com/GuiJoseh)\
[Pedro Malandrin Klesse](https://github.com/Klesse)
