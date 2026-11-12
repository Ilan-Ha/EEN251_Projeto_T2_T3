import os
from dotenv import load_dotenv


class Env():
    ENV_SCRIPT_FOLDER = 'src'
    ENV_FILE_FOLDER = '.env'

    def loadOptionalString(self,key:str,defaultValue:str):
        aux = os.getenv(key)
        return aux if aux else defaultValue
    
    def loadRequiredString(self,key:str):
        aux =  os.getenv(key)
        if not aux:
            raise KeyError(f"{key} não existe no arquivo .env ou não está preenchida")
        else:
            return aux
        
    def loadInt(self,key:str,defaulValue:int):
        aux = os.getenv(key)
        return int(aux) if aux else defaulValue
    
    def __init__(self):
        super().__init__()
        p = os.getcwd()
        if self.ENV_SCRIPT_FOLDER in p:
            p.removesuffix(str)
        p = os.path.join(p,self.ENV_FILE_FOLDER)
        load_dotenv(p)
        self.GREEN_LED=self.loadInt(key='GREEN_LED',defaulValue=38)
        self.RED_LED=self.loadInt(key='RED_LED',defaulValue=40)
        self.GPIO_MODE=self.loadOptionalString(key='GPIO_MODE',defaultValue='BOARD')
        self.UPDATE_TIME=self.loadInt(key='UPDATE_TIME',defaulValue=1000)
        self.BROKER_ENDPOINT=self.loadRequiredString('BROKER_ENDPOINT')
        self.TLS_PORT=self.loadInt('TLS_PORT',8883)
        self.MQTT_USERNAME=self.loadRequiredString('MQTT_USERNAME')
        self.MQTT_PASSWORD=self.loadOptionalString(key='MQTT_PASSWORD',defaultValue="")
        self.PIN_ECHO=self.loadInt(key='PIN_ECHO',defaulValue=5)
        self.PIN_TRIGGER=self.loadInt(key='PIN_TRIGGER',defaulValue=3)


    def __str__(self):
        response = (f'GREEN_LED:{self.GREEN_LED}\nRED_LED:{self.RED_LED}\nGPIO_MODE:{self.GPIO_MODE}'+
                    f'\nUPDATE_TIME:{self.UPDATE_TIME}\nTLS_PORT:{self.TLS_PORT}'+
                    f'\nPIN_ECHO:{self.PIN_ECHO}\nPIN_TRIGGER:{self.PIN_TRIGGER}')
        return response
    
