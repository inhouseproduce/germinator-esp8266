 import machine
import sht31

#AWS MQTT client cert example for esp8266 or esp32 running MicroPython 1.9 
from umqtt.robust import MQTTClient
import time

# SHT31 Pin Init
i = machine.I2C(sda=machine.Pin(5), scl=machine.Pin(4))
s = sht31.SHT31(i)

# Temperature Vals (TRUE)
# tempLimit = 20.56
# tMax = 21.667

# Humidity Vals (TRUE)
# humidLimit = 47.0
# hMax = 50.0

# Temperature Vals (FALSE)
tempLimit = 30.0
tMax = 35.0

# Humidity Vals (FALSE)
humidLimit = 95.0
hMax = 100.0

# 2 Relay Module Pin Init
heaterPin = machine.Pin(0, machine.Pin.OUT)
humidiPin = machine.Pin(2, machine.Pin.OUT)

#This works for either ESP8266 ESP32 if you rename certs before moving into /flash 
CERT_FILE = "CERTNAME.cert.der"
KEY_FILE = "KEYNAME.key.der"

#if you change the ClientId make sure update AWS policy
MQTT_CLIENT_ID = "basicPubSub"
MQTT_PORT = 8883

#if you change the topic make sure update AWS policy
MQTT_TOPIC = "MQTT_TOPIC"

#Change the following three settings to match your environment
MQTT_HOST = "AWS_ENDPOINT_ADDRESS-ats.iot.REGION.amazonaws.com"
WIFI_SSID = "TP-Link_33C4"
WIFI_PW = "nasturtium"

mqtt_client = None

def pub_msg(msg):
    global mqtt_client
    try:    
        mqtt_client.publish(MQTT_TOPIC, msg)
        print("Sent: " + msg)
    except Exception as e:
        print("Exception publish: " + str(e))
        raise

def connect_mqtt():    
    global mqtt_client

    try:
        with open(KEY_FILE, "r") as f: 
            key = f.read()

        print("Got Key")
            
        with open(CERT_FILE, "r") as f: 
            cert = f.read()

        print("Got Cert")	

        mqtt_client = MQTTClient(client_id=MQTT_CLIENT_ID, server=MQTT_HOST, port=MQTT_PORT, keepalive=5000, ssl=True, ssl_params={"cert":cert, "key":key, "server_side":False})
        mqtt_client.connect()
        print('MQTT Connected')
    except Exception as e:
        print('Cannot connect MQTT: ' + str(e))
        raise

def connect_wifi(ssid, pw):
    # import network
    # wlan = network.WLAN(network.STA_IF)
    
    # if(wlan.isconnected()):
    #     wlan.disconnect()  
    # # wlan.active(True)
    # nets = wlan.scan()
    
    # if not wlan.isconnected():

    #     wlan.active(True)
    #     wlan.connect(WIFI_SSID, WIFI_PW)
    #     while not wlan.isconnected():
    #         pass
    # print("connected:", wlan.ifconfig())
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(WIFI_SSID, WIFI_PW)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())

        
def connect_wifi_sdk(ssid, pw):
    from network import WLAN
    from network import STA_IF
    import machine

    wlan = WLAN(STA_IF)
    nets = wlan.scan()
    if(wlan.isconnected()):
        wlan.disconnect()            
    wlan.connect(ssid, pw)         
    while not wlan.isconnected():             
        machine.idle() # save power while waiting
        print('WLAN connection succeeded!')         
        break 
    print("connected:", wlan.ifconfig())

# Backup files
f = open('log.txt', 'w')
f.write("{\"row\" : \"" + str(iter) + "\", \"pos\" : \"0\", \"TempVal\" : \"" + str(temp) + "\"}\n")
f.write("{\"row\" : \"" + str(iter) + "\", \"pos\" : \"1\", \"HeatStat\" : \"" + statHeat + "\"}\n")
f.write("{\"row\" : \"" + str(iter) + "\", \"pos\" : \"2\", \"HumiVal\" : \"" + str(humid) + "\"}\n")
f.write("{\"row\" : \"" + str(iter) + "\", \"pos\" : \"3\", \"HumiStat\" : \"" + statHum + "\"}\n")

#start execution
try:
    print("Connecting WIFI")
    connect_wifi(WIFI_SSID, WIFI_PW)
    print("Connecting MQTT")
    connect_mqtt()
    print("Publishing")
    pub_msg("{\"row\" : \"0\", \"pos\" : \"0\", \"TempMin\" : \"" + str(tempLimit) + "\"}")
    pub_msg("{\"row\" : \"0\", \"pos\" : \"1\", \"TempMax\" : \"" + str(tMax) + "\"}")
    pub_msg("{\"row\" : \"0\", \"pos\" : \"2\", \"HumidMin\" : \"" + str(humidLimit) + "\"}")
    pub_msg("{\"row\" : \"0\", \"pos\" : \"3\", \"HumidMax\" : \"" + str(hMax) + "\"}")
    print("Initializer Complete")
except Exception as e:
    print(str(e))
    pass
