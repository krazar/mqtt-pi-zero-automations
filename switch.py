import signal
import subprocess
import os
import sched, time
import re
import paho.mqtt.client as mqttClient


class Plug:
    def __init__(self, name, cmd, state = False):
        self.name = name
        self.cmd = cmd
        self.state = state

    def enable(self):
        if not self.state:
            my_env = os.environ.copy()
            my_env["LD_LIBRARY_PATH"] = "/home/pi/mjpg-streamer/mjpg-streamer-experimental"
            self.process = subprocess.Popen(self.cmd,stdout=subprocess.PIPE, 
                       shell=True, preexec_fn=os.setsid, env=my_env)
            self.state = True


    def disable(self):
        if self.state:
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            self.state = False

plugs = [
    Plug('audio', '/opt/audiostream.py'),
    Plug('video', '/home/pi/mjpg-streamer/mjpg-streamer-experimental/mjpg_streamer -i "input_raspicam.so -x 1024 -y 768 -rot 180" -o "output_http.so -w /home/pi/mjpg-streamer/mjpg-streamer-experimental/www"'),
]
s = sched.scheduler(time.time, time.sleep)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected                #Use global variable
        Connected = True                #Signal connection
        client.subscribe("babyphone/+/command")
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
    m = re.match(r"babyphone/(.*)/command", topic)
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
    topic = f'babyphone/{p.name}/state'
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

