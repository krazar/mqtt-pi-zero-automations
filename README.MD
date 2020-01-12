# Home cinema wired relay with MQTT and PI zero

Simple project for my home. I wanted to command the power plug for my home cinema.
This part of the home is not well covered by Wifi so I wanted a wired solution.

This repository is for a small python file that run on a PI zero and is used  as point of communication between MQTT and the relay board. 

## Install

First, uprade the OS and python.Also, it needs paho-mqtt library. You can install it from apt-get as pip is not installed by default.

```bash
sudo apt update
sudo apt upgrade 
sudo apt-get install -y python3-dev python3-rpi.gpio python3-paho-mqtt
```

### Startup script

Create a bash script that will  define env variables and call the python script.
```
touch cinema.sh
chmod +x cinema.sh
```

```
#!/bin/sh
MQTT_URL=x.x.x.x MQTT_PORT=1883 MQTT_USER=xxx MQTT_PASS=xxx python3.7 switch.py

``` 

Launch script on boot and keep track of the logs
```bash
 sudo sed -i '/^exit 0/i sudo /home/pi/cinema.sh &' /etc/rc.local
```

# Wiring relay
* R: Relay board number
* S: Socket position

```
 | BCM   R  S     | S     R  BCM
 | 27    3  P3    | /        GND
 | 22    2  P2    | LOW   1  23
 | 3.3   /  /     | p1    4  24
```

# Wiring temp sensor BME280

Followed the instruction from this blog:
http://gilles.thebault.free.fr/spip.php?article48
