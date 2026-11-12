# Controle de Acesso por Reconhecimento Facial

## Integrantes do Grupo
- Diego Mourão Oliveira
- Ilan Hameiry
- Luca Lopes Martinho

## Descrição do Projeto

## Funcionamento do Sistema

## Objetivos do Projeto

## Requisitos do Sistema

### Requisitos Obrigatórios

| ID | Requisito | Tipo |
|:---:|:---|:---:|

### Requisitos Desejáveis

| ID | Requisito | Tipo |
|:---:|:---|:---:|

### Requisitos Opcionais

| ID | Requisito | Tipo |
|:---:|:---|:---:|

### Componentes Utilizados

- 1 Raspberry Pi 4 8 Gb Ram
- 1 Carão MicroSD 16 Gb
- 1 Módulo Conversor de Nível Lógico 3,3V - 5V
- 1 Webcam HD Full USB 2.0 A0198
- 2 LEDs 5mm (1 vermelha e 1 verde)
- 2 Resistores 33 Ω
- 1 Sensor Ultrassônico HC-SR04
- 1 Protoboard 170 pontos

## Diagrama de Blocos
```mermaid
flowchart TD
    MCU["Microprocessador<br/>(Raspberry Pi 4)"]
    TOUC["7'' raspberry pi touch screen display"]
    LEVEL1["Conversor de Nível Lógico<br/>(5V ↔ 3.3V)"]
    US["Sensor de Distância<br/>Ultrassom HC-SR04"]
    CAM["Webcam usb<br/>1080px"]

    MCU --> TOUC
    CAM --> MCU
    US --> LEVEL1
    LEVEL1 --> MCU


    %% Optional styling
    classDef sensor fill:#cfe8f3,stroke:#333,stroke-width:1px;
    classDef converter fill:#f4c542,stroke:#333,stroke-width:1px;
    classDef controller fill:#00ff00,stroke:#333,stroke-width:2px;

    class MCU controller;
    class US sensor;
    class LEVEL1 converter;
    classDef default fill:#cfe8f3,color:#000,stroke:#000,stroke-width:2px;

    linkStyle default stroke:#000,stroke-width:2px;

```


## Softwares Utilizados

Durante o desenvolvimento do projeto foram utilizados os seguintes softwares:

- [Thonny](https://thonny.org/) — utilizado para programação, testes e depuração do Raspberry Pi 4
- [RealVNC Viewer](https://www.realvnc.com/en/connect/download/viewer/?lai_sr=0-4&lai_sl=l) - utilizado para conectar e programar o raspberry pi remotamente, assim não necessitando um monitor, teclado e mouse apenas para interagir com o microporcessador
  
## Tecnologias Envolvidas

## Imagens do Modelo

## Apresentação do Projeto em Vídeo
