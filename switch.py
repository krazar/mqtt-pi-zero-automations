import os
import sched, time
import re
import RPi.GPIO as GPIO
import paho.mqtt.client as mqttClient

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class Plug:
    def __init__(self, name, id, state = False):
        self.name = name
        self.id = id
        self.state = state
        GPIO.setup(self.id, GPIO.OUT)
        GPIO.output(self.id, not self.state)

    def enable(self):
        if not self.state:
            GPIO.output(self.id, False)
            self.state = True

    def disable(self):
        if self.state:
            GPIO.output(self.id, True)
            self.state = False

plugs = [
    Plug('tv', 27),
    Plug('amp', 23),
    Plug('ghost', 22)
]
s = sched.scheduler(time.time, time.sleep)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected                #Use global variable
        Connected = True                #Signal connection
        client.subscribe("cinema/+/command")
        client.on_message = callbackMessage
        #s.enter(5, 1, scheduleSendStates, (s, client))

    else:
        print("Connection failed")

def scheduleSendStates(sc, client):
    sendStates(client)
    s.enter(20, 1, scheduleSendStates, (sc, client))

def callbackMessage(client, userdata, message):
    #print("message received " , str(message.payload.decode("utf-8")))
    topic = message.topic
    payload = str(message.payload.decode("utf-8"))
    m = re.match(r"cinema/(.*)/command", topic)
    if m:
        name = m.group(1)

        plug = next((x for x in plugs if x.name == name), None)
        if plug:
            # print("message received " , str(message.payload.decode("utf-8")))
            if payload == '1':
                plug.enable()
            else:
                plug.disable()

            sendState(client, plug)

def sendState(client, p):
    topic = f'cinema/{p.name}/state'
    payload = 1 if p.state else 0
    client.publish(topic, payload, 0, False)
    # print(f"state sent {p.name}")


def sendStates(client):
    for p in plugs:
        sendState(client, p)

def mqttConnection(url, port, user, password):
    client = mqttClient.Client("Python")               #create new instance
    client.username_pw_set(user, password)    #set username and password
    client.on_connect = on_connect
    client.connect(url, port)
    return client

broker = os.environ['MQTT_URL']
port = int(os.environ['MQTT_PORT'])
user = os.environ['MQTT_USER']
password = os.environ['MQTT_PASS']

client = mqttConnection(broker, port, user, password)

client.loop_start()
s.enter(5, 1, scheduleSendStates, (s, client))
s.run()

