import paho.mqtt.client as mqttClient
import ssl
import os
from log import Log
from env import Env
from datetime import datetime
from zoneinfo import ZoneInfo
import threading

class Mqtt:
    def __init__(self,log:Log,env:Env):
        super().__init__()
        self.connected = False
        self.BROKER_ENDPOINT = env.BROKER_ENDPOINT
        self.TLS_PORT = env.TLS_PORT
        self.MQTT_USERNAME = env.MQTT_USERNAME
        self.MQTT_PASSWORD = env.MQTT_PASSWORD
        self.PAD = 20
        p = os.getcwd()       
        if 'src' in p:
            p = os.path.dirname(p)        
        self.TLS_CERT_PATH = os.path.join(
        p, 'industrial.pem'
        )
        self.mqtt_client = mqttClient.Client()
        self.thread = None
        self.LOG_FILE = 'defaut_mqtt_log.txt'
        self.zone = ZoneInfo("America/Sao_Paulo")
        self.LOG = log

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.LOG.add_entry(key=self.LOG_FILE,entry=f'{str(datetime.now(self.zone))}:\t{'[CONNECTION-INFO]:':>{self.PAD}}\tConnected to Ubidots broker\n')
            self.connected = True
        else:
            self.LOG.add_entry(key=self.LOG_FILE,entry=f'{str(datetime.now(self.zone))}:\t{'[CONNECTION-ERROR]:':>{self.PAD}}\tConnection failed: {rc}\n')

    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        self.LOG.add_entry(key=self.LOG_FILE,entry=f'{str(datetime.now(self.zone))}:\t{'[CONNECTION-INFO]:':>{self.PAD}}\tDisconnected from broker\n')

    def connect(self):

        self.mqtt_client.username_pw_set(
            self.MQTT_USERNAME,
            password=self.MQTT_PASSWORD
        )

        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_disconnect = self.on_disconnect

        self.mqtt_client.tls_set(
            ca_certs=self.TLS_CERT_PATH,
            certfile=None,
            keyfile=None,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLSv1_2,
            ciphers=None
        )
        self.mqtt_client.tls_insecure_set(False)
        self.mqtt_client.connect(
            self.BROKER_ENDPOINT,
            port=self.TLS_PORT
        )

        self.mqtt_client.loop_forever()

    def start(self):
        self.thread = threading.Thread(
            target=self.connect,
            daemon=True
        )
        self.thread.start()

    def stop(self):
        self.mqtt_client.disconnect()
        self.mqtt_client.loop_stop()


class Subscriber(Mqtt):
    def __init__(self, log:Log, env:Env,topics:list, subscribers_functions:list):
        super().__init__(log,env)
        self.TOPICS = topics 
        self.SUB_FUN = subscribers_functions 
        self.LOG_FILE='subscriber_log.txt'

    def on_connect(self, client, userdata, flags, rc):
        super().on_connect(client, userdata, flags, rc)
        if self.connected:
            client.subscribe(self.TOPICS)
            for topic in self.TOPICS:
                self.LOG.add_entry(
                    key=self.LOG_FILE,
                    entry=f'{str(datetime.now(self.zone))}:\t{'[SUBSCRIBE-INFO]:':>{self.PAD}}\tSubscribed to: {topic[0]} | with Qos: {topic[1]}\n'
                )
    def on_message(self, client, userdata, message):
        self.LOG.add_entry(
            key='subscriber_log.txt',
            entry=f'{str(datetime.now(self.zone))}:\t{'[TOPIC]:':>{self.PAD}}\t{message.topic}\n')
        
    def connect(self):
        for i in range(len(self.TOPICS)):
            self.mqtt_client.message_callback_add(self.TOPICS[i][0],self.SUB_FUN[i])
        self.mqtt_client.on_message = self.on_message
        
        super().connect()

class Publisher(Mqtt):
    def __init__(self, log,env):
        super().__init__(log,env)
        self.LOG_FILE='publisher_log.txt'

    def on_publish(self,client, userdata, result):
        self.LOG.add_entry(
            key=self.LOG_FILE,
            entry=f'{str(datetime.now(self.zone))}:\t{'[PUBLISH-STATUS]:':>{self.PAD}}\tClient: {client}\tUserdata: {userdata}\tResult: {result}\n')
        
    def publish(self, topic, payload): # unique
    
        try:
            self.mqtt_client.publish(topic, payload)
            self.LOG.add_entry(
            key=self.LOG_FILE,
            entry=f'{str(datetime.now(self.zone))}:\t{'[PUBLISH-INFO]:':>{self.PAD}}\tTopic: {topic}\tPayload: {payload}\n')

        except Exception as e:
            self.LOG.add_entry(
                key=self.LOG_FILE,
                entry=f'{str(datetime.now(self.zone))}:\t{'[PUBLISH-ERROR]:':>{self.PAD}}\tCould not publish data, error: {format(e)}\n')
            
    def connect(self):
        self.mqtt_client.on_publish = self.on_publish
        super().connect()